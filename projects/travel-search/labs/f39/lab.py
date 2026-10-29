#!/usr/bin/env python3
"""F39 isolated PostgreSQL -> Debezium -> Kafka -> Java -> ES experiment."""
import argparse, collections, datetime, importlib.util, json, os, pathlib
import secrets, socket, subprocess, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
INFRA = ROOT / 'infra/f39'
ES = 'http://127.0.0.1:20339'
CONNECT = 'http://127.0.0.1:18339'
APP = 'http://127.0.0.1:18089'
INDEX = 'tut-f39-attractions-v001'
READ = 'tut-f39-attractions-read'
TOPICS = ['travel_f39.f39.'+t for t in ['city','attraction','attraction_tag']]
GROUP = 'f39-es-v1'
NAME = 'f39-pg'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok, detail):
    if not ok: raise AssertionError(detail)
def command(args, data=None, required=True):
    r = subprocess.run(args, input=data, text=True, capture_output=True, cwd=ROOT, timeout=120)
    if required: check(r.returncode == 0, {'command':args, 'stderr':r.stderr[-3000:], 'stdout':r.stdout[-2000:]})
    return r
def compose_args(*args): return ['docker','compose','-f',str(INFRA/'compose.yaml'),*args]
def compose(*args): return command(compose_args(*args)).stdout
def psql_args(): return compose_args('exec','-T','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-U','travel','-d','travel_f39')
def sql(text, required=True): return command(psql_args(),text,required)
def source(name): return (ROOT/'data/f39'/name).read_text()
def kafka(tool,*args):
    return compose_args('exec','-T','kafka','/opt/kafka/bin/'+tool+'.sh','--bootstrap-server','kafka:9092',*args)
