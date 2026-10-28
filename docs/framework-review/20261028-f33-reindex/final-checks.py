#!/usr/bin/env python3
"""Final repository, syntax and evidence checks for this lesson only."""
import datetime, hashlib, json, pathlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[3]
D = pathlib.Path(__file__).resolve().parent
P = ROOT / 'projects/travel-search'
checks = []
def command(args):
    p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    checks.append({'command': args, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    assert p.returncode == 0, checks[-1]
command(['node', 'tools/check.mjs'])
command(['node', 'tools/sync-framework-code.mjs', '--check'])
command(['python3', str((D / 'content-review.py').relative_to(ROOT))])
syntax = []
for folder in [D, P / 'labs/f33']:
    for path in sorted(folder.rglob('*.py')):
        compile(path.read_text(), str(path), 'exec')
        syntax.append(str(path.relative_to(ROOT)))
for path in sorted((P / 'labs/f33').rglob('*.sh')):
    command(['bash', '-n', str(path.relative_to(ROOT))])
command(['git', 'diff', '--check'])
command(['git', 'diff', '--cached', '--check'])
for name in ['http-review.json', 'supplement-review.json', 'visual-review.json', 'content-review.json']:
    assert json.loads((D / name).read_text())['passed'], name
for name in ['setup', 'run-01', 'run-02', 'manual', 'cleanup', 'down']:
    assert json.loads((P / 'review/f33' / name / 'summary.json').read_text())['passed'], name
assert json.loads((P / 'review/f33/final-state.json').read_text())['passed']
assert json.loads((P / 'review/f33/runtime.json').read_text())['passed']
generation = json.loads((ROOT / 'framework/diagrams/f33/generation.json').read_text())
for name, digest in generation['sha256'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True).splitlines()
allowed_files = ['STATUS.md', 'PLAN.md', 'FRAMEWORK_PLAN.md', 'FRAMEWORK_STANDARD.md',
                 'docs/framework-lesson-prompt.md', 'framework/f32.html', 'framework/f33.html', 'framework/index.html']
allowed_prefixes = ['docs/framework-review/20261028-f33-reindex/', 'framework/diagrams/f33/',
                    'projects/travel-search/data/f33/', 'projects/travel-search/infra/f33/',
                    'projects/travel-search/labs/f33/', 'projects/travel-search/review/f33/',
                    'projects/travel-search/search/f33/']
assert staged and all(x in allowed_files or any(x.startswith(prefix) for prefix in allowed_prefixes) for x in staged)
rec = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'passed': True, 'commands': checks,
       'python_syntax_files': syntax, 'diagram_hashes_equal': True, 'staged_scope_files': staged,
       'scope': 'F33 plus necessary progress/directory/F32 next-link only; shared backend/frontend unchanged',
       'build': 'Actual Maven package/classpath/tree and client execution recorded separately; no test source, no test-pass claim',
       'checks_record_note': 'This JSON and regenerated author review are staged after execution; final cached diff check is repeated before commit.'}
(D / 'checks.json').write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
print('F33 final repository/syntax/evidence checks passed')
