#!/usr/bin/env python3
"""Isolated F35 HTTPS/authentication/authorization lab. No secrets in receipts."""
import argparse, base64, collections, datetime, gzip, importlib.util, json, os
import pathlib, secrets, ssl, subprocess, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
INFRA = ROOT / 'infra/f35'
LOCAL = INFRA / '.local'
IMAGE = 'docker.elastic.co/elasticsearch/elasticsearch:9.4.0'
ES = 'https://127.0.0.1:19935'
APP = 'http://127.0.0.1:18085'
INDEX = 'tut-f35-attractions-v001'
READ = 'tut-f35-attractions-read'
WRITE = 'tut-f35-attractions-write'
VOLUMES = ['es-framework-f35-n1-data', 'es-framework-f35-n2-data']
SECRETS = []

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok, message):
    if not ok: raise AssertionError(message)
def load(path): return json.loads((ROOT/path).read_text())
def redact(value):
    if isinstance(value, dict):
        return {k: ('[REDACTED]' if k.lower() in ['api_key','encoded','password','authorization'] else redact(v)) for k,v in value.items()}
    if isinstance(value, list): return [redact(v) for v in value]
    if isinstance(value, str):
        for secret in SECRETS:
            if secret: value = value.replace(secret, '[REDACTED]')
    return value
def private(path, content):
    path.write_text(content); path.chmod(0o600)
def command(args):
    p = subprocess.run(args, text=True, capture_output=True)
    check(p.returncode == 0, 'command failed: '+str(args[0])+': '+redact(p.stderr[-2000:]))
    return p.stdout
def compose(*args, bootstrap=False):
    cmd=['docker','compose','-f',str(INFRA/'compose.yaml')]
    if bootstrap: cmd += ['-f',str(INFRA/'bootstrap.yaml')]
    return command(cmd+list(args))
def auth_admin():
    password=(LOCAL/'admin-password.txt').read_text().strip(); SECRETS.append(password)
    token=base64.b64encode(('elastic:'+password).encode()).decode(); SECRETS.append(token)
    return 'Basic '+token
def auth_key(name):
    token=(LOCAL/(name+'-key.txt')).read_text().strip(); SECRETS.append(token)
    return 'ApiKey '+token
def context(ca=None): return ssl.create_default_context(cafile=str(ca or LOCAL/'ca.crt'))

def curl_config(name):
    token=(LOCAL/(name+'-key.txt')).read_text().strip()
    private(LOCAL/(name+'.curl'),'cacert = "'+str(LOCAL/'ca.crt')+'"\nheader = "Authorization: ApiKey '+token+'"\n')

