#!/usr/bin/env python3
"""F21 fixed-time decay and sort contract. Prints every actual HTTP request/response."""
import copy,datetime,json,math,os,pathlib,sys,urllib.error,urllib.request
PROJECT=pathlib.Path(__file__).resolve().parents[2]
ES=os.environ.get('ES_URL','http://127.0.0.1:19221').rstrip('/')
APP=os.environ.get('APP_URL','http://127.0.0.1:18081').rstrip('/')
INDEX='tut-f21-attractions';AS_OF='2026-10-01T00:00:00.000Z'
CALLS,RESULTS=[],{}
EXPECTED={'text': ['hz-extreme', 'hz-far', 'hz-fresh', 'hz-missing', 'hz-near', 'hz-no-date', 'hz-no-geo', 'hz-stale', 'hz-weak'], 'bare': ['hz-missing', 'hz-no-date', 'hz-no-geo', 'hz-near', 'hz-fresh', 'hz-weak', 'hz-stale', 'hz-far', 'hz-extreme'], 'sum': ['hz-near', 'hz-fresh', 'hz-weak', 'hz-stale', 'hz-no-date', 'hz-far', 'hz-no-geo', 'hz-extreme', 'hz-missing'], 'product': ['hz-near', 'hz-fresh', 'hz-stale', 'hz-extreme', 'hz-far', 'hz-missing', 'hz-no-date', 'hz-no-geo', 'hz-weak'], 'multiply': ['hz-near', 'hz-fresh', 'hz-stale', 'hz-no-date', 'hz-far', 'hz-no-geo', 'hz-weak', 'hz-extreme', 'hz-missing'], 'replace': ['hz-weak', 'hz-near', 'hz-fresh', 'hz-stale', 'hz-no-date', 'hz-far', 'hz-no-geo', 'hz-extreme', 'hz-missing'], 'price': ['hz-weak', 'hz-no-geo', 'hz-far', 'hz-missing', 'hz-no-date', 'hz-stale', 'hz-fresh', 'hz-extreme', 'hz-near'], 'distance': ['hz-no-date', 'hz-weak', 'hz-near', 'hz-stale', 'hz-fresh', 'hz-far', 'hz-extreme', 'hz-missing', 'hz-no-geo'], 'radius': ['hz-near', 'hz-fresh', 'hz-weak', 'hz-stale', 'hz-no-date'], 'zero-budget': ['hz-weak'], 'other-city': ['sz-near'], 'empty': [], 'shift-origin': ['hz-far', 'hz-fresh', 'hz-no-geo', 'hz-near', 'hz-weak', 'hz-stale', 'hz-extreme', 'hz-missing', 'hz-no-date']}
JAVA_CASES=list(EXPECTED)
def load(slug):return json.loads((PROJECT/('search/f21/'+slug+'.json')).read_text())
def call(method, path, body=None, expected=200, app=False, ndjson=False):
    raw = body.encode() if ndjson else json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    request = urllib.request.Request((APP if app else ES) + path, data=raw, method=method,
        headers={'Content-Type': 'application/x-ndjson' if ndjson else 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status, value = response.status, json.load(response)
    except urllib.error.HTTPError as error:
        status, value = error.code, json.load(error)
    row = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'target': 'Java' if app else 'ES',
           'method': method, 'path': path, 'request': body, 'status': status, 'response': value}
    CALLS.append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)
    assert status in (expected if isinstance(expected, tuple) else (expected,)), (method, path, status, expected)
    return value

def close(a, b):
    assert math.isclose(a, b, rel_tol=2e-6, abs_tol=1e-7), (a, b)

def same(a, b):
    # Official client serializes floats through doubles; retain full structure and small numeric tolerance.
    if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
        close(a, b)
    elif isinstance(a, dict) and isinstance(b, dict):
        assert a.keys() == b.keys(), (a.keys(), b.keys())
        for key in a: same(a[key], b[key])
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b): same(x, y)
    else: assert a == b, (a, b)

def flatten(node):
    yield node
    for child in node.get('details', []): yield from flatten(child)

def canonical(x):
    if isinstance(x,list):return [canonical(v) for v in x]
    if not isinstance(x,dict):return x
    x={k:canonical(v) for k,v in x.items()}
    if 'sort' in x:
        x['sort']=[{k:v['order'] if isinstance(v,dict) and set(v)=={'order'} else v for k,v in s.items()} for s in x['sort']]
    return x

def hits(r):
 assert not r['timed_out'] and r['_shards']['failed']==0
 assert r['hits']['total']['relation']=='eq' and len(r['hits']['hits'])==r['hits']['total']['value']
 for h in r['hits']['hits']:
  assert h['_id']==h['_source']['attraction_id'];close(h['_score'],h['_explanation']['value'])
 return r['hits']['hits']

