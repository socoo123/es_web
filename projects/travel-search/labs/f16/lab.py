#!/usr/bin/env python3
"""F16 real ES/Java evidence. Each request and full response is emitted as JSONL."""
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

PROJECT = pathlib.Path(__file__).resolve().parents[2]
ES = os.environ.get('ES_URL', 'http://127.0.0.1:19216').rstrip('/')
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18080').rstrip('/')
INDEX, SET = 'tut-f16-attractions', 'tut-f16-names'
CALLS, RESULTS = [], {}


def load(name): return json.loads((PROJECT / ('search/f16/' + name + '.json')).read_text())

def call(method, path, body=None, expected=200, app=False, ndjson=False):
    data = body.encode() if ndjson else json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    request = urllib.request.Request((APP if app else ES) + path, data=data, method=method,
        headers={'Content-Type': 'application/x-ndjson' if ndjson else 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response: status, raw = response.status, response.read()
    except urllib.error.HTTPError as error: status, raw = error.code, error.read()
    value = json.loads(raw)
    row = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'target': 'Java' if app else 'ES',
           'method': method, 'path': path, 'request': body, 'status': status, 'response': value}
    CALLS.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
    assert status in (expected if isinstance(expected, tuple) else (expected,)), (method, path, status, expected)
    return value


def ids(value):
    assert not value['timed_out'] and value['_shards']['failed'] == 0
    hits = value['hits']; assert hits['total']['relation'] == 'eq' and len(hits['hits']) == hits['total']['value']
    return [h['_id'] for h in hits['hits']]


def search(name, expected):
    found = ids(call('POST', '/' + INDEX + '/_search', load(name)))
    assert found == expected, (name, found, expected)
    RESULTS[name] = found
    return found


def tokens(value):
    stream = value['detail']['tokenfilters'][-1]['tokens']
    return [(t['token'], t['position'], t['positionLength'], t['start_offset'], t['end_offset'], t['type']) for t in stream]


def analyze(analyzer, text):
    return call('POST', '/' + INDEX + '/_analyze', {'analyzer': analyzer, 'text': text,
        'explain': True})


def refresh(): assert call('POST', '/' + INDEX + '/_refresh')['_shards']['failed'] == 0


def configuration():
    config = load('index')
    mapping = call('GET', '/' + INDEX + '/_mapping')[INDEX]['mappings']
    # ES omits search_analyzer equal to analyzer and default array gap=100.
    for field in mapping['properties'].values():
        if field.get('type') == 'text': field.setdefault('search_analyzer', field['analyzer'])
    mapping['properties']['aliases'].setdefault('position_increment_gap', 100)
    assert mapping == config['mappings'], mapping
    settings = call('GET', '/' + INDEX + '/_settings')[INDEX]['settings']['index']
    assert (settings['number_of_shards'], settings['number_of_replicas'], settings['refresh_interval']) == ('1','0','-1')
    analysis = settings['analysis']
    for key, value in config['settings']['analysis']['analyzer'].items(): assert analysis['analyzer'][key] == value
    for key, value in config['settings']['analysis']['filter'].items():
        expected = {k: str(v).lower() if isinstance(v, bool) else v for k,v in value.items()}
        assert analysis['filter'][key] == expected, (key, analysis['filter'][key], expected)


CN = ['bj-palace','bj-theme','bj-traditional','bj-wall']


def prepare():
    v = call('GET', '/')['version']; assert (v['number'],v['lucene_version']) == ('9.4.0','10.4.0')
    nodes = call('GET', '/_nodes/plugins')['nodes']; assert len(nodes) == 1
    assert [(p['name'],p['version']) for n in nodes.values() for p in n['plugins']] == [('analysis-icu','9.4.0')]
    assert call('PUT', '/_synonyms/' + SET, load('synonyms'), expected=201)['result'] == 'created'
    r = call('PUT', '/' + INDEX, load('index')); assert r['acknowledged'] and r['shards_acknowledged']
    r = call('GET', '/_cluster/health/' + INDEX + '?wait_for_status=green&timeout=30s')
    assert not r['timed_out'] and r['status'] == 'green'
    r = call('POST', '/' + INDEX + '/_bulk', (PROJECT/'data/f16/attractions.ndjson').read_text(), ndjson=True)
    assert not r['errors'] and len(r['items']) == 11
    assert all(i['create']['status'] == 201 and i['create']['result'] == 'created' for i in r['items'])
    refresh(); assert call('GET', '/' + INDEX + '/_count')['count'] == 11
    configuration()
    for a,q in [('travel_plain','紫禁城'),('travel_base','紫禁城'),('travel_search','紫禁城'),
                ('travel_search','故宮'),('travel_late','故宮')]:
        RESULTS[a+':'+q] = tokens(analyze(a,q))
    for name, expected in [('plain-cn',['bj-wall']),('aliases-cn',['bj-palace','bj-wall']),('graph-cn',CN),
                           ('graph-sy',['sy-palace']),('aliases-sy',[]),('graph-trad',CN),
                           ('late-trad',['bj-palace','bj-theme','bj-traditional'])]: search(name,expected)


def graph():
    for a,q in [('travel_base','PALACE museum'),('travel_search','PALACE museum'),('travel_late','PALACE museum')]:
        RESULTS[a] = tokens(analyze(a,q))
    assert RESULTS['travel_search'] == [('forbidden',0,1,0,6,'SYNONYM'),('palace',0,2,0,6,'<ALPHANUM>'),
                                       ('city',1,1,0,6,'SYNONYM'),('museum',2,1,7,13,'<ALPHANUM>')]
    for name, expected in [('graph-en',['bj-palace','bj-tail']),('loose-en',['bj-gap','bj-palace','bj-reverse','bj-tail']),
                           ('phrase-en',['bj-palace']),('late-en',[])]: search(name,expected)
    for name in ['graph-en','loose-en','phrase-en']:
        r = call('POST', '/' + INDEX + '/_validate/query?explain=true', {'query':load(name)['query']})
        assert r['valid'] and r['_shards']['failed'] == 0
        RESULTS['rewrite:'+name] = r['explanations']
    bad = call('POST', '/' + INDEX + '/_analyze', load('bad-stop'), expected=400)
    assert 'completely eliminated' in json.dumps(bad)
    search('graph-en',['bj-palace','bj-tail'])


def changes():
    search('plain-trad',[]); search('aliases-trad',CN)
    base = analyze('travel_base','故宮文創館')
    assert [t[0] for t in tokens(base)] == list('故宫文创馆')
    before = call('GET', '/' + INDEX + '/_doc/bj-traditional')
    assert before['_source']['name'] == '故宮文創館'
    vectors = call('POST', '/' + INDEX + '/_termvectors/bj-traditional', load('vectors'))
    assert set(vectors['term_vectors']['name']['terms']) == set('故宫文创馆')
    search('alias-new',[])
    assert call('POST', '/' + INDEX + '/_update/bj-palace', load('alias-update'))['result'] == 'updated'
    search('alias-new',[])  # auto-refresh is disabled: search still sees old aliases
    refresh(); search('alias-new',['bj-palace'])
    alias_doc = call('GET', '/' + INDEX + '/_doc/bj-palace')['_source']
    assert alias_doc['aliases'] == ['紫禁城','皇家旧宫']
    search('synonym-new',[])
    old_analysis = tokens(analyze('travel_search','皇城旧称'))
    updated = call('PUT', '/_synonyms/' + SET, load('synonyms-updated'))
    assert updated['result'] == 'updated'
    reloads = updated['reload_analyzers_details']
    assert reloads['_shards']['failed'] == 0 and len(reloads['reload_details']) == 1
    assert set(reloads['reload_details'][0]['reloaded_analyzers']) == {'travel_search','travel_late'}
    new_analysis = tokens(analyze('travel_search','皇城旧称'))
    assert new_analysis != old_analysis
    search('synonym-new',CN)
    after = call('GET', '/' + INDEX + '/_doc/bj-traditional')
    assert {k:before[k] for k in ['_seq_no','_primary_term','_version','_source']} == {k:after[k] for k in ['_seq_no','_primary_term','_version','_source']}
    after_vectors = call('POST', '/' + INDEX + '/_termvectors/bj-traditional', load('vectors'))
    assert after_vectors['term_vectors'] == vectors['term_vectors']
    assert call('GET', '/' + INDEX + '/_count')['count'] == 11
    # A used synonym set cannot be removed; restore no state because deletion was rejected.
    call('DELETE', '/_synonyms/' + SET, expected=400)
    search('synonym-new',CN)
    RESULTS['name_terms_unchanged_after_query_reload'] = True
    RESULTS['stored_source_unchanged_after_query_reload'] = True


def java_check():
    cases = [('紫禁城','BJ','aliases',['bj-palace','bj-wall']),('紫禁城','BJ','graph',CN),
             ('紫禁城','SY','graph',['sy-palace']),('PALACE museum','BJ','graph',['bj-palace','bj-tail']),
             ('PALACE museum','BJ','loose',['bj-gap','bj-palace','bj-reverse','bj-tail']),
             ('PALACE museum','BJ','phrase',['bj-palace']),('故宮','BJ','late',['bj-palace','bj-theme','bj-traditional']),
             ('皇城旧称','BJ','graph',CN)]
    for q,city,mode,wanted in cases:
        input = {'q':q,'cityCode':city,'maxPriceFen':10000,'mode':mode}
        result = call('POST', '/api/attractions/synonym-search', input, app=True)
        assert result['conditions'] == input and [i['id'] for i in result['items']] == wanted
        for kind in ['base','query']:
            request = dict(result[kind+'AnalysisRequest']); assert 'index' not in request
            rest = call('POST', '/' + INDEX + '/_analyze', request)
            assert rest == result[kind+'Analysis']
            converted = [(t['token'],t['position'],t['positionLength'],t['startOffset'],t['endOffset'],t['type']) for t in result[kind+'Tokens']]
            assert converted == tokens(rest)
        request = dict(result['esRequest']); assert 'index' not in request
        fixture = load({'plain':'plain-cn','aliases':'aliases-cn','graph':'graph-cn',
                        'phrase':'phrase-en','loose':'loose-en','late':'late-trad'}[mode])
        fixture['query']['bool']['must'][0]['multi_match']['query'] = q
        fixture['query']['bool']['filter'][0]['term']['city_code'] = city
        for clause in fixture['query']['bool']['filter']:
            if 'term' in clause:
                clause['term'] = {key:{'value':value} for key,value in clause['term'].items()}
        fixture['sort'] = [{'attraction_id':{'order':'asc'}}]
        assert request == fixture, (request, fixture)
        rest = call('POST', '/' + INDEX + '/_search', request)
        assert ids(rest) == wanted and rest['hits']['total'] == {'value':result['total'],'relation':result['relation']}
        for h,card in zip(rest['hits']['hits'], result['items']):
            s=h['_source']
            assert card == {'id':h['_id'],'name':s['name'],'nameEn':s['name_en'],'aliases':s['aliases'],
                            'cityCode':s['city_code'],'ticketPriceFen':s['ticket_price_fen'],'currency':s['currency'],
                            'status':s['status'],'score':h['_score'],'sortValues':h['sort']}
        RESULTS[q+':'+city+':'+mode] = wanted


def cleanup():
    for path in ['/'+INDEX, '/_synonyms/'+SET]:
        call('DELETE',path,expected=(200,404))
        call('GET',path,expected=404)


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv)>1 else ''
    try:
        {'prepare':prepare,'graph':graph,'changes':changes,'java':java_check,'cleanup':cleanup}[stage]()
        print(json.dumps({'stage':stage,'status':'passed','client_requests':len(CALLS),'results':RESULTS},ensure_ascii=False),flush=True)
    except BaseException:
        print(json.dumps({'stage':stage,'status':'failed','client_requests':len(CALLS)},ensure_ascii=False),flush=True)
        raise
