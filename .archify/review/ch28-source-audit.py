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
html=(root/'chapters/ch28.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for p in json.loads((out/'ch28-paths.json').read_text()).values():
 d=json.loads((root/p).with_name('candidate.json').read_text());assert d['meta']['repository']['revision']==rev
 for n in d['nodes']:
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
add('server/src/main/java/org/elasticsearch/action/admin/indices/rollover/RolloverConditions.java',231,266)
add('x-pack/plugin/ilm/src/main/java/org/elasticsearch/xpack/ilm/action/TransportDeleteLifecycleAction.java',78,100)
files=[]
for p,rs in sorted(refs.items()):
 data=git('show',rev+':'+p);assert (repo/p).read_bytes()==data,p
 lines=len(data.decode().splitlines())
 for a,b in rs:assert 1<=a<=b<=lines,(p,a,b,lines)
 files.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(rs)]})
versions=git('show',rev+':build-tools-internal/version.properties').decode();assert re.search(r'^lucene\s*=\s*(\S+)',versions,re.M).group(1)=='10.4.0'
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch28.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root));ids=[e['id'] for e in ops];old=json.loads((out/'ch28-original-ids.json').read_text());assert len(ids)==len(set(ids))==40 and len(old)==20 and set(old)<=set(ids)
assert re.findall(r'data-exp="([^"]+)"',html)==ids
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD'])
for e in ops:
 if e['method'] in ['PUT','POST','DELETE']:
  path=e['path'].split('?')[0];assert path.startswith('/tut-l28-') or path.startswith('/_ilm/policy/tut-l28-') or path.startswith('/_index_template/tut-l28-') or path=='/_cluster/settings',(e['id'],path)
 assert e['method']!='DELETE' or path!='/tut-l28-*' or e['id']=='ch28-15-wildcard'
tpl=next(e for e in ops if e['id']=='ch28-03-template')['body']['template'];assert tpl['settings']['number_of_shards']==1 and tpl['settings']['number_of_replicas']==0 and tpl['settings']['refresh_interval']=='-1' and tpl['mappings']['dynamic']=='strict' and 'aliases' not in tpl
assert next(e for e in ops if e['id']=='ch28-02-policy')['body']['policy']['phases']['hot']['actions']['rollover']['min_docs']==2
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'luceneVersion':'10.4.0','originalIdsPreserved':20,'orderedUniqueOperations':40,'getAndHeadBodiesAbsent':True,'mutationsLimitedToChapterResourcesAndTemporaryPoll':True,'fixedDocumentIds':True,'explicitMinDocsBarrier':2,'chapterSha256':sha(root/'chapters/ch28.html'),'experimentSha256':sha(root/'experiments/ch28.js'),'realEsApi':'pass-see-ch28-es-review.json','semanticReview':'Target methods manually read; byte audit establishes citation identity and line boundaries, not semantics on its own.','claims':{'rollover':'any max and all min; creation age; explicit min_docs2 barrier versus default injection','phaseAge':'rollover date without origination_date; warm2h/delete24h same origin; future min_age live','phaseCache':'eligibility/current step/parse/same-step-set conditions; current cached phase overlays live policy','policyPut':'same policy and headers can no-op; changed policy increments version','template':'new index request does not copy old lifecycle settings; matching template relay; only rollover alias duplication prohibited','scheduler':'periodic and state-change runner paths differ; interval is not completion deadline','alias':'explicit true in tutorial; classic one-target implicit write case allowed','coverage':'two rollover rounds and safe condition update observed; long-age warm/delete and datastream/CCR not run'}}
(out/'ch28-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS:',len(files),'files /',report['rangeCount'],'pinned ranges; 20 stable IDs / 40 ordered operations.')
