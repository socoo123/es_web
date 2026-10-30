#!/usr/bin/env python3
"""F42: staged latency observations, bounded reconciliation and source compensation."""
import argparse, contextlib, datetime, fcntl, hashlib, http.client, importlib.util
import json, os, pathlib, secrets, selectors, socket, subprocess, time, urllib.error, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[2]
INFRA=ROOT/'infra/f42'; LOCAL=ROOT/'labs/f42/.local'; JOB=LOCAL/'job.json'
ES='http://127.0.0.1:20642'; CONNECT='http://127.0.0.1:18342'; APP='http://127.0.0.1:18092'
INDEX={'v1':'tut-f42-attractions-v001'}
READ='tut-f42-attractions-read'; TOPIC='travel_f42.f42.projection_event'
NAME='f42-pg'; GROUPS=['f42-v1']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok,detail):
    if not ok:raise AssertionError(detail)
def command(args,data=None,required=True,env=None):
    r=subprocess.run(args,input=data,text=True,capture_output=True,cwd=ROOT,env=env,timeout=180)
    if required:check(r.returncode==0,{'command':args,'exit_code':r.returncode,'stderr':r.stderr[-3000:],'stdout':r.stdout[-3000:]})
    return r
def compose_args(*args):return ['docker','compose','-f',str(INFRA/'compose.yaml'),*args]
def compose(*args):return command(compose_args(*args)).stdout
def sql_args():return compose_args('exec','-T','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-U','travel','-d','travel_f42')
def sql(content,required=True):return command(sql_args(),content,required)
def source(name):return (ROOT/'data/f42'/name).read_text()
def kafka(tool,*args):return compose_args('exec','-T','kafka','/opt/kafka/bin/'+tool+'.sh','--bootstrap-server','kafka:9092',*args)
def wait(test,detail,attempts=90):
    last=None
    for _ in range(attempts):
        try:
            last=test()
            if last:return last
        except (OSError,urllib.error.URLError,http.client.HTTPException,AssertionError,json.JSONDecodeError):pass
        time.sleep(1)
    raise TimeoutError((detail,last))
def java(*args):
    r=command(['bash','labs/f42/java.sh',*map(str,args)],required=False)
    return [dict(json.loads(x)['data'],observed_at=json.loads(x)['observed_at']) for x in r.stdout.splitlines() if x.startswith('{')],r
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def read_job():return json.loads(JOB.read_text())
def write_job(value):
    LOCAL.mkdir(exist_ok=True);tmp=JOB.with_suffix('.tmp')
    with tmp.open('w') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,JOB)
def public(value):
    if isinstance(value,dict):return {k:'<file-provider-reference>' if k=='database.password' else public(v) for k,v in value.items()}
    if isinstance(value,list):return [public(x) for x in value]
    return value