def search(slug):
 r=call('POST','/'+INDEX+'/_search',load(slug));rows=hits(r)
 assert [h['_id'] for h in rows]==EXPECTED[slug],(slug,[h['_id'] for h in rows])
 RESULTS[slug]=[{'id':h['_id'],'score':h['_score'],'sort':h['sort']} for h in rows]
 return {h['_id']:h for h in rows}

def explain(id,slug='sum',matched=True):
 r=call('POST','/'+INDEX+'/_explain/'+id,{'query':load(slug)['query']})
 assert r['_id']==id and r['matched']==matched
 if not matched:assert r['explanation']['value']==0
 return r

def prepare():
 v=call('GET','/')['version'];assert (v['number'],v['lucene_version'])==('9.4.0','10.4.0')
 n=call('GET','/_nodes/plugins')['nodes'];assert len(n)==1 and not next(iter(n.values()))['plugins']
 r=call('PUT','/'+INDEX,load('index'));assert r['acknowledged'] and r['shards_acknowledged']
 r=call('GET','/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s');assert r['status']=='green' and not r['timed_out']
 r=call('POST','/'+INDEX+'/_bulk',(PROJECT/'data/f21/attractions.ndjson').read_text(),ndjson=True)
 assert not r['errors'] and len(r['items'])==14 and all(x['create']['status']==201 and x['create']['result']=='created' for x in r['items'])
 assert call('POST','/'+INDEX+'/_refresh')['_shards']['failed']==0
 assert call('GET','/'+INDEX+'/_count')['count']==14
 actual=call('GET','/'+INDEX+'/_mapping')[INDEX]['mappings'];expected=copy.deepcopy(load('index')['mappings'])
 expected['properties']['verified_at'].pop('format') # ES omits this explicitly supplied default.
 assert actual==expected
 settings=call('GET','/'+INDEX+'/_settings')[INDEX]['settings']['index']
 assert (settings['number_of_shards'],settings['number_of_replicas'],settings['refresh_interval'])==('1','0','-1')
 assert settings['analysis']==load('index')['settings']['analysis']
 bm=settings['similarity']['lesson_bm25'];assert bm['type']=='BM25' and float(bm['k1'])==1.2 and float(bm['b'])==.75 and str(bm['discount_overlaps']).lower()=='true'
 search('text');probes={}
 for slug in ['probe-geo','probe-time']:
  rows=hits(call('POST','/'+INDEX+'/_search',load(slug)));probes[slug]={h['_id']:h['_score'] for h in rows}
 close(probes['probe-geo']['hz-missing'],1);close(probes['probe-time']['hz-missing'],1)
 close(probes['probe-time']['hz-near'],.5);assert probes['probe-geo']['hz-far']<1e-9
 r=call('POST','/'+INDEX+'/_search',load('future-probe'));assert {h['_id'] for h in hits(r)}=={'hz-near','hz-future'}
 for h in hits(r):close(h['_score'],.5)
 for id in ['hz-near','hz-missing']:explain(id,'bare')
 explain('hz-future',matched=False)
 RESULTS['raw_decay_probes']=probes

def scoring():
 rows={s:search(s) for s in ['text','bare','sum','product','multiply','replace']}
 # Use actual ES arc-sort distances, not rounded map labels, for an independent formula check.
 distance={h['_id']:h['sort'][0] for h in hits(call('POST','/'+INDEX+'/_search',load('distance')))}
 components={}
 for id,h in rows['sum'].items():
  s=h['_source'];B=rows['text'][id]['_score'];km=distance[id]
  D=0 if 'location' not in s else math.pow(.5,(max(0,km-1)/5)**2)
  age=None if 'verified_at' not in s else abs((datetime.datetime.fromisoformat(AS_OF.replace('Z','+00:00'))-datetime.datetime.fromisoformat(s['verified_at'].replace('Z','+00:00'))).total_seconds())/86400
  T=0 if age is None else math.pow(.5,max(0,age-1)/30)
  F=.5*D+.3*T
  close(h['_score'],B+F);close(rows['product'][id]['_score'],B+(.5*D)*(.3*T))
  close(rows['multiply'][id]['_score'],B*F);close(rows['replace'][id]['_score'],F)
  close(rows['bare'][id]['_score'],B+.5*(D if 'location' in s else 1)+.3*(T if 'verified_at' in s else 1))
  components[id]={'B':B,'distance_km':km,'age_days':age,'D':D,'T':T,'F':F,'sum':h['_score']}
 assert set(rows['sum'])==set(rows['multiply'])==set(rows['replace'])
 assert rows['multiply']['hz-missing']['_score']==0 and rows['replace']['hz-extreme']['_score']==0
 assert rows['sum']['hz-missing']['_score']==rows['text']['hz-missing']['_score']
 for id,slug in [('hz-missing','bare'),('hz-missing','sum'),('hz-far','sum'),('hz-weak','replace'),('hz-extreme','multiply')]:
  e=explain(id,slug);close(e['explanation']['value'],rows[slug][id]['_score'])
 # Reproduce the discarded zero-weight fallback, then compare with literal-zero functions.
 q=load('sum')
 for f in q['query']['function_score']['functions']:
  if 'script_score' in f:f.pop('script_score');f['weight']=0
 r=call('POST','/'+INDEX+'/_search',q);missing=next(h for h in hits(r) if h['_id']=='hz-missing')
 close(missing['_score'],rows['text']['hz-missing']['_score']+.8)
 RESULTS['components']=components;RESULTS['zero_weight_fallback_score']=missing['_score']

