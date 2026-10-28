#!/usr/bin/env python3
"""F29 isolated two-primary routing lab. Every actual request has a receipt."""
import argparse
import datetime
import json
import os
import pathlib
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

P = pathlib.Path(__file__).resolve().parents[2]
I = P / 'infra/f29'
URLS = ['http://127.0.0.1:' + str(p) for p in [19329, 19330, 19331]]
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18081').rstrip('/')
D, C = 'tut-f29-default', 'tut-f29-routed'
VOLUMES = ['es-framework-f29-n' + str(n) + '-data' for n in [1, 2, 3]]
OUT = None
EVENTS = []

def check(ok, detail):
    if not ok:
        raise AssertionError(detail)

def load(path):
    return json.loads((P / path).read_text())

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def event(value):
    value = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), **value}
    EVENTS.append(value)
    with (OUT / 'events.jsonl').open('a') as f:
        f.write(json.dumps(value, ensure_ascii=False) + '\n')

def command(args, expected=0):
    p = subprocess.run(args, cwd=P, text=True, capture_output=True)
    event({'kind': 'command', 'args': args, 'exit_code': p.returncode,
           'stdout': p.stdout, 'stderr': p.stderr})
    if expected is not None:
        check(p.returncode == expected, {'command': args, 'exit': p.returncode, 'stderr': p.stderr})
    return p

def compose(*args, bootstrap=False):
    c = ['docker', 'compose', '-f', str(I / 'compose.yaml')]
    if bootstrap:
        c += ['-f', str(I / 'bootstrap.yaml')]
    return command(c + list(args))

