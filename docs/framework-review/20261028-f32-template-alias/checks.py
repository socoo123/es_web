#!/usr/bin/env python3
"""Only F32 checks plus the required repository gate. No live ES rerun."""
import ast
import datetime
import json
import pathlib
import subprocess

D = pathlib.Path(__file__).resolve().parent
R = D.parents[2]
checks = []
commands = [
    ['node', 'tools/check.mjs'],
    ['node', 'tools/sync-framework-code.mjs', '--check'],
    ['python3', str((D / 'content-review.py').relative_to(R))],
    ['bash', '-n', 'projects/travel-search/labs/f32/java.sh'],
    ['git', 'diff', '--check'],
    ['git', 'diff', '--check', 'HEAD^'],
    ['git', 'diff', '--cached', '--check']
]
for command in commands:
    p = subprocess.run(command, cwd=R, capture_output=True, text=True)
    checks.append({'command': command, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    assert p.returncode == 0, checks[-1]
roots = [D] + [R / 'projects/travel-search' / name / 'f32' for name in ['labs', 'data', 'search', 'review']]
roots.append(R / 'framework/diagrams/f32')
files = []
for root in roots:
    for file in sorted(root.rglob('*')):
        if file.suffix == '.py':
            ast.parse(file.read_text(), filename=str(file))
        elif file.suffix == '.json':
            json.loads(file.read_text())
        elif file.suffix in ['.ndjson', '.jsonl']:
            raw = file.read_text()
            assert not raw or raw.endswith('\n'), file
            for line in raw.splitlines():
                json.loads(line)
        else:
            continue
        files.append(str(file.relative_to(R)))
for name in ['runtime.json', 'cleanup/summary.json', 'down/summary.json']:
    assert json.loads((R / 'projects/travel-search/review/f32' / name).read_text())['passed']
rec = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks': checks,
       'python_json_ndjson_jsonl_syntax_files': files,
       'execution_scope': 'F32 author checks; required repository gate/snippet consistency only. Live ES/Java/HTTP/visual records separate.',
       'passed': True}
(D / 'checks.json').write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')
print('F32 site/snippets/evidence/syntax checks passed')
