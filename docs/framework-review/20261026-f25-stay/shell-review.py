#!/usr/bin/env python3
"""Real browser -> Java -> ES; fixed manual totals and recoverable failures."""
import datetime, hashlib, importlib.util, json, os, pathlib, subprocess, sys, traceback, urllib.request
from playwright.sync_api import sync_playwright
import reading_helpers as h
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2]
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('lab',R/'projects/travel-search/labs/f25/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
BASE='http://127.0.0.1:18081';ES='http://127.0.0.1:19225';INDEX='tut-f25-offers'
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'matrix':[],'calls':[],'mutations':[],'screenshots':[],'js_errors':[],'direct_ES_requests':[],'unexpected_http':[]}
def require(ok,msg):
 if not ok:raise AssertionError(msg)
def es(method,path,body=None,status=200):
 raw=json.dumps(body).encode() if body is not None else None
 req=urllib.request.Request(ES+path,data=raw,method=method,headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=20) as response: actual=response.status;value=json.load(response)
 except __import__('urllib.error').error.HTTPError as e:actual=e.code;value=json.load(e)
 rec['mutations'].append(dict(method=method,path=path,body=body,status=actual,response=value));require(actual==status,'mutation status');return value
def shot(page,name,selector=None):
 p=HERE/'screenshots'/(name+'.png');p.parent.mkdir(exist_ok=True)
 if selector:page.locator(selector).screenshot(path=str(p))
 else:page.screenshot(path=str(p))
 rec['screenshots'].append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_review='pending'))
def submit(page,expected_status=200):
 with page.expect_response(lambda r:r.url==BASE+'/api/stay/inspect') as info:page.locator('#submit').click()
 response=info.value;value=response.json();page.wait_for_function("!document.getElementById('submit').disabled")
 rec['calls'].append(dict(status=response.status,input=response.request.post_data_json,response=value))
 require(response.status==expected_status,dict(expected=expected_status,actual=response.status,value=value))
 if expected_status!=200:
  require(page.locator('.card').count()==0 and page.locator('#total').inner_text()=='等待观察','failure clears old results')
  require(all(page.locator('#'+id).text_content()=='尚无本轮结果' for id in ['input-json','dsl-json','result-json']),'failure clears raw')
  require(str(expected_status) in page.locator('#status').inner_text(),'visible status')
 return value
def check(page,name):
 r=submit(page);expected=lab.EXPECTED[name]
 require(r['candidateTotal']==8 and r['acceptedTotal']==len(expected),'candidate and accepted totals')
 require({d['offerId']:d['totalMinor'] for d in r['decisions'] if d['reason']=='ACCEPTED'}==expected,'manual accepted amount constants')
 require({d['offerId']:d['reason'] for d in r['decisions'] if d['reason']!='ACCEPTED'}==lab.REASONS[name],'manual rejection constants')
 require(json.loads(page.locator('#result-json').text_content())==r and json.loads(page.locator('#dsl-json').text_content())==r['esRequest'],'raw exact typed result/DSL')
 require(json.loads(page.locator('#input-json').text_content())==r['conditions'],'input exact')
 require(page.locator('.card').count()==8 and page.locator('.card[data-accepted="true"]').count()==len(expected),'all candidate cards')
 for d in r['decisions']:
  card=page.locator('.card[data-id="'+d['offerId']+'"]');text=card.inner_text()
  require(all(v in text for v in [d['offerId'],d['hotelId'],d['roomId'],d['hotelName'],d['planId'],d['currency'],d['reason'],r['snapshotId']]),'identity and outcome')
  rows=card.locator('tbody tr');require(rows.count()==len(d['nights']),'all nights shown')
  for idx,n in enumerate(d['nights']):
   values=rows.nth(idx).locator('td').all_text_contents()
   require(values==[n['date'],'缺晚' if n['availableRooms'] is None else str(n['availableRooms']),'缺价' if n['priceMinor'] is None else 'CNY '+format(n['priceMinor']/100,'.2f'),'—' if n['minStayArrival'] is None else str(n['minStayArrival'])],'every nightly cell')
  if d['totalMinor'] is not None:require('CNY '+format(d['totalMinor']/100,'.2f') in card.locator('.price').inner_text(),'exact displayed total')
 return r
def measure(page):
 data=page.evaluate("""() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,tables:[...document.querySelectorAll('.nightly')].map(e=>{const x=e.scrollLeft;e.scrollLeft=e.scrollWidth;const moved=e.scrollLeft;e.scrollLeft=x;return {client:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX,moved};})})""")
 require(data['scroll']<=data['width'],'no whole-page overflow')
 require(all(t['scroll']<=t['client']+1 or (t['overflow']=='auto' and t['moved']>0) for t in data['tables']),'local table scroll works');return data
