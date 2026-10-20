#!/usr/bin/env python3
"""F09 real ES/Java acceptance: two clean rounds; never mocks responses.
Only deletes tut-f09-attractions and tut-f09-candidates; refuses pre-existing resources.
"""
import datetime,hashlib,json,pathlib,subprocess,traceback,urllib.request,urllib.error
H=pathlib.Path(__file__).resolve().parent;P=H.parents[1];ROOT=H.parents[3]
ES='http://127.0.0.1:19200';APP='http://127.0.0.1:18080';MAIN='tut-f09-attractions';CAND='tut-f09-candidates'
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F09 real REST/Java only','requests':[],'rounds':[]}
def need(v,d):
 if not v:raise AssertionError(d)
def req(base,path,method='GET',body=None,status=200,label=''):
 data=json.dumps(body,ensure_ascii=False).encode() if isinstance(body,(dict,list)) else body
 headers={'Content-Type':'application/x-ndjson' if path.endswith('_bulk') else 'application/json'}
 try:
  with urllib.request.urlopen(urllib.request.Request(base+path,data=data,method=method,headers=headers),timeout=30) as r:s,raw=r.status,r.read().decode()
 except urllib.error.HTTPError as e:s,raw=e.code,e.read().decode()
 R['requests'].append(dict(url=base+path,method=method,input=data.decode() if data else None,status=s,raw_response=raw,label=label))
 obj=json.loads(raw);need(s==status,dict(path=path,status=s,response=obj));return obj
def load(name):return json.loads((P/name).read_text())
def search(index,body,label):
 r=req(ES,f'/{index}/_search','POST',body,label=label);need(not r['timed_out'] and r['_shards']['failed']==0,r);return r
def setup(index,source,bulk,count):
 need(req(ES,'/'+index,'PUT',load(source))['acknowledged'],'create')
 h=req(ES,f'/_cluster/health/{index}?wait_for_status=green&timeout=30s');need(h['status']=='green' and not h['timed_out'],h)
 m=req(ES,f'/{index}/_mapping');need(m[index]['mappings']==load(source)['mappings'],m)
 b=req(ES,f'/{index}/_bulk','POST',(P/bulk).read_bytes());need(not b['errors'] and len(b['items'])==count and all(x['index']['result']=='created' and x['index']['status']==201 for x in b['items']),b)
 need(req(ES,f'/{index}/_refresh','POST')['_shards']['failed']==0,'refresh')
 c=req(ES,f'/{index}/_count');need(c['count']==count and c['_shards']['failed']==0,c)
def term_counts(documents,field):
 counts={}
 for d in documents:
  values=d.get(field,[]);values=values if isinstance(values,list) else [values]
  for v in set(values):counts[v]=counts.get(v,0)+1
 return sorted(counts.items(),key=lambda x:(-x[1],x[0]))
def check_terms(actual,docs,field):
 need(actual['doc_count_error_upper_bound']==0 and actual['sum_other_doc_count']==0,actual)
 need([(b['key'],b['doc_count']) for b in actual['buckets']]==term_counts(docs,field),actual)
 need(all(b['doc_count_error_upper_bound']==0 for b in actual['buckets']),actual)
def check_group(dto,agg,scope):
 values=agg['values'];need(dto['scope']==scope and dto['scopeTotal']==agg['doc_count'],dto)
 need(dto['docCountErrorUpperBound']==values['doc_count_error_upper_bound'] and dto['sumOtherDocCount']==values['sum_other_doc_count'],dto)
 need(dto['buckets']==[dict(key=b['key'],docCount=b['doc_count'],docCountErrorUpperBound=b['doc_count_error_upper_bound']) for b in values['buckets']],dto)
