#!/usr/bin/env python3
"""Author-only actual F11 REST/Java verification, two create/clean rounds."""
import copy, datetime, hashlib, importlib.util, json, pathlib, traceback
H=pathlib.Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1]
spec=importlib.util.spec_from_file_location('f11lab',P/'labs/f11/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
C=lab.call;S=lab.search
report={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rounds':[],'scope':'F11 isolated resource only; real ES9.4.0 and Boot4/JDK25'}

def prepare():
 node=C('GET','/');assert node['version']['number']=='9.4.0' and node['version']['lucene_version']=='10.4.0'
 assert C('PUT','/tut-f11-attractions',lab.load('search/f11/index.json'))['acknowledged']
 health=C('GET','/_cluster/health/tut-f11-attractions?wait_for_status=green&timeout=30s');assert health['status']=='green' and not health['timed_out']
 bulk=C('POST','/tut-f11-attractions/_bulk',ndjson='data/f11/attractions.ndjson');assert not bulk['errors'] and len(bulk['items'])==16 and all(x['index']['result']=='created' for x in bulk['items'])
 assert C('POST','/tut-f11-attractions/_refresh')['_shards']['failed']==0
 assert C('GET','/tut-f11-attractions/_count')['count']==16
 mapping=C('GET','/tut-f11-attractions/_mapping')['tut-f11-attractions']['mappings'];assert mapping==lab.load('search/f11/index.json')['mappings']


def extra():
 inp=lab.load('search/f11/input-price.json')
 # Pagination state survives controlled writes and gives complete original documents.
 first=C('POST','/api/attractions/pages/start',inp,app=True);cur=first['cursor']
 try:
  for key,value in [('q','茶'),('cityCode','HZ'),('maxPriceFen',8000),('sortMode','distance'),('latitude',30.0),('longitude',120.0),('trackScores',True)]:
   changed=copy.deepcopy(inp);changed['search'][key]=value
   C('POST','/api/attractions/pages/next',{'cursor':cur,'afterPage':1,'conditions':changed},app=True,expected=409)
  changed=copy.deepcopy(inp);changed['pageSize']=2
  C('POST','/api/attractions/pages/next',{'cursor':cur,'afterPage':1,'conditions':changed},app=True,expected=409)
  moved=C('POST','/tut-f11-attractions/_bulk',ndjson='data/f11/move-prices.ndjson');assert not moved['errors']
  C('POST','/tut-f11-attractions/_refresh')
  second=C('POST','/api/attractions/pages/next',{'cursor':cur,'afterPage':1,'conditions':inp},app=True)
  C('POST','/api/attractions/pages/next',{'cursor':cur,'afterPage':1,'conditions':inp},app=True,expected=409)
  third=C('POST','/api/attractions/pages/next',{'cursor':cur,'afterPage':2,'conditions':inp},app=True)
  assert [i['id'] for p in [first,second,third] for i in p['items']]==lab.OLD
  assert third['items'][0]['ticketPriceFen']==8000
  new=C('POST','/api/attractions/pages/start',inp,app=True)
  assert [i['id'] for i in new['items']]==lab.NEW[:3] and new['items'][2]['ticketPriceFen']==500
  C('POST','/api/attractions/pages/close',{'cursor':new['cursor']},app=True)
 finally:
  C('POST','/api/attractions/pages/close',{'cursor':cur},app=True);lab.restore()
 # A real backend context release gives 410, not an automatic restart on a new view.
 first=C('POST','/api/attractions/pages/start',inp,app=True)
 C('DELETE','/_pit',{'id':first['esRequest']['pit']['id']})
 C('POST','/api/attractions/pages/next',{'cursor':first['cursor'],'afterPage':1,'conditions':inp},app=True,expected=410)
 # Five pages and exact-end detection; normal empty response.
 for pageSize,q,expected_lengths in [(2,'西湖',[2,2,2,2,1]),(3,'火星',[0])]:
  data=copy.deepcopy(inp);data['pageSize']=pageSize;data['search']['q']=q
  first=C('POST','/api/attractions/pages/start',data,app=True);current=first;pages=[]
  try:
   while True:
    pages.append(current)
    if not current['hasNext']:break
    current=C('POST','/api/attractions/pages/next',{'cursor':first['cursor'],'afterPage':current['pageNumber'],'conditions':data},app=True)
   assert [len(x['items']) for x in pages]==expected_lengths
   if q=='西湖':assert [i['id'] for x in pages for i in x['items']]==lab.OLD
   else:assert first['total']==0
  finally:C('POST','/api/attractions/pages/close',{'cursor':first['cursor']},app=True)
 for key,value in [('pageSize',0),('pageSize',6),('pageSize',1.5),('search',None)]:
  bad=copy.deepcopy(inp);bad[key]=value;C('POST','/api/attractions/pages/start',bad,app=True,expected=400)
 for key,value in [('q',''),('cityCode','XX'),('maxPriceFen',-1),('sortMode','unknown'),('latitude',91),('longitude',181),('trackScores',None)]:
  bad=copy.deepcopy(inp);bad['search'][key]=value;C('POST','/api/attractions/pages/start',bad,app=True,expected=400)
 # Explicit third key is mandatory; automatic append without it is observed separately.
 pit=C('POST','/tut-f11-attractions/_pit?keep_alive=1m&allow_partial_search_results=false')['id']
 body=lab.load('search/f11/page.json');body['pit']={'id':pit,'keep_alive':'1m'}
 result=S(body,True);pit=result.get('pit_id',pit);assert all(len(h['sort'])==3 for h in result['hits']['hits'])
 body=lab.load('search/f11/pit-page.json');body['pit']={'id':pit,'keep_alive':'1m'};body['from']=3;body['search_after']=result['hits']['hits'][-1]['sort'];S(body,True,expected=400)
 C('DELETE','/_pit',{'id':pit})

try:
 # Explicit deletion only of the lesson fixture left by the earlier exploratory execution.
 C('DELETE','/tut-f11-attractions')
 for name in ['initial','repeat-after-cleanup']:
  begin=len(lab.RECORD);C('GET','/tut-f11-attractions',expected=404)
  prepare();lab.offsets();lab.view();lab.java();extra()
  C('DELETE','/tut-f11-attractions');C('GET','/tut-f11-attractions',expected=404)
  C('POST','/api/attractions/pages/start',lab.load('search/f11/input-price.json'),app=True,expected=502)
  operations=lab.RECORD[begin:]
  (H/(name+'.json')).write_text(json.dumps({'round':name,'requests':len(operations),'operations':operations,'status':'passed'},ensure_ascii=False,indent=2)+'\n')
  report['rounds'].append({'round':name,'requests':len(operations),'status':'passed'})
 report['status']='passed'
except Exception:
 report['status']='failed';report['failure']=traceback.format_exc();raise
finally:
 report['sha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['data/f11','search/f11','labs/f11','backend/src'] for p in (P/folder).rglob('*') if p.is_file()}
 (H/'es-java-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 if report['status']=='failed':(H/'failed-operations.json').write_text(json.dumps(lab.RECORD,ensure_ascii=False,indent=2)+'\n')
