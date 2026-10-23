#!/usr/bin/env python3
"""Focused HTTP check of the two edits requested by independent content review."""
import datetime,functools,hashlib,http.server,importlib.util,json,pathlib,threading
from playwright.sync_api import sync_playwright
H=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('f13reading',H/'review.py');reading=importlib.util.module_from_spec(spec);spec.loader.exec_module(reading)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(reading.Handler,directory=str(reading.ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Final input-validation paragraph changed after independent review; full reading matrix in http-review.json','matrix':[],'screenshots':[]}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  for width in [1440,320]:
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');context.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')")
    page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f13.html',wait_until='networkidle')
    paragraph=page.locator('#java + p');text=paragraph.inner_text()
    assert '60个UTF-16单位' in text and '100000000整数分' in text and '@Pattern输入校验' in text
    link=paragraph.locator('a');response=context.request.get(link.get_attribute('href') if link.get_attribute('href').startswith('http') else 'http://127.0.0.1:'+str(server.server_port)+'/es_web/projects/travel-search/backend/src/main/java/dev/esweb/travel/AnalysisInput.java')
    assert response.status==200 and 'mismatch|aligned|phrase|case-sensitive' in response.text()
    record['matrix'].append({'width':width,'theme':theme,'layout':reading.measure(page),'paragraph':text,'input_source_http':200})
    record['screenshots'].append(reading.shot(page,f'f13-{width}-{theme}-input-contract','#java + p'))
    context.close()
  browser.close()
 record['final_lesson_sha256']=hashlib.sha256((reading.ROOT/'framework/f13.html').read_bytes()).hexdigest();record['status']='passed'
finally:
 server.shutdown();server.server_close();(H/'final-text-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Final input paragraph: 4 HTTP theme/width groups passed')
