#!/usr/bin/env python3
"""F34: snapshot status, logical deletion, partial snapshot and isolated restore."""
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
INFRA = P / 'infra/f34'
BASE = 'http://127.0.0.1:19834'
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18082').rstrip('/')
MAIN = 'tut-f34-attractions-v001'
RISK = 'tut-f34-risk'
RESTORED = 'tut-f34-restore-attractions-v001'
PART_MAIN = 'tut-f34-partial-attractions-v001'
PART_RISK = 'tut-f34-partial-risk'
READ = 'tut-f34-attractions-read'
REPO, BAD_REPO = 'tut-f34-fs', 'tut-f34-outside'
GOOD, PARTIAL = 'before-delete', 'missing-primary'
INDICES = [MAIN, RISK, RESTORED, PART_MAIN, PART_RISK]
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
    p = command(['docker', 'ps', '-aq', '--filter', 'label=com.docker.compose.project=es-framework-f34'])
    if p.stdout.strip():
        for c in json.loads(command(['docker', 'inspect'] + p.stdout.split()).stdout):
            labels = c['Config']['Labels']
            check(labels.get('esweb.lesson') == 'f34'
                  and labels.get('com.docker.compose.service') in ['n1', 'n2', 'repo-init'], c['Name'])


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


def wait(index=None, nodes=2, status='green'):
    deadline = time.monotonic() + 150
    while time.monotonic() < deadline:
        try:
            r = req('/_cluster/health' + ('/' + index if index else '')
                    + '?wait_for_status=' + status + '&wait_for_nodes=' + str(nodes)
                    + '&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=2s', kind='wait', expected=None)
            if r.get('number_of_nodes') == nodes and r['status'] == status and not r.get('timed_out'):
                return r
        except (OSError, ValueError):
            pass
        time.sleep(2)
    raise AssertionError('Target health/node wait timed out')


def identity(bootstrap=False):
    root = req(kind='identity')
    nodes = req('/_nodes/settings,jvm?flat_settings=true', kind='identity')['nodes']
    check(len(nodes) == 2 and root['cluster_uuid'] != '_na_', root)
    for node in nodes.values():
        n1 = node['name'] == 'travel-f34-n1'
        check(node['name'] in ['travel-f34-n1', 'travel-f34-n2'], node)
        check(set(node['roles']) == ({'master', 'data', 'ingest'} if n1 else {'data'}), node)
        check(('cluster.initial_master_nodes' in node['settings']) == (bootstrap and n1), node)
    return {'root': root, 'nodes': nodes}


def guard():
    owned()
    r = req(kind='guard')
    check(r['cluster_name'] == 'travel-f34-lab' and r['version']['number'] == '9.4.0'
          and r['version']['lucene_version'] == '10.4.0', r)
    names = req('/_cat/indices?format=json&expand_wildcards=all&h=index', kind='guard')
    system_prefixes = ('.ds-.logs-elasticsearch.deprecation-default-', '.ds-ilm-history-7-')
    check(all(x['index'] in INDICES or x['index'].startswith(system_prefixes) for x in names),
          'F34 needs a dedicated cluster without foreign business indices')
    for api, key, allowed in [('_index_template', 'index_templates', TEMPLATES),
                              ('_component_template', 'component_templates', COMPONENTS)]:
        templates = req('/' + api, kind='guard')[key]
        check(all(not x['name'].startswith('tut-') or x['name'] in allowed for x in templates), templates)


    repositories = req('/_snapshot', kind='guard')
    check(set(repositories).issubset({REPO, BAD_REPO}), 'Foreign snapshot repositories')
    if REPO in repositories:
        snapshots = req('/_snapshot/' + REPO + '/_all', kind='guard')['snapshots']
        check(all(s['snapshot'] in [GOOD, PARTIAL] and s['state'] in ['SUCCESS', 'PARTIAL', 'FAILED']
                  for s in snapshots), 'Foreign or running snapshot; stop rather than remove')


