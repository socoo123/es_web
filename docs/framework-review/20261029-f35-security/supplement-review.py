#!/usr/bin/env python3
import functools,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
class H(http.server.SimpleHTTPRequestHandler):
 def do_GET(self):
  if not self.path.startswith('/es_web/'):self.send_error(404);return
  self.path=self.path[len('/es_web'):];super().do_GET()
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)+'/es_web/'
rec={'checks':[]}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'),headless=True)
  for width in [1440,390,320]:
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':900});context.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
    page=context.new_page();page.goto(base+'framework/index.html');page.locator('a[data-ch="f35"]').click();assert page.url==base+'framework/f35.html'
    page.locator('.pager a').first.click();assert page.url==base+'framework/f34.html'
    page.locator('.pager a[href="f35.html"]').click();assert page.url==base+'framework/f35.html'
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    for i in range(2):
     with page.expect_popup() as popup:page.locator('[data-expand-d2]').nth(i).click()
     tab=popup.value;tab.wait_for_load_state('networkidle');assert tab.url.endswith('-'+theme+'.svg');tab.close()
    rec['checks'].append({'width':width,'theme':theme,'index_f35_previous_next_clicks':True,'expand_both_diagrams':True});context.close()
  browser.close()
 rec['passed']=True
finally:
 server.shutdown();(D/'supplement-review.json').write_text(json.dumps(rec,indent=2)+'\n')
print('F35 final directory/previous-next/expand clicks passed')
