#!/usr/bin/env python3
"""F19: complete real requests and relative ranking/candidate/explanation assertions."""
import copy
import datetime
import json
import math
import os
import pathlib
import sys
import urllib.error
import urllib.request

PROJECT = pathlib.Path(__file__).resolve().parents[2]
ES = os.environ.get('ES_URL', 'http://127.0.0.1:19219').rstrip('/')
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18080').rstrip('/')
INDEX = 'tut-f19-attractions'
CALLS, RESULTS = [], {}
EXACT = ['hz-exact']
PHRASE = ['hz-exact', 'hz-both', 'hz-prefix']
NAME = ['hz-exact', 'hz-scatter', 'hz-both', 'hz-prefix']
DESCRIPTION = ['hz-description', 'hz-both']
SUM = ['hz-both', 'hz-description', 'hz-exact', 'hz-scatter', 'hz-prefix']
BEST = ['hz-description', 'hz-both', 'hz-exact', 'hz-scatter', 'hz-prefix']
TUNED = ['hz-exact', 'hz-both', 'hz-prefix', 'hz-description', 'hz-scatter']
WEIGHTED = ['hz-exact', 'hz-both', 'hz-prefix', 'hz-scatter', 'hz-description']
OPTIONAL = SUM + ['hz-cruise', 'hz-noise', 'hz-photo', 'hz-split']
EXPECTED = dict(exact=EXACT, phrase=PHRASE, description=DESCRIPTION, sum=SUM, best=BEST, tie=SUM,
    tuned=TUNED, weighted=WEIGHTED, overweight=WEIGHTED, optional=OPTIONAL, required=SUM,
    spaced=['hz-both', 'hz-exact', 'hz-prefix', 'hz-description', 'hz-scatter'], empty=[])
EXPECTED.update({'name-and': NAME, 'night-low': ['hz-cruise', 'hz-photo'], 'night-medium': ['hz-photo', 'hz-cruise'],
    'night-high': ['hz-photo', 'hz-cruise'], 'night-tuned': ['hz-photo', 'hz-cruise'], 'other-city': ['sz-exact'], 'zero-budget': ['hz-exact'],
    'mandatory-phrase': PHRASE, 'multi-best': BEST, 'multi-tie': SUM, 'multi-most': SUM})
JAVA_CASES = ['sum', 'best', 'tie', 'tuned', 'optional', 'required', 'weighted', 'overweight',
              'night-low', 'night-medium', 'night-high', 'night-tuned', 'spaced', 'other-city', 'zero-budget', 'empty']


def load(slug):
    return json.loads((PROJECT / ('search/f19/' + slug + '.json')).read_text())


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
    r = call('POST', '/' + INDEX + '/_search', load(slug))
    rows = hits(r)
    assert [h['_id'] for h in rows] == EXPECTED[slug], (slug, [h['_id'] for h in rows], EXPECTED[slug])
    RESULTS[slug] = [{'id': h['_id'], 'score': h['_score']} for h in rows]
    return {h['_id']: h for h in rows}


def explain(id, slug='tuned', matched=True):
    r = call('POST', '/' + INDEX + '/_explain/' + id, {'query': load(slug)['query']})
    assert r['_id'] == id and r['matched'] == matched, (slug, id, r)
    if not matched: assert r['explanation']['value'] == 0
    return r


def prepare():
    v = call('GET', '/')['version']; assert (v['number'], v['lucene_version']) == ('9.4.0', '10.4.0')
    n = call('GET', '/_nodes/plugins')['nodes']; assert len(n) == 1 and not next(iter(n.values()))['plugins']
    r = call('PUT', '/' + INDEX, load('index')); assert r['acknowledged'] and r['shards_acknowledged']
    r = call('GET', '/_cluster/health/' + INDEX + '?wait_for_status=green&timeout=30s')
    assert not r['timed_out'] and r['status'] == 'green'
    r = call('POST', '/' + INDEX + '/_bulk', (PROJECT / 'data/f19/attractions.ndjson').read_text(), ndjson=True)
    assert not r['errors'] and len(r['items']) == 12
    assert all(x['create']['status'] == 201 and x['create']['result'] == 'created' for x in r['items'])
    assert call('POST', '/' + INDEX + '/_refresh')['_shards']['failed'] == 0
    assert call('GET', '/' + INDEX + '/_count')['count'] == 12
    assert call('GET', '/' + INDEX + '/_mapping')[INDEX]['mappings'] == load('index')['mappings']
    s = call('GET', '/' + INDEX + '/_settings')[INDEX]['settings']['index']
    assert (s['number_of_shards'], s['number_of_replicas'], s['refresh_interval']) == ('1','0','-1')
    assert s['analysis'] == load('index')['settings']['analysis']
    bm = s['similarity']['lesson_bm25']
    assert bm['type'] == 'BM25' and float(bm['k1']) == 1.2 and float(bm['b']) == .75 and str(bm['discount_overlaps']).lower() == 'true'
    t = call('POST', '/' + INDEX + '/_analyze', load('analyze'))['tokens']
    assert [x['token'] for x in t] == list('西湖博物馆') and [x['position'] for x in t] == list(range(5))
    v = call('POST', '/' + INDEX + '/_termvectors/hz-prefix', load('termvectors'))['term_vectors']
    assert sorted(v['name.exact']['terms']) == ['西湖博物馆东馆']
    assert [x[1] for x in sorted((pos['position'], term) for term, data in v['name']['terms'].items() for pos in data['tokens'])] == list('西湖博物馆东馆')
    RESULTS['analyze'] = t; RESULTS['stored_terms'] = v
    for slug in ['exact', 'phrase', 'name-and', 'description']: search(slug)
    explain('hz-scatter', 'phrase', False)


