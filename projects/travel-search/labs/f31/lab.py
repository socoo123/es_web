#!/usr/bin/env python3
"""F31 allocation, data-node expansion/drain and fixed-snapshot resize lab."""
import argparse
import collections
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
INFRA = P / 'infra/f31'
INDEX = 'tut-f31-attractions'
SPLIT, SHRINK, REINDEX = 'tut-f31-split4', 'tut-f31-shrink2', 'tut-f31-reindex3'
BAD = ['tut-f31-bad-open', 'tut-f31-bad3', 'tut-f31-bad6', 'tut-f31-bad-shrink']
INDICES = [INDEX, SPLIT, SHRINK, REINDEX] + BAD
BASE = 'http://127.0.0.1:19531'
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18081').rstrip('/')
DISK = ['cluster.routing.allocation.disk.watermark.' + s for s in ['low', 'high', 'flood_stage']]
EXCLUDE = 'cluster.routing.allocation.exclude._name'
OUT = None
EVENTS = []
CASE = 'setup'
OBSERVER = None


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
    event({'kind': 'command', 'command': args, 'exit_code': p.returncode,
           'stdout': p.stdout, 'stderr': p.stderr})
    if expected is not None:
        check(p.returncode == expected, {'command': args, 'stderr': p.stderr})
    return p


def compose(*args, bootstrap=False):
    prefix = ['docker', 'compose', '-f', str(INFRA / 'compose.yaml')]
    if bootstrap:
        prefix += ['-f', str(INFRA / 'bootstrap.yaml')]
    return command(prefix + list(args))


def owned():
    p = command(['docker', 'ps', '-aq', '--filter', 'label=com.docker.compose.project=es-framework-f31'])
    if not p.stdout.strip():
        return []
    items = json.loads(command(['docker', 'inspect'] + p.stdout.split()).stdout)
    for c in items:
        labels = c['Config']['Labels']
        check(labels.get('esweb.lesson') == 'f31' and labels.get('com.docker.compose.service') in ['n1', 'n2', 'n3'], c['Name'])
    return items


def req(path='', method='GET', body=None, expected=200, kind='teaching', base=BASE):
    payload = body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    headers = {'Content-Type': 'application/x-ndjson' if '/_bulk' in path else 'application/json'}
    r = urllib.request.Request(base + path, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=40) as response:
            code, raw = response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        code, raw = error.code, error.read().decode()
    value = json.loads(raw)
    event({'kind': kind, 'method': method, 'url': base + path, 'body': body, 'status': code, 'response': value})
    if expected is not None:
        check(code == expected, {'path': path, 'expected': expected, 'actual': code, 'response': value})
    return value


def wait(nodes=2, color='green', index=None):
    deadline = time.monotonic() + 150
    last = None
    while time.monotonic() < deadline:
        try:
            last = req('/_cluster/health' + ('/' + index if index else '') +
                       '?wait_for_status=' + color + '&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=2s', kind='wait')
            if last.get('number_of_nodes') == nodes and last.get('status') == color and not last.get('timed_out'):
                return last
        except (OSError, ValueError):
            pass
        time.sleep(2)
    raise AssertionError(last)


def guard():
    owned()
    root = req(kind='guard')
    check(root['cluster_name'] == 'travel-f31-lab' and root['version']['number'] == '9.4.0'
          and root['version']['lucene_version'] == '10.4.0', root)
    names = req('/_cat/indices?format=json&expand_wildcards=all&h=index', kind='guard')
    check(all(x['index'] in INDICES for x in names), 'F31 requires its own cluster without foreign indices')


def identity(nodes=2, bootstrap=False):
    root = req(kind='identity')
    data = req('/_nodes/settings,jvm?flat_settings=true', kind='identity')['nodes']
    check(len(data) == nodes and root['cluster_uuid'] != '_na_', data)
    for n in data.values():
        service = n['name'].removeprefix('travel-f31-')
        check(set(n['roles']) == ({'master', 'data', 'ingest'} if service == 'n1' else {'data'}), n)
        check(('cluster.initial_master_nodes' in n['settings']) == (bootstrap and service == 'n1'), n)
    return {'root': root, 'nodes': data}


