#!/usr/bin/env python3
"""F30: separate election availability from shard availability, on owned resources."""
import argparse
import datetime
import importlib.util
import json
import os
import pathlib
import subprocess
import time
import urllib.error
import urllib.request

P = pathlib.Path(__file__).resolve().parents[2]
INFRA = P / 'infra/f30'
NAMES = ['m1', 'm2', 'm3', 'd1']
URLS = {name: 'http://127.0.0.1:' + str(19430 + n) for n, name in enumerate(NAMES)}
INDEX, META = 'tut-f30-attractions', 'tut-f30-metadata'
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18081').rstrip('/')
OUT = None
EVENTS = []
OBSERVER = None
CASE = 'setup'


def check(ok, detail):
    if not ok:
        raise AssertionError(detail)


def load(path):
    return json.loads((P / path).read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def event(value):
    value = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'case': CASE, **value}
    EVENTS.append(value)
    with (OUT / 'events.jsonl').open('a') as f:
        f.write(json.dumps(value, ensure_ascii=False) + '\n')


def command(args, expected=0):
    p = subprocess.run(args, cwd=P, text=True, capture_output=True)
    event({'kind': 'command', 'args': args, 'exit_code': p.returncode,
           'stdout': p.stdout, 'stderr': p.stderr})
    if expected is not None:
        check(p.returncode == expected, {'command': args, 'stderr': p.stderr})
    return p


def compose(*args, bootstrap=False):
    prefix = ['docker', 'compose', '-f', str(INFRA / 'compose.yaml')]
    if bootstrap:
        prefix += ['-f', str(INFRA / 'bootstrap.yaml')]
    return command(prefix + list(args))


def owned_containers():
    # Check labels on every named container BEFORE any stop/kill/start/down.
    result = command(['docker', 'inspect'] + ['es-framework-f30-' + n + '-1' for n in NAMES])
    containers = json.loads(result.stdout)
    for name, c in zip(NAMES, containers):
        labels = c['Config']['Labels']
        check(labels.get('esweb.lesson') == 'f30' and
              labels.get('com.docker.compose.project') == 'es-framework-f30' and
              labels.get('com.docker.compose.service') == name, 'Foreign container: ' + name)
    return containers


def req(path='', method='GET', body=None, expected=200, node='m1', kind='teaching'):
    base = APP if node == 'java' else URLS[node]
    payload = body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    r = urllib.request.Request(base + path, data=payload, method=method,
        headers={'Content-Type': 'application/x-ndjson' if isinstance(body, str) else 'application/json'})
    try:
        with urllib.request.urlopen(r, timeout=15) as response:
            status, value = response.status, json.loads(response.read())
    except urllib.error.HTTPError as e:
        status, value = e.code, json.loads(e.read())
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        status, value = 0, {'connection_error': str(e)}
    event({'kind': kind, 'method': method, 'url': base + path, 'request': body,
           'status': status, 'response': value})
    if expected is not None:
        check(status == expected, {'path': path, 'expected': expected, 'status': status, 'response': value})
    return value


def wait(nodes=4, color='green', node='m1', index=INDEX):
    deadline = time.monotonic() + 240
    while time.monotonic() < deadline:
        r = req('/_cluster/health' + ('/' + index if index else '') +
                '?wait_for_nodes=' + str(nodes) + '&wait_for_status=' + color +
                '&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=1s',
                expected=None, node=node, kind='wait')
        if r.get('number_of_nodes') == nodes and r.get('status') == color and not r.get('timed_out'):
            return r
        time.sleep(2)
    raise AssertionError('Cluster did not reach the required state: ' + str((nodes, color, node)))


def state(node='m1', kind='teaching'):
    return req('/_cluster/state/master_node,nodes,metadata,routing_table,blocks' +
               '?local=true&filter_path=cluster_name,cluster_uuid,version,master_node,nodes,metadata.cluster_coordination,metadata.indices.*.primary_terms,metadata.indices.*.in_sync_allocations,routing_table,blocks', node=node, kind=kind)


