#!/usr/bin/env python3
"""F41 online backfill and bounded catch-up; every observation is real."""
import argparse, contextlib, datetime, fcntl, hashlib, http.client, importlib.util
import json, os, pathlib, secrets, selectors, socket, subprocess, time, urllib.error, urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[2]
INFRA=ROOT/'infra/f41'; LOCAL=ROOT/'labs/f41/.local'; JOB=LOCAL/'job.json'
ES='http://127.0.0.1:20541'; CONNECT='http://127.0.0.1:18341'; APP='http://127.0.0.1:18091'
INDEX={'v1':'tut-f41-attractions-v001','v2':'tut-f41-attractions-v002'}
ONCE='tut-f41-once-v001'; READ='tut-f41-attractions-read'; TOPIC='travel_f41.f41.projection_event'
NAME='f41-pg'; GROUPS=['f41-v1','f41-v2']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok,detail):
    if not ok:raise AssertionError(detail)
def command(args,data=None,required=True,env=None):
    r=subprocess.run(args,input=data,text=True,capture_output=True,cwd=ROOT,env=env,timeout=180)
    if required:check(r.returncode==0,{'command':args,'exit_code':r.returncode,'stderr':r.stderr[-3000:],'stdout':r.stdout[-3000:]})
    return r
def compose_args(*args):return ['docker','compose','-f',str(INFRA/'compose.yaml'),*args]
def compose(*args):return command(compose_args(*args)).stdout
def sql_args():return compose_args('exec','-T','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-U','travel','-d','travel_f41')
def sql(content,required=True):return command(sql_args(),content,required)
def source(name):return (ROOT/'data/f41'/name).read_text()
def kafka(tool,*args):return compose_args('exec','-T','kafka','/opt/kafka/bin/'+tool+'.sh','--bootstrap-server','kafka:9092',*args)
def wait(test,detail,attempts=90):
    last=None
    for _ in range(attempts):
        try:
            last=test()
            if last:return last
        except (OSError,urllib.error.URLError,http.client.HTTPException,AssertionError):pass
        time.sleep(1)
    raise TimeoutError((detail,last))