def start():
    owned()
    exists = []
    for n in ['n1', 'n2', 'n3']:
        p = command(['docker', 'volume', 'inspect', 'es-framework-f31-' + n + '-data'], expected=None)
        if n != 'n3':
            exists.append(p.returncode == 0)
        if p.returncode == 0:
            check(json.loads(p.stdout)[0]['Labels'].get('esweb.lesson') == 'f31', 'foreign volume')
    check(all(exists) or not any(exists), 'Partial base volumes: do not bootstrap, recover the original volumes')
    compose('up', '-d', 'n1', 'n2', bootstrap=not any(exists))
    wait()
    before = identity(bootstrap=not any(exists))
    if not any(exists):
        compose('up', '-d', '--force-recreate', 'n1')
        wait()
    after = identity()
    check(before['root']['cluster_uuid'] == after['root']['cluster_uuid'] and set(before['nodes']) == set(after['nodes']), 'identity changed')
    save('identity.json', after)


def settings(index, body, kind='teaching'):
    return req('/' + index + '/_settings', 'PUT', body, kind=kind)


def cluster(body, kind='teaching'):
    return req('/_cluster/settings', 'PUT', {'persistent': body}, kind=kind)


def rows(index=INDEX, kind='teaching'):
    return req('/_cat/shards/' + index + '?format=json&h=index,shard,prirep,state,docs,node', kind=kind)


def search(index=INDEX, body=None, suffix=''):
    r = req('/' + index + '/_search?allow_partial_search_results=false' + suffix,
            'POST', body or load('search/f31/search.json'))
    check(not r['timed_out'] and r['_shards']['failed'] == 0 and r['hits']['total']['relation'] == 'eq', r)
    return r


def fields(index=INDEX, price=6000, suffix=''):
    expected = load('data/f31/attractions.json')
    expected[0]['ticket_price_fen'] = price
    r = search(index, {'size': 20, 'track_total_hits': True, 'query': {'match_all': {}}, 'sort': [{'attraction_id': 'asc'}]}, suffix)
    check(r['hits']['total']['value'] == 6 and [h['_id'] for h in r['hits']['hits']] == [x['attraction_id'] for x in expected]
          and [h['_source'] for h in r['hits']['hits']] == expected, r)
    return r


def observe(stage, price=6000):
    r = req('/api/attractions/search', 'POST', load('search/f31/input.json'), kind='java', base=APP)
    check(r['total'] == 2 and [x['id'] for x in r['items']] == ['p01', 'p02']
          and [x['ticketPriceFen'] for x in r['items']] == [price, 0] and r['esRequest'] == load('search/f31/search.json'), r)
    replay = search(body=r['esRequest'])
    check([h['_id'] for h in replay['hits']['hits']] == ['p01', 'p02']
          and [h['_source']['ticket_price_fen'] for h in replay['hits']['hits']] == [price, 0], replay)
    save(stage + '-java.json', r)
    if OBSERVER:
        OBSERVER.capture(stage, price, 200, APP, OUT)


def cleanup():
    guard()
    for index in INDICES:
        r = req('/' + index, 'DELETE', expected=None, kind='cleanup')
        check(r.get('acknowledged') or r.get('error', {}).get('type') == 'index_not_found_exception', r)


def explain():
    return req('/_cluster/allocation/explain?include_yes_decisions=true&include_disk_info=true', 'POST',
               {'index': INDEX, 'shard': 0, 'primary': False})


def decisions(r):
    return {n['node_name']: [(d['decider'], d['decision']) for d in n['deciders']] for n in r['node_allocation_decisions']}


