#!/usr/bin/env python3
"""Additional screenshots of the actual F29 Java excerpt and copyable code."""
import functools,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
B=str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell')
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start();rec=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=B,headless=True)
  for width in [1440,390]:
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':1000});context.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
    page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/framework/f29.html',wait_until='networkidle')
    for i in range(2):
     block=page.locator('pre[data-source$="RoutingLab.java"]').nth(i)
     path=D/'screenshots'/f'java-code-{width}-{theme}-{i}.png';block.screenshot(path=str(path))
     m=block.evaluate('e=>({width:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX})')
     assert m['overflow']=='auto';rec.append({'width':width,'theme':theme,'snippet':i,'screenshot':str(path.relative_to(R)),'measure':m})
    context.close()
  browser.close()
finally:server.shutdown()
(D/'code-screens.json').write_text(json.dumps({'passed':True,'screens':rec},indent=2)+'\n');print('8 actual Java code screenshots recorded')
