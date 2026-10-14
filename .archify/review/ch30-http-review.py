"""Independent HTTP layout/interaction review; API traffic is aborted here."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit,unquote,parse_qs
from html.parser import HTMLParser
import threading,json,hashlib
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
rev='2e8528e92361c3399724226deaf2b46f933e925b'
paths=json.loads((out/'ch30-paths.json').read_text())
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if t in ['a','link','script','iframe']:
   l=a.get('href') or a.get('src')
   if l:self.links.append(l)
parser=Tags();parser.feed((root/'chapters/ch30.html').read_text());assert len(parser.ids)==len(set(parser.ids))
for l in parser.links:
 u=urlsplit(l)
 if u.scheme:continue
 target=(root/'chapters'/unquote(u.path)).resolve() if u.path else root/'chapters/ch30.html'
 assert target.is_file(),l
 if not u.path and u.fragment:assert u.fragment in parser.ids,l
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)
sha=lambda p:hashlib.sha256((root/p).read_bytes()).hexdigest()
report={'kind':'independent-http-review','status':'running','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'chapterSha256':sha('chapters/ch30.html'),'experimentSha256':sha('experiments/ch30.js'),'standalone':[],'chapterLayouts':[],'mechanism':[],'captures':[],'javascriptErrors':[],'failedHttp':[],'functional':[]}
def save():(out/'ch30-http-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def capture(page,name,loc=None,full=False):
 page.wait_for_timeout(300)
 dest=out/('ch30-'+name+'.png')
 if loc:
  viewport=page.viewport_size;h=loc.bounding_box()['height']
  if h>viewport['height']-120:page.set_viewport_size({'width':viewport['width'],'height':int(h)+200})
  loc.evaluate('e=>e.scrollIntoView({block:"start"})');page.evaluate('scrollBy(0,-110)');page.wait_for_timeout(300)
  loc.screenshot(path=str(dest));page.set_viewport_size(viewport)
 else:page.screenshot(path=str(dest),full_page=full)
 report['captures'].append(dest.name)
with sync_playwright() as p:
 browser=p.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':1000})
 ctx.route('http://localhost:9200/**',lambda r:r.abort());ctx.route('http://localhost:9201/**',lambda r:r.abort())
 page=ctx.new_page();page.on('pageerror',lambda e:report['javascriptErrors'].append(str(e)))
 page.on('response',lambda r:report['failedHttp'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
 for name,path in paths.items():
  row={'id':name,'htmlSha256':sha(path),'sourceSha256':sha(str(Path(path).with_name('candidate.json'))),'sizes':[]}
  for theme in ['light','dark']:
   for width,height in [(1440,900),(1600,1000),(1920,1080),(2048,1320)]:
    page.set_viewport_size({'width':width,'height':height});assert page.goto(base+'/'+path+'?theme='+theme).status==200
    expect(page.locator('html')).to_have_attribute('data-theme',theme);expect(page.locator('.diagram-container svg[role="img"]')).to_be_visible();page.evaluate('document.fonts.ready')
    d=page.evaluate('''()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,cards:[...document.querySelectorAll('.cards .card')].map(e=>({scroll:e.scrollHeight,height:e.clientHeight})),texts:[...document.querySelectorAll('.diagram-container svg text')].filter(e=>e.getClientRects().length&&getComputedStyle(e).display!=='none').map(e=>({text:e.textContent,fontPx:parseFloat(getComputedStyle(e).fontSize)*Math.hypot(e.getScreenCTM().a,e.getScreenCTM().b)}))})''')
    assert d['scrollWidth']<=width,(name,d);assert all(c['scroll']<=c['height']+1 for c in d['cards'])
    assert min(t['fontPx'] for t in d['texts'])>=6,(name,width,d['texts'])
    row['sizes'].append({'theme':theme,**d})
    if width==1440:
     if page.locator('html').get_attribute('data-motion')=='live':page.locator('#btn-motion').click()
     capture(page,name+'-standalone-'+theme,full=True)
  report['standalone'].append(row);save()
 for theme in ['light','dark']:
  for width,height in [(1920,1080),(1440,1000),(1024,900),(768,900),(390,844),(320,800)]:
   page.set_viewport_size({'width':width,'height':height});assert page.goto(base+'/chapters/ch30.html').status==200
   if page.locator('html').get_attribute('data-theme')!=theme:page.locator('.theme-toggle').click()
   for name in paths:
    page.locator('#diagram-ch30-'+name).scroll_into_view_if_needed();fr=page.frame_locator('#diagram-ch30-'+name)
    expect(fr.locator('.diagram-container svg[role="img"]')).to_be_visible();expect(fr.locator('html')).to_have_attribute('data-theme',theme);fr.locator('html').evaluate('e=>e.ownerDocument.fonts.ready')
    panel=fr.locator('.diagram-container').bounding_box();nodes=fr.locator('.diagram-container svg[role="img"] [data-node-id]')
    for i in range(nodes.count()):
     n=nodes.nth(i).bounding_box()
     assert n and n['x']>=panel['x']-1 and n['x']+n['width']<=panel['x']+panel['width']+1 and n['y']>=panel['y']-1 and n['y']+n['height']<=panel['y']+panel['height']+1,(name,width,n,panel)
   d=page.evaluate('''()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,boxes:[...document.querySelectorAll('.ch-header,.goal,.lesson > h2,.lesson > p,.archify-shell,.archify-figure figcaption,.ktable,.exp-slot,.drills,.pitfalls,.recap,.ch-footer')].map(e=>({kind:e.className||e.tagName,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width})),frames:[...document.querySelectorAll('.archify-frame')].map(f=>({id:f.id,width:f.clientWidth,height:f.clientHeight,scrollWidth:f.contentDocument.documentElement.scrollWidth,scrollHeight:f.contentDocument.documentElement.scrollHeight}))})''')
   assert d['scrollWidth']<=width,(width,d['scrollWidth']);ref=d['boxes'][0];assert ref['width']<=880
   for b in d['boxes']:assert abs(b['left']-ref['left'])<=1 and abs(b['right']-ref['right'])<=1,(width,b,ref)
   for f in d['frames']:assert f['scrollWidth']<=f['width'] and f['scrollHeight']<=f['height'],(width,f)
   report['chapterLayouts'].append({'theme':theme,**d});save()
 print('PASS: viewport/theme layouts; checking interactions.',flush=True)
 page.set_viewport_size({'width':1440,'height':1100});page.goto(base+'/chapters/ch30.html')
 expect(page.locator('.exp-slot .exp')).to_have_count(20);expect(page.locator('.fp')).to_have_count(1)
 for name in paths:
  frame='#diagram-ch30-'+name;page.locator(frame).scroll_into_view_if_needed();fr=page.frame_locator(frame)
  fr.locator('[data-node-id]').first.click();expect(fr.locator('svg[data-focus-active]')).to_be_visible()
  if name=='search-handoffs':assert fr.locator('a[href*="/blob/'+rev+'/"]').count()>0
  fr.locator('#btn-focus-clear').click();page.mouse.move(2,2);expect(fr.locator('svg[data-focus-active]')).to_have_count(0)
  fr.locator('[data-node-id]').first.focus();page.keyboard.press('Enter');expect(fr.locator('svg[data-focus-active]')).to_be_visible();page.keyboard.press('Escape');expect(fr.locator('svg[data-focus-active]')).to_have_count(0)
  replay=page.locator('[data-replay-diagram="diagram-ch30-'+name+'"]');replay.click();expect(fr.locator('html')).to_have_attribute('data-motion','live')
  fr.locator('#btn-motion').click();expect(fr.locator('html')).to_have_attribute('data-motion','still');replay.click();expect(fr.locator('html')).to_have_attribute('data-motion','live')
  replay.focus();page.keyboard.press('Enter');expect(fr.locator('html')).to_have_attribute('data-motion','live')
  with page.expect_popup() as pop:page.locator('#fig-ch30-'+name+' .archify-actions a').click()
  full=pop.value;full.wait_for_load_state();assert 'present=' not in full.url;expect(full.locator('.diagram-container svg[role="img"]')).to_be_visible();full.close()
 for theme in ['light','dark']:
  if page.locator('html').get_attribute('data-theme')!=theme:page.locator('.theme-toggle').click()
  page.evaluate('scrollTo(0,0)');capture(page,'hero-desktop-'+theme)
  for name in paths:
   fr=page.frame_locator('#diagram-ch30-'+name);page.locator('#diagram-ch30-'+name).scroll_into_view_if_needed();expect(fr.locator('html')).to_have_attribute('data-theme',theme)
   if fr.locator('html').get_attribute('data-motion')=='live':fr.locator('#btn-motion').click()
   capture(page,name+'-embedded-'+theme,page.locator('#fig-ch30-'+name))
  mfp=page.locator('.fp');mfp.locator('[title="重置"]').click();capture(page,'mechanism-desktop-'+theme,mfp)
 fp=page.locator('.fp');fp.scroll_into_view_if_needed();fp.locator('[title="重置"]').click()
 for i in range(7):
  expect(fp.locator('.fp-count')).to_have_text(str(i+1)+' / 7')
  d=fp.locator('svg').evaluate('''svg=>({width:svg.viewBox.baseVal.width,height:svg.viewBox.baseVal.height,texts:[...svg.querySelectorAll('text')].map(t=>({text:t.textContent,...(()=>{let b=t.getBBox();return {x:b.x,y:b.y,width:b.width,height:b.height}})()})),ids:[...svg.querySelectorAll('[id]')].map(n=>n.id)})''')
  assert len(d['ids'])==len(set(d['ids']));assert all(t['x']>=0 and t['x']+t['width']<=d['width'] and t['y']>=0 and t['y']+t['height']<=d['height'] for t in d['texts']),d
  boxes=fp.locator('svg').evaluate('''svg=>[...svg.querySelectorAll('text')].map(t=>{let b=t.getBBox();return {text:t.textContent,contained:[...svg.querySelectorAll('rect')].some(r=>{let q=r.getBBox();return b.x>=q.x+5&&b.x+b.width<=q.x+q.width-5&&b.y>=q.y&&b.y+b.height<=q.y+q.height})}})''')
  assert all(t['contained'] for t in boxes),boxes
  report['mechanism'].append({'step':i+1,**d});capture(page,'step-'+str(i+1),fp)
  if i<6:fp.locator('[title="下一步"]').click()
 fp.locator('[title="上一步"]').click();expect(fp.locator('.fp-count')).to_have_text('6 / 7');fp.focus();page.keyboard.press('ArrowLeft');expect(fp.locator('.fp-count')).to_have_text('5 / 7');page.keyboard.press('ArrowRight');expect(fp.locator('.fp-count')).to_have_text('6 / 7')
 fp.locator('[title="重置"]').click();fp.locator('[title="播放/暂停"]').click();expect(fp.locator('[title="播放/暂停"]')).to_have_text('⏸');fp.locator('[title="播放/暂停"]').click();expect(fp.locator('[title="播放/暂停"]')).to_have_text('▶')
 page.locator('.chapter-outline summary').click();page.locator('.chapter-outline a[href="#failure-boundary"]').click();expect(page.locator('#failure-boundary')).to_be_in_viewport()
 page.locator('.read-toggle').click();assert page.evaluate('JSON.parse(localStorage.getItem("es-web:read"))').get('ch30');page.locator('.read-toggle').click()
 specs=page.evaluate('Object.values(window.ESEXPERIMENTS)');links=page.locator('.exp-slot a').evaluate_all('(els)=>els.map(e=>e.href)');assert len(links)==20
 for spec,l in zip(specs,links):
  u=urlsplit(l);params=parse_qs(u.query);parts=[unquote(s) for s in u.fragment.removeprefix('run=').split('|')]
  assert u.path=='/console.html' and params['ep']==[spec['endpoint']] and params['am']==['anon'];assert parts[:2]==[spec['method'],spec['path']]
  assert parts[2]=='' if spec.get('body') is None else json.loads(parts[2])==spec['body']
  page.goto(l);expect(page.locator('#req-method')).to_have_value(parts[0]);expect(page.locator('#req-path')).to_have_value(parts[1]);expect(page.locator('#req-body')).to_have_value(parts[2])
 def pages_route(r):r.fulfill(response=r.fetch(url=r.request.url.replace('/es_web/','/',1)))
 ctx.route(base+'/es_web/**',pages_route);page.goto(base+'/es_web/chapters/ch30.html')
 for name in paths:
  page.locator('#diagram-ch30-'+name).scroll_into_view_if_needed();expect(page.frame_locator('#diagram-ch30-'+name).locator('.diagram-container svg[role="img"]')).to_be_visible()
 l=page.locator('.exp-slot a').first.get_attribute('href');assert l.startswith(base+'/es_web/console.html?ep=');page.goto(l);expect(page.locator('#req-path')).to_have_value('/tut-l30-docs')
 page.set_viewport_size({'width':390,'height':844})
 for theme in ['light','dark']:
  page.goto(base+'/chapters/ch30.html')
  if page.locator('html').get_attribute('data-theme')!=theme:page.locator('.theme-toggle').click()
  capture(page,'hero-mobile-'+theme)
  for name in paths:
   page.locator('#diagram-ch30-'+name).scroll_into_view_if_needed();fr=page.frame_locator('#diagram-ch30-'+name);expect(fr.locator('.diagram-container svg[role="img"]')).to_be_visible();expect(fr.locator('html')).to_have_attribute('data-theme',theme)
   if fr.locator('html').get_attribute('data-motion')=='live':fr.locator('#btn-motion').click()
   capture(page,name+'-mobile-'+theme,page.locator('#fig-ch30-'+name));fr.locator('[data-node-id]').first.click();expect(fr.locator('svg[data-focus-active]')).to_be_visible();fr.locator('#btn-focus-clear').click()
  capture(page,'experiment-mobile-'+theme,page.locator('[data-exp="ch30-06-window"]'));capture(page,'source-mobile-'+theme,page.locator('#reading-method ~ table').first)
  fp=page.locator('.fp');fp.locator('[title="重置"]').click();capture(page,'mechanism-mobile-'+theme,fp)
 reduced=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');reduced.route('http://localhost:9200/**',lambda r:r.abort());rp=reduced.new_page();rp.goto(base+'/chapters/ch30.html')
 for name in paths:
  rp.locator('#diagram-ch30-'+name).scroll_into_view_if_needed();fr=rp.frame_locator('#diagram-ch30-'+name);expect(fr.locator('html')).to_have_attribute('data-motion','still');expect(fr.locator('#btn-motion')).to_be_disabled();rp.locator('[data-replay-diagram="diagram-ch30-'+name+'"]').click();expect(fr.locator('html')).to_have_attribute('data-motion','still')
 assert rp.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto'
 rfp=rp.locator('.fp');rfp.scroll_into_view_if_needed();rp.wait_for_timeout(2600);expect(rfp.locator('.fp-count')).to_have_text('1 / 7');rfp.locator('[title="下一步"]').click();expect(rfp.locator('.fp-count')).to_have_text('2 / 7')
 reduced.close();assert not report['javascriptErrors'] and not report['failedHttp'],report
 report['functional']=['20 console deep links with anonymous endpoint and matching method/path/body','Pages prefix assets and console','node exploration and source evidence','Enter/Escape focus','pause then outer replay','keyboard replay','theme sync','standalone popup','seven contained mechanism snapshots and controls','chapter outline and read progress','mobile exploration','reduced-motion static/replay override/no autoplay/manual step/no smooth scroll','relative paths and unique IDs','no page/iframe horizontal overflow'];report['status']='pass';save();browser.close()
server.shutdown();print('PASS: 2 diagrams x 4 desktop sizes x 2 themes; chapter x 6 sizes x 2 themes; interactions and 20 deep links. ES traffic aborted; actual API separate.')
