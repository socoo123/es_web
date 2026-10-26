#!/usr/bin/env python3
"""F20 fixed signals: actual IDs, score components, rank-feature precision and REST/Java."""
import copy,datetime,json,math,os,pathlib,sys,urllib.error,urllib.request
PROJECT=pathlib.Path(__file__).resolve().parents[2]
ES=os.environ.get('ES_URL','http://127.0.0.1:19220').rstrip('/')
APP=os.environ.get('APP_URL','http://127.0.0.1:18080').rstrip('/')
INDEX='tut-f20-attractions'
CALLS,RESULTS=[],{}
EXPECTED={
 'text':['hz-fresh','hz-huge','hz-missing','hz-small','hz-steady','hz-zero','hz-hot'],
 'raw':['hz-hot','hz-huge','hz-steady','hz-fresh','hz-small','hz-missing','hz-zero'],
 'average':['hz-small','hz-fresh','hz-steady','hz-huge','hz-missing','hz-zero','hz-hot'],
 'quality':['hz-steady','hz-huge','hz-fresh','hz-small','hz-missing','hz-zero','hz-hot'],
 'compressed':['hz-hot','hz-huge','hz-steady','hz-fresh','hz-small','hz-missing','hz-zero'],
 'bounded':['hz-huge','hz-steady','hz-fresh','hz-small','hz-hot','hz-missing','hz-zero'],
 'rank':['hz-steady','hz-huge','hz-fresh','hz-small','hz-zero','hz-hot','hz-missing'],
 'rank-only':['hz-noise','hz-steady','hz-huge','hz-fresh','hz-hot','hz-small','hz-zero'],
 'other-city':['sz-steady'],'zero-budget':['hz-small','hz-missing','hz-zero'],'empty':[]}
JAVA_CASES=list(EXPECTED)
def load(slug):
    return json.loads((PROJECT / ('search/f20/' + slug + '.json')).read_text())


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


def hits(r):
    assert not r['timed_out'] and r['_shards']['failed'] == 0
    assert r['hits']['total']['relation'] == 'eq'
    assert len(r['hits']['hits']) == r['hits']['total']['value']
    for h in r['hits']['hits']:
        assert h['_id'] == h['_source']['attraction_id']
        close(h['_score'], h['_explanation']['value']); close(h['sort'][0], h['_score'])
        assert h['sort'][1] == h['_id']
    return r['hits']['hits']


def search(slug):
 r=call('POST','/'+INDEX+'/_search',load(slug));rows=hits(r)
 assert [h['_id'] for h in rows]==EXPECTED[slug],(slug,[h['_id'] for h in rows])
 RESULTS[slug]=[{'id':h['_id'],'score':h['_score']} for h in rows]
 return {h['_id']:h for h in rows}

def explain(id,slug='bounded',matched=True):
 r=call('POST','/'+INDEX+'/_explain/'+id,{'query':load(slug)['query']})
 assert r['_id']==id and r['matched']==matched
 if not matched:assert r['explanation']['value']==0
 return r

def prepare():
 v=call('GET','/')['version'];assert (v['number'],v['lucene_version'])==('9.4.0','10.4.0')
 n=call('GET','/_nodes/plugins')['nodes'];assert len(n)==1 and not next(iter(n.values()))['plugins']
 r=call('PUT','/'+INDEX,load('index'));assert r['acknowledged'] and r['shards_acknowledged']
 r=call('GET','/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s');assert r['status']=='green' and not r['timed_out']
 r=call('POST','/'+INDEX+'/_bulk',(PROJECT/'data/f20/attractions.ndjson').read_text(),ndjson=True)
 assert not r['errors'] and len(r['items'])==11 and all(v['create']['status']==201 and v['create']['result']=='created' for v in r['items'])
 assert call('POST','/'+INDEX+'/_refresh')['_shards']['failed']==0
 assert call('GET','/'+INDEX+'/_count')['count']==11
 actual=call('GET','/'+INDEX+'/_mapping')[INDEX]['mappings']
 expected=copy.deepcopy(load('index')['mappings']);expected['properties']['quality_rank'].pop('positive_score_impact')
 assert actual==expected
 settings=call('GET','/'+INDEX+'/_settings')[INDEX]['settings']['index']
 assert (settings['number_of_shards'],settings['number_of_replicas'],settings['refresh_interval'])==('1','0','-1')
 assert settings['analysis']==load('index')['settings']['analysis']
 bm=settings['similarity']['lesson_bm25'];assert bm['type']=='BM25' and float(bm['k1'])==1.2 and float(bm['b'])==.75 and str(bm['discount_overlaps']).lower()=='true'
 docs=json.loads((PROJECT/'data/f20/attractions.json').read_text())
 for d in docs:
  if 'quality_score' in d:
   v=d['review_count'];expected=(v*d.get('review_avg',4)+80)/(v+20);close(d['quality_score'],expected)
 rows={s:search(s) for s in ['text','average','quality']}
 for id in ['hz-small','hz-steady']:explain(id,'quality')
 assert rows['average']['hz-small']['_score']>rows['average']['hz-steady']['_score']
 assert rows['quality']['hz-small']['_score']<rows['quality']['hz-steady']['_score']


