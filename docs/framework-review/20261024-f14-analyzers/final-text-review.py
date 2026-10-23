#!/usr/bin/env python3
"""Final lesson table/command checks after layout and evidence-link repairs."""
import datetime,functools,hashlib,http.server,importlib.util,json,pathlib,re,threading
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f14read',HERE/'review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
expected=json.loads((PROJECT/'search/f14/expected.json').read_text());docs=json.loads((PROJECT/'data/f14/attractions.json').read_text())
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(m.Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':[],'screenshots':[],'status':'running'}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  for width,theme in [(390,'light'),(1440,'dark')]:
   context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');context.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')")
   page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f14.html',wait_until='networkidle');m.diagrams(page,theme)
   tables=page.locator('table.ktable');assert tables.count()==5
   data=tables.nth(1).locator('tbody tr');assert data.count()==12
   for i,d in enumerate(docs):assert data.nth(i).locator('td').all_text_contents()==[d['attraction_id'],d['name'],f"{d['city_code']} / {d['status']} / {d['ticket_price_fen']}"]
   tokenrows=tables.nth(2).locator('tbody tr');hitrows=tables.nth(3).locator('tbody tr')
   for i,(name,c) in enumerate(expected.items()):
    assert tokenrows.nth(i).locator('td').all_text_contents()==[name,*[' / '.join(x[0] for x in c['tokens'][k]) for k in ['北京故宫博物院','南京市长江大桥']],c['tokens']['Ｃａｆｅ 城市咖啡馆'][0][0]]
    assert hitrows.nth(i).locator('td').all_text_contents()==[name,*[', '.join(c['queries'][k]['hits']) or '空' for k in ['palace','river','bridge','cafe']]]
   command=page.locator('pre.code-block').nth(4).text_content() # plugin setup
   assert command.index('fetch.py')<command.index('build es')<command.index('cleanup.sh')<command.index('stop es')<command.index('up -d --no-build es')
   record['groups'].append({'width':width,'theme':theme,'layout':m.measure(page),'data':'12 exact docs/values','tokens':'5 candidates × 3 displayed samples equal raw locked values','recall':'20 cells exact full ID order','commands':'download/build before destructive cleanup and node switch'})
   label='matrix' if width==390 else 'tokens';target='table.ktable';idx=3 if width==390 else 2
   p=HERE/'screenshots'/f'f14-{width}-{theme}-final-{label}.png';page.locator('.topbar').evaluate("e=>e.style.visibility='hidden'");tables.nth(idx).screenshot(path=str(p))
   record['screenshots'].append({'path':str(p.relative_to(ROOT)),'sha256':m.sha(p),'visual_review':'pending','scope':'initial horizontal position; full cells compared via DOM'})
   context.close()
  browser.close()
 record['final_lesson_sha256']=m.sha(ROOT/'framework/f14.html');record['status']='passed'
finally:
 server.shutdown();server.server_close();(HERE/'final-text-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F14 final content tables and setup order passed')
