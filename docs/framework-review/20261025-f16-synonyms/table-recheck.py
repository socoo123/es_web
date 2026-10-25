#!/usr/bin/env python3
"""Recapture only eight static tables with theme set before loading; no ES/Java calls."""
import datetime,functools,hashlib,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
record=json.loads((HERE/'visual-detail.json').read_text())
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch()
  for width,theme in [(1440,'dark'),(390,'light')]:
   context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
   context.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')")
   page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/framework/f16.html',wait_until='networkidle')
   assert page.evaluate('document.documentElement.dataset.theme')==theme
   page.locator('.topbar').evaluate("el=>el.style.visibility='hidden'")
   for id in ['samples-table','cn-matrix','en-matrix','graph-tokens']:
    path=HERE/'screenshots'/f'f16-{width}-{theme}-{id}.png';page.locator('#'+id).screenshot(path=str(path))
    r=next(s for s in record['screenshots'] if s['path']==str(path.relative_to(ROOT)))
    r['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
   context.close()
  browser.close()
finally:server.shutdown();server.server_close()
record['table_recapture']={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script':'table-recheck.py','reason':'first dark table captured during CSS transition; set theme before load; eight static tables only; earlier six Java calls retained'}
(HERE/'visual-detail.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F16 settled table captures passed')
