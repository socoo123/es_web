"""Run the chapter's ordered cards twice on the dedicated local teaching nodes.
Requires absent chapter resources; stores real HTTP status, headers and body.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,subprocess,hashlib,urllib.request,urllib.error,base64,http.client
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
specs=json.loads(subprocess.check_output(['node','-e','global.window={};require("./experiments/ch29.js");console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))'],cwd=root))
report={'status':'running','kind':'real-es-two-rounds','startedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'experimentSha256':hashlib.sha256((root/'experiments/ch29.js').read_bytes()).hexdigest(),'preflight':[],'rounds':[],'finally':[]}
admin='elastic:elastic-password'
def request(method,path,auth=admin,body=None,endpoint='http://localhost:9201',headers=None):
 h={}
 if auth:h['Authorization']='Basic '+base64.b64encode(auth.encode()).decode()
 h.update(headers or {})
 if body is not None:h['Content-Type']='application/json';data=json.dumps(body,ensure_ascii=False).encode() if not isinstance(body,str) else body.encode()
 else:data=None
 req=urllib.request.Request(endpoint+path,data=data,method=method,headers=h)
 try:res=urllib.request.urlopen(req,timeout=30)
 except urllib.error.HTTPError as err:res=err
 raw=res.read().decode();payload=json.loads(raw) if raw and res.headers.get('Content-Type','').startswith('application/json') else raw
 return {'method':method,'path':path,'endpoint':endpoint,'authMode':'anonymous' if auth is None else 'alice' if auth.startswith('tut-l29-alice:') else 'wrong' if auth.endswith('wrong-password') else 'elastic','customHeaders':headers or {},'requestBody':body,'status':res.status,'headers':list(res.headers.items()),'body':payload}
def record(rows,*args,**kwargs):
 r=request(*args,**kwargs);rows.append(r);return r
for ep in ['http://localhost:9200','http://localhost:9201']:
 r=record(report['preflight'],'GET','/',auth=None if ep.endswith('9200') else admin,endpoint=ep)
 assert r['status']==200 and r['body']['version']['number']=='9.4.0' and r['body']['version']['lucene_version']=='10.4.0' and r['body']['version']['build_hash']=='2e8528e92361c3399724226deaf2b46f933e925b'
for method,path in [('HEAD','/tut-l29-logs'),('HEAD','/tut-l29-denied'),('GET','/_security/user/tut-l29-alice'),('GET','/_security/role/tut-l29-reader')]:
 assert record(report['preflight'],method,path)['status']==404,'Requires absent chapter resources; no automatic deletion of prior objects.'
status={1:401,2:401,3:200,4:200,5:401,6:401,7:200,8:200,9:403,10:200,11:403,12:403,13:200,14:400,15:400,16:200,17:200,18:200,19:401,20:200,21:200,22:201,23:200,24:200,25:403,26:200,27:403,28:200,29:404,30:404,31:404,32:404}
def validate(n,r):
 assert r['status']==status[n],(n,r)
 b=r['body'];reason=b.get('error',{}).get('reason','') if isinstance(b,dict) and isinstance(b.get('error'),dict) else ''
 if n in [1,2]:assert 'missing authentication credentials' in reason
 if n in [5,19]:assert 'unable to authenticate user' in reason
 if n==6:assert 'unable to authenticate with provided credentials' in reason and 'xxx' in b['error']['additional_unsuccessful_credentials']
 if n in [1,2,5,6,19]:assert {v for k,v in r['headers'] if k.lower()=='www-authenticate'}=={'Basic realm="security", charset="UTF-8"','ApiKey'}
 if n in [9,11,12,25,27]:assert b['error']['type']=='security_exception' and not any(k.lower()=='www-authenticate' for k,v in r['headers'])
 if n==9:assert 'cluster:monitor/main' in reason and 'tut-l29-reader' in reason
 if n==11:assert 'indices:monitor/settings/get' in reason
 if n==12:assert 'indices:admin/create' in reason and 'tut-l29-denied' in reason
 if n==25:assert 'indices:data/write/index' in reason
 if n==27:assert 'indices:data/read/search' in reason and 'outside-tut-l29' in reason
 if n==4:assert b['username']=='elastic' and b['authentication_realm']['name']=='reserved' and b['roles']==['superuser']
 if n==7:assert b['role']['created'] is True
 if n==8:assert b['created'] is True
 if n==10:assert b['username']=='tut-l29-alice' and b['authentication_realm']['type']=='native' and b['roles']==['tut-l29-reader']
 if n==13:assert b['security']['available'] is True and b['security']['enabled'] is False
 if n in [14,15]:assert isinstance(b['error'],str) and 'no handler found' in b['error']
 if n in [17,18]:assert b['found'] is True
 if n==20:assert b['security']['enabled'] is True and b['security']['anonymous']['enabled'] is False and b['security']['token_service']['enabled'] is False and b['security']['api_key_service']['enabled'] is True and b['security']['ssl']['http']['enabled'] is False
 if n==21:assert b['acknowledged'] is True and b['shards_acknowledged'] is True
 if n==22:assert b['result']=='created'
 if n==23:assert b['found'] is True and b['_source']=={'msg':'security-demo'}
 if n==24:assert b['hits']['total']['value']==1 and b['_shards']['failed']==0 and [h['_id'] for h in b['hits']['hits']]==['1']
 if n==26:assert b['has_all_requested'] is False and b['cluster']['monitor'] is False and b['index']['tut-l29-logs']=={'read':True,'write':False,'create_index':False}
 if n in [30,31]:assert b=={}
 if n in [29,32]:assert b==''
try:
 for round_no in [1,2]:
  row={'round':round_no,'operations':[],'supplementary':[]};report['rounds'].append(row)
  for s in specs:
   n=int(s['id'].split('-')[1]);r=record(row['operations'],s['method'],s['path'],auth=s.get('auth'),body=s.get('body'),endpoint=s['endpoint'],headers=s.get('headers'));r['id']=s['id'];validate(n,r)
   if n==8:
    for oldn,key in [(7,'role'),(8,None),(22,None),(21,None)]:
     sp=next(sp for sp in specs if int(sp['id'].split('-')[1])==oldn);rr=record(row['supplementary'],sp['method'],sp['path'],body=sp['body'])
     if oldn==7:assert rr['status']==200 and rr['body']['role']['created'] is False
     if oldn==8:assert rr['status']==200 and rr['body']['created'] is False
     if oldn==22:assert rr['status']==200 and rr['body']['result']=='updated'
     if oldn==21:assert rr['status']==400 and rr['body']['error']['type']=='resource_already_exists_exception'
   if n==27:
    assert record(row['supplementary'],'GET','/tut-l29-logs/_count')['body']['count']==1
    assert record(row['supplementary'],'GET','/tut-l29-logs/_doc/2')['status']==404
  for path in ['/_security/user/tut-l29-alice','/_security/role/tut-l29-reader']:
   rr=record(row['supplementary'],'DELETE',path);assert rr['status']==404 and rr['body']['found'] is False
  rr=record(row['supplementary'],'DELETE','/tut-l29-logs');assert rr['status']==404
  # A real HTTP request with duplicate Authorization lines, impossible to express in a JS object.
  conn=http.client.HTTPConnection('localhost',9201,timeout=30);conn.putrequest('GET','/');conn.putheader('Authorization','ApiKey eHh4Onl5eQ==');conn.putheader('Authorization','Basic '+base64.b64encode(admin.encode()).decode());conn.endheaders();res=conn.getresponse();rr={'method':'GET','path':'/','endpoint':'http://localhost:9201','requestHeaders':['Authorization: ApiKey <fixed bogus xxx:yyy>','Authorization: Basic <teaching admin>'],'status':res.status,'headers':res.getheaders(),'body':json.loads(res.read())};row['supplementary'].append(rr);conn.close();assert rr['status']==400 and rr['body']['error']['reason']=='multiple values for single-valued header [Authorization].'
  row['status']='pass';print('PASS round',round_no,': 32 cards +',len(row['supplementary']),'repeat/side-effect/header checks',flush=True)
 report['status']='pass'
except Exception as err:
 report['status']='fail';report['failure']=str(err);raise
finally:
 # Preflight ensured these were absent before this script created them.
 for path in ['/_security/user/tut-l29-alice','/_security/role/tut-l29-reader','/tut-l29-logs']:
  record(report['finally'],'DELETE',path)
 for method,path in [('HEAD','/tut-l29-logs'),('HEAD','/tut-l29-denied'),('GET','/_security/user/tut-l29-alice'),('GET','/_security/role/tut-l29-reader')]:
  r=record(report['finally'],method,path);assert r['status']==404,r
 report['finishedAt']=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat();(out/'ch29-es-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
