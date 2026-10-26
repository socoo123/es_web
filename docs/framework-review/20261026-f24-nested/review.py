#!/usr/bin/env python3
"""Actual static HTTP/file reading and interactive clipboard review for F24."""
import datetime,hashlib,json,pathlib,functools,http.server,threading,traceback
from playwright.sync_api import sync_playwright
import reading_helpers as h
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2]
INIT="""(() => {window.__imageChanges=[];new MutationObserver(ms=>ms.forEach(m=>{if(m.type==='attributes'&&m.attributeName==='src'&&m.target.tagName==='IMG'&&m.oldValue)window.__imageChanges.push({old:new URL(m.oldValue,location.href).href,current:m.target.src});})).observe(document,{subtree:true,attributes:true,attributeOldValue:true,attributeFilter:['src']});})();"""
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def shot(page,name,target=None):
 p=HERE/'screenshots'/(name+'.png');p.parent.mkdir(exist_ok=True)
 if target:
  page.locator('.topbar').evaluate("e=>e.style.visibility='hidden'") if page.locator('.topbar').count() else None
  try:page.locator(target).first.screenshot(path=str(p),timeout=20000)
  finally:page.locator('.topbar').evaluate("e=>e.style.visibility=''") if page.locator('.topbar').count() else None
 else:page.screenshot(path=str(p),timeout=20000)
 return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'pending'}