def java(mode):
    r=command(['bash','labs/f39/java.sh',mode]);values=[]
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
        root=self.req('GET','/');check(root['cluster_name']=='travel-f39-lab' and root['version']['number']=='9.4.0',root)
        pg=self.sql(text='SELECT current_database(), current_user, version();')
        check(pg.startswith('travel_f39|travel|PostgreSQL 17.5 '),pg)
        worker=self.req('GET','/',base=CONNECT)
        plugins=self.req('GET','/connector-plugins',base=CONNECT)
        check(any(p['class']=='io.debezium.connector.postgresql.PostgresConnector' and p['version']=='3.3.1.Final' for p in plugins),plugins)
        self.save('identity',{'es':root,'pg':pg,'connect':worker,'plugins':plugins})
    def guard(self):
        indices=self.req('GET','/_cat/indices?format=json&expand_wildcards=all')
        check(all(x['index']==INDEX or x['index'].startswith('.') for x in indices),'Foreign ES index')
        topics=command(kafka('kafka-topics','--list')).stdout.splitlines()
        check(set(topics)<=set(TOPICS+['f39-connect-configs','f39-connect-offsets','f39-connect-status','__consumer_offsets']),'Foreign Kafka topic')
        names=self.req('GET','/connectors',base=CONNECT);check(set(names)<=set([NAME]),names)
    def status(self,record=True): return self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=record)
    def running(self):
        def test():
            s=self.status(False);return s['connector']['state']=='RUNNING' and len(s['tasks'])==1 and s['tasks'][0]['state']=='RUNNING'
        wait(test,'Connector RUNNING');self.status()
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
        body=json.loads((ROOT/'search/f39/all.json').read_text())
        return self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',body)
    def docs(self,want,name):
        r=self.all();check(not r['timed_out'] and r['_shards']['failed']==0,r)
        got={h['_id']:h['_source'] for h in r['hits']['hits']}
        check(got==want and r['hits']['total']['value']==len(want),{'actual':got,'expected':want})
        self.save(name,r)
    def expected(self):
        text=self.sql(text="SELECT json_build_object('id',p.id,'document',p.document) FROM ("+source('projection.sql').strip().rstrip(';')+") p;")
        return {r['id']:r['document'] for r in [json.loads(x) for x in text.splitlines()]}
    def refresh(self):
        r=self.req('POST','/'+INDEX+'/_refresh');check(r['_shards']['failed']==0,r)
    def observe(self,name,want):
        body=json.loads((ROOT/'search/f39/search.json').read_text())
        result=self.req('POST','/api/attractions/search',body,base=APP)
        check([(x['id'],x['ticketPriceFen']) for x in result['items']]==want,result)
        replay=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',result['esRequest'])
        check([(x['_id'],x['_source']['ticket_price_fen']) for x in replay['hits']['hits']]==want,replay)
        check(result['total']==len(want) and result['totalRelation']=='eq',result)
        self.save(name+'-java-search',{'request':body,'response':result,'rest_replay':replay})
        if ARGS.observer:
            spec=importlib.util.spec_from_file_location('f39_observer',ARGS.observer)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.capture(name,want,APP,ES,READ,self.out)
    def app_start(self):
        with socket.socket() as s:check(s.connect_ex(('127.0.0.1',18089))!=0,'18089 occupied')
        env=os.environ.copy();env.update(ES_URL=ES,ES_INDEX=READ,ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18089')
        self.log=(self.out/'application.log').open('w')
        self.proc=subprocess.Popen(['java','-Xms64m','-Xmx192m','-jar','backend/target/travel-search-0.7.0.jar'],cwd=ROOT,env=env,stdout=self.log,stderr=subprocess.STDOUT)
        def ready():
            check(self.proc.poll() is None,'Java exited; inspect application.log')
            with urllib.request.urlopen(APP+'/',timeout=1) as r:return r.status==200
        wait(ready,'Java observation service')
    def stop(self):
        if self.proc and self.proc.poll() is None:self.proc.terminate();self.proc.wait(timeout=20)
        if self.log:self.log.close()
    def prepare(self):
        self.case='c01-snapshot'
        check(not self.req('GET','/connectors',base=CONNECT),'Connector exists; cleanup first')
        check(self.sql(text="SELECT to_regnamespace('f39') IS NOT NULL;").strip()=='f','Schema exists')
        cdc=(INFRA/'.local/cdc.properties').read_text().strip().split('=',1)[1]
        projector=dict(line.split('=',1) for line in (INFRA/'.local/projector.properties').read_text().splitlines())['password']
        sql("\\set cdc_password '"+cdc+"'\n\\set projector_password '"+projector+"'\n"+source('setup.sql'))
        self.save('source-setup',{'file':'data/f39/setup.sql','two_secrets_via_stdin':True,'passed':True})
        identity=self.sql(text="SELECT relname,relreplident FROM pg_class WHERE relnamespace='f39'::regnamespace AND relkind='r' ORDER BY relname;")
        check(identity.strip()=='attraction|f\nattraction_tag|f\ncity|f',identity)
        permissions={}
        for role in ['f39_cdc','f39_projector']:
            selected=self.sql(text='SET ROLE '+role+'; SELECT count(*) FROM f39.attraction;')
            denied=self.sql(text="\\set VERBOSITY verbose\nSET ROLE "+role+"; UPDATE f39.attraction SET ticket_price_fen=1 WHERE attraction_id='p01';",required=False)
            check(selected.strip()=='3' and denied.returncode!=0 and '42501' in denied.stderr,role)
            permissions[role]={'select':selected,'write_denied':denied.stderr}
        self.save('permissions',{'identities':identity,'roles':permissions})
        for topic in TOPICS:
            command(kafka('kafka-topics','--create','--topic',topic,'--partitions','1','--replication-factor','1','--config','cleanup.policy=delete','--config','retention.ms=604800000'))
        self.req('PUT','/'+INDEX,json.loads((ROOT/'search/f39/create.json').read_text()))
        self.req('POST','/_aliases',json.loads((ROOT/'search/f39/aliases.json').read_text()))
        self.req('POST','/connectors',json.loads((ROOT/'cdc/f39/connector.json').read_text()),expected=201,base=CONNECT)
        self.running();self.wait_events(8)
    def night(self,ids,name):
        result=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',json.loads((ROOT/'search/f39/night.json').read_text()))
        check([h['_id'] for h in result['hits']['hits']]==ids and result['_shards']['failed']==0,result)
        self.save(name,result)
    def stage(self,name,want):
        applied=self.drain(name+'-apply');self.refresh()
        expected=self.expected();self.docs(expected,name+'-complete');self.observe(name,want)
        return applied,expected
    def run(self):
        self.identity();self.guard();self.prepare();self.app_start()
        events=self.inspect('c01-events',8)
        check(len(events)==8 and all(e['value']['op']=='r' for e in events),events)
        check(collections.Counter(e['topic'].split('.')[-1] for e in events)=={'city':2,'attraction':3,'attraction_tag':3},events)
        self.docs({},'c01-before-java');applied=self.drain('c01-apply')
        check(applied[-1]['processed']==8,applied[-1])
        self.req('GET','/'+READ+'/_doc/p01');self.docs({},'c01-before-refresh');self.refresh()
        initial=self.expected();self.docs(initial,'c01-complete');self.observe('initial',[('p01',6000),('p02',0)])
        self.night(['p01'],'c01-night')

        self.case='c02-shared-and-transfer';self.sql('shared.sql');self.wait_events(11)
        self.inspect('c02-shared-events',11);self.docs(initial,'c02-db-not-es')
        shared,current=self.stage('shared',[('p01',6500),('p02',0)])
        city=[e for e in shared[:-1] if e['topic'].endswith('.city')]
        check(len(city)==1 and city[0]['projection']['affected_ids']==['p01','p02'],city)
        check(current['p01']['city_name']==current['p02']['city_name']=='杭州城区' and current['p03']['city_name']=='苏州',current)
        self.sql('transfer.sql');self.wait_events(12)
        events=self.inspect('c02-transfer-events',12)
        event=[e for e in events if e['topic'].endswith('.attraction_tag') and e['value'] and e['value']['op']=='u']
        check(len(event)==1 and event[0]['value']['before']['attraction_id']=='p01' and event[0]['value']['after']['attraction_id']=='p02',event)
        self.req('POST','/'+READ+'/_update/p02',json.loads((ROOT/'search/f39/naive-update.json').read_text()))
        self.refresh();self.night(['p01','p02'],'c02-naive-residual')
        fixed,current=self.stage('transferred',[('p01',6500),('p02',0)])
        check(fixed[-1]['processed']==1 and fixed[0]['projection']['affected_ids']==['p01','p02'],fixed)
        check(current['p01']['tags']==['亲水'] and current['p02']['tags']==['亲水','夜景'],current)
        self.night(['p02'],'c02-fixed-night')

        self.case='c03-delete-and-status';self.sql('delete-tag.sql');self.wait_events(14)
        events=self.inspect('c03-tag-delete-events',14)
        deleted=[e for e in events if e['topic'].endswith('.attraction_tag') and e['key']['tag_id']=='t01' and e['value'] and e['value']['op']=='d']
        check(len(deleted)==1 and deleted[0]['value']['before']['attraction_id']=='p01',deleted)
        tag,current=self.stage('empty-tags',[('p01',6500),('p02',0)])
        check(current['p01']['tags']==[] and tag[-1]['processed']==2,tag)
        self.sql('close.sql');self.wait_events(15);closed,current=self.stage('closed',[('p01',6500)])
        self.req('GET','/'+READ+'/_doc/p02',expected=404)
        self.sql('delete-root.sql');self.wait_events(19);self.inspect('c03-cascade-events',19)
        gone,current=self.stage('root-deleted',[('p01',6500)])
        check(gone[-1]['processed']==4 and all(e['projection']['affected_ids'] in [[],['p03']] for e in gone[:-1]),gone)
        results=[i['result'] for e in gone[:-1] for i in e['projection']['items']]
        check(sorted(results)==['deleted','not_found'],results)
        self.req('GET','/'+READ+'/_doc/p03',expected=404)
        self.sql('reopen.sql');self.wait_events(20);reopened,final=self.stage('reopened',[('p01',6500),('p02',0)])
        check(final['p02']['tags']==['亲水','夜景'] and final['p01']['tags']==[],final)
        self.night(['p02'],'c03-final-night');events=self.inspect('c03-final-events',20)
        again=self.drain('c03-restart-noop');check(again[-1]['processed']==0,again)
        positions=again[-1]['positions']
        check(all(p['committed_next']==p['observed_end'] for p in positions.values()),positions)
        applied_files=['c01-apply','shared-apply','transferred-apply','empty-tags-apply','closed-apply','root-deleted-apply','reopened-apply']
        records=[r for name in applied_files for r in json.loads((self.out/(name+'.json')).read_text()) if r['kind']=='applied']
        self.save('summary',{'at':now(),'passed':True,'cases':3,'http_by_case':dict(collections.Counter(e['case'] for e in self.http)),
          'http_by_base':dict(collections.Counter(e['base'] for e in self.http)),'total_recorded_http':len(self.http),
          'kafka_events':len(events),'consumer_bulk_requests':sum(bool(r['projection']['affected_ids']) for r in records),
          'consumer_bulk_items':sum(len(r['projection']['operations']) for r in records),'final_positions':positions,
          'final_documents':final,'limits':['One PostgreSQL primary, 3 topics with 1 partition each, 1 consumer, immutable keys',
          'Paused writes per finite stage; current-state reads, no event-time or cross-topic transaction snapshot',
          'No arbitrary crash/out-of-order/late replay, retries/DLQ/HA/large fanout or performance validation']})
    def cleanup(self):
        self.identity();self.guard();self.case='cleanup'
        members=command(kafka('kafka-consumer-groups','--describe','--group',GROUP,'--members'),required=False)
        check(not any(line.startswith(GROUP+' ') for line in members.stdout.splitlines()),'Stop the F39 consumer before cleanup')
        names=self.req('GET','/connectors',base=CONNECT)
        if NAME in names:
            self.req('PUT','/connectors/'+NAME+'/stop',base=CONNECT,expected=204)
            wait(lambda:self.status(False)['connector']['state']=='STOPPED','Connector STOPPED')
            self.req('DELETE','/connectors/'+NAME+'/offsets',base=CONNECT)
            self.req('DELETE','/connectors/'+NAME,base=CONNECT,expected=204)
        self.sql(text="SELECT pg_drop_replication_slot('f39_slot') WHERE EXISTS (SELECT 1 FROM pg_replication_slots WHERE slot_name='f39_slot' AND NOT active);")
        self.sql(text='DROP PUBLICATION IF EXISTS f39_publication; DROP SCHEMA IF EXISTS f39 CASCADE;')
        if self.sql(text="SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='f39_projector');").strip()=='t':
            self.sql(text='REVOKE CONNECT ON DATABASE travel_f39 FROM f39_projector; DROP ROLE f39_projector;')
        if self.sql(text="SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='f39_cdc');").strip()=='t':
            self.sql(text='REVOKE CONNECT ON DATABASE travel_f39 FROM f39_cdc; DROP ROLE f39_cdc;')
        topics=command(kafka('kafka-topics','--list')).stdout.splitlines()
        for topic in TOPICS:
            if topic in topics:command(kafka('kafka-topics','--delete','--topic',topic))
        wait(lambda:not set(TOPICS).intersection(command(kafka('kafka-topics','--list')).stdout.splitlines()),'Topic deletion')
        group=command(kafka('kafka-consumer-groups','--delete','--group',GROUP),required=False)
        check(group.returncode==0 or 'GroupIdNotFoundException' in group.stdout+group.stderr,group.stdout+group.stderr)
        self.req('DELETE','/'+INDEX,expected=[200,404])
        remaining=self.sql(text="SELECT to_regnamespace('f39') IS NULL, NOT EXISTS(SELECT 1 FROM pg_replication_slots WHERE slot_name='f39_slot');")
        check(remaining.strip()=='t|t',remaining)
        self.save('summary',{'at':now(),'passed':True,'deleted':[NAME+' source offsets',NAME,*TOPICS,GROUP,INDEX,'f39_slot','f39_publication','f39 schema','f39_cdc/f39_projector roles'],'preserved':['all three data volumes','Connect internal topics','local secret files','other course resources']})

def main():
    lab=Lab(ARGS.out)
    try:
        if ARGS.action=='init':
            local=INFRA/'.local';check(not local.exists(),'F39 .local exists; do not overwrite')
            volumes=command(['docker','volume','ls','--format','{{.Name}}']).stdout.splitlines()
            check(not any(x.startswith('es-framework-f39_') for x in volumes),'Existing F39 volumes; do not mix new passwords')
            local.mkdir(mode=0o700)
            for name,value in [('pg-password.txt',secrets.token_urlsafe(32)+'\n'),('cdc.properties','password='+secrets.token_urlsafe(32)+'\n'),('projector.properties','url=jdbc:postgresql://127.0.0.1:15439/travel_f39\nuser=f39_projector\npassword='+secrets.token_urlsafe(32)+'\nsslmode=disable\nconnectTimeout=10\nsocketTimeout=20\n')]:
                p=local/name;p.write_text(value);p.chmod(0o600)
            lab.save('summary',{'at':now(),'passed':True,'secrets_written':3,'credentials_in_output':False})
        elif ARGS.action=='start':
            compose('up','-d')
            wait(lambda:lab.req('GET','/',record=False),'ES HTTP')
            wait(lambda:lab.req('GET','/',base=CONNECT,record=False),'Connect HTTP')
            lab.identity();lab.save('summary',{'at':now(),'passed':True})
        elif ARGS.action=='prepare':lab.identity();lab.guard();lab.prepare();lab.save('summary',{'at':now(),'passed':True})
        elif ARGS.action=='run':lab.run()
        elif ARGS.action=='inspect':
            lab.identity();lab.guard();lab.running();lab.inspect('events')
            result=lab.all();lab.save('search',result);print(json.dumps(result,ensure_ascii=False,indent=2))
        elif ARGS.action=='refresh':lab.identity();lab.guard();lab.refresh()
        elif ARGS.action=='naive':
            lab.identity();lab.guard();lab.req('POST','/'+READ+'/_update/p02',json.loads((ROOT/'search/f39/naive-update.json').read_text()))
        elif ARGS.action in ['shared','transfer','delete-tag','close','delete-root','reopen']:
            lab.identity();lab.guard();lab.sql(ARGS.action+'.sql')
        elif ARGS.action=='cleanup':lab.cleanup()
        elif ARGS.action=='down':compose('down');lab.save('summary',{'at':now(),'passed':True,'volumes_preserved':True})
        print('F39',ARGS.action,'passed:',lab.out)
    finally:lab.stop()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init','start','prepare','run','cleanup','down','inspect','refresh','naive','shared','transfer','delete-tag','close','delete-root','reopen'])
    p.add_argument('--out',required=True);p.add_argument('--observer');ARGS=p.parse_args();main()
