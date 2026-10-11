"""Run ch15's actual registered operations twice with explicit cleanup.
Only this chapter's two tut-l15 indexes are mutated. Requires ES 9.4.0.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess,json,urllib.request,urllib.error,time,hashlib,os,sys
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
endpoint=os.environ.get('ES_ENDPOINT','http://localhost:9200').rstrip('/')
script='const fs=require("fs"),vm=require("vm");const c={window:{}};vm.runInNewContext(fs.readFileSync(process.argv[1],"utf8"),c);console.log(JSON.stringify(Object.values(c.window.ESEXPERIMENTS)));'
ops=json.loads(subprocess.check_output(['node','-e',script,str(root/'experiments/ch15.js')]))
def request(method,path,body=None):
 data=None if body is None else (body.encode() if isinstance(body,str) else json.dumps(body).encode())
 req=urllib.request.Request(endpoint+path,data=data,method=method,headers={'Content-Type':'application/json'})
 started=time.monotonic()
 try:
  with urllib.request.urlopen(req,timeout=60) as response:status=response.status;value=response.read().decode()
 except urllib.error.HTTPError as e:status=e.code;value=e.read().decode()
 try:value=json.loads(value)
 except json.JSONDecodeError:pass
 return {'status':status,'response':value,'elapsedMs':round((time.monotonic()-started)*1000)}
if '--validate-only' in sys.argv:
 report=json.loads((out/'ch15-es-review.json').read_text())
 current=[{'id':o['id'],'method':o['method'],'path':o['path'],'body':o.get('body')} for o in ops]
 for run in report['runs']:
  recorded=[{k:row[k] for k in ['id','method','path','body']} for row in run['operations']]
  assert recorded==current,'Registered request bytes changed; rerun actual APIs.'
 report['reviewedExperimentSha256']=hashlib.sha256((root/'experiments/ch15.js').read_bytes()).hexdigest()
 report['requestIdentityVerified']=True
else:
 version=request('GET','/');assert version['status']==200 and version['response']['version']['number']=='9.4.0' and version['response']['version']['lucene_version']=='10.4.0',version
 nodes=request('GET','/_nodes?filter_path=nodes.*.roles,nodes.*.version');assert len(nodes['response']['nodes'])==1,nodes
 report={'kind':'real-es-api','endpoint':endpoint,'reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'version':version,'nodes':nodes,'experimentSha256':hashlib.sha256((root/'experiments/ch15.js').read_bytes()).hexdigest(),'preCleanup':[],'runs':[]}
 for name in ['tut-l15-route','tut-l15-req']:report['preCleanup'].append({'path':'/'+name+'?ignore_unavailable=true',**request('DELETE','/'+name+'?ignore_unavailable=true')})
 for run in [1,2]:
  rows=[]
  for spec in ops:
   result=request(spec['method'],spec['path'],spec.get('body'));row={'id':spec['id'],'method':spec['method'],'path':spec['path'],'body':spec.get('body'),**result};rows.append(row)
   # The JSON records every actual response; stdout stays concise.
   if spec['id']=='ch15-b-yellow-again':
    for _ in range(10):
     if result['response']['status']=='yellow' and result['response']['unassigned_shards']==3:break
     time.sleep(.2);result=request(spec['method'],spec['path']);row.update(result)
  report['runs'].append({'run':run,'operations':rows})
  report['status']='responses-collected-validation-pending'
  (out/'ch15-es-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for run in report['runs']:
 rows={r['id']:r for r in run['operations']}
 errors={'ch15-a-cross-miss':404,'ch15-11-final-wall':400,'ch15-13-req-missing':400,'ch15-c-get-missing':400,'ch15-d-closed-get':400}
 created=['ch15-02-put-routing','ch15-a-put-cross','ch15-c-put']
 for id,row in rows.items():assert row['status']==errors.get(id,201 if id in created else 200),(run['run'],id,row)
 def response(id):return rows[id]['response']
 for id in ['ch15-a-yellow','ch15-b-yellow-again']:
  value=response(id);assert not value['timed_out'] and value['status']=='yellow' and value['active_primary_shards']==3 and value['unassigned_shards']==3,value
 for id in ['ch15-09-health-green','ch15-c-health','ch15-d-open-health']:
  value=response(id);assert not value['timed_out'] and value['status']=='green' and value['active_primary_shards']==3 and value['unassigned_shards']==0,value
 for id,shard in [('ch15-05-ss-routing',0),('ch15-a-id-shard',0),('ch15-a-cross-shard',2)]:
  groups=response(id)['shards'];assert len(groups)==1 and groups[0][0]['shard']==shard,(id,groups)
 assert len(response('ch15-04-ss-all')['shards'])==3
 assert response('ch15-02-put-routing')['_shards']=={'total':2,'successful':1,'failed':0}
 for id in ['ch15-06-get-miss','ch15-07-get-hit','ch15-a-cross-hit','ch15-b-after-final','ch15-c-get-hit','ch15-d-open-get']:
  value=response(id);assert value['found'] and value['_routing']=='brown',(id,value)
 assert not response('ch15-a-cross-miss')['found']
 value=response('ch15-a-search-all');assert value['hits']['total']['value']==2 and value['_shards']['total']==3 and value['_shards']['failed']==0
 value=response('ch15-a-search-wrong');assert value['hits']['total']['value']==0 and value['_shards']['total']==1
 value=response('ch15-c-search-all');assert value['hits']['total']['value']==1 and value['_shards']['total']==3
 settings=response('ch15-b-settings')['tut-l15-route']['settings'];assert settings['index.number_of_shards']=='3' and settings['index.number_of_replicas']=='0' and settings['index.version.created']=='9094000'
 value=response('ch15-11-final-wall')['error'];assert value['type']=='illegal_argument_exception' and 'non dynamic setting(s) [[index.number_of_shards]]' in value['reason']
 for id in ['ch15-13-req-missing','ch15-c-get-missing']:assert response(id)['error']['type']=='routing_missing_exception' and 'routing is required for' in response(id)['error']['reason']
 value=response('ch15-d-closed-get')['error'];assert value['type']=='index_closed_exception' and value['reason']=='closed'
 assert response('ch15-d-open-get')['_source']['title']=='routing required'
 shards=response('ch15-d-recovery')['tut-l15-req']['shards'];assert len(shards)==3 and all(x['type']=='EXISTING_STORE' and x['stage']=='DONE' for x in shards)
 assert all(response(id)['acknowledged'] for id in ['ch15-14-cleanup-route','ch15-15-cleanup-req'])
 run['status']='pass';run['verified']=['40-status-codes','0/0/2-target-shards','same-shard-get-hit','cross-shard-404-and-routing-recovery','search-all-two-hits-vs-routed-zero','yellow-green-yellow-index-health','Final-rejected-settings-preserved-and-readable','routing-required-write-and-get-400','required-search-without-routing','closed-get-index-resolution-400','reopen-data-preserved-EXISTING_STORE-DONE','two-explicit-cleanups']
report['postCleanup']=[{'path':'/'+name,**request('HEAD','/'+name)} for name in ['tut-l15-route','tut-l15-req']]
assert all(x['status']==404 for x in report['postCleanup'])
report['status']='pass'
(out/'ch15-es-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 40 actual operations × 2 runs; predicted routing, errors, health and reopen behavior match; both chapter indexes absent after cleanup.',flush=True)
