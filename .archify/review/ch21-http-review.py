"""Actual HTTP/Chrome checks and captures; ES requests are aborted here, tested separately."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
import threading,json,hashlib
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent;screens=out/'ch21-screens';screens.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Tags(HTMLParser):
 def __init__(self):super().__init__();self.frames=[];self.links=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='iframe':self.frames.append(a)
  if tag in ['a','link','script']:
   link=a.get('href') or a.get('src')
   if link:self.links.append(link)
parser=Tags();parser.feed((root/'chapters/ch21.html').read_text());assert len(parser.ids)==len(set(parser.ids))
for link in parser.links:
 u=urlsplit(link)
 if u.scheme or u.netloc:continue
 target=(root/'chapters'/unquote(u.path)).resolve() if u.path else root/'chapters/ch21.html'
 assert target.is_file(),link
 if target.name=='ch21.html' and u.fragment:assert u.fragment in parser.ids,link
artifacts=[(f['id'].removeprefix('diagram-ch21-'),(root/'chapters'/urlsplit(f['src']).path).resolve()) for f in parser.frames]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
report={'status':'running','kind':'independent-http-review','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'chapterSha256':sha(root/'chapters/ch21.html'),'experimentSha256':sha(root/'experiments/ch21.js'),'artifacts':[],'chapterLayouts':[],'interactions':[],'javascriptErrors':[],'failedHttp':[],'captures':[],'realEsApi':'separate ch21-es-review.json','nativeBrowserGate':'separate native finalizer receipts'}
def save():(out/'ch21-http-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
def capture(page,name,locator=None):
 page.wait_for_timeout(300);dest=screens/(name+'.png');viewport=page.viewport_size
 if locator:
  box=locator.bounding_box()
  if box['height']>viewport['height']-100:page.set_viewport_size({'width':viewport['width'],'height':int(box['height'])+200})
  locator.evaluate('(e)=>e.scrollIntoView({block:"start"})');page.evaluate('scrollBy(0,-90)');locator.screenshot(path=str(dest));page.set_viewport_size(viewport)
 else:page.screenshot(path=str(dest),full_page='standalone' in name)
 report['captures'].append(str(dest.relative_to(out)));save()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 ctx=browser.new_context(viewport={'width':1440,'height':1000});ctx.route('http://localhost:9200/**',lambda route:route.abort());ctx.route('http://localhost:9201/**',lambda route:route.abort())
 page=ctx.new_page();page.on('pageerror',lambda e:report['javascriptErrors'].append(str(e)));page.on('response',lambda r:report['failedHttp'].append({'url':r.url,'status':r.status}) if r.status>=290 else None)
 for name,path in artifacts:
  row={'id':name,'path':str(path.relative_to(root)),'htmlSha256':sha(path),'sourceSha256':sha(path.with_name('candidate.json')),'sizes':[]};report['artifacts'].append(row)
  for theme in ['light','dark']:
   for width,height in [(1440,900),(1600,1000),(1920,1080),(2048,1320)]:
    page.set_viewport_size({'width':width,'height':height});assert page.goto(base+'/'+row['path']+'?theme='+theme).status==200
    expect(page.locator('.diagram-container svg[role="img"]')).to_be_visible();expect(page.locator('html')).to_have_attribute('data-theme',theme);page.evaluate('document.fonts.ready')
    dim=page.evaluate('''()=>{let ts=[...document.querySelectorAll('.diagram-container svg text')].filter(e=>e.getClientRects().length&&getComputedStyle(e).display!=='none');let proj=e=>parseFloat(getComputedStyle(e).fontSize)*Math.hypot(e.getScreenCTM().a,e.getScreenCTM().b);return {width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,scrollHeight:document.documentElement.scrollHeight,minimumSvgTextPx:Math.min(...ts.map(proj)),minimumNodeTextPx:Math.min(...ts.filter(e=>e.closest('[data-node-id]')&&!e.textContent.startsWith('来源 ')).map(proj)),cards:[...document.querySelectorAll('.cards .card')].map(e=>({height:e.clientHeight,scroll:e.scrollHeight}))}}''')
    assert dim['scrollWidth']<=width and dim['minimumSvgTextPx']>=6 and dim['minimumNodeTextPx']>=7,(name,dim)
    assert len(dim['cards'])==2 and all(c['scroll']<=c['height']+1 for c in dim['cards']),(name,dim)
    row['sizes'].append({'theme':theme,**dim});save()
    if width==1440:
     if page.locator('html').get_attribute('data-motion')=='live':page.locator('#btn-motion').click()
     capture(page,name+'-standalone-'+theme)
 for theme in ['light','dark']:
  for width,height in [(1920,1080),(1440,1000),(1024,900),(768,900),(390,844),(320,800)]:
   page.set_viewport_size({'width':width,'height':height});assert page.goto(base+'/chapters/ch21.html').status==200
   if page.locator('html').get_attribute('data-theme')!=theme:page.locator('.theme-toggle').click()
   for name,_ in artifacts:
    page.locator('#diagram-ch21-'+name).scroll_into_view_if_needed();fr=page.frame_locator('#diagram-ch21-'+name)
    expect(fr.locator('.diagram-container svg[role="img"]')).to_be_visible();expect(fr.locator('html')).to_have_attribute('data-theme',theme);fr.locator('html').evaluate('e=>e.ownerDocument.fonts.ready')
   dim=page.evaluate('''()=>{let boxes=[...document.querySelectorAll('.ch-header,.goal,.lesson>h2,.lesson>p,.archify-shell,.archify-figure figcaption,.ktable,.exp-slot,.drills,.pitfalls,.recap,.ch-footer')].map(e=>({kind:e.className||e.tagName,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width}));let frames=[...document.querySelectorAll('.archify-frame')].map(f=>({id:f.id,width:f.clientWidth,height:f.clientHeight,scrollWidth:f.contentDocument.documentElement.scrollWidth,scrollHeight:f.contentDocument.documentElement.scrollHeight,panel:f.contentDocument.querySelector('.diagram-container').getBoundingClientRect().toJSON(),nodes:[...f.contentDocument.querySelectorAll('.diagram-container svg[role="img"] [data-node-id]')].map(n=>({id:n.getAttribute('data-node-id'),...n.getBoundingClientRect().toJSON()}))}));return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,boxes,frames}}''')
   report['chapterLayouts'].append({'theme':theme,**dim});save()
   assert dim['scrollWidth']<=width and dim['boxes'][0]['width']<=880,(width,dim['scrollWidth'])
   for box in dim['boxes']:assert abs(box['left']-dim['boxes'][0]['left'])<=1 and abs(box['right']-dim['boxes'][0]['right'])<=1,(width,box)
   for f in dim['frames']:
    assert f['scrollWidth']<=f['width'] and f['scrollHeight']<=f['height'],(width,f)
    panel=f['panel']
    for n in f['nodes']:assert n['x']>=panel['x']-1 and n['right']<=panel['right']+1 and n['y']>=panel['y']-1 and n['bottom']<=panel['bottom']+1,(width,n,panel)
   if width in [1440,390]:
    page.evaluate('scrollTo(0,0)');capture(page,'hero-'+str(width)+'-'+theme)
    for name,_ in artifacts:
     fr=page.frame_locator('#diagram-ch21-'+name)
     if fr.locator('html').get_attribute('data-motion')=='live':fr.locator('#btn-motion').click()
     capture(page,name+'-embedded-'+str(width)+'-'+theme,page.locator('#fig-ch21-'+name))
    if width==390:
     capture(page,'experiment-mobile-'+theme,page.locator('[data-exp="ch21-13-two-counters"]'))
     capture(page,'source-table-mobile-'+theme,page.locator('#source-map+table'))
 report['interactions'].append('four standalone widths × two themes; six chapter widths × two themes; reading width <=880 and edges <=1px; page/iframe/nodes contained');save()
 page.set_viewport_size({'width':1440,'height':1000});page.goto(base+'/chapters/ch21.html');expect(page.locator('.exp-slot .exp')).to_have_count(29);expect(page.locator('[data-replay-diagram]')).to_have_count(1);expect(page.locator('.fp-slot')).to_have_count(0)
 for name,_ in artifacts:
  page.locator('#diagram-ch21-'+name).scroll_into_view_if_needed();fr=page.frame_locator('#diagram-ch21-'+name)
  node=fr.locator('[data-node-id]').first;node.click();expect(fr.locator('svg[data-focus-active]')).to_be_visible()
  links=fr.locator('a[href*="/blob/"]').evaluate_all('(els)=>els.map(e=>e.href)');assert any('/2e8528e92361c3399724226deaf2b46f933e925b/' in link for link in links)
  fr.locator('#btn-focus-clear').click();page.mouse.move(2,2);expect(fr.locator('svg[data-focus-active]')).to_have_count(0)
  # Keyboard focus and Enter can select a node; Escape closes viewer overlays.
  node.focus();page.keyboard.press('Enter');expect(fr.locator('svg[data-focus-active]')).to_be_visible();page.keyboard.press('Escape');expect(fr.locator('svg[data-focus-active]')).to_have_count(0)
  full_link=page.locator('#fig-ch21-'+name+' .archify-actions a');assert full_link.get_attribute('target')=='_blank'
  with page.expect_popup() as pop:full_link.click()
  popup=pop.value;popup.wait_for_load_state();assert 'present=' not in popup.url;expect(popup.locator('.diagram-container svg[role="img"]')).to_be_visible();popup.close()
 fr=page.frame_locator('#diagram-ch21-publication-apply');replay=page.locator('[data-replay-diagram]');replay.click();expect(fr.locator('html')).to_have_attribute('data-motion','live');fr.locator('#btn-motion').click();expect(fr.locator('html')).to_have_attribute('data-motion','still');replay.click();expect(fr.locator('html')).to_have_attribute('data-motion','live');replay.focus();page.keyboard.press('Enter');expect(fr.locator('html')).to_have_attribute('data-motion','live')
 static=page.frame_locator('#diagram-ch21-snapshot-parts');assert static.locator('html').get_attribute('data-motion') in [None,'still'];assert not static.locator('#btn-motion').is_visible()
 theme=page.locator('html').get_attribute('data-theme');page.locator('.theme-toggle').click()
 for name,_ in artifacts:expect(page.frame_locator('#diagram-ch21-'+name).locator('html')).to_have_attribute('data-theme','dark' if theme=='light' else 'light')
 page.locator('.chapter-outline summary').click();page.locator('.chapter-outline a[href="#memory"]').click();assert page.evaluate('location.hash')=='#memory';expect(page.locator('#memory')).to_be_in_viewport()
 page.locator('.read-toggle').click();assert page.evaluate('JSON.parse(localStorage.getItem("es-web:read"))').get('ch21');page.locator('.read-toggle').click()
 report['interactions'].append('exploration/source links/close/keyboard/expand/theme sync; static has no motion control; trace pause→outer replay and Enter; outline and read progress');save()
 specs=page.evaluate('Object.values(window.ESEXPERIMENTS)');links=page.locator('.exp-slot a').evaluate_all('(els)=>els.map(e=>e.href)');assert len(links)==len(specs)==29
 for i,link in enumerate(links):
  parts=[unquote(s) for s in urlsplit(link).fragment.removeprefix('run=').split('|')];spec=specs[i];assert spec['method']==parts[0] and spec['path']==parts[1];assert parts[2]=='' if spec.get('body') is None else json.loads(parts[2])==spec['body']
  page.goto(base+'/chapters/ch21.html');page.locator('.exp-slot a').nth(i).click();page.wait_for_url('**/console.html#run=*');expect(page.locator('#req-method')).to_have_value(parts[0]);expect(page.locator('#req-path')).to_have_value(parts[1]);expect(page.locator('#req-body')).to_have_value(parts[2])
 page.goto(base+'/chapters/ch21.html');extra=page.evaluate('ESClient.consoleLink("POST","/_example","raw\\n",{endpoint:"http://localhost:9201",authMode:"anon",allowInvalid:true})');assert 'ep=http%3A%2F%2Flocalhost%3A9201' in extra and 'am=anon' in extra and 'raw=1' in extra
 def pages_route(route):
  response=route.fetch(url=route.request.url.replace('/es_web/','/',1));route.fulfill(response=response)
 ctx.route(base+'/es_web/**',pages_route);page.goto(base+'/es_web/chapters/ch21.html')
 for name,_ in artifacts:
  page.locator('#diagram-ch21-'+name).scroll_into_view_if_needed();expect(page.frame_locator('#diagram-ch21-'+name).locator('.diagram-container svg[role="img"]')).to_be_visible()
 link=page.locator('.exp-slot a').first.get_attribute('href');assert link.startswith(base+'/es_web/console.html#run=');page.goto(link);expect(page.locator('#req-path')).to_have_value(specs[0]['path'])
 report['interactions'].append('29 actual console navigations method/path/body; endpoint/auth alias/raw; /es_web/ relative asset and console paths; .nojekyll exists');assert (root/'.nojekyll').exists();save()
 for width in [390,320]:
  page.set_viewport_size({'width':width,'height':844});page.goto(base+'/chapters/ch21.html')
  for name,_ in artifacts:
   page.locator('#diagram-ch21-'+name).scroll_into_view_if_needed();fr=page.frame_locator('#diagram-ch21-'+name);fr.locator('[data-node-id]').first.click();expect(fr.locator('svg[data-focus-active]')).to_be_visible();fr.locator('#btn-focus-clear').click()
  table=page.locator('#source-map+table');dims=table.evaluate('(e)=>{e.scrollLeft=100;return {scroll:e.scrollLeft,client:e.clientWidth,total:e.scrollWidth}}');assert dims['total']<=dims['client'] or dims['scroll']>0,dims;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 reduced=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');reduced.route('http://localhost:9200/**',lambda route:route.abort());rp=reduced.new_page();rp.goto(base+'/chapters/ch21.html')
 for name,_ in artifacts:
  rp.locator('#diagram-ch21-'+name).scroll_into_view_if_needed();expect(rp.frame_locator('#diagram-ch21-'+name).locator('.diagram-container svg[role="img"]')).to_be_visible();assert rp.frame_locator('#diagram-ch21-'+name).locator('html').get_attribute('data-motion') in [None,'still']
 rfr=rp.frame_locator('#diagram-ch21-publication-apply');expect(rfr.locator('#btn-motion')).to_be_disabled();rp.locator('[data-replay-diagram]').click();expect(rfr.locator('html')).to_have_attribute('data-motion','still');assert rp.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto'
 report['interactions'].append('390/320 node exploration and contained table scroll; reduced motion overrides replay and disables smooth scrolling');assert not report['javascriptErrors'] and not report['failedHttp'],report
 report['status']='pass';save();print('PASS: HTTP layouts/interactions,',len(report['captures']),'captures awaiting actual visual review.');browser.close()
server.shutdown()