def identity(bootstrap=False):
    roots = [req(node=n, kind='identity') for n in NAMES]
    check(len({r['cluster_uuid'] for r in roots}) == 1 and roots[0]['cluster_uuid'] != '_na_', roots)
    check(all(r['cluster_name'] == 'travel-f30-lab' and r['version']['number'] == '9.4.0'
              and r['version']['lucene_version'] == '10.4.0' for r in roots), roots)
    nodes = req('/_nodes/settings,jvm?flat_settings=true', kind='identity')['nodes']
    check(len(nodes) == 4, nodes)
    for name in NAMES:
        n = next(v for v in nodes.values() if v['name'] == 'travel-f30-' + name)
        roles = {'master', 'data', 'ingest'} if name == 'm3' else {'master'} if name.startswith('m') else {'data'}
        check(set(n['roles']) == roles and
              ('cluster.initial_master_nodes' in n['settings']) == (bootstrap and name.startswith('m')), n)
    return {'uuid': roots[0]['cluster_uuid'], 'nodes': nodes, 'version': roots[0]['version']}


def start():
    volumes = ['es-framework-f30-' + n + '-data' for n in NAMES]
    exists = []
    for v in volumes:
        r = command(['docker', 'volume', 'inspect', v], expected=None)
        exists.append(r.returncode == 0)
        if r.returncode == 0:
            check(json.loads(r.stdout)[0]['Labels'].get('esweb.lesson') == 'f30', 'Foreign volume ' + v)
    check(all(exists) or not any(exists), 'Partial F30 volumes: do not bootstrap; inspect and recover original volumes')
    compose('up', '-d', bootstrap=not any(exists))
    wait(index=None)
    first = identity(bootstrap=not any(exists))
    if not any(exists):
        compose('up', '-d', '--force-recreate')
        wait(index=None)
        steady = identity()
        check(first['uuid'] == steady['uuid'] and set(first['nodes']) == set(steady['nodes']), 'Identity changed')
    else:
        steady = first
    save('identity.json', steady)


def guard():
    owned_containers()
    r = req(node='d1', kind='guard')
    check(r['cluster_name'] == 'travel-f30-lab' and r['version']['number'] == '9.4.0', r)


def cleanup():
    guard()
    wait(index=None)
    for index in [INDEX, META]:
        r = req('/' + index, 'DELETE', expected=None, kind='cleanup')
        check(r.get('acknowledged') is True or r.get('error', {}).get('type') == 'index_not_found_exception', r)


def search(body=None, node='m1', suffix=''):
    r = req('/' + INDEX + '/_search?allow_partial_search_results=false' + suffix, 'POST',
            body or load('search/f30/search.json'), node=node)
    check(not r['timed_out'] and r['_shards']['total'] == 1 and r['_shards']['failed'] == 0
          and r['hits']['total']['relation'] == 'eq', r)
    return r


def fields(price, node='m1', suffix=''):
    expected = load('data/f30/attractions.json')
    expected[0]['ticket_price_fen'] = price
    r = search({'size': 20, 'track_total_hits': True, 'query': {'match_all': {}},
                'sort': [{'attraction_id': 'asc'}]}, node=node, suffix=suffix)
    check(r['hits']['total']['value'] == 6 and
          [h['_id'] for h in r['hits']['hits']] == [d['attraction_id'] for d in expected] and
          [h['_source'] for h in r['hits']['hits']] == expected, r)
    return r


def put(price, node='m1', copies='1', expected=200):
    doc = load('data/f30/attractions.json')[0]
    doc['ticket_price_fen'] = price
    return req('/' + INDEX + '/_doc/p01?wait_for_active_shards=' + copies + '&timeout=2s',
               'PUT', doc, expected=expected, node=node)


def observe(stage, price, expected=200):
    # Same F07 contract: a single m1 endpoint. Case 2 stops this entry; case 3 keeps it alive.
    r = req('/api/attractions/search', 'POST', load('search/f30/input.json'), expected=expected, node='java', kind='java')
    if expected == 200:
        check(r['total'] == 2 and [x['id'] for x in r['items']] == ['p01', 'p02'] and
              [x['ticketPriceFen'] for x in r['items']] == [price, 0] and
              r['esRequest'] == load('search/f30/search.json'), r)
        replay = search(r['esRequest'])
        check([h['_id'] for h in replay['hits']['hits']] == ['p01', 'p02'] and
              [h['_source']['ticket_price_fen'] for h in replay['hits']['hits']] == [price, 0], replay)
    else:
        check(r['code'] == ('SEARCH_BACKEND_REJECTED' if expected == 502 else 'SEARCH_UNAVAILABLE'), r)
    save(stage + '-java.json', r)
    if OBSERVER:
        OBSERVER.capture(stage, price, expected, APP, OUT)


