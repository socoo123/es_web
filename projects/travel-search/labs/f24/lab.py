#!/usr/bin/env python3
"""F24: actual HTTP receipts and independent fixed-snapshot qualification oracle."""
import argparse,copy,datetime,json,os,pathlib,urllib.request,urllib.error
HERE=pathlib.Path(__file__).resolve().parent;PROJECT=HERE.parents[1];DATA=PROJECT/'data/f24';SEARCH=PROJECT/'search/f24'
ES=os.environ.get('ES_URL','http://127.0.0.1:19224').rstrip('/');APP=os.environ.get('APP_URL','http://127.0.0.1:18081').rstrip('/')
LOG=None;COUNT=0;MODES=['object','split','matched','unfiltered-sort','filtered-sort']
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def read(p):return json.loads(p.read_text())
def idx(m):return 'tut-f24-'+m
def request(method,path,body=None,status=200,app=False):
 global COUNT
 raw=body.encode() if isinstance(body,str) else json.dumps(body,ensure_ascii=False).encode() if body is not None else None
 url=(APP if app else ES)+path;req=urllib.request.Request(url,data=raw,method=method,headers={'Content-Type':'application/x-ndjson' if '_bulk' in path else 'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=45) as r:actual=r.status;payload=r.read().decode()
 except urllib.error.HTTPError as e:actual=e.code;payload=e.read().decode()
 out=json.loads(payload);COUNT+=1
 if LOG:
  with LOG.open('a') as f:f.write(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),n=COUNT,method=method,url=url,request=body,status=actual,response=out),ensure_ascii=False)+'\n')
 require(actual in (status if isinstance(status,list) else [status]),dict(path=path,expected=status,actual=actual,response=out));return out
def search(model,body):
 r=request('POST','/'+idx(model)+'/_search',body);require(not r['timed_out'] and r['_shards']['failed']==0 and r['hits']['total']['relation']=='eq','complete search');return r
def runmode(mode):return search('object' if mode=='object' else 'nested',read(SEARCH/(mode+'.json')))
def ids(r):return [h['_id'] for h in r['hits']['hits']]
def oracle():
 out={}
 for h in read(DATA/'hotels.json'):
  if h['city_code']!='HZ' or h['hotel_status']!='open':continue
  rows=[r for r in h['rooms'] if all(r.get(k)==v for k,v in dict(bed_type='twin',meal='breakfast',cancellation='flexible',rate_plan_id='bf-flex',currency='CNY',offer_status='active',service_date='2026-11-01').items()) and r['capacity']>=2 and isinstance(r.get('price_minor'),int) and 0<=r['price_minor']<=70000]
  if rows:out[h['hotel_id']]=sorted(rows,key=lambda r:(r['price_minor'],r['offer_id']))
 return out
def normalize(x):
 if isinstance(x,list):return [normalize(v) for v in x]
 if isinstance(x,dict):return {k:normalize(v) for k,v in x.items() if not (k in ['_score','max_score'] and v is None)}
 return x
def mapping_normalize(x):
 if isinstance(x,list):return [mapping_normalize(v) for v in x]
 if isinstance(x,dict):return {k:mapping_normalize(v) for k,v in x.items() if not (k=='type' and v=='object')}
 return x
def verify_match(r,expected,sorted_price=False,full=False):
 require(ids(r)==expected,dict(expected=expected,actual=ids(r)));o=oracle()
 for hit in r['hits']['hits']:
  expected_rows=o[hit['_id']];inner=hit['inner_hits']['eligible']['hits'];require(inner['total']=={'value':len(expected_rows),'relation':'eq'},'inner total')
  rows=[h['_source'] for h in inner['hits']];require(rows==(expected_rows if full else expected_rows[:1]),'inner exact eligible source and order')
  for ih in inner['hits']:
   require(ih['_nested']['field']=='rooms' and ih['_source']==hit['_source']['rooms'][ih['_nested']['offset']],'offset points to original source, not rank')
  require(hit['_source']==next(h for h in read(DATA/'hotels.json') if h['hotel_id']==hit['_id']),'root full source unchanged')
  if sorted_price:require(hit['sort']==[expected_rows[0]['price_minor'],hit['_id']],'eligible min and stable hotel ID')
 return {'ids':ids(r),'prices':[h['sort'][0] for h in r['hits']['hits']] if sorted_price else None,'inner_total':{h['_id']:h['inner_hits']['eligible']['hits']['total']['value'] for h in r['hits']['hits']}}
