#!/usr/bin/env python3
"""F18 reproducible REST/Java lab. Emit complete requests/responses, assert relative behavior."""
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
ES = os.environ.get('ES_URL', 'http://127.0.0.1:19218').rstrip('/')
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18080').rstrip('/')
INDEX = 'tut-f18-attractions'
CALLS, RESULTS = [], {}
SCORED = ['hz-four', 'hz-night', 'hz-short', 'hz-twice', 'hz-once', 'hz-long']
FILTERED = sorted(SCORED)
RARE = ['hz-night', 'hz-four', 'hz-short', 'hz-twice', 'hz-once', 'hz-long']


def load(slug):
    return json.loads((PROJECT / ('search/f18/' + slug + '.json')).read_text())


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
    # The client serializes explanation values as doubles; REST prints float decimals.
    if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
        close(a, b)
    elif isinstance(a, dict) and isinstance(b, dict):
        assert a.keys() == b.keys(), (a.keys(), b.keys())
        for key in a:
            same(a[key], b[key])
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            same(x, y)
    else:
        assert a == b, (a, b)


def flatten(node):
    yield node
    for child in node.get('details', []):
        yield from flatten(child)


def value(node, prefix):
    matches = [n['value'] for n in flatten(node) if n['description'].startswith(prefix)]
    assert len(matches) == 1, (prefix, matches)
    return matches[0]


def terms(node):
    out = {}
    for n in flatten(node):
        if not n['description'].startswith('weight(description:'):
            continue
        term = n['description'].split('weight(description:', 1)[1].split(' in ', 1)[0]
        out[term] = {k: value(n, prefix) for k, prefix in {
            'freq': 'freq,', 'n': 'n,', 'N': 'N,', 'dl': 'dl,', 'avgdl': 'avgdl,',
            'k1': 'k1,', 'b': 'b,', 'boost': 'boost', 'idf': 'idf,', 'tf': 'tf,'}.items()}
        p = out[term]
        close(p['idf'], math.log(1 + (p['N'] - p['n'] + .5) / (p['n'] + .5)))
        close(p['tf'], p['freq'] / (p['freq'] + p['k1'] * (1 - p['b'] + p['b'] * p['dl'] / p['avgdl'])))
        close(n['value'], p['boost'] * p['idf'] * p['tf'])
    return out


def refresh():
    assert call('POST', '/' + INDEX + '/_refresh')['_shards']['failed'] == 0


def hits(r):
    assert not r['timed_out'] and r['_shards']['failed'] == 0
    assert r['hits']['total']['relation'] == 'eq'
    assert len(r['hits']['hits']) == r['hits']['total']['value']
    for h in r['hits']['hits']:
        assert h['_id'] == h['_source']['attraction_id']
        close(h['_score'], h['_explanation']['value'])
        close(h['sort'][0], h['_score'])
        assert h['sort'][1] == h['_id']
    return r['hits']['hits']


def search(slug, ids):
    r = call('POST', '/' + INDEX + '/_search', load(slug))
    rows = hits(r)
    assert [h['_id'] for h in rows] == ids, (slug, [h['_id'] for h in rows], ids)
    RESULTS[slug] = [{'id': h['_id'], 'score': h['_score'], 'terms': terms(h['_explanation'])} for h in rows]
    return r


def explain(id, query=None):
    body = query or load('explain')
    r = call('POST', '/' + INDEX + '/_explain/' + id, body)
    assert r['_id'] == id
    RESULTS['explain:' + id] = {'matched': r['matched'], 'value': r['explanation']['value'], 'terms': terms(r['explanation'])}
    return r


