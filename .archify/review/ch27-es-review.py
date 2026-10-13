"""Real ES9.4.0 requests: first run, cleanup rebuild, and bounded repeat observations."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from datetime import datetime
from zoneinfo import ZoneInfo
import json,subprocess,hashlib,math
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch27.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root))
report={'kind':'real-es-two-round-review','endpoint':'http://localhost:9200','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'rounds':[],'supplemental':[],'status':'running','authentication':'anonymous','sourceCommit':'2e8528e92361c3399724226deaf2b46f933e925b'}
def save(): (out/'ch27-es-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def request(e,bucket):
 b=e.get('body');data=None if b is None else (b if isinstance(b,str) else json.dumps(b)).encode()
 r=Request(report['endpoint']+e['path'],data=data,method=e['method'],headers={'Content-Type':'application/x-ndjson' if '_bulk' in e['path'] else 'application/json'})
 try:resp=urlopen(r,timeout=90)
 except HTTPError as err:resp=err
 raw=resp.read().decode();obj=json.loads(raw) if raw else None
 rec={'id':e['id'],'method':e['method'],'path':e['path'],'body':b,'httpStatus':resp.status,'raw':raw,'response':obj};bucket.append(rec);save()
 return resp.status,obj,rec
expected={'ch27-03-main':[[200]],'ch27-05-case':[[200]],'ch27-06-gte':[[175]],'ch27-07-nowhere':[[150]],'ch27-12-sort-keep':[['e',250],['d',200]],'ch27-a-limit-before':[[225]],'ch27-a-limit-after':[[200]],'ch27-c-values':[[70/3,70,3,4]],'ch27-c-empty':[[None,0]],'ch27-d-before':[[5]],'ch27-d-after':[[225]],'ch27-d-restored':[[200,3]]}
def values_equal(a,b):
 assert len(a)==len(b),(a,b)
 for x,y in zip(a,b):
  assert len(x)==len(y),(x,y)
  for v,w in zip(x,y):assert math.isclose(v,w,rel_tol=1e-10,abs_tol=1e-10) if isinstance(w,(int,float)) else v==w,(v,w)
def verify(e,status,obj):
 id=e['id'];wanted=404 if e['method']=='HEAD' else 405 if id in ['ch27-04-wrong-path','ch27-b-wrong-method','ch27-13-async-route'] else 400 if id=='ch27-a-type-error' else 201 if id=='ch27-d-write' else 200
 assert status==wanted,(id,status,obj)
 if e['method']=='HEAD':return
 if id=='ch27-pre-version':assert obj['version']['number']=='9.4.0' and obj['version']['lucene_version']=='10.4.0' and obj['version']['build_hash']==report['sourceCommit']
 if 'health' in id:assert obj['status']=='green' and obj['timed_out'] is False and obj['active_primary_shards']==1
 if 'bulk' in id:assert obj['errors'] is False and all(x['index']['status']==201 and x['index']['result']=='created' for x in obj['items'])
 if id.endswith('setup'):assert obj['acknowledged'] is True
 if id=='ch27-a-config':
  x=obj['tut-l27-pages'];assert x['settings']['index']['refresh_interval']=='-1' and x['settings']['index']['number_of_shards']=='1' and x['mappings']['dynamic']=='strict'
 if id in ['ch27-a-count','ch27-c-count']:assert obj['count']==(5 if id=='ch27-a-count' else 4)
 if id in expected:values_equal(obj['values'],expected[id]);assert obj['is_partial'] is False
 if id=='ch27-03-main':assert obj['columns']==[{'name':'avg(views)','type':'double'}]
 if id=='ch27-05-case':assert obj['columns'][0]['name']=='AVG(views)'
 if id=='ch27-08-profile':
  assert obj['values']==[[200.0]] and obj['is_partial'] is False
  text=json.dumps(obj['profile'])
  for tag in ['mode=INITIAL','mode=FINAL','SumLong','CountAggregator','DivDoublesEvaluator']:assert tag in text,(id,tag)
  assert 'FilterOperator' not in text
 if id=='ch27-a-type-error':assert obj['error']['type']=='verification_exception'
 if id.startswith('ch27-09') or id.startswith('ch27-10') or id.startswith('ch27-11') or id=='ch27-b-size-one':
  assert obj['aggregations']['avg_views']['value']==(175 if id=='ch27-11-dsl-gte' else 200)
  hits=obj['hits']['hits'];assert len(hits)==(3 if id=='ch27-10-dsl-hits' else 1 if id=='ch27-b-size-one' else 0)
  if hits:assert all('_source' in h for h in hits)
 if status==405:assert 'Incorrect HTTP method' in obj['error'] and 'allowed:' in obj['error']
 if id=='ch27-d-score':assert {r[0] for r in obj['values']}=={'a','b'} and all(r[1]>0 for r in obj['values']) and obj['columns'][1]['type']=='double'
 if id=='ch27-d-get':assert obj['found'] is True and obj['_source']['views']==300
 if id=='ch27-d-refresh':assert obj['_shards']['failed']==0
 if id=='ch27-d-reset':assert obj['result']=='deleted'
 if id in ['ch27-14-cleanup','ch27-clean-values-delete']:assert obj['acknowledged'] is True
try:
 for run in [1,2]:
  row={'run':run,'records':[]};report['rounds'].append(row)
  for e in ops:
   status,obj,rec=request(e,row['records']);verify(e,status,obj);rec['verification']='pass'
  row['status']='pass';save();print(f'Round {run}: 42 real requests PASS',flush=True)
 # Rebuild for repeat/error observations, then leave resources absent.
 for id in ['ch27-01-setup','ch27-a-health','ch27-02-bulk']:
  e=next(e for e in ops if e['id']==id);status,obj,rec=request(e,report['supplemental']);verify(e,status,obj);rec['verification']='pass'
 e=next(e for e in ops if e['id']=='ch27-01-setup');status,obj,rec=request({**e,'id':'repeat-create'},report['supplemental']);assert status==400 and obj['error']['type']=='resource_already_exists_exception';rec['verification']='pass'
 e=next(e for e in ops if e['id']=='ch27-02-bulk');status,obj,rec=request({**e,'id':'repeat-bulk'},report['supplemental']);assert status==200 and obj['errors'] is False and all(x['index']['status']==200 and x['index']['result']=='updated' for x in obj['items']);rec['verification']='pass'
 status,obj,rec=request({'id':'strict-unknown','method':'PUT','path':'/tut-l27-pages/_doc/bad?refresh=true','body':{'unknown':1}},report['supplemental']);assert status==400 and obj['error']['type']=='strict_dynamic_mapping_exception';rec['verification']='pass'
 e=next(e for e in ops if e['id']=='ch27-03-main');status,obj,rec=request({**e,'id':'correct-query-after-error'},report['supplemental']);assert status==200 and obj['values']==[[200]];rec['verification']='pass'
 status,obj,rec=request({'id':'residual-filter-profile','method':'POST','path':'/_query?allow_partial_results=false','body':{'query':'FROM tut-l27-pages | WHERE LENGTH(description) > 9 | STATS avg(views)','profile':True}},report['supplemental']);assert status==200;ops_text=json.dumps(obj['profile']);assert 'FilterOperator' in ops_text and obj['values']==[[162.5]];rec['verification']='pass'
 for id in ['ch27-14-cleanup','ch27-clean-pages']:
  e=next(e for e in ops if e['id']==id);status,obj,rec=request(e,report['supplemental']);verify(e,status,obj);rec['verification']='pass'
 e=next(e for e in ops if e['id']=='ch27-14-cleanup');status,obj,rec=request({**e,'id':'repeat-cleanup'},report['supplemental']);assert status==404;rec['verification']='pass'
 for name in ['pages','values']:
  status,obj,rec=request({'id':'final-absent-'+name,'method':'HEAD','path':'/tut-l27-'+name},report['supplemental']);assert status==404;rec['verification']='pass'
 report['status']='pass';report['firstAndCleanupRebuildPass']=True;report['finalResourcesAbsent']=True
except Exception as e:
 report['status']='fail';report['failure']=repr(e);save();raise
finally:
 for key,path in [('chapterSha256',root/'chapters/ch27.html'),('experimentSha256',root/'experiments/ch27.js')]:report[key]=hashlib.sha256(path.read_bytes()).hexdigest()
 save()
print('PASS: two rounds / 84 requests +',len(report['supplemental']),'supplemental; resources absent.')
