#!/usr/bin/env python3
"""Author integration verification, F15 only; complete dictionary transitions twice."""
import copy
import datetime
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import traceback
import time

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
ROOT = PROJECT.parents[1]
spec = importlib.util.spec_from_file_location('f15lab', PROJECT / 'labs/f15/lab.py')
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
record = {'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'scope': 'F15 local IK dictionary only; no remote reload or online migration',
          'rounds': [], 'transitions': [], 'status': 'running'}

def save(): (HERE / 'execution.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
def command(args):
    r = subprocess.run(args, cwd=PROJECT, text=True, capture_output=True)
    record['transitions'].append({'command': args, 'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}); save()
    assert r.returncode == 0, args

def switch(choice):
    command(['python3', 'infra/f15/select-dictionary.py', choice])
    command(['docker', 'compose', '-f', 'infra/f15/compose.yaml', 'restart', 'es'])
    command(['bash', 'infra/f15/wait.sh'])

def java_ready():
    # A restarted node needs cluster recovery and a usable Java transport. Record any 503, then
    # retry this read-only diagnostic explicitly; do not silently count it as success.
    for attempt in range(6):
        result = lab.call('POST', '/api/attractions/dictionary-search',
                          {'q': '星澜湾', 'cityCode': 'NJ', 'maxPriceFen': 10000, 'view': 'original'},
                          expected=(200, 503), app=True)
        if lab.CALLS[-1]['status'] == 200:
            return
        time.sleep(0.5)
    raise AssertionError('Java did not reconnect after node restart')

def extra():
    valid = {'q': '星澜湾', 'cityCode': 'NJ', 'maxPriceFen': 10000, 'view': 'rebuilt'}
    for patch in [{'q': ''}, {'q': '  '}, {'q': '星' * 61}, {'cityCode': 'BJ'}, {'view': 'tut-f15-v1'},
                  {'view': None}, {'maxPriceFen': -1}, {'maxPriceFen': 100000001}, {'maxPriceFen': 1.5}, {'q': None}]:
        lab.call('POST', '/api/attractions/dictionary-search', {**valid, **patch}, expected=400, app=True)
    for view, wanted in [('original', ['nj-new']), ('rebuilt', ['nj-bay', 'nj-new'])]:
        result = lab.call('POST', '/api/attractions/dictionary-search', {**valid, 'view': view, 'maxPriceFen': 0}, app=True)
        assert [i['id'] for i in result['items']] == wanted
        empty = lab.call('POST', '/api/attractions/dictionary-search', {**valid, 'view': view, 'q': '！！！'}, app=True)
        assert empty['total'] == 0 and empty['queryTokens'] == []
    # Both indexes contain exactly the same eleven original business documents.
    all_sources = {}
    for index in [lab.OLD, lab.NEW]:
        result = lab.call('POST', '/' + index + '/_search', {'size': 20, 'query': {'match_all': {}}, 'sort': [{'attraction_id': 'asc'}]})
        assert len(lab.ids(result)) == 11
        all_sources[index] = {h['_id']: h['_source'] for h in result['hits']['hits']}
    expected = {d['attraction_id']: d for filename in ['attractions', 'new-documents'] for d in lab.load('data/f15/' + filename + '.json')}
    assert all_sources[lab.OLD] == all_sources[lab.NEW] == expected
    # A simple term probe confirms stored evidence agrees with actual searchable postings.
    for index, wanted in [(lab.OLD, ['nj-new']), (lab.NEW, ['nj-bay', 'nj-boundary', 'nj-new'])]:
        body = copy.deepcopy(lab.load('search/f15/bay.json'))
        body['query']['bool']['must'] = [{'term': {'name': '星澜湾'}}]
        assert lab.ids(lab.call('POST', '/' + index + '/_search', body)) == wanted
    lab.call('POST', '/' + lab.OLD + '/_refresh')
    assert lab.searches('mixed', lab.OLD) == lab.RESULTS['mixed']['queries']
    lab.call('POST', '/' + lab.OLD + '/_analyze', {'analyzer': 'missing_f15', 'text': '星澜湾'}, expected=400)
    lab.call('PUT', '/' + lab.OLD, lab.load('search/f15/index.json'), expected=400)
    lab.call('PUT', '/' + lab.OLD + '/_doc/blocked-probe', expected['nj-bay'], expected=403)
    assert lab.call('GET', '/' + lab.OLD + '/_count')['count'] == 11
    # Existing-target create conflicts are visible; the target is not silently overwritten.
    duplicate = lab.call('POST', '/_reindex', lab.load('search/f15/reindex.json'), expected=409)
    assert duplicate['version_conflicts'] > 0 and duplicate['failures'] and duplicate['created'] == 0
    assert lab.call('GET', '/' + lab.NEW + '/_count')['count'] == 11
    lab.call('DELETE', '/' + lab.NEW)
    lab.call('POST', '/api/attractions/dictionary-search', valid, expected=502, app=True)
    assert lab.call('POST', '/api/attractions/dictionary-search', {**valid, 'view': 'original'}, app=True)['total'] == 1
    lab.rebuild()
    assert lab.call('POST', '/api/attractions/dictionary-search', valid, app=True)['total'] == 3

try:
    lab.cleanup()
    (HERE / 'initial-cleanup.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in lab.CALLS))
    first = None
    for number in [1, 2]:
        lab.CALLS.clear(); lab.RESULTS.clear(); phases = {}; teaching = []
        def main(name, operation):
            start = len(lab.CALLS); operation()
            rows = lab.CALLS[start:]; phases[name] = len(rows); teaching.extend(rows)
        try:
            switch('empty')
            main('baseline', lab.baseline)
            java_ready(); lab.java(('original',), 'baseline')
            main('file-only', lambda: (command(['python3', 'infra/f15/select-dictionary.py', 'travel']), lab.file_only()))
            command(['docker', 'compose', '-f', 'infra/f15/compose.yaml', 'restart', 'es'])
            command(['bash', 'infra/f15/wait.sh'])
            java_ready(); lab.java(('original',), 'loaded')
            main('loaded-new', lab.loaded_new)
            assert lab.RESULTS['baseline']['stored'] == lab.RESULTS['loaded']['stored'], 'restart did not rewrite old terms'
            main('rebuild', lab.rebuild)
            main('java-rest', lab.java)
            assert phases == {'baseline': 23, 'file-only': 4, 'loaded-new': 21, 'rebuild': 20, 'java-rest': 16}, phases
            summary = copy.deepcopy(lab.RESULTS)
            if first is None: first = summary
            else: assert summary == first, 'full two-round terms, offsets, IDs and judgments agree'
            (HERE / f'round-{number}-teaching.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in teaching))
            extra()
            lab.cleanup()
            lab.call('POST', '/api/attractions/dictionary-search', {'q': '星澜湾', 'cityCode': 'NJ', 'maxPriceFen': 10000, 'view': 'original'}, expected=502, app=True)
            record['rounds'].append({'round': number, 'status': 'passed', 'phases': phases, 'teaching_calls': len(teaching),
                                    'all_client_calls': len(lab.CALLS), 'additional_calls': len(lab.CALLS) - len(teaching), 'summary': summary})
        finally:
            (HERE / f'round-{number}.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in lab.CALLS)); save()
    record['status'] = 'passed'
    record['sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for pattern in ['projects/travel-search/data/f15/*', 'projects/travel-search/search/f15/*', 'projects/travel-search/labs/f15/*',
                        'projects/travel-search/infra/f15/*', 'projects/travel-search/infra/f15/dictionaries/*',
                        'projects/travel-search/backend/src/main/java/dev/esweb/travel/Dictionary*.java']
        for p in ROOT.glob(pattern) if p.is_file()}
except Exception:
    record['status'] = 'failed'; record['failure'] = traceback.format_exc(); raise
finally:
    save()
print('F15 two full dictionary/rebuild ES/Java rounds passed')
