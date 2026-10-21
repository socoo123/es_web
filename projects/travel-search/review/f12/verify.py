#!/usr/bin/env python3
"""Author-only actual F12 verification. Isolated resources; two clean/recreate rounds."""
import concurrent.futures, copy, datetime, hashlib, importlib.util, json, pathlib, time, traceback
H=pathlib.Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
spec=importlib.util.spec_from_file_location('f12lab',P/'labs/f12/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
C=lab.call;B=lab.BASE
report={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rounds':[],
        'scope':'real ES9.4.0; Boot4/JDK25; controlled interleaving, no random concurrency or failover'}
def remove(index):
 try:C('GET','/'+index,expected=404)
 except RuntimeError:
  C('DELETE','/'+index);C('GET','/'+index,expected=404)

def extra():
 # Current mapping/settings and no-op semantics; GET realtime=false is not the realtime path.
 mapping=C('GET','/'+lab.INDEX+'/_mapping')[lab.INDEX]['mappings'];assert mapping==lab.load('search/f12/index.json')['mappings']
 settings=C('GET','/'+lab.INDEX+'/_settings')[lab.INDEX]['settings']['index'];assert settings['refresh_interval']=='-1'
 path='/'+lab.INDEX+'/_doc/d-hz-garden';update='/'+lab.INDEX+'/_update/d-hz-garden'
 before=C('GET',path)
 noop=C('POST',update,{'doc':{'ticket_price_fen':4500}});assert noop['result']=='noop' and noop['_seq_no']==before['_seq_no']
 C('POST',update,{'doc':{'ticket_price_fen':6000}})
 assert C('GET',path)['_source']['ticket_price_fen']==6000
 assert C('GET',path+'?realtime=false')['_source']['ticket_price_fen']==4500
 # refresh=true makes a changed field visible to a new search.
 C('POST',update+'?refresh=true',{'doc':{'ticket_price_fen':6200}})
 assert next(h['_source']['ticket_price_fen'] for h in lab.search()['hits']['hits'] if h['_id']=='d-hz-garden')==6200
 # wait_for does NOT trigger an immediate refresh with -1. Explicitly release it.
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
  pending=executor.submit(C,'POST',update+'?refresh=wait_for',{'doc':{'ticket_price_fen':6400}})
  try:
   deadline=time.monotonic()+8;observed=False
   while time.monotonic()<deadline:
    current=C('GET',path)
    if current['_source']['ticket_price_fen']==6400:observed=True;break
    time.sleep(.01)
   assert observed and not pending.done()
   assert next(h['_source']['ticket_price_fen'] for h in lab.search()['hits']['hits'] if h['_id']=='d-hz-garden')==6200
   lab.refresh();assert pending.result(timeout=5)['result']=='updated'
   assert next(h['_source']['ticket_price_fen'] for h in lab.search()['hits']['hits'] if h['_id']=='d-hz-garden')==6400
  finally:
   if not pending.done():lab.refresh()
 # Required version, integer units, non-empty patches, validated complete replacement and path ID.
 g=C('GET',B+'/d-hz-garden',app=True);v=lab.version(g)
 cases=[({},'empty'),(dict(v,ticketPriceFen=-1),'negative'),(dict(v,ticketPriceFen=1.5),'fractional'),
        (dict(v,status='bad'),'bad-status'),({'ticketPriceFen':7000},'missing-version'),
        (dict(v,seqNo=-1,ticketPriceFen=7000),'negative-seq'),(dict(v,primaryTerm=0,status='closed'),'zero-term')]
 for body,label in cases:
  assert C('PATCH',B+'/d-hz-garden',body,app=True,expected=400)['code']=='INVALID_CHANGE_INPUT'
 C('PUT',B+'/d-hz-garden',dict(v,document={'ticket_price_fen':12}),app=True,expected=400)
 doc=lab.load('search/f12/new-document.json')
 assert C('POST',B+'/other-id/create',doc,app=True,expected=400)['code']=='DOCUMENT_ID_MISMATCH'
 C('GET',B+'/INVALID',app=True,expected=400)
 assert C('PATCH',B+'/no-such-id',dict(v,status='closed'),app=True,expected=404)['code']=='DOCUMENT_MISSING'
 # Local pagination error mapping is retained for the separate F12 session map.
 inp=lab.load('search/f12/input.json');p=lab.start(inp)
 changed=copy.deepcopy(inp);changed['search']['maxPriceFen']=7000
 C('POST',B+'/pages/next',{'cursor':p['cursor'],'afterPage':1,'conditions':changed},app=True,expected=409)
 lab.close(p)
 C('POST',B+'/pages/next',{'cursor':p['cursor'],'afterPage':1,'conditions':inp},app=True,expected=410)
 # Independent graduation material: two readers, old version rejected, fresh field-only merge.
 path=B+'/g-hz-garden'
 a=C('GET',path,app=True,graduation=True);b=C('GET',path,app=True,graduation=True)
 C('PATCH',path,dict(lab.version(a),ticketPriceFen=7200),app=True,graduation=True)
 C('PATCH',path,dict(lab.version(b),status='closed'),app=True,graduation=True,expected=409)
 fresh=C('GET',path,app=True,graduation=True);assert fresh['document']['ticket_price_fen']==7200 and fresh['document']['status']=='open'
 C('PATCH',path,dict(lab.version(fresh),status='closed'),app=True,graduation=True)
 final=C('GET',path,app=True,graduation=True);assert final['document']['ticket_price_fen']==7200 and final['document']['status']=='closed'
 # No PIT resources left by the completed cases, before deleting the two exact indices.
 for index in [lab.INDEX,lab.GRAD]:
  assert C('GET',f'/{index}/_stats/search')['indices'][index]['total']['search']['open_contexts']==0

try:
 for index in [lab.INDEX,lab.GRAD]:remove(index)
 for name in ['initial','repeat-after-cleanup']:
  begin=len(lab.RECORD)
  cases=[]
  for label,fn in [('prepare',lab.prepare),('crud',lab.crud),('conflict',lab.conflict),('java',lab.java),('graduation',lab.graduation)]:
   start=len(lab.RECORD);fn();cases.append({'case':label,'requests':len(lab.RECORD)-start,'status':'passed'})
  assert sum(c['requests'] for c in cases)==114
  extra()
  for index in [lab.INDEX,lab.GRAD]:C('DELETE','/'+index);C('GET','/'+index,expected=404)
  C('GET',B+'/d-hz-garden',app=True,expected=502)
  C('POST',B+'/pages/start',lab.load('search/f12/input.json'),app=True,expected=502)
  operations=lab.RECORD[begin:]
  (H/(name+'.json')).write_text(json.dumps({'round':name,'status':'passed','cases':cases,'requests':len(operations),'operations':operations},ensure_ascii=False,indent=2)+'\n')
  report['rounds'].append({'round':name,'status':'passed','cases':cases,'requests':len(operations)})
 report['status']='passed'
except Exception:
 report['status']='failed';report['failure']=traceback.format_exc();raise
finally:
 report['sha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['data/f12','search/f12','labs/f12','backend/src'] for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p)}
 (H/'es-java-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 if report['status']=='failed':(H/'failed-operations.json').write_text(json.dumps(lab.RECORD,ensure_ascii=False,indent=2)+'\n')
