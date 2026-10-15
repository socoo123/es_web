#!/usr/bin/env python3
"""执行 F04 的原样 shell/数据；保留实际响应，并验证两轮业务结果。"""
import datetime
import hashlib
import json
import pathlib
import platform
import subprocess
import urllib.request
import urllib.error

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
ROOT = PROJECT.parents[1]
BASE = 'http://127.0.0.1:19200'
RESOURCES = ['tut-f04-' + x for x in ['attractions', 'boundaries', 'dynamic', 'rebuilt']]


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=35) as r:
        return json.load(r)


def shell(args):
    r = subprocess.run(args, cwd=PROJECT, capture_output=True, text=True, timeout=240)
    if r.returncode:
        raise RuntimeError(f'{args}: exit {r.returncode}\n{r.stdout}\n{r.stderr}')
    return r


def objects(raw):
    result = []
    decoder = json.JSONDecoder()
    while raw.strip():
        raw = raw.lstrip()
        obj, end = decoder.raw_decode(raw)
        result.append(obj)
        raw = raw[end:]
    return result


def step(name, n):
    r = shell(['bash', f'labs/f04/{name}.sh'])
    (HERE / f'raw/round-{n}-{name}.json').write_text(json.dumps({
        'stdout': r.stdout, 'stderr': r.stderr, 'exit': r.returncode}, ensure_ascii=False, indent=2) + '\n')
    return objects(r.stdout)


def count_ok(body, count):
    assert body['count'] == count and body['_shards']['failed'] == 0, body


def bulk_items(body):
    return [x['index'] for x in body['items']]


def excerpt(items):
    return [{'id': x['_id'], 'status': x['status'], **({'error': x['error']['type']} if 'error' in x else {'result': x['result']})} for x in items]