class Lab:
    def __init__(self, out):
        self.out=pathlib.Path(out).resolve(); self.out.mkdir(parents=True,exist_ok=False)
        self.events=[]; self.case='setup'; self.admin=auth_admin() if LOCAL.exists() else None
        self.proc=None; self.log=None; self.stage=None
    def save(self, name, value):
        (self.out/(name+'.json')).write_text(json.dumps(redact(value),ensure_ascii=False,indent=2)+'\n')
    def req(self, method, path, body=None, auth='admin', expected=200, case=None, base=ES, ca=None):
        headers={}; data=None
        if auth == 'admin': headers['Authorization']=self.admin
        elif auth == 'issuer':
            password=(LOCAL/'reader-user-password.txt').read_text().strip(); SECRETS.append(password)
            token=base64.b64encode(('tut-f35-reader:'+password).encode()).decode(); SECRETS.append(token)
            headers['Authorization']='Basic '+token
        elif auth: headers['Authorization']=auth_key(auth) if auth in ['reader','writer','rotated'] else auth
        if body is not None:
            data=body if isinstance(body,bytes) else json.dumps(body,ensure_ascii=False).encode()
            headers['Content-Type']='application/x-ndjson' if isinstance(body,bytes) else 'application/json'
        request=urllib.request.Request(base+path,data=data,method=method,headers=headers)
        try:
            with urllib.request.urlopen(request,context=context(ca) if base.startswith('https:') else None,timeout=40) as r:
                status=r.status; value=json.load(r)
        except urllib.error.HTTPError as e:
            status=e.code; value=json.loads(e.read())
        rec={'at':now(),'case':case or self.case,'method':method,'path':path,'principal':auth if auth in ['admin','issuer','reader','writer','rotated',None] else 'invalid-credential','status':status,'body':body.decode() if isinstance(body,bytes) else body,'response':redact(value)}
        self.events.append(rec)
        with (self.out/'events.jsonl').open('a') as f: f.write(json.dumps(redact(rec),ensure_ascii=False)+'\n')
        check(status in ([expected] if isinstance(expected,int) else expected), {'path':path,'status':status,'response':redact(value)})
        return value
    def identity(self):
        roots=[self.req('GET','/',base=f'https://127.0.0.1:{port}',case='identity') for port in [19935,19936]]
        check(len({x['cluster_uuid'] for x in roots})==1 and roots[0]['cluster_name']=='travel-f35-lab','wrong cluster')
        check(all(x['version']['number']=='9.4.0' for x in roots),'version')
        nodes=self.req('GET','/_nodes/settings?flat_settings=true',case='identity')
        check({n['name'] for n in nodes['nodes'].values()}=={'travel-f35-n1','travel-f35-n2'},'wrong nodes')
        for n in nodes['nodes'].values():
            check(set(n['roles'])==({'master','data','ingest'} if n['name'].endswith('n1') else {'data'}),'node roles')
            settings=n['settings']
            for key in ['xpack.security.enabled','xpack.security.http.ssl.enabled','xpack.security.transport.ssl.enabled']:
                check(settings.get(key)=='true',key)
            container='es-framework-f35-'+('n1' if n['name'].endswith('n1') else 'n2')+'-1'
            info=json.loads(command(['docker','inspect',container]))[0]
            configured=dict(x.split('=',1) for x in info['Config']['Env'] if '=' in x)
            check(configured.get('xpack.security.transport.ssl.verification_mode')=='full','transport verification')
            n['f35_config_evidence']={'transport_verification_mode':configured['xpack.security.transport.ssl.verification_mode'],'note':'SSL detail settings are filtered from Nodes Info; checked actual container configuration'}
            check('cluster.initial_master_nodes' not in settings,'bootstrap still present')
        self.save('identity',{'roots':roots,'nodes':nodes}); return roots[0]['cluster_uuid']
    def clean(self):
        self.identity()
        indices=self.req('GET','/_cat/indices?format=json&expand_wildcards=all',case='guard')
        check(all(x['index']==INDEX or x['index'].startswith(('.security-','.ds-ilm-history-7-','.ds-.logs-elasticsearch.deprecation-default-')) for x in indices),'foreign index')
        keys=self.req('GET','/_security/api_key?name=tut-f35-*',case='cleanup')['api_keys']
        ids=[x['id'] for x in keys if not x['invalidated']]
        if ids:self.req('DELETE','/_security/api_key',{'ids':ids},case='cleanup')
        self.req('DELETE','/'+INDEX,expected=[200,404],case='cleanup')
        self.req('DELETE','/_security/user/tut-f35-reader',expected=[200,404],case='cleanup')
        self.req('DELETE','/_security/role/tut-f35-reader',expected=[200,404],case='cleanup')
    def key(self, name):
        result=self.req('POST','/_security/api_key',load('search/f35/'+('reader' if name=='rotated' else name)+'-key.json'),auth='issuer' if name in ['reader','rotated'] else 'admin')
        SECRETS.extend([result['api_key'],result['encoded']]); private(LOCAL/(name+'-key.txt'),result['encoded']+'\n')
        self.save(name+'-key-metadata',{k:v for k,v in result.items() if k not in ['api_key','encoded']})
        private(LOCAL/(name+'-id.txt'),result['id']+'\n')
        curl_config(name)
        return result['id']
    def start_app(self, stage, ca='ca.crt', key='reader'):
        self.stop_app(); self.stage=stage
        java=pathlib.Path(os.environ.get('JAVA_HOME',''))/'bin/java'
        check(java.is_file(),'Set JAVA_HOME to JDK25')
        env={**os.environ,'ES_URL':ES,'ES_INDEX':READ,'ES_CA_FILE':str(LOCAL/ca),'ES_API_KEY_FILE':str(LOCAL/(key+'-key.txt')),'APP_PORT':'18085'}
        self.log=(self.out/(stage+'-application.log')).open('w')
        self.proc=subprocess.Popen([str(java),'-jar',str(ROOT/'backend/target/travel-search-0.7.0.jar')],env=env,stdout=self.log,stderr=subprocess.STDOUT)
        for _ in range(100):
            check(self.proc.poll() is None,'application startup failed; inspect redacted log')
            try:
                with urllib.request.urlopen(APP+'/',timeout=1) as r:
                    if r.status==200:return
            except (OSError,urllib.error.URLError):pass
            time.sleep(.3)
        raise AssertionError('application startup timeout')
    def stop_app(self):
        if self.proc:
            self.proc.terminate()
            try:self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
            self.proc=None;self.log.close()
            path=self.out/(self.stage+'-application.log')
            data=redact(path.read_text());gzip.open(str(path)+'.gz','wt').write(data);path.unlink()
    def app_search(self, stage, rows, status=200, observer=None):
        result=self.req('POST','/api/attractions/search',load('search/f35/search.json'),auth=None,base=APP,expected=status)
        if status==200:
            check(collections.Counter((x['id'],x['ticketPriceFen']) for x in result['items'])==collections.Counter(rows),stage)
            replay=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',result['esRequest'],auth='reader')
            check(not replay['timed_out'] and replay['_shards']['failed']==0,'incomplete replay')
            check(collections.Counter((x['_id'],x['_source']['ticket_price_fen']) for x in replay['hits']['hits'])==collections.Counter(rows),'REST/Java differ')
        else:check(result['code']==('SEARCH_UNAVAILABLE' if status==503 else 'SEARCH_BACKEND_REJECTED'),result)
        self.save(stage+'-java',result)
        if observer:
            spec=importlib.util.spec_from_file_location('f35_observer',observer);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.capture(stage,rows,status,APP,ES,READ,self.out,context(),auth_key('reader'))