def drain(service, nodes):
    before = rows()
    check(any(r['node'] == 'travel-f31-' + service for r in before), before)
    cluster({EXCLUDE: 'travel-f31-' + service})
    layout = wait_drained(service, nodes)
    recovery = req('/' + INDEX + '/_recovery?active_only=false&detailed=true')
    check(all(s['stage'] == 'DONE' for s in recovery[INDEX]['shards']), recovery)
    # A moving replica may recover from its primary on ANOTHER node. The recovery
    # source is not necessarily the node being drained; prove evacuation by routing.
    check(any(s['type'] == 'PEER' for s in recovery[INDEX]['shards']), recovery)
    fields()
    owned()
    compose('stop', service)
    wait(nodes=nodes - 1)
    cluster({EXCLUDE: None})
    fields()
    return {'layout_before_exclusion': before, 'layout_before_stop': layout, 'recovery': recovery}


def wait_drained(service, nodes):
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        wait(nodes=nodes)
        layout = req('/_cat/shards?format=json&h=index,shard,prirep,state,docs,node', kind='wait')
        if all(r['node'] != 'travel-f31-' + service and r['state'] == 'STARTED' for r in layout):
            return layout
        time.sleep(2)
    raise AssertionError({'not_drained': service, 'layout': layout})


def recover():
    guard()
    compose('up', '-d', 'n2')
    cluster({key: None for key in DISK + [EXCLUDE]}, kind='recovery')
    for index in [INDEX, SPLIT]:
        r = req('/' + index + '/_settings', expected=None, kind='recovery')
        if index in r:
            settings(index, {'index.blocks.write': None, 'index.routing.allocation.require._name': None,
                             'index.number_of_replicas': 1 if index == INDEX else 0}, kind='recovery')
    data = req('/_nodes', kind='recovery')['nodes']
    if any(n['name'] == 'travel-f31-n3' for n in data.values()):
        cluster({EXCLUDE: 'travel-f31-n3'}, kind='recovery')
        wait_drained('n3', 3)
        owned()
        compose('stop', 'n3')
    wait()
    cluster({EXCLUDE: None}, kind='recovery')


