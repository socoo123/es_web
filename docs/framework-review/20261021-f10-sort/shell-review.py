#!/usr/bin/env python3
"""F10 actual local browser -> Java -> ES. Only named F10 cleanup and framework ES stop/start."""
import datetime,hashlib,json,pathlib,subprocess,time,traceback,urllib.request,urllib.error
from playwright.sync_api import sync_playwright
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/travel-search';APP='http://127.0.0.1:18080';API=APP+'/api/attractions/sort-search'
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F10 real local browser -> Java -> ES','matrix':[],'searches':[],'screenshots':[],'operations':[],'js_errors':[],'direct_es_requests':[],'request_failures':[]}
def need(v,d):
 if not v:raise AssertionError(d)
def load(n):return json.loads((P/f'search/f10/{n}.json').read_text())
def run(args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);R['operations'].append(dict(command=args,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr));need(p.returncode==0,p.stderr);return p
S=['a-sh-exhibit','a-hz-tea','a-hz-guide','a-fz-xihu','a-hz-plain','a-hz-xihu','a-hz-boundary','a-hz-missing-location','a-hz-far']
PR=['a-fz-xihu','a-hz-xihu','a-hz-far','a-hz-guide','a-hz-missing-location','a-hz-plain','a-hz-tea','a-sh-exhibit','a-hz-boundary']
D=['a-hz-guide','a-hz-plain','a-hz-xihu','a-hz-boundary','a-hz-tea','a-hz-far','a-sh-exhibit','a-fz-xihu','a-hz-missing-location']
EXPECTED={'relevance':S,'price':PR,'distance':D,'price-scores':PR,'hz-distance':[x for x in D if x.startswith('a-hz')],'budget-price':[x for x in PR if x not in ['a-hz-boundary','a-sh-exhibit']],'empty':[]}
def observe(page):
 page.on('pageerror',lambda e:R['js_errors'].append(str(e)))
 page.on('requestfailed',lambda r:R['request_failures'].append({'url':r.url,'failure':r.failure}))
 page.on('request',lambda r:R['direct_es_requests'].append(r.url) if any(':'+str(port)+'/' in r.url for port in [19200,9200,9201]) else None)
def measure(page):
 r=page.evaluate('''()=>({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,theme:document.documentElement.dataset.theme,inputs:[...document.querySelectorAll('input,select,button')].map(i=>({name:i.name,id:i.id,width:i.getBoundingClientRect().width}))})''');need(r['page']<=r['viewport'] and r['body']<=r['viewport'],r);return r
