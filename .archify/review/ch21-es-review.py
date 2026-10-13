"""Execute the current chapter registry twice against real ES, then clean resources.
Requires both chapter indices absent. No global setting writes or mocked responses.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,urllib.request,urllib.error,subprocess,hashlib,sys
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
endpoint='http://localhost:9200';indices=['tut-l21-docs','tut-l21-ver']
ops=json.loads(subprocess.check_output(['node','-e','global.window={};require("./experiments/ch21.js");process.stdout.write(JSON.stringify(Object.values(window.ESEXPERIMENTS)))'],cwd=root))
report={'kind':'real-es-api','endpoint':endpoint,'authentication':'anonymous','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'experimentSha256':hashlib.sha256((root/'experiments/ch21.js').read_bytes()).hexdigest(),'status':'running','rounds':[],'supplemental':[]}
def save(): (out/'ch21-es-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def request(method,path,body=None):
 data=None if body is None else json.dumps(body).encode()
 r=urllib.request.Request(endpoint+path,data=data,method=method,headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(r,timeout=20) as resp:status=resp.status;raw=resp.read().decode()
 except urllib.error.HTTPError as e:status=e.code;raw=e.read().decode()
 return {'status':status,'response':json.loads(raw) if raw else None}
def observe(name,method,path,body=None):
 r=request(method,path,body);report['supplemental'].append({'name':name,'method':method,'path':path,'body':body,**r});save();return r
report['environment']=request('GET','/');v=report['environment']['response']['version'];assert v['number']=='9.4.0' and v['lucene_version']=='10.4.0' and v['build_hash']=='2e8528e92361c3399724226deaf2b46f933e925b'
report['nodes']=request('GET','/_nodes?filter_path=_nodes,nodes.*.roles');assert report['nodes']['response']['_nodes']['total']==1
report['clusterSettingsBefore']=request('GET','/_cluster/settings?flat_settings=true')
assert all(request('HEAD','/'+name)['status']==404 for name in indices),'Existing chapter resources: clean explicitly before running.'
try:
 for round_num in [1,2]:
  run={'round':round_num,'requests':[],'status':'running'};report['rounds'].append(run);R={}
  for op in ops:
   r=request(op['method'],op['path'],op.get('body'));R[op['id']]=r;run['requests'].append({'id':op['id'],'method':op['method'],'path':op['path'],'body':op.get('body'),**r});save()
   num=int(op['id'].split('-')[1]);expected=404 if num in [25,28] else 201 if num==10 else 200
   assert r['status']==expected,(op['id'],r)
   if num==27 and round_num==1:
    # Additional observations occur after C8 and before the four cleanup cards.
    created=next(e for e in ops if e['id']=='ch21-00-setup')
    zero=observe('wait-zero-invalid','GET','/_cluster/state/version?wait_for_metadata_version=0&wait_for_timeout=1ms');assert zero['status']==400 and 'should be >= 1' in zero['response']['error']['reason']
    repeat=observe('repeat-create','PUT','/tut-l21-docs',created['body']);assert repeat['status']==400 and repeat['response']['error']['type']=='resource_already_exists_exception'
    settings=observe('explicit-settings','GET','/tut-l21-docs/_settings?flat_settings=true')['response']['tut-l21-docs']['settings']
    assert all(settings['index.'+k]==str(val) for k,val in created['body']['settings'].items())
    mapping=observe('strict-keyword-mapping','GET','/tut-l21-docs/_mapping')['response']['tut-l21-docs']['mappings'];assert mapping['dynamic']=='strict' and mapping['properties']['title']['type']=='keyword'
    before=observe('before-repeat-write','GET','/_cluster/state/version')['response']
    write=next(e for e in ops if e['id']=='ch21-10-write-doc')
    repeat=observe('repeat-declared-write',write['method'],write['path'],write['body']);assert repeat['status']==200 and repeat['response']['result']=='updated' and repeat['response']['_version']==2
    after=observe('after-repeat-write','GET','/_cluster/state/version')['response'];assert (before['version'],before['state_uuid'])==(after['version'],after['state_uuid'])
    get=observe('document-version-two','GET','/tut-l21-docs/_doc/1')['response'];assert get['_version']==2 and get['found']
    assert observe('strict-unknown-field','PUT','/tut-l21-docs/_doc/bad',{'unknown':1})['status']==400
    assert observe('unknown-field-not-written','GET','/tut-l21-docs/_doc/bad')['status']==404
    assert observe('set-local-read-only-block','PUT','/tut-l21-docs/_settings',{'index.blocks.read_only':True})['response']['acknowledged']
    block=observe('read-only-block-visible','GET','/_cluster/state/blocks/tut-l21-docs')['response'];assert block['blocks']['indices']['tut-l21-docs']
    assert observe('green-can-be-read-only','GET','/_cluster/health/tut-l21-docs')['response']['status']=='green'
    assert observe('read-only-write-rejected','PUT','/tut-l21-docs/_doc/blocked',{'title':'blocked'})['status']==403
    assert observe('restore-read-only-setting','PUT','/tut-l21-docs/_settings',{'index.blocks.read_only':False})['response']['acknowledged']
    assert observe('blocks-empty-again','GET','/_cluster/state/blocks/tut-l21-docs')['response']['blocks']=={}
  def r(n):return R[next(e['id'] for e in ops if int(e['id'].split('-')[1])==n)]['response']
  for n in [0,8]:assert r(n)['acknowledged'] and r(n)['shards_acknowledged']
  for n in [17,19]:assert r(n)['status']=='green' and not r(n)['timed_out'] and r(n)['active_primary_shards']==1
  assert not ({'version','state_uuid','master_node'}&r(1).keys())
  assert r(1)['metadata']['indices']['tut-l21-docs']['settings']['index']=={'number_of_shards':'1','number_of_replicas':'0'}
  shard=r(1)['routing_table']['indices']['tut-l21-docs']['shards']['0'][0];assert shard['primary'] and shard['state']=='STARTED'
  assert r(2)['version'] and r(2)['state_uuid'] and r(2)['master_node']==r(3)['master_node']==r(18)['master_node']
  assert r(18)['master_node'] in r(18)['nodes'] and len(r(18)['nodes'])==1
  assert r(4)['blocks']=={}
  coordination=r(5)['metadata']['cluster_coordination'];assert isinstance(coordination['term'],int) and 'config' not in coordination and all(k in coordination for k in ['last_accepted_config','last_committed_config','voting_config_exclusions'])
  assert isinstance(r(6)['tasks'],list)
  v1,v2,v3=r(7),r(9),r(11);assert v2['version']>v1['version'] and v2['state_uuid']!=v1['state_uuid'];assert (v2['version'],v2['state_uuid'])==(v3['version'],v3['state_uuid'])
  assert r(10)['result']=='created' and r(10)['_shards']['successful']==1 and r(20)['_version']==1 and r(20)['_source']['title']=='cluster-state-is-a-snapshot'
  assert r(12)['acknowledged'] and r(13)['version']>v3['version'] and r(13)['state_uuid']!=v3['state_uuid']
  assert 'version' not in r(13)['metadata'] and r(13)['metadata']['indices']['tut-l21-docs']['settings']['index']['refresh_interval']=='5s'
  assert r(21)['acknowledged'] and (r(22)['version'],r(22)['state_uuid'])==(r(13)['version'],r(13)['state_uuid'])
  assert r(23)['wait_for_timed_out']==False and 'version' in r(23)
  assert r(24)=={'wait_for_timed_out':True,'cluster_name':report['environment']['response']['cluster_name']}
  assert r(26)['acknowledged'] and r(27)['tut-l21-docs']['settings']['index']['refresh_interval']=='1s'
  assert r(14)['acknowledged'] and r(15)['acknowledged']
  run.update(status='pass',observations={'V1':v1,'V2':v2,'V3':v3,'createVersionDelta':v2['version']-v1['version'],'changedSettingVersion':r(13)['version'],'noopVersion':r(22)['version'],'term':coordination['term'],'pendingTasks':r(6)['tasks'],'restMetadataVersionPresent':False});save()
 for name in indices:
  repeat=observe('repeat-cleanup-'+name,'DELETE','/'+name);assert repeat['status']==404 and repeat['response']['error']['type']=='index_not_found_exception'
 report['clusterSettingsAfter']=request('GET','/_cluster/settings?flat_settings=true');assert report['clusterSettingsAfter']==report['clusterSettingsBefore']
 report['finalHead']={name:request('HEAD','/'+name) for name in indices};assert all(r['status']==404 for r in report['finalHead'].values())
 report['status']='pass';save();print('PASS: two real rounds ×29 exact registered requests,',len(report['supplemental']),'supplemental requests; global settings unchanged; both indices absent.')
except Exception as e:
 report['status']='fail';report['failure']=str(e);save();raise
