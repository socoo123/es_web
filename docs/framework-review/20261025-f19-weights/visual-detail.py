#!/usr/bin/env python3
"""Supplementary real table/right-scroll/card/unmatched-panel visual evidence."""
import datetime,functools,http.server,importlib.util,json,pathlib,threading
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
spec=importlib.util.spec_from_file_location('reading',HERE/'review.py');reading=importlib.util.module_from_spec(spec);spec.loader.exec_module(reading)
spec=importlib.util.spec_from_file_location('lab',P/'labs/f19/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(reading.Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'supplement after main HTTP and live observer checks','screenshots':[],'api_calls':0,'table_source_checks':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch();c=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce');c.add_init_script("localStorage.setItem('es-web:theme','dark');localStorage.setItem('travel-f19:theme','dark')");p=c.new_page()
 p.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f19.html',wait_until='networkidle')
 rows=p.locator('#samples-table tbody tr');docs=json.loads((P/'data/f19/attractions.json').read_text());assert rows.count()==len(docs)==12
 for n,d in enumerate(docs):
  values=rows.nth(n).locator('td').all_text_contents();assert values==[d['attraction_id'],d['name'],d['description'],f"{d['city_code']} / {d['status']} / {d['ticket_price_fen']}"]
  r['table_source_checks'].append(values)
 r['screenshots'].append(reading.shot(p,'f19-1440-dark-samples-table','#samples-table'))
 assert p.locator('#score-table tbody tr').count()==5
 r['screenshots'].append(reading.shot(p,'f19-1440-dark-score-table','#score-table'))
 p.set_viewport_size({'width':390,'height':1000});pre=p.locator('pre[data-source$="WeightSearchService.java"]').first
 moved=pre.evaluate('el=>{el.scrollLeft=el.scrollWidth;return {left:el.scrollLeft,scroll:el.scrollWidth,client:el.clientWidth}}');assert moved['left']>0;r['java_right_scroll']=moved
 r['screenshots'].append(reading.shot(p,'f19-390-dark-java-right','pre[data-source$="WeightSearchService.java"]'))
 p.goto('http://127.0.0.1:18080/f19.html',wait_until='networkidle')
 for name,inp,selector in [('optional-noise',dict(lab.load('input-optional'),explainId='hz-noise'),'.card[data-id="hz-noise"]'),('unmatched',dict(lab.load('input-zero-budget'),explainId='hz-prefix'),'.explain-panel'),('exact-card',lab.load('input-tuned'),'.card[data-id="hz-exact"]')]:
  for k in ['q','cityCode','mode','explainId']:
   e=p.locator('[name='+k+']');e.fill(inp[k]) if k=='q' else e.select_option(inp[k])
  p.locator('[name=budget]').fill(str(inp['maxPriceFen']/100));p.locator('[name=nameWeight]').fill(str(inp['nameWeight']))
  with p.expect_response(lambda q:q.url.endswith('/api/attractions/weight-search')) as info:p.locator('#submit').click()
  res=info.value;value=res.json();assert res.status==200;p.wait_for_function("!document.getElementById('submit').disabled");r['api_calls']+=1
  if name=='optional-noise':assert value['total']==9 and value['explainResponse']['matched'] and value['explainResponse']['explanation']['value']==0
  if name=='unmatched':assert value['total']==1 and not value['explainResponse']['matched'] and '不是候选得分' in p.locator('#explain-note').text_content()
  if name=='exact-card':assert value['items'][0]['id']=='hz-exact'
  r['screenshots'].append(reading.shot(p,'shell-390-dark-'+name,selector))
  r[name]={'input':inp,'response':value}
 c.close();b.close()
server.shutdown();r['status']='passed';(HERE/'visual-detail.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
