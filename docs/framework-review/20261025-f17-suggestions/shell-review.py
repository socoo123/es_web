#!/usr/bin/env python3
"""Real browser -> final Boot4/JDK25 jar -> isolated F17 ES. No mock responses."""
import contextlib,datetime,hashlib,importlib.util,json,pathlib,subprocess,traceback
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f17lab',P/'labs/f17/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F17 real final-jar local observer; requests are not mocked','matrix':[],'operations':[],'errors':[],'screenshots':[],'js_errors':[],'direct_es_requests':[],'status':'running'}
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def logged(name,fn):
 with (HERE/name).open('w') as f,contextlib.redirect_stdout(f):return fn()
def setup():lab.cleanup();lab.prepare();lab.pinyin();lab.fuzzy()
def observe(page):
 page.on('pageerror',lambda e:record['js_errors'].append(str(e)))
 page.on('request',lambda r:record['direct_es_requests'].append(r.url) if any(':'+str(p)+'/' in r.url for p in [9200,9201,19200,19214,19215,19216,19217]) else None)
 def response(r):
  if r.url.endswith('/api/attractions/suggestions'):record['operations'].append({'request':json.loads(r.request.post_data),'status':r.status,'response':r.json()})
 page.on('response',response)
def fill(page,q='故宫',city='BJ',mode='completion'):
 page.locator('[name=q]').fill('');page.locator('[name=q]').fill(q)
 page.locator('[name=cityCode]').select_option(city);page.locator('[name=mode]').select_option(mode)
 require(page.locator('.card').count()==0,'condition clears cards')
 for id in ['input-json','dsl-json','es-json','result-json']:require(page.locator('#'+id).text_content()=='尚无本轮结果','condition clears '+id)
def search(page,expected=None,status=200):
 with page.expect_response(lambda r:r.url.endswith('/api/attractions/suggestions'),timeout=30000) as got:page.locator('#submit').click()
 response=got.value;r=response.json();require(response.status==status,{'status':response.status,'expected':status,'body':r})
 page.wait_for_function("!document.getElementById('submit').disabled")
 if status!=200:
  require(page.locator('.card').count()==0,'error clears cards')
  require(page.locator('#status').get_attribute('class')=='error' and str(status) in page.locator('#status').inner_text(),'visible HTTP error')
  for id in ['input-json','dsl-json','es-json','result-json']:require(page.locator('#'+id).text_content()=='尚无本轮结果','error clears '+id)
  return r
 require([i['id'] for i in r['items']]==expected,r)
 require(page.locator('.card').evaluate_all('els=>els.map(e=>e.dataset.id)')==expected,'cards match IDs/order')
 for i,item in enumerate(r['items']):
  card=page.locator('.card').nth(i)
  for selector,value in [('h3',item['name']),('.pinyin',item['pinyinFull']+' / '+item['pinyinInitials']),('.tag',item['cityCode']+' · '+item['currency']+' / '+item['status']),('.price',f"{item['ticketPriceFen']/100:.2f} 元"),('.id',item['id']),('.suggestion','普通搜索候选' if item['suggestionText'] is None else '匹配提示：'+item['suggestionText'])]:require(card.locator(selector).inner_text()==value,(selector,item))
 require(page.locator('#total').inner_text()==f"{r['returnedCount']} 份候选",'returned count')
 if r['total'] is None:require('全部候选总数未知' in page.locator('#count-note').inner_text(),'no fabricated completion total')
 else:require(f"总计{r['total']}份 · {r['relation']}" in page.locator('#count-note').inner_text(),'ordinary total')
 for id,key in [('input-json','conditions'),('dsl-json','esRequest'),('es-json','esResponse'),('result-json',None)]:require(json.loads(page.locator('#'+id).text_content())==(r[key] if key else r),'complete JSON '+id)
 require(page.locator('#status').get_attribute('class')!='error','0 candidates is successful')
 return r
def layout(page):
 r=page.evaluate('({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})');require(r['page']<=r['viewport'] and r['body']<=r['viewport'],r);return r
def shot(page,name,target='.results'):
 (HERE/'screenshots').mkdir(exist_ok=True);p=HERE/'screenshots'/('shell-'+name+'.png')
 page.wait_for_timeout(250)
 if target:page.locator(target).screenshot(path=str(p))
 else:page.screenshot(path=str(p))
 record['screenshots'].append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'pending'})
