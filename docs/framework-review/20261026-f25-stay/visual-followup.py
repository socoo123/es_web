#!/usr/bin/env python3
"""Resolve screenshot capture limits with larger viewport/scroll/error details."""
import datetime, functools, hashlib, http.server, importlib.util, json, pathlib, subprocess, sys, threading
from playwright.sync_api import sync_playwright
import reading_helpers as h
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2]
spec=importlib.util.spec_from_file_location('lab',R/'projects/travel-search/labs/f25/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'screenshots':[],'captions':[],'calls':[]}
def require(ok,msg):
 if not ok:raise AssertionError(msg)
def shot(page,name,selector):
 p=HERE/'screenshots'/(name+'.png');page.locator(selector).first.screenshot(path=str(p));rec['screenshots'].append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_review='pending'))
def submit(page,status):
 with page.expect_response(lambda r:r.url.endswith('/api/stay/inspect')) as info:page.locator('#submit').click()
 response=info.value;value=response.json();page.wait_for_function("!document.getElementById('submit').disabled");require(response.status==status,'actual status')
 require(page.locator('#status').inner_text() and (status==200 or page.locator('.card').count()==0),'visible cleared error')
 rec['calls'].append(dict(status=response.status,input=response.request.post_data_json,response=value));return value
def run():
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(h.Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=h.BROWSER)
   for theme in ['light','dark']:
    c=browser.new_context(viewport={'width':320,'height':1600},reduced_motion='reduce');c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')");p=c.new_page();p.goto(base+'framework/f25.html',wait_until='networkidle');h.diagrams(p,theme)
    p.locator('.topbar').evaluate("e=>e.style.visibility='hidden'")
    caption=p.locator('#fig-verify figcaption');require('图源与生成记录' in caption.inner_text(),'complete caption text')
    rec['captions'].append(dict(theme=theme,text=caption.inner_text(),box=caption.bounding_box(),style=caption.evaluate("e=>({height:e.clientHeight,scroll:e.scrollHeight,overflow:getComputedStyle(e).overflow})")))
    shot(p,'followup-320-'+theme+'-verify','#fig-verify');shot(p,'followup-320-'+theme+'-caption','#fig-verify figcaption');c.close()
   c=browser.new_context(viewport={'width':390,'height':1200});c.add_init_script("localStorage.setItem('es-web:theme','dark')");p=c.new_page();p.goto(base+'framework/f25.html',wait_until='networkidle');p.locator('.topbar').evaluate("e=>e.style.visibility='hidden'")
   for name,selector in [('table','#samples-table'),('java','pre[data-source$="StaySearchService.java"]')]:
    e=p.locator(selector).first;e.evaluate('e=>e.scrollLeft=e.scrollWidth');require(e.evaluate('e=>e.scrollLeft')>0,'right scroll possible');shot(p,'followup-390-dark-'+name+'-right',selector)
   c.close()
   c=browser.new_context(viewport={'width':390,'height':1000});p=c.new_page();p.goto('http://127.0.0.1:18081/f25.html',wait_until='networkidle')
   p.locator('input[name="checkIn"]').fill('2026-11-02');p.locator('input[name="checkOut"]').fill('2026-11-02');submit(p,400);shot(p,'followup-shell-400','.results')
   p.locator('#scenario').select_option('two-nights');submit(p,200)
   lab.LOG=HERE/'visual-followup-http.jsonl';require(not lab.LOG.exists(),'preserve prior logs')
   original=lab.read(lab.DATA/'summaries.json')[0];altered=dict(original);del altered['hotel_name']
   try:
    lab.request('PUT','/'+lab.INDEX+'/_doc/o01',altered);lab.request('POST','/'+lab.INDEX+'/_refresh');submit(p,502);shot(p,'followup-shell-502-incomplete','.results')
   finally:lab.request('PUT','/'+lab.INDEX+'/_doc/o01',original);lab.request('POST','/'+lab.INDEX+'/_refresh')
   submit(p,200);lab.request('DELETE','/'+lab.INDEX);submit(p,502);shot(p,'followup-shell-502-index','.results');lab.prepare();submit(p,200)
   compose=['docker','compose','-f',str(R/'projects/travel-search/infra/f25/compose.yaml')]
   try:
    subprocess.run(compose+['stop','es'],check=True,capture_output=True);submit(p,503);shot(p,'followup-shell-503','.results')
   finally:
    subprocess.run(compose+['start','es'],check=True,capture_output=True);subprocess.run(['bash',str(R/'projects/travel-search/infra/f25/wait.sh')],check=True,capture_output=True)
   submit(p,200);rec['additional_ES_HTTP']=lab.COUNT;c.close();browser.close()
  rec['status']='passed';rec['capture_note']='Some 320px element screenshots at viewport height1000 cut the last caption line; DOM complete, new height1600 and isolated caption show it. Original failure viewport screenshots showed form; new results-element screenshots show error text. Horizontal table/code screenshots intentionally show separate scroll positions.'
 finally:server.shutdown();(HERE/'visual-followup.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
run()
