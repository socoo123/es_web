#!/usr/bin/env python3
import datetime,functools,http.server,importlib.util,json,pathlib,threading
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];S=D/'screenshots'
spec=importlib.util.spec_from_file_location('reading',D/'reading-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(m.Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)+'/es_web/'
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'screenshots':[],'image_checks':[],
     'anchor_checks':[], 'capture_note':'Only full-figure screenshots temporarily hide fixed topbar to avoid screenshot stitching overlay; anchor geometry checked on unmodified page.'}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=m.BROWSER,headless=True)
  for theme in ['light','dark']:
   context=browser.new_context(viewport={'width':1440,'height':1000})
   context.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
   page=context.new_page();page.goto(base+'framework/f32.html',wait_until='networkidle');m.images(page,theme)
   for slug in ['template-inheritance','alias-targets']:
    fig=page.locator('#fig-'+slug);file=S/f'final-full-{slug}-{theme}.png';fig.screenshot(path=str(file),style='.topbar{visibility:hidden!important}');rec['screenshots'].append(str(file.relative_to(R)))
    rec['image_checks'].append(page.locator('#fig-'+slug+' img').evaluate('e=>({width:e.getBoundingClientRect().width,naturalWidth:e.naturalWidth,currentSrc:e.currentSrc})'))
   for width in [1440,390]:
    page.set_viewport_size({'width':width,'height':1000})
    for slug in ['template-inheritance','alias-targets']:
     page.locator('.diagram-jumps a[href="#fig-'+slug+'"]').click()
     page.wait_for_function('''id=>{let r=document.getElementById(id).getBoundingClientRect(),n=document.querySelector('.topbar').getBoundingClientRect();return r.top>=n.bottom&&r.top<180}''',arg='fig-'+slug)
     rec['anchor_checks'].append({'width':width,'theme':theme,'id':'fig-'+slug,'figure_top_below_topbar':True})
    el=page.locator('pre[data-source$="AttractionSearchService.java"]')
    for side in ['left','right']:
     el.evaluate('''(e,side)=>{e.scrollLeft=side==='left'?0:e.scrollWidth-e.clientWidth}''',side)
     file=S/f'final-java-{width}-{theme}-{side}.png';el.screenshot(path=str(file));rec['screenshots'].append(str(file.relative_to(R)))
   context.close()
  browser.close()
finally:
 server.shutdown();(D/'extra-screenshots.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print('4 complete final figures + 8 Java-code views captured')
