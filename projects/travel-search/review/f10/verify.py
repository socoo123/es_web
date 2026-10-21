#!/usr/bin/env python3
"""F10 real REST/Java: two clean rounds, exact IDs/DSL/sort; only F10 resource."""
import copy,datetime,hashlib,json,math,pathlib,subprocess,traceback,urllib.request,urllib.error
H=pathlib.Path(__file__).resolve().parent;P=H.parents[1];ROOT=H.parents[3]
ES='http://127.0.0.1:19200';APP='http://127.0.0.1:18080';INDEX='tut-f10-attractions'
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F10 real REST/Java two clean rounds','requests':[],'rounds':[]}
def need(v,d):
 if not v:raise AssertionError(d)
def load(name):return json.loads((P/name).read_text())
def req(base,path,method='GET',body=None,status=200,label=''):
 data=json.dumps(body,ensure_ascii=False).encode() if isinstance(body,(dict,list)) else body
 headers={'Content-Type':'application/x-ndjson' if path.endswith('_bulk') else 'application/json'}
 try:
  with urllib.request.urlopen(urllib.request.Request(base+path,data=data,method=method,headers=headers),timeout=40) as r:s,raw=r.status,r.read().decode()
 except urllib.error.HTTPError as e:s,raw=e.code,e.read().decode()
 R['requests'].append(dict(url=base+path,method=method,input=data.decode() if data else None,status=s,raw_response=raw,label=label));obj=json.loads(raw)
 need(s==status,dict(path=path,status=s,response=obj));return obj
def search(body,label):
 r=req(ES,'/'+INDEX+'/_search','POST',body,label=label);need(not r['timed_out'] and r['_shards']['failed']==0,r);return r
def ids(r):return [h['_id'] for h in r['hits']['hits']]
def eq(a,b):
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):return math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-7)
 if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
 return a==b
