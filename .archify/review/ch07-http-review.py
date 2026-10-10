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
import threading, json, hashlib
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
parser=Tags();parser.feed((root/'chapters/ch07.html').read_text())
assert len(parser.ids)==len(set(parser.ids))
for link in parser.links:
 u=urlsplit(link)
 if u.scheme or u.netloc: continue
 target=((root/'chapters')/unquote(u.path)).resolve() if u.path else root/'chapters/ch07.html'
 assert target.is_file(),link
 if target.name=='ch07.html' and u.fragment: assert u.fragment in parser.ids,link
artifacts=[(f['id'].removeprefix('diagram-ch07-'),(root/'chapters'/urlsplit(f['src']).path).resolve()) for f in parser.frames]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
report={'kind':'independent-http-review','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
 'nativeBrowserGate':'failed-ERR_BLOCKED_BY_ADMINISTRATOR-file-url-policy',
 'realEsApi':'not-run-9200-not-connected-and-runtime-missing-proc-coredump_filter',
 'chapterSha256':hashlib.sha256((root/'chapters/ch07.html').read_bytes()).hexdigest(),
 'experimentSha256':hashlib.sha256((root/'experiments/ch07.js').read_bytes()).hexdigest(),
 'artifacts':[],'chapterLayouts':[],'functional':[],'javascriptErrors':[],'failedHttp':[],'captures':[]}
