#!/usr/bin/env python3
"""Actual browser -> Java -> ES F12 observation window; no mocked API responses."""
import datetime,hashlib,importlib.util,json,pathlib,subprocess,time,traceback,urllib.request
from playwright.sync_api import sync_playwright
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];P=R/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f12lab',P/'labs/f12/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'actual F12 browser/Java/ES, no fake responses',
        'matrix':[],'operations':[],'screenshots':[],'js_errors':[],'direct_es_requests':[]}
def require(ok,info):
 if not ok:raise AssertionError(info)
def observe(page):
 page.on('pageerror',lambda e:record['js_errors'].append(str(e)))
 page.on('request',lambda r:record['direct_es_requests'].append(r.url) if ':19200/' in r.url or ':9200/' in r.url else None)
 def response(r):
  if '/api/attractions/changes' in r.url:
   record['operations'].append({'url':r.url,'method':r.request.method,'request':json.loads(r.request.post_data) if r.request.post_data else None,'status':r.status,'response':r.json()})
 page.on('response',response)
def action(page,button,suffix,status=200):
 with page.expect_response(lambda r:r.url.endswith(lab.BASE+suffix),timeout=15000) as response:page.locator(button).click()
 r=response.value;require(r.status==status,{'url':r.url,'status':r.status,'body':r.json()})
 page.wait_for_function("!document.getElementById('read').disabled")
 return r.json()
def check_cards(page,data):
 require(page.locator('.card').count()==len(data['items']),data)
 ids=page.locator('.card').evaluate_all('els=>els.map(e=>e.dataset.id)')
 require(ids==[x['id'] for x in data['items']],ids)
 for i,item in enumerate(data['items']):
  card=page.locator('.card').nth(i)
  require(card.locator('h3').inner_text()==item['name'],item)
  require(card.locator('.price').inner_text()==f"{item['ticketPriceFen']/100:.2f} 元",item)
  require(json.loads(card.locator('.tag').inner_text().split(' · sort ')[1])==item['sortValues'],item)
 require(json.loads(page.locator('#dsl-json').text_content())==data['esRequest'],'DSL')
 require(json.loads(page.locator('#input-json').text_content())==data['conditions'],'input')
 require(json.loads(page.locator('#result-json').text_content())==data,'DTO')
 require(str(data['total'])+'份' in page.locator('#page-note').inner_text(),'total')
def layout(page):
 r=page.evaluate('({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,main:document.querySelector("main").getBoundingClientRect().width})')
 require(r['page']<=r['viewport'] and r['body']<=r['viewport'],r);return r
def shot(page,name,target=None):
 p=H/'screenshots'/('shell-'+name+'.png')
 (page.locator(target).screenshot(path=str(p)) if target else page.screenshot(path=str(p)))
 record['screenshots'].append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'pending'})
def search(page):
 r=action(page,'#submit','/pages/start');check_cards(page,r);return r

