"""Capture all seven complete mechanism snapshots for actual visual review."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,hashlib
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
rows=[]
with sync_playwright() as p:
 b=p.chromium.launch();ctx=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 ctx.route('http://localhost:9200/**',lambda r:r.abort());page=ctx.new_page();page.goto('http://127.0.0.1:'+str(server.server_port)+'/chapters/ch27.html');fp=page.locator('.fp');fp.scroll_into_view_if_needed()
 if page.locator('html').get_attribute('data-theme')!='light':page.locator('.theme-toggle').click()
 fp.locator('[title="重置"]').click()
 for n in range(1,8):
  expect(fp.locator('.fp-count')).to_have_text(f'{n} / 7');page.wait_for_timeout(300)
  path=out/f'ch27-step-{n:02}-light.png';fp.screenshot(path=str(path));rows.append({'step':n,'capture':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
  if n<7:fp.locator('[title="下一步"]').click()
 b.close()
server.shutdown();r={'status':'pass','kind':'mechanism-snapshot-capture','visualReview':'pending actual image inspection','experimentSha256':hashlib.sha256((root/'experiments/ch27.js').read_bytes()).hexdigest(),'captures':rows}
(out/'ch27-mechanism-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('PASS: captured seven complete snapshots; visual review recorded separately.')