def prepare():
    v = call('GET', '/')['version']
    assert (v['number'], v['lucene_version']) == ('9.4.0', '10.4.0')
    nodes = call('GET', '/_nodes/plugins')['nodes']
    assert len(nodes) == 1 and not next(iter(nodes.values()))['plugins']
    r = call('PUT', '/' + INDEX, load('index'))
    assert r['acknowledged'] and r['shards_acknowledged']
    h = call('GET', '/_cluster/health/' + INDEX + '?wait_for_status=green&timeout=30s')
    assert not h['timed_out'] and h['status'] == 'green'
    r = call('POST', '/' + INDEX + '/_bulk', (PROJECT / 'data/f18/attractions.ndjson').read_text(), ndjson=True)
    assert not r['errors'] and len(r['items']) == 10
    assert all(x['create']['status'] == 201 and x['create']['result'] == 'created' for x in r['items'])
    refresh()
    assert call('GET', '/' + INDEX + '/_count')['count'] == 10
    m = call('GET', '/' + INDEX + '/_mapping')[INDEX]['mappings']
    expected = copy.deepcopy(load('index')['mappings'])
    # Explicit defaults may be omitted by ES mapping serialization.
    m['properties']['description'].setdefault('norms', True)
    m['properties']['description'].setdefault('index_options', 'positions')
    assert m == expected, (m, expected)
    s = call('GET', '/' + INDEX + '/_settings')[INDEX]['settings']['index']
    assert (s['number_of_shards'], s['number_of_replicas'], s['refresh_interval']) == ('1', '0', '-1')
    assert s['analysis'] == load('index')['settings']['analysis']
    bm = s['similarity']['lesson_bm25']
    assert bm['type'] == 'BM25' and float(bm['k1']) == 1.2 and float(bm['b']) == .75 and str(bm['discount_overlaps']).lower() == 'true'
    token = call('POST', '/' + INDEX + '/_analyze', load('analyze'))['tokens']
    assert [t['token'] for t in token] == ['西湖', '湖景']
    RESULTS['analyze'] = token
    for id, freq, dl in [('hz-short', 1, 2), ('hz-once', 1, 8), ('hz-twice', 2, 8), ('hz-four', 4, 8), ('hz-long', 1, 16), ('hz-night', 1, 2)]:
        v = call('POST', '/' + INDEX + '/_termvectors/' + id, load('termvectors'))['term_vectors']['description']
        assert v['terms']['西湖']['term_freq'] == freq
        assert sum(t['term_freq'] for t in v['terms'].values()) == dl
        assert v['terms']['西湖']['doc_freq'] == 8
        assert v['field_statistics']['doc_count'] == 9 and v['field_statistics']['sum_ttf'] == 50
        RESULTS['vector:' + id] = v
    r = search('scored', SCORED)
    scores = {h['_id']: h['_score'] for h in hits(r)}
    assert scores['hz-four'] > scores['hz-twice'] > scores['hz-once']
    assert scores['hz-twice'] / scores['hz-once'] < 2
    assert scores['hz-four'] / scores['hz-twice'] < scores['hz-twice'] / scores['hz-once']
    assert scores['hz-short'] > scores['hz-once'] > scores['hz-long']
    for h in hits(r):
        p = terms(h['_explanation'])['西湖']
        assert (p['N'], p['n'], p['k1'], p['b']) == (9, 8, 1.2, .75)
        close(p['boost'], 2.2)
        close(p['avgdl'], 50 / 9)
    for id in ['hz-short', 'hz-long', 'hz-closed', 'hz-other']:
        e = explain(id)
        assert e['matched'] == (id in SCORED)
        if id in SCORED:
            close(e['explanation']['value'], scores[id])


def contexts():
    r = search('rare', RARE)
    p = terms(hits(r)[0]['_explanation'])
    assert p['西湖']['n'] == 8 and p['夜游']['n'] == 1
    assert p['夜游']['idf'] > p['西湖']['idf']
    e = explain('hz-night', {'query': load('rare')['query']})
    close(e['explanation']['value'], hits(r)[0]['_score'])
    r = search('filtered', FILTERED)
    assert all(h['_score'] == 0 and not terms(h['_explanation']) for h in hits(r))
    e = explain('hz-short', {'query': load('filtered')['query']})
    assert e['matched'] and e['explanation']['value'] == 0
    r = search('city-scored', SCORED)
    assert all(any(n['description'].startswith('weight(city_code:HZ') for n in flatten(h['_explanation'])) for h in hits(r))
    e = explain('hz-short', {'query': load('city-scored')['query']})
    close(e['explanation']['value'], hits(r)[2]['_score'])


