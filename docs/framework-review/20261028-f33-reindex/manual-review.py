#!/usr/bin/env python3
"""Verify the separately supplied reader curl path on the dedicated F33 cluster."""
import collections, datetime, gzip, hashlib, json, os, pathlib, subprocess, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = ROOT / 'projects/travel-search'
OUT = P / 'review/f33/manual'
OUT.mkdir(exist_ok=False)
env = dict(os.environ)
env['JAVA_HOME'] = '/tmp/es-f29-tooling/jdk-25.0.4.1+1/Contents/Home'
env['PATH'] = env['JAVA_HOME'] + '/bin:' + env['PATH']
env['APP_URL'] = 'http://127.0.0.1:18082'
source = P / 'labs/f33/requests.sh'
r = subprocess.run(['bash', str(source)], cwd=P, env=env, capture_output=True, text=True)
(OUT / 'stdout.log.gz').write_bytes(gzip.compress(r.stdout.encode(), mtime=0))
(OUT / 'stderr.log').write_text(r.stderr)
assert r.returncode == 0, r.stderr
rest, responses = r.stdout.strip(), []
decoder = json.JSONDecoder()
while rest:
    value, offset = decoder.raw_decode(rest)
    responses.append(value)
    rest = rest[offset:].lstrip()
(OUT / 'responses.json').write_text(json.dumps(responses, ensure_ascii=False, indent=2) + '\n')
reindexes = [x for x in responses if 'version_conflicts' in x]
assert [(x['total'], x['created'], x['updated']) for x in reindexes] == [(6, 6, 0), (6, 1, 5), (6, 6, 0)]
assert all(not x['failures'] and not x['timed_out'] for x in reindexes)
java = [x for x in responses if 'esRequest' in x]
assert [x['total'] for x in java] == [0, 0, 2, 0, 3]
assert [(c['id'], c['ticketPriceFen']) for c in java[-1]['items']] == [('p01', 6500), ('p07', 1500), ('p08', 2000)]
errors = [x for x in responses if 'error' in x]
assert all(x.get('status') in [400, 403, 404] for x in errors), errors
clients = [x for x in responses if 'ok' in x]
assert len(clients) == 4 and [x['ok'] for x in clients] == [True, True, False, True]
assert clients[-1]['response']['_index'] == 'tut-f33-attractions-v002'
aliases = json.load(urllib.request.urlopen('http://127.0.0.1:19733/_alias/tut-f33-attractions-read,tut-f33-attractions-write'))
assert aliases == {'tut-f33-attractions-v002': {'aliases': {'tut-f33-attractions-read': {'is_write_index': False}, 'tut-f33-attractions-write': {'is_write_index': True}}}}
rec = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'passed': True,
       'scope': 'Separate reader manual/curl path after the two formal lab.py rounds; not counted as a third formal run',
       'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'command': ['bash', 'labs/f33/requests.sh'],
       'exit_code': r.returncode, 'response_objects': len(responses), 'reindex_totals_created_updated': [[x['total'], x['created'], x['updated']] for x in reindexes],
       'java_result_counts': [x['total'] for x in java], 'expected_error_counts': dict(collections.Counter(x.get('status') for x in errors)),
       'official_java_client_writes': len(clients), 'final_aliases': aliases}
(OUT / 'summary.json').write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
print('Separate F33 manual curl path passed')
