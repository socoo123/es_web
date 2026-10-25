#!/usr/bin/env python3
"""Targeted error screenshots and final static tables; no repeated full matrix."""
import contextlib
import datetime
import functools
import hashlib
import http.server
import importlib.util
import json
import pathlib
import subprocess
import threading
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Targeted error message visibility and source/ID tables after broad checks','operations':[],'screenshots':[],'status':'running'}
spec=importlib.util.spec_from_file_location('shellcheck',HERE/'shell-review.py')
# shell-review has a top-level executable workflow, so import only the lab helper instead.
spec=importlib.util.spec_from_file_location('f16lab',P/'labs/f16/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
def shot(page,name,selector):
 path=HERE/'screenshots'/(name+'.png');page.locator(selector).screenshot(path=str(path))
 record['screenshots'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_review':'pending'})
def search(page,q,status):
 page.locator('[name=q]').fill(q)
 with page.expect_response(lambda r:r.url.endswith('/api/attractions/synonym-search')) as info:page.locator('#submit').click()
 r=info.value;value=r.json();assert r.status==status,value
 page.wait_for_function("!document.getElementById('submit').disabled")
 record['operations'].append({'request':json.loads(r.request.post_data),'status':r.status,'response':value})
 if status!=200:assert str(status) in page.locator('#status').inner_text() and page.locator('.card,.token').count()==0
 else:assert [v['id'] for v in value['items']]==['bj-palace','bj-wall']
def command(args):
 r=subprocess.run(args,cwd=P,capture_output=True,text=True);assert r.returncode==0,r.stderr
 record.setdefault('transitions',[]).append({'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
with sync_playwright() as pw:
 browser=pw.chromium.launch();page=browser.new_page(viewport={'width':390,'height':1000})
 page.goto('http://127.0.0.1:18080/f16.html',wait_until='networkidle');page.locator('[name=q]').evaluate("el=>el.removeAttribute('maxlength')")
 search(page,'x'*61,400);shot(page,'shell-390-invalid-error-detail','.results');search(page,'紫禁城',200)
 with (HERE/'visual-detail-es.jsonl').open('w') as f,contextlib.redirect_stdout(f):lab.call('DELETE','/'+lab.INDEX)
 search(page,'紫禁城',502);shot(page,'shell-390-missing-index-error-detail','.results')
 with (HERE/'visual-detail-es.jsonl').open('a') as f,contextlib.redirect_stdout(f):
  lab.call('PUT','/'+lab.INDEX,lab.load('index'))
  health=lab.call('GET','/_cluster/health/'+lab.INDEX+'?wait_for_status=green&timeout=30s');assert not health['timed_out'] and health['status']=='green'
  b=lab.call('POST','/'+lab.INDEX+'/_bulk',(P/'data/f16/attractions.ndjson').read_text(),ndjson=True);assert not b['errors']
  lab.call('POST','/'+lab.INDEX+'/_update/bj-palace',lab.load('alias-update'));lab.refresh()
 search(page,'紫禁城',200)
 command(['docker','compose','-f','infra/f16/compose.yaml','stop','es'])
 search(page,'紫禁城',503);shot(page,'shell-390-unavailable-error-detail','.results')
 command(['docker','compose','-f','infra/f16/compose.yaml','up','-d','es']);command(['bash','infra/f16/wait.sh']);search(page,'紫禁城',200)
 handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  for width,theme in [(1440,'dark'),(390,'light')]:
   page.set_viewport_size({'width':width,'height':1000})
   page.goto(f'http://127.0.0.1:{server.server_port}/framework/f16.html',wait_until='networkidle')
   if page.evaluate('document.documentElement.dataset.theme')!=theme:page.locator('.theme-toggle').click()
   page.wait_for_timeout(400)  # Capture settled theme colors, not the CSS transition.
   page.locator('.topbar').evaluate("el=>el.style.visibility='hidden'")
   for id in ['samples-table','cn-matrix','en-matrix','graph-tokens']:shot(page,f'f16-{width}-{theme}-{id}','#'+id)
 finally:server.shutdown();server.server_close()
 browser.close()
record['status']='passed';(HERE/'visual-detail.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F16 targeted error/table screenshots passed; six actual Java API calls')
