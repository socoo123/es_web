#!/usr/bin/env python3
"""Real F08 acceptance; ES9.4.0 and running F07 Boot4/JDK25 application with F08 increment.
Refuses an existing F08 index. Only deletes tut-f08-attractions. No mocked HTTP responses.
"""
import datetime,hashlib,html,json,pathlib,re,subprocess,urllib.request,urllib.error
HERE=pathlib.Path(__file__).resolve().parent
P=HERE.parents[1]; ROOT=HERE.parents[3]
ES='http://127.0.0.1:19200'; APP='http://127.0.0.1:18080'; INDEX='tut-f08-attractions'
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requests':[],'rounds':[]}
def need(value,detail):
 if not value:raise AssertionError(detail)
def req(base,path,method='GET',body=None,expected=200,label=''):
 data=json.dumps(body,ensure_ascii=False).encode() if isinstance(body,(dict,list)) else body
 content='application/x-ndjson' if path.endswith('_bulk') else 'application/json'
 try:
  with urllib.request.urlopen(urllib.request.Request(base+path,data=data,method=method,headers={'Content-Type':content}),timeout=20) as r:status,raw=r.status,r.read().decode()
 except urllib.error.HTTPError as e:status,raw=e.code,e.read().decode()
 obj=json.loads(raw)
 R['requests'].append(dict(label=label,url=base+path,method=method,input=data.decode() if data else None,status=status,raw_response=raw))
 need(status==expected,dict(label=label,status=status,response=obj));return obj
def load(name):return json.loads((P/name).read_text())
def segments(raw):
 return [dict(text=html.unescape(s),matched=i%2==1) for i,s in enumerate(re.split(r'<mark>|</mark>',raw)) if s]
