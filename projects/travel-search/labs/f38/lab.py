#!/usr/bin/env python3
"""F38 isolated MySQL -> Debezium -> Kafka -> Java -> ES experiment."""
import argparse, collections, datetime, importlib.util, json, os, pathlib
import re, secrets, socket, subprocess, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
INFRA = ROOT / 'infra/f38'
ES = 'http://127.0.0.1:20238'
CONNECT = 'http://127.0.0.1:18238'
APP = 'http://127.0.0.1:18088'
INDEX = 'tut-f38-attractions-v001'
READ = 'tut-f38-attractions-read'
TOPIC = 'travel_f38.travel_f38.attraction'
GROUP = 'f38-es-v1'
NAME = 'f38-mysql'
HISTORY = 'f38-schema-history'
EMPTY_HISTORY = 'f38-schema-history-empty'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok, detail):
    if not ok: raise AssertionError(detail)
def command(args, data=None, required=True):
    r = subprocess.run(args, input=data, text=True, capture_output=True, cwd=ROOT, timeout=120)
    if required: check(r.returncode == 0, {'command':args, 'stderr':r.stderr[-3000:], 'stdout':r.stdout[-2000:]})
    return r
def compose_args(*args): return ['docker','compose','--profile','mysql','-f',str(INFRA/'compose.yaml'),*args]
def compose(*args): return command(compose_args(*args)).stdout
def mysql_args(cdc=False): return compose_args('exec','-T','mysql','mysql','--defaults-extra-file=/run/secrets/'+('cdc-cnf' if cdc else 'admin-cnf'),'--batch','--raw','--skip-column-names','--default-character-set=utf8mb4')
def sql(text, required=True, cdc=False): return command(mysql_args(cdc),text,required)
def source(name): return (ROOT/'data/f38'/name).read_text()
def kafka(tool,*args):
    return compose_args('exec','-T','kafka','/opt/kafka/bin/'+tool+'.sh','--bootstrap-server','kafka:9092',*args)