def unrelated():
    before = search('scored', SCORED)
    doc = call('GET', '/' + INDEX + '/_doc/hz-short')
    r = call('POST', '/' + INDEX + '/_bulk', (PROJECT / 'data/f18/unrelated.ndjson').read_text(), ndjson=True)
    assert not r['errors'] and len(r['items']) == 6
    assert all(x['create']['status'] == 201 for x in r['items'])
    old_view = search('scored', SCORED)
    assert [h['_score'] for h in hits(before)] == [h['_score'] for h in hits(old_view)]
    refresh()
    assert call('GET', '/' + INDEX + '/_count')['count'] == 16
    after = search('scored', SCORED)
    for old, new in zip(hits(before), hits(after)):
        p = terms(new['_explanation'])['西湖']
        assert (p['N'], p['n']) == (15, 8)
        close(p['avgdl'], 62 / 15)
        assert old['_score'] != new['_score']
    e = explain('hz-short')
    close(e['explanation']['value'], hits(after)[2]['_score'])
    v = call('POST', '/' + INDEX + '/_termvectors/hz-short', load('termvectors'))['term_vectors']['description']
    assert v['field_statistics']['doc_count'] == 15 and v['field_statistics']['sum_ttf'] == 62
    unchanged = call('GET', '/' + INDEX + '/_doc/hz-short')
    assert unchanged == doc
    RESULTS['unrelated'] = {'before': [h['_score'] for h in hits(before)], 'after': [h['_score'] for h in hits(after)],
                            'same_ids': SCORED, 'same_original_doc': True, 'N': 15, 'n': 8, 'avgdl': 62 / 15}


def canonical(x):
    if isinstance(x, list):
        return [canonical(v) for v in x]
    if not isinstance(x, dict):
        return x
    x = {k: canonical(v) for k, v in x.items()}
    if 'sort' in x:
        x['sort'] = [{k: v['order'] if isinstance(v, dict) and set(v) == {'order'} else v for k, v in s.items()} for s in x['sort']]
    return x


def verify_java(slug, expected):
    input = load('input-' + slug)
    r = call('POST', '/api/attractions/score-search', input, app=True)
    assert r['conditions'] == input
    assert canonical(r['esRequest']) == canonical(load(slug)), (r['esRequest'], load(slug))
    actual = call('POST', '/' + INDEX + '/_search', r['esRequest'])
    rows = hits(actual)
    assert [h['_id'] for h in rows] == expected
    cards = []
    for h in rows:
        s = h['_source']
        cards.append({'id': h['_id'], 'name': s['name'], 'description': s['description'], 'cityCode': s['city_code'],
                      'ticketPriceFen': s['ticket_price_fen'], 'currency': s['currency'], 'status': s['status'],
                      'score': h['_score'], 'sortValues': h['sort'], 'explanation': h['_explanation']})
    same(r['items'], cards)
    assert r['total'] == len(cards) and r['relation'] == 'eq'
    assert r['explainRequest'] == {'query': r['esRequest']['query']}
    assert r['explainPath'] == '/' + INDEX + '/_explain/' + input['explainId']
    e = call('POST', r['explainPath'], r['explainRequest'])
    assert r['explainResponse']['matched'] == e['matched']
    assert r['explainResponse']['_id'] == e['_id']
    same(r['explainResponse']['explanation'], e['explanation'])
    same([(h['_id'], h['_source'], h['_score'], h['sort'], h['_explanation']) for h in hits(r['esResponse'])],
         [(h['_id'], h['_source'], h['_score'], h['sort'], h['_explanation']) for h in rows])
    RESULTS['Java:' + slug] = {'ids': expected, 'matched': e['matched'], 'score': e['explanation']['value']}


def java_check():
    for slug, expected in [('scored', SCORED), ('filtered', FILTERED), ('city-scored', SCORED), ('rare', RARE),
                           ('other-city', ['sz-copy']), ('zero-budget', ['hz-short']), ('empty', [])]:
        verify_java(slug, expected)


def cleanup():
    call('DELETE', '/' + INDEX, expected=(200, 404))
    call('GET', '/' + INDEX, expected=404)


if __name__ == '__main__':
    {'prepare': prepare, 'contexts': contexts, 'unrelated': unrelated, 'java': java_check, 'cleanup': cleanup}[sys.argv[1]]()
