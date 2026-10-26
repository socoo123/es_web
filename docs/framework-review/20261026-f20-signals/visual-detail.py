"""F20 targeted table/code/one-card/explanation inspection after matrix validation."""
import math,traceback,datetime,functools,hashlib,http.server,importlib.util,json,pathlib,threading
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
httpcheck=module('f20http',HERE/'review.py')
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'targeted readable table/code/card/explanation screenshots, separate from complete matrix','screenshots':[],'api_calls':0,'checks':[]}
def shot(page,name,selector):
 p=HERE/'screenshots'/(name+'.png');page.locator(selector).first.screenshot(path=str(p));record['screenshots'].append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'pending'})
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(httpcheck.Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch();c=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce',permissions=['clipboard-read','clipboard-write']);c.add_init_script("localStorage.setItem('es-web:theme','dark');localStorage.setItem('travel-f20:theme','dark')");p=c.new_page();p.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f20.html',wait_until='networkidle')
  docs=json.loads((P/'data/f20/attractions.json').read_text());table=p.locator('#samples-table tbody tr');assert table.count()==11
  for i,d in enumerate(docs):
   cells=table.nth(i).locator('td').all_text_contents();assert cells[0]==d['attraction_id'] and cells[1]==d['description']
   def val(k):return '缺失' if k not in d else str(d[k])
   assert cells[2]==val('review_avg')+' / '+val('review_count')
   assert cells[3]==('缺失' if 'quality_score' not in d else f"{d['quality_score']:.6f}")+' / '+val('hot_30d')
   assert cells[4]==f"{d['ticket_price_fen']} / {d['city_code']} / {d['status']}"
  ranks=json.loads((P/'review/f20/ranking-summary.json').read_text());rows=p.locator('#ranking-table tbody tr');assert rows.count()==6
  for row in rows.all():
   cells=row.locator('td').all_text_contents();assert cells[1]==' / '.join(x['id'].removeprefix('hz-') for x in ranks[cells[0]])
  record['checks']+=['11 sample table rows/columns exactly match fixed source','six complete order rows match actual two-round summary']
  p.locator('.topbar').evaluate("e=>e.style.visibility='hidden'")
  shot(p,'f20-1440-dark-samples-table','#samples-table');shot(p,'f20-1440-dark-ranking-table','#ranking-table')
  p.set_viewport_size({'width':390,'height':1000});code=p.locator('pre[data-source$="SignalSearchService.java"]').first
  shot(p,'f20-390-dark-java-left','pre[data-source$="SignalSearchService.java"]');code.evaluate('e=>e.scrollLeft=e.scrollWidth');assert code.evaluate('e=>e.scrollLeft')>0
  shot(p,'f20-390-dark-java-right','pre[data-source$="SignalSearchService.java"]')
  table=p.locator('#samples-table');table.evaluate('e=>e.scrollLeft=e.scrollWidth');assert table.evaluate('e=>e.scrollLeft')>0;shot(p,'f20-390-dark-samples-right','#samples-table')
  record['checks'].append('narrow Java/table actual horizontal scroll succeeds; full text in DOM and clipboard covered separately')
  p.goto('http://127.0.0.1:18080/f20.html',wait_until='networkidle')
  def submit(mode,id):
   p.locator('[name=mode]').select_option(mode);p.locator('[name=explainId]').select_option(id)
   with p.expect_response(lambda r:r.url.endswith('/api/attractions/signal-search')) as info:p.locator('#submit').click()
   r=info.value;assert r.status==200;record['api_calls']+=1;p.wait_for_function("!document.getElementById('submit').disabled");return r.json()
  r=submit('bounded','hz-hot');assert r['items'][4]['id']=='hz-hot'
  shot(p,'shell-390-dark-hot-card','.card[data-id="hz-hot"]');shot(p,'shell-390-dark-missing-card','.card[data-id="hz-missing"]')
  p.locator('.explain-panel details summary').click();shot(p,'shell-390-dark-hot-explain','.explain-panel')
  r=submit('rank','hz-missing');assert r['explainResponse']['matched'];assert math.isclose(r['explainResponse']['explanation']['value'],next(x['score'] for x in r['items'] if x['id']=='hz-missing'),rel_tol=2e-6,abs_tol=1e-7)
  shot(p,'shell-390-dark-missing-feature','.explain-panel')
  r=submit('bounded','hz-closed');assert not r['explainResponse']['matched'] and r['explainResponse']['explanation']['value']==0
  shot(p,'shell-390-dark-unmatched','.explain-panel')
  record['checks']+=['weak hot one-card and missing/zero distinction visible','actual bounded hot and rank missing full explanations','unmatched closed root0 distinct from child contribution'];c.close();b.close()
 record['status']='passed'
except Exception:
 record['status']='failed';record['failure']=traceback.format_exc();raise
finally:
 server.shutdown();server.server_close();(HERE/'visual-detail.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F20 detail passed: 11 source rows, six orders, narrow code/table scroll, three actual Java calls')