def edges():
 for slug in ['price','distance','radius','shift-origin','zero-budget','other-city','empty']:search(slug)
 r=call('POST','/'+INDEX+'/_search',load('default-score'));scores=[h['_score'] for h in hits(r)]
 assert scores==sorted(scores,reverse=True) and all('sort' not in h for h in r['hits']['hits'])
 q=load('price');q['track_scores']=False;q['explain']=False
 r=call('POST','/'+INDEX+'/_search',q);assert [h['_id'] for h in r['hits']['hits']]==EXPECTED['price'] and all(h['_score'] is None for h in r['hits']['hits'])
 q=load('multiply');q['min_score']=.000001
 r=call('POST','/'+INDEX+'/_search',q);assert r['hits']['total']['value']==7 and all(h['_id'] not in ['hz-extreme','hz-missing'] for h in hits(r))
 for slug in ['bad-scale','bad-decay']:call('POST','/'+INDEX+'/_search',load(slug),expected=400)
 call('PUT','/'+INDEX+'/_doc/hz-invalid-location',{'location':{'lat':91,'lon':120}},expected=400)
 q=load('distance');q['sort'][0]['_geo_distance']['unknown_location']=q['sort'][0]['_geo_distance'].pop('location')
 call('POST','/'+INDEX+'/_search',q,expected=400)
 for id in ['hz-noise','hz-closed','hz-expensive','hz-future','sz-near']:explain(id,matched=False)
 explain('hz-far','radius',matched=False)
 assert 'hz-far' in EXPECTED['sum'] and 'hz-far' not in EXPECTED['radius']

def verify_java(slug):
 i=load('input-'+slug);r=call('POST','/api/attractions/decay-search',i,app=True)
 assert r['conditions']==i and r['asOf']==AS_OF and canonical(r['esRequest'])==canonical(load(slug)),(slug,r['esRequest'],load(slug))
 rows=hits(call('POST','/'+INDEX+'/_search',r['esRequest']));assert [h['_id'] for h in rows]==EXPECTED[slug]
 cards=[]
 for h in rows:
  s=h['_source'];cards.append(dict(id=h['_id'],name=s['name'],description=s['description'],cityCode=s['city_code'],ticketPriceFen=s['ticket_price_fen'],currency=s['currency'],status=s['status'],location=s.get('location'),verifiedAt=s.get('verified_at'),distanceKm=h['sort'][0] if i['sortMode']=='distance' and s.get('location') is not None else None,score=h['_score'],sortValues=h['sort'],explanation=h['_explanation']))
 same(r['items'],cards);assert r['total']==len(cards) and r['relation']=='eq'
 assert r['explainRequest']=={'query':r['esRequest']['query']} and r['explainPath']=='/'+INDEX+'/_explain/'+i['explainId']
 e=call('POST',r['explainPath'],r['explainRequest']);assert r['explainResponse']['matched']==e['matched'] and r['explainResponse']['_id']==e['_id']
 same(r['explainResponse']['explanation'],e['explanation'])
 same([(h['_id'],h['_source'],h['_score'],h['sort'],h['_explanation']) for h in hits(r['esResponse'])],[(h['_id'],h['_source'],h['_score'],h['sort'],h['_explanation']) for h in rows])
 RESULTS['Java:'+slug]={'ids':EXPECTED[slug],'matched':e['matched']}

def java_check():
 for slug in JAVA_CASES:verify_java(slug)

def cleanup():
 call('DELETE','/'+INDEX,expected=(200,404));call('GET','/'+INDEX,expected=404)

if __name__=='__main__':
 {'prepare':prepare,'scoring':scoring,'edges':edges,'java':java_check,'cleanup':cleanup}[sys.argv[1]]()
