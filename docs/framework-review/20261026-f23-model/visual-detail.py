#!/usr/bin/env python3
"""Final tutorial amendment and native screenshot details after overview review."""
import datetime,functools,hashlib,http.server,importlib.util,json,pathlib,threading
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('reading',HERE/'review.py');review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(review.Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'Final paragraph makes local table/code scrolling discoverable; explicitly distinguish client serialization from HTTP raw bytes. Recheck affected layout at all standard widths and capture horizontal ends at native scale.','matrix':[],'screenshots':[],'horizontal_ends':[]}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=review.BROWSER)
  for width in review.WIDTHS:
   for theme in review.THEMES:
    c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')");page=c.new_page();page.goto(base+'framework/f23.html',wait_until='networkidle');review.diagrams(page,theme)
    record['matrix'].append({'width':width,'theme':theme,'layout':review.measure(page)})
    if width==390:
     for table in ['samples','models','counts']:
      loc=page.locator('#'+table+'-table');ends=loc.evaluate('e=>{e.scrollLeft=e.scrollWidth;return {left:e.scrollLeft,max:e.scrollWidth-e.clientWidth}}');review.require(ends['left']>0 and abs(ends['left']-ends['max'])<=1,ends);record['horizontal_ends'].append({'table':table,'theme':theme,**ends});record['screenshots'].append(review.shot(page,f'final-detail-390-{theme}-{table}-right','#'+table+'-table'))
     pre=page.locator('pre[data-source$="ModelSearchService.java"]');body=pre.locator('code').text_content().splitlines()
     for label,fragment in [('query','public SearchRequest request'),('projection','public Result inspect')]:
      line=next(i for i,x in enumerate(body) if fragment in x)
      for side in ['left','right']:
       pre.evaluate('(e,args)=>{e.scrollLeft=args.side==="right"?e.scrollWidth:0;const r=e.getBoundingClientRect();window.scrollTo(0,scrollY+r.top+args.line*parseFloat(getComputedStyle(e).lineHeight)-130)}',{'side':side,'line':line})
       page.wait_for_timeout(250);record['screenshots'].append(review.shot(page,f'final-detail-390-{theme}-java-{label}-{side}'))
    if width==320:
     page.locator('.course-status').first.scroll_into_view_if_needed();page.wait_for_timeout(250);record['screenshots'].append(review.shot(page,f'final-detail-320-{theme}-scroll-hint'))
    c.close()
  browser.close()
 record['status']='passed';record['sha256']={'framework/f23.html':review.sha(ROOT/'framework/f23.html')}
finally:
 server.shutdown();server.server_close();(HERE/'visual-detail.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Final paragraph/layout amendment passed: 12 groups /',len(record['screenshots']),'detail screenshots')