def main():
 node=req(ES,'/',label='version');need(node['version']['number']=='9.4.0',node)
 req(ES,'/'+INDEX,expected=404,label='refuse existing index')
 R['environment']={'ES':node,'application':'Spring Boot4.0.8 / Java Client & Rest5 9.4.8; real HTTP','platform':subprocess.check_output(['uname','-sm'],text=True)}
 R['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['data/f08','search/f08','labs/f08','backend/src'] for p in (P/folder).rglob('*') if p.is_file()}
 docs={d['attraction_id']:d for d in load('data/f08/attractions.json')}
 need(len(docs)==15,'15 unique business IDs')
 for original in load('data/f07/attractions.json'):
  inherited={k:v for k,v in docs[original['attraction_id']].items() if k!='aliases'}
  need(inherited==original,'F07 existing values must be inherited unchanged')
 base=['a-hz-boundary','a-hz-plain','a-hz-xihu']; multi=['a-hz-boundary','a-hz-guide','a-hz-plain','a-hz-tea','a-hz-xihu']
 expected={'name-only':base,'multi':multi,'alias':['a-hz-xihu'],'copy':sorted(multi+['a-hz-split']),'no-highlight':multi,'empty':[]}
 for number in [1,2]:
  need(req(ES,'/'+INDEX,'PUT',load('search/f08/index.json'))['acknowledged'],'create')
  health=req(ES,f'/_cluster/health/{INDEX}?wait_for_status=green&timeout=30s');need(health['status']=='green' and not health['timed_out'],health)
  mapping=req(ES,f'/{INDEX}/_mapping');need(mapping[INDEX]['mappings']==load('search/f08/index.json')['mappings'],mapping)
  bulk=req(ES,f'/{INDEX}/_bulk','POST',(P/'data/f08/attractions.ndjson').read_bytes());need(not bulk['errors'] and len(bulk['items'])==15 and all(x['index']['result']=='created' for x in bulk['items']),bulk)
  full=req(ES,f'/{INDEX}/_doc/a-hz-xihu',label='unfiltered source after copy_to')
  need(full['_source']==docs['a-hz-xihu'] and 'search_text' not in full['_source'],'copy_to must preserve unfiltered source')
  need(req(ES,f'/{INDEX}/_refresh','POST')['_shards']['failed']==0,'refresh')
  count=req(ES,f'/{INDEX}/_count');need(count['count']==15 and count['_shards']['failed']==0,count)
  results={}
  for slug,ids in expected.items():
   response=req(ES,f'/{INDEX}/_search','POST',load(f'search/f08/{slug}.json'),label=f'round{number} REST {slug}')
   need(not response['timed_out'] and response['_shards']['failed']==0,response)
   hits=response['hits'];need(hits['total']=={'value':len(ids),'relation':'eq'} and [h['_id'] for h in hits['hits']]==ids,response)
   need(all('search_text' not in h['_source'] for h in hits['hits']),'copy_to must not alter _source')
   if slug in ['copy','no-highlight']:need(all('highlight' not in h for h in hits['hits']),response)
   results[slug]=response
  need([h['_score'] for h in results['multi']['hits']['hits']]==[h['_score'] for h in results['no-highlight']['hits']['hits']], 'highlight must not change scores')
  for slug in ['multi','alias','empty']:
   inp=load(f'search/f08/input-{slug}.json');actual=req(APP,'/api/attractions/multi-search','POST',inp,label=f'round{number} Java {slug}')
   need(actual['conditions']==inp and actual['esRequest']==load(f'search/f08/{slug}.json'),actual)
   need(actual['total']==len(expected[slug]) and actual['totalRelation']=='eq' and [c['id'] for c in actual['items']]==expected[slug],actual)
   for card,hit in zip(actual['items'],results[slug]['hits']['hits']):
    src=docs[card['id']];need(card['name']==src['name'] and card['ticketPriceFen']==src['ticket_price_fen'] and card['currency']=='CNY' and card['status']=='open' and card['cityCode']=='HZ',card)
    need(card['score']==hit['_score'],card)
    for snippet in card['snippets']:
     field=snippet['field'];fragments=hit.get('highlight',{}).get(field,[])
     if fragments:
      target=[]
      for fragment in fragments:
       if target:target.append(dict(text=' … ',matched=False))
       target.extend(segments(fragment))
      need(snippet['highlighted'] and snippet['segments']==target,snippet)
     else:
      fallback=src.get(field) or {'aliases':'未提供别名','description':'暂无描述'}.get(field,src['name'])
      if isinstance(fallback,list):fallback='、'.join(fallback)
      need(not snippet['highlighted'] and snippet['segments']==[dict(text=fallback,matched=False)],snippet)
   if slug=='multi':
    guide=next(c for c in actual['items'] if c['id']=='a-hz-guide')
    desc=next(s for s in guide['snippets'] if s['field']=='description')
    need(''.join(s['text'] for s in desc['segments'])==docs['a-hz-guide']['description'],'original HTML literal roundtrip')
  invalid=dict(load('search/f08/input-multi.json'),maxPriceFen=-1)
  need(req(APP,'/api/attractions/multi-search','POST',invalid,400)['code']=='INVALID_SEARCH_INPUT','validation')
  need(req(ES,'/'+INDEX,'DELETE')['acknowledged'],'cleanup');req(ES,'/'+INDEX,expected=404,label='cleanup verified')
  need(req(APP,'/api/attractions/multi-search','POST',load('search/f08/input-multi.json'),502)['code']=='SEARCH_BACKEND_REJECTED','missing index')
  R['rounds'].append(dict(round=number,status='passed',ids=expected,checks=['mapping','15 created Bulk items','refresh/count','full ID order/total/relation','exact REST↔Java DSL','prices/source','all highlight segments and fallbacks','HTML literal roundtrip','400/502','named DELETE and 404']))
 R['status']='passed'
if __name__=='__main__':
 try:main();print('F08: two clean rounds passed, all six REST cases and three Java DTOs checked')
 except Exception as e:R['status']='failed';R['failure']=repr(e);raise
 finally:(HERE/'es-java-review.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