def init():
    check(not LOCAL.exists(),'Local secrets already exist; preserve existing material for original data volumes')
    check(not any(subprocess.run(['docker','volume','inspect',v],capture_output=True).returncode==0 for v in VOLUMES+['es-framework-f35-certs']),'Existing F35 volumes: preserve original certificates and password')
    LOCAL.mkdir(mode=0o700)
    (LOCAL/'openssl.cnf').write_text('[req]\ndistinguished_name=dn\n[dn]\n[v3_ca]\nbasicConstraints=critical,CA:TRUE\nkeyUsage=critical,keyCertSign,cRLSign\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid:always\n')
    private(LOCAL/'admin-password.txt',secrets.token_urlsafe(36)+'\n')
    for ca in ['ca','wrong-ca']:
        command(['openssl','req','-config',str(LOCAL/'openssl.cnf'),'-extensions','v3_ca','-x509','-newkey','rsa:2048','-sha256','-nodes','-days','30','-subj','/CN=F35-'+ca,'-keyout',str(LOCAL/(ca+'.key')),'-out',str(LOCAL/(ca+'.crt'))])
        (LOCAL/(ca+'.key')).chmod(0o600)
    for node in ['n1','n2']:
        dest=LOCAL/node;dest.mkdir(mode=0o700)
        command(['openssl','req','-config',str(LOCAL/'openssl.cnf'),'-new','-newkey','rsa:2048','-nodes','-subj','/CN='+node,'-keyout',str(dest/'server.key'),'-out',str(dest/'server.csr')])
        private(dest/'extensions.cnf','basicConstraints=CA:FALSE\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth,clientAuth\nsubjectAltName=DNS:'+node+',DNS:localhost,IP:127.0.0.1,IP:172.30.35.'+('11' if node=='n1' else '12')+'\n')
        command(['openssl','x509','-req','-in',str(dest/'server.csr'),'-CA',str(LOCAL/'ca.crt'),'-CAkey',str(LOCAL/'ca.key'),'-CAcreateserial','-days','30','-sha256','-extfile',str(dest/'extensions.cnf'),'-out',str(dest/'server.crt')])
        (dest/'server.key').chmod(0o600)
    command(['docker','volume','create','--label','esweb.lesson=f35','es-framework-f35-certs'])
    command(['docker','run','--rm','--network','none','--user','0:0','--mount','type=bind,src='+str(LOCAL)+',dst=/input,readonly','--mount','type=volume,src=es-framework-f35-certs,dst=/output',IMAGE,'bash','-c','cp /input/ca.crt /output/ && for n in n1 n2; do mkdir -p /output/$n; cp /input/$n/server.crt /input/$n/server.key /output/$n/; done && chown -R 1000:0 /output && chmod -R u=rwX,g=rX,o= /output'])
    # Curl reads secrets from a file; no token appears in argv or output.
    password=(LOCAL/'admin-password.txt').read_text().strip()
    private(LOCAL/'admin.curl','cacert = "'+str(LOCAL/'ca.crt')+'"\nuser = "elastic:'+password+'"\n')