def run():
 rec['java_pid_before']=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=h.BROWSER);rec['browser']={'version':browser.version,'engine':'Chromium'}
  for width in [1440,768,390,320]:
   for theme in ['light','dark']:
    print('Shell',width,theme,flush=True)
    c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');c.add_init_script(f"if(!localStorage.getItem('travel-f25:theme'))localStorage.setItem('travel-f25:theme','{theme}')")
    page=c.new_page();page.on('pageerror',lambda e:rec['js_errors'].append(str(e)))
    page.on('request',lambda q:rec['direct_ES_requests'].append(q.url) if ':19225' in q.url or ':9200' in q.url or ':9201' in q.url else None)
    page.on('response',lambda q:rec['unexpected_http'].append(dict(url=q.url,status=q.status)) if q.status>=400 and q.url!=BASE+'/api/stay/inspect' else None)
    page.goto(BASE+'/f25.html',wait_until='networkidle');require(page.locator('html').get_attribute('data-theme')==theme,'theme initialized')
    for name in ['two-nights','two-rooms','three-nights','one-night']:
     page.locator('#scenario').select_option(name);require(page.locator('.card').count()==0,'changing clears old cards');r=check(page,name)
     rec['matrix'].append(dict(width=width,theme=theme,scenario=name,accepted=r['acceptedTotal'],layout=measure(page)))
     if name=='two-nights':
      page.evaluate('scrollTo(0,0)');shot(page,f'shell-{width}-{theme}-form');shot(page,f'shell-{width}-{theme}-o01','.card[data-id="o01"]')
     if width==390 and name=='two-rooms':shot(page,'shell-390-'+theme+'-o04','.card[data-id="o04"]')
    page.locator('#theme').click();other='dark' if theme=='light' else 'light';require(page.locator('html').get_attribute('data-theme')==other,'theme changes');page.reload(wait_until='networkidle');require(page.locator('html').get_attribute('data-theme')==other,'theme persists')
    c.close()
  c=browser.new_context(viewport={'width':390,'height':1000});page=c.new_page();page.on('pageerror',lambda e:rec['js_errors'].append(str(e)));page.goto(BASE+'/f25.html',wait_until='networkidle')
  page.locator('input[name="checkIn"]').fill('2026-11-02');page.locator('input[name="checkOut"]').fill('2026-11-02');r=submit(page,400);require(r['code']=='INVALID_STAY_INPUT','invalid dates');shot(page,'shell-400-dates')
  page.locator('#scenario').select_option('two-nights');check(page,'two-nights')
  summary=json.loads((R/'projects/travel-search/data/f25/summaries.json').read_text())[0];changed=dict(summary);del changed['hotel_name']
  try:
   es('PUT','/'+INDEX+'/_doc/o01',changed);es('POST','/'+INDEX+'/_refresh');r=submit(page,502);require(r['code']=='SEARCH_INCOMPLETE','missing identity fails closed');shot(page,'shell-502-incomplete')
  finally:es('PUT','/'+INDEX+'/_doc/o01',summary);es('POST','/'+INDEX+'/_refresh')
  check(page,'two-nights')
  es('DELETE','/'+INDEX);r=submit(page,502);require(r['code']=='SEARCH_BACKEND_REJECTED','missing index');shot(page,'shell-502-index')
  subprocess.run([sys.executable,str(R/'projects/travel-search/labs/f25/lab.py'),'prepare','--out',str(R/'projects/travel-search/review/f25/shell-restore')],check=True,capture_output=True)
  check(page,'two-nights')
  try:
   subprocess.run(['docker','compose','-f',str(R/'projects/travel-search/infra/f25/compose.yaml'),'stop','es'],check=True,capture_output=True)
   r=submit(page,503);require(r['code']=='SEARCH_UNAVAILABLE','real stopped ES');shot(page,'shell-503-stopped')
  finally:
   subprocess.run(['docker','compose','-f',str(R/'projects/travel-search/infra/f25/compose.yaml'),'start','es'],check=True,capture_output=True)
   subprocess.run(['bash',str(R/'projects/travel-search/infra/f25/wait.sh')],check=True,capture_output=True)
  check(page,'two-nights');c.close();browser.close()
 require(not rec['js_errors'] and not rec['direct_ES_requests'] and not rec['unexpected_http'],'no unexpected JS/network/direct ES')
 rec['java_pid_after']=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip();require(rec['java_pid_before']==rec['java_pid_after'],'same Java process across failures')
 rec['status']='passed';rec['limitations']='No timeout/shard failure injection. All ES failures used real index/source/stop changes; no mocked API responses.'
try:run()
except Exception as error:rec['status']='failed';rec['error']=str(error);rec['traceback']=traceback.format_exc();raise
finally:(HERE/'shell-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print('Real shell passed',len(rec['matrix']),'matrix scenarios;',len(rec['calls']),'Java calls')
