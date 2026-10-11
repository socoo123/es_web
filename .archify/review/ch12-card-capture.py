"""Recapture a tall mobile card without sticky-header screenshot artifacts.
Only viewport height changes; width, chapter and request bytes stay unchanged.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import threading,json,hashlib
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844})
 for theme in ['light','dark']:
  page.goto(f'http://127.0.0.1:{server.server_port}/chapters/ch12.html')
  if page.locator('html').get_attribute('data-theme')!=theme:page.locator('.theme-toggle').click()
  card=page.locator('[data-exp="ch12-05-pipeline-failure-inline"]')
  page.set_viewport_size({'width':390,'height':int(card.bounding_box()['height'])+200})
  card.evaluate('(e)=>e.scrollIntoView({block:"start"})');page.evaluate('scrollBy(0,-100)');page.wait_for_timeout(300)
  card.screenshot(path=str(out/('ch12-experiment-mobile-'+theme+'.png')))
  page.set_viewport_size({'width':390,'height':844})
 browser.close()
server.shutdown()
report={'kind':'focused-mobile-card-capture','chapterSha256':hashlib.sha256((root/'chapters/ch12.html').read_bytes()).hexdigest(),'experimentSha256':hashlib.sha256((root/'experiments/ch12.js').read_bytes()).hexdigest(),'viewportWidth':390,'captures':['ch12-experiment-mobile-light.png','ch12-experiment-mobile-dark.png'],'reason':'remove sticky-header artifact in tall locator screenshot; no chapter change','realEsApi':'not-run'}
(out/'ch12-card-capture.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Recaptured two mobile card images at unchanged 390px width.')