def start(lab):
    existing=[v for v in VOLUMES if subprocess.run(['docker','volume','inspect',v],capture_output=True).returncode==0]
    check(len(existing) in [0,2],'Partial data volumes: refuse to bootstrap')
    fresh=not existing
    compose('up','-d','n1','n2',bootstrap=fresh)
    for _ in range(200):
        try:
            with urllib.request.urlopen(urllib.request.Request(ES+'/_cluster/health?wait_for_nodes=2&timeout=1s',headers={'Authorization':lab.admin}),context=context(),timeout=3) as r:
                health=json.load(r)
            if health['number_of_nodes']==2 and not health['timed_out']:break
        except (OSError,urllib.error.URLError):pass
        time.sleep(1)
    else:raise AssertionError('HTTPS two-node startup timeout')
    if fresh:
        compose('up','-d','--no-deps','--force-recreate','n1')
        for _ in range(160):
            try:
                with urllib.request.urlopen(urllib.request.Request(ES+'/_cluster/health?wait_for_nodes=2&timeout=1s',headers={'Authorization':lab.admin}),context=context(),timeout=3) as r:health=json.load(r)
                if health['number_of_nodes']==2 and not health['timed_out']:break
            except (OSError,urllib.error.URLError):pass
            time.sleep(1)
        else:raise AssertionError('post-bootstrap restart timeout')
    lab.identity()

def credentials(lab):
    lab.req('PUT','/_security/role/tut-f35-reader',load('search/f35/reader-role.json'))
    role=lab.req('GET','/_security/role/tut-f35-reader');check(role['tut-f35-reader']['indices'][0]['privileges']==['read'],'role')
    password=secrets.token_urlsafe(32);SECRETS.append(password);private(LOCAL/'reader-user-password.txt',password+'\n')
    lab.req('PUT','/_security/user/tut-f35-reader',{'password':password,'roles':['tut-f35-reader']})
    lab.req('GET','/_security/_authenticate',auth='issuer')
    reader_id=lab.key('reader');lab.key('writer')
    return reader_id

