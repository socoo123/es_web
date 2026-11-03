import functools, http.server, json, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/catalog-review/20261103'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/framework/index.html'
report={'views':[],'errors':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=str(Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
 for width in [1440,390,320]:
  for theme in ['light','dark']:
   page=browser.new_page(viewport={'width':width,'height':1000}, reduced_motion='reduce')
   page.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+"); localStorage.setItem('es-web:read',JSON.stringify({'f01-v2':true}));")
   page.on('pageerror',lambda e:report['errors'].append(str(e)))
   page.on('response',lambda r:report['errors'].append(str(r.status)+' '+r.url) if r.status>=400 else None)
   page.goto(base,wait_until='networkidle')
   assert page.locator('.curriculum-lesson-link').count()==45
   assert page.locator('.curriculum-lesson-link.is-read').count()==1
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
   page.screenshot(path=str(OUT/f'screenshots/{width}-{theme}-top.png'))
   page.goto(base+'#stage-1',wait_until='networkidle')
   assert page.locator('.curriculum-nav a[aria-current]').get_attribute('href')=='#stage-1'
   assert page.locator('#stage-1').evaluate('(e)=>e.getBoundingClientRect().top') >= page.locator('.topbar').evaluate('(e)=>e.getBoundingClientRect().bottom')
   page.screenshot(path=str(OUT/f'screenshots/{width}-{theme}-stage1.png'))
   page.locator('#stage-1 summary').first.click()
   assert page.locator('#stage-1 details').first.get_attribute('open') is not None
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
   page.locator('#stage-1 .stage-top').click()
   page.locator('.curriculum-nav a[href="#stage-7"]').click()
   page.wait_for_timeout(100)
   assert page.locator('.curriculum-nav a[aria-current]').get_attribute('href')=='#stage-7'
   page.locator('.theme-toggle').click()
   assert page.locator('html').get_attribute('data-theme') != theme
   report['views'].append({'width':width,'theme':theme,'anchors':'passed','overflow':False,'details':'passed','read-marker':'passed','theme-toggle':'passed'})
   page.close()
 browser.close()
server.shutdown()
assert not report['errors'],report['errors']
(OUT/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
