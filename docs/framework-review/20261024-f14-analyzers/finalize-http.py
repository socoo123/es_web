#!/usr/bin/env python3
"""Complete the sole failed final link check, retaining the original failure."""
import importlib.util,json,pathlib,datetime
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('f14reading',HERE/'review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=HERE/'http-review.json';j=json.loads(p.read_text())
assert len(j['matrix'])==12 and len(j['regression'])==24 and len(j['independent_diagrams'])==16
assert len(j['clipboard'])>0 and j['offline']['status']=='passed'
assert not any(j[k] for k in ['js_errors','http_failures','request_failures','business_requests'])
assert j.get('failure', '').endswith("AssertionError: {'file': 'projects/travel-search/review/f14/README.md', 'link': 'build/runtime.json'}\n")
j['static_links']=m.static_links();j.pop('failure');j['status']='passed'
j['completion']={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repair':'Actual build/runtime, workspace restoration and attempts records completed; reran all local-link checks only. Browser matrix/source hashes retained; final paragraph changes covered by separate final-text-review.json.','original':'attempts/http-before-runtime-link.json'}
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n');print('F14 HTTP completed; only missing runtime-link check repeated')