def master_service(s):
    return s['nodes'][s['master_node']]['name'].removeprefix('travel-f30-')


def votes(s):
    c = s['metadata']['cluster_coordination']
    check(set(c['last_committed_config']) == set(c['last_accepted_config']) and len(c['last_committed_config']) == 3, c)
    return c


def shard(s):
    return s['routing_table']['indices'][INDEX]['shards']['0']


def term(s):
    return s['metadata']['indices'][INDEX]['primary_terms']['0']


def layout():
    return req('/_cat/shards/' + INDEX + '?format=json&h=index,shard,prirep,state,docs,node')


def healthy(price):
    wait()
    fields(price)
    rows = layout()
    check(len(rows) == 2 and {r['prirep'] for r in rows} == {'p', 'r'} and
          {r['node'] for r in rows} == {'travel-f30-m3', 'travel-f30-d1'} and
          all(r['state'] == 'STARTED' and r['docs'] == '6' for r in rows), rows)
    for name in ['m3', 'd1']:
        node_id = next(k for k, n in state()['nodes'].items() if n['name'] == 'travel-f30-' + name)
        fields(price, suffix='&preference=_only_nodes:' + node_id)
    check(req('/' + INDEX + '/_mapping')[INDEX]['mappings'] == load('search/f30/create.json')['mappings'], 'mapping changed')


def dedicated_master(index=None):
    # Only for isolating the experiment: avoid stopping a mixed-role master
    # while trying to observe JUST a shard failure. Record this preparation.
    global CASE
    previous = CASE; CASE = 'preparation'
    s = state()
    if master_service(s) == 'm3':
        owned_containers(); compose('kill', '-s', 'SIGKILL', 'm3')
        wait(nodes=3, color='yellow' if index else 'green', index=index)
        check(master_service(state()) in ['m1', 'm2'], 'Dedicated master not elected')
        compose('start', 'm3'); wait(index=index)
    check(master_service(state()) in ['m1', 'm2'], 'Unexpected mixed-role master')
    CASE = previous


def election():
    global CASE
    CASE = 'f30-c01'
    before = state(); votes(before)
    elected = master_service(before)
    owned_containers(); compose('kill', '-s', 'SIGKILL', elected)
    entry = next(n for n in ['m1', 'm2', 'm3'] if n != elected)
    wait(nodes=3, node=entry)
    after = state(node=entry); votes(after)
    check(after['master_node'] != before['master_node'] and
          votes(after)['term'] > votes(before)['term'], after)
    check({(s['node'], s['primary']) for s in shard(before)} ==
          {(s['node'], s['primary']) for s in shard(after)} and term(before) == term(after), 'Data primary changed')
    fields(6000, node=entry)
    r = put(6500, node=entry, copies='all'); check(r['_shards']['successful'] == 2, r)
    req('/' + INDEX + '/_refresh', 'POST', node=entry)
    fields(6500, node=entry)
    req('/' + META + '?master_timeout=2s', 'PUT', {'settings': {'number_of_shards': 1, 'number_of_replicas': 0}}, node=entry)
    req('/' + META, 'DELETE', node=entry)
    compose('start', elected); healthy(6500)
    observe('elected-recovered', 6500)
    save('election.json', {'stopped_service': elected, 'live_entry': entry, 'before': before, 'after': after})


