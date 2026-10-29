#!/usr/bin/env python3
"""F40 real PG outboxes -> Debezium -> two Kafka topics -> Java -> ES."""
import argparse, datetime, http.client, importlib.util, json, os, pathlib, secrets, socket, subprocess, time, urllib.error, urllib.request
from fault_proxy import Proxy

ROOT=pathlib.Path(__file__).resolve().parents[2]
INFRA=ROOT/'infra/f40'; ES='http://127.0.0.1:20440'; CONNECT='http://127.0.0.1:18340'; APP='http://127.0.0.1:18090'
INDEX='tut-f40-attractions-v001'; NAIVE='tut-f40-naive-v001'; READ='tut-f40-attractions-read'
TOPICS=['travel_f40.f40.root_event','travel_f40.f40.related_event']; DLQ='f40-es-dlq'; GROUP='f40-es-v1'; NAME='f40-pg'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok,detail):
    if not ok:raise AssertionError(detail)
def command(args,data=None,required=True,env=None):
    r=subprocess.run(args,input=data,text=True,capture_output=True,cwd=ROOT,env=env,timeout=180)
    if required:check(r.returncode==0,{'command':args,'code':r.returncode,'stderr':r.stderr[-2500:],'stdout':r.stdout[-2500:]})
    return r
def compose_args(*args):return ['docker','compose','-f',str(INFRA/'compose.yaml'),*args]
def compose(*args):return command(compose_args(*args)).stdout
def sql(content,required=True):return command(compose_args('exec','-T','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-U','travel','-d','travel_f40'),content,required)
def source(name):return (ROOT/'data/f40'/name).read_text()
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
def java(*args,proxy=False):
    env=os.environ.copy()
    if proxy:env['F40_ES_URL']='http://127.0.0.1:20441'
    r=command(['bash','labs/f40/java.sh',*args],required=False,env=env)
    values=[json.loads(x) for x in r.stdout.splitlines() if x.startswith('{')]
    return values,r
def public(v):
    if isinstance(v,dict):return {k:'<file-provider-reference>' if k=='database.password' else public(x) for k,x in v.items()}
    if isinstance(v,list):return [public(x) for x in v]
    return v