def start():
    owned()
    exists = []
    for n in ['n1', 'n2']:
        p = command(['docker', 'volume', 'inspect', 'es-framework-f34-' + n + '-data'], expected=None)
        exists.append(p.returncode == 0)
        if p.returncode == 0:
            check(json.loads(p.stdout)[0]['Labels'].get('esweb.lesson') == 'f34', 'foreign volume')
    check(all(exists) or not any(exists), 'Partial base volumes: recover original volumes; do not bootstrap')
    volume = command(['docker', 'volume', 'inspect', 'es-framework-f34-snapshots'], expected=None)
    if volume.returncode == 0:
        check(json.loads(volume.stdout)[0]['Labels'].get('esweb.lesson') == 'f34', 'foreign repository volume')
    # A new Docker volume at /mnt is root-owned. Only set ownership on this lab's mount root.
    compose('run', '--rm', '--no-deps', 'repo-init')
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
    # Restore n2 first, including after an interrupted incomplete-snapshot exercise.
    compose('up', '-d', 'n2')
    wait()
    for index in INDICES:
        r = req('/' + index, 'DELETE', expected=None, kind='cleanup')
        check(r.get('acknowledged') or r.get('status') == 404, r)
    repos = req('/_snapshot', kind='guard')
    if REPO in repos:
        for snapshot in [GOOD, PARTIAL]:
            r = req('/_snapshot/' + REPO + '/' + snapshot, 'DELETE', expected=None, kind='cleanup')
            check(r.get('acknowledged') or r.get('status') == 404, r)
    for repo in [REPO, BAD_REPO]:
        r = req('/_snapshot/' + repo, 'DELETE', expected=None, kind='cleanup')
        check(r.get('acknowledged') or r.get('status') == 404, r)


def fixture(name):
    return load('search/f34/' + name + '.json')


def create(index, name):
    r = req('/' + index, 'PUT', fixture(name))
    check(r['acknowledged'] and r['shards_acknowledged'], r)
    wait(index)


def search(index, body=None):
    r = req('/' + index + '/_search?allow_partial_search_results=false', 'POST', body or fixture('search'))
    check(not r['timed_out'] and r['_shards']['failed'] == 0 and r['hits']['total']['relation'] == 'eq', r)
    return r


def fields(index, expected, node=None):
    r = req('/' + index + '/_search?allow_partial_search_results=false'
            + ('&preference=_only_nodes:' + node if node else ''), 'POST', fixture('fields'))
    check(not r['timed_out'] and r['_shards']['failed'] == 0
          and r['hits']['total'] == {'value': len(expected), 'relation': 'eq'}, r)
    check([h['_id'] for h in r['hits']['hits']] == [d['attraction_id'] for d in expected]
          and [h['_source'] for h in r['hits']['hits']] == expected, r)
    return r


def aliases(name):
    r = req('/_aliases', 'POST', fixture(name))
    check(r.get('acknowledged') and not r.get('errors'), r)


def alias_state(target):
    r = req('/_alias/' + READ)
    check(r == {target: {'aliases': {READ: {'is_write_index': False}}}}, r)
    return r


def observe(stage, rows):
    r = req('/api/attractions/search', 'POST', fixture('input'), base=APP, kind='java-api')
    check(r['total'] == len(rows) and r['esRequest'] == fixture('search'), r)
    check([(x['id'], x['ticketPriceFen']) for x in r['items']] == rows, r)
    replay = search(READ, r['esRequest'])
    check([(x['_id'], x['_source']['ticket_price_fen']) for x in replay['hits']['hits']] == rows, replay)
    for card, hit in zip(r['items'], replay['hits']['hits']):
        d = hit['_source']
        check((card['name'], card['cityCode'], card['currency'], card['status']) ==
              (d['name'], d['city_code'], d['currency'], d['status']), r)
    save(stage + '-java.json', r)
    if OBSERVER:
        OBSERVER.capture(stage, rows, 200, APP, BASE, READ, OUT)


def snapshot(name, request, state, total, successful, failed):
    if name == GOOD:
        r = req('/_snapshot/' + REPO + '/' + name + '?wait_for_completion=false', 'PUT', fixture(request))
        check(r == {'accepted': True}, r)
        save('snapshot-accepted.json', r)
        # No assumption that a tiny snapshot remains IN_PROGRESS long enough to observe.
        deadline = time.monotonic() + 150
        while time.monotonic() < deadline:
            r = req('/_snapshot/' + REPO + '/' + name, kind='wait')
            if r['snapshots'][0]['state'] in ['SUCCESS', 'PARTIAL', 'FAILED']:
                break
            time.sleep(1)
        else:
            raise AssertionError('Snapshot did not finish')
    else:
        r = req('/_snapshot/' + REPO + '/' + name + '?wait_for_completion=true', 'PUT', fixture(request))
        check(r['snapshot']['state'] == state, r)
    info = req('/_snapshot/' + REPO + '/' + name)['snapshots'][0]
    check(info['state'] == state and info['shards'] == {'total': total, 'failed': failed, 'successful': successful}, info)
    check(info['include_global_state'] is False and not info['feature_states'], info)
    check(len(info['failures']) == failed, info)
    save(name + '-snapshot.json', info)
    status = req('/_snapshot/' + REPO + '/' + name + '/_status')['snapshots'][0]
    # In 9.4.0 the status API maps completed SUCCESS and PARTIAL to SUCCESS.
    # Snapshot metadata plus failed-shard counts decide completeness.
    check(status['state'] == 'SUCCESS' and status['shards_stats']['total'] == total
          and status['shards_stats']['done'] == successful and status['shards_stats']['failed'] == failed, status)
    save(name + '-status.json', status)
    return info


