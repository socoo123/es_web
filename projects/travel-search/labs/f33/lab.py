#!/usr/bin/env python3
"""F33: controlled reindex, frozen reconciliation, alias switch and rollback."""
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
INFRA = P / 'infra/f33'
BASE = 'http://127.0.0.1:19733'
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18082').rstrip('/')
V1, V2 = 'tut-f33-attractions-v001', 'tut-f33-attractions-v002'
READ, WRITE = 'tut-f33-attractions-read', 'tut-f33-attractions-write'
INDICES = [V1, V2]
TEMPLATES, COMPONENTS = [], []
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
    p = command(['docker', 'ps', '-aq', '--filter', 'label=com.docker.compose.project=es-framework-f33'])
    if p.stdout.strip():
        for c in json.loads(command(['docker', 'inspect'] + p.stdout.split()).stdout):
            labels = c['Config']['Labels']
            check(labels.get('esweb.lesson') == 'f33'
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
        n1 = node['name'] == 'travel-f33-n1'
        check(node['name'] in ['travel-f33-n1', 'travel-f33-n2'], node)
        check(set(node['roles']) == ({'master', 'data', 'ingest'} if n1 else {'data'}), node)
        check(('cluster.initial_master_nodes' in node['settings']) == (bootstrap and n1), node)
    return {'root': root, 'nodes': nodes}


def guard():
    owned()
    r = req(kind='guard')
    check(r['cluster_name'] == 'travel-f33-lab' and r['version']['number'] == '9.4.0'
          and r['version']['lucene_version'] == '10.4.0', r)
    names = req('/_cat/indices?format=json&expand_wildcards=all&h=index', kind='guard')
    system_prefixes = ('.ds-.logs-elasticsearch.deprecation-default-', '.ds-ilm-history-7-')
    check(all(x['index'] in INDICES or x['index'].startswith(system_prefixes) for x in names),
          'F33 needs a dedicated cluster without foreign business indices')
    for api, key, allowed in [('_index_template', 'index_templates', TEMPLATES),
                              ('_component_template', 'component_templates', COMPONENTS)]:
        templates = req('/' + api, kind='guard')[key]
        check(all(not x['name'].startswith('tut-') or x['name'] in allowed for x in templates), templates)


def start():
    owned()
    exists = []
    for n in ['n1', 'n2']:
        p = command(['docker', 'volume', 'inspect', 'es-framework-f33-' + n + '-data'], expected=None)
        exists.append(p.returncode == 0)
        if p.returncode == 0:
            check(json.loads(p.stdout)[0]['Labels'].get('esweb.lesson') == 'f33', 'foreign volume')
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


def aliases(fixture):
    r = req('/_aliases', 'POST', load('search/f33/' + fixture + '.json'))
    check(r.get('acknowledged') and not r.get('errors'), r)


def alias_state(target):
    r = req('/_alias/' + READ + ',' + WRITE)
    check(r == {target: {'aliases': {READ: {'is_write_index': False},
                                    WRITE: {'is_write_index': True}}}}, r)
    return r


def search(index, body=None):
    r = req('/' + index + '/_search?allow_partial_search_results=false', 'POST',
            body or load('search/f33/search.json'))
    check(not r['timed_out'] and r['_shards']['failed'] == 0
          and r['hits']['total']['relation'] == 'eq', r)
    return r


def fields(index, expected, suffix=''):
    r = req('/' + index + '/_search?allow_partial_search_results=false' + suffix, 'POST',
            {'size': 20, 'track_total_hits': True, 'query': {'match_all': {}},
             'sort': [{'attraction_id': 'asc'}]})
    check(not r['timed_out'] and r['_shards']['failed'] == 0
          and r['hits']['total'] == {'value': len(expected), 'relation': 'eq'}, r)
    check([h['_id'] for h in r['hits']['hits']] == [d['attraction_id'] for d in expected]
          and [h['_source'] for h in r['hits']['hits']] == expected, r)
    return r


def java_write(ident, fixture=None, ok=True, status=None):
    fixture = fixture or ident
    p = command(['bash', 'labs/f33/java.sh', WRITE, ident, 'data/f33/' + fixture + '.json'])
    r = json.loads(p.stdout)
    event({'kind': 'java-client', 'method': 'PUT', 'target': WRITE, 'id': ident,
           'require_alias': True, 'response': r})
    check(r['ok'] == ok and (ok or r['status'] == status), r)
    return r


def observe(stage, rows):
    r = req('/api/attractions/search', 'POST', load('search/f33/input.json'),
            kind='java-api', base=APP)
    check(r['total'] == len(rows) and r['esRequest'] == load('search/f33/search.json'), r)
    check([(x['id'], x['ticketPriceFen']) for x in r['items']] == rows, r)
    replay = search(READ, r['esRequest'])
    check([(x['_id'], x['_source']['ticket_price_fen']) for x in replay['hits']['hits']] == rows, replay)
    check(all((c['name'], c['cityCode'], c['currency'], c['status']) ==
              (h['_source']['name'], h['_source']['city_code'], h['_source']['currency'], h['_source']['status'])
              for c, h in zip(r['items'], replay['hits']['hits'])), r)
    save(stage + '-java.json', r)
    if OBSERVER:
        OBSERVER.capture(stage, rows, 200, APP, BASE, READ, OUT)


def reindex(label, created, updated):
    r = req('/_reindex?wait_for_completion=true&wait_for_active_shards=all&refresh=true&slices=1',
            'POST', load('search/f33/reindex.json'))
    check(not r['timed_out'] and not r['failures'] and r['version_conflicts'] == 0
          and r['total'] == 6 and r['created'] == created and r['updated'] == updated
          and r['deleted'] == 0, r)
    save(label + '.json', r)


def run():
    global CASE
    guard()
    before = identity()
    baseline = req('/_cluster/settings?flat_settings=true', kind='guard')
    check(baseline == {'persistent': {}, 'transient': {}}, baseline)
    cleanup()
    original = load('data/f33/v001.json')
    current = [load('data/f33/p01-updated.json')] + original[2:] + [load('data/f33/p07.json')]
    CASE = 'f33-c01-schema-and-fixed-copy'
    create(V1, load('search/f33/create-old.json'))
    bulk = req('/' + V1 + '/_bulk?wait_for_active_shards=all', 'POST',
               (P / 'data/f33/v001.ndjson').read_text())
    check(not bulk['errors'] and len(bulk['items']) == 6
          and all(x['create']['status'] == 201 and x['create']['_shards']['successful'] == 2
                  for x in bulk['items']), bulk)
    req('/' + V1 + '/_refresh', 'POST')
    aliases('aliases-initial')
    save('aliases-initial.json', alias_state(V1))
    fields(V1, original)
    error = req('/' + V1 + '/_mapping', 'PUT', load('search/f33/incompatible-mapping.json'), expected=400)
    check('cannot be changed' in json.dumps(error), error)
    save('error-incompatible-mapping.json', error)
    create(V2, load('search/f33/create-new.json'))
    for index, shards, typ in [(V1, '1', 'keyword'), (V2, '2', 'text')]:
        settings = req('/' + index + '/_settings?flat_settings=true')[index]['settings']
        mapping = req('/' + index + '/_mapping')[index]['mappings']
        check(settings['index.number_of_shards'] == shards and settings['index.number_of_replicas'] == '1'
              and settings['index.refresh_interval'] == '-1', settings)
        check(mapping == load('search/f33/create-' + ('old' if index == V1 else 'new') + '.json')['mappings'], mapping)
        tokens = req('/' + index + '/_analyze', 'POST', load('search/f33/analyze.json'))
        check([t['token'] for t in tokens['tokens']] == (['西湖 湖畔'] if index == V1 else ['西湖', '湖畔']), tokens)
    # The source is unchanged throughout this first synchronous copy. No timing race.
    reindex('reindex-initial', 6, 0)
    fields(V2, original)
    check(req('/' + V2 + '/_count')['count'] == 6, 'initial target count')
    check([h['_id'] for h in search(V2)['hits']['hits']] == ['p01', 'p02'], 'new recall')
    observe('01-before-switch-old-recall', [])

    CASE = 'f33-c02-drift-and-frozen-rebuild'
    # Complete the first copy BEFORE these changes; "not following" is deterministic.
    r = req('/' + WRITE + '/_doc/p01?require_alias=true&wait_for_active_shards=all', 'PUT',
            load('data/f33/p01-updated.json'))
    check(r['_index'] == V1 and r['result'] == 'updated', r)
    r = java_write('p01', 'p01-updated')
    check(r['response']['_index'] == V1 and r['response']['result'] == 'updated', r)
    r = req('/' + WRITE + '/_doc/p02?wait_for_active_shards=all', 'DELETE')
    check(r['_index'] == V1 and r['result'] == 'deleted', r)
    r = java_write('p07')
    check(r['response']['_index'] == V1 and r['response']['result'] == 'created', r)
    req('/' + V1 + '/_refresh', 'POST')
    fields(V1, current); fields(V2, original)
    counts = {i: req('/' + i + '/_count')['count'] for i in INDICES}
    check(list(counts.values()) == [6, 6], counts)
    save('equal-counts-different-documents.json', counts)
    # Re-running into a nonempty target overwrites/adds, but cannot infer source deletions.
    reindex('reindex-nonempty-ghost', 1, 5)
    ghost = sorted(current + [original[1]], key=lambda x: x['attraction_id'])
    fields(V2, ghost)
    check(req('/' + V2 + '/_count')['count'] == 7, 'deleted p02 must remain as ghost')
    save('ghost-query.json', search(V2))
    block = req('/' + V1 + '/_block/write', 'PUT')
    check(block['acknowledged'] and block['shards_acknowledged']
          and all(x['blocked'] for x in block['indices']), block)
    save('freeze-source.json', block)
    error = req('/' + WRITE + '/_doc/p09?require_alias=true', 'PUT', load('data/f33/p09.json'), expected=403)
    check(error['error']['type'] == 'cluster_block_exception', error)
    save('error-write-frozen.json', error)
    java_write('p09', ok=False, status=403)
    req('/' + V1 + '/_refresh', 'POST')
    # Only the not-yet-served target is discarded. Source and both aliases stay intact.
    alias_state(V1)
    req('/' + V2, 'DELETE')
    create(V2, load('search/f33/create-new.json'))
    reindex('reindex-frozen-clean', 6, 0)
    fields(V1, current); fields(V2, current)
    for index in INDICES:
        check(req('/' + index + '/_count')['count'] == 6, index)
        check(not req('/' + index + '/_doc/p02', expected=404)['found'], 'deleted p02 leaked')
        check(not req('/' + index + '/_doc/p09', expected=404)['found'], 'rejected write leaked')
    candidate = search(V2)
    check([(h['_id'], h['_source']['ticket_price_fen']) for h in candidate['hits']['hits']]
          == [('p01', 6500), ('p07', 1500)], candidate)
    save('validated-candidate-query.json', candidate)
    observe('02-frozen-source-still-serves', [])

    CASE = 'f33-c03-atomic-switch-and-rollback'
    error = req('/_aliases', 'POST', load('search/f33/aliases-bad-precondition.json'), expected=404)
    check(error['error']['type'] == 'aliases_not_found_exception', error)
    save('error-switch-precondition.json', error)
    save('aliases-after-rejected-switch.json', alias_state(V1))
    aliases('aliases-switch')
    save('aliases-switched.json', alias_state(V2))
    observe('03-switched-to-new', [('p01', 6500), ('p07', 1500)])
    # No business write is allowed during this rollback trial.
    aliases('aliases-rollback')
    save('aliases-rolled-back.json', alias_state(V1))
    observe('04-rollback-old-recall', [])
    r = req('/' + WRITE + '/_doc/p09?require_alias=true', 'PUT', load('data/f33/p09.json'), expected=403)
    check(r['error']['type'] == 'cluster_block_exception', r)
    fields(V1, current); fields(V2, current)
    aliases('aliases-switch')
    alias_state(V2)
    r = java_write('p08')
    check(r['response']['_index'] == V2 and r['response']['result'] == 'created', r)
    req('/' + V2 + '/_refresh', 'POST')
    final = current + [load('data/f33/p08.json')]
    fields(V1, current); fields(V2, final)
    check(not req('/' + V1 + '/_doc/p08', expected=404)['found'], 'old must not follow new writes')
    observe('05-new-writes-break-simple-rollback', [('p01', 6500), ('p07', 1500), ('p08', 2000)])
    save('aliases-final.json', alias_state(V2))
    for index in INDICES:
        s = req('/' + index + '/_settings?flat_settings=true')[index]['settings']
        check((s.get('index.blocks.write') == 'true') == (index == V1), s)
        check(not req('/' + index + '/_doc/p09', expected=404)['found'], 'p09 persisted')
    after = identity()
    check(before['root']['cluster_uuid'] == after['root']['cluster_uuid'] and set(before['nodes']) == set(after['nodes']), 'identity changed')
    for node in after['nodes']:
        fields(V1, current, '&preference=_only_nodes:' + node)
        fields(V2, final, '&preference=_only_nodes:' + node)
    check(req('/_cluster/settings?flat_settings=true', kind='guard') == baseline, 'cluster settings changed')
    save('identity-final.json', after)
    save('final-layout.json', req('/_cat/shards/' + V1 + ',' + V2 + '?format=json&h=index,shard,prirep,state,docs,node'))


def main():
    global OUT, OBSERVER
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'run', 'cleanup', 'down'])
    parser.add_argument('--out', type=pathlib.Path, required=True)
    parser.add_argument('--observer', type=pathlib.Path)
    args = parser.parse_args()
    OUT = args.out.resolve(); OUT.mkdir(parents=True, exist_ok=False)
    if args.observer:
        spec = importlib.util.spec_from_file_location('f33_observer', args.observer.resolve())
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
