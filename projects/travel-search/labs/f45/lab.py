#!/usr/bin/env python3
"""F45 independent capstone: frozen acceptance boundary, real CDC and ES."""
import argparse
import gzip
import hashlib
import json
import os
import pathlib
import secrets
import subprocess
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
INFRA = ROOT / 'infra/f45'
LOCAL = INFRA / '.local'
ES = 'http://127.0.0.1:20945'
CONNECT = 'http://127.0.0.1:18345'
TOPIC = 'travel_f45.f45.projection_event'
INDEX = 'tut-f45-attractions-v001'
READ = 'tut-f45-attractions-read'
HOTELS = 'tut-f45-hotels'


def check(ok, detail):
    if not ok:
        raise AssertionError(detail)


def command(args, data=None, required=True, timeout=120):
    r = subprocess.run(args, input=data, text=True, capture_output=True, cwd=ROOT, timeout=timeout)
    if required:
        check(r.returncode == 0, {'args': args, 'code': r.returncode, 'stdout': r.stdout[-2500:], 'stderr': r.stderr[-2500:]})
    return r


def compose(*args):
    return ['docker', 'compose', '-f', str(INFRA / 'compose.yaml'), *args]


def kafka(tool, *args):
    return compose('exec', '-T', 'kafka', '/opt/kafka/bin/' + tool + '.sh', '--bootstrap-server', 'kafka:9092', *args)


def sql(text):
    return command(compose('exec', '-T', 'postgres', 'psql', '-X', '-qAt', '-v', 'ON_ERROR_STOP=1', '-U', 'travel', '-d', 'travel_f45'), text).stdout


def wait(test, why):
    for _ in range(90):
        try:
            result = test()
            if result:
                return result
        except (OSError, urllib.error.URLError, AssertionError, json.JSONDecodeError):
            pass
        time.sleep(1)
    raise TimeoutError(why)


def read(name):
    return json.loads((ROOT / name).read_text())


def ids(reply):
    check(not reply['timed_out'] and reply['_shards']['failed'] == 0, 'Incomplete search')
    return [h['_id'] for h in reply['hits']['hits']]