def minority():
    global CASE
    CASE = 'f30-c02'
    before = state(); votes(before)
    defaults = req('/_cluster/settings?include_defaults=true&flat_settings=true')
    check(defaults['defaults']['cluster.no_master_block'] == 'write' and
          all('cluster.no_master_block' not in defaults[k] for k in ['persistent', 'transient']), defaults)
    owned_containers(); compose('kill', '-s', 'SIGKILL', 'm1', 'm2')
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        s = state(node='d1', kind='wait')
        if not s.get('master_node') and '2' in s.get('blocks', {}).get('global', {}):
            break
        time.sleep(1)
    else:
        raise AssertionError('No-master block was not observed')
    # Wait on the remaining voter too, not only the data node's view.
    while time.monotonic() < deadline:
        local = state(node='m3', kind='wait')
        if not local.get('master_node') and '2' in local.get('blocks', {}).get('global', {}):
            break
        time.sleep(1)
    else:
        raise AssertionError('m3 did not observe no master')
    votes(s)
    check(set(s['metadata']['cluster_coordination']['last_committed_config']) ==
          set(before['metadata']['cluster_coordination']['last_committed_config']), 'Voting configuration changed')
    fields(6500, node='d1'); observe('minority-entry-down', 6500, expected=503)
    rejected = put(9900, node='d1', expected=503)
    check(rejected['error']['type'] in ['cluster_block_exception', 'master_not_discovered_exception'], rejected)
    metadata = req('/' + META + '?master_timeout=2s&timeout=2s', 'PUT',
                   {'settings': {'number_of_shards': 1, 'number_of_replicas': 0}}, expected=503, node='d1')
    check(metadata['error']['type'] == 'master_not_discovered_exception', metadata)
    fields(6500, node='d1')
    command(['docker', 'logs', '--tail', '160', 'es-framework-f30-m3-1'])
    compose('start', 'm1', 'm2'); healthy(6500)
    missing = req('/' + META, expected=404)
    check(missing['error']['type'] == 'index_not_found_exception', missing)
    observe('majority-restored', 6500)
    save('minority.json', {'before': before, 'no_master_data_view': s, 'no_master_entry_view': local,
                          'write_error': rejected, 'metadata_error': metadata})


def data_failure():
    global CASE
    CASE = 'f30-c03'
    dedicated_master(index=INDEX)
    before = state(); votes(before)
    primary = next(s for s in shard(before) if s['primary'])
    replica = next(s for s in shard(before) if not s['primary'])
    stopped = before['nodes'][primary['node']]['name'].removeprefix('travel-f30-')
    owned_containers(); compose('kill', '-s', 'SIGKILL', stopped)
    wait(nodes=3, color='yellow')
    promoted = state()
    check(promoted['master_node'] == before['master_node'] and
          next(s for s in shard(promoted) if s['primary'])['node'] == replica['node'] and
          term(promoted) > term(before), promoted)
    fields(6500)
    r = put(7000); check(r['_shards']['successful'] == 1, r)
    rejected = put(9900, copies='all', expected=503)
    check(rejected['error']['type'] == 'unavailable_shards_exception', rejected)
    req('/' + INDEX + '/_refresh', 'POST'); fields(7000)
    observe('promoted-yellow', 7000)
    layout()
    compose('start', stopped); healthy(7000)
    recovery = req('/' + INDEX + '/_recovery?detailed=true')
    peers = recovery[INDEX]['shards']
    check(any(s['type'] == 'PEER' and s['stage'] == 'DONE' and
              s['target']['name'] == 'travel-f30-' + stopped for s in peers), recovery)
    # Both copies are now current. Take both data processes away, keep m1/m2, a majority of the three voters.
    pre_all = state(); owned_containers(); compose('kill', '-s', 'SIGKILL', 'm3', 'd1')
    wait(nodes=2, color='red')
    all_down = state(); votes(all_down)
    check(all_down['master_node'] == pre_all['master_node'] and
          all(s['state'] == 'UNASSIGNED' for s in shard(all_down)), all_down)
    failed_search = req('/' + INDEX + '/_search?allow_partial_search_results=false',
                        'POST', load('search/f30/search.json'), expected=503)
    check(failed_search['error']['type'] == 'search_phase_execution_exception', failed_search)
    failed_write = put(9900, expected=503)
    check(failed_write['error']['type'] == 'unavailable_shards_exception', failed_write)
    # Explicitly skip waiting for shard starts: this tests metadata, not data readiness.
    meta = req('/' + META + '?wait_for_active_shards=0&master_timeout=2s&timeout=2s', 'PUT',
               {'settings': {'number_of_shards': 1, 'number_of_replicas': 0}})
    check(meta['acknowledged'], meta)
    meta_rows = req('/_cat/shards/' + META + '?format=json&h=index,shard,prirep,state,node')
    check(len(meta_rows) == 1 and meta_rows[0]['state'] == 'UNASSIGNED', meta_rows)
    req('/' + META, 'DELETE')
    observe('data-unavailable', 7000, expected=503)
    compose('start', 'm3', 'd1'); healthy(7000)
    observe('data-restored', 7000)
    save('data-failure.json', {'stopped_primary_service': stopped, 'before': before, 'promoted': promoted,
         'recovery_after_one_node_returns': recovery, 'all_data_down': all_down,
         'metadata_creation_without_data': meta, 'metadata_shards': meta_rows,
         'search_error': failed_search, 'write_error': failed_write})


