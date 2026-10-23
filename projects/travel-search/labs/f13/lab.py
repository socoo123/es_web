#!/usr/bin/env python3
"""F13 reader labs. Print actual requests/responses; stop on a failed premise."""
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

PROJECT = pathlib.Path(__file__).resolve().parents[2]
INDEX = 'tut-f13-attractions'
ES = os.environ.get('ES_URL', 'http://127.0.0.1:19200').rstrip('/')
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18080').rstrip('/')
CALLS = []
FOUR = ['bj-mixed', 'bj-palace', 'bj-punctuation', 'bj-separated']
EXPECTED = [[], FOUR, FOUR[:3], [], ['bj-palace'], ['bj-dash', 'bj-mixed'], [], FOUR, [], [], ['sy-palace']]


def load(path):
    return json.loads((PROJECT / path).read_text())


def call(method, path, body=None, expected=200, app=False, ndjson=False):
    data = body.encode() if ndjson else (json.dumps(body, ensure_ascii=False).encode() if body is not None else None)
    req = urllib.request.Request((APP if app else ES) + path, data=data, method=method,
                                 headers={'Content-Type': 'application/x-ndjson' if ndjson else 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, raw = error.code, error.read()
    result = json.loads(raw)
    row = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'target': 'Java' if app else 'ES',
           'method': method, 'path': path, 'request': body, 'status': status, 'response': result}
    CALLS.append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)
    if status != expected:
        raise RuntimeError(f'{method} {path}: expected {expected}, received {status}')
    return result


def ids(response):
    assert not response['timed_out'] and response['_shards']['failed'] == 0
    assert response['hits']['total']['relation'] == 'eq'
    hits = response['hits']['hits']
    assert len(hits) == response['hits']['total']['value']
    return [hit['_id'] for hit in hits]


def tokens(response):
    return [(t['token'], t['position'], t['start_offset'], t['end_offset']) for t in response['tokens']]


def prepare():
    version = call('GET', '/')['version']
    assert (version['number'], version['lucene_version']) == ('9.4.0', '10.4.0')
    assert call('PUT', '/' + INDEX, load('search/f13/index.json'))['acknowledged']
    health = call('GET', '/_cluster/health/' + INDEX + '?wait_for_status=green&timeout=30s')
    assert health['status'] == 'green' and not health['timed_out']
    bulk = call('POST', '/' + INDEX + '/_bulk', (PROJECT / 'data/f13/attractions.ndjson').read_text(), ndjson=True)
    assert not bulk['errors'] and len(bulk['items']) == 8
    assert all(item['index']['status'] == 201 and item['index']['result'] == 'created' for item in bulk['items'])
    assert call('POST', '/' + INDEX + '/_refresh')['_shards']['failed'] == 0
    assert call('GET', '/' + INDEX + '/_count')['count'] == 8


def chain():
    mapping = call('GET', '/' + INDEX + '/_mapping')[INDEX]['mappings']
    # ES omits search_analyzer when it equals the index analyzer. Check the effective value.
    name = mapping['properties']['name']
    name.setdefault('search_analyzer', name['analyzer'])
    assert mapping == load('search/f13/index.json')['mappings']
    settings = call('GET', '/' + INDEX + '/_settings')[INDEX]['settings']['index']
    assert settings['analysis'] == load('search/f13/index.json')['settings']['analysis']
    assert (settings['number_of_shards'], settings['number_of_replicas'], settings['refresh_interval']) == ('1', '0', '-1')
    responses = [call('POST', '/' + INDEX + '/_analyze', load(str(p.relative_to(PROJECT))))
                 for p in sorted((PROJECT / 'search/f13/analyze').glob('*.json'))]
    base = [('故', 0, 0, 1), ('宫', 1, 1, 2), ('palace', 2, 3, 9), ('museum', 3, 10, 16), ('东', 4, 17, 18), ('门', 5, 18, 19)]
    assert tokens(responses[0]) == base and tokens(responses[2]) == base
    assert [t['token'] for t in responses[1]['tokens']] == ['故', '宫', 'Palace', 'MUSEUM', '东', '门']
    assert [t['token'] for t in responses[3]['tokens']] == ['故宫', 'Palace-MUSEUM（东门）']
    detail = responses[4]['detail']
    assert detail['custom_analyzer'] and detail['charfilters'][0]['name'] == 'html_strip'
    assert [t['token'] for t in detail['tokenizer']['tokens']] == ['故', '宫', 'Palace', 'MUSEUM', '东', '门']
    assert [t['token'] for t in detail['tokenfilters'][-1]['tokens']] == [t[0] for t in base]
    assert tokens(responses[5]) == [('故', 0, 0, 1), ('宫', 1, 1, 2)]
    assert tokens(responses[6]) == [('故宫', 0, 0, 2)]
    assert tokens(responses[7]) == [('故', 0, 0, 1), ('宫', 1, 2, 3)]
    assert tokens(responses[8]) == [('故', 0, 0, 1), ('宫', 1, 1, 2), ('😀', 2, 2, 4), ('palace', 3, 5, 11)]
    assert responses[9]['tokens'] == []
    return responses


def recall():
    for path, expected in zip(sorted((PROJECT / 'search/f13/queries').glob('*.json')), EXPECTED, strict=True):
        result = call('POST', '/' + INDEX + '/_search', load(str(path.relative_to(PROJECT))))
        assert ids(result) == expected, (path.name, ids(result), expected)
    source = call('GET', '/' + INDEX + '/_doc/bj-mixed')['_source']
    assert source == next(d for d in load('data/f13/attractions.json') if d['attraction_id'] == 'bj-mixed')


def java():
    expected = [[], FOUR, FOUR[:3], ['bj-dash', 'bj-mixed'], [], ['sy-palace'], []]
    for path, wanted in zip(sorted((PROJECT / 'search/f13/inputs').glob('*.json')), expected, strict=True):
        input = load(str(path.relative_to(PROJECT)))
        result = call('POST', '/api/attractions/analysis-search', input, app=True)
        assert result['conditions'] == input
        index_tokens = call('POST', '/' + INDEX + '/_analyze', result['indexAnalysisRequest'])
        query_tokens = call('POST', '/' + INDEX + '/_analyze', result['searchAnalysisRequest'])
        for key, raw in [('indexTokens', index_tokens), ('searchTokens', query_tokens)]:
            assert [(t['token'], t['position'], t['startOffset'], t['endOffset']) for t in result[key]] == tokens(raw)
        rest = call('POST', '/' + INDEX + '/_search', result['esRequest'])
        assert ids(rest) == wanted == [item['id'] for item in result['items']]
        assert result['total'] == len(wanted) and result['relation'] == 'eq'
        for item, hit in zip(result['items'], rest['hits']['hits'], strict=True):
            assert item['name'] == hit['_source']['name']
            assert item['ticketPriceFen'] == hit['_source']['ticket_price_fen']
            assert item['cityCode'] == hit['_source']['city_code']
            assert item['score'] == hit['_score'] and item['sortValues'] == hit['sort']


def cleanup():
    try:
        call('DELETE', '/' + INDEX)
    except RuntimeError:
        if CALLS[-1]['status'] != 404:
            raise
    call('GET', '/' + INDEX, expected=404)


if __name__ == '__main__':
    {'prepare': prepare, 'chain': chain, 'recall': recall, 'java': java, 'cleanup': cleanup}[sys.argv[1]]()