class Lab:
    def __init__(self, out):
        self.out = pathlib.Path(out).resolve()
        self.out.mkdir(parents=True, exist_ok=False)
        self.http = 0

    def save(self, name, value):
        (self.out / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

    def req(self, method, path, body=None, base=ES, expected=200, record=True):
        raw = None if body is None else (body.encode() if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode())
        req = urllib.request.Request(base + path, data=raw, method=method,
            headers={'Content-Type': 'application/x-ndjson' if isinstance(body, str) else 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                status, raw = r.status, r.read()
        except urllib.error.HTTPError as e:
            status, raw = e.code, e.read()
        value = json.loads(raw) if raw else None
        row = {'method': method, 'base': base, 'path': path, 'body': body, 'status': status, 'response': value}
        if record:
            self.http += 1
            with gzip.open(self.out / 'http.jsonl.gz', 'at') as f:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
        check(status in ([expected] if isinstance(expected, int) else expected), row)
        return value

    def worker(self, name, *args, expected=0):
        r = command(['bash', 'labs/f45/java.sh', *map(str, args)], required=False)
        records = [json.loads(x) for x in r.stdout.splitlines() if x.startswith('{')]
        self.save(name, {'args': args, 'code': r.returncode, 'records': records})
        (self.out / (name + '.stderr.txt')).write_text(r.stderr)
        check(r.returncode == expected, {'name': name, 'code': r.returncode, 'records': records, 'stderr': r.stderr[-2000:]})
        return records

    def position(self):
        r = command(['bash', 'labs/f45/java.sh', 'inspect'])
        return json.loads(r.stdout.splitlines()[-1])

    def boundary(self, count):
        # The only source writer has finished; verify actual event IDs too.
        wait(lambda: self.position()['end'] == count, 'CDC events at frozen source boundary')
        rows = self.worker('events-' + str(count), 'events', count)
        events = [json.loads(x['value']) for x in rows if x.get('kind') == 'event']
        check(sorted(e['after']['event_id'] for e in events) == list(range(1, count + 1)), events)
        self.save('boundary-' + str(count), {'source_event_ids': list(range(1, count + 1)), 'kafka': self.position(),
            'source_writes_paused': True, 'connector': self.req('GET', '/connectors/f45-pg/status', base=CONNECT)})
        return count

    def identity(self):
        root = self.req('GET', '/')
        check(root['cluster_name'] == 'travel-f45-lab' and root['version']['number'] == '9.4.0', root)
        nodes = self.req('GET', '/_nodes')
        check(len(nodes['nodes']) == 2 and {n['name'] for n in nodes['nodes'].values()} == {'f45-n1', 'f45-n2'}, nodes)
        pg = sql('SELECT current_database(),version();')
        check(pg.startswith('travel_f45|PostgreSQL 17.5'), pg)
        plugins = self.req('GET', '/connector-plugins', base=CONNECT)
        check(any(p['class'] == 'io.debezium.connector.postgresql.PostgresConnector' and p['version'] == '3.3.1.Final' for p in plugins), plugins)
        self.save('identity', {'es': root, 'nodes': nodes, 'postgres': pg, 'connector_plugins': plugins})

    def refresh(self):
        for index in [INDEX, HOTELS]:
            check(self.req('POST', '/' + index + '/_refresh')['_shards']['failed'] == 0, 'Refresh failure')

    def search(self, name, java=True):
        body = read('search/f45/' + name + '.json')
        index = HOTELS if name.startswith('hotels') else READ
        rest = self.req('POST', '/' + index + '/_search?allow_partial_search_results=false', body)
        ids(rest)
        if java:
            reply = self.worker('java-' + name + '-' + str(self.http), 'search', name)[-1]
            check(reply['request'] == body, 'Java serialized DSL differs')
            check(ids(reply['reply']) == ids(rest), 'REST/Java IDs differ')
            check([h['_source'] for h in reply['reply']['hits']['hits']] == [h['_source'] for h in rest['hits']['hits']], 'REST/Java fields differ')
        return rest

    def source_docs(self):
        raw = sql('SELECT row_to_json(a)::text FROM f45.attractions a ORDER BY attraction_id;').splitlines()
        docs = {}
        for text in raw:
            doc = json.loads(text)
            doc['sync_hash'] = hashlib.sha256(text.encode()).hexdigest()
            docs[doc['attraction_id']] = doc
        return docs

    def reconcile(self, label):
        expected = self.source_docs()
        reply = self.req('POST', '/' + INDEX + '/_search?allow_partial_search_results=false', {'size': 100, 'query': {'match_all': {}}})
        check(reply['hits']['total']['value'] == len(expected) == 8 and len(ids(reply)) == 8, 'Full physical scope required')
        actual = {h['_id']: h['_source'] for h in reply['hits']['hits']}
        check(actual == expected, {'expected': expected, 'actual': actual})
        self.save(label, {'source': expected, 'es': actual, 'equal': True})

    def prepare(self):
        self.identity()
        check(self.req('GET', '/connectors', base=CONNECT) == [], 'Run requires empty F45 connector scope')
        check(sql("SELECT to_regnamespace('f45');").strip() == '', 'F45 schema already exists; use cleanup')
        for index in [INDEX, HOTELS]:
            self.req('GET', '/' + index, expected=404)
        password = (LOCAL / 'cdc-password.txt').read_text().strip()
        # Random hex password is passed on stdin; do not put it in evidence/argv.
        sql("CREATE ROLE f45_cdc LOGIN REPLICATION PASSWORD '" + password + "'; GRANT CONNECT ON DATABASE travel_f45 TO f45_cdc;")
        sql((ROOT / 'data/f45/schema.sql').read_text())
        sql((ROOT / 'data/f45/seed.sql').read_text())
        initial = sql('SELECT document FROM f45.projection_event ORDER BY event_id;').splitlines()
        self.save('initial-documents', initial)
        for index, file in [(INDEX, 'attractions'), (HOTELS, 'hotels')]:
            self.req('PUT', '/' + index, read('search/f45/create-' + file + '.json'))
        self.req('POST', '/_aliases', read('search/f45/aliases.json'))
        command(kafka('kafka-topics', '--create', '--topic', TOPIC, '--partitions', '1', '--replication-factor', '1', '--config', 'retention.ms=604800000'))
        self.req('POST', '/connectors', read('cdc/f45/connector.json'), base=CONNECT, expected=201)
        wait(lambda: all(t['state'] == 'RUNNING' for t in self.req('GET', '/connectors/f45-pg/status', base=CONNECT, record=False)['tasks'])
            and len(self.req('GET', '/connectors/f45-pg/status', base=CONNECT, record=False)['tasks']) == 1, 'Connector task')
        self.boundary(8)
        self.worker('seed', 'seed', 0)
        self.worker('initial-drain', 'drain', 8)
        self.refresh()
        health = self.req('GET', '/_cluster/health/' + INDEX + ',' + HOTELS + '?wait_for_status=green&timeout=30s')
        check(health['status'] == 'green' and not health['timed_out'] and health['number_of_nodes'] == 2, health)
        shards = self.req('GET', '/_cat/shards/' + INDEX + ',' + HOTELS + '?format=json&h=index,shard,prirep,state,node')
        check(len(shards) == 4 and all(s['state'] == 'STARTED' for s in shards), shards)
        for index in [INDEX, HOTELS]:
            rows = [s for s in shards if s['index'] == index]
            check({s['prirep'] for s in rows} == {'p', 'r'} and len({s['node'] for s in rows}) == 2, rows)
        self.save('layout', {'health': health, 'shards': shards})
        self.reconcile('initial-full-fields')

    def hotels(self):
        table = read('data/f45/stay-table.json')
        projected, omitted = [], []
        expected = []
        for h in table['hotels']:
            offers = []
            for o in h['offers']:
                nights = o['nights']
                if [n['date'] for n in nights] != ['2027-04-03', '2027-04-04'] or any(n['stock'] < 1 or n['price_fen'] is None for n in nights) or o['min_nights'] > 2:
                    omitted.append({'hotel_id': h['hotel_id'], 'offer_id': o['offer_id'], 'reason': 'night coverage, stock, price or minimum stay'})
                    continue
                doc = {k: o[k] for k in ['offer_id', 'capacity', 'accessible', 'breakfast', 'refundable', 'currency']}
                doc.update(check_in=table['check_in'], check_out=table['check_out'], total_price_fen=sum(n['price_fen'] for n in nights))
                offers.append(doc)
                if o['capacity'] >= 2 and o['accessible'] and o['breakfast'] and o['refundable'] and o['currency'] == 'CNY' and doc['total_price_fen'] <= 65000:
                    expected.append((h['hotel_id'], o['offer_id'], doc['total_price_fen']))
            projected.append({'hotel_id': h['hotel_id'], 'name': h['name'], 'city_code': 'HZ', 'status': 'open', 'offers': offers})
        ndjson = ''.join(json.dumps({'index': {'_index': HOTELS, '_id': h['hotel_id']}}) + '\n' + json.dumps(h, ensure_ascii=False) + '\n' for h in projected)
        bulk = self.req('POST', '/_bulk', ndjson)
        check(not bulk['errors'], bulk)
        self.refresh()
        good = self.search('hotels')
        check(ids(good) == ['h03', 'h02'] and good['hits']['total']['value'] == 2, good)
        actual = []
        for h in good['hits']['hits']:
            inner = h['inner_hits']['eligible']['hits']
            check(inner['total']['value'] == len(inner['hits']) == 1, inner)
            for o in inner['hits']:
                actual.append((h['_id'], o['_source']['offer_id'], o['_source']['total_price_fen']))
            check(h['sort'][0] == inner['hits'][0]['_source']['total_price_fen'], h)
        check(actual == sorted(expected, key=lambda x: (x[2], x[0])), {'actual': actual, 'source_expected': expected})
        bad = self.search('hotels-wrong', java=False)
        check(ids(bad) == ['h01', 'h02', 'h03'], bad)
        self.save('c02', {'source_table': table, 'projection': projected, 'omitted': omitted, 'eligible': actual, 'correct': good, 'split_nested_wrong': bad})

    def observe(self, stage, enabled):
        if enabled:
            env_python = os.environ.get('F45_BROWSER_PYTHON', 'python3')
            script = ROOT.parents[1] / 'docs/framework-review/20261101-f45-capstone/observe.py'
            r = command([env_python, str(script), str(self.out), stage])
            (self.out / ('observer-' + stage + '.log')).write_text(r.stdout + r.stderr)

    def run(self, observer):
        print('Preparing independent F45 sources and cluster', flush=True)
        self.prepare()
        before = self.search('attractions')
        check(ids(before) == ['n02', 'n01'] and [h['_source']['ticket_price_fen'] for h in before['hits']['hits']] == [4000, 6000], before)
        self.save('c01', {'reply': before, 'excluded': {'n03': 'accessible=false', 'n04': 'closed', 'n05': 'outside 3km', 'n06': '120 minutes', 'n07': 'other city', 'n08': 'missing 夜游'}})
        self.observe('initial', observer)
        print('Attractions passed; checking same-offer hotel requirements', flush=True)
        self.hotels()
        sql((ROOT / 'data/f45/changes.sql').read_text())
        self.boundary(10)
        frozen_source = self.source_docs()
        old = self.position()
        self.req('PUT', '/' + INDEX + '/_settings', {'index.blocks.write': True})
        print('Injecting real ES write block', flush=True)
        try:
            failed = self.worker('blocked-drain', 'drain', 10, expected=1)
            check([x['status'] for x in failed if x.get('kind') == 'item'] == [403, 403], failed)
            blocked = self.position()
            check(blocked['next'] == old['next'] == 8 and blocked['end'] == 10, blocked)
            stale = self.search('attractions')
            check(ids(stale) == ['n02', 'n01'] and stale['hits']['hits'][1]['_source']['ticket_price_fen'] == 6000, stale)
        finally:
            self.req('PUT', '/' + INDEX + '/_settings', {'index.blocks.write': None})
        self.worker('recovered-drain', 'drain', 10)
        applied = self.position()
        check(applied['next'] == 10, applied)
        get = self.req('GET', '/' + INDEX + '/_doc/n01')
        check(get['_source']['ticket_price_fen'] == 4500, get)
        still_stale = self.search('attractions')
        check(ids(still_stale) == ['n02', 'n01'] and still_stale['hits']['hits'][1]['_source']['ticket_price_fen'] == 6000, still_stale)
        self.refresh()
        after = self.search('attractions')
        check(ids(after) == ['n01'] and after['hits']['hits'][0]['_source']['ticket_price_fen'] == 4500, after)
        self.reconcile('recovered-full-fields')
        replay = self.worker('old-snapshot-replay', 'replay', str(self.out / 'initial-documents.json'))
        check(len(replay) == 8 and all(x['result'] == 'noop' for x in replay), replay)
        self.refresh()
        self.reconcile('after-replay-full-fields')
        check(self.position() == applied, 'Replay must not change consumer position')
        self.observe('recovered', observer)
        self.save('c03', {'frozen_source': frozen_source, 'before': old, 'blocked': blocked, 'after': applied,
            'get_before_refresh': get, 'search_before_refresh': still_stale, 'search_after_refresh': after,
            'old_replay': replay, 'deleted_id': 'n02', 'physical_documents': 8, 'logical_deleted': 1})
        self.save('summary', {'passed': True, 'cases': ['f45-c01', 'f45-c02', 'f45-c03'], 'explicit_rest_calls': self.http,
            'observer_executed': observer, 'source_event_count': 10, 'committed_next': 10})
        print('F45 three cases passed', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['init', 'start', 'prepare', 'run', 'cleanup', 'down'])
    parser.add_argument('--out', required=True)
    parser.add_argument('--observer', action='store_true')
    args = parser.parse_args()
    lab = Lab(args.out)
    if args.mode == 'init':
        check(not LOCAL.exists(), 'F45 local credentials already exist')
        volumes = command(['docker', 'volume', 'ls', '-q', '--filter', 'label=com.docker.compose.project=es-framework-f45']).stdout
        check(not volumes.strip(), 'Existing F45 volumes; preserve their original credentials')
        LOCAL.mkdir(mode=0o700)
        admin, cdc = secrets.token_hex(24), secrets.token_hex(24)
        for name, value in [('pg-password.txt', admin), ('cdc-password.txt', cdc), ('cdc.properties', 'password=' + cdc)]:
            path = LOCAL / name
            path.write_text(value + '\n'); path.chmod(0o600)
        lab.save('init', {'generated_local_credentials': True, 'secrets_committed': False})
    elif args.mode == 'start':
        check(LOCAL.exists(), 'Run init first')
        marker = LOCAL / 'cluster-uuid.txt'
        first = not marker.exists()
        cmd = compose('up', '-d') if not first else compose('-f', str(INFRA / 'bootstrap.yaml'), 'up', '-d')
        (lab.out / 'compose.log').write_text(command(cmd).stdout)
        def formed():
            value = lab.req('GET', '/', record=False)
            return value if value.get('cluster_uuid') not in [None, '_na_'] else False
        root = wait(formed, 'ES first startup')
        check(root.get('cluster_uuid') not in [None, '_na_'], root)
        if first:
            marker.write_text(root['cluster_uuid'])
            (lab.out / 'remove-bootstrap.log').write_text(command(compose('up', '-d')).stdout)
        wait(lambda: lab.req('GET', '/', record=False).get('cluster_uuid') == marker.read_text(), 'Original cluster UUID')
        wait(lambda: lab.req('GET', '/_cluster/health?wait_for_nodes=2&timeout=1s', record=False).get('number_of_nodes') == 2, 'Two nodes')
        wait(lambda: lab.req('GET', '/connector-plugins', base=CONNECT, record=False), 'Connect plugins')
        wait(lambda: command(kafka('kafka-topics', '--list'), required=False, timeout=20).returncode == 0, 'Kafka')
        lab.identity()
        settings = lab.req('GET', '/_nodes/settings?flat_settings=true')
        check(all('cluster.initial_master_nodes' not in n['settings'] for n in settings['nodes'].values()), settings)
        lab.save('bootstrap', {'cluster_uuid': marker.read_text(), 'first_start': first, 'removed_bootstrap_setting': True})
    elif args.mode == 'prepare':
        lab.prepare()
    elif args.mode == 'run':
        lab.run(args.observer)
    elif args.mode == 'cleanup':
        lab.identity()
        connectors = lab.req('GET', '/connectors', base=CONNECT)
        if 'f45-pg' in connectors:
            lab.req('PUT', '/connectors/f45-pg/stop', {}, base=CONNECT, expected=204)
            wait(lambda: lab.req('GET', '/connectors/f45-pg/status', base=CONNECT, record=False)['connector']['state'] == 'STOPPED', 'Connector stopped')
            lab.req('DELETE', '/connectors/f45-pg/offsets', base=CONNECT)
            lab.req('DELETE', '/connectors/f45-pg', base=CONNECT, expected=204)
        for index in [INDEX, HOTELS]:
            lab.req('DELETE', '/' + index, expected=[200, 404])
            lab.req('GET', '/' + index, expected=404)
        command(kafka('kafka-consumer-groups', '--delete', '--group', 'f45-projection'), required=False)
        topics = command(kafka('kafka-topics', '--list')).stdout.splitlines()
        if TOPIC in topics:
            command(kafka('kafka-topics', '--delete', '--topic', TOPIC))
            wait(lambda: TOPIC not in command(kafka('kafka-topics', '--list')).stdout.splitlines(), 'Topic deletion')
        sql("SELECT pg_drop_replication_slot(slot_name) FROM pg_replication_slots WHERE slot_name='f45_slot';\nDROP PUBLICATION IF EXISTS f45_publication;\nDROP SCHEMA IF EXISTS f45 CASCADE;\nREVOKE CONNECT ON DATABASE travel_f45 FROM f45_cdc;\nDROP ROLE IF EXISTS f45_cdc;")
        lab.save('cleanup', {'indices_absent': True, 'connector_absent': lab.req('GET', '/connectors', base=CONNECT) == [],
            'source_topic_absent': TOPIC not in command(kafka('kafka-topics', '--list')).stdout.splitlines(),
            'schema_absent': sql("SELECT to_regnamespace('f45');").strip() == '', 'local_credentials_and_volumes_preserved': True})
    else:
        (lab.out / 'compose.log').write_text(command(compose('down')).stdout)


if __name__ == '__main__':
    main()
