#!/usr/bin/env python3
import datetime,functools,hashlib,http.server,importlib.util,json,pathlib,threading
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
spec=importlib.util.spec_from_file_location('review',D/'reading-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(m.Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'views':[],'errors':[]}
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=m.BROWSER,headless=True)
  for width in [1440,320]:
   for theme in ['light','dark']:
    c=b.new_context(viewport={'width':width,'height':900});c.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
    page=c.new_page();page.on('pageerror',lambda e:rec['errors'].append(str(e)))
    for path in ['framework/f30.html','framework/index.html','framework/f29.html']:
     page.goto(base+path,wait_until='networkidle');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
     if path=='framework/f30.html':
      m.images(page,theme);measure=m.measure(page)
      assert '75教学REST' in page.locator('.meta-line').text_content()
      assert '正式两轮均通过' in page.locator('#repeat').locator('xpath=following-sibling::p[contains(@class,"course-status")]').text_content()
      page.locator('#repeat').evaluate('e=>scrollTo({top:e.getBoundingClientRect().top+scrollY-110,behavior:"instant"})')
      pathshot=D/'screenshots'/f'final-repeat-{width}-{theme}.png';page.screenshot(path=str(pathshot))
     elif path.endswith('index.html'):
      assert page.locator('a[data-ch="f30"]').get_attribute('href')=='f30.html'
      assert 'F01–F30' in page.locator('.hero').text_content()
     else:assert page.locator('.pager a[href="f30.html"]').count()==1
     rec['views'].append({'path':path,'width':width,'theme':theme,'no_overflow':True})
    c.close()
  b.close()
finally:
 server.shutdown()
assert not rec['errors'];rec['passed']=True;rec['sha256']={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['framework/f30.html','framework/f29.html','framework/index.html']}
(D/'final-smoke.json').write_text(json.dumps(rec,indent=2)+'\n');print('Final F30 and navigation smoke passed')