class Lab:
    def __init__(self,out):
        self.out=pathlib.Path(out).resolve();self.out.mkdir(parents=True,exist_ok=False)
        self.case='identity';self.http=[];self.worker=[];self.proc=None;self.log=None;self.proxy=None
    def save(self,name,value):(self.out/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    def req(self,method,path,body=None,expected=200,base=ES,record=True):
        data=None if body is None else json.dumps(body,ensure_ascii=False).encode()
        req=urllib.request.Request(base+path,data=data,method=method,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=15) as r:status=r.status;raw=r.read()
        except urllib.error.HTTPError as e:status=e.code;raw=e.read()
        value=json.loads(raw) if raw else None
        rec={'at':now(),'case':self.case,'base':base,'method':method,'path':path,'body':public(body),'status':status,'response':public(value)}
        if record:
            self.http.append(rec)
            with (self.out/'http.jsonl').open('a') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
        check(status in ([expected] if isinstance(expected,int) else expected),rec)
        return value
    def sql(self,name=None,text=None):
        body=source(name) if name else text;r=sql(body)
        with (self.out/'sql.jsonl').open('a') as f:f.write(json.dumps({'at':now(),'case':self.case,'file':name,'sql':body,'stdout':r.stdout},ensure_ascii=False)+'\n')
        return r.stdout
    def identity(self):
        es=self.req('GET','/');check(es['cluster_name']=='travel-f40-lab' and es['version']['number']=='9.4.0',es)
        pg=self.sql(text='SELECT current_database(),version();');check(pg.startswith('travel_f40|PostgreSQL 17.5'),pg)
        plugins=self.req('GET','/connector-plugins',base=CONNECT)
        check(any(p['class']=='io.debezium.connector.postgresql.PostgresConnector' and p['version']=='3.3.1.Final' for p in plugins),plugins)
        self.save('identity',{'es':es,'pg':pg,'plugins':plugins,'at':now()})
    def guard(self):
        indices=self.req('GET','/_cat/indices?format=json&expand_wildcards=all')
        check(all(x['index'] in [INDEX,NAIVE] or x['index'].startswith('.') for x in indices),'Foreign ES index')
        names=command(kafka('kafka-topics','--list')).stdout.splitlines()
        check(set(names)<=set(TOPICS+[DLQ,'f40-connect-configs','f40-connect-offsets','f40-connect-status','__consumer_offsets']),'Foreign Kafka topic')
        check(set(self.req('GET','/connectors',base=CONNECT))<=set([NAME]),'Foreign connector')
    def worker_run(self,name,*args,expect=0,proxy=False):
        values,r=java(*args,proxy=proxy);self.save(name,{'exit_code':r.returncode,'records':values})
        (self.out/(name+'.stderr.txt')).write_text(r.stderr)
        check(r.returncode==expect,{'name':name,'code':r.returncode,'stderr':r.stderr[-2500:],'records':values})
        self.worker.append({'name':name,'mode':list(args),'exit_code':r.returncode,'records':values})
        return values
    def events(self):
        values,r=java('inspect');check(r.returncode==0,r.stderr)
        return [v for v in values if v['kind']=='event']
    def wait_events(self,count):wait(lambda:len(self.events())>=count,'Expected '+str(count)+' source events')
    def state(self):
        values,r=java('inspect');check(r.returncode==0,r.stderr);return values[-1]['positions']
    def next(self,channel='root'):return self.state()['travel_f40.f40.'+channel+'_event']['committed_next']
    def get(self,id):return self.req('GET','/'+INDEX+'/_doc/'+id)['_source']
    def refresh(self):check(self.req('POST','/'+INDEX+'/_refresh')['_shards']['failed']==0,'Refresh failure')
    def docs(self,name):
        result=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',{'size':20,'sort':[{'attraction_id':'asc'}],'query':{'match_all':{}}})
        check(not result['timed_out'] and result['_shards']['failed']==0,result);self.save(name,result)
        return {h['_id']:h['_source'] for h in result['hits']['hits']}
    def expected(self):
        rows=self.sql(text="SELECT json_build_object('id',c.attraction_id,'revision',c.revision,'document',f40.project(c.attraction_id)) FROM f40.projection_clock c ORDER BY c.attraction_id;")
        return [json.loads(x) for x in rows.splitlines()]
    def compare(self,name):
        got=self.docs(name);wanted={}
        for row in self.expected():
            if row['document'] is None:continue
            d=row['document'];d.update(sync_revision=row['revision'],sync_deleted=False);wanted[row['id']]=d
        reduced={id:{k:v for k,v in d.items() if k!='sync_hash'} for id,d in got.items()}
        check(reduced==wanted,{'actual':reduced,'expected':wanted});return got
    def app_start(self):
        with socket.socket() as s:check(s.connect_ex(('127.0.0.1',18090))!=0,'18090 occupied')
        env=os.environ.copy();env.update(ES_URL=ES,ES_INDEX=READ,ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18090')
        self.log=(self.out/'application.log').open('w')
        self.proc=subprocess.Popen(['java','-Xms64m','-Xmx192m','-jar','backend/target/travel-search-0.7.0.jar'],cwd=ROOT,env=env,stdout=self.log,stderr=subprocess.STDOUT)
        def ready():
            check(self.proc.poll() is None,'Java service exited')
            with urllib.request.urlopen(APP+'/',timeout=1) as r:return r.status==200
        wait(ready,'Observation service')
    def observe(self,name,want):
        body=json.loads((ROOT/'search/f40/search.json').read_text())
        result=self.req('POST','/api/attractions/search',body,base=APP)
        check([(x['id'],x['ticketPriceFen']) for x in result['items']]==want,result)
        replay=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',result['esRequest'])
        check([(x['_id'],x['_source']['ticket_price_fen']) for x in replay['hits']['hits']]==want,replay)
        self.save(name+'-java-search',{'request':body,'response':result,'rest_replay':replay})
        if ARGS.observer:
            spec=importlib.util.spec_from_file_location('f40_observer',ARGS.observer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
            m.capture(name,want,APP,ES,READ,self.out)
    def prepare(self):
        self.case='prepare';self.guard()
        check(not self.req('GET','/connectors',base=CONNECT),'Cleanup old connector first')
        check(self.sql(text="SELECT to_regnamespace('f40') IS NOT NULL;").strip()=='f','Cleanup old schema first')
        password=(INFRA/'.local/cdc.properties').read_text().strip().split('=',1)[1]
        sql("\\set cdc_password '"+password+"'\n"+source('setup.sql'))
        self.save('source-setup',{'file':'data/f40/setup.sql','secret_via_stdin':True,'passed':True})
        for topic in TOPICS+[DLQ]:command(kafka('kafka-topics','--create','--topic',topic,'--partitions','1','--replication-factor','1','--config','cleanup.policy=delete','--config','retention.ms=604800000'))
        self.req('PUT','/'+INDEX,json.loads((ROOT/'search/f40/create.json').read_text()))
        self.req('POST','/_aliases',json.loads((ROOT/'search/f40/aliases.json').read_text()))
        self.req('POST','/connectors',json.loads((ROOT/'cdc/f40/connector.json').read_text()),expected=201,base=CONNECT)
        def running():
            s=self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=False)
            return s['connector']['state']=='RUNNING' and len(s['tasks'])==1 and s['tasks'][0]['state']=='RUNNING'
        wait(running,'Connector RUNNING');self.wait_events(3)
        self.save('initial-events',self.events())
    def change(self,price):
        self.sql(text="BEGIN; SELECT pg_advisory_xact_lock(40040); UPDATE f40.attraction SET ticket_price_fen="+str(price)+" WHERE attraction_id='p01'; SELECT f40.emit('p01','root'); COMMIT;")
    def repair_file(self,events):
        check(len(events)==1,'This lesson repair expects exactly the p02 failure')
        audit=json.loads(events[0]['value']);envelope=json.loads(audit['value']);after=envelope['after']
        check(after['attraction_id']=='p02' and after['revision']==3,'Review this different failure manually')
        check(self.sql(text="SELECT revision FROM f40.projection_clock WHERE attraction_id='p02';").strip()=='3','Newer source state exists; do not relabel it as revision 3')
        good=self.sql(text="SELECT f40.project('p02') || jsonb_build_object('sync_revision',revision,'sync_deleted',false) FROM f40.projection_clock WHERE attraction_id='p02';").strip()
        after['document']=good;audit['value']=json.dumps(envelope,ensure_ascii=False);audit['repair_note']='Repair projection price serialization from authoritative SQL; revision 3 has not been applied. Original DLQ retained.'
        self.save('reviewed-repair',audit)
        return self.out/'reviewed-repair.json'
    def run(self):
        self.prepare();self.app_start();self.case='c01-duplicate-and-crash'
        self.worker_run('initial-apply','drain','root');self.refresh();self.compare('initial-complete');self.observe('initial',[('p01',6000),('p02',0)])
        self.sql('crash.sql');self.wait_events(4);before=self.next()
        self.worker_run('crash-after-es','drain','root','crash',expect=40)
        check(self.next()==before,'Crash committed');check(self.get('p01')['ticket_price_fen']==6500,'ES did not write')
        self.worker_run('restart-replay','drain','root');check(self.next()==before+1,'Restart next')
        self.worker_run('replay-duplicates','replay','root');self.refresh();self.compare('duplicate-complete');self.observe('duplicate',[('p01',6500),('p02',0)])
        self.case='c02-cross-topic-delete';self.sql('reorder.sql');self.wait_events(7)
        self.worker_run('new-related-first','drain','related');check(self.get('p01')['sync_revision']==4,'Expected v4')
        self.worker_run('old-root-late','drain','root');check(self.get('p01')['sync_revision']==4,'Old event overwrote v4')
        self.refresh();self.compare('ordered-complete');self.observe('reordered',[('p01',7000),('p02',0)])
        self.req('PUT','/'+NAIVE,json.loads((ROOT/'search/f40/create.json').read_text()))
        entries=[json.loads(e['value'])['after'] for e in self.events()]
        v2=next(json.loads(e['document']) for e in entries if e['attraction_id']=='p01' and e['revision']==2)
        v4=next(json.loads(e['document']) for e in entries if e['attraction_id']=='p01' and e['revision']==4)
        self.req('PUT','/'+NAIVE+'/_doc/p01',v4,expected=201);self.req('PUT','/'+NAIVE+'/_doc/p01',v2)
        check(self.req('GET','/'+NAIVE+'/_doc/p01')['_source']['ticket_price_fen']==6500,'Naive overwrite counterexample')
        self.req('DELETE','/'+NAIVE+'/_doc/p01');self.req('PUT','/'+NAIVE+'/_doc/p01',v4,expected=201)
        self.save('naive-resurrection',self.req('GET','/'+NAIVE+'/_doc/p01'))
        self.sql('delete.sql');self.wait_events(8);self.worker_run('delete-marker','drain','root');self.refresh()
        marker=self.get('p01');check(marker['sync_deleted'] and marker['sync_revision']==5 and 'name' not in marker,marker)
        self.save('delete-marker',marker);self.worker_run('old-after-delete','replay','related');self.refresh()
        check(self.get('p01')==marker,'Resurrection after old event');self.compare('deleted-complete');self.observe('deleted',[('p02',0)])
        check(self.req('GET','/'+READ+'/_doc/p01')['_source']['sync_deleted'],'Alias GET bypasses filter must be documented')
        self.sql('reopen.sql');self.wait_events(9);self.worker_run('reopened-apply','drain','root');self.refresh();self.compare('reopened-complete');self.observe('reopened',[('p01',7200),('p02',0)])
        self.case='c03-partial-dlq';self.sql('partial.sql');self.wait_events(12);before=self.next()
        values=self.worker_run('partial-block','drain','root',expect=1)
        statuses=[v['status'] for v in values if v['kind']=='item'];check(statuses==[200,400,200],statuses)
        check(self.next()==before,'Partial batch committed past failed record')
        self.worker_run('partial-park','drain','root','park');check(self.next()==before+3,'Parked batch not committed')
        self.refresh();self.observe('parked',[('p01',7500),('p02',0)])
        dlq=self.worker_run('dlq-evidence','dlq');events=[v for v in dlq if v['kind']=='event'];check(len(events)==1,events)
        repair=self.repair_file(events)
        self.worker_run('repair-applied','repair',str(repair));self.worker_run('repair-duplicate','repair',str(repair))
        self.refresh();self.compare('repaired-complete');self.observe('repaired',[('p01',7500),('p02',1000)])
        self.case='c04-retry-and-unavailable';self.proxy=Proxy(self.out);self.proxy.start()
        self.sql(text="BEGIN; SELECT pg_advisory_xact_lock(40040); UPDATE f40.attraction SET ticket_price_fen=7800 WHERE attraction_id='p01'; UPDATE f40.attraction SET ticket_price_fen=1200 WHERE attraction_id='p02'; SELECT f40.emit('p01','root'),f40.emit('p02','root'); COMMIT;")
        self.wait_events(14);self.proxy.mode='item429_once'
        values=self.worker_run('item429-retry','drain','root',proxy=True)
        check([(v['id'],v['status']) for v in values if v['kind']=='item']==[('p01',200),('p02',429),('p02',200)],values)
        self.change(7900);self.wait_events(15);before=self.next();self.proxy.mode='429'
        self.worker_run('request429-exhausted','drain','root',proxy=True,expect=1);check(self.next()==before,'429 committed')
        self.proxy.mode='off';self.worker_run('request429-recovery','drain','root')
        self.change(8000);self.wait_events(16);before=self.next();compose('stop','es')
        try:
            self.worker_run('es-unavailable','drain','root',expect=1);check(self.next()==before,'Unavailable committed')
        finally:
            compose('start','es');wait(lambda:self.req('GET','/_cluster/health?wait_for_status=yellow&timeout=1s',record=False).get('status') in ['green','yellow'],'ES recovery')
        self.worker_run('es-recovered','drain','root')
        self.change(8100);self.wait_events(17);self.proxy.mode='drop_once'
        self.worker_run('acknowledgement-lost','drain','root',proxy=True)
        self.refresh();final=self.compare('final-complete');self.observe('final',[('p01',8100),('p02',1200)])
        empty=self.worker_run('restart-empty','drain','all');check(empty[-1]['processed']==0,empty[-1])
        self.save('final-events',self.events());self.save('source-vs-es',{'rows':self.expected(),'visible':final})
        self.save('summary',{'at':now(),'passed':True,'cases':4,'source_events':17,'final_positions':self.state(),'worker_runs':len(self.worker),'http_requests':len(self.http),'http_by_base':{b:sum(x['base']==b for x in self.http) for b in [ES,CONNECT,APP]},'final_ids':list(final),'final_revisions':{id:d['sync_revision'] for id,d in final.items()},'observed_prices_fen':{'p01':8100,'p02':1200,'p03':3200},'limits':['single VM, broker, partition per topic, consumer','cooperative serial writer/outbox, not arbitrary writers','HTTP/item 429 and lost acknowledgement are explicit injected faults','no HA, arbitrary power-loss, Kafka/DLQ outage, performance or online rebuild proof']})
    def cleanup(self):
        self.case='cleanup';self.guard()
        # All readers/workers must be stopped. Do not reset an active group.
        desc=command(kafka('kafka-consumer-groups','--describe','--group',GROUP,'--state'),required=False)
        check('Stable' not in desc.stdout and 'Rebalancing' not in desc.stdout,desc.stdout)
        if NAME in self.req('GET','/connectors',base=CONNECT):
            self.req('PUT','/connectors/'+NAME+'/stop',base=CONNECT,expected=204)
            wait(lambda:self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=False)['connector']['state']=='STOPPED','Connector stopped')
            self.req('DELETE','/connectors/'+NAME+'/offsets',base=CONNECT);self.req('DELETE','/connectors/'+NAME,base=CONNECT,expected=204)
        self.sql(text="SELECT pg_drop_replication_slot(slot_name) FROM pg_replication_slots WHERE slot_name='f40_slot'; DROP PUBLICATION IF EXISTS f40_publication; DROP SCHEMA IF EXISTS f40 CASCADE; DO $$ BEGIN IF EXISTS(SELECT FROM pg_roles WHERE rolname='f40_cdc') THEN EXECUTE 'REVOKE CONNECT ON DATABASE travel_f40 FROM f40_cdc'; END IF; END $$; DROP ROLE IF EXISTS f40_cdc;")
        names=command(kafka('kafka-topics','--list')).stdout.splitlines()
        for topic in TOPICS+[DLQ]:
            if topic in names:command(kafka('kafka-topics','--delete','--topic',topic))
        groups=command(kafka('kafka-consumer-groups','--list')).stdout.splitlines()
        if GROUP in groups:command(kafka('kafka-consumer-groups','--delete','--group',GROUP))
        self.req('DELETE','/'+INDEX,expected=[200,404]);self.req('DELETE','/'+NAIVE,expected=[200,404])
        self.save('summary',{'at':now(),'passed':True,'deleted':['F40 connector/source offset/schema/publication/slot/CDC role','two outbox topics, DLQ, application group','two explicit F40 indices and aliases'],'preserved':['F40 named volumes and local secret files','Connect internal topics','all other Compose projects']})
    def close(self):
        if self.proc and self.proc.poll() is None:self.proc.terminate();self.proc.wait(timeout=20)
        if self.log:self.log.close()
        if self.proxy:self.proxy.close()

def init(lab):
    local=INFRA/'.local';check(not local.exists(),'Existing .local: preserve its secrets')
    check(not command(['docker','volume','ls','-q','--filter','label=com.docker.compose.project=es-framework-f40']).stdout.strip(),'Existing F40 volumes: do not replace secrets')
    local.mkdir(mode=0o700)
    for name,content in [('pg-password.txt',secrets.token_urlsafe(32)),('cdc.properties','password='+secrets.token_urlsafe(32))]:
        path=local/name;path.write_text(content+'\n');path.chmod(0o600)
    lab.save('summary',{'passed':True,'local_secrets_created':True,'secrets_printed':False})
def start(lab):
    compose('up','-d')
    wait(lambda:sql('SELECT 1;',required=False).returncode==0,'PostgreSQL')
    wait(lambda:command(kafka('kafka-topics','--list'),required=False).returncode==0,'Kafka')
    wait(lambda:lab.req('GET','/connector-plugins',base=CONNECT,record=False),'Connect')
    wait(lambda:lab.req('GET','/_cluster/health?wait_for_status=yellow&timeout=1s',record=False).get('status') in ['green','yellow'],'ES')
    lab.identity();lab.save('summary',{'passed':True,'started':now()})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init','start','prepare','run','cleanup','down','step','refresh','inspect','repair-file']);p.add_argument('step',nargs='?');p.add_argument('--out',required=True);p.add_argument('--observer')
    ARGS=p.parse_args();lab=Lab(ARGS.out)
    try:
        if ARGS.action=='init':init(lab)
        elif ARGS.action=='start':start(lab)
        elif ARGS.action=='down':
            lab.identity();lab.guard();compose('down');lab.save('summary',{'passed':True,'named_volumes_and_local_secrets_preserved':True})
        else:
            lab.identity()
            if ARGS.action=='prepare':lab.prepare()
            elif ARGS.action=='run':lab.run()
            elif ARGS.action=='cleanup':lab.cleanup()
            elif ARGS.action=='repair-file':
                values=lab.worker_run('dlq-evidence','dlq');print(lab.repair_file([v for v in values if v['kind']=='event']))
            elif ARGS.action=='step':
                check(ARGS.step in ['crash','reorder','delete','reopen','partial'],'Unknown step');lab.sql(ARGS.step+'.sql')
            elif ARGS.action=='refresh':lab.refresh()
            else:lab.save('events',lab.events());lab.docs('search');print(json.dumps({'events':len(lab.events()),'positions':lab.state()},ensure_ascii=False))
        print(json.dumps({'action':ARGS.action,'evidence':str(lab.out),'passed':True},ensure_ascii=False))
    finally:lab.close()
