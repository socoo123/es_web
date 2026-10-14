"""Run the ordered ch30 cards twice; record actual local HTTP evidence."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,subprocess,hashlib,urllib.request,urllib.error
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
specs=json.loads(subprocess.check_output(['node','-e','global.window={};require("./experiments/ch30.js");console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))'],cwd=root))
def request(method,path,body=None):
 data=json.dumps(body,ensure_ascii=False).encode() if body is not None else None
 req=urllib.request.Request('http://localhost:9200'+path,data=data,method=method,headers={'Content-Type':'application/json'} if data else {})
 try:res=urllib.request.urlopen(req,timeout=30)
 except urllib.error.HTTPError as e:res=e
 raw=res.read().decode();return {'method':method,'path':path,'requestBody':body,'status':res.status,'headers':list(res.headers.items()),'body':json.loads(raw) if raw else None}
def usage(r):return {n:v.get('rest_actions',{}).get('search_action',0) for n,v in r['body']['nodes'].items()}
report={'status':'running','kind':'real-es-two-rounds','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'endpoint':'http://localhost:9200','auth':'anonymous','experimentSha256':hashlib.sha256((root/'experiments/ch30.js').read_bytes()).hexdigest(),'preflight':[],'rounds':[]}
def save(name='ch30-es-review.json'):(out/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
try:
 version=request('GET','/');report['preflight'].append(version)
 assert version['body']['version']['number']=='9.4.0' and version['body']['version']['lucene_version']=='10.4.0'
 assert version['body']['version']['build_hash']=='2e8528e92361c3399724226deaf2b46f933e925b'
 absent=request('HEAD','/tut-l30-docs');report['preflight'].append(absent);assert absent['status']==404,'Expected absent dedicated chapter index'
 for roundnum in [1,2]:
  row={'round':roundnum,'responses':[]};report['rounds'].append(row)
  for spec in specs:
   r=request(spec['method'],spec['path'],spec.get('body'));r['id']=spec['id'];row['responses'].append(r)
   id=spec['id'];b=r['body']
   expected=201 if id in ['ch30-02-doc1','ch30-07-doc2'] else 400 if id in ['ch30-04-no-route','ch30-05-illegal-type','ch30-06-window'] else 404 if id in ['ch30-17-get-nrt','ch30-19-cleanup-again'] else 200
   assert r['status']==expected,(id,r)
   if id=='ch30-01-setup':assert b['acknowledged'] and b['shards_acknowledged']
   if id=='ch30-15-health':assert b['status']=='green' and not b['timed_out'] and b['active_primary_shards']==1
   if id=='ch30-02-doc1':assert b['result']=='created' and b['forced_refresh']
   if id=='ch30-14-usage-before':baseline=usage(r)
   if id=='ch30-03-search-brown':assert b['hits']['total']['value']==1 and b['hits']['hits'][0]['_id']=='1' and b['hits']['hits'][0]['_score']>0
   if id=='ch30-04-no-route':assert isinstance(b['error'],str) and 'no handler found for uri' in b['error']
   if id=='ch30-05-illegal-type':assert 'No search type for [some_search_type]' in b['error']['reason']
   if id=='ch30-06-window':
    assert b['error']['type']=='search_phase_execution_exception' and b['error']['failed_shards'][0]['index']=='tut-l30-docs'
    assert '[10000] but was [10010]' in b['error']['root_cause'][0]['reason']
   if id=='ch30-07-doc2':assert b['result']=='created'
   if id=='ch30-08-search-purple':assert b['hits']['total']['value']==0
   if id=='ch30-09-get-doc2':assert b['found'] and b['_source']['title']=='purple lion'
   if id=='ch30-17-get-nrt':assert b['found'] is False
   if id=='ch30-10-refresh':assert b['_shards']=={'total':1,'successful':1,'failed':0}
   if id=='ch30-11-search-purple2':assert b['hits']['total']['value']==1 and b['hits']['hits'][0]['_id']=='2'
   if id=='ch30-18-count':assert b['count']==2
   if id=='ch30-16-default-search':assert b['hits']['total']['value']==2 and len(b['hits']['hits'])==2
   if id=='ch30-20-tasks':assert b['nodes']=={}
   if id=='ch30-12-usage':
    delta={n:v-baseline[n] for n,v in usage(r).items()};assert list(delta.values())==[5],delta;row['searchActionDelta']=delta
   if id=='ch30-13-cleanup':assert b['acknowledged']
   if id=='ch30-19-cleanup-again':assert b['error']['type']=='index_not_found_exception'
   r['assertions']='pass';save()
 report['status']='pass';report['operationCountPerRound']=len(specs);report['indexAbsentAfter']=request('HEAD','/tut-l30-docs');assert report['indexAbsentAfter']['status']==404
 report['limitations']=['single node/single shard; no network phase tracing','source tests read, Gradle not run','no concurrent search traffic during usage delta','no security-enabled, PIT, rank, kNN or cross-cluster API tests']
 save();print('PASS: 20 ordered operations x 2 rounds; both usage deltas=5; chapter index absent.')
except Exception as e:
 report['status']='fail';report['failure']=repr(e);save('ch30-es-failure.json');raise