def run(lab, observer):
    lab.clean();lab.case='f35-c01'
    # TLS failures are NOT HTTP statuses; both calls send no credentials.
    tls=[]
    for label,url,ca in [('untrusted-ca',ES,LOCAL/'wrong-ca.crt'),('wrong-hostname','https://127.0.0.2:19935',LOCAL/'ca.crt')]:
        try:
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context(ca)))
            if label=='wrong-hostname':
                # Same TLS listener and TCP address; change the verified peer name explicitly.
                import socket
                with socket.create_connection(('127.0.0.1',19935),timeout=10) as sock:
                    with context(ca).wrap_socket(sock,server_hostname='not-f35.invalid'):pass
            else:opener.open(url,timeout=10)
            raise AssertionError('TLS failure expected')
        except (ssl.SSLCertVerificationError,urllib.error.URLError) as e:
            reason=e.reason if isinstance(e,urllib.error.URLError) else e
            check(isinstance(reason,ssl.SSLCertVerificationError),'unexpected connection failure')
            tls.append({'case':label,'http_status':None,'verify_code':reason.verify_code,'reason':reason.verify_message})
    lab.save('tls-failures',tls)
    lab.req('GET','/_security/_authenticate',auth=None,expected=401)
    lab.req('GET','/_security/_authenticate',auth='ApiKey '+base64.b64encode(b'f35:invalid').decode(),expected=401)
    lab.req('PUT','/'+INDEX,load('search/f35/create-main.json'))
    health=lab.req('GET','/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s');check(not health['timed_out'],'green')
    bulk=lab.req('POST','/'+INDEX+'/_bulk?refresh=true&wait_for_active_shards=all',(ROOT/'data/f35/v001.ndjson').read_bytes())
    check(not bulk['errors'] and all(next(iter(x.values()))['status']==201 for x in bulk['items']),'bulk items')
    lab.req('POST','/_aliases',load('search/f35/aliases.json'))
    reader_id=credentials(lab)
    # Keep a syntactically valid invalid key in an ignored file for Java's 401 check.
    private(LOCAL/'invalid-key.txt',base64.b64encode(b'f35:invalid').decode()+'\n')
    lab.req('GET','/_security/_authenticate',auth='reader')
    lab.case='f35-c02'
    found=lab.req('POST','/'+READ+'/_search',{'query':{'match_all':{}}},auth='reader')
    check(found['hits']['total']['value']==6,'reader count')
    for method,path,body in [
        ('POST','/'+INDEX+'/_search',{'query':{'match_all':{}}}),
        ('PUT','/'+WRITE+'/_doc/p01?require_alias=true',load('data/f35/p01-updated.json')),
        ('GET','/_cluster/health',None),
        ('DELETE','/'+INDEX,None),
        ('PUT','/_security/role/tut-f35-reader',load('search/f35/reader-role.json'))]:
        lab.req(method,path,body,auth='reader',expected=403)
    writer=lab.req('PUT','/'+WRITE+'/_doc/p01?require_alias=true&wait_for_active_shards=all',load('data/f35/p01-updated.json'),auth='writer')
    check(writer['result']=='updated','writer update')
    lab.req('DELETE','/'+WRITE+'/_doc/p02?wait_for_active_shards=all',auth='writer')
    for method,path,body in [
        ('POST','/'+READ+'/_search',{'query':{'match_all':{}}}),
        ('PUT','/'+INDEX+'/_doc/p01',load('data/f35/p01-updated.json')),
        ('POST','/'+WRITE+'/_refresh',None),
        ('PUT','/'+INDEX+'/_settings',{'index.refresh_interval':'1s'}),
        ('PUT','/tut-f35-forbidden',load('search/f35/create-main.json'))]:
        lab.req(method,path,body,auth='writer',expected=403)
    lab.req('POST','/'+INDEX+'/_refresh')
    lab.case='f35-c03'
    lab.start_app('01-wrong-ca',ca='wrong-ca.crt');lab.app_search('01-wrong-ca',[],503,observer)
    lab.start_app('02-invalid-key',key='invalid');lab.app_search('02-invalid-key',[],502,observer)
    lab.start_app('03-writer-cannot-search',key='writer');lab.app_search('03-writer-cannot-search',[],502,observer)
    lab.start_app('04-reader-after-update');lab.app_search('04-reader-after-update',[('p01',6500)],observer=observer)
    seed=(ROOT/'data/f35/v001.ndjson').read_text().splitlines()
    for i in [0,2]:
        id=json.loads(seed[i])['create']['_id']
        lab.req('PUT','/'+WRITE+'/_doc/'+id+'?require_alias=true&wait_for_active_shards=all',json.loads(seed[i+1]),auth='writer',expected=200 if id=='p01' else 201)
    lab.req('POST','/'+INDEX+'/_refresh')
    lab.app_search('05-reader-after-repair',[('p01',6000),('p02',0)],observer=observer)
    lab.req('DELETE','/_security/api_key',{'ids':[reader_id]})
    lab.req('GET','/_security/_authenticate',auth='reader',expected=401)
    lab.app_search('06-revoked-key',[],502,observer)
    lab.key('rotated');private(LOCAL/'reader-key.txt',(LOCAL/'rotated-key.txt').read_text());curl_config('reader')
    lab.app_search('07-file-replaced-old-client',[],502,observer)
    lab.start_app('08-restarted-rotated-key');lab.app_search('08-restarted-rotated-key',[('p01',6000),('p02',0)],observer=observer)
    final=lab.req('POST','/'+READ+'/_search',{'size':20,'query':{'match_all':{}},'sort':['attraction_id']},auth='reader')
    check(final['hits']['total']['value']==6,'final count')
    lab.save('final-documents',final)
    lab.identity()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['init','start','run','credentials','revoke','rotate','cleanup','down']);parser.add_argument('--out',required=True);parser.add_argument('--observer')
    args=parser.parse_args();lab=Lab(args.out);passed=False
    try:
        if args.action=='init':init()
        elif args.action=='start':start(lab)
        elif args.action=='run':run(lab,args.observer)
        elif args.action=='credentials':lab.identity();credentials(lab)
        elif args.action=='revoke':
            lab.identity();lab.req('DELETE','/_security/api_key',{'ids':[(LOCAL/'reader-id.txt').read_text().strip()]})
        elif args.action=='rotate':
            lab.identity();new_id=lab.key('rotated');private(LOCAL/'reader-key.txt',(LOCAL/'rotated-key.txt').read_text());private(LOCAL/'reader-id.txt',new_id+'\n');curl_config('reader')
        elif args.action=='cleanup':lab.clean()
        elif args.action=='down':lab.identity();compose('down')
        passed=True
    finally:
        lab.stop_app()
        counts=collections.Counter(e['case'] for e in lab.events)
        lab.save('summary',{'at':now(),'action':args.action,'passed':passed,'http_counts_by_case':dict(counts),'tls_failures_are_http':False,'credential_policy':'local ignored files; issuance responses and all receipts redacted','observation_hook':bool(args.observer)})
    print('F35 '+args.action+' passed; receipts: '+str(lab.out))
if __name__=='__main__':main()