def run():
 rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F24 static tutorial; Java/ES recorded separately','matrix':[],'regression':[],'independent_diagrams':[],'screenshots':[],'js_errors':[],'http_failures':[],'request_failures':[],'business_requests':[],'replacement_proofs':[]}
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(h.Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
 def observe(page,group):
  page.on('pageerror',lambda e:rec['js_errors'].append({'group':group,'error':str(e)}))
  page.on('response',lambda r:rec['http_failures'].append({'group':group,'url':r.url,'status':r.status}) if r.status>=400 else None)
  page.on('requestfailed',lambda r:rec['request_failures'].append({'group':group,'url':r.url,'failure':r.failure}))
 def prove(page,group,theme):
  images=h.diagrams(page,theme);rec['replacement_proofs'].append({'group':group,'changes':page.evaluate('window.__imageChanges||[]'),'loaded':images});return images
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=h.BROWSER);rec['browser']={'engine':'Chromium','version':browser.version}
   for width in h.WIDTHS:
    print('Reading',width,flush=True)
    for theme in h.THEMES:
     group=f'{width}-{theme}';c=browser.new_context(viewport={'width':width,'height':1000},permissions=['clipboard-read','clipboard-write'],reduced_motion='reduce');c.add_init_script(INIT);c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')")
     def route(rt):
      from urllib.parse import urlsplit
      u=urlsplit(rt.request.url)
      if u.hostname in ['127.0.0.1','localhost'] and u.port in [9200,9201,19224,18081]:rec['business_requests'].append(rt.request.url);rt.abort()
      else:rt.continue_()
     c.route('**/*',route);page=c.new_page();observe(page,group);page.goto(base+'framework/f24.html',wait_until='networkidle');images=prove(page,group,theme);anchors=h.anchors(page)
     folds=[]
     for fold in page.locator('details').all():
      fold.locator('summary').click();require(fold.get_attribute('open') is not None,'opens');layout=h.measure(page);folds.append({'summary':fold.locator('summary').inner_text(),'expanded_width':layout['page']});fold.locator('summary').click()
     require(page.locator('.drills details').count()==7,'seven exercises');require(page.locator('pre.code-block').count()==page.locator('.copy-code').count(),'copy controls')
     rec['matrix'].append({'width':width,'theme':theme,'layout':h.measure(page),'images':images,'anchors':anchors,'folds':folds,'copy_controls':page.locator('.copy-code').count()})
     if width in [1440,390,320]:
      page.evaluate('scrollTo(0,0)');rec['screenshots'].append(shot(page,'f24-'+group+'-opening'))
      for slug in ['same-entry','price-scope']:rec['screenshots'].append(shot(page,'f24-'+group+'-'+slug,'#fig-'+slug))
      for name in ['samples','recap']:rec['screenshots'].append(shot(page,'f24-'+group+'-'+name,'#'+name+'-table'))
      rec['screenshots'].append(shot(page,'f24-'+group+'-query','pre[data-source$="matched.json"]'))
      rec['screenshots'].append(shot(page,'f24-'+group+'-java','pre[data-source$="NestedSearchService.java"]'))
     page.goto(base+'framework/index.html',wait_until='networkidle');require(page.locator('.curriculum-lesson-link[href="f24.html"][data-ch="f24"]').count()==1,'directory F24');require(page.locator('a[href="f25.html"]').count()==0,'F25 pending');rec['regression'].append({'page':'index','width':width,'theme':theme,'layout':h.measure(page,False)})
     page.goto(base+'framework/f23.html',wait_until='networkidle');prove(page,group,theme);require(page.locator('.pager a[href="f24.html"]').count()==1,'F23 next');rec['regression'].append({'page':'F23','width':width,'theme':theme,'layout':h.measure(page)});c.close()
   c=browser.new_context(viewport={'width':1440,'height':1000},permissions=['clipboard-read','clipboard-write'],reduced_motion='reduce');c.add_init_script(INIT);page=c.new_page();group='interactions';observe(page,group);page.goto(base+'framework/f24.html',wait_until='networkidle');prove(page,group,'light')
   # Copy every real block, including collapsed Java and JSON, through OS clipboard.
   for fold in page.locator('details').all():fold.evaluate('e=>e.open=true')
   copies=[]
   for i in range(page.locator('.copy-code').count()):
    text=page.locator('pre.code-block code').nth(i).text_content();page.locator('.copy-code').nth(i).click();page.wait_for_function('s=>navigator.clipboard.readText().then(v=>v===s)',arg=text);require(page.evaluate('navigator.clipboard.readText()')==text,'clipboard exact');copies.append({'block':i,'chars':len(text),'sha256':hashlib.sha256(text.encode()).hexdigest(),'actual_clipboard_equal':True})
   rec['clipboard']=copies
   for fold in page.locator('details').all():fold.evaluate('e=>e.open=false')
   for theme in ['dark','light']:
    page.locator('.theme-toggle').click();prove(page,group,theme);page.reload(wait_until='networkidle');prove(page,group,theme)
   rec['theme_reload']='actual switch/images/expand URLs and reload preserved'
   popups=[]
   for link in page.locator('[data-expand-d2]').all():
    with page.expect_popup() as info:link.click()
    popup=info.value;popup.wait_for_load_state('load');require(popup.locator('svg').first.is_visible(),'SVG opened');popups.append(popup.url);popup.close()
   rec['actual_popups']=popups
   page.evaluate("localStorage.setItem('es-web:read',JSON.stringify({'f23':true,'f01-v2':true}))");page.reload(wait_until='networkidle');prove(page,group,'light');page.locator('.read-toggle').click();page.reload(wait_until='networkidle');prove(page,group,'light');require(page.locator('.read-toggle').evaluate("e=>e.classList.contains('is-on')"),'read persists');state=page.evaluate("JSON.parse(localStorage.getItem('es-web:read'))");require(state['f23'] and state['f24'] and state['f01-v2'],'independent read keys');rec['progress_keys']=state
   page.locator('.pager a[href="index.html"]').click();page.wait_for_load_state('networkidle');require(page.locator('[data-ch="f24"]').evaluate("e=>e.classList.contains('is-read')"),'directory badge');page.locator('.curriculum-lesson-link[href="f24.html"]').click();page.wait_for_load_state('networkidle');prove(page,group,'light')
   focuses=[]
   page.locator('.theme-toggle').focus()
   for _ in range(8):page.keyboard.press('Tab');focuses.append(page.evaluate("({tag:document.activeElement.tagName,text:document.activeElement.textContent.slice(0,80)})"))
   require(all(f['tag']!='BODY' for f in focuses),'keyboard reaches controls');rec['keyboard']=focuses;rec['reduced_motion']=page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches");require(rec['reduced_motion'],'reduce active');c.close()
   for width in [1440,1600,1920,2048]:
    for theme in h.THEMES:
     for slug in ['same-entry','price-scope']:
      c=browser.new_context(viewport={'width':width,'height':1000});p=c.new_page();p.goto(base+f'framework/diagrams/f24/{slug}-{theme}.svg',wait_until='load');require(p.locator('svg').first.is_visible(),'independent svg');rec['independent_diagrams'].append({'width':width,'theme':theme,'slug':slug,'box':p.locator('svg').first.bounding_box()})
      if width==1440:rec['screenshots'].append(shot(p,f'independent-{slug}-{theme}'))
      c.close()
   for theme in h.THEMES:
    c=browser.new_context(viewport={'width':390,'height':1000});c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')");p=c.new_page();p.goto((R/'framework/f24.html').as_uri(),wait_until='load');h.diagrams(p,theme);h.measure(p);rec.setdefault('file_reading',[]).append({'theme':theme,'passed':True});c.close()
   browser.close()
  rec['static_links']=h.static_links();rec['verified_theme_cancellations']=[];rec['unexplained_request_failures']=[]
  for failure in rec['request_failures']:
   proof=next(({'failure':failure,'change':change,'replacement':image} for p in rec['replacement_proofs'] if p['group']==failure['group'] for change in p['changes'] for image in p['loaded'] if failure['failure']=='net::ERR_ABORTED' and failure['url']==change['old'] and change['current']==image['src'] and image['width']>0 and image['height']>0),None)
   (rec['verified_theme_cancellations'] if proof else rec['unexplained_request_failures']).append(proof or failure)
  require(not rec['js_errors'] and not rec['http_failures'] and not rec['unexplained_request_failures'] and not rec['business_requests'],'no unhandled JS/network/business calls')
  rec['status']='passed'
 except Exception as e:rec['status']='failed';rec['error']=str(e);rec['traceback']=traceback.format_exc();raise
 finally:server.shutdown();(HERE/'http-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
 print('F24 HTTP reading passed',len(rec['matrix']),'groups,',len(rec['screenshots']),'screenshots',len(rec['clipboard']),'actual clipboard copies')
if __name__=='__main__':run()