try:
 logged('shell-setup.jsonl',setup)
 with sync_playwright() as pw:
  browser=pw.chromium.launch();record['browser']={'engine':'Chromium','version':browser.version}
  cases=[('completion','故宫','BJ','completion',['bj-palace','bj-same-a','bj-same-b']),('middle','博物','BJ','sayt',['bj-palace']),
    ('pinyin','GuGong','BJ','pinyin',['bj-garden','bj-palace','bj-same-a','bj-same-b']),('initials','gg','BJ','pinyin',['bj-garden','bj-palace','bj-same-a','bj-same-b']),
    ('typo','天谈公园','BJ','fuzzy',['bj-pond','bj-temple']),('short','西胡','BJ','fuzzy',['bj-river','bj-west']),('guarded','西胡','BJ','guarded',[]),
    ('exact','天谈公园','BJ','exact',[]),('city','故宫','SY','completion',['sy-palace']),('guarded-long','天谈公园','BJ','guarded',['bj-pond','bj-temple']),
    ('sayt','故宫','BJ','sayt',['bj-infix','bj-palace','bj-same-a','bj-same-b'])]
  for width in [1440,390,320]:
   for theme in ['light','dark']:
    print('Shell matrix',width,theme,flush=True)
    context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
    context.add_init_script(f"if(localStorage.getItem('travel-f17:theme')===null)localStorage.setItem('travel-f17:theme','{theme}')")
    page=context.new_page();observe(page);page.goto('http://127.0.0.1:18080/f17.html',wait_until='networkidle')
    require(page.evaluate('document.documentElement.dataset.theme')==theme,'theme')
    if width in [1440,390]:shot(page,f'{width}-{theme}-opening',None)
    for slug,q,city,mode,expected in cases:
     fill(page,q,city,mode);r=search(page,expected)
     record['matrix'].append({'width':width,'theme':theme,'case':slug,'input':r['conditions'],'ids':expected,'layout':layout(page)})
     if width in [1440,390] and slug in ['completion','pinyin','typo','short','guarded']:shot(page,f'{width}-{theme}-{slug}')
    page.locator('.observe summary').click();layout(page)
    page.locator('#theme').click();opposite='dark' if theme=='light' else 'light'
    page.reload(wait_until='networkidle');require(page.evaluate('document.documentElement.dataset.theme')==opposite,'theme reload')
    context.close()
  context=browser.new_context(viewport={'width':390,'height':1000},reduced_motion='reduce');page=context.new_page();observe(page)
  page.goto('http://127.0.0.1:18080/f17.html',wait_until='networkidle')
  fill(page,'g','BJ','pinyin');r=search(page,status=400);shot(page,'390-invalid-400');record['errors'].append({'case':'invalid-pinyin','response':r})
  # Real stale status/context projection triggers a visible incomplete-contract error.
  logged('shell-stale.jsonl',lambda:lab.call('POST','/'+lab.INDEX+'/_update/bj-palace',{'doc':{'status':'closed'}}))
  logged('shell-stale-refresh.jsonl',lab.refresh)
  fill(page);r=search(page,status=502);require(r['code']=='SEARCH_INCOMPLETE',r);shot(page,'390-stale-502');record['errors'].append({'case':'stale-context','response':r})
  logged('shell-restore.jsonl',setup)
  fill(page);search(page,['bj-palace','bj-same-a','bj-same-b']);shot(page,'390-stale-recovered')
  logged('shell-delete.jsonl',lambda:lab.call('DELETE','/'+lab.INDEX))
  fill(page);r=search(page,status=502);require(r['code']=='SEARCH_BACKEND_REJECTED',r);shot(page,'390-missing-502');record['errors'].append({'case':'missing-index','response':r})
  logged('shell-restore-index.jsonl',setup)
  fill(page);search(page,['bj-palace','bj-same-a','bj-same-b']);shot(page,'390-missing-recovered')
  subprocess.run(['docker','compose','-f',str(P/'infra/f17/compose.yaml'),'stop','es'],check=True,capture_output=True,text=True)
  fill(page);r=search(page,status=503);require(r['code']=='SEARCH_UNAVAILABLE',r);shot(page,'390-offline-503');record['errors'].append({'case':'real-es-stop','response':r})
  subprocess.run(['docker','compose','-f',str(P/'infra/f17/compose.yaml'),'up','-d','es'],check=True,capture_output=True,text=True)
  result=subprocess.run(['bash',str(P/'infra/f17/wait.sh')],check=True,capture_output=True,text=True);record['es_recovery']=result.stdout.strip()
  fill(page);search(page,['bj-palace','bj-same-a','bj-same-b']);shot(page,'390-offline-recovered')
  page.locator('#submit').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
  require(page.locator('#submit').evaluate("el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=='none'"),'keyboard focus')
  context.close();browser.close()
 require(not record['js_errors'] and not record['direct_es_requests'],record)
 record['same_java_process']='All errors and recovery used the same final jar process; only F17 ES was restarted'
 record['jar_sha256']=hashlib.sha256((P/'backend/target/travel-search-0.7.0.jar').read_bytes()).hexdigest()
 record['status']='passed'
except BaseException:record['status']='failed';record['error']=traceback.format_exc();raise
finally:(HERE/'shell-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F17 shell passed',len(record['matrix']),'matrix searches;',len(record['operations']),'actual Java requests')