def run():
    # 不自动 up/stop：作者先按本课入口启动，以便保留已有服务状态。
    info = get('/')
    assert info['version']['number'] == '9.4.0' and info['cluster_name'] == 'travel-search-lab'
    current = {x['index'] for x in get('/_cat/indices?format=json&h=index')}
    assert not current.intersection(RESOURCES), '本课索引已存在；确认可删除后手工点名 cleanup'
    (HERE / 'raw').mkdir(exist_ok=True)
    (HERE / 'outputs').mkdir(exist_ok=True)
    docs = json.loads((PROJECT / 'data/f04/attractions.json').read_text())
    expected = {x['attraction_id']: x for x in docs}
    rounds = []
    for n in [1, 2]:
        print(f'F04 round {n}', flush=True)
        info, created, health, mapping = step('01-create', n)
        assert created['acknowledged'] and created['shards_acknowledged']
        assert health['status'] == 'green' and not health['timed_out']
        assert health['number_of_nodes'] == 1
        props = mapping[RESOURCES[0]]['mappings']['properties']
        assert mapping[RESOURCES[0]]['mappings']['dynamic'] == 'strict'
        assert props['ticket_price_fen'] == {'type': 'integer', 'coerce': False}
        assert props['name']['fields']['raw']['type'] == 'keyword'
        mixed, refresh, count = step('02-mixed', n)
        mi = bulk_items(mixed)
        assert mixed['errors'] and [x['status'] for x in mi] == [201, 400, 201, 201, 400], mi
        assert mi[1]['error']['type'] == 'document_parsing_exception'
        assert mi[4]['error']['type'] == 'strict_dynamic_mapping_exception'
        assert refresh['_shards']['failed'] == 0
        count_ok(count, 3)
        retry, refresh2, search = step('03-retry', n)
        assert not retry['errors'] and [x['status'] for x in bulk_items(retry)] == [201, 201]
        assert refresh2['_shards']['failed'] == 0
        assert not search['timed_out'] and search['_shards']['failed'] == 0
        assert search['hits']['total'] == {'value': 5, 'relation': 'eq'}
        assert [x['_id'] for x in search['hits']['hits']] == sorted(expected)
        for hit in search['hits']['hits']:
            assert hit['_source'] == expected[hit['_id']]
            assert hit['fields']['name.raw'] == [hit['_source']['name']]
            assert 'name.raw' not in hit['_source']
            assert hit['fields']['published_on'] == ['2026-10-01']
        repeated, refresh3, count2, doc = step('04-reimport', n)
        assert not repeated['errors']
        assert all(x['result'] == 'updated' and x['_version'] == 2 for x in bulk_items(repeated))
        assert refresh3['_shards']['failed'] == 0
        count_ok(count2, 5)
        assert doc['_source'] == expected['a-hz-xihu'] and doc['_version'] == 2
        bc, boundaries, br, bcount, bsearch = step('05-boundaries', n)
        bi = bulk_items(boundaries)
        assert bc['acknowledged'] and boundaries['errors']
        assert [x['status'] for x in bi] == [400]*4 + [201]*4, bi
        assert br['_shards']['failed'] == 0
        count_ok(bcount, 4)
        assert not bsearch['timed_out'] and bsearch['_shards']['failed'] == 0
        assert bsearch['hits']['total'] == {'value': 4, 'relation': 'eq'}
        bd = {x['_id']: x['_source'] for x in bsearch['hits']['hits']}
        assert bd['business-invalid']['ticket_price_fen'] == -100 and bd['business-invalid']['status'] == 'mystery'
        assert 'ticket_price_fen' not in bd['missing'] and bd['null']['ticket_price_fen'] is None
        assert bd['zero']['ticket_price_fen'] == 0
        dc, dw, dm, change, rc, rw, rr, rcount, rm = step('06-dynamic', n)
        dp = dm[RESOURCES[2]]['mappings']['properties']
        assert dc['acknowledged'] and dw['result'] == 'created'
        assert dp['city_code']['type'] == dp['ticket_price_fen']['type'] == 'text'
        assert change['status'] == 400 and change['error']['type'] == 'illegal_argument_exception'
        assert rc['acknowledged'] and rw['result'] == 'created' and rr['_shards']['failed'] == 0
        count_ok(rcount, 1)
        assert rm[RESOURCES[3]]['mappings']['properties']['ticket_price_fen']['type'] == 'integer'
        assert get('/tut-f04-rebuilt/_doc/a-hz-tea')['_source'] == expected['a-hz-tea']
        cleaned, = step('cleanup', n)
        assert cleaned['acknowledged']
        assert not {x['index'] for x in get('/_cat/indices?format=json&h=index')}.intersection(RESOURCES)
        rounds.append({'round': n, 'cases': {f'f04-c0{i}': 'passed' for i in [1, 2, 3]},
                       'mapping': mapping, 'mixed': mixed, 'count_after_mixed': count,
                       'retry': retry, 'search': search, 'reimport': repeated, 'count_after_reimport': count2,
                       'boundaries': boundaries, 'boundary_search': bsearch, 'dynamic_mapping': dm,
                       'type_change': change, 'rebuilt_mapping': rm, 'rebuilt_count': rcount,
                       'cleanup': cleaned})
        if n == 1:
            for name, value in {'mixed': {'errors': mixed['errors'], 'items': excerpt(mi), 'count_after_refresh': 3},
                                'retry': {'errors': retry['errors'], 'items': excerpt(bulk_items(retry)), 'count_after_refresh': 5},
                                'reimport': {'errors': repeated['errors'], 'items': excerpt(bulk_items(repeated)), 'count_after_refresh': 5},
                                'boundaries': {'errors': boundaries['errors'], 'items': excerpt(bi)},
                                'search': search, 'type-change': change,
                                'dynamic-mapping': dm}.items():
                (HERE / f'outputs/{name}.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    inputs = [p for folder in ['data/f04', 'search/f04', 'labs/f04'] for p in (PROJECT / folder).iterdir() if p.is_file()]
    record = {'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'environment': {'platform': platform.platform(), 'python': platform.python_version(), 'es': info,
                              'docker': shell(['docker', 'version', '--format', '{{.Server.Version}}']).stdout.strip(),
                              'image': shell(['docker', 'image', 'inspect', 'docker.elastic.co/elasticsearch/elasticsearch:9.4.0', '--format', '{{.Id}}']).stdout.strip()},
              'rounds': rounds, 'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              'final': 'all four F04 indices absent; shared single-node left running by verifier',
              'scope': 'actual shell scripts; 28 teaching HTTP requests/round plus named cleanup; probes/assertion reads counted separately',
              'status': 'passed'}
    (HERE / 'es-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print('F04: 3 cases × 2 rounds passed; named cleanup passed')


if __name__ == '__main__':
    run()
