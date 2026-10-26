#!/usr/bin/env python3
"""Supplement screenshots for real tables, narrow code scroll and shell form."""
import datetime,functools,http.server,importlib.util,json,pathlib,threading
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2]
spec=importlib.util.spec_from_file_location('f22review',HERE/'review.py');review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(review.Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pending','scope':'table values from final ES results, actual narrow code scroll, no extra Java requests','screenshots':[],'measurements':[]}
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=review.BROWSER);p=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
  for width in [1440,390]:
   for theme in ['light','dark']:
    p.set_viewport_size({'width':width,'height':1000});p.goto(base+'framework/f22.html',wait_until='networkidle')
    if p.evaluate('document.documentElement.dataset.theme')!=theme:p.locator('.theme-toggle').click()
    review.diagrams(p,theme);p.wait_for_function("document.getAnimations().every(a=>a.playState!=='running')");p.evaluate("() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))");record['measurements'].append({'width':width,'theme':theme,'layout':review.measure(p)})
    for id in ['samples-table','ranking-table','holdout-table']:
     table=p.locator('#'+id);table.evaluate('e=>e.scrollLeft=0');record['screenshots'].append(review.shot(p,f'detail-{width}-{theme}-{id}-left','#'+id))
     if width==390 and table.evaluate('e=>e.scrollWidth>e.clientWidth+2'):
      table.evaluate('e=>e.scrollLeft=e.scrollWidth');review.require(table.evaluate('e=>e.scrollLeft>0'),'table moved')
      record['screenshots'].append(review.shot(p,f'detail-{width}-{theme}-{id}-right','#'+id))
    if width==390:
     pre=p.locator('pre[data-source$="QualityEvaluationService.java"]').first
     pre.evaluate("e=>{window.scrollTo({top:window.scrollY+e.getBoundingClientRect().top-160,behavior:'instant'});e.scrollTop=0;e.scrollLeft=0}");p.evaluate("() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))")
     record['screenshots'].append(review.shot(p,f'detail-{width}-{theme}-java-left'))
     pre.evaluate('e=>e.scrollLeft=e.scrollWidth');p.evaluate("() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))");review.require(pre.evaluate('e=>e.scrollLeft>0'),'long Java code scroll')
     record['screenshots'].append(review.shot(p,f'detail-{width}-{theme}-java-right'))
  # Updated local shell layout: no API called here; full matrix is shell-review.py.
  for width in [1440,390,320]:
   for theme in ['light','dark']:
    c=b.new_context(viewport={'width':width,'height':1000});c.add_init_script(f"localStorage.setItem('travel-f22:theme','{theme}')");s=c.new_page();s.goto('http://127.0.0.1:18081/f22.html',wait_until='networkidle')
    actual=s.locator('form').evaluate("e=>({columns:getComputedStyle(e).gridTemplateColumns,width:e.clientWidth,scroll:e.scrollWidth,options:[...e.querySelectorAll('select')].map(s=>({value:s.value,text:s.selectedOptions[0].textContent,width:s.clientWidth}))})")
    review.require(s.evaluate('document.documentElement.scrollWidth<=innerWidth'),'shell width')
    record['measurements'].append({'shell_width':width,'theme':theme,'form':actual})
    if width in [390,320]:record['screenshots'].append(review.shot(s,f'detail-shell-{width}-{theme}-form','form'))
    c.close()
  b.close();record['status']='passed'
finally:
 server.shutdown();server.server_close();(HERE/'visual-detail.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F22 detailed screenshots and real scroll checks passed:',len(record['screenshots']))
