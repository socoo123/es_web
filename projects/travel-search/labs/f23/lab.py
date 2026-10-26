#!/usr/bin/env python3
"""F23 real REST/Java lab: root boundaries, projection counts and update scope."""
import argparse,copy,datetime,json,os,pathlib,urllib.request,urllib.error
HERE=pathlib.Path(__file__).resolve().parent;PROJECT=HERE.parents[1]
DATA=PROJECT/'data/f23';SEARCH=PROJECT/'search/f23'
ES=os.environ.get('ES_URL','http://127.0.0.1:19223').rstrip('/')
APP=os.environ.get('APP_URL','http://127.0.0.1:18081').rstrip('/')
MODELS=['hotels','object','nested','offers'];LOG=None;COUNT=0

def require(ok,detail):
 if not ok:raise AssertionError(detail)
def read(path):return json.loads(path.read_text())
def idx(m):return 'tut-f23-'+m
def normalize_mapping(x):
 if isinstance(x,list):return [normalize_mapping(v) for v in x]
 if isinstance(x,dict):return {k:normalize_mapping(v) for k,v in x.items() if not (k=='type' and v=='object')}
 return x
def request(method,path,body=None,status=200,app=False,label=''):
 global COUNT
 raw=body.encode() if isinstance(body,str) else json.dumps(body,ensure_ascii=False).encode() if body is not None else None
 url=(APP if app else ES)+path
 req=urllib.request.Request(url,data=raw,method=method,headers={'Content-Type':'application/x-ndjson' if '_bulk' in path else 'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=40) as res:actual=res.status;payload=res.read().decode()
 except urllib.error.HTTPError as e:actual=e.code;payload=e.read().decode()
 out=json.loads(payload);COUNT+=1
 if LOG:
  with LOG.open('a') as f:f.write(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),n=COUNT,label=label,method=method,url=url,request=body,status=actual,response=out),ensure_ascii=False)+'\n')
 require(actual in (status if isinstance(status,list) else [status]),dict(path=path,expected=status,actual=actual,response=out))
 return out

def search(m,body):
 out=request('POST','/'+idx(m)+'/_search',body)
 require(not out['timed_out'] and out['_shards']['failed']==0 and out['hits']['total']['relation']=='eq','complete search')
 return out

def ids(r):return [h['_id'] for h in r['hits']['hits']]
def doc(m,i):return request('GET','/'+idx(m)+'/_doc/'+i)
def all_docs(m):
 rows=read(DATA/(m+'.json'));key='offer_id' if m=='offers' else 'hotel_id'
 out=request('POST','/'+idx(m)+'/_mget',{'ids':[r[key] for r in rows]})
 require(all(r.get('found') for r in out['docs']),'all found')
 return {r['_id']:r for r in out['docs']}

def prepare():
 v=request('GET','/');require(v['version']['number']=='9.4.0' and v['version']['lucene_version']=='10.4.0','version')
 p=request('GET','/_nodes/plugins');require(all(not n['plugins'] for n in p['nodes'].values()),'plugins')
 summary={}
 for m in MODELS:
  require(request('PUT','/'+idx(m),read(SEARCH/(m+'-index.json')))['acknowledged'],'create')
  h=request('GET','/_cluster/health/'+idx(m)+'?wait_for_status=green&timeout=30s');require(h['status']=='green' and not h['timed_out'] and h['number_of_nodes']==1,'health')
  rows=read(DATA/(m+'.json'));b=request('POST','/'+idx(m)+'/_bulk',(DATA/(m+'.ndjson')).read_text());require(not b['errors'] and len(b['items'])==len(rows) and all(x['create']['result']=='created' for x in b['items']),'all created')
  request('POST','/'+idx(m)+'/_refresh')
  c=request('GET','/'+idx(m)+'/_count')['count'];require(c==len(rows),'root count')
  mapping=request('GET','/'+idx(m)+'/_mapping')[idx(m)]['mappings'];require(normalize_mapping(mapping)==normalize_mapping(read(SEARCH/(m+'-index.json'))['mappings']),'mapping; only explicit object type is omitted by server')
  settings=request('GET','/'+idx(m)+'/_settings')[idx(m)]['settings']['index'];require(settings['number_of_shards']=='1' and settings['number_of_replicas']=='0' and settings['refresh_interval']=='-1','settings')
  stats=request('GET','/'+idx(m)+'/_stats/docs')['_all']['primaries']['docs'];live=8 if m in ['nested','offers'] else 3;require(stats['count']==live,'live docs')
  saved=all_docs(m);key='offer_id' if m=='offers' else 'hotel_id'
  require(all(saved[r[key]]['_source']==r for r in rows),'exact source')
  summary[m]={'roots':c,'lucene_live':stats['count'],'deleted_observed':stats['deleted'],'source_docs':len(saved)}
 return {'status':'passed','projections':summary,'http':COUNT}

