#!/usr/bin/env python3
"""F36 SQL snapshot/projection lab. Manual known-key reconciliation, no CDC claim."""
import argparse, collections, datetime, gzip, importlib.util, json, os, pathlib
import secrets, socket, subprocess, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
INFRA = ROOT / 'infra/f36'
ES = 'http://127.0.0.1:20036'
APP = 'http://127.0.0.1:18086'
INDEX = 'tut-f36-attractions-v001'
READ = 'tut-f36-attractions-read'
WRITE = 'tut-f36-attractions-write'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def check(ok, detail):
    if not ok: raise AssertionError(detail)
def command(args, data=None):
    r = subprocess.run(args, input=data, text=True, capture_output=True, cwd=ROOT, timeout=120)
    check(r.returncode == 0, {'command': args, 'stderr': r.stderr[-3000:]})
    return r.stdout
def compose_args(*args): return ['docker','compose','-f',str(INFRA/'compose.yaml'),*args]
def compose(*args): return command(compose_args(*args))
def psql_args(): return compose_args('exec','-T','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-U','travel','-d','travel_f36')
def sql(text): return command(psql_args(), text)
def source(name): return (ROOT/'data/f36'/name).read_text()
def rows(text): return [json.loads(line) for line in text.splitlines() if line.startswith('{')]
def bulk_bytes(projection):
    lines = []
    for r in projection:
        lines.append(json.dumps({r['op']: {'_id': r['id']}}, ensure_ascii=False))
        if r['op'] == 'index': lines.append(json.dumps(r['document'], ensure_ascii=False))
    return ('\n'.join(lines)+'\n').encode()

