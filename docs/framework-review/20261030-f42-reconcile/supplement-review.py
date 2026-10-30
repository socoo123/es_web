#!/usr/bin/env python3
"""Actual navigation/expand clicks and fully opened lesson layout, limited to F42."""
import datetime,functools,http.server,importlib.util,json,pathlib,threading
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reading',D/'reading-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(m.Handler,directory=str(m.ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
 rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'views':[],'screenshots':[]}
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(executable_path=m.BROWSER,headless=True)
   for width in [1440,390,320]:
    for theme in ['light','dark']:
     ctx=browser.new_context(viewport={'width':width,'height':900});ctx.add_init_script("localStorage.setItem('es-web:theme',"+json.dumps(theme)+");")
     page=ctx.new_page();m.observe(page);page.goto(base+'framework/f42.html',wait_until='networkidle');m.images(page,theme)
     page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)');layout=m.measure(page)
     name=f'f42-{width}-{theme}-all-open.png';page.locator('#java').scroll_into_view_if_needed();page.screenshot(path=str(D/'screenshots'/name));rec['screenshots'].append('screenshots/'+name)
     page.locator('.chapter-outline a[href="#reconcile"]').click()
     m.check(page.url.endswith('#reconcile'),'TOC actual click');page.wait_for_timeout(100)
     m.check(page.locator('#reconcile').evaluate('e=>e.getBoundingClientRect().top>=document.querySelector(".topbar").getBoundingClientRect().bottom-1'),'TOC target under header')
     expanded=[]
     for i in range(2):
      fig=page.locator('figure.d2-figure').nth(i)
      with page.expect_popup() as event:fig.locator('[data-expand-d2]').click()
      popup=event.value;popup.wait_for_load_state('networkidle')
      m.check(popup.url.endswith('-'+theme+'.svg') and popup.locator('svg').count()>=1,popup.url)
      expanded.append(popup.url.split('/')[-1]);popup.close()
      if width in [1440,390]:
       name=f'f42-{width}-{theme}-full-figure-{i+1}.png';fig.screenshot(path=str(D/'screenshots'/name));rec['screenshots'].append('screenshots/'+name)
     page.locator('.pager a').first.click();page.wait_for_url('**/framework/f41.html')
     page.locator('.pager a').last.click();page.wait_for_url('**/framework/f42.html')
     page.goto(base+'framework/index.html',wait_until='networkidle');page.locator('a[data-ch="f42"]').click();page.wait_for_url('**/framework/f42.html')
     rec['views'].append({'width':width,'theme':theme,'all_details_layout':layout,'toc_click':True,'expanded_svg':expanded,'previous_next_directory_clicks':True})
     ctx.close()
   browser.close()
  m.check(not m.REC['js_errors'] and not m.REC['http_failures'] and not m.REC['request_failures'] and not m.REC['business_requests'],m.REC)
  rec.update(js_errors=m.REC['js_errors'],http_failures=m.REC['http_failures'],request_failures=m.REC['request_failures'],business_requests=m.REC['business_requests'],passed=True)
 finally:
  server.shutdown();(D/'supplement-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
 print('F42 actual TOC/pager/directory/expand clicks and all-details layouts passed')
if __name__=='__main__':main()
