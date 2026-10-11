"""Independent HTTP checks; does not replace Archify's native file:// browser gate.
Run with Python + Playwright and the environment's installed Chromium.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit, unquote
from html.parser import HTMLParser
import threading, json, hashlib, sys
from playwright.sync_api import sync_playwright, expect
root=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent
class Tags(HTMLParser):
 def __init__(self): super().__init__(); self.frames=[]; self.links=[]; self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a: self.ids.append(a['id'])
  if tag=='iframe': self.frames.append(a)
  if tag in ['a','link','script']:
   value=a.get('href') or a.get('src')
   if value: self.links.append(value)
parser=Tags();parser.feed((root/'chapters/ch14.html').read_text())
assert len(parser.ids)==len(set(parser.ids))
for link in parser.links:
 u=urlsplit(link)
 if u.scheme or u.netloc: continue
 target=((root/'chapters')/unquote(u.path)).resolve() if u.path else root/'chapters/ch14.html'
 assert target.is_file(),link
 if target.name=='ch14.html' and u.fragment: assert u.fragment in parser.ids,link
artifacts=[(f['id'].removeprefix('diagram-ch14-'),(root/'chapters'/urlsplit(f['src']).path).resolve()) for f in parser.frames]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
report={'kind':'independent-http-review','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
 'nativeBrowserGate':'failed-ERR_BLOCKED_BY_ADMINISTRATOR-file-url-policy',
 'realEsApi':'not-run-9200-not-connected-and-runtime-missing-proc-coredump_filter',
 'chapterSha256':hashlib.sha256((root/'chapters/ch14.html').read_bytes()).hexdigest(),
 'experimentSha256':hashlib.sha256((root/'experiments/ch14.js').read_bytes()).hexdigest(),
 'artifacts':[],'chapterLayouts':[],'functional':[],'javascriptErrors':[],'failedHttp':[],'captures':[]}
def capture(page,path,locator=None,full=False):
 dest=out/path
 # Theme colors transition briefly; capture the settled visual state.
 page.wait_for_timeout(300)
 if locator:
  viewport=page.viewport_size
  if locator.bounding_box()['height']>viewport['height']-100:
   page.set_viewport_size({'width':viewport['width'],'height':int(locator.bounding_box()['height'])+200})
   locator.evaluate('(e)=>e.scrollIntoView({block:"start"})');page.evaluate('scrollBy(0,-100)')
   locator.screenshot(path=str(dest))
   page.set_viewport_size(viewport)
  else: locator.screenshot(path=str(dest))
 else: page.screenshot(path=str(dest),full_page=full)
 report['captures'].append(path)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1440,'height':1000})
 page=ctx.new_page()
 page.on('pageerror',lambda e:report['javascriptErrors'].append(str(e)))
 page.on('response',lambda r:report['failedHttp'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
 run_layouts='--interactions-only' not in sys.argv
 if not run_layouts:
  cached=json.loads((out/'ch14-http-review.json').read_text())
  assert cached['chapterSha256']==report['chapterSha256'] and cached['experimentSha256']==report['experimentSha256']
  assert len(cached['artifacts'])==2 and len(cached['chapterLayouts'])==12
  for record in cached['artifacts']:
   path=root/record['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==record['htmlSha256']
   assert hashlib.sha256(path.with_name('candidate.json').read_bytes()).hexdigest()==record['sourceSha256']
   assert len(record['sizes'])==8
  for key in ['artifacts','chapterLayouts','captures']:report[key]=cached[key]
 if run_layouts:
  for name,path in artifacts:
   row={'id':name,'path':str(path.relative_to(root)),
    'htmlSha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'sourceSha256':hashlib.sha256(path.with_name('candidate.json').read_bytes()).hexdigest(),'sizes':[]}
   for theme in ['light','dark']:
    for width,height in [(1440,900),(1600,1000),(1920,1080),(2048,1320)]:
     page.set_viewport_size({'width':width,'height':height})
     assert page.goto(base+'/'+row['path']+'?theme='+theme).status==200
     expect(page.locator('.diagram-container svg[role="img"]')).to_be_visible()
     expect(page.locator('html')).to_have_attribute('data-theme',theme)
     page.evaluate('document.fonts.ready')
     page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
     dim=page.evaluate('''() => {
       const texts=[...document.querySelectorAll('.diagram-container svg text')].filter(e=>e.getClientRects().length && getComputedStyle(e).display!=='none');
       const projected=texts.map(e=>({text:e.textContent,fontPx:parseFloat(getComputedStyle(e).fontSize)*Math.hypot(e.getScreenCTM().a,e.getScreenCTM().b)}));
       const cards=[...document.querySelectorAll('.cards .card')].map(e=>({scroll:e.scrollHeight,height:e.clientHeight}));
       const nodeText=texts.filter(e=>e.closest('[data-node-id]') && !e.textContent.startsWith('来源 ')).map(e=>parseFloat(getComputedStyle(e).fontSize)*Math.hypot(e.getScreenCTM().a,e.getScreenCTM().b));
       return {width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,minimumSvgTextPx:Math.min(...projected.map(t=>t.fontPx)),minimumNodeTextPx:Math.min(...nodeText),cards};
     }''')
     assert dim['scrollWidth']<=width,(name,dim)
     assert dim['minimumSvgTextPx']>=6,(name,dim)
     # 6px is the required projection floor; normal node context also stays at least 7px.
     assert dim['minimumNodeTextPx']>=7,(name,dim)
     assert len(dim['cards'])==({'index-order':2,'flush-order':2}[name]),(name,dim)
     assert all(c['scroll']<=c['height']+1 for c in dim['cards']),(name,dim)
     # The independent measurements retain actual SVG text size, including small badges.
     row['sizes'].append({'theme':theme,**dim})
     if width==1440:
      if page.locator('html').get_attribute('data-motion')=='live': page.locator('#btn-motion').click()
      capture(page,'ch14-'+name+'-standalone-'+theme+'.png',full=True)
   report['artifacts'].append(row)
  for theme in ['light','dark']:
   for width,height in [(1920,1080),(1440,1000),(1024,900),(768,900),(390,844),(320,800)]:
    page.set_viewport_size({'width':width,'height':height})
    assert page.goto(base+'/chapters/ch14.html').status==200
    if page.locator('html').get_attribute('data-theme')!=theme: page.locator('.theme-toggle').click()
    for name,_ in artifacts:
     page.locator('#diagram-ch14-'+name).scroll_into_view_if_needed()
     fr=page.frame_locator('#diagram-ch14-'+name)
     expect(fr.locator('.diagram-container svg[role="img"]')).to_be_visible()
     expect(fr.locator('html')).to_have_attribute('data-theme',theme)
     panel=fr.locator('.diagram-container').bounding_box()
     nodes=fr.locator('.diagram-container svg[role="img"] [data-node-id]')
     assert nodes.count()>0
     for j in range(nodes.count()):
      n=nodes.nth(j).bounding_box()
      assert n and n['width']>0 and n['height']>0,(width,name,j,n)
      assert n['x']>=panel['x']-1 and n['x']+n['width']<=panel['x']+panel['width']+1 and n['y']>=panel['y']-1 and n['y']+n['height']<=panel['y']+panel['height']+1,(width,name,j,n,panel)
    dim=page.evaluate('''() => {
     const boxes=[...document.querySelectorAll('.ch-header,.goal,.lesson > h2,.lesson > p,.archify-shell,.archify-figure figcaption,.ktable,.exp-slot,.drills,.pitfalls,.recap,.ch-footer')].map(e=>({kind:e.className||e.tagName,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width}));
     const frames=[...document.querySelectorAll('.archify-frame')].map(f=>({id:f.id,width:f.clientWidth,height:f.clientHeight,scrollWidth:f.contentDocument.documentElement.scrollWidth,scrollHeight:f.contentDocument.documentElement.scrollHeight,diagram:f.contentDocument.querySelector('.diagram-container').getBoundingClientRect().toJSON(), nodes:[...f.contentDocument.querySelectorAll('.diagram-container svg[role="img"] [data-node-id]')].map(n=>({id:n.getAttribute('data-node-id'),...n.getBoundingClientRect().toJSON()}))}));
     return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,boxes,frames};
    }''')
    assert dim['scrollWidth']<=width,(width,dim['scrollWidth'])
    assert dim['boxes'][0]['width']<=880
    for box in dim['boxes']:
     assert abs(box['left']-dim['boxes'][0]['left'])<=1 and abs(box['right']-dim['boxes'][0]['right'])<=1,(width,box)
    for frame in dim['frames']:
     expectedHeight={'index-order':500,'flush-order':500} if width<=600 else ({'index-order':780,'flush-order':740} if width<=800 else {'index-order':940,'flush-order':840})
     assert frame['height']==expectedHeight[frame['id'].removeprefix('diagram-ch14-')],frame
     assert frame['scrollWidth']<=frame['width'],frame
     assert frame['scrollHeight']<=frame['height'],frame
    report['chapterLayouts'].append({'theme':theme,**dim})
 report['status']='layouts-pass-interactions-pending'
 (out/'ch14-http-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Passed diagram and chapter viewport/theme containment; checking interactions.',flush=True)
 page.set_viewport_size({'width':1440,'height':1000})
 page.goto(base+'/chapters/ch14.html')
 if page.locator('html').get_attribute('data-theme')!='light': page.locator('.theme-toggle').click()
 expect(page.locator('.exp-slot .exp')).to_have_count(46)
 expect(page.locator('.fp-slot .fp')).to_have_count(1)
 expect(page.locator('[data-replay-diagram]')).to_have_count(2)
 for name,_ in artifacts:
  page.locator('#diagram-ch14-'+name).scroll_into_view_if_needed()
  fr=page.frame_locator('#diagram-ch14-'+name)
  fr.locator('[data-node-id]').first.click()
  expect(fr.locator('svg[data-focus-active]')).to_be_visible()
  links=fr.locator('a[href*="/blob/"]').evaluate_all('(els)=>els.map(e=>e.href)')
  assert links and any('/2e8528e92361c3399724226deaf2b46f933e925b/' in l for l in links),links
  fr.locator('#btn-focus-clear').click()
  page.mouse.move(2,2)
  expect(fr.locator('svg[data-focus-active]')).to_have_count(0)
 for name,_ in artifacts:
  fr=page.frame_locator('#diagram-ch14-'+name)
  replay=page.locator('[data-replay-diagram="diagram-ch14-'+name+'"]')
  replay.click()
  expect(fr.locator('html')).to_have_attribute('data-motion','live')
  fr.locator('#btn-motion').click()
  expect(fr.locator('html')).to_have_attribute('data-motion','still')
  replay.click()
  expect(fr.locator('html')).to_have_attribute('data-motion','live')
  replay.focus();page.keyboard.press('Enter')
  expect(fr.locator('html')).to_have_attribute('data-motion','live')
 # Each step is inspected for contained SVG text, unique marker IDs and actual controls.
 fp=page.locator('.fp');fp.scroll_into_view_if_needed()
 fp.locator('[title="重置"]').click()
 for step in range(8):
  expect(fp.locator('.fp-count')).to_have_text(str(step+1)+' / 8')
  widths=fp.locator('.fp-stage svg').evaluate("""svg=>{
   const vb=svg.viewBox.baseVal;
   const ids=[...svg.querySelectorAll('[id]')].map(n=>n.id);
   const text=[...svg.querySelectorAll('text')].map(t=>(()=>{const b=t.getBBox();return {text:t.textContent,x:b.x,y:b.y,width:b.width,height:b.height};})());
   return {width:vb.width,height:vb.height,uniqueIds:new Set(ids).size===ids.length,text};
  }""")
  assert widths['uniqueIds']
  assert all(t['x']>=-1 and t['x']+t['width']<=widths['width']+1 and t['y']>=-1 and t['y']+t['height']<=widths['height']+1 for t in widths['text']),widths
  if step<7:fp.locator('[title="下一步"]').click()
 fp.locator('[title="上一步"]').click();expect(fp.locator('.fp-count')).to_have_text('7 / 8')
 fp.focus();page.keyboard.press('ArrowLeft');expect(fp.locator('.fp-count')).to_have_text('6 / 8')
 page.keyboard.press('ArrowRight');expect(fp.locator('.fp-count')).to_have_text('7 / 8')
 fp.locator('[title="重置"]').click();expect(fp.locator('.fp-count')).to_have_text('1 / 8')
 fp.locator('[title="播放/暂停"]').click();expect(fp.locator('[title="播放/暂停"]')).to_have_text('⏸')
 fp.locator('[title="播放/暂停"]').click();expect(fp.locator('[title="播放/暂停"]')).to_have_text('▶')
 for theme in ['light','dark']:
  if page.locator('html').get_attribute('data-theme')!=theme: page.locator('.theme-toggle').click()
  for name,_ in artifacts:
   expect(page.frame_locator('#diagram-ch14-'+name).locator('html')).to_have_attribute('data-theme',theme)
   fig=page.locator('#fig-ch14-'+name)
   fig.evaluate('(e)=>e.scrollIntoView({block:"start"})')
   page.mouse.move(2,2)
   capture(page,'ch14-'+name+'-embedded-'+theme+'.png',fig)
  fp.locator('[title="重置"]').click()
  for _ in range(4):fp.locator('[title="下一步"]').click()
  capture(page,'ch14-mechanism-desktop-'+theme+'.png',fp)
  page.evaluate('scrollTo(0,0)')
  capture(page,'ch14-hero-desktop-'+theme+'.png')
 for name,_ in artifacts:
  a=page.locator('#fig-ch14-'+name+' .archify-actions a')
  assert a.get_attribute('target')=='_blank'
  with page.expect_popup() as pop: a.click()
  full=pop.value;full.wait_for_load_state()
  assert 'present=' not in full.url
  expect(full.locator('.diagram-container svg[role="img"]')).to_be_visible()
  full.close()
 page.locator('.chapter-outline summary').click()
 page.locator('.chapter-outline a[href="#indexing"]').click()
 assert page.evaluate('location.hash')=='#indexing'
 expect(page.locator('#indexing')).to_be_in_viewport()
 page.locator('.read-toggle').click()
 assert page.evaluate('JSON.parse(localStorage.getItem("es-web:read"))').get('ch14')
 page.locator('.read-toggle').click()
 specs=page.evaluate('Object.values(window.ESEXPERIMENTS)')
 assert len(specs)==46
 links=page.locator('.exp-slot a').evaluate_all('(els)=>els.map(e=>e.href)')
 assert len(links)==46 and all(urlsplit(l).path=='/console.html' for l in links),links
 # Each real card opens the root console with the same request, without sending it.
 for i,link in enumerate(links):
  parts=[unquote(s) for s in urlsplit(link).fragment.removeprefix('run=').split('|')]
  spec=specs[i]
  assert spec['method']==parts[0] and spec['path']==parts[1]
  assert (parts[2]=='' if spec['body'] is None else parts[2]==spec['body'] if isinstance(spec['body'],str) else json.loads(parts[2])==spec['body'])
  assert ('raw=1' in urlsplit(link).query)==bool(spec.get('allowInvalidBody'))
  page.goto(base+'/chapters/ch14.html')
  page.locator('.exp-slot a').nth(i).click()
  expect(page.locator('#req-method')).to_have_value(parts[0])
  expect(page.locator('#req-path')).to_have_value(parts[1])
  expect(page.locator('#req-body')).to_have_value(parts[2])
 page.goto(base+'/chapters/ch14.html')
 checklink=page.evaluate('ESClient.consoleLink("POST","/_example","raw\\n",{endpoint:"http://localhost:9201",authMode:"anon",allowInvalid:true})')
 assert 'ep=http%3A%2F%2Flocalhost%3A9201' in checklink and 'am=anon' in checklink and 'raw=1' in checklink
 def pages_route(route):
  response=route.fetch(url=route.request.url.replace('/es_web/','/',1));route.fulfill(response=response)
 ctx.route(base+'/es_web/**',pages_route)
 page.goto(base+'/es_web/chapters/ch14.html')
 for name,_ in artifacts:
  page.locator('#diagram-ch14-'+name).scroll_into_view_if_needed()
  expect(page.frame_locator('#diagram-ch14-'+name).locator('.diagram-container svg[role="img"]')).to_be_visible()
 link=page.locator('.exp-slot a').first.get_attribute('href')
 assert link.startswith(base+'/es_web/console.html#run=')
 page.goto(link);expect(page.locator('#req-path')).to_have_value(specs[0]['path'])
 page.set_viewport_size({'width':390,'height':844})
 for theme in ['light','dark']:
  page.goto(base+'/chapters/ch14.html')
  if page.locator('html').get_attribute('data-theme')!=theme: page.locator('.theme-toggle').click()
  capture(page,'ch14-hero-mobile-'+theme+'.png')
  for name,_ in artifacts:
   page.locator('#fig-ch14-'+name).evaluate('(e)=>e.scrollIntoView({block:"start"})')
   ready=page.frame_locator('#diagram-ch14-'+name)
   expect(ready.locator('.diagram-container svg[role="img"]')).to_be_visible()
   expect(ready.locator('html')).to_have_attribute('data-theme',theme)
   ready.locator('html').evaluate('e=>e.ownerDocument.fonts.ready')
   capture(page,'ch14-'+name+'-mobile-'+theme+'.png',page.locator('#fig-ch14-'+name))
   page.locator('#diagram-ch14-'+name).evaluate('(e)=>e.scrollIntoView({block:"center",behavior:"instant"})')
   page.wait_for_timeout(300)
   fr=page.frame_locator('#diagram-ch14-'+name)
   fr.locator('[data-node-id]').first.click()
   expect(fr.locator('svg[data-focus-active]')).to_be_visible()
   fr.locator('#btn-focus-clear').click()
  capture(page,'ch14-experiment-mobile-'+theme+'.png',page.locator('[data-exp="ch14-01-nrt-put"]'))
  capture(page,'ch14-source-table-mobile-'+theme+'.png',page.locator('#source-map + table'))
  fp=page.locator('.fp');fp.locator('[title="重置"]').click()
  for _ in range(4):fp.locator('[title="下一步"]').click()
  capture(page,'ch14-mechanism-mobile-'+theme+'.png',fp)
 reduced=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 rp=reduced.new_page();rp.goto(base+'/chapters/ch14.html')
 for name,_ in artifacts:
  rp.locator('#diagram-ch14-'+name).scroll_into_view_if_needed()
  rfr=rp.frame_locator('#diagram-ch14-'+name)
  expect(rfr.locator('html')).to_have_attribute('data-motion','still')
  expect(rfr.locator('#btn-motion')).to_be_disabled()
  rp.locator('[data-replay-diagram="diagram-ch14-'+name+'"]').click()
  expect(rfr.locator('html')).to_have_attribute('data-motion','still')
 assert rp.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto'
 rfp=rp.locator('.fp');rfp.scroll_into_view_if_needed();rp.wait_for_timeout(2500)
 expect(rfp.locator('.fp-count')).to_have_text('1 / 8')
 expect(rfp.locator('[title="播放/暂停"]')).to_have_text('▶')
 rfp.locator('[title="下一步"]').click();expect(rfp.locator('.fp-count')).to_have_text('2 / 8')
 rfp.focus();rp.keyboard.press('ArrowRight');expect(rfp.locator('.fp-count')).to_have_text('3 / 8')
 reduced.close()
 assert not report['javascriptErrors'],report['javascriptErrors']
 assert not report['failedHttp'],report['failedHttp']
 report['functional']=['NDJSON-and-JSON-console-deep-links','46-real-operation-cards','eight-step-mechanism-player','all-diagram-nodes-contained-without-mobile-clipping','two-trace-replay-controls','theme-sync','node-source-exploration-close','pause-outer-replay','keyboard-replay','standalone-popup','chapter-outline-anchor','read-progress-toggle','46-console-request-deep-links','endpoint-auth-alias-raw-marker','Pages-prefix-assets-iframes-and-console','mobile-node-exploration','reduced-motion-overrides-replay','reduced-motion-no-smooth-scroll','internal-links-and-unique-chapter-ids']
 report['status']='pass'
 browser.close()
server.shutdown()
(out/'ch14-http-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 2 diagrams × 4 desktop sizes × 2 themes; ch14 × 6 widths × 2 themes; navigation, focus, replay, reduced motion, and 46 console links. Real ES API not run.')
