#!/usr/bin/env python3
"""Author self-review of F33 evidence. No independent-agent claim."""
import collections, datetime, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[3]
D = pathlib.Path(__file__).resolve().parent
P = ROOT / 'projects/travel-search'
REC = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'reviewer': 'author self-review', 'independent': False, 'lesson': 'F33', 'checks': []}
def check(name, value, detail):
    assert value, (name, detail)
    REC['checks'].append({'name': name, 'passed': True, 'detail': detail})
for n in ['01', '02']:
    out = P / ('review/f33/run-' + n)
    s = json.loads((out / 'summary.json').read_text())
    events = [json.loads(x) for x in (out / 'events.jsonl').read_text().splitlines()]
    check('round-' + n, s['passed'] and s['teaching_http_total'] == 75
          and s['official_java_client_writes'] == 4 and s['http_by_kind']['java-api'] == 5,
          '75 teaching REST + 5 Java API + 4 client writes; guard/identity/cleanup/wait separate')
    for key, values in {'reindex-initial': (6, 0), 'reindex-nonempty-ghost': (1, 5),
                        'reindex-frozen-clean': (6, 0)}.items():
        r = json.loads((out / (key + '.json')).read_text())
        check(n + '-' + key, (r['created'], r['updated']) == values and not r['failures']
              and not r['version_conflicts'] and not r['timed_out'], 'Real synchronous response')
    failures = [e for e in events if e['kind'] == 'teaching' and e['status'] >= 400]
    check(n + '-expected-errors', collections.Counter(x['status'] for x in failures)
          == {400: 1, 403: 2, 404: 8}, 'Mapping 400; source-block writes 403; missing docs and wrong alias precondition 404')
    layout = json.loads((out / 'final-layout.json').read_text())
    check(n + '-layout', len(layout) == 6 and all(x['state'] == 'STARTED' for x in layout),
          '1P+1R old and 2P+2R target; real two-data-node reads in events')
    java = [json.loads((out / (stage + '-java.json')).read_text()) for stage in
            ['01-before-switch-old-recall', '02-frozen-source-still-serves', '03-switched-to-new',
             '04-rollback-old-recall', '05-new-writes-break-simple-rollback']]
    check(n + '-java-results', [x['total'] for x in java] == [0, 0, 2, 0, 3],
          'Unchanged process/index configuration; IDs/prices/fields asserted by lab and replay')
html = (ROOT / 'framework/f33.html').read_text()
plain = re.sub(r'<pre\b.*?</pre>|<script\b.*?</script>|<style\b.*?</style>', '', html, flags=re.S)
plain = re.sub('<[^>]+>', '', plain)
REC['chinese_characters_excluding_code'] = len(re.findall('[\u4e00-\u9fff]', plain))
REC['code_blocks'] = html.count('class="code-block"')
check('teaching-structure', all(f'class="{c}"' in html for c in
      ['goal', 'lesson', 'drills', 'pitfalls', 'recap', 'ch-footer']),
      'Business problem → concepts/causes → input/implementation → result/counterexample → capability → F34/F41')
check('exercise-traps', html.count('<details>') >= 11 and html.count('class="callout warn"') == 4,
      '8 folded capability checks, source/prerequisites folded, 4 actual traps')
check('sources', all(x['local_official_equal'] for x in json.loads((D / 'sources.json').read_text())['files']),
      '4 targeted files; official v9.4.0 byte equality, separate from actual API')
check('diagram-generation', all(x['exit_code'] == 0 for x in
      json.loads((ROOT / 'framework/diagrams/f33/generation.json').read_text())['checks']),
      '2 sources and 4 SVG exports, official D2; no manual asset edit')
REC['content_read_through'] = ['Field type and historical terms; fixed view vs backup Snapshot; immutable initial copy; '
    'equal-count differences; no delete propagation; block then refresh; discard only unserved target; complete IDs/source; '
    '4-action switch/must_exist; actual alias target; paused rollback restores old recall; p08 ends simple rollback window; '
    'stable Java process; operational REST scope; F34 backup and F41 continuous-data boundary.']
REC['validation_script_correction'] = 'Initial post-run summary assertion undercounted missing-document 404s (7 vs actual 8); inspected all endpoints and corrected. Both original ES runs passed unchanged. This was not an ES/API failure.'
REC['published_old_lesson_errata'] = []
REC['passed'] = True
(D / 'content-review.json').write_text(json.dumps(REC, ensure_ascii=False, indent=2) + '\n')
print('F33 author content/evidence cross-check passed')
