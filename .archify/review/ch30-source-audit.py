"""Bind cited fixed source ranges and stable chapter registrations."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,re,subprocess,hashlib
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
repo=Path('/tmp/es-ch15/es-v9.4.0');rev='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
assert git('rev-parse','HEAD').decode().strip()==rev and not git('status','--porcelain')
assert git('remote','get-url','origin').decode().strip()=='https://github.com/elastic/elasticsearch.git'
refs={}
def add(p,a,b):refs.setdefault(p,set()).add((int(a),int(b)))
html=(root/'chapters/ch30.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for name,p in json.loads((out/'ch30-paths.json').read_text()).items():
 d=json.loads((root/p).with_name('candidate.json').read_text())
 if name=='reading-loop':assert 'repository' not in d['meta'];continue
 assert d['meta']['repository']['revision']==rev
 for n in d['nodes']:
  assert n['sources']
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
files=[]
for p,ranges in sorted(refs.items()):
 data=git('show',rev+':'+p);linecount=len(data.decode().splitlines())
 if (repo/p).exists():assert (repo/p).read_bytes()==data,p
 for a,b in ranges:assert 1<=a<=b<=linecount,(p,a,b,linecount)
 files.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(ranges)]})
specs=json.loads(subprocess.check_output(['node','-e','global.window={};require("./experiments/ch30.js");console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))'],cwd=root));ids=[s['id'] for s in specs]
assert len(ids)==len(set(ids))==20
assert set(json.loads((out/'ch30-original-ids.json').read_text()))<=set(ids)
assert re.findall(r'<div class="exp-slot" data-exp="([^"]+)"',html)==ids==json.loads((out/'ch30-operation-order.json').read_text())
assert all(s['endpoint']=='http://localhost:9200' and s['auth'] is None for s in specs)
assert all(s.get('body') is None for s in specs if s['method'] in ['GET','HEAD'])
assert all(s['path'].split('?')[0]=='/tut-l30-docs' or s['path'].startswith('/tut-l30-docs/') for s in specs if s['method'] in ['PUT','POST','DELETE'])
version=git('show',rev+':build-tools-internal/version.properties').decode();assert re.search(r'^lucene\s*=\s*(\S+)',version,re.M).group(1)=='10.4.0'
report={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'originalIdsPreserved':13,'orderedUniqueOperations':20,'getAndHeadBodiesAbsent':True,'explicitEndpointAndAuth':True,'chapterSha256':hashlib.sha256((root/'chapters/ch30.html').read_bytes()).hexdigest(),'experimentSha256':hashlib.sha256((root/'experiments/ch30.js').read_bytes()).hexdigest(),'semanticReview':'Named source/test methods manually read; byte/range audit alone does not prove semantic entailment.','testExecution':'Gradle source tests not run; real API separately recorded','claims':{'window':'DefaultSearchContext.preProcess before main shard query, not before coordinator fan-out','usage':'prepare and postchecks before increment, before consumer execution; two rounds delta5','singleShard':'normal single shard/no-rank query-fetch optimization; API not network trace','async':'listener interface does not itself guarantee thread switch or nonblocking','visibility':'ordinary new search differs from realtime GET; refresh response plural _shards; no unconditional new-segment or translog guarantee','methodsDiagram':'conceptual reading order without repository runtime-call claim'}}
(out/'ch30-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS:',len(files),'fixed source files;',report['rangeCount'],'ranges; 13 stable IDs / 20 ordered operations.')