def prepare():
 v=request('GET','/');require(v['version']['number']=='9.4.0' and v['version']['lucene_version']=='10.4.0','version')
 p=request('GET','/_nodes/plugins');require(all(not n['plugins'] for n in p['nodes'].values()),'plugins');result={}
 for m in ['object','nested']:
  mapping=read(SEARCH/(m+'-index.json'));request('PUT','/'+idx(m),mapping)
  h=request('GET','/_cluster/health/'+idx(m)+'?wait_for_status=green&timeout=30s');require(h['status']=='green' and not h['timed_out'] and h['number_of_nodes']==1,'health')
  b=request('POST','/'+idx(m)+'/_bulk',(DATA/'hotels.ndjson').read_text());require(not b['errors'] and len(b['items'])==9 and all(i['create']['result']=='created' for i in b['items']),'bulk9')
  request('POST','/'+idx(m)+'/_refresh');require(request('GET','/'+idx(m)+'/_count')['count']==9,'roots9')
  actual=request('GET','/'+idx(m)+'/_mapping')[idx(m)]['mappings'];require(mapping_normalize(actual)==mapping_normalize(mapping['mappings']),'exact mapping except omitted object type')
  s=request('GET','/'+idx(m)+'/_settings')[idx(m)]['settings']['index'];require(s['number_of_shards']=='1' and s['number_of_replicas']=='0' and s['refresh_interval']=='-1','settings')
  stats=request('GET','/'+idx(m)+'/_stats/docs')['_all']['primaries']['docs'];require(stats['count']==(9 if m=='object' else 25),'Lucene live')
  rows=read(DATA/'hotels.json');docs=request('POST','/'+idx(m)+'/_mget',{'ids':[h['hotel_id'] for h in rows]})['docs'];require(all(d['found'] and d['_source']==h for d,h in zip(docs,rows)),'all source exact')
  result[m]={'roots':9,'lucene_live':stats['count'],'source_docs_checked':9}
 return {'projections':result,'oracle_matching_offers':{k:[r['offer_id'] for r in v] for k,v in oracle().items()}}
def matching():
 out={};contract=read(DATA/'contract.json')
 for mode in ['object','split']:
  r=runmode(mode);require(ids(r)==contract['expected'][mode],mode+' false positives');out[mode]=ids(r)
 r=runmode('matched');out['matched']=verify_match(r,['h02','h03','h08'])
 q=read(SEARCH/'object.json');r=search('nested',q);require(ids(r)==[],'nested fields not root searchable')
 request('POST','/'+idx('object')+'/_search',read(SEARCH/'matched.json'),status=400)
 q=read(SEARCH/'matched.json');q['query']['bool']['filter'][2]['nested']['path']='missing';request('POST','/'+idx('nested')+'/_search',q,status=400)
 for field,expected in [('rooms.capacity',['h02','h03','h05','h08']),('rooms.cancellation',['h02','h03','h08','h09']),('rooms.currency',['h02','h03','h07','h08'])]:
  q=read(SEARCH/'matched.json');fs=q['query']['bool']['filter'][2]['nested']['query']['bool']['filter'];fs[:]=[a for a in fs if field not in a.get('term',{}) and field not in a.get('range',{})]
  r=search('nested',q);require(ids(r)==expected,'omitted '+field);out['omit_'+field]=ids(r)
 out['restored']=verify_match(runmode('matched'),['h02','h03','h08']);return out