def java(*args):
    r=command(['bash','labs/f41/java.sh',*map(str,args)],required=False)
    return [json.loads(x) for x in r.stdout.splitlines() if x.startswith('{')],r
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
        es=self.req('GET','/');check(es['cluster_name']=='travel-f41-lab' and es['version']['number']=='9.4.0',es)
        pg=self.sql(text='SELECT current_database(),version();');check(pg.startswith('travel_f41|PostgreSQL 17.5'),pg)
        plugins=self.req('GET','/connector-plugins',base=CONNECT)
        check(any(p['class']=='io.debezium.connector.postgresql.PostgresConnector' and p['version']=='3.3.1.Final' for p in plugins),plugins)
        self.save('identity',{'at':now(),'es':es,'pg':pg,'plugins':plugins})
    def guard(self):
        indices=self.req('GET','/_cat/indices?format=json&expand_wildcards=all')
        check(all(x['index'] in [*INDEX.values(),ONCE] or x['index'].startswith('.') for x in indices),'Foreign ES index')
        topics=command(kafka('kafka-topics','--list')).stdout.splitlines()
        check(set(topics)<=set([TOPIC,'f41-connect-configs','f41-connect-offsets','f41-connect-status','__consumer_offsets']),'Foreign Kafka topic')
        check(set(self.req('GET','/connectors',base=CONNECT))<=set([NAME]),'Foreign connector')
    def worker(self,name,*args,expect=0):
        values,r=java(*args);self.save(name,{'exit_code':r.returncode,'records':values});(self.out/(name+'.stderr.txt')).write_text(r.stderr)
        check(r.returncode==expect,{'name':name,'code':r.returncode,'stderr':r.stderr[-2500:],'records':values})
        self.workers.append({'name':name,'args':args,'exit_code':r.returncode});return values
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
        with socket.socket() as s:check(s.connect_ex(('127.0.0.1',18091))!=0,'18091 occupied')
        env=os.environ.copy();env.update(ES_URL=ES,ES_INDEX=READ,ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18091')
        self.log=(self.out/'application.log').open('w')
        self.proc=subprocess.Popen(['java','-Xms64m','-Xmx192m','-jar','backend/target/travel-search-0.7.0.jar'],cwd=ROOT,env=env,stdout=self.log,stderr=subprocess.STDOUT)
        def ready():
            check(self.proc.poll() is None,'Observation service exited')
            with urllib.request.urlopen(APP+'/',timeout=1) as r:return r.status==200
        wait(ready,'Observation service');self.save('observer-process',{'pid':self.proc.pid,'started':now()})
    def observe(self,name,want):
        body=json.loads((ROOT/'search/f41/search.json').read_text());value=self.req('POST','/api/attractions/search',body,base=APP)
        check([(x['id'],x['ticketPriceFen']) for x in value['items']]==want,value)
        replay=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',value['esRequest'])
        check([(x['_id'],x['_source']['ticket_price_fen']) for x in replay['hits']['hits']]==want,replay)
        self.save(name+'-java-search',{'request':body,'response':value,'rest_replay':replay,'pid':self.proc.pid if self.proc else None})
        if ARGS.observer:
            spec=importlib.util.spec_from_file_location('f41_observer',ARGS.observer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            m.capture(name,want,APP,ES,READ,self.out)
    def prepare(self):
        self.case='prepare';self.guard();check(not JOB.exists(),'Cleanup previous job first')
        check(not self.req('GET','/connectors',base=CONNECT),'Cleanup previous connector first')
        check(self.sql(text="SELECT to_regnamespace('f41') IS NOT NULL;").strip()=='f','Cleanup previous source first')
        password=(INFRA/'.local/cdc.properties').read_text().strip().split('=',1)[1]
        sql("\\set cdc_password '"+password+"'\n"+source('setup.sql'))
        self.save('source-setup',{'file':'data/f41/setup.sql','secret_via_stdin':True,'passed':True})
        command(kafka('kafka-topics','--create','--topic',TOPIC,'--partitions','1','--replication-factor','1','--config','cleanup.policy=delete','--config','retention.ms=604800000'))
        for v in ['v1','v2']:self.req('PUT','/'+INDEX[v],json.loads((ROOT/f'search/f41/create-{v}.json').read_text()))
        self.req('POST','/_aliases',json.loads((ROOT/'search/f41/aliases.json').read_text()))
        self.req('POST','/connectors',json.loads((ROOT/'cdc/f41/connector.json').read_text()),base=CONNECT,expected=201)
        def running():
            s=self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=False)
            return s['connector']['state']=='RUNNING' and len(s['tasks'])==1 and s['tasks'][0]['state']=='RUNNING'
        wait(running,'Connector RUNNING');self.wait_events(3)
        self.worker('seed-v1','seed','v1',0);self.worker('initial-v1','drain','v1',3);self.refresh()
        self.save('initial-events',self.events())
    def snapshot_open(self):
        check(not JOB.exists(),'Previous job exists')
        position=self.positions();check(position['end']==3 and position['begin']==0,'Clean three-row starting point required')
        job={'generation':secrets.token_hex(8),'source':position,'low':position['end'],'snapshot_complete':False,'fences':{},'active':'v1',
             'es_cluster_uuid':self.req('GET','/')['cluster_uuid'],
             'index_uuids':{v:self.req('GET','/'+i+'/_settings')[i]['settings']['index']['uuid'] for v,i in INDEX.items()}}
        write_job(job);self.save('captured-low',job)
        self.worker('seed-v2','seed','v2',job['low'])
        self.snapshot=subprocess.Popen(sql_args(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,cwd=ROOT)
        self.snapshot.stdin.write('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\nSELECT pg_current_snapshot();\n\\echo F41_READY\n');self.snapshot.stdin.flush()
        lines=self.snapshot_until('F41_READY');self.save('snapshot-open',{'at':now(),'low':job['low'],'pg_snapshot':lines,'transaction_still_open':True})
    def snapshot_until(self,marker):
        # readline is bounded by the psql server statement_timeout, rather than
        # timing the concurrent writer to win a race.
        rows=[]
        while True:
            line=self.snapshot.stdout.readline()
            if not line:raise AssertionError('Snapshot session exited: '+self.snapshot.stderr.read())
            if line.strip()==marker:return rows
            if line.strip():rows.append(line.strip())
    def snapshot_close(self):
        self.snapshot.stdin.write("SET LOCAL statement_timeout='30s';\nSELECT f41.envelope(attraction_id)::text FROM f41.projection_clock ORDER BY attraction_id;\nCOMMIT;\n\\echo F41_DONE\n\\q\n");self.snapshot.stdin.flush()
        rows=self.snapshot_until('F41_DONE');self.snapshot.wait(timeout=40);check(self.snapshot.returncode==0,self.snapshot.stderr.read());self.snapshot=None
        check([json.loads(r)['attraction_id'] for r in rows]==['p01','p02','p03'],rows)
        check(json.loads(rows[0])['ticket_price_fen']==6000 and not json.loads(rows[1])['sync_deleted'],'Snapshot not held across writes')
        path=LOCAL/'snapshot.json';path.write_text(json.dumps({'documents':rows},ensure_ascii=False,indent=2)+'\n')
        job=read_job();job.update(snapshot_path=str(path.relative_to(ROOT)),snapshot_sha256=sha(path));write_job(job)
        self.save('snapshot-export',{'documents':rows,'sha256':sha(path),'captured_before_concurrent_transactions':True})
    def snapshot_apply(self):
        job=read_job();path=ROOT/job['snapshot_path'];check(sha(path)==job['snapshot_sha256'],'Snapshot file changed')
        self.worker('snapshot-load','snapshot','v2',str(path));job['snapshot_complete']=True;write_job(job);self.save('snapshot-complete',job)
    def fence(self,key):
        check(key in ['backfill','cutover','rollback','final'],'Unknown fence')
        raw=self.sql(text="\\set fence_key '"+key+"'\n"+source('fence.sql'))
        expected=next(json.loads(x) for x in raw.splitlines() if x.startswith('{'))
        def found():
            return next((e for e in self.events() if json.loads(e['value'])['after']['fence_key']==key),None)
        event=wait(found,'Committed source fence '+key);high=event['offset']+1
        job=read_job();job['fences'][key]={'high':high,'expected':expected,'source_event':event};write_job(job)
        self.save('fence-'+key,job['fences'][key]);return high
    def compare(self,version,fence):
        got=self.docs(version);wanted={}
        for raw in fence['expected']['documents']:
            doc=json.loads(raw);doc['projection_schema']=1 if version=='v1' else 2
            if version=='v2' and not doc['sync_deleted']:
                price=doc['ticket_price_fen'];doc['price_band']='free' if price==0 else 'under_50' if price<5000 else 'from_50'
            doc['sync_hash']=hashlib.sha256(((str(doc['projection_schema'])+'\n')+raw).encode()).hexdigest()
            wanted[doc['attraction_id']]=doc
        check(got==wanted,{'version':version,'actual':got,'expected':wanted});return got
    def gate(self,key,save=True):
        job=read_job();position=self.positions();fence=job['fences'][key];high=fence['high']
        check(job['source']['topic_id']==position['topic_id'] and job['source']['kafka_cluster_id']==position['kafka_cluster_id'],'Source topic/cluster identity changed')
        check(position['begin']<=job['low'],'Low watermark no longer retained; rebuild needs a new generation')
        check(self.req('GET','/')['cluster_uuid']==job['es_cluster_uuid'],'ES cluster changed')
        for v,index in INDEX.items():check(self.req('GET','/'+index+'/_settings')[index]['settings']['index']['uuid']==job['index_uuids'][v],'Target index was recreated')
        check(job['snapshot_complete'] and sha(ROOT/job['snapshot_path'])==job['snapshot_sha256'],'Full snapshot is not completed or changed')
        check(position['committed_next']=={'v1':high,'v2':high},{'reason':'Both targets must be exactly at this fence','position':position,'high':high})
        self.refresh();docs={v:self.compare(v,fence) for v in INDEX}
        aliases=self.req('GET','/_alias/'+READ+',tut-f41-v1-ingest,tut-f41-v2-ingest')
        for v,index in INDEX.items():
            check(aliases[index]['aliases']['tut-f41-'+v+'-ingest']['is_write_index'],'Dedicated ingestion target changed')
        active=[i for i,detail in aliases.items() if READ in detail['aliases']]
        check(active==[INDEX[job['active']]],{'active':active,'job':job['active']})
        check(aliases[active[0]]['aliases'][READ]['filter']=={'term':{'sync_deleted':False}},'Read filter changed')
        result={'at':now(),'passed':True,'generation':job['generation'],'fence':key,'high':high,'source':position,
                'snapshot_sha256':job['snapshot_sha256'],'active_before':job['active'],'complete_documents':docs,
                'backlog_after_fence':position['end']-high,'aliases':aliases}
        if save:self.save('gate-'+key,result)
        return result
    def rejected(self,name,key):
        with coordinator():
            before=self.req('GET','/_alias/'+READ)
            try:self.gate(key)
            except AssertionError as error:
                after=self.req('GET','/_alias/'+READ);check(before==after,'Rejected gate changed routing')
                self.save(name,{'rejected':True,'reason':str(error),'aliases_unchanged':True,'positions':self.positions()});return
            raise AssertionError('Gate unexpectedly accepted '+name)
    def switch(self,key,target):
        with coordinator():
            evidence=self.gate(key);job=read_job();check(job['active']!=target,'Already on target')
            filename='cutover.json' if target=='v2' else 'rollback.json'
            response=self.req('POST','/_aliases',json.loads((ROOT/'search/f41'/filename).read_text()))
            check(response.get('acknowledged') and not response.get('errors',False),response)
            job['active']=target;write_job(job);aliases=self.req('GET','/_alias/'+READ)
            check(list(aliases)==[INDEX[target]],aliases)
            self.save('switch-'+key,{'gate':evidence,'response':response,'active':target,'aliases':aliases})
    def run(self):
        self.prepare();self.app_start();self.observe('initial',[('p01',6000),('p02',0)])
        self.case='c01-full-and-continuous-delta'
        self.req('PUT','/'+ONCE,json.loads((ROOT/'search/f41/create-v1.json').read_text()))
        reindex=self.req('POST','/_reindex?refresh=true',{'source':{'index':INDEX['v1']},'dest':{'index':ONCE}})
        check(reindex['created']==3 and not reindex['failures'],reindex);self.save('once-reindex',reindex)
        self.snapshot_open();self.sql('during-snapshot.sql');self.snapshot_close();high=self.fence('backfill')
        check(high==9,high)
        self.worker('backfill-live','drain','v1',high);self.worker('delta-before-snapshot','drain','v2',high)
        self.rejected('gate-reject-snapshot-incomplete','backfill')
        self.snapshot_apply();self.refresh()
        with coordinator():self.gate('backfill')
        self.observe('backfill',[('p01',6500),('p04',4500)])
        stale=self.req('POST','/'+ONCE+'/_search',{'query':{'match_all':{}},'sort':[{'attraction_id':'asc'}]})
        check([h['_id'] for h in stale['hits']['hits']]==['p01','p02','p03'] and stale['hits']['hits'][0]['_source']['ticket_price_fen']==6000,stale)
        self.save('once-stale',stale)
        self.case='c02-lag-failure-and-cutover';self.sql('backlog.sql');high=self.fence('cutover');check(high==13,high)
        self.worker('cutover-live','drain','v1',high);self.rejected('gate-reject-lag','cutover')
        self.req('PUT','/'+INDEX['v2']+'/_settings',{'index.blocks.write':True})
        before=self.positions();self.worker('blocked-new-target','drain','v2',high,expect=1)
        check(self.positions()['committed_next']==before['committed_next'],'Blocked write advanced checkpoint')
        self.rejected('gate-reject-target-failure','cutover')
        self.req('PUT','/'+INDEX['v2']+'/_settings',{'index.blocks.write':False})
        self.worker('resume-new-target','drain','v2',high)
        self.sql('after-fence.sql');self.wait_events(15)
        self.switch('cutover','v2');self.observe('cutover',[('p01',7000),('p04',4500)])
        bands=self.req('POST','/'+READ+'/_search',{'query':{'term':{'price_band':'under_50'}}})
        check([h['_id'] for h in bands['hits']['hits']]==['p04'],bands);self.save('v2-price-band',bands)
        self.case='c03-mirror-and-rollback';high=self.fence('rollback');check(high==16,high)
        self.worker('new-after-switch','drain','v2',high);self.refresh();self.observe('new-live',[('p01',7200)])
        self.rejected('rollback-reject-old-lag','rollback')
        self.worker('old-mirror-catchup','drain','v1',high);self.switch('rollback','v1');self.observe('rollback',[('p01',7200)])
        self.sql('after-rollback.sql');high=self.fence('final');check(high==19,high)
        for v in INDEX:self.worker('final-'+v,'drain',v,high)
        self.worker('late-snapshot-again','snapshot','v2',str(LOCAL/'snapshot.json'))
        with coordinator():final=self.gate('final')
        self.observe('final',[('p01',7600),('p04',4800)])
        for v in INDEX:
            values=self.worker('empty-'+v,'drain',v,high);check(values[-1]['processed']==0,values)
        self.save('final-events',self.events());self.save('job-final',read_job())
        self.save('summary',{'at':now(),'passed':True,'cases':3,'source_events':19,'document_events':15,'fences':4,
            'worker_runs':len(self.workers),'http_requests':len(self.http),'final_positions':self.positions(),
            'final_revisions':{id:doc['sync_revision'] for id,doc in final['complete_documents']['v1'].items()},
            'active':'v1','observation_process_same_pid':self.proc.pid,'workers':self.workers})
    def cleanup(self):
        self.case='cleanup';self.guard()
        with coordinator():
            for group in GROUPS:
                state=command(kafka('kafka-consumer-groups','--describe','--group',group,'--state'),required=False)
                check('Stable' not in state.stdout and 'Rebalancing' not in state.stdout,state.stdout)
            if NAME in self.req('GET','/connectors',base=CONNECT):
                self.req('PUT','/connectors/'+NAME+'/stop',base=CONNECT,expected=204)
                wait(lambda:self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=False)['connector']['state']=='STOPPED','Connector stopped')
                self.req('DELETE','/connectors/'+NAME+'/offsets',base=CONNECT);self.req('DELETE','/connectors/'+NAME,base=CONNECT,expected=204)
            self.sql(text="SELECT pg_drop_replication_slot(slot_name) FROM pg_replication_slots WHERE slot_name='f41_slot'; DROP PUBLICATION IF EXISTS f41_publication; DROP SCHEMA IF EXISTS f41 CASCADE; DO $$ BEGIN IF EXISTS(SELECT FROM pg_roles WHERE rolname='f41_cdc') THEN EXECUTE 'REVOKE CONNECT ON DATABASE travel_f41 FROM f41_cdc'; END IF; END $$; DROP ROLE IF EXISTS f41_cdc;")
            if TOPIC in command(kafka('kafka-topics','--list')).stdout.splitlines():command(kafka('kafka-topics','--delete','--topic',TOPIC))
            groups=command(kafka('kafka-consumer-groups','--list')).stdout.splitlines()
            for group in GROUPS:
                if group in groups:command(kafka('kafka-consumer-groups','--delete','--group',group))
            for index in [*INDEX.values(),ONCE]:self.req('DELETE','/'+index,expected=[200,404])
            for name in ['job.json','snapshot.json']:(LOCAL/name).unlink(missing_ok=True)
        self.save('summary',{'at':now(),'passed':True,'deleted':['F41 source schema, clock, outbox, connector/source offsets, publication/slot/CDC role','F41 business topic, two groups, three named ES indices and aliases','F41 local rebuild checkpoint and snapshot'],
            'preserved':['F41 named volumes, Connect internal topics, local secrets','all unrelated projects']})
    def close(self):
        if self.snapshot and self.snapshot.poll() is None:self.snapshot.kill();self.snapshot.wait(timeout=10)
        if self.proc and self.proc.poll() is None:self.proc.terminate();self.proc.wait(timeout=20)
        if self.log:self.log.close()

def init(lab):
    local=INFRA/'.local';check(not local.exists(),'Existing .local: preserve secrets')
    check(not command(['docker','volume','ls','-q','--filter','label=com.docker.compose.project=es-framework-f41']).stdout.strip(),'Existing F41 volumes: preserve secrets')
    local.mkdir(mode=0o700)
    for name,value in [('pg-password.txt',secrets.token_urlsafe(32)),('cdc.properties','password='+secrets.token_urlsafe(32))]:
        path=local/name;path.write_text(value+'\n');path.chmod(0o600)
    lab.save('summary',{'passed':True,'local_secrets_created':True,'secrets_printed':False})
def start(lab):
    compose('up','-d');wait(lambda:sql('SELECT 1;',required=False).returncode==0,'PostgreSQL')
    wait(lambda:command(kafka('kafka-topics','--list'),required=False).returncode==0,'Kafka')
    wait(lambda:lab.req('GET','/connector-plugins',base=CONNECT,record=False),'Connect')
    wait(lambda:lab.req('GET','/_cluster/health?wait_for_status=yellow&timeout=1s',record=False).get('status') in ['green','yellow'],'ES')
    lab.identity();lab.save('summary',{'at':now(),'passed':True})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init','start','prepare','run','cleanup','down','step','inspect','snapshot','load','fence','drain','gate','switch','refresh'])
    p.add_argument('value',nargs='?');p.add_argument('--out',required=True);p.add_argument('--observer');ARGS=p.parse_args();lab=Lab(ARGS.out)
    try:
        if ARGS.action=='init':init(lab)
        elif ARGS.action=='start':start(lab)
        elif ARGS.action=='down':lab.identity();lab.guard();compose('down');lab.save('summary',{'passed':True,'named_volumes_and_secrets_preserved':True})
        else:
            lab.identity()
            if ARGS.action=='prepare':lab.prepare()
            elif ARGS.action=='run':lab.run()
            elif ARGS.action=='cleanup':lab.cleanup()
            elif ARGS.action=='step':
                check(ARGS.value in ['during-snapshot','backlog','after-fence','after-rollback'],'Unknown step');lab.sql(ARGS.value+'.sql')
            elif ARGS.action=='snapshot':
                lab.snapshot_open();lab.sql('during-snapshot.sql');lab.snapshot_close()
            elif ARGS.action=='load':lab.snapshot_apply()
            elif ARGS.action=='fence':print(json.dumps({'high':lab.fence(ARGS.value)}))
            elif ARGS.action=='drain':
                key,version=ARGS.value.split(':');check(version in INDEX,'Version required');lab.worker('drain','drain',version,read_job()['fences'][key]['high'])
            elif ARGS.action=='gate':
                with coordinator():lab.gate(ARGS.value)
            elif ARGS.action=='switch':
                check(ARGS.value in ['cutover','rollback'],'Unknown switch');lab.switch(ARGS.value,'v2' if ARGS.value=='cutover' else 'v1')
            elif ARGS.action=='refresh':lab.refresh()
            else:lab.save('events',lab.events());lab.save('positions',lab.positions());print(json.dumps(lab.positions()))
        print(json.dumps({'action':ARGS.action,'evidence':str(lab.out),'passed':True},ensure_ascii=False))
    finally:lab.close()
