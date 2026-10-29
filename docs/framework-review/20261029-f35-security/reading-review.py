#!/usr/bin/env python3
"""F35 actual HTTP/file reading checks. Not an ES/Java integration substitute."""
import importlib.metadata,sys
import datetime,functools,http.server,json,os,pathlib,threading
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];SHOTS=D/'screenshots'
BROWSER=os.environ.get('F35_BROWSER_EXECUTABLE',str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
REC={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'js_errors':[],'http_failures':[],'request_failures':[],'business_requests':[],'image_source_cancellations':[],'viewports':[],'screenshots':[]}
def check(ok,detail):
 if not ok:raise AssertionError(detail)
class Handler(http.server.SimpleHTTPRequestHandler):
 def do_GET(self):
  if not self.path.startswith('/es_web/'):self.send_error(404);return
  self.path=self.path[len('/es_web'):];super().do_GET()
 def log_message(self,*args):pass
def shot(page,name,locator=None):
 path=SHOTS/(name+'.png')
 if locator:page.locator(locator).screenshot(path=str(path))
 else:page.screenshot(path=str(path))
 REC['screenshots'].append(str(path.relative_to(ROOT)))
def observe(page):
 page.on('pageerror',lambda e:REC['js_errors'].append(str(e)))
 page.on('response',lambda r:REC['http_failures'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
 page.on('requestfailed',lambda r:(REC['image_source_cancellations'] if r.resource_type=='image' and '/framework/diagrams/' in r.url and r.url.endswith('.svg') and r.failure=='net::ERR_ABORTED' else REC['request_failures']).append({'url':r.url,'page':page.url,'failure':r.failure,'resource_type':r.resource_type}))
 page.on('request',lambda r:REC['business_requests'].append(r.url) if '/api/' in r.url or urlsplit(r.url).port in [19935,19936,18085] else None)
def images(page,theme):
 page.wait_for_function("""theme=>[...document.querySelectorAll('[data-d2-light]')].every(i=>i.complete&&i.naturalWidth>0&&i.currentSrc===new URL(theme==='dark'?i.dataset.d2Dark:i.dataset.d2Light,location.href).href&&i.closest('figure').querySelector('[data-expand-d2]').href===i.currentSrc)""",arg=theme)
def measure(page):
 r=page.evaluate("""()=>{const a=document.querySelector('article.chapter'),b=a.getBoundingClientRect();return{width:innerWidth,document:document.documentElement.scrollWidth,column:b.width,left:b.left,right:b.right,blocks:[...a.querySelectorAll(':scope > header,:scope > section,:scope > footer,.d2-figure,.lesson > pre.code-block')].map(e=>{let r=e.getBoundingClientRect();return{tag:e.tagName,id:e.id,left:r.left,right:r.right}})}}""")
 check(r['document']<=r['width'],r);check(r['column']<=880.1,r)
 for b in r['blocks']:check(abs(b['left']-r['left'])<=1 and abs(b['right']-r['right'])<=1,b)
 return r
def main():
 SHOTS.mkdir(exist_ok=True)
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)+'/es_web/'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path=BROWSER,headless=True)
   REC['tooling']={'python':sys.version,'executable':sys.executable,'playwright':importlib.metadata.version('playwright'),'browser':browser.version,'browser_executable':BROWSER}
   for width in [1920,1440,1024,768,390,320]:
    for theme in ['light','dark']:
     context=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,permissions=['clipboard-read','clipboard-write'])
     context.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
     page=context.new_page();observe(page);page.goto(base+'framework/f35.html',wait_until='networkidle');images(page,theme)
     check(page.locator('html').get_attribute('data-theme')==theme,theme)
     rec={'width':width,'theme':theme,'measure':measure(page)};REC['viewports'].append(rec)
     shot(page,f'f35-{width}-{theme}-opening')
     if width in [1440,320]:
      for id in ['problem','fig-three-checks','fig-boundaries','tls','permissions','java','rotation','recap']:
       page.locator('#'+id).scroll_into_view_if_needed();page.wait_for_timeout(80);shot(page,f'f35-{width}-{theme}-{id}')
     elif width in [390,768]:
      page.locator('#fig-three-checks').scroll_into_view_if_needed();shot(page,f'f35-{width}-{theme}-two-decisions')
     if width==320:
      rec['right_scroll']=[]
      for index,selector in enumerate(['.d2-view', '.ktable', 'pre.code-block']):
       el=page.locator(selector).first;el.scroll_into_view_if_needed()
       value=el.evaluate('e=>{e.scrollLeft=e.scrollWidth-e.clientWidth;return e.scrollLeft}')
       check(value>0,[selector,value]);rec['right_scroll'].append({'selector':selector,'scrollLeft':value})
       shot(page,f'f35-{width}-{theme}-right-{index}')
     # Local overflow must remain discoverable and confined.
     rec['local_scroll']=page.locator('pre.code-block, .ktable, .d2-view').evaluate_all("es=>es.filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>({tag:e.tagName,width:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX}))")
     check(all(x['overflow'] in ['auto','scroll'] for x in rec['local_scroll']),rec['local_scroll'])
     context.close()
   context=browser.new_context(viewport={'width':1440,'height':900},permissions=['clipboard-read','clipboard-write'])
   page=context.new_page();observe(page);page.goto(base+'framework/f35.html',wait_until='networkidle')
   # All snippets are copied via the real Clipboard API, including collapsed details.
   page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
   copies=[]
   for i in range(page.locator('pre.code-block').count()):
    code=page.locator('pre.code-block').nth(i);expected=code.locator('code').text_content()
    code.locator('xpath=preceding-sibling::*[1]').get_by_role('button',name='复制代码').click()
    actual=page.evaluate('navigator.clipboard.readText()');check(actual==expected,{'snippet':i});copies.append({'snippet':i,'characters':len(actual),'clipboard_equal':True})
   REC['copies']=copies
   anchors=page.locator('a[href^="#"]').evaluate_all('es=>es.map(e=>e.hash.slice(1))')
   for id in anchors:check(page.locator('[id="'+id+'"]').count()==1,id)
   REC['anchors']=anchors
   details=page.locator('details').count()
   page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=false)')
   for i in range(details):
    item=page.locator('details').nth(i);item.locator('summary').click();check(item.get_attribute('open') is not None,i)
    item.locator('summary').click();check(item.get_attribute('open') is None,i)
   REC['details_toggled']=details
   page.locator('.theme-toggle').click();images(page,'dark');page.reload(wait_until='networkidle');images(page,'dark')
   REC['theme_toggle_reload']='passed'
   page.locator('.read-toggle').click();read=page.evaluate("JSON.parse(localStorage.getItem('es-web:read'))");check(read=={'f35':True},read)
   page.goto(base+'framework/index.html');check('is-read' in page.locator('a[data-ch="f35"]').get_attribute('class'),'directory progress')
   page.goto(base+'framework/f34.html',wait_until='networkidle');images(page,'dark');check(not page.locator('.read-toggle').evaluate("e=>e.classList.contains('is-on')"),'f34 progress changed')
   page.goto(base+'framework/f35.html',wait_until='networkidle');images(page,'dark');page.locator('.read-toggle').click();check(page.evaluate("JSON.parse(localStorage.getItem('es-web:read'))")=={},'cancel read')
   REC['progress']='f35 set/directory reflected/f34 isolated/f35 canceled'
   # Same-origin local links are requested directly; external sources/local Java are excluded.
   links=page.locator('a[href]').evaluate_all('es=>[...new Set(es.map(e=>e.href))]')
   checked=[]
   for url in links:
    if url.startswith(base) and '#' not in url:
     response=context.request.get(url);check(response.status==200,[url,response.status]);checked.append(url.removeprefix(base))
   REC['local_links_200']=checked
   for width in [1440,1600,1920,2048]:
    for theme in ['light','dark']:
     for slug in ['three-checks','privilege-boundaries']:
      page.set_viewport_size({'width':width,'height':1000});page.goto(base+f'framework/diagrams/f35/{slug}-{theme}.svg',wait_until='networkidle')
      check(page.locator('svg').count()>=1,'svg not loaded')
      if width==1440:shot(page,f'independent-{slug}-{theme}')
   REC['independent_diagram_views']=16
   for path in ['framework/index.html','framework/f34.html']:
    for width in [1440,390,320]:
     for theme in ['light','dark']:
      page.set_viewport_size({'width':width,'height':900});page.goto(base+path,wait_until='networkidle');page.evaluate("t=>{document.documentElement.dataset.theme=t;localStorage.setItem('es-web:theme',t)}",theme)
      page.wait_for_load_state('networkidle')
      if path.endswith('f34.html'):images(page,theme)
      check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'related page overflow')
   REC['related_views']=12
   context.close()
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':390,'height':900},reduced_motion='reduce')
    context.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
    page=context.new_page();observe(page);page.goto((ROOT/'framework/f35.html').as_uri(),wait_until='networkidle');images(page,theme)
    check(page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches"),'reduced motion')
    check(page.evaluate("getComputedStyle(document.documentElement).scrollBehavior")=='auto','smooth reduced')
    page.locator('.theme-toggle').focus();check(page.locator('.theme-toggle').evaluate("e=>e===document.activeElement"),'focus')
    context.close()
   REC['file_themes_reduced_motion_keyboard']='passed'
   browser.close()
  check(not REC['js_errors'] and not REC['http_failures'] and not REC['request_failures'] and not REC['business_requests'],{k:REC[k] for k in ['js_errors','http_failures','request_failures','business_requests']})
  REC['passed']=True
 finally:
  server.shutdown();(D/'http-review.json').write_text(json.dumps(REC,ensure_ascii=False,indent=2)+'\n')
 print('F35 HTTP/file reading checks passed')
if __name__=='__main__':main()