def sorting():
 out={};r=runmode('unfiltered-sort');require(ids(r)==['h02','h03','h08'] and [h['sort'][0] for h in r['hits']['hits']]==[10000,50000,50000],'unqualified cheap room incorrectly sorts h02 first')
 verify_match(r,['h02','h03','h08']);out['unfiltered']={'ids':ids(r),'prices':[h['sort'][0] for h in r['hits']['hits']]}
 r=runmode('filtered-sort');out['filtered']=verify_match(r,['h03','h08','h02'],True)
 q=read(SEARCH/'filtered-sort.json');q['query']['bool']['filter'][2]['nested']['inner_hits']['size']=10;r=search('nested',q);out['all_inner']=verify_match(r,['h03','h08','h02'],True,True)
 q=read(SEARCH/'filtered-sort.json');q['query']['bool']['filter'][2]['nested']['inner_hits']['sort'][0]['rooms.price_minor']['order']='desc';r=search('nested',q)
 h=r['hits']['hits'][0];require(h['_id']=='h03' and h['sort'][0]==50000 and h['inner_hits']['eligible']['hits']['hits'][0]['_source']['offer_id']=='o302','inner sort independent from hotel min');out['changed_inner']={'hotel_min':50000,'displayed_offer':'o302','displayed_price':55000}
 q=read(SEARCH/'filtered-sort.json');q['sort'][0]['rooms.price_minor']['nested']['filter']={'range':{'rooms.price_minor':{'gte':900000}}};r=search('nested',q);require(ids(r)==['h02','h03','h08'] and all(h['sort'][0]==2147483647 for h in r['hits']['hits']),'sort filter does not filter root, missing last');out['empty_sort_eligible']=ids(r)
 out['restored']=verify_match(runmode('filtered-sort'),['h03','h08','h02'],True);return out
def java():
 out=[];c=read(DATA/'contract.json')
 for mode in MODES:
  r=request('POST','/api/nested/inspect',{'mode':mode},app=True);actual=search(r['model'],r['esRequest']);require(normalize(actual['hits'])==r['esResponse']['hits'],'Java actual DSL replay only scoring null omission')
  require(r['esRequest']==read(SEARCH/(mode+'.json')),'full canonical REST DSL equals Java builder DSL')
  require([i['id'] for i in r['items']]==c['expected'][mode] and r['total']==len(c['expected'][mode]),'Java IDs/total')
  for item,hit in zip(r['items'],actual['hits']['hits']):
   require(item['source']==hit['_source'],'Java exact root source')
   if mode not in ['object','split']:
    require([o['source'] for o in item['offers']]==[h['_source'] for h in hit['inner_hits']['eligible']['hits']['hits']],'Java actual inner source');require(item['matchingOffers']==hit['inner_hits']['eligible']['hits']['total']['value'],'inner count')
   if mode.endswith('-sort'):require(item['sortPriceMinor']==hit['sort'][0],'actual sort price')
  out.append({'mode':mode,'ids':c['expected'][mode],'total':r['total'],'dsl':r['esRequest']})
 return {'reports':out,'java_internal_es_searches':5}
def errors():
 for m in ['object','nested']:
  request('PUT','/'+idx(m),read(SEARCH/(m+'-index.json')),status=400)
  b=request('POST','/'+idx(m)+'/_bulk',(DATA/'hotels.ndjson').read_text());require(b['errors'] and len(b['items'])==9 and all(i['create']['status']==409 for i in b['items']),'repeat18 conflict items')
 for body in [{},{'mode':None},{'mode':'all'},{'mode':1},{'mode':'../nested'}]:request('POST','/api/nested/inspect',body,status=400,app=True)
 bad=copy.deepcopy(read(DATA/'hotels.json')[0]);bad['rooms'][0]['price_minor']='bad';request('PUT','/'+idx('nested')+'/_doc/bad',bad,status=400)
 bad=copy.deepcopy(read(DATA/'hotels.json')[0]);bad['extra']='strict';request('PUT','/'+idx('nested')+'/_doc/bad',bad,status=400)
 for m in ['object','nested']:require(request('GET','/'+idx(m)+'/_count')['count']==9,'failed writes no extra roots')
 return {'repeat_create':'2 HTTP400; 18 bulk items409','invalid_input':5,'invalid_writes':2}
def cleanup():
 for m in ['object','nested']:request('DELETE','/'+idx(m),status=[200,404]);request('GET','/'+idx(m),status=404)
 return {'deleted_only':[idx('object'),idx('nested')]}
def main():
 global LOG
 p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','matching','sorting','java','errors','cleanup']);p.add_argument('--out',default=os.environ.get('F24_OUT',str(PROJECT/'review/f24/latest')));a=p.parse_args();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True);LOG=out/(a.command+'.jsonl');require(not LOG.exists(),'preserve logs; use fresh F24_OUT')
 result=globals()[a.command]();result.update(status='passed',http=COUNT,at=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/(a.command+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'command':a.command,'http':COUNT,'status':'passed'}))
if __name__=='__main__':main()