def run():
    global CASE
    guard()
    recover()
    cleanup()
    baseline = req('/_cluster/settings?flat_settings=true', kind='identity')
    check(not any(key in baseline.get(level, {}) for key in DISK + [EXCLUDE] for level in ['persistent', 'transient']), baseline)
    save('settings-before.json', baseline)
    initial = identity()
    CASE = 'f31-c01-filter-and-expansion'
    try:
        req('/' + INDEX, 'PUT', load('search/f31/create.json'))
        bulk = req('/' + INDEX + '/_bulk?wait_for_active_shards=1', 'POST', (P / 'data/f31/attractions.ndjson').read_text())
        check(not bulk['errors'] and all(x['create']['status'] == 201 for x in bulk['items']), bulk)
        req('/' + INDEX + '/_refresh', 'POST')
        wait(color='yellow')
        fields()
        first = explain()
        d = decisions(first)
        check(('same_shard', 'NO') in d['travel-f31-n1'] and ('filter', 'NO') in d['travel-f31-n2'], d)
        save('filter-two-nodes.json', first)
        observe('01-yellow-filter')
        compose('up', '-d', 'n3')
        wait(nodes=3, color='yellow')
        expanded = identity(nodes=3)
        check(initial['root']['cluster_uuid'] == expanded['root']['cluster_uuid'] and set(initial['nodes']) < set(expanded['nodes']), expanded)
        still = explain()
        check(('filter', 'NO') in decisions(still)['travel-f31-n3'], decisions(still))
        save('filter-three-nodes.json', still)
        observe('02-added-still-yellow')
        settings(INDEX, {'index.routing.allocation.require._name': None})
        wait(nodes=3)
        layout = rows()
        check(len(layout) == 4 and all(r['state'] == 'STARTED' for r in layout)
              and {r['node'] for r in layout} == {'travel-f31-n1', 'travel-f31-n2', 'travel-f31-n3'}, layout)
        save('expanded-layout.json', layout)
        fields()
        observe('03-filter-repaired')

        CASE = 'f31-c02-disk-and-drain'
        fs = req('/_nodes/stats/fs')['nodes']
        check(all(2 * 1024**3 < n['fs']['total']['available_in_bytes'] < 10 * 1024**4 for n in fs.values()), fs)
        save('actual-disk.json', fs)
        cluster({DISK[0]: '10tb', DISK[1]: '1gb', DISK[2]: '512mb'})
        settings(INDEX, {'index.number_of_replicas': 2})
        wait(nodes=3, color='yellow')
        disk = explain()
        check(any(('disk_threshold', 'NO') in ds for ds in decisions(disk).values()), decisions(disk))
        save('disk-low-rejection.json', disk)
        fields()
        observe('04-disk-yellow')
        cluster({key: None for key in DISK})
        wait(nodes=3)
        restored = rows()
        check(len(restored) == 6 and all(r['state'] == 'STARTED' for r in restored), restored)
        settings(INDEX, {'index.number_of_replicas': 1})
        wait(nodes=3)
        save('drain-n2.json', drain('n2', 3))
        observe('05-drained-n2')
        compose('up', '-d', 'n2')
        wait(nodes=3)
        save('drain-n3.json', drain('n3', 3))
        observe('06-baseline-topology')

        CASE = 'f31-c03-resize-conditions'
        error = req('/' + INDEX + '/_settings', 'PUT', {'index.number_of_shards': 4}, expected=400)
        save('error-static-shards.json', error)
        error = req('/' + INDEX + '/_split/' + BAD[0], 'POST', {'settings': {'index.number_of_shards': 4}}, expected=500)
        check('read-only' in json.dumps(error), error)
        save('error-open-source.json', error)
        req('/' + INDEX + '/_block/write', 'PUT')
        denied = req('/' + INDEX + '/_doc/p01', 'PUT', load('data/f31/attractions.json')[0], expected=403)
        check(denied['error']['type'] == 'cluster_block_exception', denied)
        for count, target in [(3, BAD[1]), (6, BAD[2])]:
            error = req('/' + INDEX + '/_split/' + target, 'POST', {'settings': {'index.number_of_shards': count}}, expected=400 if count == 3 else 500)
            check('error' in error and ('factor' in json.dumps(error) or 'multiple' in json.dumps(error)), error)
            save('error-split-' + str(count) + '.json', error)
        r = req('/' + INDEX + '/_split/' + SPLIT + '?wait_for_active_shards=all', 'POST', load('search/f31/split.json'))
        check(r['acknowledged'] and r['shards_acknowledged'], r)
        wait()
        req('/' + SPLIT + '/_refresh', 'POST')
        fields(SPLIT)
        settings(SPLIT, {'index.routing.allocation.total_shards_per_node': 2})
        wait()
        spread = rows(SPLIT)
        check(collections.Counter(r['node'] for r in spread) == {'travel-f31-n1': 2, 'travel-f31-n2': 2}, spread)
        req('/' + SPLIT + '/_block/write', 'PUT')
        error = req('/' + SPLIT + '/_shrink/' + BAD[3], 'POST', {'settings': {'index.number_of_shards': 2}}, expected=500)
        check('same node' in json.dumps(error), error)
        save('error-shrink-spread.json', error)
        settings(SPLIT, {'index.routing.allocation.total_shards_per_node': None,
                         'index.routing.allocation.require._name': 'travel-f31-n1'})
        wait()
        colocated = rows(SPLIT)
        check(len(colocated) == 4 and all(r['node'] == 'travel-f31-n1' and r['state'] == 'STARTED' for r in colocated), colocated)
        save('shrink-colocated.json', colocated)
        r = req('/' + SPLIT + '/_shrink/' + SHRINK + '?wait_for_active_shards=all', 'POST', load('search/f31/shrink.json'))
        check(r['acknowledged'] and r['shards_acknowledged'], r)
        wait()
        req('/' + SHRINK + '/_refresh', 'POST')
        fields(SHRINK)
        create3 = load('search/f31/create-reindex.json')
        req('/' + REINDEX, 'PUT', create3)
        wait()
        r = req('/_reindex?refresh=true', 'POST', load('search/f31/reindex.json'))
        check(r['created'] == 6 and r['total'] == 6 and r['version_conflicts'] == 0 and not r['failures'], r)
        fields(REINDEX)
        for index, count in [(INDEX, 2), (SPLIT, 4), (SHRINK, 2), (REINDEX, 3)]:
            meta = req('/' + index + '/_settings?flat_settings=true')[index]['settings']
            check(meta['index.number_of_shards'] == str(count), meta)
            mapping = req('/' + index + '/_mapping')[index]['mappings']
            check(mapping == load('search/f31/create.json')['mappings'], mapping)
            r = search(index)
            check([h['_id'] for h in r['hits']['hits']] == ['p01', 'p02'], r)
        settings(INDEX, {'index.blocks.write': None})
        r = req('/' + INDEX + '/_update/p01?wait_for_active_shards=all', 'POST', {'doc': {'ticket_price_fen': 6500}})
        check(r['_shards']['successful'] == 2, r)
        req('/' + INDEX + '/_refresh', 'POST')
        fields(price=6500)
        for index in [SPLIT, SHRINK, REINDEX]:
            fields(index)
        observe('07-source-only-update', 6500)
        settings(SPLIT, {'index.blocks.write': None, 'index.routing.allocation.require._name': None})
        wait()
        final = identity()
        check(initial['root']['cluster_uuid'] == final['root']['cluster_uuid'] and set(initial['nodes']) == set(final['nodes']), final)
        for node_id in final['nodes']:
            fields(price=6500, suffix='&preference=_only_nodes:' + node_id)
        save('identity-final.json', final)
        after = req('/_cluster/settings?flat_settings=true')
        check(after == baseline, after)
        save('settings-after.json', after)
        save('final-layout.json', req('/_cat/shards?format=json&h=index,shard,prirep,state,docs,node'))
    except BaseException as error:
        save('primary-failure.json', {'case': CASE, 'error': repr(error)})
        CASE = 'failure-recovery'
        try:
            recover()
        except BaseException as recovery_error:
            save('recovery-failure.json', {'error': repr(recovery_error)})
        raise


