#!/usr/bin/env python3
"""F44: fixed request contrasts, one diagnostic window, controlled protection/recovery."""
import argparse
import concurrent.futures
import copy
import datetime as dt
import gzip
import hashlib
import json
import pathlib
import subprocess
import threading
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
URL = 'http://127.0.0.1:20844'
MAIN = 'tut-f44-attractions'
FAN = 'tut-f44-fanout'
LOCK = threading.Lock()
OUT = None
SEQ = 0


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load(name):
    return json.loads((ROOT / 'search/f44' / (name + '.json')).read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def api(method, path, body=None, opaque='f44-lab', accept=(200,)):
    global SEQ
    raw = body if isinstance(body, bytes) else (json.dumps(body, ensure_ascii=False).encode() if body is not None else None)
    headers = {'Content-Type': 'application/x-ndjson' if isinstance(body, bytes) else 'application/json', 'X-Opaque-Id': opaque}
    start_at, start = now(), time.perf_counter()
    request = urllib.request.Request(URL + path, data=raw, headers=headers, method=method)
    try:
        response = urllib.request.urlopen(request, timeout=120)
    except urllib.error.HTTPError as e:
        response = e
    with response:
        data = response.read()
        try:
            value = json.loads(data)
        except json.JSONDecodeError:
            value = data.decode()
        result = {'at': start_at, 'finished_at': now(), 'method': method, 'path': path,
                  'opaque': opaque, 'status': response.status, 'client_ms': (time.perf_counter()-start)*1000,
                  'response_bytes': len(data), 'request': '<NDJSON>' if isinstance(body, bytes) else body, 'body': value}
    with LOCK:
        SEQ += 1
        result['sequence'] = SEQ
        with gzip.open(OUT / 'http.jsonl.gz', 'at', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    assert result['status'] in accept, (path, result['status'], value)
    return result


def compose(*args, limited=False):
    command = ['docker', 'compose', '-f', str(ROOT / 'infra/f44/compose.yaml')]
    if limited:
        command += ['-f', str(ROOT / 'infra/f44/limited.yaml')]
    result = subprocess.run(command + list(args), capture_output=True, text=True)
    with (OUT / 'compose.log').open('a') as f:
        f.write(now() + ' ' + ' '.join(command + list(args)) + '\n' + result.stdout + result.stderr)
    result.check_returncode()
    return result.stdout


def ready():
    for _ in range(120):
        try:
            with urllib.request.urlopen(URL, timeout=1) as r:
                value = json.load(r)
            if value['cluster_name'] != 'travel-f44-lab':
                raise RuntimeError('Unexpected cluster at F44 endpoint')
            if value['cluster_uuid'] != '_na_':
                return value
            time.sleep(.5)  # HTTP can start before the persisted cluster state is loaded.
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(.5)
    raise TimeoutError('F44 ES startup did not complete')


def corpus():
    for i in range(1, 6001):
        yield {'attraction_id': f'p{i:06d}', 'name': ('西湖 游船' if i % 2 else '山水 公园') + f' 样本 {i:06d}',
               'summary': '西湖 游船 亲水 合成旅游资料 ' * 160, 'city_code': 'HZ' if i % 2 else 'SZ',
               'currency': 'CNY', 'status': 'open', 'tags': ['亲水', '合成'],
               'ticket_price_fen': 6000 + (i % 20)*100, 'location': {'lat': 30.25, 'lon': 120.15}}


def ids(reply):
    return [h['_id'] for h in reply['hits']['hits']]


def search(body, index=MAIN, opaque='f44-cost', accept=(200,)):
    return api('POST', f'/{index}/_search?request_cache=false&allow_partial_search_results=false', body, opaque, accept)


def stats():
    return api('GET', '/_nodes/stats/jvm,process,thread_pool,breaker,indices')['body']


def java(body, profile=False):
    path = OUT / ('java-input-' + str(SEQ) + '.json')
    path.write_text(json.dumps(body, ensure_ascii=False))
    command = ['bash', 'labs/f44/java.sh', str(path)] + (['profile'] if profile else [])
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    result.check_returncode()
    value = json.loads(result.stdout)
    save('java-' + str(SEQ) + '.json', value)
    return value


def seed():
    documents = list(corpus())
    source = ''.join(json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n' for d in documents).encode()
    save('corpus.json', {'generator': 'f44-v1', 'count': len(documents), 'bytes': len(source),
                         'sha256': hashlib.sha256(source).hexdigest(), 'first': documents[0]})
    for index, shards in [(MAIN, 1), (FAN, 2)]:
        mapping = load('create'); mapping['settings']['number_of_shards'] = shards
        api('PUT', '/' + index, mapping)
        for offset in range(0, len(documents), 250):
            lines = []
            for doc in documents[offset:offset+250]:
                lines += [json.dumps({'index': {'_index': index, '_id': doc['attraction_id']}}), json.dumps(doc, ensure_ascii=False)]
            reply = api('POST', '/_bulk', ('\n'.join(lines)+'\n').encode())['body']
            assert not reply['errors'] and all(item['index']['status'] == 201 for item in reply['items'])
        api('POST', '/' + index + '/_refresh')
        assert api('GET', '/' + index + '/_count')['body']['count'] == 6000
    api('GET', '/_cat/shards/tut-f44-attractions,tut-f44-fanout?format=json')
    # The hash proves equal input; this scan separately checks what was stored.
    for index in [MAIN, FAN]:
        reply = search({'size': 6000, 'query': {'match_all': {}}, 'sort': [{'attraction_id': 'asc'}]}, index)['body']
        assert [h['_source'] for h in reply['hits']['hits']] == documents
    base = search(load('base'))['body']
    assert base['hits']['total'] == {'value': 3000, 'relation': 'eq'}
    assert ids(base) == [f'p{i:06d}' for i in range(1, 20, 2)]


def costs():
    base = load('base')
    variants = {'docvalues': base, 'source-full': dict(base, _source=True),
                'source-filter': dict(base, _source=['attraction_id', 'ticket_price_fen', 'city_code']),
                'highlight': dict(base, highlight={'fields': {'summary': {'fragment_size': 50, 'number_of_fragments': 1}}, 'require_field_match': False}),
                'terms-2': dict(base, aggs={'tags': {'terms': {'field': 'tags', 'size': 2}}}),
                'terms-1000': dict(base, aggs=load('aggregate')['aggs']),
                'deep-2000': dict(base, **{'from': 2000})}
    result = {}
    for name, body in variants.items():
        samples = [search(body) for _ in range(3)]
        expected = [f'p{i:06d}' for i in range(4001, 4020, 2)] if name == 'deep-2000' else [f'p{i:06d}' for i in range(1, 20, 2)]
        for sample in samples:
            assert ids(sample['body']) == expected and sample['body']['hits']['total']['value'] == 3000
            assert all(h['fields']['ticket_price_fen'] == [6000 + int(h['_id'][1:]) % 20 * 100] for h in sample['body']['hits']['hits'])
        profiled = search(dict(body, profile=True), opaque='f44-profile')
        save(name + '-profile.json', profiled)
        assert profiled['body']['profile']['shards'][0]['searches'][0]['query']
        if name == 'highlight':
            assert all('<em>西湖</em>' in h['highlight']['summary'][0] for h in samples[0]['body']['hits']['hits'])
        if name == 'terms-1000':
            agg = samples[0]['body']['aggregations']['places']
            assert len(agg['buckets']) == 1000 and agg['sum_other_doc_count'] == 2000
        if name == 'terms-2':
            assert {b['key']: b['doc_count'] for b in samples[0]['body']['aggregations']['tags']['buckets']} == {'亲水': 3000, '合成': 3000}
        result[name] = {'normal': [{k: s[k] for k in ['client_ms', 'response_bytes']} | {'took': s['body']['took']} for s in samples],
                        'ids': expected, 'profile_shards': len(profiled['body']['profile']['shards'])}
    fan = search(dict(base, profile=True), FAN)['body']
    assert fan['_shards']['total'] == 2 and len(fan['profile']['shards']) == 2 and ids(fan) == result['docvalues']['ids']
    save('fanout-profile.json', fan)
    result['fanout'] = {'shards': fan['_shards'], 'ids': ids(fan)}
    bad = search(dict(base, **{'from': 10000}), accept=(400,))
    result['result-window-error'] = {'status': bad['status'], 'type': bad['body']['error']['type']}
    # Explicit deep anchor: this does NOT make random access free.
    before = stats()
    pit = api('POST', '/' + MAIN + '/_pit?keep_alive=1m')['body']['id']
    try:
        anchor_body = dict(base, size=1, **{'from': 1999}, pit={'id': pit, 'keep_alive': '1m'})
        anchor = api('POST', '/_search?request_cache=false', anchor_body)['body']
        pit = anchor.get('pit_id', pit)
        cursor = anchor['hits']['hits'][-1]['sort']
        page = api('POST', '/_search?request_cache=false', dict(base, search_after=cursor, pit={'id': pit, 'keep_alive': '1m'}))['body']
        pit = page.get('pit_id', pit)
        assert ids(page) == result['deep-2000']['ids']
        during = stats()
        result['pit'] = {'anchor_cursor': cursor, 'next_ids': ids(page), 'before': before, 'during': during}
    finally:
        api('DELETE', '/_pit', {'id': pit})
    result['pit']['after'] = stats()
    contexts = lambda s: sum(n['indices']['search']['open_contexts'] for n in s['nodes'].values())
    assert contexts(during) > contexts(before) and contexts(result['pit']['after']) == contexts(before)
    cache_before = api('GET', '/' + MAIN + '/_stats/request_cache')['body']['_all']['total']['request_cache']
    for _ in range(3):
        api('POST', '/' + MAIN + '/_search?request_cache=true', load('aggregate'))
    cache_after = api('GET', '/' + MAIN + '/_stats/request_cache')['body']['_all']['total']['request_cache']
    assert cache_after['hit_count'] - cache_before['hit_count'] == 2
    result['cache'] = {'before': cache_before, 'after': cache_after}
    jr = java(base, True)
    assert jr['status'] == 200 and ids(jr['reply']) == result['docvalues']['ids'] and jr['reply']['profile']['shards']
    save('c01.json', result)


def diagnose():
    identity = ready()['cluster_uuid']
    normal_before = api('GET', '/_nodes/thread_pool,settings')['body']
    compose('up', '-d', '--force-recreate', limited=True)
    assert ready()['cluster_uuid'] == identity
    api('GET', '/_cluster/health/' + MAIN + '?wait_for_status=green&timeout=30s')
    before_settings = api('GET', '/' + MAIN + '/_settings')['body']
    api('PUT', '/' + MAIN + '/_settings', {'index.search.slowlog.threshold.query.warn': '0ms', 'index.search.slowlog.threshold.fetch.warn': '0ms'})
    window = {'started_at': now(), 'before': stats(), 'before_settings': before_settings, 'normal_before': normal_before}
    slow = load('slow')
    warm = copy.deepcopy(slow); warm['query']['script_score']['script']['params']['loops'] = 1
    search(warm, opaque='f44-warm')
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(search, slow, MAIN, 'f44-diagnose', (200, 429)) for _ in range(4)]
            time.sleep(.15)
            window['tasks'] = api('GET', '/_tasks?detailed=true&actions=indices:data/read/search*')['body']
            window['active'] = stats()
            window['hot_threads'] = api('GET', '/_nodes/hot_threads?threads=3&interval=200ms&snapshots=3')['body']
            window['requests'] = [f.result() for f in futures]
        window['after'] = stats(); window['finished_at'] = now()
        assert window['before']['nodes'].keys() == window['after']['nodes'].keys()
        node = next(iter(window['before']['nodes']))
        assert window['after']['nodes'][node]['thread_pool']['search']['rejected'] > window['before']['nodes'][node]['thread_pool']['search']['rejected']
        statuses = [r['status'] for r in window['requests']]
        assert 200 in statuses and 429 in statuses, statuses
        assert any(t.get('headers', {}).get('X-Opaque-Id') == 'f44-diagnose' for n in window['tasks']['nodes'].values() for t in n.get('tasks', {}).values())
        container = compose('ps', '-q', 'es').strip()
        # This pinned Docker image sends its ECS slow log to Console.
        logs = subprocess.run(['docker', 'logs', container], capture_output=True, text=True, check=True)
        entries = [json.loads(line) for line in (logs.stdout + logs.stderr).splitlines() if line.startswith('{')]
        related = [e for e in entries if e.get('elasticsearch.slowlog.id') == 'f44-diagnose']
        assert any(e['log.logger'].endswith('query') for e in related) and any(e['log.logger'].endswith('fetch') for e in related)
        save('slowlog.json', related)
    finally:
        api('PUT', '/' + MAIN + '/_settings', {'index.search.slowlog.threshold.query.warn': None, 'index.search.slowlog.threshold.fetch.warn': None})
        compose('up', '-d', '--force-recreate')
        assert ready()['cluster_uuid'] == identity
        health = api('GET', '/_cluster/health/' + MAIN + '?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s')['body']
        assert not health['timed_out'], health
    window['recovered'] = search(load('base'))
    window['normal_settings'] = api('GET', '/_nodes/thread_pool,settings')['body']
    for node, value in normal_before['nodes'].items():
        assert window['normal_settings']['nodes'][node]['thread_pool']['search'] == value['thread_pool']['search']
    assert ids(window['recovered']['body'])[0] == 'p000001'
    save('c02.json', window)


def protect():
    result = {'before_settings': api('GET', '/_cluster/settings?include_defaults=true')['body'], 'before': stats()}
    try:
        api('PUT', '/_cluster/settings', {'transient': {'indices.breaker.request.limit': '1kb'}})
        reply = search(load('aggregate'), accept=(429,))
        assert 'circuit_breaking_exception' in json.dumps(reply['body'])
        result['error'] = reply
        result['tripped'] = stats()
        node = next(iter(result['before']['nodes']))
        assert result['tripped']['nodes'][node]['breakers']['request']['tripped'] > result['before']['nodes'][node]['breakers']['request']['tripped']
        jr = java(load('aggregate'))
        assert jr['status'] == 429 and jr['type'] in ['search_phase_execution_exception', 'circuit_breaking_exception']
        result['java'] = jr
    finally:
        api('PUT', '/_cluster/settings', {'transient': {'indices.breaker.request.limit': None}})
    result['recovered'] = search(load('aggregate'))
    assert len(result['recovered']['body']['aggregations']['places']['buckets']) == 1000
    # A configuration prohibition is a 400, not evidence of exhausted memory.
    try:
        api('PUT', '/_cluster/settings', {'transient': {'search.allow_expensive_queries': False}})
        result['prohibited'] = search(load('slow'), accept=(400,))
        assert 'search.allow_expensive_queries' in json.dumps(result['prohibited']['body'])
        result['cheap_still_works'] = search(load('base'))
    finally:
        api('PUT', '/_cluster/settings', {'transient': {'search.allow_expensive_queries': None}})
    result['after_settings'] = api('GET', '/_cluster/settings?include_defaults=true')['body']
    assert result['before_settings']['transient'] == result['after_settings']['transient']
    result['after'] = stats()
    save('c03.json', result)


def cleanup():
    ready()
    api('PUT', '/_cluster/settings', {'transient': {'indices.breaker.request.limit': None, 'search.allow_expensive_queries': None}})
    for index in [MAIN, FAN]:
        api('DELETE', '/' + index, accept=(200, 404))
        api('GET', '/' + index, accept=(404,))
    compose('up', '-d')
    ready()
    save('cleanup.json', {'deleted': [MAIN, FAN], 'settings': api('GET', '/_cluster/settings')['body'], 'volumes_retained': True})


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['start', 'run', 'cleanup', 'down'])
    parser.add_argument('--out', type=pathlib.Path, required=True)
    args = parser.parse_args()
    OUT = args.out.resolve(); OUT.mkdir(parents=True, exist_ok=False)
    if args.command == 'start':
        compose('up', '-d'); save('identity.json', ready())
    elif args.command == 'cleanup':
        cleanup()
    elif args.command == 'down':
        compose('down')
    else:
        save('identity.json', ready())
        save('nodes.json', api('GET', '/_nodes/jvm,settings,os')['body'])
        seed(); costs(); diagnose(); protect()
        save('summary.json', {'passed': True, 'finished_at': now(), 'http_calls': SEQ, 'cases': ['c01', 'c02', 'c03']})
    print(args.command + ' complete: ' + str(OUT))


if __name__ == '__main__':
    main()
