#!/usr/bin/env python3
"""F32: composable templates and independent read/write aliases, ES 9.4.0."""
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
INFRA = P / 'infra/f32'
BASE = 'http://127.0.0.1:19632'
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18082').rstrip('/')
V1, V2, V3, V4 = ['tut-f32-attractions-v00' + str(i) for i in range(1, 5)]
READ, WRITE = 'tut-f32-attractions-read', 'tut-f32-attractions-write'
MISSING = 'tut-f32-missing-write'
INDICES = [V1, V2, V3, V4, MISSING]
TEMPLATES = ['tut-f32-attractions', 'tut-f32-shadow', 'tut-f32-equal']
COMPONENTS = ['tut-f32-settings', 'tut-f32-fields']
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
    p = command(['docker', 'ps', '-aq', '--filter', 'label=com.docker.compose.project=es-framework-f32'])
    if p.stdout.strip():
        for c in json.loads(command(['docker', 'inspect'] + p.stdout.split()).stdout):
            labels = c['Config']['Labels']
            check(labels.get('esweb.lesson') == 'f32'
                  and labels.get('com.docker.compose.service') in ['n1', 'n2'], c['Name'])


def req(path='', method='GET', body=None, expected=200, kind='teaching', base=BASE):
    payload = body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    request = urllib.request.Request(base + path, data=payload, method=method,
                                    headers={'Content-Type': 'application/x-ndjson' if '/_bulk' in path else 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            code, raw = response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        code, raw = error.code, error.read().decode()
    value = json.loads(raw) if raw else {'http_status': code}
    event({'kind': kind, 'method': method, 'url': base + path, 'body': body, 'status': code, 'response': value})
    if expected is not None:
        check(code == expected, {'path': path, 'expected': expected, 'actual': code, 'response': value})
    return value


def wait(index=None):
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        try:
            r = req('/_cluster/health' + ('/' + index if index else '')
                    + '?wait_for_status=green&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=2s', kind='wait')
            if r.get('number_of_nodes') == 2 and r['status'] == 'green' and not r.get('timed_out'):
                return r
        except (OSError, ValueError):
            pass
        time.sleep(2)
    raise AssertionError('Two-node green wait timed out')


def identity(bootstrap=False):
    root = req(kind='identity')
    nodes = req('/_nodes/settings,jvm?flat_settings=true', kind='identity')['nodes']
    check(len(nodes) == 2 and root['cluster_uuid'] != '_na_', root)
    for node in nodes.values():
        n1 = node['name'] == 'travel-f32-n1'
        check(node['name'] in ['travel-f32-n1', 'travel-f32-n2'], node)
        check(set(node['roles']) == ({'master', 'data', 'ingest'} if n1 else {'data'}), node)
        check(('cluster.initial_master_nodes' in node['settings']) == (bootstrap and n1), node)
    return {'root': root, 'nodes': nodes}


def guard():
    owned()
    r = req(kind='guard')
    check(r['cluster_name'] == 'travel-f32-lab' and r['version']['number'] == '9.4.0'
          and r['version']['lucene_version'] == '10.4.0', r)
    names = req('/_cat/indices?format=json&expand_wildcards=all&h=index', kind='guard')
    system_prefixes = ('.ds-.logs-elasticsearch.deprecation-default-', '.ds-ilm-history-7-')
    check(all(x['index'] in INDICES or x['index'].startswith(system_prefixes) for x in names),
          'F32 needs a dedicated cluster without foreign business indices')
    for api, key, allowed in [('_index_template', 'index_templates', TEMPLATES),
                              ('_component_template', 'component_templates', COMPONENTS)]:
        templates = req('/' + api, kind='guard')[key]
        check(all(not x['name'].startswith('tut-') or x['name'] in allowed for x in templates), templates)


def start():
    owned()
    exists = []
    for n in ['n1', 'n2']:
        p = command(['docker', 'volume', 'inspect', 'es-framework-f32-' + n + '-data'], expected=None)
        exists.append(p.returncode == 0)
        if p.returncode == 0:
            check(json.loads(p.stdout)[0]['Labels'].get('esweb.lesson') == 'f32', 'foreign volume')
    check(all(exists) or not any(exists), 'Partial base volumes: recover original volumes; do not bootstrap')
    compose('up', '-d', 'n1', 'n2', bootstrap=not any(exists))
    wait()
    before = identity(bootstrap=not any(exists))
    if not any(exists):
        compose('up', '-d', '--force-recreate', 'n1')
        wait()
    after = identity()
    check(before['root']['cluster_uuid'] == after['root']['cluster_uuid'] and set(before['nodes']) == set(after['nodes']), 'identity changed')
    save('identity.json', after)


def cleanup():
    guard()
    # Exact resources only. Indices first, index templates before referenced components.
    for path in ['/' + i for i in INDICES] + ['/_index_template/' + i for i in TEMPLATES] + ['/_component_template/' + i for i in COMPONENTS]:
        r = req(path, 'DELETE', expected=None, kind='cleanup')
        check(r.get('acknowledged') or r.get('status') == 404, r)


def create(index, body):
    r = req('/' + index, 'PUT', body)
    check(r['acknowledged'] and r['shards_acknowledged'], r)
    wait(index)


def actual(index, shards, replicas, refresh, extra):
    settings = req('/' + index + '/_settings?flat_settings=true')[index]['settings']
    mapping = req('/' + index + '/_mapping')[index]['mappings']
    check([settings['index.number_of_shards'], settings['index.number_of_replicas'], settings['index.refresh_interval']]
          == [str(shards), str(replicas), refresh], settings)
    expected = load('search/f32/create-old.json')['mappings'] if extra == 0 else load('search/f32/component-fields-v' + str(extra) + '.json')['template']['mappings']
    check(mapping == expected, mapping)
    return {'settings': settings, 'mappings': mapping}


def aliases(body):
    r = req('/_aliases', 'POST', body)
    check(r.get('acknowledged') and not r.get('errors'), r)
    return r


def alias_state():
    return req('/_alias/' + READ + ',' + WRITE)


def search(index, body=None, expected=200):
    r = req('/' + index + '/_search?allow_partial_search_results=false', 'POST', body or load('search/f32/search.json'), expected=expected)
    if expected == 200:
        check(not r['timed_out'] and r['_shards']['failed'] == 0 and r['hits']['total']['relation'] == 'eq', r)
    return r


def fields(index, version, added=(), suffix=''):
    expected = load('data/f32/' + version + '.json') + [load('data/f32/' + i + '.json') for i in added]
    r = req('/' + index + '/_search?allow_partial_search_results=false' + suffix, 'POST',
            {'size': 20, 'track_total_hits': True, 'query': {'match_all': {}}, 'sort': [{'attraction_id': 'asc'}]})
    check(not r['timed_out'] and r['_shards']['failed'] == 0 and r['hits']['total'] == {'value': len(expected), 'relation': 'eq'}, r)
    check([h['_id'] for h in r['hits']['hits']] == [d['attraction_id'] for d in expected]
          and [h['_source'] for h in r['hits']['hits']] == expected, r)


def java_write(target, ident, ok, status=None):
    p = command(['bash', 'labs/f32/java.sh', target, ident, 'data/f32/' + ident + '.json'])
    r = json.loads(p.stdout)
    event({'kind': 'java-client', 'method': 'PUT', 'target': target, 'id': ident, 'require_alias': True, 'response': r})
    check(r['ok'] == ok and (ok or r['status'] == status), r)
    return r


def observe(stage, rows, status=200):
    r = req('/api/attractions/search', 'POST', load('search/f32/input.json'), expected=status, kind='java-api', base=APP)
    if status == 200:
        check(r['total'] == len(rows) and r['esRequest'] == load('search/f32/search.json'), r)
        check(collections.Counter((x['id'], x['ticketPriceFen']) for x in r['items']) == collections.Counter(rows), r)
        replay = search(READ, r['esRequest'])
        check(collections.Counter((x['_id'], x['_source']['ticket_price_fen']) for x in replay['hits']['hits']) == collections.Counter(rows), replay)
        for card in r['items']:
            matches = [h['_source'] for h in replay['hits']['hits'] if (h['_id'], h['_source']['ticket_price_fen']) == (card['id'], card['ticketPriceFen'])]
            check(any((card['name'], card['cityCode'], card['currency'], card['status']) == (s['name'], s['city_code'], s['currency'], s['status']) for s in matches), card)
    else:
        check(r['code'] == 'SEARCH_BACKEND_REJECTED', r)
        search(READ, expected=404)
    save(stage + '-java.json', r)
    if OBSERVER:
        OBSERVER.capture(stage, rows, status, APP, BASE, READ, OUT)


def run():
    global CASE
    guard()
    before = identity()
    baseline = req('/_cluster/settings?flat_settings=true', kind='guard')
    check(baseline == {'persistent': {}, 'transient': {}}, baseline)
    cleanup()
    CASE = 'f32-c01-template-inheritance'
    create(V1, load('search/f32/create-old.json'))
    for name, fixture in [('settings', 'component-settings'), ('fields', 'component-fields-v1')]:
        req('/_component_template/tut-f32-' + name, 'PUT', load('search/f32/' + fixture + '.json'))
    req('/_index_template/tut-f32-attractions', 'PUT', load('search/f32/template.json'))
    req('/_index_template/tut-f32-shadow', 'PUT', load('search/f32/template-shadow.json'))
    shadow = req('/_index_template/_simulate_index/' + V2, 'POST')
    check(shadow['template']['settings']['index']['number_of_shards'] == '3'
          and shadow['template']['mappings']['properties'] == {'name': {'type': 'keyword'}}
          and any(x['name'] == 'tut-f32-attractions' for x in shadow['overlapping']), shadow)
    save('shadow-simulation.json', shadow)
    error = req('/_index_template/tut-f32-equal', 'PUT', load('search/f32/template-shadow.json'), expected=400)
    check('same priority' in error['error']['reason'], error)
    save('error-equal-priority.json', error)
    req('/_index_template/tut-f32-shadow', 'DELETE')
    good = req('/_index_template/_simulate_index/' + V2, 'POST')
    named = req('/_index_template/_simulate/tut-f32-attractions', 'POST')
    check(good['template'] == named['template'] and good['template']['settings']['index']['number_of_shards'] == '2'
          and good['template']['mappings']['dynamic'] == 'strict', good)
    req('/' + V2, 'HEAD', expected=404)
    save('repaired-simulation.json', good)
    create(V2, {})
    state = {V1: actual(V1, 1, 1, '-1', 0), V2: actual(V2, 2, 1, '-1', 1)}
    for name in ['settings', 'fields']:
        fixture = 'component-settings-v2' if name == 'settings' else 'component-fields-v2'
        req('/_component_template/tut-f32-' + name, 'PUT', load('search/f32/' + fixture + '.json'))
    newer = req('/_index_template/_simulate_index/' + V3, 'POST')
    check(newer['template']['settings']['index']['refresh_interval'] == '1s'
          and newer['template']['mappings']['properties']['source_note']['type'] == 'keyword', newer)
    create(V3, {})
    create(V4, load('search/f32/create-override.json'))
    state.update({V1: actual(V1, 1, 1, '-1', 0), V2: actual(V2, 2, 1, '-1', 1),
                  V3: actual(V3, 2, 1, '1s', 2), V4: actual(V4, 3, 0, '-1', 2)})
    for index in [V1, V2, V3, V4]:
        check(req('/' + index + '/_count')['count'] == 0, index)
    save('actual-inheritance.json', state)
    CASE = 'f32-c02-read-write-targets'
    for index, version in [(V1, 'v001'), (V2, 'v002')]:
        bulk = req('/' + index + '/_bulk?wait_for_active_shards=all', 'POST', (P / ('data/f32/' + version + '.ndjson')).read_text())
        check(not bulk['errors'] and len(bulk['items']) == 6 and all(x['create']['status'] == 201 and x['create']['_shards']['successful'] == 2 for x in bulk['items']), bulk)
        req('/' + index + '/_refresh', 'POST')
        fields(index, version)
    aliases(load('search/f32/aliases-initial.json'))
    save('aliases-initial.json', alias_state())
    observe('01-initial-alias', [('p01', 6000), ('p02', 0)])
    r = req('/' + WRITE + '/_doc/p07?require_alias=true&wait_for_active_shards=all', 'PUT', load('data/f32/p07.json'), expected=201)
    check(r['_index'] == V1 and r['_shards']['successful'] == 2, r)
    sdk = java_write(WRITE, 'p07', True)
    check(sdk['response']['_index'] == V1 and sdk['response']['result'] == 'updated', sdk)
    req('/' + WRITE + '/_refresh', 'POST')
    check(req('/' + V1 + '/_doc/p07')['_source'] == load('data/f32/p07.json'), 'wrong p07')
    check(not req('/' + V2 + '/_doc/p07', expected=404)['found'], 'p07 leaked')
    # A single-target alias without an explicit flag is implicitly writable.
    aliases({'actions': [{'add': {'index': V1, 'alias': 'tut-f32-implicit'}}]})
    implicit = req('/tut-f32-implicit/_doc/p07?require_alias=true&wait_for_active_shards=all', 'PUT', load('data/f32/p07.json'))
    check(implicit['_index'] == V1 and implicit['result'] == 'updated', implicit)
    aliases({'actions': [{'remove': {'index': V1, 'alias': 'tut-f32-implicit', 'must_exist': True}}]})
    aliases({'actions': [{'add': {'index': V2, 'alias': READ, 'is_write_index': False}},
                         {'add': {'index': V2, 'alias': WRITE, 'is_write_index': False}}]})
    combined = search(WRITE)
    check(combined['hits']['total']['value'] == 4 and {h['_index'] for h in combined['hits']['hits']} == {V1, V2}, combined)
    save('write-alias-searches-both.json', combined)
    observe('02-read-both-versions', [('p01', 6000), ('p01', 6500), ('p02', 0), ('p02', 0)])
    aliases({'actions': [{'remove': {'index': V2, 'alias': READ, 'must_exist': True}}]})
    observe('03-read-scope-repaired', [('p01', 6000), ('p02', 0)])
    fields(V1, 'v001', ['p07']); fields(V2, 'v002')
    CASE = 'f32-c03-errors-and-repair'
    for label, target, expected in [('missing', MISSING, 404), ('physical', V2, 404), ('read-disabled', READ, 400)]:
        r = req('/' + target + '/_doc/p09?require_alias=true&wait_for_active_shards=all', 'PUT', load('data/f32/p09.json'), expected=expected)
        save('error-' + label + '.json', r)
        java_write(target, 'p09', False, expected)
    req('/' + MISSING, 'HEAD', expected=404)
    aliases(load('search/f32/aliases-no-writer.json'))
    r = req('/' + WRITE + '/_doc/p09?require_alias=true', 'PUT', load('data/f32/p09.json'), expected=400)
    check('no write index' in r['error']['reason'], r)
    save('error-no-writer.json', r)
    java_write(WRITE, 'p09', False, 400)
    r = req('/_aliases', 'POST', load('search/f32/aliases-two-writers.json'), expected=500)
    check('more than one write index' in r['error']['reason'], r)
    save('error-two-writers.json', r)
    unchanged = alias_state()
    check(all(not unchanged[i]['aliases'][WRITE]['is_write_index'] for i in [V1, V2]), unchanged)
    aliases(load('search/f32/aliases-writer-v002.json'))
    r = req('/' + WRITE + '/_doc/p08?require_alias=true&wait_for_active_shards=all', 'PUT', load('data/f32/p08.json'), expected=201)
    check(r['_index'] == V2 and r['_shards']['successful'] == 2, r)
    sdk = java_write(WRITE, 'p08', True)
    check(sdk['response']['_index'] == V2 and sdk['response']['result'] == 'updated', sdk)
    req('/' + WRITE + '/_refresh', 'POST')
    check(not req('/' + V1 + '/_doc/p08', expected=404)['found'], 'p08 leaked')
    check(req('/' + V2 + '/_doc/p08')['_source'] == load('data/f32/p08.json'), 'wrong p08')
    # Removing the read alias is a deliberate fault, not a migration recipe.
    aliases({'actions': [{'remove': {'index': V1, 'alias': READ, 'must_exist': True}}]})
    observe('04-missing-read-alias', [], 502)
    aliases({'actions': [{'add': {'index': V3, 'alias': READ, 'is_write_index': False}}]})
    observe('05-wrong-empty-target', [])
    aliases({'actions': [{'remove': {'index': V3, 'alias': READ, 'must_exist': True}},
                         {'add': {'index': V2, 'alias': READ, 'is_write_index': False}}]})
    observe('06-target-repaired', [('p01', 6500), ('p02', 0)])
    fields(V1, 'v001', ['p07']); fields(V2, 'v002', ['p08'])
    for index in [V1, V2]:
        check(not req('/' + index + '/_doc/p09', expected=404)['found'], 'rejected write leaked')
    final = alias_state()
    check(final[V1]['aliases'] == {WRITE: {'is_write_index': False}}
          and final[V2]['aliases'] == {READ: {'is_write_index': False}, WRITE: {'is_write_index': True}}, final)
    save('aliases-final.json', final)
    after = identity()
    check(before['root']['cluster_uuid'] == after['root']['cluster_uuid'] and set(before['nodes']) == set(after['nodes']), 'identity changed')
    for node in after['nodes']:
        fields(V1, 'v001', ['p07'], '&preference=_only_nodes:' + node)
        fields(V2, 'v002', ['p08'], '&preference=_only_nodes:' + node)
    check(req('/_cluster/settings?flat_settings=true', kind='guard') == baseline, 'cluster settings changed')
    save('identity-final.json', after)
    save('final-layout.json', req('/_cat/shards?format=json&h=index,shard,prirep,state,docs,node'))


def main():
    global OUT, OBSERVER
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'run', 'cleanup', 'down'])
    parser.add_argument('--out', type=pathlib.Path, required=True)
    parser.add_argument('--observer', type=pathlib.Path)
    args = parser.parse_args()
    OUT = args.out.resolve(); OUT.mkdir(parents=True, exist_ok=False)
    if args.observer:
        spec = importlib.util.spec_from_file_location('f32_observer', args.observer.resolve())
        OBSERVER = importlib.util.module_from_spec(spec); spec.loader.exec_module(OBSERVER)
    try:
        if args.action == 'down':
            owned(); compose('down')
        else:
            globals()[args.action]()
        counts = collections.Counter(e['case'] for e in EVENTS if e['kind'] == 'teaching')
        summary = {'action': args.action, 'passed': True, 'teaching_http_by_case': dict(counts),
                   'teaching_http_total': sum(counts.values()),
                   'http_by_kind': dict(collections.Counter(e['kind'] for e in EVENTS if 'url' in e)),
                   'official_java_client_writes': sum(e['kind'] == 'java-client' for e in EVENTS),
                   'observer': str(args.observer) if args.observer else None}
        save('summary.json', summary); print(json.dumps(summary))
    except BaseException as error:
        save('failure.json', {'case': CASE, 'error': repr(error)})
        raise


if __name__ == '__main__':
    main()