def run():
    global CASE
    guard(); cleanup()
    dedicated_master()
    initial = identity()
    req('/' + INDEX, 'PUT', load('search/f30/create.json'))
    wait()
    bulk = req('/' + INDEX + '/_bulk?wait_for_active_shards=all', 'POST', (P / 'data/f30/attractions.ndjson').read_text())
    check(not bulk['errors'] and len(bulk['items']) == 6 and
          all(i['create']['status'] == 201 and i['create']['_shards']['successful'] == 2 for i in bulk['items']), bulk)
    req('/' + INDEX + '/_refresh', 'POST'); healthy(6000)
    settings = req('/' + INDEX + '/_settings?flat_settings=true')[INDEX]['settings']
    for k, v in load('search/f30/create.json')['settings'].items():
        check(settings['index.' + k] == str(v), settings)
    observe('baseline', 6000)
    election(); minority(); data_failure()
    CASE = 'final'
    final = identity()
    check(initial['uuid'] == final['uuid'] and set(initial['nodes']) == set(final['nodes']), 'Identity changed')
    save('identity.json', {'initial': initial, 'final': final, 'settings': settings})
    save('summary.json', {'passed': True, 'cases': ['f30-c01', 'f30-c02', 'f30-c03'],
         'uuid': final['uuid'], 'final_price_fen': 7000, 'final_count': 6,
         'teaching_http_by_case': {c: sum(e['kind'] == 'teaching' and e['case'] == c for e in EVENTS)
                                 for c in ['setup', 'f30-c01', 'f30-c02', 'f30-c03']},
         'java_requests': sum(e['kind'] == 'java' for e in EVENTS),
         'wait_http': sum(e['kind'] == 'wait' for e in EVENTS),
         'scope': 'SIGKILL of named Docker processes on one VM; original volumes; no network partition or disk loss; no timing SLO',
         'all_requests': 'events.jsonl; setup/wait/identity/cleanup/Java and commands are tagged separately'})


def main():
    global OUT, OBSERVER
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['start', 'run', 'recover', 'cleanup', 'down'])
    p.add_argument('--out', required=True, type=pathlib.Path)
    p.add_argument('--observer', type=pathlib.Path, help='Optional author browser-review module, no reader dependency')
    a = p.parse_args(); OUT = a.out.resolve(); OUT.mkdir(parents=True, exist_ok=False)
    if a.observer:
        spec = importlib.util.spec_from_file_location('f30_observer', a.observer.resolve())
        OBSERVER = importlib.util.module_from_spec(spec); spec.loader.exec_module(OBSERVER)
    try:
        if a.action == 'start':
            start()
        elif a.action == 'run':
            run()
        elif a.action == 'recover':
            owned_containers(); compose('start', *NAMES); wait(index=None); save('identity.json', identity())
        elif a.action == 'cleanup':
            cleanup()
        else:
            owned_containers(); compose('down')  # No -v: keep the original four data volumes.
        print('F30 ' + a.action + ' passed: ' + str(OUT), flush=True)
    except Exception as e:
        save('failure.json', {'error': str(e), 'recovery': 'python3 labs/f30/lab.py recover --out NEW_DIRECTORY'})
        raise


if __name__ == '__main__':
    main()
