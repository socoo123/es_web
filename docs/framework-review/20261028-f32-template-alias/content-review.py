#!/usr/bin/env python3
"""Author's F32 content/evidence cross-check; not an independent reviewer."""
import collections
import datetime
import hashlib
import html
import json
import pathlib
import re

D = pathlib.Path(__file__).resolve().parent
R = D.parents[2]
P = R / 'projects/travel-search'
PAGE = R / 'framework/f32.html'


def load(path):
    return json.loads(path.read_text())


def main():
    page = PAGE.read_text()
    snippets = []
    for m in re.finditer(r'<pre\b([^>]*data-source="([^"]+)"[^>]*)><code>([\s\S]*?)</code></pre>', page):
        lines = (R / m[2]).read_text().rstrip().split('\n')
        selected = re.search(r'data-lines="(\d+)-(\d+)"', m[1])
        if selected:
            lines = lines[int(selected[1]) - 1:int(selected[2])]
        assert html.unescape(m[3]) == '\n'.join(lines), m[2]
        snippets.append({'file': m[2], 'range': selected[0] if selected else 'full', 'equal': True})
    rounds = []
    for name in ['round-1', 'round-2']:
        path = P / 'review/f32' / name
        summary = load(path / 'summary.json')
        events = [json.loads(line) for line in (path / 'events.jsonl').read_text().splitlines()]
        counts = collections.Counter(e['case'] for e in events if e['kind'] == 'teaching')
        assert summary['passed'] and summary['teaching_http_by_case'] == dict(counts)
        assert summary['teaching_http_total'] == sum(counts.values()) == 85
        java = [e for e in events if e['kind'] == 'java-client']
        api = [e for e in events if e['kind'] == 'java-api']
        assert len(java) == len(api) == 6
        assert [e['status'] for e in api] == [200, 200, 200, 502, 200, 200]
        assert [e['response'].get('status') for e in java if not e['response']['ok']] == [404, 404, 400, 400]
        assert [e['response']['response']['_index'] for e in java if e['response']['ok']] == [
            'tut-f32-attractions-v001', 'tut-f32-attractions-v002']
        inherited = load(path / 'actual-inheritance.json')
        assert [inherited['tut-f32-attractions-v00' + str(i)]['settings']['index.number_of_shards'] for i in range(1, 5)] == ['1', '2', '2', '3']
        assert [inherited['tut-f32-attractions-v00' + str(i)]['settings']['index.refresh_interval'] for i in range(1, 5)] == ['-1', '-1', '1s', '-1']
        assert load(path / 'error-two-writers.json')['status'] == 500
        assert load(path / 'write-alias-searches-both.json')['hits']['total']['value'] == 4
        assert load(path / '05-wrong-empty-target-java.json')['total'] == 0
        assert [(i['id'], i['ticketPriceFen']) for i in load(path / '06-target-repaired-java.json')['items']] == [('p01', 6500), ('p02', 0)]
        rounds.append({'round': name, 'passed': True, 'rest_by_case': dict(counts), 'java_api': len(api), 'java_writes': len(java)})
    reading = load(D / 'http-review.json')
    assert reading['passed'] and len(reading['copies']) == 28
    browser = [load(p) for p in sorted((P / 'review/f32/round-1').glob('*-browser.json'))]
    assert len(browser) == 6 and all(b['passed'] and not b['direct_es'] for b in browser)
    assert sum(len(b['calls']) for b in browser) == 24
    assert sum('rest_replay' in c for b in browser for c in b['calls']) == 20
    prose = re.sub(r'<[^>]+>', '', re.sub(r'<pre.*?</pre>', '', page, flags=re.S))
    record = {
        'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'reviewer': 'author self-review; no independent agent or independent review claimed',
        'model_reasoning_limit': 'reasoning.json records unavailable runtime setting/readback',
        'scope': 'F32 only; necessary F31 next link, curriculum and progress summaries',
        'chinese_prose_characters_without_pre': len(re.findall(r'[\u4e00-\u9fff]', prose)),
        'author_content_findings': [
            'Explains travel search failure before terms/API; templates govern creation, aliases govern target resolution.',
            'Priority and version, winner selection versus component merge, explicit creation settings and compatible mappings distinguished.',
            'Both snapshots independently loaded; no reindex, continuous updates or F33 migration completeness claimed.',
            'Actual old/new settings and mappings checked; simulate does not create, old indices do not subscribe to later components.',
            'Alias search uses all targets; business IDs repeat; is_write_index selects only writes, and single-target implicit writer is demonstrated.',
            'Read alias explicitly false, naming and require_alias are not authorization; F35 remains future work.',
            '404 for missing/concrete require_alias targets, 400 for no writer, 500 for two writers match real 9.4.0 evidence and exercises.',
            'Java uses stable config and same process; DSL body alone does not prove URI target, original _index and alias metadata are needed.',
            'Shell proves duplicate cards, 502 clearing, valid empty response and repaired 65/0 prices; full source and physical target evidence separately retained.',
            '8 folded checks/4 traps/2 static D2/no player; no frontend code or new controller; point-named repeat/cleanup and limits stated.'
        ],
        'prior_author_failures': 'attempts/README.md; failures not counted as formal rounds or published-lesson errata',
        'published_f32_errata': 0,
        'snippets': snippets,
        'rounds': rounds,
        'sha256': {str(p.relative_to(R)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [PAGE, P/'labs/f32/lab.py', P/'labs/f32/java/AliasWriter.java']},
        'passed': True
    }
    (D / 'content-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print('F32 author content/evidence/snippet review passed')


if __name__ == '__main__':
    main()