def run():
 for index in [lab.INDEX,lab.GRAD]:
  try:lab.call('GET','/'+index,expected=404)
  except RuntimeError:lab.call('DELETE','/'+index)
 lab.prepare();lab.prepare(True)
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch();record['browser']={'engine':'Chromium','version':browser.version}
   for width in [1920,1440,1024,768,390,320]:
    for theme in ['light','dark']:
     print('F12 shell',width,theme,flush=True)
     context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
     context.add_init_script(f"localStorage.setItem('travel-f12:theme','{theme}')")
     page=context.new_page();observe(page);page.goto(lab.APP+'/f12.html',wait_until='networkidle')
     require(page.locator('html').get_attribute('data-theme')==theme,'theme')
     read=action(page,'#read','/d-hz-garden');require(read['document']['ticket_price_fen']==4500,'GET')
     require(json.loads(page.locator('#document-json').inner_text())==read,'GET DTO')
     first=search(page);require([i['id'] for i in first['items']]==['d-hz-walk','d-hz-garden'] and first['total']==3,'first')
     if width in [1440,390]:shot(page,f'{width}-{theme}-first')
     last=action(page,'#next','/pages/next');check_cards(page,last)
     require([i['id'] for i in last['items']]==['d-hz-boat'] and not last['hasNext'] and page.locator('#next').is_disabled(),'last')
     if width==390:shot(page,f'{width}-{theme}-last','.results')
     action(page,'#close','/pages/close');require(page.locator('.card').count()==0,'close clears')
     record['matrix'].append({'width':width,'theme':theme,'layout':layout(page),'get_matches':True,'ids_prices_sort_dsl_dto':'both pages exact','page_lengths':[2,1],'closed':True})
     context.close()
   context=browser.new_context(viewport={'width':390,'height':1000},reduced_motion='reduce');page=context.new_page();observe(page)
   page.goto(lab.APP+'/f12.html',wait_until='networkidle')
   first=search(page);action(page,'#read','/d-hz-garden');page.locator('#price').fill('9000')
   action(page,'#save','/d-hz-garden');require(page.locator('#save').is_disabled(),'write needs reread')
   fresh=action(page,'#read','/d-hz-garden');require(fresh['document']['ticket_price_fen']==9000,'GET new value')
   require(json.loads(page.locator('#result-json').text_content())['items'][1]['ticketPriceFen']==4500,'search unchanged')
   shot(page,'390-write-before-refresh')
   before=search(page);require(before['items'][1]['ticketPriceFen']==4500,'new PIT before refresh still old')
   action(page,'#refresh','/refresh')
   oldlast=action(page,'#next','/pages/next');require([i['id'] for i in oldlast['items']]==['d-hz-boat'],'old PIT after refresh');check_cards(page,oldlast)
   live=search(page);require([i['id'] for i in live['items']]==['d-hz-walk','d-hz-boat'] and live['total']==2,'new PIT excludes garden')
   shot(page,'390-after-refresh')
   # Change conditions closes the old PIT and clears the displayed request.
   with page.expect_response(lambda r:r.url.endswith('/pages/close')):page.locator('[name=cityCode]').select_option('SH')
   page.wait_for_function("!document.getElementById('read').disabled")
   require(page.locator('.card').count()==0 and page.locator('#next').is_disabled(),'condition change clears')
   sh=search(page);require([i['id'] for i in sh['items']]==['d-sh-park'],'city change');action(page,'#close','/pages/close')
   # Two actual browser windows read the same version, then preserve the winner's new price.
   lab.restore();other=context.new_page();observe(other);other.goto(lab.APP+'/f12.html',wait_until='networkidle')
   action(page,'#read','/d-hz-garden');action(other,'#read','/d-hz-garden')
   page.locator('#price').fill('6500');action(page,'#save','/d-hz-garden')
   other.locator('#state').select_option('closed');err=action(other,'#save','/d-hz-garden',409)
   require(err['code']=='WRITE_CONFLICT' and other.locator('#save').is_disabled(),'conflict disabled')
   shot(other,'390-conflict')
   read=action(other,'#read','/d-hz-garden');require(read['document']['ticket_price_fen']==6500 and read['document']['status']=='open','winner retained')
   other.locator('#state').select_option('closed');action(other,'#save','/d-hz-garden');action(other,'#refresh','/refresh')
   read=action(other,'#read','/d-hz-garden');require(read['document']['ticket_price_fen']==6500 and read['document']['status']=='closed','field-only recovery')
   shot(other,'390-conflict-recovered');other.close()
   # Missing document clears the editor version and prevents a stale save.
   page.locator('#document-id').fill('not-found');action(page,'#read','/not-found',404)
   require(page.locator('#save').is_disabled() and '404' in page.locator('#write-status').inner_text(),'missing')
   lab.restore();page.locator('[name=cityCode]').select_option('HZ');search(page);action(page,'#close','/pages/close')
   # True missing-index failure, then recreate and recover in the SAME Java process.
   lab.call('DELETE','/'+lab.INDEX);action(page,'#submit','/pages/start',502)
   require(page.locator('.card').count()==0 and '尚无当前结果' in page.locator('#dsl-json').text_content(),'502 stale cleared')
   shot(page,'390-missing-index');lab.prepare();search(page);action(page,'#close','/pages/close')
   # True ES stop; preserve the two Java processes and framework volume.
   compose=['docker','compose','-f',str(P/'infra/single-node/compose.yaml')]
   subprocess.run([*compose,'stop','es'],check=True,capture_output=True,text=True)
   try:
    action(page,'#submit','/pages/start',503)
    require(page.locator('.card').count()==0,'503 stale cleared');shot(page,'390-unavailable')
   finally:subprocess.run([*compose,'up','-d','es'],check=True,capture_output=True,text=True)
   deadline=time.monotonic()+30
   while True:
    try:
     r=urllib.request.urlopen(lab.ES,timeout=2)
     if r.status==200:break
    except Exception:pass
    if time.monotonic()>deadline:raise AssertionError('ES restart timeout')
    time.sleep(.2)
   # A ready HTTP root is not a promise that the Java transport's first retry has recovered.
   deadline=time.monotonic()+15
   while True:
    try:
     result=search(page);break
    except AssertionError:
     if time.monotonic()>deadline:raise
     time.sleep(.2)
   require(result['total']==3,'same process recovery');shot(page,'390-recovered');action(page,'#close','/pages/close')
   # Empty result is a successful current view; no retained cards.
   page.locator('[name=q]').fill('火星');page.locator('[name=q]').press('Tab');page.wait_for_function("!document.getElementById('read').disabled")
   empty=search(page);require(empty['total']==0 and not empty['hasNext'],'empty');action(page,'#close','/pages/close')
   page.locator('#theme').click();require(page.locator('html').get_attribute('data-theme')=='dark','toggle')
   page.reload(wait_until='networkidle');require(page.locator('html').get_attribute('data-theme')=='dark','reload theme')
   page.locator('#read').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
   require(page.locator('#read').evaluate("e=>e===document.activeElement && getComputedStyle(e).outlineStyle!=='none'"),'actual Tab focus')
   # Fresh graduation source in its separately configured Java process.
   grad=context.new_page();observe(grad);grad.goto(lab.GRAD_APP+'/f12.html',wait_until='networkidle')
   grad.locator('[name=q]').fill('星湾');grad.locator('[name=budget]').fill('60');grad.locator('[name=budget]').press('Tab')
   grad.wait_for_function("!document.getElementById('read').disabled")
   first=search(grad);require([i['id'] for i in first['items']]==['g-hz-free','g-hz-garden'] and first['total']==3,'graduation first')
   grad.locator('#document-id').fill('g-hz-garden');action(grad,'#read','/g-hz-garden');shot(grad,'390-graduation-first')
   last=action(grad,'#next','/pages/next');check_cards(grad,last);require([i['id'] for i in last['items']]==['g-hz-museum'],'graduation last')
   action(grad,'#close','/pages/close');grad.close();context.close();browser.close()
  require(not record['js_errors'] and not record['direct_es_requests'],record)
  for index in [lab.INDEX,lab.GRAD]:
   require(lab.call('GET',f'/{index}/_stats/search')['indices'][index]['total']['search']['open_contexts']==0,'no active contexts')
  record['interactions']=['GET/source/version exact','save accepted does not refresh','ordinary search before/after refresh','existing PIT unchanged',
     'two real browser editors 409 and reread','condition change closes','404 missing document','502 missing index/recreate',
     'real ES stop 503/same Java process recovery','empty result','theme reload','actual Tab focus','fresh graduation two pages']
  record['status']='passed'
 except Exception:
  record['status']='failed';record['failure']=traceback.format_exc();raise
 finally:
  record['es_author_operations']=lab.RECORD
  record['sha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'backend/src').rglob('*') if p.is_file()}
  (H/'shell-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print('F12 shell passed',len(record['matrix']),'groups',len(record['operations']),'real API calls',len(record['screenshots']),'PNGs',flush=True)
if __name__=='__main__':run()
