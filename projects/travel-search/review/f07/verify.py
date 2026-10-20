#!/usr/bin/env python3
"""F07 real REST↔Boot/Java acceptance. Refuses an existing lesson index/occupied port.
Requires the packaged jar, JDK25, Python3 and the course Compose ES. No fake ES.
"""
import datetime
import hashlib
import http.client
import json
import os
import pathlib
import socket
import subprocess
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
ROOT = HERE.parents[3]
INDEX = 'tut-f07-attractions'
ES = 'http://127.0.0.1:19200'
APP = 'http://127.0.0.1:18080'
COMPOSE = ['docker', 'compose', '-f', 'infra/single-node/compose.yaml']
RECORD = {'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'F07 only; real ES9.4.0 and Boot4/JDK25, no mocks', 'requests': [], 'rounds': [], 'commands': []}

def require(value, detail):
    if not value: raise AssertionError(detail)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def command(args):
    r = subprocess.run(args, cwd=PROJECT, capture_output=True, text=True)
    RECORD['commands'].append({'args': args, 'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
    require(r.returncode == 0, r.stderr)
    return r.stdout

def request(base, path, method='GET', body=None, expected=200, content='application/json', label=''):
    data = json.dumps(body, ensure_ascii=False).encode() if isinstance(body, (dict, list)) else body
    req = urllib.request.Request(base + path, data=data, method=method, headers={'Content-Type': content})
    try:
        with urllib.request.urlopen(req, timeout=15) as r: status, raw = r.status, r.read().decode()
    except urllib.error.HTTPError as e: status, raw = e.code, e.read().decode()
    result = json.loads(raw) if raw else None
    RECORD['requests'].append({'label': label, 'url': base + path, 'method': method,
                               'input': data.decode() if data else None, 'status': status, 'raw_response': raw})
    require(status == expected, {'label': label, 'expected': expected, 'actual': status, 'response': result})
    return result

def probe(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as r: return r.status == 200
    except (OSError, http.client.HTTPException): return False

def wait(url):
    for _ in range(90):
        if probe(url): return
        time.sleep(1)
    raise AssertionError('Service not ready: ' + url)

def input_for(slug): return json.loads((PROJECT / f'search/f07/input-{slug}.json').read_text())

def verify_round(number):
    prefix=f'round-{number}'
    created=request(ES,'/'+INDEX,'PUT',json.loads((PROJECT/'search/f07/index.json').read_text()),label=prefix+' create')
    require(created['acknowledged'], created)
    health=request(ES,f'/_cluster/health/{INDEX}?wait_for_status=green&timeout=30s',label=prefix+' index health')
    require(health['status']=='green' and not health['timed_out'],health)
    mapping=request(ES,f'/{INDEX}/_mapping',label=prefix+' mapping')
    require(mapping[INDEX]['mappings']==json.loads((PROJECT/'search/f07/index.json').read_text())['mappings'],mapping)
    bulk=request(ES,f'/{INDEX}/_bulk','POST',(PROJECT/'data/f07/attractions.ndjson').read_bytes(),
                 content='application/x-ndjson',label=prefix+' bulk')
    require(not bulk['errors'] and len(bulk['items'])==12 and all(x['index']['result']=='created' for x in bulk['items']),bulk)
    refresh=request(ES,f'/{INDEX}/_refresh','POST',label=prefix+' refresh')
    require(refresh['_shards']['failed']==0,refresh)
    count=request(ES,f'/{INDEX}/_count',label=prefix+' count')
    require(count['count']==12 and count['_shards']['failed']==0,count)
    fixtures={x['attraction_id']:x for x in json.loads((PROJECT/'data/f07/attractions.json').read_text())}
    compared=[]
    for slug,ids in [('near',['a-hz-boundary','a-hz-tea','a-hz-xihu']),('budget-80',['a-hz-tea','a-hz-xihu']),('empty',[])]:
        dsl=json.loads((PROJECT/f'search/f07/{slug}.json').read_text())
        direct=request(ES,f'/{INDEX}/_search','POST',dsl,label=prefix+' REST '+slug)
        actual=request(APP,'/api/attractions/search','POST',input_for(slug),label=prefix+' Java '+slug)
        require(not direct['timed_out'] and direct['_shards']['failed']==0,direct)
        require(direct['hits']['total']=={'value':len(ids),'relation':'eq'},direct)
        require([h['_id'] for h in direct['hits']['hits']]==ids,direct)
        require(actual['total']==len(ids) and actual['totalRelation']=='eq',actual)
        require([x['id'] for x in actual['items']]==ids,actual)
        require(actual['conditions']==input_for(slug),actual)
        require(actual['esRequest']==dsl,{'Java DSL':actual['esRequest'],'REST DSL':dsl})
        for item in actual['items']:
            src=fixtures[item['id']]
            require(item['name']==src['name'] and item['cityCode']==src['city_code'] and
                    item['ticketPriceFen']==src['ticket_price_fen'] and item['currency']=='CNY' and item['status']=='open',item)
            require(item['score'] is not None and item['score']>=0,item)
        compared.append({'input':slug,'ids':ids,'total':actual['total'],'DTO':'verified','DSL':'exact parsed JSON match'})
    for body in [dict(input_for('near'),maxPriceFen=-1),dict(input_for('near'),q=' '),dict(input_for('near'),latitude=91),
                 dict(input_for('near'),radiusKm=0),dict(input_for('near'),maxPriceFen=1.5),dict(input_for('near'),cityCode='hz'),
                 {k:v for k,v in input_for('near').items() if k!='longitude'},b'{broken']:
        invalid=request(APP,'/api/attractions/search','POST',body,expected=400,label=prefix+' invalid input')
        require(invalid['code']=='INVALID_SEARCH_INPUT',invalid)
    before=request(APP,'/api/health',label=prefix+' health before stop')
    command(COMPOSE+['stop','es'])
    try:
        require(not probe(ES+'/'), 'ES must be stopped')
        alive=request(APP,'/api/health',label=prefix+' Java alive while ES stopped')
        require(alive==before and alive['scope']=='java-process-only',alive)
        down=request(APP,'/api/attractions/search','POST',input_for('near'),expected=503,label=prefix+' ES unavailable')
        require(down['code']=='SEARCH_UNAVAILABLE',down)
    finally:
        command(COMPOSE+['up','-d','es']);wait(ES+'/')
    health=request(ES,f'/_cluster/health/{INDEX}?wait_for_status=green&timeout=30s',label=prefix+' recovered index')
    require(not health['timed_out'] and health['status']=='green',health)
    recovered=request(APP,'/api/attractions/search','POST',input_for('near'),label=prefix+' same Java process recovery')
    require([x['id'] for x in recovered['items']]==['a-hz-boundary','a-hz-tea','a-hz-xihu'],recovered)
    deleted=request(ES,'/'+INDEX,'DELETE',label=prefix+' named cleanup')
    require(deleted['acknowledged'],deleted)
    request(ES,'/'+INDEX,expected=404,label=prefix+' cleanup verified')
    RECORD['rounds'].append({'round':number,'status':'passed','comparisons':compared,'invalid_input_cases':8,
        'failure':'ES stopped, Java health200 / search503','recovery':'same Java PID, same client, all three IDs',
        'cleanup':'only tut-f07-attractions deleted and 404 verified'})

def main():
    java=pathlib.Path(os.environ['JAVA_HOME'])/'bin/java'
    jar=PROJECT/'backend/target/travel-search-0.7.0.jar'
    require(jar.exists(),'Build the jar first')
    with socket.socket() as s: require(s.connect_ex(('127.0.0.1',18080))!=0,'Port 18080 occupied')
    command(COMPOSE+['up','-d','es']);wait(ES+'/')
    node=request(ES,'/',label='ES version')
    require(node['version']['number']=='9.4.0',node)
    request(ES,'/'+INDEX,expected=404,label='refuse existing index')
    RECORD['environment']={'java':subprocess.check_output([str(java),'-version'],stderr=subprocess.STDOUT,text=True),
        'platform':subprocess.check_output(['uname','-sm'],text=True),'docker':command(['docker','version','--format','{{.Server.Version}}']),
        'compose':command(['docker','compose','version','--short']),
        'image':json.loads(command(['docker','image','inspect','docker.elastic.co/elasticsearch/elasticsearch:9.4.0','--format','{{json .RepoDigests}}'])),
        'ES':node,'jar_sha256':sha(jar)}
    RECORD['inputs']={str(p.relative_to(ROOT)):sha(p) for folder in ['data/f07','search/f07','backend/src','labs/f07'] for p in (PROJECT/folder).rglob('*') if p.is_file()}
    process=None
    try:
        with (HERE/'java.log').open('w') as log:
            env=dict(os.environ,ES_URL=ES,ES_INDEX=INDEX,APP_PORT='18080')
            process=subprocess.Popen([str(java),'-jar',str(jar)],cwd=PROJECT,env=env,stdout=log,stderr=subprocess.STDOUT)
            RECORD['java_pid']=process.pid
            wait(APP+'/api/health')
            rejected=request(APP,'/api/attractions/search','POST',input_for('near'),expected=502,label='missing lesson index')
            require(rejected['code']=='SEARCH_BACKEND_REJECTED',rejected)
            for number in [1,2]:verify_round(number)
            RECORD['status']='passed'
    finally:
        if process:
            process.terminate()
            try:process.wait(timeout=20)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            require(not probe(APP+'/api/health'),'Java port closed after process shutdown')
            RECORD['shutdown']={'exit_code':process.returncode,'health_unreachable':True,'client_close':'Spring bean destroyMethod=close; ApiClient.close closes transport'}
        RECORD['final']={'lesson_index_exists':probe(ES+'/'+INDEX),'java_running':probe(APP+'/api/health'),'ES_running':probe(ES+'/'),'volume':'preserved'}
        (HERE/'es-java-review.json').write_text(json.dumps(RECORD,ensure_ascii=False,indent=2)+'\n')
    print('F07 real ES/Java: two clean rounds passed; same-process recovery and exact DSL/DTO checked')

if __name__=='__main__':
    try:main()
    except Exception as error:
        RECORD['status']='failed';RECORD['failure']=repr(error)
        (HERE/'es-java-review.json').write_text(json.dumps(RECORD,ensure_ascii=False,indent=2)+'\n')
        raise