def lookup():
 out={}
 for m in ['hotels','object','nested']:
  r=search(m,read(SEARCH/'hotel.json'));require(ids(r)==['h01'],'hotel hit')
  out[m]={'ids':ids(r),'has_rooms':'rooms' in r['hits']['hits'][0]['_source']}
 r=search('object',read(SEARCH/'room-object.json'));require(ids(r)==['h01'],'object single room id')
 out['object_room']=ids(r)
 r=search('nested',read(SEARCH/'room-object.json'));require(ids(r)==[],'nested direct root scope no match')
 out['nested_wrong_scope']=ids(r)
 r=search('nested',read(SEARCH/'room-nested.json'));require(ids(r)==['h01'],'nested returns root')
 require(len(r['hits']['hits'][0]['_source']['rooms'])==2,'source contains all rooms, not automatic selection')
 out['nested_room']=ids(r)
 r=request('GET','/'+idx('nested')+'/_doc/r101',status=404);require(not r['found'],'nested is not addressable root')
 r=doc('offers','o101');require(r['_source']['room_id']=='r101' and r['_source']['rate_plan_id']=='bf-flex','own offer root')
 r=search('offers',read(SEARCH/'offers-flex.json'));require(ids(r)==['o101','o201'],'all constraints belong to each offer')
 out['flex']={'offer_ids':ids(r),'hotel_ids':[h['_source']['hotel_id'] for h in r['hits']['hits']]}
 r=search('offers',read(SEARCH/'offers-budget.json'));require(ids(r)==['o102','o104','o203'],'budget offers')
 out['budget']={'offer_ids':ids(r),'hotel_ids':[h['_source']['hotel_id'] for h in r['hits']['hits']],'offer_total':r['hits']['total']['value'],'distinct_hotels_in_this_full_small_result':len(set(h['_source']['hotel_id'] for h in r['hits']['hits']))}
 # Controlled wrong query: removing one condition exposes a concrete boundary, then restore.
 canonical=read(SEARCH/'offers-flex.json')
 for field,expected in [('currency',['o101','o103','o201']),('offer_status',['o101','o201','o202']),('hotel_status',['o101','o201','o301'])]:
  q=copy.deepcopy(canonical);q['query']['bool']['filter']=[f for f in q['query']['bool']['filter'] if not ('term' in f and field in f['term'])]
  r=search('offers',q);require(ids(r)==expected,field+' omission')
  out['omit_'+field]=ids(r)
 r=search('offers',canonical);require(ids(r)==['o101','o201'],'restored qualifications')
 return {'status':'passed','observations':out,'http':COUNT}

def updates():
 before_nested=all_docs('nested');before_offer=all_docs('offers')
 seg_before=request('GET','/'+idx('nested')+'/_segments')
 old=before_nested['h01'];params='?if_seq_no='+str(old['_seq_no'])+'&if_primary_term='+str(old['_primary_term'])
 r=request('POST','/'+idx('nested')+'/_update/h01'+params,read(SEARCH/'update-nested-price.json'));require(r['result']=='updated' and r['_version']==old['_version']+1,'nested root updated')
 request('POST','/'+idx('nested')+'/_refresh')
 after_nested=all_docs('nested');expected=copy.deepcopy(old['_source']);expected['rooms'][0]['rates'][0]['price_minor']=63000
 require(after_nested['h01']['_source']==expected,'only selected rate value changes in root source')
 require(all(after_nested[i]['_source']==before_nested[i]['_source'] and after_nested[i]['_version']==before_nested[i]['_version'] for i in ['h02','h03']),'other hotels untouched')
 seg_after=request('GET','/'+idx('nested')+'/_segments')
 stat=request('GET','/'+idx('nested')+'/_stats/docs')['_all']['primaries']['docs'];require(stat['count']==8,'nested live stays8')
 request('POST','/'+idx('nested')+'/_update/h01'+params,read(SEARCH/'update-nested-price.json'),status=409)
 request('POST','/'+idx('nested')+'/_update/r101',{'doc':{'room_name':'not-a-root'}},status=404)
 r=request('POST','/'+idx('offers')+'/_update/o101',read(SEARCH/'update-offer-price.json'));require(r['result']=='updated','one offer update')
 request('POST','/'+idx('offers')+'/_refresh');after_offer=all_docs('offers')
 changed=[i for i in before_offer if after_offer[i]['_version']!=before_offer[i]['_version']];require(changed==['o101'],'one root changed')
 require(after_offer['o101']['_source']==dict(before_offer['o101']['_source'],price_minor=63000),'offer content')
 require(all(after_offer[i]['_source']==before_offer[i]['_source'] for i in before_offer if i!='o101'),'other offers untouched')
 # Duplication recovery: changing catalog does not propagate to copied hotel fields.
 request('POST','/'+idx('hotels')+'/_update/h01',read(SEARCH/'rename-hotel.json'))
 r=doc('offers','o101');require(r['_source']['hotel_name']=='西湖湖畔酒店','no implicit join propagation')
 r=request('POST','/'+idx('offers')+'/_update_by_query?refresh=true&conflicts=abort',read(SEARCH/'rename-offers.json'))
 require(not r['timed_out'] and not r['failures'] and r['updated']==4 and r['version_conflicts']==0,'rename fanout4')
 renamed=all_docs('offers');require(all(x['_source']['hotel_name']=='西湖湖畔酒店·新名' for x in renamed.values() if x['_source']['hotel_id']=='h01'),'all four copies')
 # Restore exact canonical source and explicit refresh; first vs repeated is intentionally different.
 restore=read(SEARCH/'update-nested-price.json');restore['script']['params']['price']=60000
 request('POST','/'+idx('nested')+'/_update/h01',restore)
 request('POST','/'+idx('offers')+'/_update/o101',read(SEARCH/'restore-offer-price.json'))
 request('POST','/'+idx('offers')+'/_refresh') # update_by_query must see the new version with refresh=-1
 request('POST','/'+idx('hotels')+'/_update/h01',{'doc':{'hotel_name':'西湖湖畔酒店'}})
 restore=read(SEARCH/'rename-offers.json');restore['script']['params']['name']='西湖湖畔酒店'
 r=request('POST','/'+idx('offers')+'/_update_by_query?refresh=true&conflicts=abort',restore);require(r['updated']==4 and not r['failures'],'restore copies')
 for m in ['hotels','nested','offers']:
  request('POST','/'+idx(m)+'/_refresh');saved=all_docs(m);key='offer_id' if m=='offers' else 'hotel_id';require(all(saved[x[key]]['_source']==x for x in read(DATA/(m+'.json'))),'canonical restored')
 return {'status':'passed','nested_roots_changed':['h01'],'nested_live_after':stat['count'],'nested_deleted_observed':stat['deleted'],'nested_h01_lucene_block_size':3,'segments_before':seg_before,'segments_after':seg_after,'offer_roots_changed':changed,'hotel_name_copy_updates':4,'canonical_restored':True,'http':COUNT,'interpretation':'source and root versions observed; block rewrite backed by fixed source; deleted count is merge-dependent, not durable counter; no latency/throughput claim'}

