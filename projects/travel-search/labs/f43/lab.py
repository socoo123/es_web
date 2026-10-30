#!/usr/bin/env python3
"""F43 bounded, isolated experiment. Run from projects/travel-search."""
import argparse, concurrent.futures, contextlib, datetime, fcntl, hashlib
import http.client, json, math, os, pathlib, platform, socket, subprocess, threading, time

ROOT=pathlib.Path(__file__).resolve().parents[2]
LOCAL=ROOT/'labs/f43/.local'
ES='http://127.0.0.1:20743'
INDEXES=['tut-f43-import','tut-f43-load','tut-f43-pressure','tut-f43-warmup']
COMPOSE=['docker','compose','-f',str(ROOT/'infra/f43/compose.yaml')]
RECORD_LOCK=threading.Lock()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def encoded(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def check(ok,message):
    if not ok:raise AssertionError(message)
def command(args,out,name,ok=True):
    p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    (out/(name+'.stdout.txt')).write_text(p.stdout);(out/(name+'.stderr.txt')).write_text(p.stderr)
    check(not ok or p.returncode==0,{'command':args,'status':p.returncode,'stderr':p.stderr[-1500:]})
    return p
class HTTP:
    def __init__(self):self.connection=http.client.HTTPConnection('127.0.0.1',20743,timeout=30)
    def close(self):self.connection.close()
    def call(self,method,path,body=None,raw=False):
        data=body if raw else None if body is None else encoded(body)
        self.connection.request(method,path,body=data,headers={'Content-Type':'application/x-ndjson' if path=='/_bulk' else 'application/json'})
        response=self.connection.getresponse();payload=response.read()
        return response.status,json.loads(payload) if payload else None
def api(out,method,path,body=None,expected=200):
    with contextlib.closing(HTTP()) as c:status,result=c.call(method,path,body)
    with RECORD_LOCK:
        with (out/'http.jsonl').open('a') as f:f.write(json.dumps({'at':now(),'method':method,'path':path,'body':body,'status':status,'response':result},ensure_ascii=False)+'\n')
    check(status in ([expected] if isinstance(expected,int) else expected),{'path':path,'status':status,'response':result})
    return result
def identity(out):
    value=api(out,'GET','/')
    check(value['cluster_name']=='travel-f43-lab' and value['version']['number']=='9.4.0','Wrong ES cluster/version')
    expected=json.loads((LOCAL/'identity.json').read_text())
    check(value['cluster_uuid']==expected['cluster_uuid'],'Wrong persistent cluster identity')
    return value
def ready(nodes=1):
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        try:
            with contextlib.closing(HTTP()) as c:
                status,value=c.call('GET','/_cluster/health')
            if status==200 and value['number_of_nodes']==nodes:return
        except (OSError,http.client.HTTPException):pass
        time.sleep(1)
    raise TimeoutError('F43 nodes not ready; inspect only this Compose project')
def start(out):
    LOCAL.mkdir(parents=True,exist_ok=True)
    marker=LOCAL/'identity.json'
    if not marker.exists():
        for name in ['n1','n2']:
            p=subprocess.run(['docker','volume','inspect','es-framework-f43_'+name+'-data'],capture_output=True)
            check(p.returncode!=0,'Existing F43 volume without identity; refuse automatic bootstrap')
        command(COMPOSE+['-f',str(ROOT/'infra/f43/bootstrap.yaml'),'up','-d','n1'],out,'bootstrap')
        ready()
        value=api(out,'GET','/');check(value['cluster_name']=='travel-f43-lab','Wrong cluster')
        save(marker,{'cluster_uuid':value['cluster_uuid']})
        # Remove bootstrap configuration on the original persisted volume.
        command(COMPOSE+['up','-d','--force-recreate','n1'],out,'remove-bootstrap')
    else:command(COMPOSE+['up','-d','n1'],out,'start')
    ready();identity(out)
def corpus(count):
    for i in range(1,count+1):
        yield {'attraction_id':f'p{i:06d}','name':('西湖 游船' if i%4==1 else '山水 公园')+f' 样本 {i:06d}',
               'summary':'合成旅游资料，用于固定负载对照。'*12,'city_code':'HZ' if i%2 else 'SZ',
               'city_name':'杭州' if i%2 else '苏州','ticket_price_fen':6000+(i%20)*100,
               'currency':'CNY','status':'closed' if i%10==0 else 'open',
               'location':{'lat':30.25+(i%10)*.0001,'lon':120.15+(i%10)*.0001},'tags':['合成','亲水']}
def generate(out,count):
    path=out/f'corpus-{count}.jsonl'
    data=b''.join(encoded(d)+b'\n' for d in corpus(count));path.write_bytes(data)
    save(out/f'corpus-{count}.json',{'generator':'f43-v1','count':count,'utf8_bytes':len(data),
        'sha256':hashlib.sha256(data).hexdigest(),'first':next(corpus(count))})
    return path
def create(out,index,shards=1,replicas=0):
    check(index in INDEXES,'Index whitelist')
    api(out,'DELETE','/'+index,expected=[200,404])
    value=json.loads((ROOT/'search/f43/create.json').read_text())
    value['settings'].update(number_of_shards=shards,number_of_replicas=replicas)
    api(out,'PUT','/'+index,value)
    health=api(out,'GET',f'/_cluster/health/{index}?wait_for_status=green&wait_for_no_relocating_shards=true&timeout=60s')
    check(not health['timed_out'],'Index allocation timed out')
def refresh(out,index):
    value=api(out,'POST','/'+index+'/_refresh');check(value['_shards']['failed']==0,'Refresh failure')
def bulk(out,path,batch,workers,index='tut-f43-import',name='bulk',failure=False):
    result=out/(name+'.json')
    p=command(['bash','labs/f43/java.sh',index,str(path),str(batch),str(workers),str(result)],out,name,ok=False)
    check(p.returncode==(2 if failure else 0),{'bulk_exit':p.returncode,'stderr':p.stderr[-2000:]})
    value=json.loads(result.read_text());check((value['failures']>0)==failure,'Bulk failure expectation')
    return value
def verify(out,index,documents,prices=None,name='verified'):
    refresh(out,index)
    count=len(documents);actual={};cursor=None
    while True:
        query={'size':500,'sort':[{'attraction_id':'asc'}],'query':{'match_all':{}}}
        if cursor:query['search_after']=cursor
        result=api(out,'POST','/'+index+'/_search?allow_partial_search_results=false',query)
        check(not result['timed_out'] and result['_shards']['failed']==0,'Incomplete verification')
        hits=result['hits']['hits']
        if not hits:break
        for hit in hits:
            check(hit['_id'] not in actual,'Duplicate verification ID');actual[hit['_id']]=hit['_source']
        cursor=hits[-1]['sort']
    expected={d['attraction_id']:dict(d) for d in documents}
    for key,price in (prices or {}).items():expected[key]['ticket_price_fen']=price
    check(actual==expected,{'verification':'complete source mismatch','count':len(actual)})
    query=json.loads((ROOT/'search/f43/query.json').read_text())
    result=api(out,'POST','/'+index+'/_search?allow_partial_search_results=false&request_cache=false',query)
    check(result['hits']['total']=={'value':count//4,'relation':'eq'},'Wrong query total')
    expected_ids=[f'p{i:06d}' for i in range(1,38,4)]
    check([x['_id'] for x in result['hits']['hits']]==expected_ids,'Wrong first page')
    value={'count':count,'full_source_equal':True,'first_ids':expected_ids,'query_total':count//4,
           'last_prices':{k:prices[k] for k in sorted(prices or {})[:5]}}
    save(out/(name+'.json'),value);return value
def stats(out,name):
    # Dedicated cluster only. Node-level counters include both measured and monitoring work.
    value=api(out,'GET','/_nodes/stats/indices,jvm,process,fs,thread_pool,indexing_pressure,breaker')
    check(value['_nodes']['failed']==0,'Node stats partial failure')
    save(out/(name+'.json'),value);return value
def pctl(values,p):
    return sorted(values)[math.ceil(len(values)*p)-1] if values else None
def mixed(out,documents,searchers,updaters,warmup,seconds,name):
    # Persistent connection per worker; one outstanding request per worker (closed loop).
    # The sole updater owns all changed IDs, so final-state verification is unambiguous.
    check(updaters in [0,1] and searchers in [4,8],'Bounded worker topology')
    query=(ROOT/'search/f43/query.json').read_bytes();samples=[];prices={};guard=threading.Lock()
    gate=threading.Barrier(searchers+updaters+1);clock={};failures=[]
    def worker(w,kind):
        local=[];seq=0
        try:
            with contextlib.closing(HTTP()) as connection:
                gate.wait(timeout=15)
                while time.monotonic()<clock['deadline']:
                    begin=time.monotonic();measured=begin>=clock['measure'];utc=now()
                    if begin>=clock['deadline']:break
                    if kind=='search':
                        status,value=connection.call('POST','/tut-f43-load/_search?allow_partial_search_results=false&request_cache=false',query,raw=True)
                        ok=status==200 and not value.get('timed_out',True) and value.get('_shards',{}).get('failed',1)==0
                        ok=ok and value['hits']['total']=={'value':len(documents)//4,'relation':'eq'}
                        ok=ok and [x['_id'] for x in value['hits']['hits']]==[f'p{i:06d}' for i in range(1,38,4)]
                        units=1
                    else:
                        items=[];changes={}
                        for j in range(20):
                            source=dict(documents[(seq*20+j)%len(documents)])
                            key=source['attraction_id'];source['ticket_price_fen']=7000+(seq%100)*10
                            items.extend([{'index':{'_index':'tut-f43-load','_id':key}},source]);changes[key]=source['ticket_price_fen']
                        payload=b''.join(encoded(x)+b'\n' for x in items)
                        status,value=connection.call('POST','/_bulk',payload,raw=True)
                        ok=status==200 and len(value.get('items',[]))==20 and all(x['index']['status']<300 for x in value['items'])
                        units=20
                        if ok:prices.update(changes)
                    end=time.monotonic()
                    local.append({'worker':w,'kind':kind,'at':utc,'start_seconds':begin-clock['measure'],
                        'end_seconds':end-clock['measure'],'ms':(end-begin)*1000,'measured':measured,
                        'ok':ok,'http':status,'units':units,'error':None if ok else value})
                    seq+=1
                    if not ok:raise AssertionError('Request failed; bounded experiment stopped')
        except BaseException as error:
            with guard:failures.append(repr(error))
        finally:
            with guard:samples.extend(local)
    before=stats(out,name+'-before')
    resource=[];stop=threading.Event()
    def monitor():
        try:
            while not stop.wait(1):
                with contextlib.closing(HTTP()) as c:
                    status,value=c.call('GET','/_nodes/stats/jvm,process,fs,thread_pool,indexing_pressure,breaker')
                check(status==200 and value['_nodes']['failed']==0,'Monitoring failed')
                resource.append({'at':now(),'relative_seconds':time.monotonic()-clock['measure'],'nodes':value})
        except BaseException as error:
            with guard:failures.append('monitor: '+repr(error))
    with concurrent.futures.ThreadPoolExecutor(max_workers=searchers+updaters) as pool:
        tasks=[pool.submit(worker,w,'search' if w<searchers else 'update') for w in range(searchers+updaters)]
        # All workers are created and at the barrier before the shared clock starts.
        while gate.n_waiting<searchers+updaters:
            check(not any(task.done() for task in tasks),'Worker failed before start barrier');time.sleep(.01)
        start=time.monotonic();clock.update(measure=start+warmup,deadline=start+warmup+seconds)
        probe=threading.Thread(target=monitor,daemon=True);probe.start();gate.wait(timeout=15)
        for task in tasks:task.result(timeout=warmup+seconds+40)
        ended=time.monotonic();stop.set();probe.join(timeout=35)
    after=stats(out,name+'-after')
    save(out/(name+'-resources.json'),resource)
    measured=[s for s in samples if s['measured']]
    span=ended-clock['measure'];result={'name':name,'searchers':searchers,'updaters':updaters,
        'warmup_seconds':warmup,'admission_window_seconds':seconds,'elapsed_including_drain_seconds':span,
        'window_definition':'request starts in [0, window); count after every admitted request finishes',
        'failures':failures,'samples':sorted(samples,key=lambda s:(s['start_seconds'],s['worker']))}
    for kind in ['search','update']:
        group=[s for s in measured if s['kind']==kind];good=[s for s in group if s['ok']]
        latency=[s['ms'] for s in group]
        result[kind]={'requests':len(group),'successes':len(good),'failed':len(group)-len(good),
            'successful_units':sum(s['units'] for s in good),'successful_units_per_second':sum(s['units'] for s in good)/span,
            'p50_ms':pctl(latency,.5),'p95_ms':pctl(latency,.95),'p99_ms':pctl(latency,.99)}
    # Counters are compared per node ID. Node restart would invalidate subtraction.
    check(set(before['nodes'])==set(after['nodes']),'Node IDs changed in measurement')
    deltas={}
    for node,b in before['nodes'].items():
        a=after['nodes'][node]
        pools={k:{'rejected':a['thread_pool'][k]['rejected']-v['rejected'],
                  'completed':a['thread_pool'][k]['completed']-v['completed']} for k,v in b['thread_pool'].items()}
        deltas[node]={'name':a['name'],'thread_pool':pools,'cpu_ms':a['process']['cpu']['total_in_millis']-b['process']['cpu']['total_in_millis'],
            'gc_ms':sum(v['collection_time_in_millis'] for v in a['jvm']['gc']['collectors'].values())-sum(v['collection_time_in_millis'] for v in b['jvm']['gc']['collectors'].values()),
            'indexing_pressure_before':b['indexing_pressure'],'indexing_pressure_after':a['indexing_pressure'],
            'breaker_trip_deltas':{k:a['breakers'][k]['tripped']-v['tripped'] for k,v in b['breakers'].items()},
            'heap_peak_sampled_bytes':max([x['nodes']['nodes'][node]['jvm']['mem']['heap_used_in_bytes'] for x in resource]+[a['jvm']['mem']['heap_used_in_bytes']]),
            'disk_available_bytes_end':a['fs']['total']['available_in_bytes']}
    result['counter_bracket']='includes warmup and stats/monitoring; not the exact admission window'
    result['node_deltas']=deltas;save(out/(name+'.json'),result)
    save(out/(name+'-prices.json'),prices)
    check(not failures and result['search']['requests']>0 and resource,'Mixed load or monitoring failure')
    verify(out,'tut-f43-load',documents,prices,name+'-verified')
    return {k:v for k,v in result.items() if k!='samples'}
def shell(out,stage,expected_price,observer=None):
    env=os.environ.copy();env.update(ES_URL=ES,ES_INDEX='tut-f43-load',ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18093')
    with socket.socket() as s:check(s.connect_ex(('127.0.0.1',18093))!=0,'Stop existing app on 18093 first')
    with (out/(stage+'-app.log')).open('w') as log:
        process=subprocess.Popen(['java','-Xms64m','-Xmx192m','-jar','backend/target/travel-search-0.7.0.jar'],cwd=ROOT,env=env,stdout=log,stderr=log)
        try:
            for _ in range(90):
                if process.poll() is not None:raise RuntimeError('F43 observation app exited')
                try:
                    c=http.client.HTTPConnection('127.0.0.1',18093,timeout=2);c.request('GET','/');r=c.getresponse();r.read();c.close()
                    if r.status==200:break
                except OSError:time.sleep(.5)
            else:raise TimeoutError('F43 app not ready')
            # Read the existing F07 contract from its provided observer input.
            body=json.loads((ROOT/'search/f43/shell-request.json').read_text())
            c=http.client.HTTPConnection('127.0.0.1',18093,timeout=20);c.request('POST','/api/attractions/search',encoded(body),{'Content-Type':'application/json'})
            r=c.getresponse();value=json.loads(r.read());c.close();check(r.status==200,value)
            check(value['total']==2500 and value['items'][0]['id']=='p000001' and value['items'][0]['ticketPriceFen']==expected_price,{'observation_contract':value})
            replay=api(out,'POST','/tut-f43-load/_search?allow_partial_search_results=false',value['esRequest'])
            check([x['_id'] for x in replay['hits']['hits']]==[x['id'] for x in value['items']],'REST/Java mismatch')
            save(out/(stage+'-java-search.json'),value)
            if observer:
                import importlib.util
                spec=importlib.util.spec_from_file_location('f43_observer',observer);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                module.capture(stage,value,'http://127.0.0.1:18093',out)
        finally:
            process.terminate()
            try:process.wait(timeout=20)
            except subprocess.TimeoutExpired:process.kill();process.wait();raise
def cleanup(out):
    identity(out)
    actual=api(out,'GET','/_cat/indices?format=json&h=index')
    check(all(x['index'] in INDEXES or x['index'].startswith('.') for x in actual),'Unknown user index; refuse cleanup')
    for name in INDEXES:api(out,'DELETE','/'+name,expected=[200,404])
    command(COMPOSE+['stop','n2'],out,'stop-n2');command(COMPOSE+['up','-d','--force-recreate','n1'],out,'normal-n1');ready()
    for name in INDEXES:api(out,'GET','/'+name,expected=404)
def run(out,args):
    identity(out);ready()
    actual=api(out,'GET','/_cat/indices?format=json&h=index')
    check(not any(not x['index'].startswith('.') for x in actual),'Run requires clean F43 indexes; cleanup first')
    env={'at':now(),'host':platform.platform(),'python':platform.python_version(),
         'docker_info':json.loads(command(['docker','info','--format','{{json .}}'],out,'docker-info').stdout),
         'es':api(out,'GET','/'),'nodes':api(out,'GET','/_nodes/settings,jvm,os,process')}
    save(out/'environment.json',env)
    inspected=json.loads(command(['docker','inspect','es-framework-f43-n1-1'],out,'containers-before').stdout)
    save(out/'container-resources.json',[{'name':x['Name'],'id':x['Id'],'started_at':x['State']['StartedAt'],
        'pid':x['State']['Pid'],'memory_limit_bytes':x['HostConfig']['Memory'],'nano_cpus':x['HostConfig']['NanoCpus'],
        'image':x['Image']} for x in inspected])
    paths={n:generate(out,n) for n in [2000,10000]};documents=list(corpus(10000));summary={'bulk':[],'mixed':[]}
    create(out,'tut-f43-warmup')
    for count,batch,workers in [(2000,100,1),(10000,100,1),(10000,500,1),(10000,500,4)]:
        name=f'c01-n{count}-b{batch}-w{workers}';create(out,'tut-f43-import')
        before=stats(out,name+'-before');result=bulk(out,paths[count],batch,workers,name=name)
        stats(out,name+'-after');verify(out,'tut-f43-import',list(corpus(count)),name=name+'-verified')
        summary['bulk'].append({k:v for k,v in result.items() if k!='samples'})
    api(out,'DELETE','/tut-f43-import');api(out,'DELETE','/tut-f43-warmup');create(out,'tut-f43-warmup')
    for name,nodes,shards,replicas,searchers,updaters in [
        ('c02-single-1p-search',1,1,0,4,0),('c02-single-1p-mixed',1,1,0,4,1),
        ('c02-single-1p-8search',1,1,0,8,1),('c02-single-2p-mixed',1,2,0,4,1),
        ('c02-pair-2p-mixed',2,2,0,4,1),('c02-pair-2p1r-mixed',2,2,1,4,1)]:
        if nodes==2:
            command(COMPOSE+['up','-d','n2'],out,name+'-nodes');ready(2)
        create(out,'tut-f43-load',shards,replicas)
        bulk(out,paths[10000],500,2,index='tut-f43-load',name=name+'-import')
        api(out,'PUT','/tut-f43-load/_settings',{'index':{'refresh_interval':'1s'}})
        refresh(out,'tut-f43-load')
        layout=api(out,'GET','/_cat/shards/tut-f43-load?format=json&h=index,shard,prirep,state,node,docs,store')
        check(len(layout)==shards*(replicas+1) and all(x['state']=='STARTED' for x in layout),'Wrong layout')
        check(len({x['node'] for x in layout})==nodes,'Expected shard distribution absent')
        save(out/(name+'-layout.json'),layout)
        api(out,'GET','/tut-f43-load/_stats/docs,store,indexing,search,refresh,merge,segments')
        if name=='c02-single-1p-search':shell(out,'initial',6100,args.observer)
        result=mixed(out,documents,searchers,updaters,args.warmup,args.seconds,name)
        api(out,'GET','/tut-f43-load/_stats/docs,store,indexing,search,refresh,merge,segments')
        result.update(nodes=nodes,primaries=shards,replicas=replicas);summary['mixed'].append(result)
        if name=='c02-single-1p-mixed':
            prices=json.loads((out/(name+'-prices.json')).read_text());shell(out,'changed',prices['p000001'],args.observer)
        api(out,'DELETE','/tut-f43-load')
    # Actual ES rejection with a deliberately tiny coordinating memory limit.
    command(COMPOSE+['stop','n2'],out,'pressure-stop-n2');ready()
    create(out,'tut-f43-pressure')
    command(COMPOSE+['-f',str(ROOT/'infra/f43/pressure.yaml'),'up','-d','--force-recreate','n1'],out,'pressure-enable');ready();identity(out)
    initial=stats(out,'c03-before');check(all(x['indexing_pressure']['memory']['limit_in_bytes']==1024 for x in initial['nodes'].values()),'Fault limit absent')
    rejected=bulk(out,paths[2000],500,1,index='tut-f43-pressure',name='c03-rejected',failure=True)
    stats(out,'c03-after');check(rejected['successes']==0,'Pressure probe unexpectedly partly succeeded')
    check(all(t.get('http')==429 for s in rejected['samples'] for t in s['trace'] if 'http' in t),'Expected actual HTTP429')
    command(COMPOSE+['up','-d','--force-recreate','n1'],out,'pressure-remove');ready();identity(out)
    normal=stats(out,'c03-normal');check(all(x['indexing_pressure']['memory']['limit_in_bytes']>1024 for x in normal['nodes'].values()),'Fault limit still active')
    recovered=bulk(out,paths[2000],100,1,index='tut-f43-pressure',name='c03-recovered')
    verify(out,'tut-f43-pressure',list(corpus(2000)),name='c03-recovered-verified')
    summary['pressure']={k:v for k,v in rejected.items() if k!='samples'}
    summary['recovered']={k:v for k,v in recovered.items() if k!='samples'}
    summary['passed']=True;save(out/'summary.json',summary)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['start','run','cleanup','down'])
    parser.add_argument('--out',type=pathlib.Path,required=True);parser.add_argument('--observer',type=pathlib.Path)
    parser.add_argument('--warmup',type=int,default=3);parser.add_argument('--seconds',type=int,default=15)
    args=parser.parse_args();check(1<=args.warmup<=30 and 5<=args.seconds<=120,'Bounded measurement windows')
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    check(pathlib.Path.cwd().resolve()==ROOT,'Run from projects/travel-search')
    LOCAL.mkdir(parents=True,exist_ok=True)
    with (LOCAL/'run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.action=='start':start(args.out)
        elif args.action=='run':run(args.out,args)
        elif args.action=='cleanup':cleanup(args.out)
        else:identity(args.out);command(COMPOSE+['down'],args.out,'down') # Preserves volumes and identity.
    print(json.dumps({'action':args.action,'out':str(args.out),'passed':True}))
if __name__=='__main__':main()
