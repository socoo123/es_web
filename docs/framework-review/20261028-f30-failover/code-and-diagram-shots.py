#!/usr/bin/env python3
import importlib.util,json,pathlib,functools,http.server,threading
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
spec=importlib.util.spec_from_file_location('reading',D/'reading-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(m.Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
shots=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=m.BROWSER,headless=True)
  for width in [1440,390]:
   for theme in ['light','dark']:
    c=b.new_context(viewport={'width':width,'height':1000});c.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
    page=c.new_page();page.goto(base+'framework/f30.html',wait_until='networkidle');m.images(page,theme)
    block=page.locator('pre[data-source$="AttractionSearchService.java"]');block.evaluate('e=>scrollTo({top:e.getBoundingClientRect().top+scrollY-110,behavior:"instant"})');page.wait_for_timeout(100)
    name=f'java-request-{width}-{theme}.png';page.screenshot(path=str(D/'screenshots'/name));shots.append(name)
    block.evaluate('e=>e.scrollLeft=e.scrollWidth-e.clientWidth');page.evaluate('scrollBy({top:620,behavior:"instant"})');page.wait_for_timeout(100)
    name=f'java-search-{width}-{theme}.png';page.screenshot(path=str(D/'screenshots'/name));shots.append(name)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    c.close()
  c=b.new_context(viewport={'width':1440,'height':1200});page=c.new_page()
  for theme in ['light','dark']:
   for slug in ['two-decisions','shard-recovery']:
    page.goto(base+f'framework/diagrams/f30/{slug}-{theme}.svg',wait_until='networkidle')
    name=f'whole-{slug}-{theme}.png';page.locator('svg').first.screenshot(path=str(D/'screenshots'/name));shots.append(name)
  c.close();b.close()
finally:
 server.shutdown();(D/'extra-screenshots.json').write_text(json.dumps({'screenshots':shots,'scope':'Actual code request/search at desktop/mobile in both themes; whole generated SVGs captured for visual reading'},indent=2)+'\n')
print('Extra screenshots captured:',len(shots))
