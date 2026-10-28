#!/usr/bin/env python3
"""Targeted final reading check after adding the actual two-round results."""
import datetime,functools,hashlib,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
B=str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell');rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'views':[],'errors':[],'http_errors':[]}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=B,headless=True)
  for width in [1440,320]:
   for theme in ['light','dark']:
    c=browser.new_context(viewport={'width':width,'height':900});c.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
    page=c.new_page();page.on('pageerror',lambda e:rec['errors'].append(str(e)));page.on('response',lambda r:rec['http_errors'].append([r.url,r.status]) if r.status>=400 else None)
    page.goto(f'http://127.0.0.1:{server.server_port}/framework/f29.html',wait_until='networkidle')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert page.locator('body').inner_text().find('0组p04/p05，1组p01/p02/p03/p06')>=0
    page.locator('#default').scroll_into_view_if_needed();path=D/'screenshots'/f'final-{width}-{theme}-default.png';page.screenshot(path=str(path))
    rec['views'].append({'width':width,'theme':theme,'screenshot':str(path.relative_to(R)),'column':page.locator('article.chapter').bounding_box()['width'],'actual_two_round_ids_present':True})
    c.close()
  browser.close()
finally:server.shutdown()
assert not rec['errors'] and not rec['http_errors'];rec['passed']=True;rec['final_html_sha256']=hashlib.sha256((R/'framework/f29.html').read_bytes()).hexdigest();(D/'final-smoke.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('Final actual-result prose: 4 targeted reading views passed')
