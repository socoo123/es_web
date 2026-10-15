#!/usr/bin/env python3
"""运行原样 F06 脚本，两轮核对业务结果；失败也保留实际记录。"""
import datetime
import hashlib
import json
import pathlib
import platform
import subprocess
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
ROOT = PROJECT.parents[1]
BASE = 'http://127.0.0.1:19200'
INDEX = 'tut-f06-attractions'
GROUPS = {
    '02-hard': ['all', 'keyword', 'city', 'budget', 'open', 'near'],
    '03-boundaries': ['strict-upper', 'free', 'missing-price', 'not-offline'],
    '04-should': ['should-optional', 'should-required', 'should-only',
                  'should-filter-default', 'should-filter-required', 'filter-only'],
}


def require(condition, evidence):
    if not condition:
        raise AssertionError(evidence)


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=35) as response:
        return json.load(response)


def exists():
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + '/' + INDEX, method='HEAD'), timeout=10):
            return True
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return False
        raise


def objects(raw):
    result = []
    decoder = json.JSONDecoder()
    while raw.strip():
        raw = raw.lstrip()
        obj, end = decoder.raw_decode(raw)
        result.append(obj)
        raw = raw[end:]
    return result


def step(name, number):
    args = ['bash', f'labs/f06/{name}.sh']
    result = subprocess.run(args, cwd=PROJECT, capture_output=True, text=True, timeout=240)
    path = HERE / f'raw/round-{number}-{name}.json'
    path.write_text(json.dumps({'command': args, 'exit': result.returncode,
                               'stdout': result.stdout, 'stderr': result.stderr},
                              ensure_ascii=False, indent=2) + '\n')
    require(result.returncode == 0, {'script': name, 'exit': result.returncode, 'raw': str(path.relative_to(ROOT))})
    return objects(result.stdout)


def search_ok(body, name, expected, documents):
    wanted = expected['queries'][name]['ids']
    require(body['timed_out'] is False and body['_shards']['failed'] == 0, body)
    require(body['hits']['total'] == {'value': len(wanted), 'relation': 'eq'}, {'query': name, 'body': body})
    hits = body['hits']['hits']
    require([hit['_id'] for hit in hits] == wanted, {'query': name, 'wanted': wanted, 'body': body})
    fields = json.loads((PROJECT / f'search/f06/{name}.json').read_text())['_source']
    for hit in hits:
        require(hit['_index'] == INDEX and hit['sort'] == [hit['_id']], hit)
        source = {field: documents[hit['_id']][field] for field in fields if field in documents[hit['_id']]}
        assertion = expected['queries'][name].get('score_assertion')
        if assertion == 'zero': require(hit['_score'] == 0.0, hit)
        if assertion == 'positive': require(isinstance(hit['_score'], (int, float)) and hit['_score'] > 0, hit)
        require(hit['_source'] == source, {'query': name, 'expected_source': source, 'hit': hit})
    return {'ids': wanted, 'total': body['hits']['total'], 'timed_out': body['timed_out'],
            'failed_shards': body['_shards']['failed'], 'sources_checked': True, 'score_assertion': expected['queries'][name].get('score_assertion'), 'actual_scores': {hit['_id']: hit['_score'] for hit in hits}}


def run():
    (HERE / 'raw').mkdir(exist_ok=True)
    inputs = [p for folder in ['data/f06', 'search/f06', 'labs/f06']
              for p in (PROJECT / folder).iterdir() if p.is_file()]
    record = {
        'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'F06 actual scripts: 22 teaching HTTP requests/round; cleanup 1; author preflight/assertion reads separate',
        'status': 'running', 'stage': 'preflight', 'rounds': [],
        'environment': {'platform': platform.platform(), 'python': platform.python_version(), 'endpoint': BASE},
        'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'final': 'not checked',
    }
    try:
        info = get('/')
        require(info['version']['number'] == '9.4.0' and info['cluster_name'] == 'travel-search-lab', info)
        record['environment']['es'] = info
        require(not exists(), 'F06 索引已存在；先确认资料可删，再手工点名 cleanup，验收不自动删除初始资源')
        for args in [['docker', 'version', '--format', '{{.Server.Version}}'],
                     ['docker', 'image', 'inspect', 'docker.elastic.co/elasticsearch/elasticsearch:9.4.0', '--format', '{{.Id}}']]:
            result = subprocess.run(args, cwd=PROJECT, capture_output=True, text=True, timeout=15)
            record['environment'].setdefault('docker_observations', []).append(
                {'command': args, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        expected = json.loads((PROJECT / 'search/f06/expected.json').read_text())
        documents = {d['attraction_id']: d for d in json.loads((PROJECT / 'data/f06/attractions.json').read_text())}
        contract = json.loads((PROJECT / 'search/f06/index.json').read_text())
        for number in [1, 2]:
            print(f'F06 round {number}', flush=True)
            record['stage'] = f'round-{number}-prepare'
            version, created, health, mapping, bulk, refreshed = step('01-prepare', number)
            require(version['version']['number'] == '9.4.0' and version['cluster_name'] == 'travel-search-lab', version)
            require(created['acknowledged'] and created['shards_acknowledged'], created)
            require(health['status'] == 'green' and not health['timed_out'] and health['number_of_nodes'] == 1, health)
            require(mapping[INDEX]['mappings'] == contract['mappings'], mapping)
            items = [item['index'] for item in bulk['items']]
            require(bulk['errors'] is False and [item['_id'] for item in items] == list(documents), bulk)
            require(all(item['status'] == 201 and item['result'] == 'created' and item['_version'] == 1 for item in items), bulk)
            require(refreshed['_shards']['failed'] == 0, refreshed)
            current = {'round': number, 'queries': {}, 'cases': {},
                       'prepare': {'version': version, 'created': created, 'health': health, 'mapping': mapping,
                                   'bulk': bulk, 'refresh': refreshed}}
            for script, names in GROUPS.items():
                record['stage'] = f'round-{number}-{script}'
                responses = step(script, number)
                require(len(responses) == len(names), {'script': script, 'responses': len(responses)})
                for name, response in zip(names, responses):
                    current['queries'][name] = search_ok(response, name, expected, documents)
            current['cases'] = {f'f06-c0{i}': 'passed' for i in [1, 2, 3]}
            record['stage'] = f'round-{number}-cleanup'
            cleaned, = step('cleanup', number)
            require(cleaned['acknowledged'] and not exists(), cleaned)
            current['cleanup'] = cleaned
            record['rounds'].append(current)
        record['status'] = 'passed'
        record['stage'] = 'completed'
        record['final'] = 'tut-f06-attractions absent; dedicated shared node left running; volume retained'
        print('F06: 3 cases × 2 rounds passed; named cleanup passed')
    except Exception as error:
        record['status'] = 'blocked_before_http' if record['stage'] == 'preflight' and isinstance(error, urllib.error.URLError) else 'failed'
        record['failure'] = {'type': type(error).__name__, 'message': str(error)}
        record['final'] = 'failure preserved; no automatic failure cleanup; inspect before rerun'
        raise
    finally:
        (HERE / 'es-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    run()