def java(mode):
    r=command(['bash','labs/f38/java.sh',mode]);values=[]
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
        root=self.req('GET','/');check(root['cluster_name']=='travel-f38-lab' and root['version']['number']=='9.4.0',root)
        mysql=self.sql('positions.sql')
        identity=json.loads(mysql.splitlines()[0]);check(identity['version']=='8.4.5' and identity['server_id']==1838 and identity['log_bin']==1 and identity['binlog_format']=='ROW' and identity['binlog_row_image']=='FULL' and identity['binlog_row_value_options']=='' and identity['gtid_mode']=='OFF' and identity['binlog_expire_logs_seconds']==604800,mysql)
        worker=self.req('GET','/',base=CONNECT)
        plugins=self.req('GET','/connector-plugins',base=CONNECT)
        check(any(p['class']=='io.debezium.connector.mysql.MySqlConnector' and p['version']=='3.3.1.Final' for p in plugins),plugins)
        self.save('identity',{'es':root,'mysql':mysql,'connect':worker,'plugins':plugins})
    def guard(self):
        indices=self.req('GET','/_cat/indices?format=json&expand_wildcards=all')
        check(all(x['index']==INDEX or x['index'].startswith('.') for x in indices),'Foreign ES index')
        topics=command(kafka('kafka-topics','--list')).stdout.splitlines()
        check(set(topics)<=set([TOPIC,HISTORY,EMPTY_HISTORY,'f38-connect-configs','f38-connect-offsets','f38-connect-status','__consumer_offsets']),'Foreign Kafka topic')
        names=self.req('GET','/connectors',base=CONNECT);check(set(names)<=set([NAME]),names)
    def status(self,record=True): return self.req('GET','/connectors/'+NAME+'/status',base=CONNECT,record=record)
    def running(self):
        def test():
            s=self.status(False);return s['connector']['state']=='RUNNING' and len(s['tasks'])==1 and s['tasks'][0]['state']=='RUNNING'
        wait(test,'Connector RUNNING');self.status()
    def position(self,name):
        raw=self.sql('positions.sql');lines=raw.splitlines()
        mysql={'variables':json.loads(lines[0]),'binary_log_status':lines[1].split('\t'),
               'binary_logs':[x.split('\t') for x in lines[2:]]}
        offsets=self.req('GET','/connectors/'+NAME+'/offsets',base=CONNECT)
        group=command(kafka('kafka-consumer-groups','--describe','--group',GROUP),required=False)
        self.save(name,{'mysql':mysql,'connect_source_offsets':offsets,'java_consumer_group':group.stdout,'group_stderr':group.stderr})
        return mysql
    def history(self,name):
        r=command(kafka('kafka-console-consumer','--topic',HISTORY,'--from-beginning','--timeout-ms','2000'),required=False)
        # The finite CLI observation ends with a timeout diagnostic; verify every reported record.
        # Kafka's value may itself contain pretty-printed, multiline JSON.
        values=[];raw=r.stdout.strip();decoder=json.JSONDecoder()
        while raw:
            value,end=decoder.raw_decode(raw);values.append(value);raw=raw[end:].lstrip()
        check(values,'Schema history must contain records')
        total=re.search(r'Processed a total of (\d+) messages',r.stderr)
        check(total and int(total[1])==len(values) and 'TimeoutException' in r.stderr,r.stderr)
        config=command(kafka('kafka-configs','--entity-type','topics','--entity-name',HISTORY,'--describe')).stdout
        describe=command(kafka('kafka-topics','--describe','--topic',HISTORY)).stdout
        check('PartitionCount: 1' in describe and 'retention.ms=-1' in config and 'retention.bytes=-1' in config and 'cleanup.policy=delete' in config,describe+config)
        self.save(name,{'records':values,'topic_configuration':config,'topic_description':describe,'cli_exit':r.returncode})
        return values
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
        body=json.loads((ROOT/'search/f38/all.json').read_text())
        return self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',body)
    def docs(self,want,name):
        r=self.all();check(not r['timed_out'] and r['_shards']['failed']==0,r)
        got={h['_id']:h['_source'] for h in r['hits']['hits']}
        check(got==want and r['hits']['total']['value']==len(want),{'actual':got,'expected':want})
        self.save(name,r)
    def expected(self):
        text=self.sql(text="""SELECT JSON_OBJECT('id',attraction_id,'document',JSON_OBJECT(
          'attraction_id',attraction_id,'name',name,'city_code',city_code,'ticket_price_fen',ticket_price_fen,
          'currency','CNY','status',status,'location',JSON_OBJECT('lat',latitude,'lon',longitude)))
          FROM travel_f38.attraction WHERE status='open' ORDER BY attraction_id;""")
        return {r['id']:r['document'] for r in [json.loads(x) for x in text.splitlines()]}
    def refresh(self):
        r=self.req('POST','/'+INDEX+'/_refresh');check(r['_shards']['failed']==0,r)
    def observe(self,name,want):
        body=json.loads((ROOT/'search/f38/search.json').read_text())
        result=self.req('POST','/api/attractions/search',body,base=APP)
        check([(x['id'],x['ticketPriceFen']) for x in result['items']]==want,result)
        replay=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',result['esRequest'])
        check([(x['_id'],x['_source']['ticket_price_fen']) for x in replay['hits']['hits']]==want,replay)
        check(result['total']==len(want) and result['totalRelation']=='eq',result)
        self.save(name+'-java-search',{'request':body,'response':result,'rest_replay':replay})
        if ARGS.observer:
            spec=importlib.util.spec_from_file_location('f38_observer',ARGS.observer)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.capture(name,want,APP,ES,READ,self.out)
    def app_start(self):
        with socket.socket() as s:check(s.connect_ex(('127.0.0.1',18088))!=0,'18088 occupied')
        env=os.environ.copy();env.update(ES_URL=ES,ES_INDEX=READ,ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18088')
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
        check(not self.req('GET','/connectors',base=CONNECT),'Connector already exists; clean up first')
        exists=self.sql(text="SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='travel_f38';")
        check(exists.strip()=='0','Database exists; clean up first')
        credential=(INFRA/'.local/cdc.properties').read_text().strip().split('=',1)[1]
        sql(source('setup.sql').replace('@CDC_PASSWORD@',"'"+credential+"'"))
        self.save('source-setup',{'file':'data/f38/setup.sql','secret_via_stdin':True,'passed':True})
        grants=sql("SHOW GRANTS; SELECT COUNT(*) FROM travel_f38.attraction;",cdc=True)
        check('REPLICATION SLAVE' in grants.stdout and 'RELOAD' in grants.stdout and grants.stdout.rstrip().endswith('2'),grants.stdout)
        denied=sql("UPDATE travel_f38.attraction SET ticket_price_fen=1 WHERE attraction_id='p01';",required=False,cdc=True)
        check(denied.returncode!=0 and '1142' in denied.stderr,denied.stderr)
        self.save('permissions',{'cdc_grants_and_select':grants.stdout,'denied_update':denied.stderr,'passed':True})
        for topic in [TOPIC,HISTORY]:
            args=['kafka-topics','--create','--topic',topic,'--partitions','1','--replication-factor','1','--config','cleanup.policy=delete','--config','retention.ms='+('-1' if topic==HISTORY else '604800000')]
            if topic==HISTORY:args+=['--config','retention.bytes=-1']
            command(kafka(*args))
        self.req('PUT','/'+INDEX,json.loads((ROOT/'search/f38/create.json').read_text()))
        self.req('POST','/_aliases',json.loads((ROOT/'search/f38/aliases.json').read_text()))
        self.req('POST','/connectors',json.loads((ROOT/'cdc/f38/connector.json').read_text()),expected=201,base=CONNECT)
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
        self.position('c01-positions');self.history('c01-history')

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
        check(deleted['value']['before']['attraction_id']=='p03' and deleted['value']['before']['ticket_price_fen']==3000 and deleted['value']['before']['name']=='西湖 花园' and marker['value'] is None and marker['key']==deleted['key'],events)
        applied=self.drain('c02-delete-apply');check([e['result'] for e in applied[:-1]]==['delete:deleted','tombstone'],applied)
        self.refresh();before_stop=self.expected();self.docs(before_stop,'c02-deleted');self.observe('deleted',[('p01',6500)])
        self.position('c02-positions')

        self.case='c03-restart'
        before_events=self.inspect('c03-before-stop-events');before_count=len(before_events)
        compose('stop','connect')
        before_raw=self.sql('positions.sql');self.save('c03-binlog-before-offline',before_raw)
        self.sql('offline.sql');after_raw=self.sql('positions.sql');self.save('c03-binlog-offline',after_raw)
        before=before_raw.splitlines()[1].split('\t');after=after_raw.splitlines()[1].split('\t')
        check(before[0]==after[0] and int(after[1])>int(before[1]),{'before':before,'after':after})
        check(len(self.inspect('c03-offline-events'))==before_count,'Kafka changed with Connect off')
        self.docs(before_stop,'c03-offline-es');self.observe('offline',[('p01',6500)])
        compose('start','connect');wait(lambda:self.req('GET','/',base=CONNECT,record=False),'Connect HTTP')
        self.running();self.wait_events(before_count+4)
        events=self.inspect('c03-resumed-events');new=events[before_count:]
        check([(e['value']['op'] if e['value'] else 'tombstone',e['key']['attraction_id']) for e in new]==[('u','p01'),('c','p04'),('d','p02'),('tombstone','p02')],new)
        check(new[0]['value']['after']['source_note']=='binlog-after-restart',new)
        history=self.history('c03-history');check(any('ADD COLUMN source_note' in x.get('ddl','') for x in history),history)
        self.docs(before_stop,'c03-kafka-ahead-of-es')
        self.drain('c03-resume-apply');self.refresh();final=self.expected();self.docs(final,'c03-final')
        self.observe('resumed',[('p01',7000),('p04',1800)])
        self.req('GET','/'+READ+'/_doc/p02',expected=404);self.req('GET','/'+READ+'/_doc/p03',expected=404)
        again=self.drain('c03-java-restart-noop');check(again[-1]['processed']==0,again)
        pos=self.position('c03-positions')
        check(pos['variables']['server_id']==1838 and pos['variables']['server_uuid']==json.loads(before_raw.splitlines()[0])['server_uuid'],pos)
        # An empty schema-history topic is not a substitute for saved source offsets.
        self.missing_history_probe()
        self.save('summary',{'at':now(),'passed':True,'cases':3,'http_by_case':dict(collections.Counter(e['case'] for e in self.http)),
            'http_by_base':dict(collections.Counter(e['base'] for e in self.http)),'total_recorded_http':len(self.http),
            'kafka_event_count':len(events),'consumer_final':again[-1],'final_documents':final,
            'binlog_test':'Same server and original volumes; file position grew while stopped; DDL read after history restore; empty-history failure and restoration tested; no purge/long-outage test',
            'limits':['One MySQL primary, one Kafka partition, one consumer and immutable business keys',
                      'Graceful Connect stop/start with original Kafka offsets and schema history; no crash/exactly-once proof',
                      'No multi-table projection, arbitrary out-of-order delivery, retry/DLQ or online rebuild']})
    def missing_history_probe(self):
        command(kafka('kafka-topics','--create','--topic',EMPTY_HISTORY,'--partitions','1','--replication-factor','1','--config','retention.ms=-1','--config','retention.bytes=-1'))
        config=json.loads((ROOT/'cdc/f38/connector.json').read_text())['config']
        broken=dict(config);broken['schema.history.internal.kafka.topic']=EMPTY_HISTORY
        self.req('PUT','/connectors/'+NAME+'/config',broken,base=CONNECT)
        failed=wait(lambda:(lambda s:s if s['tasks'] and s['tasks'][0]['state']=='FAILED' else False)(self.status(False)),'Expected missing-history failure',attempts=60)
        trace=failed['tasks'][0].get('trace','')
        check('history' in trace.lower() and ('missing' in trace.lower() or 'not available' in trace.lower() or 'does not exist' in trace.lower()),trace)
        self.save('c03-missing-history-failure',failed)
        self.req('PUT','/connectors/'+NAME+'/config',config,base=CONNECT);self.running()
        events=self.inspect('c03-history-restored-events');check(len(events)==11 and not any(e['value'] and e['value']['op']=='r' for e in events[2:]),events)
        again=self.drain('c03-history-restored-noop');check(again[-1]['processed']==0,again)
        command(kafka('kafka-topics','--delete','--topic',EMPTY_HISTORY))
        wait(lambda:EMPTY_HISTORY not in command(kafka('kafka-topics','--list')).stdout.splitlines(),'Empty topic deletion')
    def cleanup(self):
        self.identity();self.guard();self.case='cleanup'
        names=self.req('GET','/connectors',base=CONNECT)
        if NAME in names:
            self.req('PUT','/connectors/'+NAME+'/stop',base=CONNECT,expected=204)
            wait(lambda:self.status(False)['connector']['state']=='STOPPED','Connector STOPPED')
            self.req('DELETE','/connectors/'+NAME+'/offsets',base=CONNECT)
            self.req('DELETE','/connectors/'+NAME,base=CONNECT,expected=204)
        self.sql(text="DROP DATABASE IF EXISTS travel_f38; DROP USER IF EXISTS 'f38_cdc'@'%';")
        topics=command(kafka('kafka-topics','--list')).stdout.splitlines()
        for topic in [TOPIC,HISTORY,EMPTY_HISTORY]:
            if topic in topics:command(kafka('kafka-topics','--delete','--topic',topic))
        wait(lambda:not set([TOPIC,HISTORY,EMPTY_HISTORY]).intersection(command(kafka('kafka-topics','--list')).stdout.splitlines()),'Topic deletion')
        group=command(kafka('kafka-consumer-groups','--delete','--group',GROUP),required=False)
        check(group.returncode==0 or 'GroupIdNotFoundException' in group.stdout+group.stderr,group.stdout+group.stderr)
        self.req('DELETE','/'+INDEX,expected=[200,404])
        remaining=self.sql(text="SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='travel_f38'; SELECT COUNT(*) FROM mysql.user WHERE user='f38_cdc';")
        check(remaining.strip()=='0\n0',remaining)
        self.save('summary',{'at':now(),'passed':True,'deleted':[NAME+' source offsets',NAME,TOPIC,HISTORY,GROUP,INDEX,'travel_f38 database','f38_cdc user'],'preserved':['all three data volumes','Connect internal topics','local secret files','other course resources']})

def main():
    lab=Lab(ARGS.out)
    try:
        if ARGS.action=='init':
            local=INFRA/'.local';check(not local.exists(),'F38 .local exists; do not overwrite')
            volumes=command(['docker','volume','ls','--format','{{.Name}}']).stdout.splitlines()
            check(not any(x.startswith('es-framework-f38_') for x in volumes),'Existing F38 volumes; do not mix new passwords')
            local.mkdir(mode=0o700)
            admin=secrets.token_urlsafe(32);cdc=secrets.token_urlsafe(32)
            for name,value in [('mysql-password.txt',admin+'\n'),('admin.cnf','[client]\nuser=root\npassword='+admin+'\n'),
                               ('cdc.cnf','[client]\nuser=f38_cdc\npassword='+cdc+'\nhost=127.0.0.1\n'),
                               ('cdc.properties','password='+cdc+'\n')]:
                p=local/name;p.write_text(value);p.chmod(0o600)
            lab.save('summary',{'at':now(),'passed':True,'secrets_written':4,'credentials_in_output':False})
        elif ARGS.action=='start':
            compose('up','-d')
            wait(lambda:lab.req('GET','/',record=False),'ES HTTP')
            wait(lambda:lab.req('GET','/',base=CONNECT,record=False),'Connect HTTP')
            lab.identity();lab.save('summary',{'at':now(),'passed':True})
        elif ARGS.action=='prepare':lab.identity();lab.guard();lab.prepare();lab.save('summary',{'at':now(),'passed':True})
        elif ARGS.action=='run':lab.run()
        elif ARGS.action=='probe-history':
            lab.identity();lab.guard();lab.case='history-probe'
            events=lab.inspect('before-events');check(len(events)==11,'Complete the three cases first')
            check(lab.drain('before-noop')[-1]['processed']==0,'Expected original committed group')
            lab.missing_history_probe();lab.save('summary',{'at':now(),'passed':True})
        elif ARGS.action=='cleanup':lab.cleanup()
        elif ARGS.action=='down':compose('down');lab.save('summary',{'at':now(),'passed':True,'volumes_preserved':True})
        print('F38',ARGS.action,'passed:',lab.out)
    finally:lab.stop()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init','start','prepare','run','probe-history','cleanup','down'])
    p.add_argument('--out',required=True);p.add_argument('--observer');ARGS=p.parse_args();main()
