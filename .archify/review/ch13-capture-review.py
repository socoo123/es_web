"""Repair lazy-frame captures; wait for the actual SVG and fonts before capture.
Chapter, registry, JSON and generated HTML remain unchanged. No ES requests.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import threading,json,hashlib,shutil
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
history=out/'ch13-before-capture-repair';history.mkdir(exist_ok=True)
names=['ch13-replication-waits-mobile-'+t+'.png' for t in ['light','dark']]
before={}
for name in names:
 dest=history/name
 if not dest.exists():shutil.copyfile(out/name,dest)
 before[name]=sha(dest)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844})
 for theme,name in zip(['light','dark'],names):
  page.goto(f'http://127.0.0.1:{server.server_port}/chapters/ch13.html')
  if page.locator('html').get_attribute('data-theme')!=theme:page.locator('.theme-toggle').click()
  fig=page.locator('#fig-ch13-replication-waits');fig.scroll_into_view_if_needed()
  fr=page.frame_locator('#diagram-ch13-replication-waits')
  expect(fr.locator('.diagram-container svg[role="img"]')).to_be_visible()
  expect(fr.locator('html')).to_have_attribute('data-theme',theme)
  fr.locator('html').evaluate('e=>e.ownerDocument.fonts.ready')
  if fr.locator('html').get_attribute('data-motion')=='live':fr.locator('#btn-motion').click()
  page.set_viewport_size({'width':390,'height':int(fig.bounding_box()['height'])+200})
  fig.evaluate('(e)=>e.scrollIntoView({block:"start"})');page.evaluate('scrollBy(0,-100)')
  page.wait_for_timeout(300)
  panel=fr.locator('.diagram-container').bounding_box();nodes=fr.locator('.diagram-container svg[role="img"] [data-node-id]')
  assert nodes.count()==5
  for j in range(5):
   n=nodes.nth(j).bounding_box()
   assert n and n['width']>0 and n['height']>0 and n['x']>=panel['x']-1 and n['x']+n['width']<=panel['x']+panel['width']+1 and n['y']>=panel['y']-1 and n['y']+n['height']<=panel['y']+panel['height']+1
  fig.screenshot(path=str(out/name))
  rows.append({'theme':theme,'capture':name,'width':390,'svgVisible':True,'fontReady':True,'nodesContained':5,'beforeSha256':before[name],'afterSha256':sha(out/name)})
  page.set_viewport_size({'width':390,'height':844})
 browser.close()
server.shutdown()
report={'status':'pass','kind':'focused-lazy-frame-capture-repair','reason':'initial locator capture ran before lazy iframe had a visible SVG; actual interaction checks already passed','chapterSha256':sha(root/'chapters/ch13.html'),'experimentSha256':sha(root/'experiments/ch13.js'),'rows':rows,'realEsApi':'not-run','visualReview':'requires-actual-image-inspection'}
(out/'ch13-capture-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: two lazy-frame mobile captures now have visible SVG, ready fonts and all five nodes at unchanged 390px width.')