S=['a-sh-exhibit','a-hz-tea','a-hz-guide','a-fz-xihu','a-hz-plain','a-hz-xihu','a-hz-boundary','a-hz-missing-location','a-hz-far']
PR=['a-fz-xihu','a-hz-xihu','a-hz-far','a-hz-guide','a-hz-missing-location','a-hz-plain','a-hz-tea','a-sh-exhibit','a-hz-boundary']
D=['a-hz-guide','a-hz-plain','a-hz-xihu','a-hz-boundary','a-hz-tea','a-hz-far','a-sh-exhibit','a-fz-xihu','a-hz-missing-location']
def main():
 node=req(ES,'/');need(node['version']['number']=='9.4.0' and node['version']['lucene_version']=='10.4.0',node)
 req(ES,'/'+INDEX,status=404,label='refuse pre-existing resource')
 R['environment']={'node':node,'platform':subprocess.check_output(['uname','-sm'],text=True),'application':'Boot4.0.8 / Temurin25.0.4.1+1 / official Java and Rest5 Client9.4.8'}
 R['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['data/f10','search/f10','labs/f10','backend/src'] for p in (P/folder).rglob('*') if p.is_file()}
 docs={d['attraction_id']:d for d in load('data/f10/attractions.json')};need(list(docs.values())==load('data/f09/attractions.json'),'F09 data unchanged');need(len(docs)==16,'16 unique IDs')
 expected={'relevance':S,'price':PR,'distance':D,'price-scores':PR,'hz-distance':[x for x in D if docs[x]['city_code']=='HZ'],'budget-price':[x for x in PR if docs[x]['ticket_price_fen']<=8000],'empty':[]}
 for number in [1,2]:
  need(req(ES,'/'+INDEX,'PUT',load('search/f10/index.json'))['acknowledged'],'create')
  h=req(ES,'/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s');need(h['status']=='green' and not h['timed_out'],h)
  need(req(ES,'/'+INDEX+'/_mapping')[INDEX]['mappings']==load('search/f10/index.json')['mappings'],'mapping')
  b=req(ES,'/'+INDEX+'/_bulk','POST',(P/'data/f10/attractions.ndjson').read_bytes());need(not b['errors'] and len(b['items'])==16 and all(x['index']['status']==201 and x['index']['result']=='created' for x in b['items']),b)
  need(req(ES,'/'+INDEX+'/_refresh','POST')['_shards']['failed']==0,'refresh');c=req(ES,'/'+INDEX+'/_count');need(c['count']==16 and c['_shards']['failed']==0,c)
  compared={};responses={}
  for slug,expected_ids in expected.items():
   body=load(f'search/f10/{slug}.json');inp=load(f'search/f10/input-{slug}.json');r=search(body,f'round{number} REST {slug}');responses[slug]=r
   need(r['hits']['total']=={'value':len(expected_ids),'relation':'eq'} and ids(r)==expected_ids,r)
   a=req(APP,'/api/attractions/sort-search','POST',inp,label=f'round{number} Java {slug}')
   need(a['conditions']==inp and a['esRequest']==body,a);need(a['total']==len(expected_ids) and a['totalRelation']=='eq' and [x['id'] for x in a['items']]==expected_ids,a)
   for card,hit in zip(a['items'],r['hits']['hits']):
    doc=docs[card['id']];need(hit['_source']=={k:v for k,v in doc.items() if k in body['_source']['includes']},'source projection')
    need(card['name']==doc['name'] and card['cityCode']==doc['city_code'] and card['ticketPriceFen']==doc['ticket_price_fen'] and card['currency']=='CNY' and card['status']=='open',card)
    need(eq(card['sortValues'],hit['sort']) and eq(card['score'],hit['_score']),card)
    need(card['hasLocation']==('location' in doc),card)
    need(eq(card['distanceKm'],hit['sort'][0] if inp['sortMode']=='distance' and 'location' in doc else None),card)
    need(hit['sort'][1]==card['id'] and 0<=doc['ticket_price_fen']<=inp['maxPriceFen'],card)
    if inp['cityCode']!='ALL':need(doc['city_code']==inp['cityCode'],card)
   if slug in ['price','distance']:need(all(h['_score'] is None for h in r['hits']['hits']),slug)
   if slug in ['relevance','price-scores']:need(all(isinstance(h['_score'],(int,float)) for h in r['hits']['hits']),slug)
   compared[slug]={'ids':expected_ids,'sort_values':[h['sort'] for h in r['hits']['hits']],'scores':[h['_score'] for h in r['hits']['hits']]}
  need(set(S)==set(PR)==set(D),'same candidates')
  need([h['sort'] for h in responses['price']['hits']['hits']]==[h['sort'] for h in responses['price-scores']['hits']['hits']],'track_scores preserves sort')
  default=search(load('search/f10/default.json'),f'round{number} no explicit sort');need(set(ids(default))==set(S),'default same set')
  scores=[h['_score'] for h in default['hits']['hits']];need(scores==sorted(scores,reverse=True) and all('sort' not in h for h in default['hits']['hits']),'default score order, no tied ID guarantee')
  distance=responses['distance']['hits']['hits'];need(distance[-1]['sort']==['Infinity','a-hz-missing-location'],'missing geo wire value')
  body=load('search/f10/distance.json');body['sort'][0]['_geo_distance']['unit']='m';m=search(body,f'round{number} unit=m');need(ids(m)==D,'m order')
  need(all(eq(x['sort'][0],y['sort'][0]*1000) for x,y in zip(m['hits']['hits'][:-1],distance[:-1])),'m/km')
  body=load('search/f10/distance.json');body['query']['bool']['filter'].append({'geo_distance':{'distance':'3km','distance_type':'arc','location':{'lat':30.25,'lon':120.15}}});radius=search(body,f'round{number} radius changes set');need(ids(radius)==D[:5] and radius['hits']['total']=={'value':5,'relation':'eq'},radius)
  for slug,expect,first in [('missing-last',['a-hz-xihu','a-hz-guide','a-hz-missing-price','a-hz-null-price'],[0,1000,2147483647,2147483647]),('missing-zero',['a-hz-missing-price','a-hz-null-price','a-hz-xihu','a-hz-guide'],[0,0,0,1000])]:
   r=search(load(f'search/f10/{slug}.json'),f'round{number} {slug}');need(ids(r)==expect and r['hits']['total']=={'value':4,'relation':'eq'},r);need([h['sort'][0] for h in r['hits']['hits']]==first,r)
   for h in r['hits']['hits']:
    d=docs[h['_id']];need(h['_source']=={k:v for k,v in d.items() if k in load('search/f10/price.json')['_source']['includes']},'missing strategy did not write source')
  valid=load('search/f10/input-price.json');invalid=[{'q':''},{'sortMode':'rating'},{'cityCode':'XX'},{'maxPriceFen':-1},{'maxPriceFen':1.5},{'maxPriceFen':100000001},{'latitude':91},{'longitude':181},{'trackScores':None},{'latitude':None},{'q':'x'*61}]
  for changes in invalid:need(req(APP,'/api/attractions/sort-search','POST',dict(valid,**changes),400)['code']=='INVALID_SEARCH_INPUT',changes)
  need(req(ES,'/'+INDEX,'DELETE')['acknowledged'],'cleanup');req(ES,'/'+INDEX,status=404,label='deleted before next clean round')
  need(req(APP,'/api/attractions/sort-search','POST',valid,502)['code']=='SEARCH_BACKEND_REJECTED','missing index')
  R['rounds'].append({'number':number,'created':16,'cases':compared,'default_scores':scores,'invalid_inputs':len(invalid),'cleanup':'index 404; Java 502; next round starts clean','status':'passed'})
 R['status']='passed';R['limitations']=['No multi-node or concurrent changes/PIT/pagination','No forced ES execution timeout or partial shard failure','No cost/quality benchmark']
try:main()
except Exception:R['status']='failed';R['failure']=traceback.format_exc();raise
finally:(H/'es-java-review.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print('F10 real REST/Java passed: two clean rounds, full IDs/sort/DSL/source/score, units and missing values')