def scoring():
 rows={s:search(s) for s in ['text','raw','quality','compressed','bounded']}
 for id,h in rows['bounded'].items():
  d=h['_source'];text=rows['text'][id]['_score'];quality=.2*d.get('quality_score',4);hot=.15*math.log1p(d.get('hot_30d',0))
  close(rows['quality'][id]['_score'],text+quality)
  close(rows['compressed'][id]['_score'],text+quality+hot)
  close(h['_score'],text+min(quality+hot,1.5))
  close(rows['raw'][id]['_score'],text+d.get('hot_30d',0))
  if id=='hz-hot':RESULTS['hot_components']={'text':text,'quality':quality,'heat':hot,'function_sum':quality+hot,'bounded':h['_score']}
 assert set(rows['raw'])==set(rows['bounded']) and rows['bounded']['hz-huge']['_score']>1.5
 for id,slug in [('hz-hot','raw'),('hz-hot','compressed'),('hz-hot','bounded'),('hz-huge','bounded'),('hz-missing','bounded'),('hz-zero','bounded')]:
  e=explain(id,slug);close(e['explanation']['value'],rows[slug][id]['_score'])


def edges():
 search('text');rows=search('rank');only=search('rank-only')
 assert 'hz-noise' not in rows and 'hz-missing' in rows and 'hz-noise' in only and 'hz-missing' not in only
 encoded={}
 for id,h in only.items():
  nodes=list(flatten(h['_explanation']));raw=h['_source']['quality_rank']
  feature=next(n['value'] for n in nodes if n['description']=='S, feature value')
  assert abs(feature-raw)/raw<.0041
  close(h['_score'],feature/(feature+4));encoded[id]={'source':raw,'encoded_S':feature,'saturation':h['_score']}
 RESULTS['rank_precision']=encoded
 explain('hz-missing','rank');explain('hz-noise','rank-only')
 for id in ['hz-noise','hz-closed','hz-expensive','sz-steady']:explain(id,matched=False)
 for slug in ['ln-zero','no-missing']:
  e=call('POST','/'+INDEX+'/_search',load(slug),expected=400);assert e['error']['type']=='search_phase_execution_exception'
 for value in [0,-1,[4,5]]:
  e=call('PUT','/'+INDEX+'/_doc/hz-invalid-rank',{'quality_rank':value},expected=400)
  assert e['error']['type']=='document_parsing_exception'
 assert call('GET','/'+INDEX+'/_doc/hz-invalid-rank',expected=404)['found']==False
 for slug in ['zero-budget','other-city','empty']:search(slug)
 for body in [{'sort':[{'quality_rank':'desc'}]},{'size':0,'aggs':{'q':{'avg':{'field':'quality_rank'}}}}]:
  call('POST','/'+INDEX+'/_search',body,expected=400)
 # Explicit factor is inside ln1p, weight is outside. Restore nothing: query only.
 q=load('compressed');q['query']['function_score']['functions'][1]['field_value_factor']['factor']=.1
 r=call('POST','/'+INDEX+'/_search',q)
 for h in hits(r):
  d=h['_source'];base=next(x['score'] for x in RESULTS['text'] if x['id']==h['_id'])
  close(h['_score'],base+.2*d.get('quality_score',4)+.15*math.log1p(.1*d.get('hot_30d',0)))


def canonical(x):
    if isinstance(x,list):return [canonical(v) for v in x]
    if not isinstance(x,dict):return x
    x={k:canonical(v) for k,v in x.items()}
    if 'sort' in x:
        x['sort']=[{k:v['order'] if isinstance(v,dict) and set(v)=={'order'} else v for k,v in s.items()} for s in x['sort']]
    return x


def verify_java(slug):
    i=load('input-'+slug);r=call('POST','/api/attractions/signal-search',i,app=True)
    assert r['conditions']==i and canonical(r['esRequest'])==canonical(load(slug)), (slug,r['esRequest'],load(slug))
    rows=hits(call('POST','/'+INDEX+'/_search',r['esRequest']))
    assert [h['_id'] for h in rows]==EXPECTED[slug]
    cards=[]
    for h in rows:
        s=h['_source'];cards.append(dict(id=h['_id'],name=s['name'],description=s['description'],cityCode=s['city_code'],
            ticketPriceFen=s['ticket_price_fen'],currency=s['currency'],status=s['status'],reviewAvg=s.get('review_avg'),reviewCount=s.get('review_count'),qualityScore=s.get('quality_score'),hot30d=s.get('hot_30d'),score=h['_score'],sortValues=h['sort'],explanation=h['_explanation']))
    same(r['items'],cards);assert r['total']==len(cards) and r['relation']=='eq'
    assert r['explainRequest']=={'query':r['esRequest']['query']}
    assert r['explainPath']=='/'+INDEX+'/_explain/'+i['explainId']
    e=call('POST',r['explainPath'],r['explainRequest'])
    assert r['explainResponse']['matched']==e['matched'] and r['explainResponse']['_id']==e['_id']
    same(r['explainResponse']['explanation'],e['explanation'])
    same([(h['_id'],h['_source'],h['_score'],h['sort'],h['_explanation']) for h in hits(r['esResponse'])],
         [(h['_id'],h['_source'],h['_score'],h['sort'],h['_explanation']) for h in rows])
    RESULTS['Java:'+slug]={'ids':EXPECTED[slug],'matched':e['matched']}


def java_check():
    for slug in JAVA_CASES:verify_java(slug)


def cleanup():
    call('DELETE','/'+INDEX,expected=(200,404));call('GET','/'+INDEX,expected=404)


if __name__=='__main__':
 {'prepare':prepare,'scoring':scoring,'edges':edges,'java':java_check,'cleanup':cleanup}[sys.argv[1]]()
