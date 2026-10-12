"""Execute ch16's registered requests twice; only its two indexes are mutated."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,subprocess,urllib.request,urllib.error,hashlib,os,sys
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
endpoint=os.environ.get('ES_ENDPOINT','http://localhost:9200').rstrip('/')
ops=json.loads(subprocess.check_output(['node','-e','global.window={};require(process.argv[1]);console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))',str(root/'experiments/ch16.js')]))
def request(m,p,b=None):
 data=b.encode() if isinstance(b,str) else json.dumps(b).encode() if b is not None else None
 req=urllib.request.Request(endpoint+p,data=data,method=m,headers={'Content-Type':'application/x-ndjson' if '_bulk' in p else 'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=30) as r:s=r.status;raw=r.read().decode()
 except urllib.error.HTTPError as e:s=e.code;raw=e.read().decode()
 try:v=json.loads(raw)
 except json.JSONDecodeError:v=raw
 return {'status':s,'response':v}
identity=[{k:o.get(k) for k in ['id','method','path','body']} for o in ops]
if '--validate-only' in sys.argv:
 report=json.loads((out/'ch16-es-review.json').read_text())
 for run in report['runs']:assert [{k:r.get(k) for k in ['id','method','path','body']} for r in run['operations']]==identity
else:
 version=request('GET','/');v=version['response']['version'];assert v['number']=='9.4.0' and v['lucene_version']=='10.4.0' and v['build_hash']=='2e8528e92361c3399724226deaf2b46f933e925b'
 nodes=request('GET','/_nodes?filter_path=nodes.*.version');assert len(nodes['response']['nodes'])==1
 report={'kind':'real-es-api','endpoint':endpoint,'reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'version':version,'nodes':nodes,'experimentSha256':hashlib.sha256((root/'experiments/ch16.js').read_bytes()).hexdigest(),'preCleanup':[],'runs':[]}
 for name in ['tut-l16-qtf','tut-l16-single']:report['preCleanup'].append({'path':'/'+name,**request('DELETE','/'+name+'?ignore_unavailable=true')})
 for n in [1,2]:
  run={'run':n,'operations':[]};report['runs'].append(run)
  for spec in ops:
   result=request(spec['method'],spec['path'],spec.get('body'));run['operations'].append({**{k:spec.get(k) for k in ['id','method','path','body']},**result})
  report['status']='responses-collected-validation-pending';(out/'ch16-es-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for run in report['runs']:
 rows={r['id']:r for r in run['operations']}
 def R(n):return next(r['response'] for id,r in rows.items() if id.startswith(f'ch16-{n:02}-'))
 for id,row in rows.items():
  num=int(id.split('-')[1]);expected={6:400,9:201,22:404,28:404}.get(num,200)
  assert row['status']==expected,(run['run'],id,row)
 assert R(0)['acknowledged'] and R(24)['acknowledged']
 assert R(15)['status']=='green' and not R(15)['timed_out'] and R(15)['active_primary_shards']==3
 settings=R(16)['tut-l16-qtf']['settings'];assert settings['index.refresh_interval']=='-1' and settings['index.max_result_window']=='10000' and settings['index.number_of_shards']=='3'
 for n,count in [(1,30),(25,2)]:assert not R(n)['errors'] and len(R(n)['items'])==count and all(x['index']['status']==201 and x['index']['result']=='created' for x in R(n)['items'])
 shards=R(2);assert len(shards)==3 and all(s['state']=='STARTED' and s['prirep']=='p' for s in shards)
 assert sorted(int(s['docs']) for s in shards)==[9,9,12]
 assert R(3)['_shards']=={'total':3,'successful':3,'skipped':0,'failed':0} and R(3)['hits']['total']=={'value':30,'relation':'eq'} and len(R(3)['hits']['hits'])==10
 for n in [4,5,17]:
  ps=R(n)['profile']['shards'];assert len(ps)==3 and all(s.get('searches') for s in ps)
  fs=[s['fetch'] for s in ps if 'fetch' in s];assert len(fs)>=1
  if n==4:assert sum(f['breakdown']['load_stored_fields_count'] for f in fs)==10
  if n in [5,17]:assert len(fs)==1 and len(R(n)['hits']['hits'])==1
  if n==17:assert all('_source' not in h for h in R(n)['hits']['hits'])
 err=R(6)['error'];assert err['type']=='search_phase_execution_exception' and err['reason']=='all shards failed' and err['root_cause'][0]['type']=='illegal_argument_exception' and '[10010]' in err['root_cause'][0]['reason']
 assert R(7)['hits']['hits']==[] and R(7)['hits']['total']['value']==30
 def ids(n):return [h['_id'] for h in R(n)['hits']['hits']]
 assert ids(8)==list(map(str,range(21,31))) and ids(19)==list(map(str,range(1,6))) and ids(20)==list(map(str,range(6,11)))
 assert R(19)['hits']['hits'][-1]['sort']==[5] and R(20)['hits']['hits'][-1]['sort']==[10]
 s=R(18);assert s['hits']['hits']==[] and s['hits']['total']['value']==30 and all('fetch' not in p for p in s['profile']['shards'])
 assert s['aggregations']['n_stats']=={'count':30,'min':1.0,'max':30.0,'avg':15.5,'sum':465.0}
 assert R(22)['result']=='not_found' and R(23)['count']==0 and R(9)['result']=='created' and R(10)['found'] and R(11)['count']==0 and R(21)['count']==1
 assert R(12)['_shards']=={'total':3,'successful':3,'failed':0}
 s=R(26);assert s['_shards']['total']==s['_shards']['successful']==1 and ids(26)==['2'] and s['hits']['hits'][0]['_source']['n']==2 and s['profile']['shards'][0]['searches'] and s['profile']['shards'][0]['fetch']
 assert R(13)['acknowledged'] and R(27)['acknowledged']
 run['status']='pass';run['verified']=['29-status-codes','explicit-settings-and-health','12/9/9-distribution','global-page-ten','three-query-profiles','size-one-single-fetch','source-disabled-fetch-retained','size-zero-aggregation-without-fetch','window-root-cause-and-empty-valid-page','sorted-last-page','search-after-two-batches','reset-GET-visible-COUNT-zero-refresh-COUNT-one','single-shard-query-and-fetch','both-indexes-cleaned']
report['postCleanup']=[{'path':'/'+name,**request('HEAD','/'+name)} for name in ['tut-l16-qtf','tut-l16-single']]
assert all(r['status']==404 for r in report['postCleanup'])
report['reviewedExperimentSha256']=hashlib.sha256((root/'experiments/ch16.js').read_bytes()).hexdigest();report['requestIdentityVerified']=True;report['status']='pass'
(out/'ch16-es-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: two rounds of 29 registered requests; both chapter indexes now absent.')