def restore(name, request, expected=200):
    r = req('/_snapshot/' + REPO + '/' + name + '/_restore?wait_for_completion=true', 'POST', fixture(request), expected=expected)
    save(request + '-response.json', r)
    if expected == 200:
        expected_shards = {'total': 3, 'failed': 1, 'successful': 2} if request == 'restore-partial-accepted' else {'total': 2, 'failed': 0, 'successful': 2}
        check(r['snapshot']['shards'] == expected_shards, r)
    else:
        check(r['error']['type'] == 'snapshot_restore_exception', r)
    return r


def run():
    global CASE
    guard()
    cleanup()
    before = identity()
    baseline = req('/_cluster/settings?flat_settings=true', kind='guard')
    check(baseline == {'persistent': {}, 'transient': {}}, baseline)
    original = load('data/f34/v001.json')
    current = [load('data/f34/p01-updated.json')] + original[2:]
    CASE = 'f34-c01-repository-and-complete-snapshot'
    error = req('/_snapshot/' + BAD_REPO, 'PUT', fixture('repository-bad'), expected=500)
    check(error['error']['type'] == 'repository_exception' and 'path.repo' in json.dumps(error), error)
    save('repository-path-error.json', error)
    check(BAD_REPO not in req('/_snapshot'), 'Rejected registration left a repository')
    r = req('/_snapshot/' + REPO, 'PUT', fixture('repository'))
    check(r['acknowledged'], r)
    registered = req('/_snapshot/' + REPO)
    check(registered[REPO]['type'] == 'fs' and registered[REPO]['settings']['location'] == 'travel-f34', registered)
    verify = req('/_snapshot/' + REPO + '/_verify', 'POST')
    check(set(verify['nodes']) == set(before['nodes']), verify)
    save('repository-verify.json', verify)
    create(MAIN, 'create-main')
    r = req('/' + MAIN + '/_bulk?wait_for_active_shards=all', 'POST', (P / 'data/f34/v001.ndjson').read_text())
    check(not r['errors'] and len(r['items']) == 6
          and all(x['create']['status'] == 201 and x['create']['_shards']['successful'] == 2 for x in r['items']), r)
    aliases('aliases-initial')
    r = req('/' + MAIN + '/_block/write', 'PUT')
    check(r['acknowledged'] and r['shards_acknowledged'] and all(x['blocked'] for x in r['indices']), r)
    req('/' + MAIN + '/_refresh', 'POST')
    fields(MAIN, original)
    alias_state(MAIN)
    observe('01-before-backup', [('p01', 6000), ('p02', 0)])
    snapshot(GOOD, 'snapshot-good', 'SUCCESS', 2, 2, 0)

    CASE = 'f34-c02-logical-delete-and-incomplete-snapshot'
    req('/' + MAIN + '/_settings', 'PUT', {'index.blocks.write': False})
    r = req('/' + MAIN + '/_doc/p01?wait_for_active_shards=all', 'PUT', load('data/f34/p01-updated.json'))
    check(r['result'] == 'updated' and r['_shards']['successful'] == 2, r)
    r = req('/' + MAIN + '/_doc/p02?wait_for_active_shards=all', 'DELETE')
    check(r['result'] == 'deleted' and r['_shards']['successful'] == 2, r)
    req('/' + MAIN + '/_refresh', 'POST')
    for node in before['nodes']:
        fields(MAIN, current, node)
    check(not req('/' + MAIN + '/_doc/p02', expected=404)['found'], 'Deleted document remains')
    observe('02-delete-reaches-replicas', [('p01', 6500)])
    create(RISK, 'create-risk')
    r = req('/' + RISK + '/_doc/risk-01', 'PUT', load('data/f34/risk.json'), expected=201)
    check(r['result'] == 'created', r)
    req('/' + RISK + '/_refresh', 'POST')
    check(req('/' + RISK + '/_count')['count'] == 1, 'risk fixture missing')
    layout = req('/_cat/shards/' + RISK + '?format=json&h=index,shard,prirep,state,docs,node')
    check(len(layout) == 1 and layout[0]['node'] == 'travel-f34-n2' and layout[0]['state'] == 'STARTED', layout)
    save('risk-before-stop.json', layout)
    compose('stop', 'n2')
    try:
        wait(MAIN, nodes=1, status='yellow')
        unavailable = req('/_cat/shards/' + RISK + '?format=json&h=index,shard,prirep,state,node')
        check(len(unavailable) == 1 and unavailable[0]['state'] == 'UNASSIGNED', unavailable)
        save('risk-unavailable.json', unavailable)
        partial = snapshot(PARTIAL, 'snapshot-partial', 'PARTIAL', 3, 2, 1)
        check(partial['failures'][0]['index'] == RISK, partial)
    finally:
        # A failed assertion must not leave the data node stopped.
        compose('up', '-d', 'n2')
        wait()
    check(req('/' + RISK + '/_count')['count'] == 1, 'n2 original volume not recovered')
    restore(PARTIAL, 'restore-partial-refused', expected=500)
    # Explicit opt-in is a loss demonstration, never the complete-restore path.
    restore(PARTIAL, 'restore-partial-accepted')
    wait(PART_MAIN + ',' + PART_RISK)
    fields(PART_MAIN, current)
    check(req('/' + PART_RISK + '/_count')['count'] == 0, 'Missing shard was not recreated empty')
    empty = req('/' + PART_RISK + '/_recovery?detailed=true')
    check(any(s['type'] == 'EMPTY_STORE' and s['stage'] == 'DONE' for s in empty[PART_RISK]['shards']), empty)
    save('partial-empty-store-recovery.json', empty)
    check(req('/' + RISK + '/_count')['count'] == 1, 'Partial restore changed original risk index')
    save('partial-is-not-complete.json', {'snapshot_state': 'PARTIAL', 'risk_original_count': 1, 'risk_restored_count': 0,
                                       'missing_shard_recreated_empty': True})
    alias_state(MAIN)

    CASE = 'f34-c03-isolated-complete-restore-and-search'
    restore(GOOD, 'restore-conflict', expected=500)
    alias_state(MAIN)
    restore(GOOD, 'restore-good')
    wait(RESTORED)
    req('/' + RESTORED + '/_refresh', 'POST')
    check(req('/' + RESTORED + '/_count')['count'] == 6, 'Complete restore count')
    for node in before['nodes']:
        fields(RESTORED, original, node)
    fields(MAIN, current)
    old = req('/' + RESTORED + '/_doc/p02')
    check(old['found'] and old['_source'] == original[1], old)
    check(not req('/' + MAIN + '/_doc/p02', expected=404)['found'], 'Source unexpectedly restored')
    for index in [MAIN, RESTORED]:
        mapping = req('/' + index + '/_mapping')[index]['mappings']
        settings = req('/' + index + '/_settings?flat_settings=true')[index]['settings']
        check(mapping == fixture('create-main')['mappings'], mapping)
        check(settings['index.number_of_shards'] == '2' and settings['index.number_of_replicas'] == '1'
              and settings['index.refresh_interval'] == '-1', settings)
        check((settings.get('index.blocks.write') == 'true') == (index == RESTORED), settings)
    check(req('/' + RESTORED + '/_alias')[RESTORED]['aliases'] == {}, 'Snapshot alias reattached')
    recovered = search(RESTORED)
    check([(h['_id'], h['_source']['ticket_price_fen']) for h in recovered['hits']['hits']]
          == [('p01', 6000), ('p02', 0)], recovered)
    save('complete-restored-query.json', recovered)
    recovery = req('/' + RESTORED + '/_recovery?detailed=true')
    check(any(s['type'] == 'SNAPSHOT' and s['stage'] == 'DONE' for s in recovery[RESTORED]['shards']), recovery)
    save('snapshot-recovery.json', recovery)
    alias_state(MAIN)
    observe('03-restored-isolated-live-unchanged', [('p01', 6500)])
    aliases('aliases-restored')
    save('read-alias-restored.json', alias_state(RESTORED))
    observe('04-read-validated-historical-copy', [('p01', 6000), ('p02', 0)])
    fields(MAIN, current)
    after = identity()
    check(before['root']['cluster_uuid'] == after['root']['cluster_uuid'] and set(before['nodes']) == set(after['nodes']), 'Identity changed')
    check(req('/_cluster/settings?flat_settings=true', kind='guard') == baseline, 'Cluster settings changed')
    save('identity-final.json', after)
    save('final-layout.json', req('/_cat/shards/' + ','.join(INDICES) + '?format=json&h=index,shard,prirep,state,docs,node'))


def main():
    global OUT, OBSERVER
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'run', 'cleanup', 'down'])
    parser.add_argument('--out', type=pathlib.Path, required=True)
    parser.add_argument('--observer', type=pathlib.Path)
    args = parser.parse_args()
    OUT = args.out.resolve(); OUT.mkdir(parents=True, exist_ok=False)
    if args.observer:
        spec = importlib.util.spec_from_file_location('f34_observer', args.observer.resolve())
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
                   'observer': str(args.observer) if args.observer else None}
        save('summary.json', summary); print(json.dumps(summary))
    except BaseException as error:
        save('failure.json', {'case': CASE, 'error': repr(error)})
        raise


if __name__ == '__main__':
    main()
