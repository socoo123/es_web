"""Focused confirmation of permitted local table/SVG scrolling; no ES requests."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
import threading,json,hashlib
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 context=browser.new_context(reduced_motion='reduce');page=context.new_page()
 for width in [390,320]:
  page.set_viewport_size({'width':width,'height':844});page.goto('http://127.0.0.1:'+str(server.server_port)+'/chapters/ch17.html')
  for theme in ['light','dark']:
   if page.locator('html').get_attribute('data-theme')!=theme:page.locator('.theme-toggle').click()
   for selector in ['.fp-stage','#source-map + table']:
    row=page.locator(selector).evaluate('''e=>{e.scrollLeft=e.scrollWidth;return {selector:e.className,clientWidth:e.clientWidth,scrollWidth:e.scrollWidth,scrollLeft:e.scrollLeft,overflowX:getComputedStyle(e).overflowX,pageWidth:document.documentElement.scrollWidth,viewport:innerWidth};}''')
    assert row['scrollWidth']>row['clientWidth'] and row['scrollLeft']>0 and row['overflowX']=='auto' and row['pageWidth']<=width,row
    rows.append({'width':width,'theme':theme,**row})
   request=page.locator('[data-exp="ch17-03-bulk30"] .exp-req')
   measured=request.evaluate('e=>{e.scrollTop=e.scrollHeight;return {clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,scrollTop:e.scrollTop,overflowY:getComputedStyle(e).overflowY,pageWidth:document.documentElement.scrollWidth};}')
   assert measured['clientHeight']<=340 and measured['scrollHeight']>measured['clientHeight'] and measured['scrollTop']>0 and measured['pageWidth']<=width,measured
   rows.append({'width':width,'theme':theme,'bulkRequest':measured})
   if width==390:
    request.evaluate('e=>e.scrollTop=0');page.locator('[data-exp="ch17-03-bulk30"]').screenshot(path=str(out/('ch17-bulk-mobile-'+theme+'.png')))
 browser.close()
server.shutdown()
report={'status':'pass','kind':'focused-local-scroll-review','chapterSha256':hashlib.sha256((root/'chapters/ch17.html').read_bytes()).hexdigest(),'experimentSha256':hashlib.sha256((root/'experiments/ch17.js').read_bytes()).hexdigest(),'rows':rows,'realEsApi':'separate-ch17-es-review.json'}
(out/'ch17-scroll-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS: local SVG and source-table scrolling at 390/320px in both themes; whole page remains contained.')
