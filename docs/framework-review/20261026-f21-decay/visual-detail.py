"""F21 targeted samples/orders/code/card/explanation after full live matrices."""
import datetime,functools,hashlib,http.server,importlib.util,json,pathlib,threading,traceback
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
s=importlib.util.spec_from_file_location('f21http',HERE/'review.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'targeted table/card/code/complete query explanations; full HTTP and live matrices separately recorded','screenshots':[],'api_calls':0,'checks':[]}
def shot(page,name,selector):
 path=HERE/'screenshots'/(name+'.png');page.locator(selector).first.screenshot(path=str(path));r['screenshots'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_review':'pending'})
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(h.Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch();c=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');c.add_init_script("localStorage.setItem('es-web:theme','dark');localStorage.setItem('travel-f21:theme','dark')");p=c.new_page();p.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f21.html',wait_until='networkidle')
  docs={d['attraction_id']:d for d in json.loads((P/'data/f21/attractions.json').read_text())};rows=p.locator('#samples-table tbody tr');assert rows.count()==11
  for row in rows.all()[:10]:
   cells=row.locator('td').all_text_contents();d=docs['hz-'+cells[0]];assert float(cells[3])==d['ticket_price_fen']/100
   if d['attraction_id'] in ['hz-missing','hz-no-geo']:assert '缺坐标' in cells[1]
   if d['attraction_id'] in ['hz-missing','hz-no-date']:assert cells[2]=='缺日期'
  grouped=rows.nth(10).locator('td').all_text_contents();assert grouped[0]=='closed / expensive / sz-near / future' and grouped[3]=='0 / 120 / 10 / 0'
  for table in ['ranking-table','sort-table']:
   ranks=json.loads((P/'review/f21/ranking-summary.json').read_text())
   for row in p.locator('#'+table+' tbody tr').all():
    cells=row.locator('td').all_text_contents();key={'价格升序':'price','距离升序':'distance','sum且硬半径10km':'radius'}.get(cells[0],cells[0])
    assert cells[1]==' / '.join(x['id'].removeprefix('hz-') for x in ranks[key]),(cells,key)
  r['checks']+=['11 sample rows: each individual price/missing state and grouped eligibility/price labels match fixed contract','six scoring orders and three sort/radius orders match actual two-round summary']
  p.locator('.topbar').evaluate("e=>e.style.visibility='hidden'")
  for name in ['samples-table','ranking-table','sort-table']:shot(p,'f21-1440-dark-'+name,'#'+name)
  p.set_viewport_size({'width':390,'height':1000});code=p.locator('pre[data-source$="DecaySearchService.java"]').first;code.evaluate('e=>e.scrollLeft=0');shot(p,'f21-390-dark-java-left','pre[data-source$="DecaySearchService.java"]');code.evaluate('e=>e.scrollLeft=e.scrollWidth');assert code.evaluate('e=>e.scrollLeft')>0;shot(p,'f21-390-dark-java-right','pre[data-source$="DecaySearchService.java"]')
  table=p.locator('#samples-table');table.evaluate('e=>e.scrollLeft=e.scrollWidth');assert table.evaluate('e=>e.scrollLeft')>0;shot(p,'f21-390-dark-samples-right','#samples-table');r['checks'].append('actual narrow Java/table scroll to right works; complete snippets also copied in HTTP matrix')
  p.goto('http://127.0.0.1:18081/f21.html',wait_until='networkidle')
  def submit(mode,id,sort='relevance'):
   p.locator('[name=mode]').select_option(mode);p.locator('[name=explainId]').select_option(id);p.locator('[name=sortMode]').select_option(sort)
   with p.expect_response(lambda v:v.url.endswith('/api/attractions/decay-search')) as info:p.locator('#submit').click()
   v=info.value;assert v.status==200;r['api_calls']+=1;p.wait_for_function("!document.getElementById('submit').disabled");return v.json()
  value=submit('sum','hz-far');assert value['items'][0]['id']=='hz-near' and value['items'][2]['id']=='hz-weak'
  for id in ['hz-far','hz-weak','hz-missing']:shot(p,'shell-390-dark-'+id+'-card','.card[data-id="'+id+'"]')
  p.locator('.explain-panel details summary').click();shot(p,'shell-390-dark-far-explain','.explain-panel')
  value=submit('multiply','hz-missing');assert value['explainResponse']['matched'] and value['explainResponse']['explanation']['value']==0;shot(p,'shell-390-dark-missing-zero','.explain-panel')
  value=submit('sum','hz-missing','distance');card=next(v for v in value['items'] if v['id']=='hz-missing');assert card['distanceKm'] is None and card['sortValues'][0]=='Infinity';p.set_viewport_size({'width':320,'height':1000});shot(p,'shell-320-dark-infinity-card','.card[data-id="hz-missing"]')
  value=submit('sum','hz-closed');assert not value['explainResponse']['matched'] and value['explainResponse']['explanation']['value']==0;shot(p,'shell-320-dark-unmatched','.explain-panel')
  r['checks']+=['actual sum far/weak/missing cards and complete far explanation','multiply missing matched=true with zero score distinct from unmatched','distance missing null with full sort Infinity at320px','closed full query matched=false/root0']
  c.close();b.close()
 r['status']='passed'
except Exception:
 r['status']='failed';r['failure']=traceback.format_exc();raise
finally:
 server.shutdown();server.server_close();(HERE/'visual-detail.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('F21 targeted table/order/code/card checks passed; four actual Java calls')
