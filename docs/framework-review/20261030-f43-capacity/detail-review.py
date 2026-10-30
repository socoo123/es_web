#!/usr/bin/env python3
"""Final result-table and complete diagram captures over prefixed local HTTP."""
import functools,http.server,json,pathlib,threading,datetime
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];SHOTS=D/'screenshots'
BROWSER=str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell')
class Handler(http.server.SimpleHTTPRequestHandler):
 def do_GET(self):
  if not self.path.startswith('/es_web/'):self.send_error(404);return
  self.path=self.path[len('/es_web'):];super().do_GET()
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'screenshots':[],'errors':[],'tables':[]}
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=BROWSER,headless=True)
  for width in [1440,390,320]:
   for theme in ['light','dark']:
    ctx=b.new_context(viewport={'width':width,'height':900});ctx.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
    page=ctx.new_page();page.on('pageerror',lambda e:rec['errors'].append(str(e)))
    page.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f43.html',wait_until='networkidle')
    for id in ['bulk-results','mixed-results','resource-results','drills']:
     locator=page.locator('#'+id);locator.scroll_into_view_if_needed()
     if id!='drills':
      state=locator.evaluate("e=>({overflow:getComputedStyle(e).overflowX,width:e.clientWidth,scroll:e.scrollWidth,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})")
      if state["scroll"]>state["width"]+1:assert state["overflow"] in ["auto","scroll"],state
      assert state["right"]<=page.locator("article.chapter").bounding_box()["x"]+page.locator("article.chapter").bounding_box()["width"]+1,state
      if width<=390:
       left=locator.evaluate('e=>{e.scrollLeft=0;return {width:e.clientWidth,scroll:e.scrollWidth}}');assert left['scroll']>left['width']
       path=SHOTS/f'results-{width}-{theme}-{id}-left.png';page.screenshot(path=str(path));rec['screenshots'].append(str(path.relative_to(ROOT)))
       locator.evaluate('e=>e.scrollLeft=e.scrollWidth-e.clientWidth')
     else:page.locator('#drills details').last.evaluate('e=>e.open=true')
     path=SHOTS/f'results-{width}-{theme}-{id}.png';page.screenshot(path=str(path));rec['screenshots'].append(str(path.relative_to(ROOT)))
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    rec['tables'].append({'width':width,'theme':theme,'passed':True});ctx.close()
  for theme in ['light','dark']:
   page=b.new_page(viewport={'width':1440,'height':1000})
   for slug in ['measurement','compare']:
    page.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/diagrams/f43/{slug}-{theme}.svg',wait_until='networkidle')
    path=SHOTS/f'whole-{slug}-{theme}.png';page.locator('svg').first.screenshot(path=str(path));rec['screenshots'].append(str(path.relative_to(ROOT)))
   page.close()
  b.close()
 assert not rec['errors'];rec['passed']=True
finally:
 server.shutdown();(D/'detail-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print('Final result tables and full diagrams captured and checked')