class Lab:
    def __init__(self, out):
        self.out = pathlib.Path(out).resolve(); self.out.mkdir(parents=True, exist_ok=False)
        self.events = []; self.case = 'setup'; self.proc = None; self.log = None
    def save(self, name, value):
        (self.out/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    def req(self, method, path, body=None, expected=200, base=ES):
        data = body if isinstance(body,bytes) else None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(base+path, data=data, method=method,
            headers={'Content-Type': 'application/x-ndjson' if isinstance(body,bytes) else 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=30) as r: status, value = r.status, json.load(r)
        except urllib.error.HTTPError as e:
            status, value = e.code, json.loads(e.read()) if method != 'HEAD' else {}
        rec = {'at':now(),'case':self.case,'base':base,'method':method,'path':path,'status':status,
               'body':body.decode() if isinstance(body,bytes) else body,'response':value}
        self.events.append(rec)
        with (self.out/'http.jsonl').open('a') as f: f.write(json.dumps(rec,ensure_ascii=False)+'\n')
        check(status in ([expected] if isinstance(expected,int) else expected), rec)
        return value
    def sql(self, name=None, text=None):
        content = source(name) if name else text; result = sql(content)
        with (self.out/'sql.jsonl').open('a') as f:
            f.write(json.dumps({'at':now(),'case':self.case,'file':name,'sql':content,'stdout':result},ensure_ascii=False)+'\n')
        return result
    def export(self, name, query='export.sql'):
        text = self.sql(query); (self.out/(name+'.ndjson')).write_text(text); return rows(text)
    def identity(self):
        identity = self.req('GET','/')
        check(identity['cluster_name']=='travel-f36-lab' and identity['version']['number']=='9.4.0',identity)
        nodes = self.req('GET','/_nodes/jvm')
        check(len(nodes['nodes'])==1 and next(iter(nodes['nodes'].values()))['name']=='travel-f36-es',nodes)
        pg = self.sql(text='SELECT current_database(), current_user, version();')
        check(pg.startswith('travel_f36|travel|PostgreSQL 17.5 '),pg)
        self.save('identity',{'es':identity,'nodes':nodes,'postgres':pg})
    def guard(self):
        indices = self.req('GET','/_cat/indices?format=json&expand_wildcards=all')
        check(all(x['index']==INDEX or x['index'].startswith('.') for x in indices), 'foreign business index')
    def rest_import(self, projection, name):
        data = bulk_bytes(projection); (self.out/(name+'.bulk.ndjson')).write_bytes(data)
        result = self.req('POST','/'+WRITE+'/_bulk?require_alias=true',data)
        check(len(result['items'])==len(projection) and not result['errors'],result)
        for item in result['items']:
            action, value = next(iter(item.items())); check('error' not in value and value['status'] in [200,201],item)
        self.save(name+'-rest-import', result); return result
    def java_import(self, name):
        text = command(['bash','labs/f36/java.sh',str(self.out/(name+'.ndjson'))])
        (self.out/(name+'-java-import.txt')).write_text(text)
        operations = [line for line in text.splitlines() if line.startswith(('index ','delete '))]
        check(operations, text); return operations
    def refresh(self):
        r=self.req('POST','/'+INDEX+'/_refresh');check(r['_shards']['failed']==0,r)
    def all(self):
        result=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',json.loads((ROOT/'search/f36/all.json').read_text()))
        check(not result['timed_out'] and result['_shards']['failed']==0,result)
        return result
    def assert_docs(self, expected, name):
        result=self.all(); actual={h['_id']:h['_source'] for h in result['hits']['hits']}
        want={r['id']:r['document'] for r in expected if r['op']=='index'}
        check(actual==want and result['hits']['total']['value']==len(want),{'actual':actual,'expected':want})
        self.save(name,result)
    def observe(self, name, want):
        body=json.loads((ROOT/'search/f36/search.json').read_text())
        result=self.req('POST','/api/attractions/search',body,base=APP)
        check([(r['id'],r['ticketPriceFen']) for r in result['items']]==want,result)
        check(result['total']==len(want) and result['totalRelation']=='eq',result)
        replay=self.req('POST','/'+READ+'/_search?allow_partial_search_results=false',result['esRequest'])
        check([(r['_id'],r['_source']['ticket_price_fen']) for r in replay['hits']['hits']]==want,replay)
        self.save(name+'-java',{'request':body,'response':result,'rest_replay':replay})
        if ARGS.observer:
            spec=importlib.util.spec_from_file_location('f36_observer',ARGS.observer)
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            module.capture(name,want,APP,ES,READ,self.out)
    def app_start(self):
        with socket.socket() as s: check(s.connect_ex(('127.0.0.1',18086))!=0,'18086 already occupied')
        env=os.environ.copy();env.update(ES_URL=ES,ES_INDEX=READ,ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18086')
        self.log=(self.out/'application.log').open('w')
        self.proc=subprocess.Popen(['java','-Xms64m','-Xmx192m','-jar','backend/target/travel-search-0.7.0.jar'],cwd=ROOT,env=env,stdout=self.log,stderr=subprocess.STDOUT)
        for _ in range(90):
            check(self.proc.poll() is None,'Java failed; inspect application.log')
            try:
                with urllib.request.urlopen(APP+'/',timeout=1) as r:
                    if r.status==200:return
            except (OSError,urllib.error.URLError):pass
            time.sleep(1)
        raise TimeoutError('Java startup')
    def stop(self):
        if self.proc:
            self.proc.terminate()
            try:self.proc.wait(timeout=20)
            except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
        if self.log:
            self.log.close();p=self.out/'application.log'
            with gzip.open(str(p)+'.gz','wb') as f:f.write(p.read_bytes())
            p.unlink()
    def cleanup(self):
        self.case='cleanup';self.identity();self.guard()
        self.req('DELETE','/'+INDEX,expected=[200,404])
        self.sql(text='DROP SCHEMA IF EXISTS f36 CASCADE;')
        check(self.sql(text="SELECT count(*) FROM pg_namespace WHERE nspname='f36';").strip()=='0','schema remains')
        self.req('HEAD','/'+INDEX,expected=404)
    def run(self):
        self.identity();self.guard()
        check(self.sql(text="SELECT count(*) FROM pg_namespace WHERE nspname='f36';").strip()=='0','run cleanup first')
        self.req('HEAD','/'+INDEX,expected=404)
        self.case='f36-c01'
        for name in ['schema.sql','seed.sql','projection-view.sql']:self.sql(name)
        before=self.export('01-initial')
        check([(r['id'],r['op']) for r in before]==[('p01','index'),('p02','index')],before)
        self.req('PUT','/'+INDEX,json.loads((ROOT/'search/f36/create.json').read_text()))
        self.req('POST','/_aliases',json.loads((ROOT/'search/f36/aliases.json').read_text()))
        self.rest_import(before,'01-initial');self.refresh();self.assert_docs(before,'01-projected')
        self.java_import('01-initial');self.refresh();self.assert_docs(before,'01-repeated-same-ids')
        self.app_start();self.observe('01-initial',[('p01',6000),('p02',0)])
        self.case='f36-c02';self.sql('related-change.sql');related=self.export('02-related')
        check(all(r['document']['city_name']=='杭州（旅游展示名）' for r in related),related)
        check(related[0]['document']['tags']==['亲子'],related)
        self.assert_docs(before,'02-db-changed-es-still-old')
        self.java_import('02-related');self.refresh();self.assert_docs(related,'02-related-refreshed')
        self.case='f36-c03'
        snapshot=subprocess.Popen(psql_args(),cwd=ROOT,text=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            begin="BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;\nSELECT current_setting('transaction_isolation'), count(*) FROM f36.attraction;\n"+source('export.sql')+'\n\\echo F36_SNAPSHOT_READY\n'
            snapshot.stdin.write(begin);snapshot.stdin.flush();captured=[]
            while True:
                line=snapshot.stdout.readline()
                check(line!='', 'snapshot session ended unexpectedly')
                if line.strip()=='F36_SNAPSHOT_READY':break
                captured.append(line)
            check('repeatable read|2' in ''.join(captured),captured)
            frozen=rows(''.join(captured));check(frozen==related,frozen)
            (self.out/'03-frozen.ndjson').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in frozen))
            self.sql('during-snapshot.sql')
            tail,err=snapshot.communicate(source('export.sql')+'\nCOMMIT;\n',timeout=30)
            check(snapshot.returncode==0,err);check(rows(tail)==frozen,'repeatable read changed view')
            self.save('03-snapshot-session',{'begin_sql':begin,'first_stdout':''.join(captured),'second_stdout':tail,
                'first_projection':frozen,'second_projection':rows(tail),'same':True,'boundary':'first SELECT, not BEGIN; not a CDC checkpoint'})
        finally:
            if snapshot.poll() is None:snapshot.kill();snapshot.wait()
        current=self.export('03-current','known-delta.sql')
        check([(r['id'],r['op']) for r in current]==[('p01','index'),('p02','delete'),('p03','index')],current)
        self.rest_import(frozen,'03-frozen');self.refresh();self.assert_docs(frozen,'03-snapshot-omits-commits')
        self.observe('03-snapshot-gap',[('p01',6000),('p02',0)])
        ops=self.java_import('03-current')
        check(ops==['index p01 200 updated','delete p02 200 deleted','index p03 201 created'],ops)
        get=self.req('GET','/'+READ+'/_doc/p01');check(get['_source']['ticket_price_fen']==6500,get)
        self.req('GET','/'+READ+'/_doc/p02',expected=404)
        self.assert_docs(frozen,'03-written-search-still-old')
        self.observe('03-before-refresh',[('p01',6000),('p02',0)])
        self.refresh();self.assert_docs(current,'03-reconciled');self.observe('03-after-refresh',[('p01',6500),('p03',3000)])
        # Re-read every source projection while no other writer runs; count alone is insufficient.
        final=self.export('03-final');check(final==current,'source changed during controlled pause')
        self.save('03-stage-evidence',{'snapshot_ids':['p01','p02'],'committed_source':['p01:6500','p02:closed','p03:3000'],
            'manual_keys':['p01','p02','p03'],'get_before_refresh':6500,'search_before_refresh':[['p01',6000],['p02',0]],
            'search_after_refresh':[['p01',6500],['p03',3000]],'source_and_es_full_fields_equal':True,
            'automatic_event_capture':False,'checkpoint':None,'pause':'no other writers in this isolated lab',
            'not_verified':['WAL/binlog','Kafka','consumer offset','continuous catch-up','cross-table ordering','physical-delete capture']})
    def finish(self, action):
        counts=collections.Counter((r['case'],'java-search' if r['base']==APP else 'rest') for r in self.events)
        self.save('summary',{'at':now(),'action':action,'passed':True,'http_counts':[{'case':c,'type':t,'count':n} for (c,t),n in counts.items()],
            'java_bulk_calls':3 if action=='run' else 0,'cdc_implemented':False,'review':'author self-review'})

def main():
    global ARGS
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['init','start','run','cleanup','down','rest-import'])
    parser.add_argument('--out',required=True);parser.add_argument('--observer');parser.add_argument('--file');ARGS=parser.parse_args()
    lab=Lab(ARGS.out)
    try:
        if ARGS.action=='init':
            local=INFRA/'.local';check(not local.exists(),'local secrets already exist')
            existing=command(['docker','volume','ls','--format','{{.Name}}']).splitlines()
            check(not any(v.startswith('es-framework-f36-') or v.startswith('es-framework-f36_') for v in existing),'F36 volumes already exist')
            local.mkdir(mode=0o700);p=local/'pg-password.txt';p.write_text(secrets.token_urlsafe(32)+'\n');p.chmod(0o600)
        elif ARGS.action=='start':
            check((INFRA/'.local/pg-password.txt').is_file(),'init first')
            compose('up','-d')
            for attempt in range(100):
                try:
                    with urllib.request.urlopen(ES+'/',timeout=2) as r:check(json.load(r)['cluster_name']=='travel-f36-lab','wrong endpoint')
                    sql('SELECT 1;');break
                except (OSError,AssertionError):
                    if attempt==99:raise
                    time.sleep(2)
            lab.identity()
        elif ARGS.action=='run':lab.run()
        elif ARGS.action=='cleanup':lab.cleanup()
        elif ARGS.action=='down':compose('down')
        else:
            check(ARGS.file,'--file required');lab.identity()
            lab.rest_import(rows(pathlib.Path(ARGS.file).read_text()),'manual')
        lab.finish(ARGS.action);print('F36 '+ARGS.action+' passed: '+str(lab.out))
    except Exception as e:
        lab.save('failure',{'at':now(),'action':ARGS.action,'error':str(e)});raise
    finally:lab.stop()
if __name__=='__main__':main()
