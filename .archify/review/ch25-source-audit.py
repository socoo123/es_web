"""Validate pinned citation bytes and experiment repeatability boundaries; not API proof."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,subprocess,re,os,hashlib
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
repo=Path(os.environ.get('ES_SOURCE_ROOT','/workspace/scratch/es-v9.4.0'));rev='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
assert git('rev-parse','HEAD').decode().strip()==rev and not git('status','--porcelain')
assert git('remote','get-url','origin').decode().strip()=='https://github.com/elastic/elasticsearch.git'
refs={}
def add(p,a,b):refs.setdefault(p,set()).add((int(a),int(b)))
html=(root/'chapters/ch25.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for p in json.loads((out/'ch25-paths.json').read_text()).values():
 d=json.loads((root/p).with_name('candidate.json').read_text());assert d['meta']['repository']['revision']==rev
 for n in d['nodes']:
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
extra={'indices/breaker/HierarchyCircuitBreakerService.java':[(178,210),(631,717)],'common/breaker/ChildMemoryCircuitBreaker.java':[(194,207)],'search/aggregations/AggregatorBase.java':[(349,357)],'index/IndexingPressure.java':[(30,83)]}
for p,rs in extra.items():
 for a,b in rs:add('server/src/main/java/org/elasticsearch/'+p,a,b)
files=[]
for p,rs in sorted(refs.items()):
 data=git('show',rev+':'+p);assert (repo/p).read_bytes()==data,p
 lines=len(data.decode().splitlines())
 for a,b in rs:assert 1<=a<=b<=lines,(p,a,b,lines)
 files.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(rs)]})
versions=git('show',rev+':build-tools-internal/version.properties').decode();assert re.search(r'^lucene\s*=\s*(\S+)',versions,re.M).group(1)=='10.4.0'
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch25.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root));ids=[e['id'] for e in ops];old=json.loads((out/'ch25-original-ids.json').read_text());assert len(ids)==len(set(ids))==29 and len(old)==14 and set(old)<=set(ids)
assert re.findall(r'data-exp="([^"]+)"',html)==ids
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD'])
for e in ops:
 if e['method'] in ['PUT','POST','DELETE']:
  path=e['path'].split('?')[0]
  assert path=='/_cluster/settings' or path in ['/tut-l25-card','/tut-l25-card/_bulk','/tut-l25-card/_search'],(e['id'],path)
  if path=='/_cluster/settings':
   assert set(e['body'])=={'transient'} and set(e['body']['transient'])=={'indices.breaker.request.limit'}
   assert e['body']['transient']['indices.breaker.request.limit'] in ['1kb',None]
setup=next(e for e in ops if e['id']=='ch25-02-setup');assert setup['body']['settings']=={'number_of_shards':1,'number_of_replicas':0,'auto_expand_replicas':'false'} and setup['body']['mappings']['dynamic']=='strict' and setup['body']['mappings']['properties']['user_id']['type']=='keyword'
for id in ['ch25-03-bulk','ch25-pressure-bulk']:
 data=next(e for e in ops if e['id']==id)['body'];assert data.endswith('\n');lines=[json.loads(l) for l in data.splitlines()];assert len(lines)==40
 assert [l['index']['_id'] for l in lines[::2]]==list(map(str,range(1,21)))
 assert [l['user_id'] for l in lines[1::2]]==['u-'+str(i) for i in range(1,21)]
qs=[e['body'] for e in ops if e['id'] in ['ch25-04-terms-ok','ch25-06-terms-break','ch25-10-terms-ok2']];assert len(qs)==3 and qs[0]==qs[1]==qs[2]
assert all('request_cache=false' in e['path'] for e in ops if e['id'] in ['ch25-04-terms-ok','ch25-06-terms-break','ch25-10-terms-ok2'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'inspectedLocalSourceMatchesCommittedBytes':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'luceneVersion':'10.4.0','originalIdsPreserved':14,'orderedUniqueOperations':29,'getAndHeadBodiesAbsent':True,'mutationsLimitedToNamedIndexAndSingleTransientSetting':True,'fixedBulkDocumentIds':20,'chapterSha256':sha(root/'chapters/ch25.html'),'experimentSha256':sha(root/'experiments/ch25.js'),'realEsApi':'not-run-see-ch25-es-runtime.json','semanticReview':'Source methods manually read; byte audit verifies citation identity and boundaries, not the semantics by itself.','claims':{'child':'positive-limit check before CAS; -1 only skips child, Parent still checked; rollback raw bytes','parent':'real/weighted modes, strategy second comparison, all children durability','preallocation':'6KB covers internal 5KB; only overflow charged; close and memory GC distinct','stats':'raw child used versus Parent mode; current/total/tripped not same measure','pressure':'phase limits and forceExecution; >= both conditions in incremental maybeSplit','restoration':'null removes named layer, no unknown-original transient overwrite; actual baseline check'}}
(out/'ch25-source-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('PASS:',r['fileCount'],'files /',r['rangeCount'],'pinned source ranges; 14 stable IDs / 29 ordered operations. Real API not run.')
