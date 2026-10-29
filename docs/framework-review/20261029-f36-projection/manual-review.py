#!/usr/bin/env python3
"""Independently execute the published reader shell/psql path, after formal rounds."""
import datetime, gzip, json, os, pathlib, subprocess, time, urllib.error, urllib.request
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search'
O=P/'review/f36/manual';O.mkdir(exist_ok=False);W=O/'work';rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[],'checks':[]}
log=(O/'commands.log').open('w');app=None;snapshot=None
def cmd(args,data=None):
    r=subprocess.run(args,cwd=P,text=True,input=data,capture_output=True,timeout=120)
    rec['commands'].append({'args':args,'returncode':r.returncode})
    log.write(json.dumps(args,ensure_ascii=False)+'\n'+r.stdout+r.stderr+'\n');log.flush()
    assert r.returncode==0,(args,r.stderr)
    return r.stdout
def req(path,body=None,expected=200,app=False):
    base='http://127.0.0.1:'+('18086' if app else '20036')
    request=urllib.request.Request(base+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=20) as r:status,value=r.status,json.load(r)
    except urllib.error.HTTPError as e:status,value=e.code,json.load(e)
    assert status==expected,(path,status,value)
    rec['checks'].append({'path':path,'app':app,'status':status,'response':value});return value
def all_docs():
    r=req('/tut-f36-attractions-read/_search',{'size':20,'query':{'match_all':{}},'sort':[{'attraction_id':'asc'}]})
    return {h['_id']:h['_source'] for h in r['hits']['hits']}
def prices(docs):return [(id,d['ticket_price_fen']) for id,d in docs.items()]
try:
    cmd(['python3','labs/f36/lab.py','cleanup','--out',str(O/'cleanup-before')])
    text=cmd(['bash','labs/f36/requests.sh','prepare',str(W)]);assert '"errors":false' in text
    initial=all_docs();assert prices(initial)==[('p01',6000),('p02',0)]
    text=cmd(['bash','labs/f36/java.sh',str(W/'initial.ndjson')]);assert 'index p01 200 updated' in text
    cmd(['bash','labs/f36/requests.sh','refresh'])
    cmd(['bash','labs/f36/requests.sh','related',str(W)])
    assert all_docs()==initial
    cmd(['bash','labs/f36/java.sh',str(W/'related.ndjson')]);cmd(['bash','labs/f36/requests.sh','refresh'])
    related=all_docs();assert all(d['city_name']=='杭州（旅游展示名）' for d in related.values()) and related['p01']['tags']==['亲子']
    psql=['docker','compose','-f','infra/f36/compose.yaml','exec','-T','postgres','psql','-X','-qAt','-v','ON_ERROR_STOP=1','-U','travel','-d','travel_f36']
    snapshot=subprocess.Popen(psql,cwd=P,text=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    snapshot.stdin.write('\\i /lesson/snapshot-begin.sql\n\\echo F36_READY\n');snapshot.stdin.flush();first=[]
    while True:
        line=snapshot.stdout.readline();assert line!='','snapshot ended'
        if line.strip()=='F36_READY':break
        first.append(line)
    assert 'repeatable read|2' in ''.join(first)
    cmd(['bash','labs/f36/requests.sh','change'])
    tail,err=snapshot.communicate('\\i /lesson/snapshot-end.sql\n\\q\n',timeout=30);assert snapshot.returncode==0,err
    for name in ['snapshot','snapshot-again']:
        cmd(['docker','compose','-f','infra/f36/compose.yaml','cp',f'postgres:/tmp/f36-{name}.ndjson',str(W/(name+'.ndjson'))])
    cmd(['cmp',str(W/'snapshot.ndjson'),str(W/'snapshot-again.ndjson')])
    rec['snapshot']={'first_stdout':''.join(first),'end_stdout':tail,'identical_files':True}
    bulk=cmd(['python3','labs/f36/to-bulk.py',str(W/'snapshot.ndjson')]);(W/'snapshot.bulk.ndjson').write_text(bulk)
    text=cmd(['curl','--fail-with-body','-sS','-X','POST','http://127.0.0.1:20036/tut-f36-attractions-write/_bulk?require_alias=true',
        '-H','Content-Type: application/x-ndjson','--data-binary','@'+str(W/'snapshot.bulk.ndjson')]);assert json.loads(text)['errors'] is False
    cmd(['bash','labs/f36/requests.sh','refresh']);assert all_docs()==related
    logapp=(O/'application.log').open('w');env=os.environ.copy();env.update(ES_URL='http://127.0.0.1:20036',ES_INDEX='tut-f36-attractions-read',ES_CA_FILE='',ES_API_KEY_FILE='',APP_PORT='18086')
    app=subprocess.Popen(['java','-Xms64m','-Xmx192m','-jar','backend/target/travel-search-0.7.0.jar'],cwd=P,env=env,stdout=logapp,stderr=subprocess.STDOUT)
    for _ in range(60):
        try:urllib.request.urlopen('http://127.0.0.1:18086/',timeout=1).close();break
        except OSError:assert app.poll() is None;time.sleep(1)
    body=json.loads((P/'search/f36/search.json').read_text())
    before=req('/api/attractions/search',body,app=True);assert [(r['id'],r['ticketPriceFen']) for r in before['items']]==[('p01',6000),('p02',0)]
    cmd(['bash','labs/f36/requests.sh','delta',str(W)])
    text=cmd(['bash','labs/f36/java.sh',str(W/'delta.ndjson')]);assert 'delete p02 200 deleted' in text and 'index p03 201 created' in text
    assert req('/tut-f36-attractions-read/_doc/p01')['_source']['ticket_price_fen']==6500
    req('/tut-f36-attractions-read/_doc/p02',expected=404);assert all_docs()==related
    old=req('/api/attractions/search',body,app=True);assert [(r['id'],r['ticketPriceFen']) for r in old['items']]==[('p01',6000),('p02',0)]
    cmd(['bash','labs/f36/requests.sh','refresh']);final=all_docs();assert prices(final)==[('p01',6500),('p03',3000)]
    after=req('/api/attractions/search',body,app=True);assert [(r['id'],r['ticketPriceFen']) for r in after['items']]==[('p01',6500),('p03',3000)]
    # Exercise the documented missing-delete branch through the same official-client importer.
    text=cmd(['bash','labs/f36/java.sh',str(W/'delta.ndjson')]);assert 'delete p02 404 not_found' in text
    cmd(['bash','labs/f36/requests.sh','refresh']);assert all_docs()==final
    rec['missing_delete_404_without_error_accepted']=True;rec['passed']=True
finally:
    if snapshot and snapshot.poll() is None:snapshot.kill();snapshot.wait()
    if app:
        app.terminate();app.wait(timeout=20);logapp.close()
        with gzip.open(O/'application.log.gz','wb') as f:f.write((O/'application.log').read_bytes())
        (O/'application.log').unlink()
    log.close()
    with gzip.open(O/'commands.log.gz','wb') as f:f.write((O/'commands.log').read_bytes())
    (O/'commands.log').unlink()
    (O/'summary.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print('F36 published manual SQL/curl/Java path passed')