def java():
 reports=[]
 for mode in ['hotel','object','nested','offers-flex','offers-budget']:
  input={'mode':mode};r=request('POST','/api/model/inspect',input,app=True)
  raw=search(r['model'],r['esRequest'])
  # Official typed response serialization omits only these null scoring fields.
  replay=copy.deepcopy(raw['hits'])
  if replay.get('max_score') is None:replay.pop('max_score',None)
  for hit in replay['hits']:
   if hit.get('_score') is None:hit.pop('_score',None)
  require(replay==r['esResponse']['hits'],'Java actual DSL replay; source/index/ID/sort/total unchanged')
  expected={'hotel':['h01'],'object':['h01'],'nested':['h01'],'offers-flex':['o101','o201'],'offers-budget':['o102','o104','o203']}[mode]
  require([c['id'] for c in r['items']]==expected and r['total']==len(expected),'Java ID/total')
  require([c['source'] for c in r['items']]==[h['_source'] for h in raw['hits']['hits']],'Java projection exact source')
  reports.append({'mode':mode,'ids':expected,'total':r['total'],'model':r['model'],'dsl':r['esRequest']})
 return {'status':'passed','reports':reports,'http':COUNT,'java_internal_es_searches':5}

def errors():
 for m in MODELS:
  request('PUT','/'+idx(m),read(SEARCH/(m+'-index.json')),status=400)
  r=request('POST','/'+idx(m)+'/_bulk',(DATA/(m+'.ndjson')).read_text());require(r['errors'] and all(i['create']['status']==409 for i in r['items']),'repeat creates409')
 # Bad mapping/type requests do not add documents.
 request('PUT','/'+idx('offers')+'/_doc/bad',dict(read(DATA/'offers.json')[0],price_minor='not-an-integer'),status=400)
 request('PUT','/'+idx('offers')+'/_doc/bad',dict(read(DATA/'offers.json')[0],unknown='strict'),status=400)
 for invalid in [{},{'mode':None},{'mode':'all'},{'mode':'../nested'},{'mode':1}]:
  request('POST','/api/model/inspect',invalid,status=400,app=True)
 for m in MODELS:
  require(request('GET','/'+idx(m)+'/_count')['count']==len(read(DATA/(m+'.json'))),'failed writes not added')
 return {'status':'passed','http':COUNT}

def cleanup():
 for m in MODELS:
  request('DELETE','/'+idx(m),status=[200,404])
  request('GET','/'+idx(m),status=404)
 return {'status':'passed','deleted_only':[idx(m) for m in MODELS],'http':COUNT}

def main():
 global LOG
 p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','lookup','updates','java','errors','cleanup']);p.add_argument('--out',default=os.environ.get('F23_OUT',str(PROJECT/'review/f23/latest')));a=p.parse_args()
 out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True);LOG=out/(a.command+'.jsonl');require(not LOG.exists(),'new output directory or remove only own previous log explicitly')
 r=globals()[a.command]();r['at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/(a.command+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'command':a.command,'http':COUNT,'status':'passed'},ensure_ascii=False))
if __name__=='__main__':main()