def weights():
    rows = {slug: search(slug) for slug in ['sum','best','tie','tuned','weighted','overweight','night-low','night-medium','night-high','night-tuned','spaced','multi-best','multi-tie','multi-most']}
    for other, base in [('multi-best','best'),('multi-tie','tie'),('multi-most','sum')]:
        same([(i,h['_score']) for i,h in rows[other].items()], [(i,h['_score']) for i,h in rows[base].items()])
    a = rows['best']['hz-both']['_explanation']
    best = next(n for n in flatten(a) if n['description'] == 'max of:')
    assert len(best['details']) == 2
    scores = [n['value'] for n in best['details']]
    close(rows['sum']['hz-both']['_score'], sum(scores))
    close(rows['best']['hz-both']['_score'], max(scores))
    close(rows['tie']['hz-both']['_score'], max(scores) + .1 * min(scores))
    roots = rows['tuned']['hz-exact']['_explanation']['details']
    contributions = [{'value':n['value'],'description':n['description']} for n in roots if n['value'] > 0]
    assert len(contributions) == 3 and contributions[-1]['value'] == 8
    close(rows['weighted']['hz-scatter']['_score'], rows['best']['hz-scatter']['_score'] * 3)
    close(rows['night-high']['hz-photo']['_score'], rows['night-low']['hz-photo']['_score'] * 50)
    assert rows['night-high']['hz-cruise']['_score'] == rows['night-low']['hz-cruise']['_score']
    assert rows['tuned']['hz-exact']['_score'] > rows['spaced']['hz-exact']['_score']
    close(rows['tuned']['hz-exact']['_score'] - rows['spaced']['hz-exact']['_score'],8)
    RESULTS['both_combination']={'field_scores':scores,'sum':rows['sum']['hz-both']['_score'],'best':rows['best']['hz-both']['_score'],'tie':rows['tie']['hz-both']['_score']}
    RESULTS['exact_contributions']=contributions
    for slug,id in [('best','hz-both'),('sum','hz-both'),('tie','hz-both'),('tuned','hz-exact'),('weighted','hz-scatter'),('night-medium','hz-photo')]:
        e=explain(id,slug);close(e['explanation']['value'],rows[slug][id]['_score'])


def gates():
    optional, required, mandatory = search('optional'), search('required'), search('mandatory-phrase')
    assert set(required) == set(TUNED) and set(mandatory) < set(required)
    assert all(optional[i]['_score'] == 0 for i in ['hz-cruise','hz-noise','hz-photo','hz-split'])
    explain('hz-noise','optional',True);explain('hz-noise','required',False)
    for id in ['hz-closed','hz-expensive','sz-exact']:explain(id,'tuned',False)


def canonical(x):
    if isinstance(x,list):return [canonical(v) for v in x]
    if not isinstance(x,dict):return x
    x={k:canonical(v) for k,v in x.items()}
    if 'sort' in x:
        x['sort']=[{k:v['order'] if isinstance(v,dict) and set(v)=={'order'} else v for k,v in s.items()} for s in x['sort']]
    return x


def verify_java(slug):
    i=load('input-'+slug);r=call('POST','/api/attractions/weight-search',i,app=True)
    assert r['conditions']==i and canonical(r['esRequest'])==canonical(load(slug)), (slug,r['esRequest'],load(slug))
    rows=hits(call('POST','/'+INDEX+'/_search',r['esRequest']))
    assert [h['_id'] for h in rows]==EXPECTED[slug]
    cards=[]
    for h in rows:
        s=h['_source'];cards.append(dict(id=h['_id'],name=s['name'],description=s['description'],cityCode=s['city_code'],
            ticketPriceFen=s['ticket_price_fen'],currency=s['currency'],status=s['status'],score=h['_score'],sortValues=h['sort'],explanation=h['_explanation']))
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
    {'prepare':prepare,'weights':weights,'gates':gates,'java':java_check,'cleanup':cleanup}[sys.argv[1]]()