def req(path='', method='GET', body=None, expected=200, node=1, kind='teaching'):
    base = APP if node == 'java' else URLS[node]
    payload = body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    request = urllib.request.Request(base + path, data=payload, method=method,
        headers={'Content-Type': 'application/x-ndjson' if isinstance(body, str) else 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=40) as r:
            status, value = r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        status, value = e.code, json.loads(e.read())
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        status, value = 0, {'connection_error': str(e)}
    event({'kind': kind, 'method': method, 'url': base + path,
           'request': body, 'status': status, 'response': value})
    if expected is not None:
        check(status == expected, {'path': path, 'expected': expected, 'actual': status, 'body': value})
    return value

def wait(index=None):
    path = '/_cluster/health' + ('/' + index if index else '')
    path += '?wait_for_nodes=3&wait_for_status=green&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=2s'
    deadline = time.monotonic() + 210
    while time.monotonic() < deadline:
        r = req(path, expected=None, kind='wait')
        if r.get('number_of_nodes') == 3 and r.get('status') == 'green' and not r.get('timed_out'):
            return r
        time.sleep(2)
    raise AssertionError('F29 did not reach the required three-node green state')

def identity(bootstrap=False):
    roots = [req(node=n, kind='setup') for n in range(3)]
    check(len({r['cluster_uuid'] for r in roots}) == 1 and roots[0]['cluster_uuid'] != '_na_', roots)
    check(all(r['cluster_name'] == 'travel-f29-lab' and r['version']['number'] == '9.4.0'
              and r['version']['lucene_version'] == '10.4.0' for r in roots), roots)
    nodes = req('/_nodes/settings,jvm?flat_settings=true', kind='setup')['nodes']
    check(len(nodes) == 3, nodes)
    roles = [{'master'}, {'master', 'data', 'ingest'}, {'master', 'data'}]
    for n, role in enumerate(roles, 1):
        node = next(v for v in nodes.values() if v['name'] == f'travel-f29-0{n}')
        check(set(node['roles']) == role and ('cluster.initial_master_nodes' in node['settings']) == bootstrap, node)
    return {'uuid': roots[0]['cluster_uuid'], 'nodes': nodes, 'version': roots[0]['version']}

def start():
    exists = [command(['docker', 'volume', 'inspect', v], expected=None).returncode == 0 for v in VOLUMES]
    check(all(exists) or not any(exists), 'Partial F29 volumes: inspect instead of automatically bootstrapping')
    compose('up', '-d', bootstrap=not any(exists))
    wait()
    first = identity(bootstrap=not any(exists))
    if not any(exists):
        compose('up', '-d', '--force-recreate')
        wait()
        steady = identity()
        check(first['uuid'] == steady['uuid'] and set(first['nodes']) == set(steady['nodes']), 'identity changed')
    else:
        steady = first
    save('identity.json', steady)

def search(index, body, suffix='', node=1):
    r = req('/' + index + '/_search?allow_partial_search_results=false' + suffix,
            'POST', body, node=node)
    check(not r['timed_out'] and r['_shards']['failed'] == 0 and r['hits']['total']['relation'] == 'eq', r)
    return r

def ids(r):
    return [h['_id'] for h in r['hits']['hits']]

def route(index, value):
    r = req('/' + index + '/_search_shards?routing=' + urllib.parse.quote(value))
    check(len(r['shards']) == 1 and len(r['shards'][0]) == 2, r)
    return r['shards'][0][0]['shard']

def layout(index, expected_count):
    config = load('search/f29/create-' + ('default' if index == D else 'routed') + '.json')
    mapping = req('/' + index + '/_mapping')[index]['mappings']
    check(mapping == config['mappings'], mapping)
    settings = req('/' + index + '/_settings?flat_settings=true')[index]['settings']
    for key, val in config['settings'].items():
        check(settings['index.' + key] == str(val), settings)
    check('index.routing_partition_size' not in settings or settings['index.routing_partition_size'] == '1', settings)
    shards = req('/_cat/shards/' + index + '?format=json&h=index,shard,prirep,state,docs,node')
    check(len(shards) == 4 and all(s['state'] == 'STARTED' for s in shards), shards)
    for n in ['0', '1']:
        pair = [s for s in shards if s['shard'] == n]
        check(len(pair) == 2 and {s['prirep'] for s in pair} == {'p', 'r'}
              and {s['node'] for s in pair} == {'travel-f29-02', 'travel-f29-03'}
              and len({s['docs'] for s in pair}) == 1, pair)
    check(sum(int(s['docs']) for s in shards if s['prirep'] == 'p') == expected_count, shards)
    return {'settings': settings, 'mapping': mapping, 'shards': shards}

def default():
    req('/' + D, 'PUT', load('search/f29/create-default.json'))
    bulk = req('/' + D + '/_bulk?wait_for_active_shards=all', 'POST', (P / 'data/f29/attractions.ndjson').read_text())
    check(not bulk['errors'] and len(bulk['items']) == 6 and all(x['create']['status'] == 201
          and x['create']['_shards']['successful'] == 2 for x in bulk['items']), bulk)
    req('/' + D + '/_refresh', 'POST'); wait(D)
    proof = layout(D, 6)
    groups = req('/' + D + '/_search_shards')['shards']
    check(len(groups) == 2 and all(len(g) == 2 for g in groups), groups)
    docs = load('data/f29/attractions.json')
    actual = {}
    for shard in [0, 1]:
        r = search(D, {'size': 20, 'track_total_hits': True, 'query': {'match_all': {}},
                       'sort': [{'attraction_id': 'asc'}]}, '&preference=_shards:' + str(shard))
        check(r['_shards']['total'] == 1, r)
        for h in r['hits']['hits']:
            check(h['_source'] == next(d for d in docs if d['attraction_id'] == h['_id']), h)
            actual[h['_id']] = shard
    check(set(actual) == {d['attraction_id'] for d in docs}, actual)
    for id, shard in actual.items():
        check(route(D, id) == shard, {'id': id, 'shard': shard})
    get = req('/' + D + '/_doc/p01', node=2)
    check(get['found'] and get['_source'] == docs[0], get)
    body = load('search/f29/search.json')
    for n in range(3):
        r = search(D, body, node=n)
        check(ids(r) == ['p01', 'p02'] and r['_shards']['total'] == 2, r)
    java = req('/api/attractions/search', 'POST', load('search/f29/input.json'), node='java')
    check(java['total'] == 2 and [x['id'] for x in java['items']] == ['p01', 'p02'] and java['esRequest'] == body, java)
    replay = search(D, java['esRequest'])
    for hit, card in zip(replay['hits']['hits'], java['items']):
        source = hit['_source']
        check(card['name'] == source['name'] and card['ticketPriceFen'] == source['ticket_price_fen']
              and card['currency'] == source['currency'] and abs(card['score'] - hit['_score']) < 1e-6, [hit, card])
    save('default-proof.json', {**proof, 'actual_document_shards': actual, 'search_ids': ids(replay), 'java': java})

def routing():
    req('/' + C, 'PUT', load('search/f29/create-routed.json')); wait(C)
    routes = {value: route(C, value) for value in ['HZ', 'FZ', 'SZ', 'NJ', 'SH', 'BJ']}
    # Fixed values were selected using actual _search_shards; fail if the premise changes.
    fixture = load('data/f29/routes.json')
    right, wrong, collision = fixture['right'], fixture['wrong'], fixture['collision']
    check(routes[right] != routes[wrong] and routes[right] == routes[collision], routes)
    missing = req('/' + C + '/_doc/missing', 'PUT', load('data/f29/routed.json')[0]['source'], expected=400)
    check(missing['error']['type'] == 'routing_missing_exception', missing)
    bulk = req('/' + C + '/_bulk?wait_for_active_shards=all', 'POST', (P / 'data/f29/routed.ndjson').read_text())
    check(not bulk['errors'] and len(bulk['items']) == 6 and all(x['create']['status'] == 201
          and x['create']['_shards']['successful'] == 2 for x in bulk['items']), bulk)
    req('/' + C + '/_refresh', 'POST'); wait(C)
    proof = layout(C, 6)
    original = load('data/f29/routed.json')[0]['source']
    getpath = '/' + C + '/_doc/r01'
    good = req(getpath + '?routing=' + right)
    check(good['found'] and good['_routing'] == right and good['_source'] == original, good)
    bad = req(getpath + '?routing=' + wrong, expected=404); check(not bad['found'], bad)
    missing = req(getpath, expected=400); check(missing['error']['type'] == 'routing_missing_exception', missing)
    collided = req(getpath + '?routing=' + collision)
    check(collided['found'] and collided['_routing'] == right and collided['_source'] == original, collided)
    bad = req('/' + C + '/_update/r01?routing=' + wrong, 'POST', {'doc': {'ticket_price_fen': 7000}}, expected=404)
    check(bad['error']['type'] == 'document_missing_exception', bad)
    req('/' + C + '/_update/r01?routing=' + right, 'POST', {'doc': {'ticket_price_fen': 7000}})
    check(req(getpath + '?routing=' + right)['_source']['ticket_price_fen'] == 7000, 'update did not apply')
    deleted = req(getpath + '?routing=' + wrong, 'DELETE', expected=404)
    check(deleted['result'] == 'not_found', deleted)
    check(req(getpath + '?routing=' + right)['_source']['ticket_price_fen'] == 7000, 'wrong delete removed original')
    duplicate = {**original, 'city_code': wrong, 'ticket_price_fen': 9900}
    created = req(getpath + '?routing=' + wrong + '&wait_for_active_shards=all', 'PUT', duplicate, expected=201)
    check(created['result'] == 'created' and created['_shards']['successful'] == 2, created)
    req('/' + C + '/_refresh', 'POST')
    dup = search(C, {'size': 20, 'track_total_hits': True, 'query': {'ids': {'values': ['r01']}}})
    check(ids(dup) == ['r01', 'r01'] and {h['_routing'] for h in dup['hits']['hits']} == {right, wrong}, dup)
    for h in dup['hits']['hits']:
        check(h['_source'] == (duplicate if h['_routing'] == wrong else {**original, 'ticket_price_fen': 7000}), h)
    req(getpath + '?routing=' + wrong, 'DELETE')
    req('/' + C + '/_update/r01?routing=' + right, 'POST', {'doc': {'ticket_price_fen': 6000}})
    req('/' + C + '/_refresh', 'POST')
    save('routing-proof.json', {**proof, 'routes': routes, 'right': right, 'wrong': wrong,
         'collision': collision, 'same_shard_wrong_get_found': collided['found'], 'duplicate_hits': dup['hits']})

def reads():
    fixture = load('data/f29/routes.json'); right, wrong = fixture['right'], fixture['wrong']
    allbody = {'size': 20, 'track_total_hits': True, 'query': {'match_all': {}}, 'sort': [{'attraction_id': 'asc'}]}
    full = search(C, allbody)
    expected = load('data/f29/routed.json')
    check(ids(full) == [d['source']['attraction_id'] for d in expected] and full['_shards']['total'] == 2, full)
    for h, d in zip(full['hits']['hits'], expected):
        check(h['_source'] == d['source'] and h['_routing'] == d['routing'], h)
    limited = search(C, allbody, '&routing=' + right)
    check(ids(limited) == ['r01', 'r02', 'r04', 'r05'] and limited['_shards']['total'] == 1, limited)
    filtered_body = load('search/f29/search.json')
    filtered = search(C, filtered_body, '&routing=' + right)
    global_filtered = search(C, filtered_body)
    check(ids(filtered) == ids(global_filtered) == ['r01', 'r02']
          and filtered['_shards']['total'] == 1 and global_filtered['_shards']['total'] == 2, [filtered, global_filtered])
    empty = search(C, filtered_body, '&routing=' + wrong)
    check(ids(empty) == [] and empty['hits']['total']['value'] == 0 and empty['_shards']['total'] == 1, empty)
    multi = search(C, allbody, '&routing=' + right + ',' + wrong)
    check(ids(multi) == ids(full) and multi['_shards']['total'] == 2, multi)
    state = req('/_nodes')['nodes']
    shards = req('/' + C + '/_search_shards?routing=' + right)['shards'][0]
    copies = []
    for copy in shards:
        node = copy['node']
        r = search(C, {**filtered_body, 'profile': True}, '&routing=' + right + '&preference=_only_nodes:' + node)
        check(ids(r) == ['r01', 'r02'] and r['_shards']['total'] == 1 and len(r['profile']['shards']) == 1, r)
        profile = r['profile']['shards'][0]
        check(profile['id'].startswith('[' + node + ']'), profile)
        copies.append({'node_id': node, 'node': state[node]['name'], 'primary': copy['primary'],
                       'profile_id': profile['id'], 'ids': ids(r), 'shards': r['_shards']})
    check({c['primary'] for c in copies} == {True, False}, copies)
    save('reads-proof.json', {'all_ids': ids(full), 'routed_without_filter': ids(limited),
         'filtered_ids': ids(filtered), 'wrong_routing_ids': ids(empty), 'copies': copies,
         'final_layout': layout(C, 6)})

def cleanup():
    for index in [D, C]:
        r = req('/' + index, 'DELETE', expected=None, kind='cleanup')
        check(r.get('acknowledged') is True or r.get('status') == 404, r)
        r = req('/' + index, expected=404, kind='cleanup')
        check(r['error']['type'] == 'index_not_found_exception', r)

def reset(confirm):
    check(confirm, 'reset requires --delete-f29-data; deletes only three named disposable F29 volumes')
    compose('down')
    for v in VOLUMES:
        command(['docker', 'volume', 'rm', v])

def main():
    global OUT
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['start', 'default', 'routing', 'reads', 'cleanup', 'reset'])
    p.add_argument('--out', required=True)
    p.add_argument('--delete-f29-data', action='store_true')
    args = p.parse_args()
    OUT = pathlib.Path(args.out).resolve(); OUT.mkdir(parents=True, exist_ok=False)
    passed = False
    try:
        if args.action == 'reset': reset(args.delete_f29_data)
        else: globals()[args.action]()
        passed = True
    finally:
        counts = {kind: sum(e['kind'] == kind for e in EVENTS) for kind in ['teaching', 'setup', 'wait', 'cleanup', 'command']}
        save('summary.json', {'action': args.action, 'passed': passed, 'counts': counts})
    print(json.dumps({'action': args.action, 'passed': passed, 'counts': counts}))

if __name__ == '__main__':
    main()
