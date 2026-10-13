"""Run the actual ordered chapter cards twice on a dedicated anonymous 9.4.0 node.
Preserve full requests/responses, wait for observed states, and restore poll in finally.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import json,time,hashlib,subprocess
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
specs=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch28.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root))
assert [s['id'] for s in specs]==json.loads((out/'ch28-operations-order.json').read_text())
report={'status':'running','endpoint':'http://localhost:9200','startedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'experimentSha256':hashlib.sha256((root/'experiments/ch28.js').read_bytes()).hexdigest(),'rounds':[]}
def save(): (out/'ch28-es-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def req(m,path,body=None):
 b=None if body is None else json.dumps(body).encode();r=Request('http://localhost:9200'+path,data=b,method=m,headers={'Content-Type':'application/json'})
 try:
  with urlopen(r,timeout=40) as f: status=f.status;raw=f.read().decode()
 except HTTPError as e:status=e.code;raw=e.read().decode()
 try:data=json.loads(raw)
 except ValueError:data=raw
 return {'method':m,'path':path,'body':body,'status':status,'response':data}
def row(id):return next(s for s in specs if s['id']=='ch28-'+id)
def run(id,predicate=None,timeout=180):
 s=row(id);start=time.monotonic()
 while True:
  r=req(s['method'],s['path'],s.get('body'));r['id']=s['id'];r['elapsed']=round(time.monotonic()-start,3);cur['requests'].append(r);save()
  if not predicate or predicate(r):return r['response']
  assert time.monotonic()-start<timeout,(id,r)
  time.sleep(2)
def ok(r):return r['status']==200
names=['tut-l28-logs-000001','tut-l28-logs-000002','tut-l28-safe-000001']
for name in names:assert req('HEAD','/'+name)['status']==404,('existing resource',name)
for path in ['/_ilm/policy/tut-l28-policy','/_ilm/policy/tut-l28-safe-policy','/_index_template/tut-l28-tpl']:assert req('GET',path)['status']==404,('existing resource',path)
baseline=req('GET','/_cluster/settings?include_defaults=true&flat_settings=true')['response'];original=baseline.get('transient',{}).get('indices.lifecycle.poll_interval');report['baselineSettings']=baseline
protection=next((baseline.get(k,{}).get('action.destructive_requires_name') for k in ['transient','persistent','defaults'] if 'action.destructive_requires_name' in baseline.get(k,{})),None);report['deletionProtection']=protection;assert str(protection).lower()=='true','deletion protection required'
def hot(r,name,version=1):
 if r['status']!=200:return False
 d=r['response']['indices'][name];assert d.get('step')!='ERROR',d
 return d.get('phase')=='hot' and d.get('step')=='check-rollover-ready' and d.get('phase_execution',{}).get('version')==version
try:
 for n in range(1,3):
  cur={'round':n,'requests':[],'supplemental':[]};report['rounds'].append(cur)
  v=run('00-version');assert v['version']['number']=='9.4.0' and v['version']['lucene_version']=='10.4.0' and v['version']['build_hash']=='2e8528e92361c3399724226deaf2b46f933e925b'
  assert run('00-mode')['operation_mode']=='RUNNING';run('00-settings')
  for id in ['01-poll','02-policy','03-template','04-index']:assert run(id)['acknowledged']
  h=run('21-health');assert h['status']=='green' and not h['timed_out']
  settings=run('22-settings')['tut-l28-logs-000001']['settings'];assert settings['index.number_of_shards']=='1' and settings['index.number_of_replicas']=='0' and settings['index.refresh_interval']=='-1' and settings['index.lifecycle.name']=='tut-l28-policy'
  d=run('23-dry-empty');assert d['dry_run'] and not d['rolled_over'] and not next(v for k,v in d['conditions'].items() if 'min_docs' in k)
  assert run('05-doc')['result']=='created';run('06-explain-new');run('07-explain-hot',lambda r:hot(r,names[0]))
  d=run('24-dry-one',lambda r:r['status']==200 and next(v for k,v in r['response']['conditions'].items() if 'max_age' in k));assert not d['rolled_over']
  assert run('08-policy-v2')['acknowledged'];p=run('09-policy-get')['tut-l28-policy'];assert p['version']==2 and 'forcemerge' in p['policy']['phases']['hot']['actions']
  d=run('10-explain-after')['indices'][names[0]];assert d['phase_execution']['version']==1 and set(d['phase_execution']['phase_definition']['actions'])=={'rollover'}
  assert run('25-release')['result']=='created';assert run('26-count')['count']==2
  run('11-wait-cat',lambda r:r['status']==200 and names[1] in r['response'])
  a=run('12-alias-flip',lambda r:r['status']==200 and names[1] in r['response']);assert not a[names[0]]['aliases']['tut-l28-logs']['is_write_index'] and a[names[1]]['aliases']['tut-l28-logs']['is_write_index']
  def both(r):
   if r['status']!=200:return False
   ds=r['response']['indices'];return ds.get(names[0],{}).get('step')=='complete' and hot({'status':200,'response':r['response']},names[1],2)
  d=run('13-explain-both',both)['indices'];assert d[names[0]]['phase_execution']['version']==1 and 'forcemerge' not in d[names[0]]['phase_execution']['phase_definition']['actions'] and 'forcemerge' in d[names[1]]['phase_execution']['phase_definition']['actions'];assert d[names[0]]['lifecycle_date_millis']>=d[names[0]]['index_creation_date_millis']
  s=run('27-old-settings');assert s[names[0]]['settings']['index.lifecycle.indexing_complete']=='true' and s[names[1]]['settings']['index.lifecycle.name']=='tut-l28-policy'
  assert run('28-new-doc')['_index']==names[1]
  d=run('14-delete-inuse');assert 'in use by one or more indices' in d['error']['reason'];assert cur['requests'][-1]['status']==400
  d=run('15-wildcard');assert 'Wildcard expressions' in d['error']['reason'];assert cur['requests'][-1]['status']==400
  for id in ['29-safe-policy','30-safe-index']:assert run(id)['acknowledged']
  run('31-safe-hot',lambda r:hot(r,names[2]));assert run('32-safe-update')['acknowledged']
  d=run('33-safe-explain',lambda r:hot(r,names[2],2))['indices'][names[2]];assert d['phase_execution']['phase_definition']['actions']['rollover']['max_age']=='10m'
  # Genuine extra observations of repeat semantics and a no-op policy PUT.
  r=req('PUT','/_ilm/policy/tut-l28-safe-policy',row('32-safe-update')['body']);cur['supplemental'].append(r);assert r['status']==200
  r=req('GET','/_ilm/policy/tut-l28-safe-policy');cur['supplemental'].append(r);assert r['response']['tut-l28-safe-policy']['version']==2
  r=req('PUT','/tut-l28-logs/_doc/after?refresh=true',{'msg':'l28-after'});cur['supplemental'].append(r);assert r['status']==200 and r['response']['result']=='updated' and r['response']['_index']==names[1]
  r=req('PUT','/tut-l28-logs-000001',row('04-index')['body']);cur['supplemental'].append(r);assert r['status']==400 and r['response']['error']['type']=='resource_already_exists_exception'
  for id in ['34-safe-del-index','35-safe-del-policy','16-del-1','17-del-2','18-del-tpl-policy','19-del-policy']:assert run(id)['acknowledged']
  # The page assumes no initial transient override; runner restores actual baseline unconditionally.
  restore=row('20-restore').copy();restore['body']={'transient':{'indices.lifecycle.poll_interval':original}}
  r=req(restore['method'],restore['path'],restore['body']);r['id']=restore['id'];cur['requests'].append(r);assert r['response']['acknowledged']
  run('36-final-head');assert cur['requests'][-1]['status']==404
  restored=run('37-settings-check');assert restored.get('transient',{}).get('indices.lifecycle.poll_interval')==original
  for name in names:
   r=req('HEAD','/'+name);cur['supplemental'].append(r);assert r['status']==404
  assert set(x['id'] for x in cur['requests'])==set(s['id'] for s in specs)
  cur['status']='pass';save();print('Round',n,'PASS: 40 cards, observed waits, explicit cleanup and poll restore.',flush=True)
 report['status']='pass'
except Exception as e:
 report['status']='fail';report['error']=repr(e);raise
finally:
 report['finallyRestore']=req('PUT','/_cluster/settings',{'transient':{'indices.lifecycle.poll_interval':original}})
 if report['status']!='pass':
  report['failureCleanup']=[req('DELETE','/'+name) for name in names]+[req('DELETE',p) for p in ['/_index_template/tut-l28-tpl','/_ilm/policy/tut-l28-policy','/_ilm/policy/tut-l28-safe-policy']]
 save()
