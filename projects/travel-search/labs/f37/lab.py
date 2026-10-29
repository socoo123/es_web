#!/usr/bin/env python3
"""F37 isolated PostgreSQL -> Debezium -> Kafka -> Java -> ES experiment."""
import argparse, collections, datetime, importlib.util, json, os, pathlib
import secrets, socket, subprocess, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
INFRA = ROOT / 'infra/f37'
ES = 'http://127.0.0.1:20137'
CONNECT = 'http://127.0.0.1:18137'
APP = 'http://127.0.0.1:18087'
INDEX = 'tut-f37-attractions-v001'
READ = 'tut-f37-attractions-read'
TOPIC = 'travel_f37.f37.attraction'
GROUP = 'f37-es-v1'
NAME = 'f37-pg'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok, detail):
    if not ok: raise AssertionError(detail)
def command(args, data=None, required=True):
    r = subprocess.run(args, input=data, text=True, capture_output=True, cwd=ROOT, timeout=120)
    if required: check(r.returncode == 0, {'command':args, 'stderr':r.stderr[-3000:], 'stdout':r.stdout[-2000:]})
    return r
def compose_args(*args): return ['docker','compose','-f',str(INFRA/'compose.yaml'),*args]
def compose(*args): return command(compose_args(*args)).stdout
def psql_args(): return compose_args('exec','-T','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-U','travel','-d','travel_f37')
def sql(text, required=True): return command(psql_args(),text,required)
def source(name): return (ROOT/'data/f37'/name).read_text()
def kafka(tool,*args):
    return compose_args('exec','-T','kafka','/opt/kafka/bin/'+tool+'.sh','--bootstrap-server','kafka:9092',*args)
def java(mode):
    r=command(['bash','labs/f37/java.sh',mode]);values=[]
    for line in r.stdout.splitlines():
        if line.startswith('{'):values.append(json.loads(line))
    check(values and values[-1]['kind']=='summary',r.stdout[-3000:]);return values,r
def wait(test, detail, attempts=90):
    last=None
    for _ in range(attempts):
        try:
            last=test()
            if last:return last
        except (OSError,urllib.error.URLError,AssertionError):pass
        time.sleep(1)
    raise TimeoutError((detail,last))
def decode(raw):
    if not raw:return None
    try:return json.loads(raw)
    except json.JSONDecodeError:return raw.decode(errors='replace')
def public(value):
    if isinstance(value,dict):return {k:'<redacted>' if k=='database.password' else public(v) for k,v in value.items()}
    if isinstance(value,list):return [public(v) for v in value]
    return value

