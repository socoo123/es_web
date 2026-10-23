#!/usr/bin/env python3
"""F15: local dictionary publication, historical terms, new writes and a frozen rebuild."""
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

PROJECT = pathlib.Path(__file__).resolve().parents[2]
ES = os.environ.get('ES_URL', 'http://127.0.0.1:19215').rstrip('/')
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18080').rstrip('/')
OLD, NEW = 'tut-f15-v1', 'tut-f15-v2'
CALLS = []
RESULTS = {}

def load(path): return json.loads((PROJECT / path).read_text())
def call(method, path, body=None, expected=200, app=False, ndjson=False):
    data = body.encode() if ndjson else (json.dumps(body, ensure_ascii=False).encode() if body is not None else None)
    request = urllib.request.Request((APP if app else ES) + path, data=data, method=method,
        headers={'Content-Type': 'application/x-ndjson' if ndjson else 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response: status, raw = response.status, response.read()
    except urllib.error.HTTPError as error: status, raw = error.code, error.read()
    result = json.loads(raw)
    row = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'target': 'Java' if app else 'ES',
           'method': method, 'path': path, 'request': body, 'status': status, 'response': result}
    CALLS.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
    assert status in (expected if isinstance(expected, tuple) else (expected,)), (method, path, status, expected)
    return result

def ids(response):
    assert response['timed_out'] is False and response['_shards']['failed'] == 0
    assert response['hits']['total']['relation'] == 'eq'
    hits = response['hits']['hits']; assert len(hits) == response['hits']['total']['value']
    return [h['_id'] for h in hits]

def tokens(response):
    return [(t['token'], t['position'], t['start_offset'], t['end_offset']) for t in response['tokens']]

def vector_tokens(response):
    assert response['found']
    return sorted([(term, t['position'], t['start_offset'], t['end_offset'])
                   for term, details in response['term_vectors']['name']['terms'].items() for t in details['tokens']],
                  key=lambda t: (t[1], t[0]))

def inventory():
    version = call('GET', '/')['version']
    assert (version['number'], version['lucene_version']) == ('9.4.0', '10.4.0')
    nodes = call('GET', '/_nodes/plugins')['nodes']; assert len(nodes) == 1
    plugins = [p for n in nodes.values() for p in n['plugins']]
    assert [(p['name'], p['version']) for p in plugins] == [('analysis-ik', '9.4.0')]

def settings(index):
    expected = load('search/f15/index.json')
    mapping = call('GET', '/' + index + '/_mapping')[index]['mappings']
    mapping['properties']['name'].setdefault('search_analyzer', mapping['properties']['name']['analyzer'])
    assert mapping == expected['mappings']
    config = call('GET', '/' + index + '/_settings')[index]['settings']['index']
    assert (config['number_of_shards'], config['number_of_replicas'], config['refresh_interval']) == ('1', '0', '-1')

def create(index):
    response = call('PUT', '/' + index, load('search/f15/index.json'))
    assert response['acknowledged'] and response['shards_acknowledged']
    health = call('GET', '/_cluster/health/' + index + '?wait_for_status=green&timeout=30s')
    assert not health['timed_out'] and health['status'] == 'green'

def bulk(filename, count):
    response = call('POST', '/' + OLD + '/_bulk', (PROJECT / ('data/f15/' + filename + '.ndjson')).read_text(), ndjson=True)
    assert not response['errors'] and len(response['items']) == count
    assert all(i['index']['status'] == 201 and i['index']['result'] == 'created' for i in response['items'])
    assert call('POST', '/' + OLD + '/_refresh')['_shards']['failed'] == 0
    assert call('GET', '/' + OLD + '/_count')['count'] == (9 if count == 9 else 11)

EXPECTED = {
    'baseline': {'brand': ['hz-brand'], 'bay': ['nj-bay', 'nj-scattered']},
    'file-only': {'brand': ['hz-brand'], 'bay': ['nj-bay', 'nj-scattered']},
    'loaded': {'brand': [], 'bay': []},
    'mixed': {'brand': ['hz-new'], 'bay': ['nj-new']},
    'rebuilt': {'brand': ['hz-brand', 'hz-new'], 'bay': ['nj-bay', 'nj-boundary', 'nj-new']},
}

def searches(phase, index):
    rows = {}
    for q in load('data/f15/judgments.json')['queries']:
        found = ids(call('POST', '/' + index + '/_search', load('search/f15/' + q['id'] + '.json')))
        assert found == EXPECTED[phase][q['id']], (phase, q['id'], found)
        relevant = q['finalRelevant'] if phase in {'mixed', 'rebuilt'} else q['initialRelevant']
        rows[q['id']] = {'hits': found, 'missed': sorted(set(relevant) - set(found)), 'unwanted': sorted(set(found) - set(relevant))}
    return rows

def observe(phase, index):
    active = phase in {'loaded', 'rebuilt'}
    streams = {}
    for text in ['云栖里', '星澜湾', '云栖里酒店', '星澜湾观景台', '星澜湾流科普馆', '星港澜庭湾畔酒店']:
        streams[text] = tokens(call('POST', '/' + index + '/_analyze', {'analyzer': 'ik_smart', 'text': text}))
    assert [t[0] for t in streams['云栖里']] == (['云栖里'] if active else ['云栖', '里'])
    assert [t[0] for t in streams['星澜湾']] == (['星澜湾'] if active else ['星', '澜', '湾'])
    vectors = {}
    for id in ['hz-brand', 'nj-bay', 'nj-boundary', 'nj-scattered']:
        vectors[id] = vector_tokens(call('POST', '/' + index + '/_termvectors/' + id, load('search/f15/termvectors.json')))
    # These were explicitly stored at write time. No artificial doc or analyzer override.
    if phase == 'rebuilt':
        assert '云栖里' in [t[0] for t in vectors['hz-brand']]
        assert '星澜湾' in [t[0] for t in vectors['nj-bay']]
        assert '星澜湾' in [t[0] for t in vectors['nj-boundary']]
    else:
        assert '云栖里' not in [t[0] for t in vectors['hz-brand']]
        assert '星澜湾' not in [t[0] for t in vectors['nj-bay']]
        assert '湾流' in [t[0] for t in vectors['nj-boundary']]
    result = {'analysis': streams, 'stored': vectors, 'queries': searches(phase, index)}
    RESULTS[phase] = result
    return result

def baseline():
    inventory()
    # Preflight prevents accidentally writing the baseline under the new dictionary.
    for text, expected in [('云栖里', ['云栖', '里']), ('星澜湾', ['星', '澜', '湾'])]:
        response = call('POST', '/_analyze', {'analyzer': 'ik_smart', 'text': text})
        assert [t['token'] for t in response['tokens']] == expected, 'Select empty, restart, then retry'
    create(OLD); bulk('attractions', 9); settings(OLD)
    observe('baseline', OLD)

def file_only():
    # File publication is performed by the wrapper, without a restart.
    for text, expected in [('云栖里', ['云栖', '里']), ('星澜湾', ['星', '澜', '湾'])]:
        response = call('POST', '/' + OLD + '/_analyze', {'analyzer': 'ik_smart', 'text': text})
        assert [t['token'] for t in response['tokens']] == expected
    RESULTS['file-only'] = {'queries': searches('file-only', OLD)}

def loaded_new():
    inventory(); observe('loaded', OLD)
    bulk('new-documents', 2)
    stored = {id: vector_tokens(call('POST', '/' + OLD + '/_termvectors/' + id, load('search/f15/termvectors.json')))
              for id in ['hz-new', 'nj-new']}
    assert '云栖里' in [t[0] for t in stored['hz-new']]
    assert '星澜湾' in [t[0] for t in stored['nj-new']]
    RESULTS['mixed'] = {'stored': stored, 'queries': searches('mixed', OLD)}

def rebuild():
    assert call('PUT', '/' + OLD + '/_settings', {'index.blocks.write': True})['acknowledged']
    create(NEW)
    response = call('POST', '/_reindex', load('search/f15/reindex.json'))
    assert not response['timed_out'] and not response['failures']
    assert (response['total'], response['created'], response['updated'], response['version_conflicts']) == (11, 11, 0, 0)
    assert call('POST', '/' + NEW + '/_refresh')['_shards']['failed'] == 0
    assert call('GET', '/' + NEW + '/_count')['count'] == 11
    settings(NEW); observe('rebuilt', NEW)

def java(views=('original', 'rebuilt'), phase=None):
    for view in views:
        index = OLD if view == 'original' else NEW
        for q in load('data/f15/judgments.json')['queries']:
            inp = {k: q[k] for k in ['q', 'cityCode', 'maxPriceFen']}; inp['view'] = view
            result = call('POST', '/api/attractions/dictionary-search', inp, app=True)
            assert result['conditions'] == inp and result['index'] == index
            rest = call('POST', '/' + index + '/_analyze', result['queryAnalysisRequest'])
            assert [(t['token'], t['position'], t['startOffset'], t['endOffset']) for t in result['queryTokens']] == tokens(rest)
            rest = call('POST', '/' + index + '/_termvectors/' + result['exampleId'], result['storedVectorRequest'])
            assert [(t['token'], t['position'], t['startOffset'], t['endOffset']) for t in result['storedTokens']] == vector_tokens(rest)
            assert result['storedVectors']['term_vectors'] == rest['term_vectors']
            rest = call('POST', '/' + index + '/_search', result['esRequest'])
            wanted = EXPECTED[phase or ('mixed' if view == 'original' else 'rebuilt')][q['id']]
            assert ids(rest) == wanted == [i['id'] for i in result['items']]
            assert result['total'] == len(wanted) and result['relation'] == 'eq'
            for item, hit in zip(result['items'], rest['hits']['hits'], strict=True):
                assert (item['name'], item['cityCode'], item['ticketPriceFen'], item['score'], item['sortValues']) == (
                    hit['_source']['name'], hit['_source']['city_code'], hit['_source']['ticket_price_fen'], hit['_score'], hit['sort'])

def cleanup():
    for index in [NEW, OLD]:
        call('DELETE', '/' + index, expected=(200, 404))
        call('GET', '/' + index, expected=404)

if __name__ == '__main__':
    actions = {'baseline': baseline, 'file-only': file_only, 'loaded-new': loaded_new, 'rebuild': rebuild, 'java': java, 'cleanup': cleanup}
    actions[sys.argv[1]]()