def shot(page,name,target=None):
 path=H/'screenshots'/('shell-'+name+'.png');
 if target:page.locator(target).screenshot(path=str(path))
 else:page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(path))
 R['screenshots'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_review':'pending'})
def submit(page,slug,status=200):
 inp=load('input-'+slug)
 for name,value in {'q':inp['q'],'budget':str(inp['maxPriceFen']/100),'latitude':str(inp['latitude']),'longitude':str(inp['longitude'])}.items():page.locator('[name='+name+']').fill(value)
 for name,value in {'cityCode':inp['cityCode'],'sortMode':inp['sortMode'],'trackScores':str(inp['trackScores']).lower()}.items():page.locator('[name='+name+']').select_option(value)
 with page.expect_response(lambda r:r.url==API) as event:page.locator('#submit').click()
 response=event.value;result=response.json();page.wait_for_function('!document.querySelector("#submit").disabled');need(response.status in (status if isinstance(status,list) else [status]),dict(status=response.status,result=result))
 need(json.loads(page.locator('#input-json').text_content())==inp,'displayed input')
 need(json.loads(page.locator('#result-json').text_content())==result,'displayed result')
 if response.status==200:
  need(result['conditions']==inp and result['esRequest']==load(slug),'exact query')
  need(result['total']==len(EXPECTED[slug]) and result['totalRelation']=='eq','exact count')
  need([x['id'] for x in result['items']]==EXPECTED[slug],'expected full ID order')
  need(page.locator('.card').evaluate_all('els=>els.map(x=>x.dataset.id)')==EXPECTED[slug],'DOM full ID order')
  need(json.loads(page.locator('#dsl-json').text_content())==result['esRequest'],'displayed DSL')
  for i,item in enumerate(result['items']):
   card=page.locator('.card').nth(i)
   need(card.locator('h3').text_content()==item['name'],'name')
   need(card.locator('.price').text_content().startswith('¥'+f"{item['ticketPriceFen']/100:.2f}"),'price CNY fen -> yuan')
   need(json.loads(card.locator('.sort-values').text_content().split(' = ',1)[1])==item['sortValues'],'full sort DOM')
   need(card.locator('.score').text_content()=='评分：'+('未返回' if item['score'] is None else str(item['score'])),'score DOM')
   expected='待定位' if not item['hasLocation'] else ('本模式未计算' if item['distanceKm'] is None else f"{item['distanceKm']:.3f} km")
   need(card.locator('.distance').text_content()=='距离：'+expected,'distance label/precision')
 else:
  need(page.locator('.card').count()==0 and page.locator('#status').get_attribute('class')=='error','clear stale cards')
 R['searches'].append({'case':slug,'HTTP':response.status,'input':inp,'response':result,'layout':measure(page),'DOM':'all cards/units/full sort/score/distance compared' if response.status==200 else 'stale cards cleared'})
 return result
try:
 R['java_pid_before']=subprocess.check_output(['lsof','-t','-iTCP:18080','-sTCP:LISTEN'],text=True).strip()
 with sync_playwright() as pw:
  browser=pw.chromium.launch();R['browser']={'engine':'Chromium','version':browser.version}
  for width in [1920,1440,1024,768,390,320]:
   for theme in ['light','dark']:
    c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');page=c.new_page();observe(page)
    page.goto(APP+'/f10.html',wait_until='networkidle');page.evaluate('v=>localStorage.setItem("travel-search:theme",v)',theme);page.reload(wait_until='networkidle');need(page.evaluate('document.documentElement.dataset.theme')==theme,'theme')
    slug='distance' if theme=='dark' else 'price';submit(page,slug)
    R['matrix'].append({'width':width,'theme':theme,'layout':measure(page),'case':slug})
    if width in [1440,390]:
     shot(page,f'{width}-{theme}-opening');shot(page,f'{width}-{theme}-results','.results')
    c.close()
  c=browser.new_context(viewport={'width':390,'height':1000},reduced_motion='reduce');page=c.new_page();observe(page);page.goto(APP+'/f10.html',wait_until='networkidle')
  compared={slug:submit(page,slug) for slug in ['relevance','price','price-scores','distance','hz-distance','budget-price','empty']}
  need([x['sortValues'] for x in compared['price']['items']]==[x['sortValues'] for x in compared['price-scores']['items']],'track_scores same sort')
  need(compared['distance']['items'][-1]['distanceKm'] is None and compared['distance']['items'][-1]['sortValues'][0]=='Infinity','missing geo')
  page.locator('#theme').click();theme=page.evaluate('document.documentElement.dataset.theme');page.reload(wait_until='networkidle');need(page.evaluate('document.documentElement.dataset.theme')==theme,'theme persists')
  page.locator('[name=q]').focus();page.keyboard.press('Tab');need(page.locator('[name=cityCode]').evaluate('el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=="none"'),'actual Tab visible focus')
  page.locator('.observe summary').click();measure(page);page.locator('.observe summary').click()
  submit(page,'distance');run(['bash','projects/travel-search/labs/f10/cleanup.sh']);need(submit(page,'distance',502)['code']=='SEARCH_BACKEND_REJECTED','missing index');shot(page,'390-dark-missing-index','.results')
  run(['bash','projects/travel-search/labs/f10/01-prepare.sh']);submit(page,'distance')
  run(['docker','compose','-f','projects/travel-search/infra/single-node/compose.yaml','stop','es'])
  need(json.load(urllib.request.urlopen(APP+'/api/health'))=={'application':'up','scope':'java-process-only'},'health only Java')
  need(submit(page,'distance',503)['code']=='SEARCH_UNAVAILABLE','ES down');shot(page,'390-dark-unavailable','.results')
  run(['docker','compose','-f','projects/travel-search/infra/single-node/compose.yaml','up','-d','es']);run(['bash','projects/travel-search/infra/single-node/wait.sh'])
  started=time.monotonic()
  while True:
   recovered=submit(page,'distance',[200,503])
   if 'items' in recovered:break
   need(time.monotonic()-started<90,'same-client recovery within90s');page.wait_for_timeout(1000)
  R['recovery_wait_seconds']=time.monotonic()-started;shot(page,'390-dark-recovered','.results')
  R['java_pid_after']=subprocess.check_output(['lsof','-t','-iTCP:18080','-sTCP:LISTEN'],text=True).strip();need(R['java_pid_after']==R['java_pid_before'],'same Java process/client recovery')
  R['interactions']={'actual_tab':'q -> city selector with visible outline','theme':'switch/reload preserved','observe':'expand/collapse readable at390','recovery':'missing index502 -> reprepare; ES stop503 -> restart, same Java process','scope':'Pages reading separate; direct ES browser requests must be zero'}
  c.close();browser.close()
 need(not R['js_errors'] and not R['request_failures'] and not R['direct_es_requests'],R)
 R['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'backend/src').rglob('*') if p.is_file()}
 R['status']='passed'
except Exception:R['status']='failed';R['failure']=traceback.format_exc();raise
finally:(H/'shell-review.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print(f"F10 shell passed: {len(R['matrix'])} size/theme groups, {len(R['searches'])} real searches, 502/503 recovery")