@contextlib.contextmanager
def coordinator():
    LOCAL.mkdir(exist_ok=True)
    with (LOCAL/'worker.lock').open('a') as f:
        fcntl.lockf(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:yield
        finally:fcntl.lockf(f,fcntl.LOCK_UN)

class Lab:
    def __init__(self,out):
        self.out=pathlib.Path(out).resolve();self.out.mkdir(parents=True,exist_ok=False)
        self.case='identity';self.http=[];self.workers=[];self.proc=None;self.log=None;self.snapshot=None
    def save(self,name,value):(self.out/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    def req(self,method,path,body=None,expected=200,base=ES,record=True):
        req=urllib.request.Request(base+path,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),method=method,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=20) as r:status=r.status;raw=r.read()
        except urllib.error.HTTPError as e:status=e.code;raw=e.read()
        value=json.loads(raw) if raw else None
        row={'at':now(),'case':self.case,'base':base,'method':method,'path':path,'body':public(body),'status':status,'response':public(value)}
        if record:
            self.http.append(row)
            with (self.out/'http.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
        check(status in ([expected] if isinstance(expected,int) else expected),row);return value
    def sql(self,name=None,text=None):
        content=source(name) if name else text;r=sql(content)
        with (self.out/'sql.jsonl').open('a') as f:f.write(json.dumps({'at':now(),'case':self.case,'file':name,'sql':content,'stdout':r.stdout},ensure_ascii=False)+'\n')
        return r.stdout
    def identity(self):
        es=self.req('GET','/');check(es['cluster_name']=='travel-f42-lab' and es['version']['number']=='9.4.0',es)
        pg=self.sql(text='SELECT current_database(),version();');check(pg.startswith('travel_f42|PostgreSQL 17.5'),pg)
        plugins=self.req('GET','/connector-plugins',base=CONNECT)
        check(any(p['class']=='io.debezium.connector.postgresql.PostgresConnector' and p['version']=='3.3.1.Final' for p in plugins),plugins)
        self.save('identity',{'at':now(),'es':es,'pg':pg,'plugins':plugins})
    def guard(self):
        indices=self.req('GET','/_cat/indices?format=json&expand_wildcards=all')
        check(all(x['index'] in list(INDEX.values()) or x['index'].startswith('.') for x in indices),'Foreign ES index')
        topics=command(kafka('kafka-topics','--list')).stdout.splitlines()
        check(set(topics)<=set([TOPIC,'f42-connect-configs','f42-connect-offsets','f42-connect-status','__consumer_offsets']),'Foreign Kafka topic')
        check(set(self.req('GET','/connectors',base=CONNECT))<=set([NAME]),'Foreign connector')
    def worker(self,name,*args,expect=0):
        values,r=java(*args);self.save(name,{'exit_code':r.returncode,'records':values});(self.out/(name+'.stderr.txt')).write_text(r.stderr)
        check(r.returncode==expect,{'name':name,'code':r.returncode,'stderr':r.stderr[-2500:],'records':values})
        self.workers.append({'name':name,'args':list(map(str,args)),'exit_code':r.returncode});return values
    def positions(self):
        values,r=java('inspect');check(r.returncode==0,r.stderr);return values[-1]
    def events(self):
        values,r=java('events');check(r.returncode==0,r.stderr);return [v for v in values if v['kind']=='event']
    def wait_events(self,count):wait(lambda:len(self.events())>=count,'Source events '+str(count))
    def refresh(self):
        for index in INDEX.values():check(self.req('POST','/'+index+'/_refresh')['_shards']['failed']==0,'Refresh failure')
    def docs(self,version):
        response=self.req('POST','/'+INDEX[version]+'/_search?allow_partial_search_results=false',{'size':100,'sort':[{'attraction_id':'asc'}],'query':{'match_all':{}}})
        check(not response['timed_out'] and response['_shards']['failed']==0 and response['hits']['total']['value']<=100,'Incomplete verification set')
        return {h['_id']:h['_source'] for h in response['hits']['hits']}
    def app_start(self):
        with socket.socket() as s:check(s.connect_ex(('127.0.0.1',18092))!=0,'18092 occupied')
        env=os.environ.copy();env.update(ES_URL=ES,ES_INDEX=READ,ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18092')
        self.log=(self.out/'application.log').open('w')
        self.proc=subprocess.Popen(['java','-Xms64m','-Xmx192m','-jar','backend/target/travel-search-0.7.0.jar'],cwd=ROOT,env=env,stdout=self.log,stderr=subprocess.STDOUT)
        def ready():
            check(self.proc.poll() is None,'Observation service exited')
            with urllib.request.urlopen(APP+'/',timeout=1) as r:return r.status==200
        wait(ready,'Observation service');self.save('observer-process',{'pid':self.proc.pid,'started':now()})
    def observe(self,name,want):
        body=json.loads((ROOT/'search/f42/search.json').read_text());value=self.req('POST','/api/attractions/search',body,base=APP)
        check([(x['id'],x['ticketPriceFen']) for x in value['items']]==want,value)
        replay=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',value['esRequest'])
        check([(x['_id'],x['_source']['ticket_price_fen']) for x in replay['hits']['hits']]==want,replay)
        self.save(name+'-java-search',{'request':body,'response':value,'rest_replay':replay,'pid':self.proc.pid if self.proc else None})
        if ARGS.observer:
            spec=importlib.util.spec_from_file_location('f42_observer',ARGS.observer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            m.capture(name,want,APP,ES,READ,self.out)
    def canonical(self):
        return json.loads(self.sql(text="SELECT jsonb_agg(f42.envelope(attraction_id)::text ORDER BY attraction_id) FROM f42.projection_clock;"))
    def expected(self,raws):
        result={}
        for raw in raws:
            doc=json.loads(raw);doc['projection_schema']=1
            doc['sync_hash']=hashlib.sha256(('1\n'+raw).encode()).hexdigest();result[doc['attraction_id']]=doc
        return result
    def prepare(self):
        self.case='prepare';self.guard();check(not JOB.exists(),'Cleanup existing lesson state first')
        check(not self.req('GET','/connectors',base=CONNECT),'Cleanup connector first')
        check(self.sql(text="SELECT to_regnamespace('f42') IS NOT NULL;").strip()=='f','Cleanup source first')
        password=(INFRA/'.local/cdc.properties').read_text().strip().split('=',1)[1]
        sql("\\set cdc_password '"+password+"'\n"+source('setup.sql'))
        self.save('source-setup',{'file':'data/f42/setup.sql','secret_via_stdin':True,'passed':True})
        command(kafka('kafka-topics','--create','--topic',TOPIC,'--partitions','1','--replication-factor','1','--config','cleanup.policy=delete','--config','retention.ms=604800000'))
        self.req('PUT','/'+INDEX['v1'],json.loads((ROOT/'search/f42/create-v1.json').read_text()))
        self.req('POST','/_aliases',json.loads((ROOT/'search/f42/aliases.json').read_text()))
        self.req('POST','/connectors',json.loads((ROOT/'cdc/f42/connector.json').read_text()),base=CONNECT,expected=201)
        self.connector_state('RUNNING');self.wait_events(3)
        self.worker('seed','seed','v1',0);self.worker('initial','drain','v1',3);self.refresh()
        pos=self.positions();settings=self.req('GET','/'+INDEX['v1']+'/_settings')
        job={'generation':secrets.token_hex(8),'topic_id':pos['topic_id'],'kafka_cluster_id':pos['kafka_cluster_id'],
             'index_uuid':settings[INDEX['v1']]['settings']['index']['uuid'],'fences':{},'audits':{},'initial_documents':self.canonical()}
        write_job(job);self.save('initial-events',self.events())
    def connector_state(self,state):
        return wait(lambda:(lambda s:s['connector']['state']==state and len(s['tasks'])==1 and s['tasks'][0]['state']==state)(self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=False)),'Connector '+state)
    def pause(self):
        self.req('PUT','/connectors/'+NAME+'/pause',base=CONNECT,expected=202);self.connector_state('PAUSED')
    def resume(self):
        self.req('PUT','/connectors/'+NAME+'/resume',base=CONNECT,expected=202);self.connector_state('RUNNING')
    def scope(self):
        job=read_job();pos=self.positions();settings=self.req('GET','/'+INDEX['v1']+'/_settings')
        check(pos['topic_id']==job['topic_id'] and pos['kafka_cluster_id']==job['kafka_cluster_id'],'Source identity changed')
        check(settings[INDEX['v1']]['settings']['index']['uuid']==job['index_uuid'],'Target identity changed')
        return job,pos
    def fence(self,key):
        check(key in ['audit','repaired','stale','final'],'Unknown fence key')
        job,pos=self.scope();check(key not in job['fences'],'Fence already exists; preserve its boundary')
        raw=self.sql(text="\\set fence_key '"+key+"'\n"+source('fence.sql'))
        expected=next(json.loads(x) for x in raw.splitlines() if x.startswith('{'))
        event=wait(lambda:next((e for e in self.events() if json.loads(e['value'])['after']['fence_key']==key),None),'Source fence '+key)
        job['fences'][key]={'high':event['offset']+1,'expected':expected,'source_event':event};write_job(job)
        self.save('fence-'+key,job['fences'][key]);return event['offset']+1
    def audit(self,key):
        with coordinator():
            job,pos=self.scope();fence=job['fences'][key];high=fence['high']
            check(pos['begin']<=high and pos['committed_next']['v1']==high and high<=pos['end'],'Require the exact retained audit boundary')
            self.refresh();got=self.docs('v1');want=self.expected(fence['expected']['documents']);findings=[]
            for id in sorted(set(got)|set(want)):
                a,b=got.get(id),want.get(id)
                if b is None:kind='unexpected';fields=[]
                elif a is None:kind='missing';fields=[]
                elif a==b:continue
                else:
                    kind='ahead_revision' if a.get('sync_revision',0)>b['sync_revision'] else 'deletion_residual' if b['sync_deleted'] and not a.get('sync_deleted') else 'field_mismatch'
                    fields=[k for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k) or (k in a)!=(k in b)]
                findings.append({'id':id,'kind':kind,'fields':fields,'actual':a,'expected':b})
            live=lambda docs:sum(not d['sync_deleted'] for d in docs.values())
            report={'at':now(),'key':key,'generation':job['generation'],'index_uuid':job['index_uuid'],'topic_id':job['topic_id'],
                    'high':high,'positions':pos,'expected_documents':fence['expected']['documents'],
                    'raw_count':{'expected':len(want),'actual':len(got)},'live_count':{'expected':live(want),'actual':live(got)},
                    'findings':findings,'clean':not findings}
            job['audits'][key]=report;write_job(job);self.save('audit-'+key,report);return report
    def repair(self,key,expect_failure=False):
        with coordinator():
            job,pos=self.scope();plan=job['audits'][key];check(plan['generation']==job['generation'],'Foreign generation')
            check(pos['committed_next']['v1']==plan['high'],'Checkpoint moved; make a fresh plan')
            check(plan['findings'] and all(f['kind'] in ['missing','field_mismatch','deletion_residual'] for f in plan['findings']),'No automatic repair for an ahead revision or unknown ID')
            ids=[f['id'] for f in plan['findings']];check(all(__import__('re').fullmatch('p[0-9]{2}',id) for id in ids),'Invalid business ID')
            # psql receives this reviewed plan through stdin. Source equality is
            # checked while holding the SAME transaction lock as every writer.
            expected=json.dumps(plan['expected_documents'],ensure_ascii=False).replace("'","''")
            content="BEGIN;\nSELECT pg_advisory_xact_lock(42042);\nCREATE TEMP TABLE repair_expected AS SELECT '"+expected+"'::jsonb AS value;\n"+(ROOT/'data/f42/repair-check.sql').read_text()
            content+='\n'+''.join("SELECT f42.emit('"+id+"');\n" for id in ids)+'COMMIT;\n'
            before=now();r=sql(content,required=False);after=now()
            record={'plan':key,'ids':ids,'started':before,'finished':after,'exit_code':r.returncode,'sql':content,'stdout':r.stdout,'stderr':r.stderr,'target_direct_writes':0}
            self.save('repair-'+key,record)
            if expect_failure:check(r.returncode!=0 and 'stale repair plan' in r.stderr,record)
            else:check(r.returncode==0,record)
            return record
    def corrupt(self):
        job=read_job();old=self.expected(job['initial_documents']);current=self.docs('v1')['p01']
        current['ticket_price_fen']=6500
        self.req('PUT','/'+INDEX['v1']+'/_doc/p01',current,expected=200)
        self.req('PUT','/'+INDEX['v1']+'/_doc/p02',old['p02'],expected=200)
        self.req('DELETE','/'+INDEX['v1']+'/_doc/p04',expected=200);self.refresh()
    def corrupt_stale(self):
        current=self.docs('v1')['p01'];current['ticket_price_fen']=6500
        self.req('PUT','/'+INDEX['v1']+'/_doc/p01',current,expected=200)
    def probe(self,name,get_price,search_price):
        before=now();doc=self.req('GET','/'+INDEX['v1']+'/_doc/p01');after_get=now()
        value=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',{'query':{'ids':{'values':['p01']}}});after_search=now()
        check(not value['timed_out'] and value['_shards']['failed']==0 and len(value['hits']['hits'])==1,value)
        actual=value['hits']['hits'][0]['_source']['ticket_price_fen']
        check(doc['_source']['ticket_price_fen']==get_price and actual==search_price,{'get':doc,'search':value})
        self.save(name,{'probe_start':before,'get_return':after_get,'search_return':after_search,'get':doc,'search':value,'positions':self.positions()})
    def replay(self,name,raws):
        path=LOCAL/(name+'.json');path.write_text(json.dumps({'documents':raws},ensure_ascii=False))
        return self.worker(name,'snapshot','v1',path)
    def drain(self,name,high):return self.worker(name,'drain','v1',high)
    def run(self):
        self.prepare();self.app_start();self.observe('initial',[('p01',6000),('p02',0)])
        self.case='c01-latency';self.pause();before=now();self.sql('price.sql');after=now()
        pos=self.positions();check(pos['end']==3 and pos['committed_next']['v1']==3,pos)
        self.save('capture-paused',{'commit_client_bracket':[before,after],'db':self.canonical(),'positions':pos,'observed_at':now()})
        self.probe('capture-paused-probe',6000,6000);self.resume();self.wait_events(4)
        pos=self.positions();check(pos['end']==4 and pos['committed_next']['v1']==3,pos)
        self.save('consumer-paused',pos);self.probe('consumer-paused-probe',6000,6000)
        self.drain('price-applied',4);self.probe('written-not-searchable',6500,6000)
        self.observe('before-refresh',[('p01',6000),('p02',0)])
        self.refresh();self.probe('after-refresh',6500,6500);self.observe('visible',[('p01',6500),('p02',0)])
        self.case='c02-reconcile';self.sql('changes.sql');high=self.fence('audit');check(high==8,high)
        self.drain('changes-applied',high);self.refresh();self.observe('before-corruption',[('p01',7000),('p04',4500)])
        self.corrupt();report=self.audit('audit')
        check([(x['id'],x['kind']) for x in report['findings']]==[('p01','field_mismatch'),('p02','deletion_residual'),('p04','missing')],report)
        check(report['live_count']=={'expected':3,'actual':3},report)
        self.observe('corrupted',[('p01',6500),('p02',0)])
        # The stored fingerprint is deliberately unchanged. Replaying the same
        # revision noops; compare complete fields, then issue a NEW revision.
        p01=next(r for r in report['expected_documents'] if json.loads(r)['attraction_id']=='p01')
        replay=self.replay('same-revision-replay',[p01]);check([x['result'] for x in replay if x['kind']=='item']==['noop'],replay)
        self.probe('same-revision-still-wrong',6500,6500)
        self.repair('audit');high=self.fence('repaired');check(high==12,high)
        self.drain('compensation-applied',high);report=self.audit('repaired');check(report['clean'],report)
        self.observe('repaired',[('p01',7000),('p04',4500)])
        self.case='c03-stale-plan';self.corrupt_stale()
        high=self.fence('stale');check(high==13,high);self.drain('stale-boundary',high)
        report=self.audit('stale');check(len(report['findings'])==1,report)
        self.sql('newer.sql');self.wait_events(14);self.repair('stale',expect_failure=True)
        # Failed stale plan emitted no compensation record; only the business
        # change exists. Consume it and establish a NEW audit boundary.
        self.wait_events(14);check(self.positions()['end']==14,'Stale plan emitted work')
        self.drain('newer-applied',14);high=self.fence('final');check(high==15,high)
        self.drain('final-boundary',high);report=self.audit('final');check(report['clean'],report)
        pos=self.positions();replay=self.replay('old-snapshot-replay',read_job()['initial_documents'])
        check(all(x['result']=='noop' for x in replay if x['kind']=='item'),replay)
        check(self.positions()['committed_next']==pos['committed_next'],'Snapshot moved checkpoint')
        self.refresh();self.observe('final',[('p01',7200),('p04',4500)])
        self.save('final-events',self.events());self.save('final-documents',self.docs('v1'))
        self.save('summary',{'at':now(),'passed':True,'cases':3,'source_events':len(self.events()),'http_operations':len(self.http),'workers':self.workers,
                             'final_next':self.positions()['committed_next']['v1'],'final_prices_fen':{'p01':7200,'p04':4500},
                             'boundaries':{k:v['high'] for k,v in read_job()['fences'].items()},'controlled_delays':True,'performance_benchmark':False})
    def cleanup(self):
        self.case='cleanup';self.guard()
        with coordinator():
            state=command(kafka('kafka-consumer-groups','--describe','--group','f42-v1','--state'),required=False)
            check('Stable' not in state.stdout and 'Rebalancing' not in state.stdout,'Active lesson worker')
            if NAME in self.req('GET','/connectors',base=CONNECT):
                self.req('PUT','/connectors/'+NAME+'/stop',base=CONNECT,expected=204)
                wait(lambda:self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=False)['connector']['state']=='STOPPED','Stopped')
                self.req('DELETE','/connectors/'+NAME+'/offsets',base=CONNECT);self.req('DELETE','/connectors/'+NAME,base=CONNECT,expected=204)
            self.sql(text="SELECT pg_drop_replication_slot(slot_name) FROM pg_replication_slots WHERE slot_name='f42_slot'; DROP PUBLICATION IF EXISTS f42_publication; DROP SCHEMA IF EXISTS f42 CASCADE; DO $$ BEGIN IF EXISTS(SELECT FROM pg_roles WHERE rolname='f42_cdc') THEN EXECUTE 'REVOKE CONNECT ON DATABASE travel_f42 FROM f42_cdc'; END IF; END $$; DROP ROLE IF EXISTS f42_cdc;")
            if TOPIC in command(kafka('kafka-topics','--list')).stdout.splitlines():command(kafka('kafka-topics','--delete','--topic',TOPIC))
            if 'f42-v1' in command(kafka('kafka-consumer-groups','--list')).stdout.splitlines():command(kafka('kafka-consumer-groups','--delete','--group','f42-v1'))
            self.req('DELETE','/'+INDEX['v1'],expected=[200,404])
            for path in LOCAL.glob('*.json'):path.unlink()
        self.save('summary',{'at':now(),'passed':True,'deleted':['f42 schema/clock/outbox/role/slot/publication','f42 connector/source offsets/topic/group','tut-f42-attractions-v001 and aliases','f42 local job/replay files'],'preserved':['named volumes, Connect internal topics, local secrets','unrelated projects']})
    def close(self):
        if self.proc and self.proc.poll() is None:self.proc.terminate();self.proc.wait(timeout=20)
        if self.log:self.log.close()

def init(lab):
    local=INFRA/'.local';check(not local.exists(),'Existing secrets: use start')
    check(not command(['docker','volume','ls','-q','--filter','label=com.docker.compose.project=es-framework-f42']).stdout.strip(),'Existing F42 volumes: preserve secrets')
    local.mkdir(mode=0o700)
    for name,value in [('pg-password.txt',secrets.token_urlsafe(32)),('cdc.properties','password='+secrets.token_urlsafe(32))]:
        path=local/name;path.write_text(value+'\n');path.chmod(0o600)
    lab.save('summary',{'passed':True,'secrets_created':True,'secrets_printed':False})
def start(lab):
    compose('up','-d');wait(lambda:sql('SELECT 1;',required=False).returncode==0,'PostgreSQL')
    wait(lambda:command(kafka('kafka-topics','--list'),required=False).returncode==0,'Kafka')
    wait(lambda:lab.req('GET','/connector-plugins',base=CONNECT,record=False),'Connect')
    wait(lambda:lab.req('GET','/_cluster/health?wait_for_status=yellow&timeout=1s',record=False).get('status') in ['green','yellow'],'ES')
    lab.identity();lab.save('summary',{'at':now(),'passed':True})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init','start','prepare','run','cleanup','down','step','pause','resume','inspect','drain','fence','audit','repair','corrupt','corrupt-stale','refresh'])
    p.add_argument('value',nargs='?');p.add_argument('--out',required=True);p.add_argument('--observer');ARGS=p.parse_args();lab=Lab(ARGS.out)
    try:
        if ARGS.action=='init':init(lab)
        elif ARGS.action=='start':start(lab)
        elif ARGS.action=='down':lab.identity();lab.guard();compose('down');lab.save('summary',{'passed':True,'volumes_and_secrets_preserved':True})
        else:
            lab.identity()
            if ARGS.action in ['prepare','run','cleanup','pause','resume','corrupt','refresh']:getattr(lab,ARGS.action)()
            elif ARGS.action=='corrupt-stale':lab.corrupt_stale()
            elif ARGS.action=='step':
                check(ARGS.value in ['price','changes','newer'],'Unknown step');lab.sql(ARGS.value+'.sql')
            elif ARGS.action=='fence':print(json.dumps({'high':lab.fence(ARGS.value)}))
            elif ARGS.action=='drain':lab.drain('drain',int(ARGS.value))
            elif ARGS.action=='audit':print(json.dumps(lab.audit(ARGS.value),ensure_ascii=False))
            elif ARGS.action=='repair':lab.repair(ARGS.value)
            else:lab.save('events',lab.events());lab.save('positions',lab.positions());print(json.dumps(lab.positions()))
        print(json.dumps({'action':ARGS.action,'evidence':str(lab.out),'passed':True},ensure_ascii=False))
    finally:lab.close()
