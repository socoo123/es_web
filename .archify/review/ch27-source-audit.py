"""Verify the fixed committed sources actually cited by the chapter and diagrams."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,subprocess,re,os,hashlib
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
repo=Path(os.environ.get('ES_SOURCE_ROOT','/tmp/es-ch15/es-v9.4.0'));rev='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
assert git('rev-parse','HEAD').decode().strip()==rev and not git('status','--porcelain')
assert git('remote','get-url','origin').decode().strip()=='https://github.com/elastic/elasticsearch.git'
refs={}
def add(p,a,b):refs.setdefault(p,set()).add((int(a),int(b)))
html=(root/'chapters/ch27.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for p in json.loads((out/'ch27-paths.json').read_text()).values():
 d=json.loads((root/p).with_name('candidate.json').read_text());assert d['meta']['repository']['revision']==rev
 for n in d['nodes']:
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
files=[]
for p,rs in sorted(refs.items()):
 data=git('show',rev+':'+p);assert (repo/p).read_bytes()==data,p
 lines=len(data.decode().splitlines())
 for a,b in rs:assert 1<=a<=b<=lines,(p,a,b,lines)
 files.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(rs)]})
versions=git('show',rev+':build-tools-internal/version.properties').decode();assert re.search(r'^lucene\s*=\s*(\S+)',versions,re.M).group(1)=='10.4.0'
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch27.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root));ids=[e['id'] for e in ops];old=json.loads((out/'ch27-original-ids.json').read_text());assert len(ids)==len(set(ids))==42 and len(old)==14 and set(old)<=set(ids)
assert re.findall(r'data-exp="([^"]+)"',html)==ids
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD'])
for e in ops:
 if e['method'] in ['PUT','POST','DELETE']:
  p=e['path'].split('?')[0];assert p=='/_query' or p=='/_esql' or p.startswith('/tut-l27-pages') or p.startswith('/tut-l27-values'),(e['id'],p)
for id in ['ch27-01-setup','ch27-c-setup']:
 s=next(e for e in ops if e['id']==id)['body'];assert s['settings']=={'number_of_shards':1,'number_of_replicas':0,'auto_expand_replicas':'false','refresh_interval':'-1'} and s['mappings']['dynamic']=='strict'
for e in ops:
 if '_bulk' in e['path']:
  assert e['body'].endswith('\n') and 'refresh=true' in e['path']
  lines=[json.loads(l) for l in e['body'].splitlines()];assert all('_id' in x['index'] for x in lines[::2])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'luceneVersion':'10.4.0','originalIdsPreserved':14,'orderedUniqueOperations':42,'getAndHeadBodiesAbsent':True,'mutationsLimitedToChapterResourcesAndEsqlRequests':True,'fixedBulkDocumentIds':True,'chapterSha256':sha(root/'chapters/ch27.html'),'experimentSha256':sha(root/'experiments/ch27.js'),'realEsApi':'pass-see-ch27-es-review.json','semanticReview':'Methods manually read; this audit verifies citation identity and line boundaries, not semantics on its own.','claims':{'pipeline':'input dependencies and semantics, physical rewrites permitted','pushdown':'logical movement and physical translatable-condition merge, residual filters retained','avg':'ordinary long SUM/COUNT; valid values differ from rows; NULL on no values','page':'Block[] positions, document IDs can remain, 256KiB estimate not fixed bound','driver':'single-threaded chain with blocking/readiness and output ownership, multiple drivers can execute','score':'MATCH plus metadata, MetadataAttribute DOUBLE despite doc float table','limit':'ordinary output truncation versus explicit LIMIT before STATS','visibility':'empirical fixed-refresh interval GET/FROM distinction'}}
(out/'ch27-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS:',report['fileCount'],'files /',report['rangeCount'],'pinned ranges; 14 stable IDs / 42 ordered operations.')