class Lab:
    def __init__(self,out):
        self.out=pathlib.Path(out).resolve();self.out.mkdir(parents=True,exist_ok=False)
        self.case='identity';self.http=[];self.proc=None;self.log=None
    def save(self,name,value):
        (self.out/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    def req(self,method,path,body=None,expected=200,base=ES,record=True):
        request=urllib.request.Request(base+path,method=method,
            data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=20) as r:
                status=r.status;value=decode(r.read())
        except urllib.error.HTTPError as e:
            status=e.code;value=decode(e.read())
        rec={'at':now(),'case':self.case,'base':base,'method':method,'path':path,'body':public(body),'status':status,'response':public(value)}
        if record:
            self.http.append(rec)
            with (self.out/'http.jsonl').open('a') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
        check(status in ([expected] if isinstance(expected,int) else expected),rec)
        return value
    def sql(self,name=None,text=None,required=True):
        content=source(name) if name else text;r=sql(content,required)
        with (self.out/'sql.jsonl').open('a') as f:
            f.write(json.dumps({'at':now(),'case':self.case,'file':name,'sql':content,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},ensure_ascii=False)+'\n')
        return r.stdout if required else r
    def identity(self):
        root=self.req('GET','/');check(root['cluster_name']=='travel-f37-lab' and root['version']['number']=='9.4.0',root)
        pg=self.sql(text='SELECT current_database(), current_user, version();')
        check(pg.startswith('travel_f37|travel|PostgreSQL 17.5 '),pg)
        worker=self.req('GET','/',base=CONNECT)
        plugins=self.req('GET','/connector-plugins',base=CONNECT)
        check(any(p['class']=='io.debezium.connector.postgresql.PostgresConnector' and p['version']=='3.3.1.Final' for p in plugins),plugins)
        self.save('identity',{'es':root,'pg':pg,'connect':worker,'plugins':plugins})
    def guard(self):
        indices=self.req('GET','/_cat/indices?format=json&expand_wildcards=all')
        check(all(x['index']==INDEX or x['index'].startswith('.') for x in indices),'Foreign ES index')
        topics=command(kafka('kafka-topics','--list')).stdout.splitlines()
        check(set(topics)<=set([TOPIC,'f37-connect-configs','f37-connect-offsets','f37-connect-status','__consumer_offsets']),'Foreign Kafka topic')
        names=self.req('GET','/connectors',base=CONNECT);check(set(names)<=set([NAME]),names)
    def status(self,record=True): return self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=record)
    def running(self):
        def test():
            s=self.status(False);return s['connector']['state']=='RUNNING' and len(s['tasks'])==1 and s['tasks'][0]['state']=='RUNNING'
        wait(test,'Connector RUNNING');self.status()
    def position(self,name):
        pg=json.loads(self.sql('positions.sql'))
        offsets=self.req('GET','/connectors/'+NAME+'/offsets',base=CONNECT)
        group=command(kafka('kafka-consumer-groups','--describe','--group',GROUP),required=False)
        self.save(name,{'postgres':pg,'connect_source_offsets':offsets,'java_consumer_group':group.stdout,'group_stderr':group.stderr})
        return pg
    def inspect(self,name,minimum=None):
        values,r=java('inspect');self.save(name,values)
        if minimum is not None:check(values[-1]['processed']>=minimum,values[-1])
        return [v for v in values if v['kind']=='event']
    def drain(self,name):
        values,r=java('drain');self.save(name,values)
        (self.out/(name+'.stderr.txt')).write_text(r.stderr)
        return values
    def wait_events(self,count):
        # Kafka console tools are useful for independent evidence; inspect never joins/commits the apply group.
        wait(lambda: len(java('inspect')[0])-1>=count,'Expected Kafka events')
    def all(self):
        body=json.loads((ROOT/'search/f37/all.json').read_text())
        return self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',body)
    def docs(self,want,name):
        r=self.all();check(not r['timed_out'] and r['_shards']['failed']==0,r)
        got={h['_id']:h['_source'] for h in r['hits']['hits']}
        check(got==want and r['hits']['total']['value']==len(want),{'actual':got,'expected':want})
        self.save(name,r)
    def expected(self):
        text=self.sql(text="""SELECT json_build_object('id',attraction_id,'document',json_build_object(
          'attraction_id',attraction_id,'name',name,'city_code',city_code,'ticket_price_fen',ticket_price_fen,
          'currency','CNY','status',status,'location',json_build_object('lat',latitude,'lon',longitude)))
          FROM f37.attraction WHERE status='open' ORDER BY attraction_id;""")
        return {r['id']:r['document'] for r in [json.loads(x) for x in text.splitlines()]}
    def refresh(self):
        r=self.req('POST','/'+INDEX+'/_refresh');check(r['_shards']['failed']==0,r)
    def observe(self,name,want):
        body=json.loads((ROOT/'search/f37/search.json').read_text())
        result=self.req('POST','/api/attractions/search',body,base=APP)
        check([(x['id'],x['ticketPriceFen']) for x in result['items']]==want,result)
        replay=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',result['esRequest'])
        check([(x['_id'],x['_source']['ticket_price_fen']) for x in replay['hits']['hits']]==want,replay)
        check(result['total']==len(want) and result['totalRelation']=='eq',result)
        self.save(name+'-java-search',{'request':body,'response':result,'rest_replay':replay})
        if ARGS.observer:
            spec=importlib.util.spec_from_file_location('f37_observer',ARGS.observer)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.capture(name,want,APP,ES,READ,self.out)
    def app_start(self):
        with socket.socket() as s:check(s.connect_ex(('127.0.0.1',18087))!=0,'18087 occupied')
        env=os.environ.copy();env.update(ES_URL=ES,ES_INDEX=READ,ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18087')
        self.log=(self.out/'application.log').open('w')
        self.proc=subprocess.Popen(['java','-Xms64m','-Xmx192m','-jar','backend/target/travel-search-0.7.0.jar'],cwd=ROOT,env=env,stdout=self.log,stderr=subprocess.STDOUT)
        def ready():
            check(self.proc.poll() is None,'Java exited; inspect application.log')
            with urllib.request.urlopen(APP+'/',timeout=1) as r:return r.status==200
        wait(ready,'Java observation service')
    def stop(self):
        if self.proc and self.proc.poll() is None:self.proc.terminate();self.proc.wait(timeout=20)
        if self.log:self.log.close()
    def replica_identity_probe(self):
        r=self.sql('identity-failure.sql',required=False)
        check(r.returncode!=0 and 'replica identity' in r.stderr,r.stderr)
        restored=self.sql(text="SELECT relreplident FROM pg_class WHERE oid='f37.attraction'::regclass; SELECT count(*) FROM f37.attraction WHERE attraction_id='p01';")
        check(restored.strip()=='d\n1',restored)
        self.save('replica-identity',{'at':now(),'expected_delete_refused':True,'stderr':r.stderr,'default_identity_and_p01_restored':True})
    def prepare(self):
        self.case='c01-snapshot'
        check(not self.req('GET','/connectors',base=CONNECT),'Connector already exists; clean up first')
        exists=self.sql(text="SELECT to_regnamespace('f37') IS NOT NULL;");check(exists.strip()=='f','Schema exists')
        credential=(INFRA/'.local/cdc.properties').read_text().strip().split('=',1)[1]
        # Send password through stdin; do not log SQL containing its value or put it in argv.
        sql("\\set cdc_password '"+credential+"'\n"+source('setup.sql'))
        self.save('source-setup',{'file':'data/f37/setup.sql','secret_via_stdin':True,'passed':True})
        grants=self.sql(text="SELECT rolname, rolsuper, rolreplication FROM pg_roles WHERE rolname='f37_cdc'; SET ROLE f37_cdc; SELECT count(*) FROM f37.attraction;")
        check('f37_cdc|f|t' in grants and grants.rstrip().endswith('2'),grants)
        denied=self.sql(text="\\set VERBOSITY verbose\nSET ROLE f37_cdc; UPDATE f37.attraction SET ticket_price_fen=1 WHERE attraction_id='p01';",required=False)
        check(denied.returncode!=0 and '42501' in denied.stderr,denied.stderr)
        identity=self.sql(text="SELECT c.relreplident, i.indisprimary FROM pg_class c JOIN pg_index i ON i.indrelid=c.oid WHERE c.oid='f37.attraction'::regclass;")
        check(identity.strip()=='d|t',identity)
        self.replica_identity_probe()
        command(kafka('kafka-topics','--create','--topic',TOPIC,'--partitions','1','--replication-factor','1','--config','cleanup.policy=delete','--config','retention.ms=604800000'))
        self.req('PUT','/'+INDEX,json.loads((ROOT/'search/f37/create.json').read_text()))
        self.req('POST','/_aliases',json.loads((ROOT/'search/f37/aliases.json').read_text()))
        self.req('POST','/connectors',json.loads((ROOT/'cdc/f37/connector.json').read_text()),expected=201,base=CONNECT)
        self.running();self.wait_events(2)
    def run(self):
        self.identity();self.guard();self.prepare();self.app_start()
        events=self.inspect('c01-events',2)
        check(len(events)==2 and all(e['value']['op']=='r' for e in events),events)
        check({e['key']['attraction_id'] for e in events}=={'p01','p02'},events)
        self.docs({},'c01-before-java')
        applied=self.drain('c01-apply');check(applied[-1]['processed']==2,applied)
        get=self.req('GET','/'+READ+'/_doc/p01');check(get['_source']['ticket_price_fen']==6000,get)
        self.docs({},'c01-before-refresh');self.refresh()
        initial=self.expected();self.docs(initial,'c01-complete');self.observe('initial',[('p01',6000),('p02',0)])
        self.position('c01-positions')

        self.case='c02-changes'
        self.sql('changes.sql');self.wait_events(5)
        events=self.inspect('c02-change-events',5)
        check([(e['value']['op'],e['key']['attraction_id']) for e in events[2:]]==[('c','p03'),('u','p01'),('u','p02')],events)
        self.docs(initial,'c02-kafka-not-es');self.drain('c02-change-apply')
        get=self.req('GET','/'+READ+'/_doc/p01');check(get['_source']['ticket_price_fen']==6500,get)
        self.req('GET','/'+READ+'/_doc/p02',expected=404)
        self.docs(initial,'c02-not-refreshed');self.refresh();changed=self.expected()
        self.docs(changed,'c02-changed');self.observe('changes',[('p01',6500),('p03',3000)])
        self.sql('delete.sql');self.wait_events(7)
        events=self.inspect('c02-delete-events',7)
        deleted,marker=events[-2:]
        check(deleted['value']['op']=='d' and deleted['value']['after'] is None,deleted)
        check(deleted['value']['before']['attraction_id']=='p03' and marker['value'] is None and marker['key']==deleted['key'],events)
        applied=self.drain('c02-delete-apply');check([e['result'] for e in applied[:-1]]==['delete:deleted','tombstone'],applied)
        self.refresh();before_stop=self.expected();self.docs(before_stop,'c02-deleted');self.observe('deleted',[('p01',6500)])
        self.position('c02-positions')

        self.case='c03-restart'
        before_events=self.inspect('c03-before-stop-events');before_count=len(before_events)
        compose('stop','connect')
        wait(lambda:json.loads(sql(source('positions.sql')).stdout)['slot']['active'] is False,'Slot inactive')
        before=json.loads(self.sql('positions.sql'));self.save('c03-slot-before-offline',before)
        self.sql('offline.sql');after=json.loads(self.sql('positions.sql'));self.save('c03-slot-offline',after)
        check(after['slot']['active'] is False and after['slot']['restart_lsn']==before['slot']['restart_lsn'],after)
        check(after['slot']['retained_distance_bytes']>before['slot']['retained_distance_bytes'],after)
        check(len(self.inspect('c03-offline-events'))==before_count,'Kafka changed with Connect off')
        self.docs(before_stop,'c03-offline-es');self.observe('offline',[('p01',6500)])
        compose('start','connect');wait(lambda:self.req('GET','/',base=CONNECT,record=False),'Connect HTTP')
        self.running();self.wait_events(before_count+4)
        events=self.inspect('c03-resumed-events');new=events[before_count:]
        check([(e['value']['op'] if e['value'] else 'tombstone',e['key']['attraction_id']) for e in new]==[('u','p01'),('c','p04'),('d','p02'),('tombstone','p02')],new)
        self.docs(before_stop,'c03-kafka-ahead-of-es')
        self.drain('c03-resume-apply');self.refresh();final=self.expected();self.docs(final,'c03-final')
        self.observe('resumed',[('p01',7000),('p04',1800)])
        self.req('GET','/'+READ+'/_doc/p02',expected=404);self.req('GET','/'+READ+'/_doc/p03',expected=404)
        again=self.drain('c03-java-restart-noop');check(again[-1]['processed']==0,again)
        pos=self.position('c03-positions')
        check(pos['slot']['slot_name']=='f37_slot' and pos['slot']['active'] is True,pos)
        self.save('summary',{'at':now(),'passed':True,'cases':3,'http_by_case':dict(collections.Counter(e['case'] for e in self.http)),
            'http_by_base':dict(collections.Counter(e['base'] for e in self.http)),'total_recorded_http':len(self.http),
            'kafka_event_count':len(events),'consumer_final':again[-1],'final_documents':final,
            'wal_test':'Inactive slot retained restart_lsn; observed distance grew; no disk fill/slot invalidation test',
            'limits':['One PG primary, one Kafka partition, one consumer and immutable business keys',
                      'Graceful Connect stop/start with original Kafka offsets/PG slot; no crash/exactly-once proof',
                      'No multi-table projection, arbitrary out-of-order delivery, retry/DLQ or online rebuild']})
    def cleanup(self):
        self.identity();self.guard();self.case='cleanup'
        names=self.req('GET','/connectors',base=CONNECT)
        if NAME in names:
            self.req('PUT','/connectors/'+NAME+'/stop',base=CONNECT,expected=204)
            wait(lambda:self.status(False)['connector']['state']=='STOPPED','Connector STOPPED')
            self.req('DELETE','/connectors/'+NAME+'/offsets',base=CONNECT)
            self.req('DELETE','/connectors/'+NAME,base=CONNECT,expected=204)
        self.sql(text="SELECT pg_drop_replication_slot('f37_slot') WHERE EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name='f37_slot' AND NOT active);")
        self.sql(text='DROP PUBLICATION IF EXISTS f37_publication; DROP SCHEMA IF EXISTS f37 CASCADE;')
        if self.sql(text="SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='f37_cdc');").strip()=='t':
            self.sql(text='REVOKE CONNECT ON DATABASE travel_f37 FROM f37_cdc; DROP ROLE f37_cdc;')
        topics=command(kafka('kafka-topics','--list')).stdout.splitlines()
        if TOPIC in topics:command(kafka('kafka-topics','--delete','--topic',TOPIC))
        wait(lambda:TOPIC not in command(kafka('kafka-topics','--list')).stdout.splitlines(),'Topic deletion')
        group=command(kafka('kafka-consumer-groups','--delete','--group',GROUP),required=False)
        check(group.returncode==0 or 'GroupIdNotFoundException' in group.stdout+group.stderr,group.stdout+group.stderr)
        self.req('DELETE','/'+INDEX,expected=[200,404])
        remaining=self.sql(text="SELECT to_regnamespace('f37') IS NULL, NOT EXISTS(SELECT 1 FROM pg_replication_slots WHERE slot_name='f37_slot');")
        check(remaining.strip()=='t|t',remaining)
        self.save('summary',{'at':now(),'passed':True,'deleted':[NAME+' source offsets',NAME,TOPIC,GROUP,INDEX,'f37_slot','f37_publication','f37 schema','f37_cdc role'],'preserved':['all three data volumes','Connect internal topics','local secret files','other course resources']})

def main():
    lab=Lab(ARGS.out)
    try:
        if ARGS.action=='init':
            local=INFRA/'.local';check(not local.exists(),'F37 .local exists; do not overwrite')
            volumes=command(['docker','volume','ls','--format','{{.Name}}']).stdout.splitlines()
            check(not any(x.startswith('es-framework-f37_') for x in volumes),'Existing F37 volumes; do not mix new passwords')
            local.mkdir(mode=0o700)
            for name,value in [('pg-password.txt',secrets.token_urlsafe(32)+'\n'),('cdc.properties','password='+secrets.token_urlsafe(32)+'\n')]:
                p=local/name;p.write_text(value);p.chmod(0o600)
            lab.save('summary',{'at':now(),'passed':True,'secrets_written':2,'credentials_in_output':False})
        elif ARGS.action=='start':
            compose('up','-d')
            wait(lambda:lab.req('GET','/',record=False),'ES HTTP')
            wait(lambda:lab.req('GET','/',base=CONNECT,record=False),'Connect HTTP')
            lab.identity();lab.save('summary',{'at':now(),'passed':True})
        elif ARGS.action=='prepare':lab.identity();lab.guard();lab.prepare();lab.save('summary',{'at':now(),'passed':True})
        elif ARGS.action=='run':lab.run()
        elif ARGS.action=='cleanup':lab.cleanup()
        elif ARGS.action=='down':compose('down');lab.save('summary',{'at':now(),'passed':True,'volumes_preserved':True})
        print('F37',ARGS.action,'passed:',lab.out)
    finally:lab.stop()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init','start','prepare','run','cleanup','down'])
    p.add_argument('--out',required=True);p.add_argument('--observer');ARGS=p.parse_args();main()
