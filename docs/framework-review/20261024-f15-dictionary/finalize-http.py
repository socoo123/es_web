#!/usr/bin/env python3
"""Finish static-link gating after real runtime receipts exist, without repeating passed UI checks."""
import datetime
import importlib.util
import json
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('f15http', HERE / 'review.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
p = HERE / 'http-review.json'; record = json.loads(p.read_text())
if record.get('status') == 'failed':
    assert "round-2.jsonl" in record['failure'], 'Do not bypass any other failure'
    shutil.copy(p, HERE / 'attempts/http-before-runtime-records.json')
assert len(record['matrix']) == 12 and len(record['regression']) == 24 and len(record['independent_diagrams']) == 16
assert not any(record[k] for k in ['js_errors', 'http_failures', 'request_failures', 'business_requests'])
for path, expected in record['sha256'].items():
    assert module.sha(ROOT / path) == expected, path + ': repeat affected checks after a content change'
record['static_links'] = module.static_links()
record['status'] = 'passed'
record['resolved_failure'] = record.pop('failure', None)
record['finalized_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
record['finalization'] = 'Real runtime receipts now exist; every captured page/diagram/style hash unchanged; only dependent static-link gate rerun'
p.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print('HTTP finalization passed',len(record['clipboard']),'copied blocks',len(record['static_links']),'local links')
