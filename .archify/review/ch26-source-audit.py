"""Bind inspected fixed-version source and repeatability constraints; not API proof."""
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
html=(root/'chapters/ch26.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for p in json.loads((out/'ch26-paths.json').read_text()).values():
 d=json.loads((root/p).with_name('candidate.json').read_text());assert d['meta']['repository']['revision']==rev
 for n in d['nodes']:
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
extra={
 'modules/lang-painless/src/main/java/org/elasticsearch/painless/lookup/PainlessLookupUtility.java':[(89,153)],
 'modules/lang-painless/src/main/resources/org/elasticsearch/painless/org.elasticsearch.script.score.txt':[(10,54)],
 'modules/lang-painless/src/main/resources/org/elasticsearch/painless/org.elasticsearch.script.ingest.txt':[(10,41)],
 'server/src/main/java/org/elasticsearch/script/ScriptException.java':[(158,161)],
 'server/src/main/java/org/elasticsearch/index/query/MatchAllQueryBuilder.java':[(65,68)],
 'server/src/main/java/org/elasticsearch/index/query/functionscore/FunctionScoreQueryBuilder.java':[(60,65),(328,342)],
 'server/src/main/java/org/elasticsearch/action/ingest/SimulateDocumentBaseResult.java':[(98,109)],
 'server/src/main/java/org/elasticsearch/action/ingest/WriteableIngestDocument.java':[(119,132)]}
for p,rs in extra.items():
 for a,b in rs:add(p,a,b)
files=[]
for p,rs in sorted(refs.items()):
 data=git('show',rev+':'+p);assert (repo/p).read_bytes()==data,p
 lines=len(data.decode().splitlines())
 for a,b in rs:assert 1<=a<=b<=lines,(p,a,b,lines)
 files.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(rs)]})
versions=git('show',rev+':build-tools-internal/version.properties').decode();assert re.search(r'^lucene\s*=\s*(\S+)',versions,re.M).group(1)=='10.4.0'
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch26.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root));ids=[e['id'] for e in ops];old=json.loads((out/'ch26-original-ids.json').read_text());assert len(ids)==len(set(ids))==45 and len(old)==20 and set(old)<=set(ids)
assert re.findall(r'data-exp="([^"]+)"',html)==ids
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD'])
allowed=['/_cluster/settings','/tut-l26-score','/tut-l26-score/_bulk','/tut-l26-score/_search','/tut-l26-score/_update/cheap','/_ingest/pipeline/tut-l26-script','/_ingest/pipeline/tut-l26-file','/_ingest/pipeline/tut-l26-script/_simulate','/_scripts/painless/_execute']
for e in ops:
 if e['method'] in ['PUT','POST','DELETE']:
  p=e['path'].split('?')[0];assert p in allowed,(e['id'],p)
  if p=='/_cluster/settings':
   assert set(e['body'])=={'transient'} and set(e['body']['transient'])=={'search.allow_expensive_queries'}
   assert e['body']['transient']['search.allow_expensive_queries'] is False or e['body']['transient']['search.allow_expensive_queries'] is None
setup=next(e for e in ops if e['id']=='ch26-01-setup');assert setup['body']['settings']=={'number_of_shards':1,'number_of_replicas':0,'auto_expand_replicas':'false'} and setup['body']['mappings']['dynamic']=='strict'
assert setup['body']['mappings']['properties']=={'title':{'type':'keyword'},'popularity':{'type':'long'},'price':{'type':'double'},'views':{'type':'long'}}
bulk=next(e for e in ops if e['id']=='ch26-02-bulk');assert 'refresh=true' in bulk['path'] and bulk['body'].endswith('\n')
lines=[json.loads(l) for l in bulk['body'].splitlines()];assert [x['index']['_id'] for x in lines[::2]]==['cheap','popular'] and len(lines)==4
assert [d for d in lines[1::2]]==[{'title':'obscure','popularity':10,'price':100.0},{'title':'hit','popularity':100,'price':80.0}]
params=[e for e in ops if e['id'] in ['ch26-d-param-2','ch26-d-param-3']];assert params[0]['body']['script']['source']==params[1]['body']['script']['source'] and [e['body']['script']['params']['multiplier'] for e in params]==[2,3]
assert all('request_cache=false' in e['path'] for e in ops if e['path'].startswith('/tut-l26-score/_search'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'inspectedLocalSourceMatchesCommittedBytes':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'luceneVersion':'10.4.0','originalIdsPreserved':20,'orderedUniqueOperations':45,'getAndHeadBodiesAbsent':True,'mutationsLimitedToNamedResourcesAndSingleTransientSetting':True,'fixedBulkDocumentIds':2,'chapterSha256':sha(root/'chapters/ch26.html'),'experimentSha256':sha(root/'experiments/ch26.js'),'realEsApi':'not-run-see-ch26-es-runtime.json','semanticReview':'Source methods manually read; byte audit verifies citation identity and boundaries, not semantics on its own.','claims':{'loader':'extends ClassLoader, parent delegation not overridden; File refusal is semantic lookup','cache':'project/lang/resolved source/context/options; params absent; node-local lifetime conditions','dynamic':'static member check versus runtime Def.lookupMethod','ingest':'creation validates compile; stored processor does not retain factory, service cache can still hit','scoring':'returned float score multiplied by boost, skip when COMPLETE_NO_SCORES and no minScore','api-shape':'test execute returns string; simulate wraps doc._source; context API internal','restoration':'null deletes named layer; E and matching cleanup conditional on known empty overlays'}}
(out/'ch26-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS:',report['fileCount'],'files /',report['rangeCount'],'pinned ranges; 20 stable IDs / 45 ordered operations. API not run.')