def capture(page,path,locator=None,full=False):
 dest=out/path
 # Theme colors transition briefly; capture the settled visual state.
 page.wait_for_timeout(300)
 if locator:
  viewport=page.viewport_size
  if viewport['width']>800 and locator.bounding_box()['height']>viewport['height']-100:
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
    assert len(dim['cards'])==2,(name,dim)
    assert all(c['scroll']<=c['height']+1 for c in dim['cards']),(name,dim)
    # The independent measurements retain actual SVG text size, including small badges.
    row['sizes'].append({'theme':theme,**dim})
    if width==1440:
     if page.locator('html').get_attribute('data-motion')=='live': page.locator('#btn-motion').click()
     capture(page,'ch07-'+name+'-standalone-'+theme+'.png',full=True)
  report['artifacts'].append(row)
 for theme in ['light','dark']:
  for width,height in [(1920,1080),(1440,1000),(1024,900),(768,900),(390,844),(320,800)]:
   page.set_viewport_size({'width':width,'height':height})
   assert page.goto(base+'/chapters/ch07.html').status==200
   if page.locator('html').get_attribute('data-theme')!=theme: page.locator('.theme-toggle').click()
   for name,_ in artifacts:
    page.locator('#diagram-ch07-'+name).scroll_into_view_if_needed()
    fr=page.frame_locator('#diagram-ch07-'+name)
    expect(fr.locator('.diagram-container svg[role="img"]')).to_be_visible()
    expect(fr.locator('html')).to_have_attribute('data-theme',theme)
   dim=page.evaluate('''() => {
    const boxes=[...document.querySelectorAll('.ch-header,.goal,.lesson > h2,.lesson > p,.archify-shell,.archify-figure figcaption,.ktable,.exp-slot,.drills,.pitfalls,.recap,.ch-footer')].map(e=>({kind:e.className||e.tagName,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width}));
    const frames=[...document.querySelectorAll('.archify-frame')].map(f=>({id:f.id,width:f.clientWidth,height:f.clientHeight,scrollWidth:f.contentDocument.documentElement.scrollWidth,scrollHeight:f.contentDocument.documentElement.scrollHeight,diagram:f.contentDocument.querySelector('.diagram-container').getBoundingClientRect().toJSON()}));
    return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,boxes,frames};
   }''')
   assert dim['scrollWidth']<=width,(width,dim['scrollWidth'])
   assert dim['boxes'][0]['width']<=880
   for box in dim['boxes']:
    assert abs(box['left']-dim['boxes'][0]['left'])<=1 and abs(box['right']-dim['boxes'][0]['right'])<=1,(width,box)
   for frame in dim['frames']:
    expectedHeight={'action-dispatch':440,'execution-chain':440} if width<=600 else ({'action-dispatch':680,'execution-chain':680} if width<=800 else {'action-dispatch':760,'execution-chain':760})
    assert frame['height']==expectedHeight[frame['id'].removeprefix('diagram-ch07-')],frame
    assert frame['scrollWidth']<=frame['width'],frame
    assert frame['scrollHeight']<=frame['height'],frame
   report['chapterLayouts'].append({'theme':theme,**dim})
 report['status']='layouts-pass-interactions-pending'
 (out/'ch07-http-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Passed diagram and chapter viewport/theme containment; checking interactions.',flush=True)
 page.set_viewport_size({'width':1440,'height':1000})
 page.goto(base+'/chapters/ch07.html')
 if page.locator('html').get_attribute('data-theme')!='light': page.locator('.theme-toggle').click()
 expect(page.locator('.exp-slot .exp')).to_have_count(15)
 expect(page.locator('.fp-slot')).to_have_count(0)
 expect(page.locator('[data-replay-diagram]')).to_have_count(2)
 for name,_ in artifacts:
  page.locator('#diagram-ch07-'+name).scroll_into_view_if_needed()
  fr=page.frame_locator('#diagram-ch07-'+name)
  fr.locator('[data-node-id]').first.click()
  expect(fr.locator('svg[data-focus-active]')).to_be_visible()
  links=fr.locator('a[href*="/blob/"]').evaluate_all('(els)=>els.map(e=>e.href)')
  assert links and any('/2e8528e92361c3399724226deaf2b46f933e925b/' in l for l in links),links
  fr.locator('#btn-focus-clear').click()
  page.mouse.move(2,2)
  expect(fr.locator('svg[data-focus-active]')).to_have_count(0)
 for name,_ in artifacts:
  fr=page.frame_locator('#diagram-ch07-'+name)
  replay=page.locator('[data-replay-diagram="diagram-ch07-'+name+'"]')
  replay.click()
  expect(fr.locator('html')).to_have_attribute('data-motion','live')
  fr.locator('#btn-motion').click()
  expect(fr.locator('html')).to_have_attribute('data-motion','still')
  replay.click()
  expect(fr.locator('html')).to_have_attribute('data-motion','live')
  replay.focus();page.keyboard.press('Enter')
  expect(fr.locator('html')).to_have_attribute('data-motion','live')
 for theme in ['light','dark']:
  if page.locator('html').get_attribute('data-theme')!=theme: page.locator('.theme-toggle').click()
  for name,_ in artifacts:
   expect(page.frame_locator('#diagram-ch07-'+name).locator('html')).to_have_attribute('data-theme',theme)
   fig=page.locator('#fig-ch07-'+name)
   fig.evaluate('(e)=>e.scrollIntoView({block:"start"})')
   page.mouse.move(2,2)
   capture(page,'ch07-'+name+'-embedded-'+theme+'.png',fig)
  page.evaluate('scrollTo(0,0)')
  capture(page,'ch07-hero-desktop-'+theme+'.png')
 for name,_ in artifacts:
  a=page.locator('#fig-ch07-'+name+' .archify-actions a')
  assert a.get_attribute('target')=='_blank'
  with page.expect_popup() as pop: a.click()
  full=pop.value;full.wait_for_load_state()
  assert 'present=' not in full.url
  expect(full.locator('.diagram-container svg[role="img"]')).to_be_visible()
  full.close()
 page.locator('.chapter-outline summary').click()
 page.locator('.chapter-outline a[href="#observation"]').click()
 assert page.evaluate('location.hash')=='#observation'
 expect(page.locator('#observation')).to_be_in_viewport()
 page.locator('.read-toggle').click()
 assert page.evaluate('JSON.parse(localStorage.getItem("es-web:read"))').get('ch07')
 page.locator('.read-toggle').click()
 specs=page.evaluate('Object.values(window.ESEXPERIMENTS)')
 assert len(specs)==15
 links=page.locator('.exp-slot a').evaluate_all('(els)=>els.map(e=>e.href)')
 assert len(links)==15 and all(l.startswith(base+'/console.html#run=') for l in links),links
 # Each real card opens the root console with the same request, without sending it.
 for i,link in enumerate(links):
  parts=[unquote(s) for s in urlsplit(link).fragment.removeprefix('run=').split('|')]
  spec=next(s for s in specs if s['method']==parts[0] and s['path']==parts[1])
  assert (parts[2]=='' if spec['body'] is None else json.loads(parts[2])==spec['body'])
  page.goto(base+'/chapters/ch07.html')
  page.locator('.exp-slot a').nth(i).click()
  expect(page.locator('#req-method')).to_have_value(parts[0])
  expect(page.locator('#req-path')).to_have_value(parts[1])
  expect(page.locator('#req-body')).to_have_value(parts[2])
 page.goto(base+'/chapters/ch07.html')
 checklink=page.evaluate('ESClient.consoleLink("POST","/_example","raw\\n",{endpoint:"http://localhost:9201",authMode:"anon",allowInvalid:true})')
 assert 'ep=http%3A%2F%2Flocalhost%3A9201' in checklink and 'am=anon' in checklink and 'raw=1' in checklink
 def pages_route(route):
  response=route.fetch(url=route.request.url.replace('/es_web/','/',1));route.fulfill(response=response)
 ctx.route(base+'/es_web/**',pages_route)
 page.goto(base+'/es_web/chapters/ch07.html')
 for name,_ in artifacts:
  page.locator('#diagram-ch07-'+name).scroll_into_view_if_needed()
  expect(page.frame_locator('#diagram-ch07-'+name).locator('.diagram-container svg[role="img"]')).to_be_visible()
 link=page.locator('.exp-slot a').first.get_attribute('href')
 assert link.startswith(base+'/es_web/console.html#run=')
 page.goto(link);expect(page.locator('#req-path')).to_have_value('/tut-l07-docs')
 page.set_viewport_size({'width':390,'height':844})
 for theme in ['light','dark']:
  page.goto(base+'/chapters/ch07.html')
  if page.locator('html').get_attribute('data-theme')!=theme: page.locator('.theme-toggle').click()
  capture(page,'ch07-hero-mobile-'+theme+'.png')
  for name,_ in artifacts:
   page.locator('#fig-ch07-'+name).evaluate('(e)=>e.scrollIntoView({block:"start"})')
   capture(page,'ch07-'+name+'-mobile-'+theme+'.png',page.locator('#fig-ch07-'+name))
   fr=page.frame_locator('#diagram-ch07-'+name)
   fr.locator('[data-node-id]').first.click()
   expect(fr.locator('svg[data-focus-active]')).to_be_visible()
   fr.locator('#btn-focus-clear').click()
  capture(page,'ch07-experiment-mobile-'+theme+'.png',page.locator('[data-exp="ch07-04-tasks-self"]'))
  capture(page,'ch07-source-table-mobile-'+theme+'.png',page.locator('#source-map + table'))
 reduced=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 rp=reduced.new_page();rp.goto(base+'/chapters/ch07.html')
 for name,_ in artifacts:
  rp.locator('#diagram-ch07-'+name).scroll_into_view_if_needed()
  rfr=rp.frame_locator('#diagram-ch07-'+name)
  expect(rfr.locator('html')).to_have_attribute('data-motion','still')
  expect(rfr.locator('#btn-motion')).to_be_disabled()
  rp.locator('[data-replay-diagram="diagram-ch07-'+name+'"]').click()
  expect(rfr.locator('html')).to_have_attribute('data-motion','still')
 assert rp.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto'
 reduced.close()
 assert not report['javascriptErrors'],report['javascriptErrors']
 assert not report['failedHttp'],report['failedHttp']
 report['functional']=['15-real-operation-cards','two-trace-replay-controls','theme-sync','node-source-exploration-close','pause-outer-replay','keyboard-replay','standalone-popup','chapter-outline-anchor','read-progress-toggle','15-console-request-deep-links','endpoint-auth-alias-raw-marker','Pages-prefix-assets-iframes-and-console','mobile-node-exploration','reduced-motion-overrides-replay','reduced-motion-no-smooth-scroll','internal-links-and-unique-chapter-ids']
 report['status']='pass'
 browser.close()
server.shutdown()
(out/'ch07-http-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 2 diagrams × 4 desktop sizes × 2 themes; ch07 × 6 widths × 2 themes; navigation, focus, replay, reduced motion, and 15 console links. Real ES API not run.')
