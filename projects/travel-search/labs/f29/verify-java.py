#!/usr/bin/env python3
"""Run the bounded Java lab and independently replay its three search requests."""
import argparse
import datetime
import importlib.util
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('f29lab', HERE / 'lab.py')
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
p = argparse.ArgumentParser(description=__doc__); p.add_argument('--out', required=True)
args = p.parse_args(); lab.OUT = pathlib.Path(args.out).resolve(); lab.OUT.mkdir(parents=True, exist_ok=False)
passed = False
try:
    result = subprocess.run(['bash', str(HERE / 'java.sh')], cwd=lab.P, text=True, capture_output=True)
    (lab.OUT / 'java.stdout').write_text(result.stdout)
    (lab.OUT / 'java.stderr').write_text(result.stderr)
    lab.check(result.returncode == 0, result.stderr)
    java = json.loads(result.stdout)
    lab.check(java['passed'] and java['sdk_calls'] == 13 and len(java['events']) == 13, java)
    lab.check(java['dsl'] == lab.load('search/f29/search.json'), 'Java DSL differs from the teaching REST body')
    searches = [e for e in java['events'] if e['method'] == 'POST' and '/_search?' in e['path']]
    lab.check(len(searches) == 3, searches)
    for e in searches:
        live = lab.req(e['path'], 'POST', e['request'], kind='verification')
        expected = e['response']
        lab.check(live['hits']['total'] == expected['hits']['total'] and live['_shards'] == expected['_shards'], [live, expected])
        for a, b in zip(live['hits']['hits'], expected['hits']['hits']):
            lab.check(a['_id'] == b['_id'] and a['_source'] == b['_source']
                      and a['_routing'] == b['_routing'] and abs(a['_score'] - b['_score']) < 1e-6, [a, b])
        lab.check(len(live['hits']['hits']) == len(expected['hits']['hits']), [live, expected])
    lab.req('/' + lab.C + '/_refresh', 'POST', kind='verification')
    live = lab.req('/' + lab.C + '/_search', 'POST', {'size': 20, 'track_total_hits': True,
                   'query': {'match_all': {}}, 'sort': [{'attraction_id': 'asc'}]}, kind='verification')
    fixtures = lab.load('data/f29/routed.json')
    lab.check(live['hits']['total'] == {'value': 6, 'relation': 'eq'} and len(live['hits']['hits']) == 6
              and not live['timed_out'] and live['_shards']['failed'] == 0, live)
    for h, d in zip(live['hits']['hits'], fixtures):
        lab.check(h['_source'] == d['source'] and h['_routing'] == d['routing'], h)
    lab.save('java-proof.json', java)
    passed = True
finally:
    lab.save('summary.json', {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'passed': passed,
             'sdk_calls': 13 if passed else None, 'verification_http': len(lab.EVENTS),
             'note': 'SDK invocations counted; underlying transport attempts/retries were not captured'})
print('F29 official Java client: 13 SDK calls and 5 independent verification HTTP passed')