def main():
    global OUT, OBSERVER
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'run', 'cleanup', 'recover', 'down'])
    parser.add_argument('--out', type=pathlib.Path, required=True)
    parser.add_argument('--observer', type=pathlib.Path)
    args = parser.parse_args()
    OUT = args.out.resolve()
    OUT.mkdir(parents=True, exist_ok=False)
    if args.observer:
        spec = importlib.util.spec_from_file_location('f31_observer', args.observer.resolve())
        OBSERVER = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(OBSERVER)
    try:
        if args.action == 'down':
            owned()
            compose('--profile', 'extra', 'down')
        else:
            globals()[args.action]()
        counts = collections.Counter(e['case'] for e in EVENTS if e['kind'] == 'teaching')
        save('summary.json', {'action': args.action, 'passed': True, 'teaching_http_by_case': dict(counts),
                              'teaching_http_total': sum(counts.values()),
                              'http_by_kind': dict(collections.Counter(e['kind'] for e in EVENTS if 'url' in e)),
                              'commands': sum(e['kind'] == 'command' for e in EVENTS),
                              'observer': str(args.observer) if args.observer else None})
        print(json.dumps({'action': args.action, 'passed': True, 'teaching_http': sum(counts.values())}))
    except BaseException as error:
        save('failure.json', {'error': repr(error)})
        raise


if __name__ == '__main__':
    main()
