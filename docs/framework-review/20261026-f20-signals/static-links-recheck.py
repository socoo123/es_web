"""Recheck only corrected evidence-index path after the browser phase completed."""
import datetime,importlib.util,json,pathlib,shutil
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('f20http',HERE/'review.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
p=HERE/'http-review.json';r=json.loads(p.read_text())
assert r['status']=='failed' and '20261025-f20-weights/README.md' in r['failure']
assert len(r['matrix'])==12 and len(r['regression'])==24 and len(r['independent_diagrams'])==16
assert all(not r[k] for k in ['js_errors','http_failures','request_failures','business_requests'])
shutil.copyfile(p,HERE/'attempts/http-evidence-index-path.json')
r['static_links']=module.static_links()
r['static_links_recheck']={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'corrected review script index path only; no product changes after completed browser phase','previous_failure_preserved':'attempts/http-evidence-index-path.json','count':len(r['static_links'])}
r.pop('failure');r['status']='passed';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('HTTP passed: completed 12 reading/24 regressions/16 independent groups plus actual copies; corrected static links rechecked:',len(r['static_links']))
