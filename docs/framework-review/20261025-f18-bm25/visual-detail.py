#!/usr/bin/env python3
"""Supplementary readable table, explanation and single-card screenshots over real HTTP."""
import functools,hashlib,http.server,importlib.util,json,pathlib,threading,datetime
from playwright.sync_api import sync_playwright
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2]
spec=importlib.util.spec_from_file_location('f18http',H/'review.py');rev=importlib.util.module_from_spec(spec);spec.loader.exec_module(rev)
spec=importlib.util.spec_from_file_location('f18shell',H/'shell-review.py');mod=importlib.util.module_from_spec(spec)
# Do not import shell-review (its top-level execution mutates resources).
P=R/'projects/travel-search';baseinput=json.loads((P/'search/f18/input-scored.json').read_text())
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(rev.Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/es_web/'
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F18 supplementary visual inspection; no modifications to product CSS or screenshots','screenshots':[],'actual_java_requests':0,'table_row_text_checks':[]}
def shot(page,name,selector):
 p=H/'screenshots'/('detail-'+name+'.png');page.locator(selector).first.screenshot(path=str(p),timeout=20000)
 record['screenshots'].append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'pending'})
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch()
  for width,theme in [(1440,'light'),(390,'dark')]:
   c=b.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}');localStorage.setItem('travel-f18:theme','{theme}')")
   page=c.new_page();page.goto(base+'framework/f18.html',wait_until='networkidle');rev.diagrams(page,theme)
   # DOM text of the complete fixture table is checked in content-check.py, including offscreen columns.
   table=page.locator('#samples-table');record['table_row_text_checks'].append({'width':width,'theme':theme,'rows':table.locator('tr').all_text_contents()})
   page.locator('.topbar').evaluate("e=>e.style.visibility='hidden'")
   shot(page,f'{width}-{theme}-samples-left','#samples-table')
   if width==390:
    table.evaluate('e=>e.scrollLeft=e.scrollWidth');shot(page,f'{width}-{theme}-samples-right','#samples-table')
   shot(page,f'{width}-{theme}-score-table','#score-table')
   page.goto('http://127.0.0.1:18080/f18.html',wait_until='networkidle')
   for id in ['hz-short','hz-closed']:
    page.locator('[name=explainId]').select_option(id)
    with page.expect_response(lambda r:r.url.endswith('/api/attractions/score-search')) as info:page.locator('#submit').click()
    response=info.value;record['actual_java_requests']+=1;assert response.status==200;data=response.json()
    page.wait_for_function("!document.getElementById('submit').disabled")
    assert data['explainResponse']['matched']==(id=='hz-short')
    shot(page,f'{width}-{theme}-{id}-panel','.explain-panel')
    if id=='hz-short':shot(page,f'{width}-{theme}-single-card','.card')
   c.close()
  b.close()
 record['status']='passed'
finally:
 server.shutdown();server.server_close();(H/'visual-detail.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Supplementary screenshots: complete sample table DOM/left-right, score table, real card and matched/filtered panels; four extra Java requests')
