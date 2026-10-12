"""Run only ch18's registered operations twice; validate real ES responses."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess,json,urllib.request,urllib.error,os,hashlib,sys
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
endpoint=os.environ.get('ES_ENDPOINT','http://localhost:9200').rstrip('/')
ops=json.loads(subprocess.check_output(['node','-e','global.window={};require(process.argv[1]);console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))',str(root/'experiments/ch18.js')]))
identity=[{k:e.get(k) for k in ['id','method','path','body']} for e in ops]
def req(m,p,b=None):
 assert b is None or m not in ['GET','HEAD'],'Browser fetch cannot send GET/HEAD body'
 data=b.encode() if isinstance(b,str) else json.dumps(b).encode() if b is not None else None
 r=urllib.request.Request(endpoint+p,data=data,method=m,headers={'Content-Type':'application/x-ndjson' if '_bulk' in p else 'application/json'})
 try:
  with urllib.request.urlopen(r,timeout=30) as s:status=s.status;raw=s.read().decode()
 except urllib.error.HTTPError as s:status=s.code;raw=s.read().decode()
 return {'status':status,'response':json.loads(raw) if raw else None}
file=out/'ch18-es-review.json'
if '--validate-only' in sys.argv or '--repeatability-only' in sys.argv:
 report=json.loads(file.read_text());assert report['registeredRequests']==identity
else:
 version=req('GET','/');v=version['response']['version'];assert (v['number'],v['lucene_version'],v['build_hash'])==('9.4.0','10.4.0','2e8528e92361c3399724226deaf2b46f933e925b')
 nodes=req('GET','/_nodes?filter_path=nodes.*.version');assert len(nodes['response']['nodes'])==1
 report={'kind':'real-es-api','endpoint':endpoint,'version':version,'nodes':nodes,'reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'registeredRequests':identity,'preCleanup':req('DELETE','/tut-l18-dsl?ignore_unavailable=true'),'runs':[]}
 for n in [1,2]:
  run={'run':n,'operations':[]};report['runs'].append(run)
  for e in ops:
   r=req(e['method'],e['path'],e.get('body'));run['operations'].append({**{k:e.get(k) for k in ['id','method','path','body']},**r})
   report['status']='collected-validation-pending';file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
   print(n,e['id'],r['status'],flush=True)
for run in report['runs']:
 rows={int(r['id'].split('-')[1]):r for r in run['operations']}
 def R(n):return rows[n]['response']
 def ids(n):return sorted(h['_id'] for h in R(n)['hits']['hits'])
 def total(n):return R(n)['hits']['total']['value']
 for n,r in rows.items():assert r['status']==200,(n,r)
 assert R(0)['acknowledged'] and R(18)['acknowledged']
 assert R(19)['status']=='green' and not R(19)['timed_out'] and R(19)['active_primary_shards']==1
 assert not R(1)['errors'] and len(R(1)['items'])==4 and all(i['index']['status']==201 and i['index']['result']=='created' for i in R(1)['items'])
 assert [t['token'] for t in R(2)['tokens']]==['the','quick','brown','fox']
 assert [t['token'] for t in R(21)['tokens']]==['quick','brown'] and [t['position'] for t in R(21)['tokens']]==[0,1]
 terms=R(20)['term_vectors']['title']['terms'];assert set(terms)=={'the','quick','brown','fox'}
 assert [terms[t]['tokens'][0]['position'] for t in ['the','quick','brown','fox']]==[0,1,2,3]
 for n in [3,5,16,22,23]:assert ids(n)==['1','2'],(n,ids(n))
 for n in [4,6,15,17,24,26]:assert total(n)==0,(n,R(n))
 for n in [7,25,28,29,14,31]:assert ids(n)==['1','3','4'],(n,ids(n))
 for n in [8,30]:assert ids(n)==['1']
 assert ids(27)==['1','2','3','4']
 assert R(9)['matched'] and 'title:quick' in json.dumps(R(9)) and 'title:brown' in json.dumps(R(9))
 assert not R(10)['matched'] and not R(33)['matched'] and 'status:published' in json.dumps(R(33))
 assert sorted(h['_id'] for h in R(11)['hits']['hits'])==['1','2'] and all('_explanation' in h for h in R(11)['hits']['hits'])
 assert ids(12)==ids(13)==['4'] and R(13)['hits']['hits'][0]['_score']>R(12)['hits']['hits'][0]['_score']
 assert all(h['_score']==0 for h in R(28)['hits']['hits'])
 scores={h['_id']:h['_score'] for h in R(29)['hits']['hits']};assert scores['1']>0 and scores['3']==scores['4']==0
 def buckets(n):return {b['key']:b['doc_count'] for b in R(n)['aggregations']['by_status']['buckets']}
 assert buckets(14)=={'published':3,'draft':1} and buckets(31)=={'published':3}
 ex=R(32)['explanations'][0]['explanation'];assert R(32)['valid'] and 'title:quick' in ex and 'title:brown' in ex and '+title:' not in ex
 assert [{k:r.get(k) for k in ['id','method','path','body']} for r in run['operations']]==identity
 run['status']='pass';run['verified']=['34-actual-registered-requests','browser-compatible-POST-query-bodies','explicit-one-shard-green-health','fixed-ID-created-and-refreshed','stored-termvectors-positions','standard-punctuation-lowercase','match-term-case-and-keyword-normalizer','OR-AND-reversed-phrase-gap','explicit-request-stop-zero-none-all','two-Explain-entrances-rewritten-query-and-alias-filter','filter-must-score-contribution','pure-filter-zero-score','should-default-optional-and-explicit-minimum','post-filter-and-query-filter-aggregation-scope','validate-two-term-OR','pointed-cleanup-and-rebuild']
if '--validate-only' not in sys.argv:
 # Separate targeted observations verify the repeated-create/write/delete prose.
 if '--repeatability-only' in sys.argv:report['repeatabilityRecoveryCleanup']=req('DELETE','/tut-l18-dsl?ignore_unavailable=true')
 report['repeatabilityChecks']=[]
 def observe(name,m,p,b=None):
  r=req(m,p,b);report['repeatabilityChecks'].append({'name':name,'method':m,'path':p,'body':b,**r});return r
 create=next(e for e in ops if e['id']=='ch18-00-setup');bulk=next(e for e in ops if e['id']=='ch18-01-bulk')
 assert observe('fresh-create',create['method'],create['path'],create['body'])['response']['acknowledged']
 mapping=observe('actual-mapping','GET','/tut-l18-dsl/_mapping')['response']['tut-l18-dsl']['mappings']
 # Mapping serialization omits search_analyzer when it equals analyzer.
 expectedMapping=json.loads(json.dumps(create['body']['mappings']));expectedMapping['properties']['title'].pop('search_analyzer')
 assert mapping==expectedMapping
 settings=observe('actual-settings','GET','/tut-l18-dsl/_settings?flat_settings=true')['response']['tut-l18-dsl']['settings']
 assert settings['index.refresh_interval']=='-1' and settings['index.requests.cache.enable']=='false' and settings['index.auto_expand_replicas']=='false'
 assert settings['index.default_pipeline']==settings['index.final_pipeline']=='_none' and settings['index.mapping.source.mode']=='stored'
 repeated=observe('repeat-create',create['method'],create['path'],create['body']);assert repeated['status']==400 and repeated['response']['error']['type']=='resource_already_exists_exception'
 fresh=observe('fresh-bulk',bulk['method'],bulk['path'],bulk['body']);again=observe('repeat-bulk',bulk['method'],bulk['path'],bulk['body'])
 assert all(i['index']['status']==201 and i['index']['result']=='created' for i in fresh['response']['items'])
 assert all(i['index']['status']==200 and i['index']['result']=='updated' for i in again['response']['items'])
 assert observe('cleanup','DELETE','/tut-l18-dsl')['response']['acknowledged']
 absent=observe('repeat-cleanup','DELETE','/tut-l18-dsl');assert absent['status']==404 and absent['response']['error']['type']=='index_not_found_exception'
else:
 assert len(report['repeatabilityChecks'])==8
report['postCleanup']=[{'path':'/'+name,**req('HEAD','/'+name)} for name in ['tut-l18-dsl','tut-l18-published']]
assert all(r['status']==404 for r in report['postCleanup'])
report['status']='pass';report['requestIdentityVerified']=True;report['experimentSha256']=hashlib.sha256((root/'experiments/ch18.js').read_bytes()).hexdigest();file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: two runs × 34 real registered operations; both chapter resources absent.')
