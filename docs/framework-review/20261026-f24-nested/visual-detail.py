#!/usr/bin/env python3
"""Targeted actual browser detail captures and geometry after contact-sheet review."""
import functools,http.server,json,pathlib,threading,hashlib
from playwright.sync_api import sync_playwright
import reading_helpers as h
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(h.Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
rec={'checks':[],'screenshots':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=h.BROWSER)
 for width,theme in [(320,'light'),(390,'dark'),(1440,'light'),(1440,'dark')]:
  c=b.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')");p=c.new_page();p.goto(base+'framework/f24.html',wait_until='networkidle');h.diagrams(p,theme)
  for slug in ['same-entry','price-scope']:
   figure=p.locator('#fig-'+slug);figure.scroll_into_view_if_needed();p.wait_for_timeout(150)
   m=figure.evaluate('''e=>{const r=e.getBoundingClientRect(),c=e.querySelector('figcaption'),q=c.getBoundingClientRect();return {figure:{top:r.top,bottom:r.bottom,height:r.height},caption:{top:q.top,bottom:q.bottom,height:q.height,scroll:c.scrollHeight,client:c.clientHeight,overflow:getComputedStyle(c).overflow},text:c.textContent};}''');rec['checks'].append({'width':width,'theme':theme,'slug':slug,'geometry':m});assert m['caption']['bottom']<=m['figure']['bottom']+1,m
   for target,suffix in [(figure,'figure'),(figure.locator('figcaption'),'caption')]:
    name=f'detail-{width}-{theme}-{slug}-{suffix}.png';path=HERE/'screenshots'/name;p.locator('.topbar').evaluate("e=>e.style.visibility='hidden'");target.screenshot(path=str(path));p.locator('.topbar').evaluate("e=>e.style.visibility=''");rec['screenshots'].append({'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_review':'pending'})
  # Actual horizontal scrolling to both table and code ends, with screenshots.
  for target,name in [('#samples-table','samples'),('#recap-table','recap'),('pre[data-source$="NestedSearchService.java"]','java')]:
   e=p.locator(target);e.evaluate('e=>e.scrollLeft=e.scrollWidth');m=e.evaluate('e=>({left:e.scrollLeft,client:e.clientWidth,scroll:e.scrollWidth})');rec['checks'].append({'width':width,'theme':theme,'target':name,'scrolled':m})
   if width==390:
    path=HERE/'screenshots'/f'detail-{width}-{theme}-{name}-right.png';e.screenshot(path=str(path));rec['screenshots'].append({'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_review':'pending'})
  c.close()
 b.close()
server.shutdown();rec['status']='passed';(HERE/'visual-detail.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('detail geometry and end-of-scroll captures passed',len(rec['screenshots']))
