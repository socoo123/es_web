#!/usr/bin/env python3
"""Run only F13, with two fresh-index rounds and actual REST/Java comparisons."""
import contextlib
import datetime
import hashlib
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('f13lab', PROJECT / 'labs/f13/lab.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def extra():
    good = lab.load('search/f13/inputs/02-aligned.json')
    invalid = [{'q': ''}, {'q': '故' * 61}, {'cityCode': 'HZ'}, {'maxPriceFen': -1},
               {'maxPriceFen': 1.5}, {'mode': 'name.raw'}, {'mode': None}, {'q': '   '}]
    for patch in invalid:
        result = lab.call('POST', '/api/attractions/analysis-search', good | patch, expected=400, app=True)
        assert result['code'] == 'INVALID_ANALYSIS_INPUT'
    result = lab.call('POST', '/api/attractions/analysis-search', good | {'maxPriceFen': 0}, app=True)
    assert result['items'] == [] and result['total'] == 0
    error = lab.call('POST', '/_analyze', {'analyzer': 'travel_text', 'text': '故宫'}, expected=400)
    assert error['error']['type'] == 'illegal_argument_exception'
    error = lab.call('POST', '/' + lab.INDEX + '/_analyze', {'analyzer': 'no_such_analyzer', 'text': '故宫'}, expected=400)
    assert error['error']['type'] == 'illegal_argument_exception'
    mapping = lab.call('GET', '/' + lab.INDEX + '/_mapping')[lab.INDEX]['mappings']
    assert mapping['properties']['name']['fields']['mismatch']['search_analyzer'] == 'keyword'
    # The Java process stays running while this named resource is deleted and rebuilt.
    lab.call('DELETE', '/' + lab.INDEX)
    error = lab.call('POST', '/api/attractions/analysis-search', good, expected=502, app=True)
    assert error['code'] == 'SEARCH_BACKEND_REJECTED'
    lab.prepare()
    result = lab.call('POST', '/api/attractions/analysis-search', good, app=True)
    assert [card['id'] for card in result['items']] == lab.FOUR


def run():
    record = {'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'F13 only; real ES9.4.0 single node/one primary, Boot4/JDK25, no mock responses',
              'rounds': [], 'status': 'running', 'unverified': ['plugins', 'multi-node', 'random concurrent load',
                  'ranking quality evaluation', 'performance', 'TLS/auth', 'search timeout/partial shard failures']}
    try:
        # Explicit named cleanup before round one; never remove volumes or other lessons' resources.
        with (HERE / 'initial-cleanup.jsonl').open('w') as output, contextlib.redirect_stdout(output):
            lab.cleanup()
        for number in [1, 2]:
            lab.CALLS.clear()
            with (HERE / f'round-{number}.jsonl').open('w') as output, contextlib.redirect_stdout(output):
                start = len(lab.CALLS)
                lab.prepare(); lab.chain(); lab.recall(); lab.java()
                teaching = len(lab.CALLS) - start
                assert teaching == 58
                extra()
                lab.cleanup()
            record['rounds'].append({'round': number, 'status': 'passed', 'teaching_http_requests': teaching,
                'additional_http_requests': len(lab.CALLS) - teaching, 'total_http_requests': len(lab.CALLS),
                'corpus_count': 8, 'query_counts': [0, 4, 3, 0, 1, 2, 0, 4, 0, 0, 1],
                'java_cases': 7, 'comparisons': 'Both analysis token/position/offset streams and actual Java search DSL replayed in REST; all IDs/order/price/score/sort/total/relation equal',
                'errors_and_recovery': '8 invalid inputs400, budget0 empty, custom analyzer without index400, unknown analyzer400, missing index502, recreate with same Java process200, named delete then GET404'})
            print(f'F13 round {number}: passed, {len(lab.CALLS)} actual HTTP requests', flush=True)
        record['status'] = 'passed'
    except Exception as error:
        record['status'] = 'failed'
        record['error'] = repr(error)
        raise
    finally:
        record['sha256'] = {str(p.relative_to(PROJECT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for pattern in ['data/f13/*', 'search/f13/**/*.json', 'labs/f13/*',
                            'backend/src/main/java/dev/esweb/travel/Analysis*.java']
            for p in PROJECT.glob(pattern) if p.is_file()}
        record['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (HERE / 'execution.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    run()