def main():
 node=req(ES,'/');need(node['version']['number']=='9.4.0' and node['version']['lucene_version']=='10.4.0',node)
 for index in [MAIN,CAND]:req(ES,'/'+index,status=404,label='refuse pre-existing resource')
 R['environment']={'ES':node,'application':'Boot4.0.8 / Temurin25.0.4.1+1 / official Java and Rest5 Client9.4.8','platform':subprocess.check_output(['uname','-sm'],text=True)}
 R['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['data/f09','search/f09','labs/f09','backend/src'] for p in (P/folder).rglob('*') if p.is_file()}
 docs={d['attraction_id']:d for d in load('data/f09/attractions.json')};need(len(docs)==16,'16 unique docs')
 for d in load('data/f08/attractions.json'):need({k:v for k,v in docs[d['attraction_id']].items() if k!='themes'}==d,'F08 inherited unchanged')
 B=['a-fz-xihu','a-hz-boundary','a-hz-far','a-hz-guide','a-hz-missing-location','a-hz-plain','a-hz-tea','a-hz-xihu','a-sh-exhibit']
 selected=['a-hz-boundary','a-hz-far','a-hz-guide','a-hz-xihu']
 expected={'selected':selected,'multi-city':['a-fz-xihu']+selected,'overlap':['a-hz-guide','a-hz-missing-location','a-hz-xihu'],'empty':[],'unselected':B}
 for number in [1,2]:
  setup(MAIN,'search/f09/index.json','data/f09/attractions.ndjson',16)
  compared={}
  for slug,ids in expected.items():
   inp=load(f'search/f09/input-{slug}.json');r=search(MAIN,load(f'search/f09/{slug}.json'),f'round{number} REST {slug}')
   hits=r['hits'];need(hits['total']=={'value':len(ids),'relation':'eq'} and [h['_id'] for h in hits['hits']]==ids,r)
   base=[docs[x] for x in B] if inp['q']=='西湖' else []
   cities=[d for d in base if not inp['themes'] or set(d.get('themes',[]))&set(inp['themes'])]
   themes=[d for d in base if not inp['cityCodes'] or d['city_code'] in inp['cityCodes']]
   aggs=r['aggregations'];need(aggs['cities']['doc_count']==len(cities) and aggs['themes']['doc_count']==len(themes),'branch scopes')
   check_terms(aggs['cities']['values'],cities,'city_code');check_terms(aggs['themes']['values'],themes,'themes')
   need(aggs['themes']['missing_theme']['doc_count']==sum(not d.get('themes') for d in themes),'missing theme')
   price=aggs['prices'];need(price['doc_count']==len(ids),'price scope')
   counts=[sum(0<=docs[x]['ticket_price_fen']<10000 for x in ids),sum(10000<=docs[x]['ticket_price_fen']<20000 for x in ids),sum(docs[x]['ticket_price_fen']>=20000 for x in ids)]
   need([b['doc_count'] for b in price['ranges']['buckets']]==counts,price)
   actual=req(APP,'/api/attractions/facet-search','POST',inp,label=f'round{number} Java {slug}')
   need(actual['conditions']==inp and actual['esRequest']==load(f'search/f09/{slug}.json'),actual)
   need(actual['total']==len(ids) and actual['totalRelation']=='eq' and [x['id'] for x in actual['items']]==ids,actual)
   for card,hit in zip(actual['items'],hits['hits']):
    d=docs[card['id']];need(card==dict(id=hit['_id'],name=d['name'],cityCode=d['city_code'],ticketPriceFen=d['ticket_price_fen'],currency=d['currency'],status=d['status'],themes=d.get('themes',[])),card)
    need(hit['_source']=={k:v for k,v in d.items() if k in load('search/f09/selected.json')['_source']['includes']},'source includes')
   check_group(actual['cities'],aggs['cities'],'base AND selected themes; city ignored')
   check_group(actual['themes'],aggs['themes'],'base AND selected cities; theme ignored')
   need(actual['missingThemeCount']==aggs['themes']['missing_theme']['doc_count'] and actual['priceScopeTotal']==len(ids),actual)
   need(actual['prices']==[dict(key=b['key'],fromFen=b.get('from'),toFen=b.get('to'),docCount=b['doc_count']) for b in price['ranges']['buckets']],actual)
   compared[slug]={'ids':ids,'cities':actual['cities'],'themes':actual['themes'],'prices':actual['prices']}
  for slug,scope_ids in [('all-query',selected),('post-only',B)]:
   r=search(MAIN,load(f'search/f09/{slug}.json'),f'round{number} {slug}')
   need([h['_id'] for h in r['hits']['hits']]==selected and r['hits']['total']=={'value':4,'relation':'eq'},r)
   for name,field in [('cities','city_code'),('themes','themes')]:check_terms(r['aggregations'][name],[docs[x] for x in scope_ids],field)
  for size in [2,0]:
   body=load('search/f09/selected.json');body['size']=size;r=search(MAIN,body,f'round{number} size={size}')
   need(len(r['hits']['hits'])==size and r['hits']['total']=={'value':4,'relation':'eq'},r)
   need(r['aggregations']['cities']['doc_count']==6 and r['aggregations']['themes']['doc_count']==7 and r['aggregations']['prices']['doc_count']==4,r)
  valid=load('search/f09/input-selected.json')
  for changes in [{'cityCodes':['XX']},{'themes':['unknown']},{'cityCodes':None},{'themes':[None]},{'maxPriceFen':-1},{'maxPriceFen':1.5},{'q':''},{'cityCodes':['HZ']*4},{'themes':['lake']*5}]:
   need(req(APP,'/api/attractions/facet-search','POST',dict(valid,**changes),400)['code']=='INVALID_SEARCH_INPUT','invalid input')
  setup(CAND,'search/f09/candidates-index.json','data/f09/candidates.ndjson',20)
  shards=[]
  for route in ['a','b']:
   r=req(ES,f'/{CAND}/_search_shards?routing={route}');need(len(r['shards'])==1,'single routing shard');shards.append(r['shards'][0][0]['shard'])
  need(shards==[0,1],shards)
  results={}
  for slug,expected_buckets,error,other in [('candidate-small',[('A',5,5)],10,15),('candidate-wide',[('C',8,0)],0,12),('candidate-all',[('C',8,0),('A',6,0),('B',6,0)],0,0)]:
   r=search(CAND,load(f'search/f09/{slug}.json'),f'round{number} {slug}');t=r['aggregations']['tags']
   need(r['hits']['total']=={'value':20,'relation':'eq'} and r['hits']['hits']==[],r)
   need(t['doc_count_error_upper_bound']==error and t['sum_other_doc_count']==other,t)
   need([(b['key'],b['doc_count'],b['doc_count_error_upper_bound']) for b in t['buckets']]==expected_buckets,t);results[slug]=t
  for index in [MAIN,CAND]:
   need(req(ES,'/'+index,'DELETE')['acknowledged'],'cleanup');req(ES,'/'+index,status=404,label='named cleanup verified')
  need(req(APP,'/api/attractions/facet-search','POST',valid,502)['code']=='SEARCH_BACKEND_REJECTED','missing index')
  R['rounds'].append(dict(round=number,status='passed',main=compared,candidates=results,checks=['mapping/Bulk created/refresh/count','all expected IDs/source/total/relation','scope sets and exact buckets','REST Java exact DSL and all DTO metadata','same dimension OR/cross dimension AND','missing theme/overlap/range boundaries','size0/2 still total4 and same scopes','nine invalid inputs400','two primary routing/candidate undercount/truncation','named cleanup404 and Java502']))
 R['status']='passed'
if __name__=='__main__':
 try:main();print('F09: two clean rounds passed; exact REST/Java IDs/scopes/buckets/error metadata and real two-shard candidate error')
 except Exception:R['status']='failed';R['failure']=traceback.format_exc();raise
 finally:(H/'es-java-review.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
