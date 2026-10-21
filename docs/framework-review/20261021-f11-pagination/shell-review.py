#!/usr/bin/env python3
"""F11 real browser -> Java -> ES, pagination and lifecycle; named fixture only."""
import copy,datetime,hashlib,importlib.util,json,pathlib,subprocess,time,traceback
from playwright.sync_api import sync_playwright
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/travel-search';APP='http://127.0.0.1:18080';API=APP+'/api/attractions/pages/'
spec=importlib.util.spec_from_file_location('f11lab',P/'labs/f11/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F11 real local shell, same Java process/client','matrix':[],'actions':[],'screenshots':[],'operations':[],'js_errors':[],'request_failures':[],'direct_es_requests':[]}
EXPECTED={'price':lab.OLD,'relevance':['a-sh-exhibit','a-hz-tea','a-hz-guide','a-fz-xihu','a-hz-plain','a-hz-xihu','a-hz-boundary','a-hz-missing-location','a-hz-far'],'distance':['a-hz-guide','a-hz-plain','a-hz-xihu','a-hz-boundary','a-hz-tea','a-hz-far','a-sh-exhibit','a-fz-xihu','a-hz-missing-location']}
def need(v,d):
 if not v:raise AssertionError(d)
def run(args):
 result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);R['operations'].append({'command':args,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr});need(result.returncode==0,result.stderr)
def measure(page):
 result=page.evaluate('''()=>({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,theme:document.documentElement.dataset.theme})''');need(result['page']<=result['viewport'] and result['body']<=result['viewport'],result);return result
def observe(page):
 page.on('pageerror',lambda e:R['js_errors'].append(str(e)))
 page.on('requestfailed',lambda req:R['request_failures'].append({'url':req.url,'failure':req.failure}))
 page.on('request',lambda req:R['direct_es_requests'].append(req.url) if any(':'+str(port)+'/' in req.url for port in [9200,9201,19200]) else None)
def shot(page,name,target=None):
 path=H/'screenshots'/('shell-'+name+'.png')
 if target:page.locator(target).screenshot(path=str(path))
 else:page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(path))
 R['screenshots'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_review':'pending'})
def action(page,kind,status=200):
 with page.expect_response(lambda response:response.url==API+kind) as event:page.locator({'start':'#submit','next':'#next','close':'#close'}[kind]).click()
 response=event.value;data=response.json();page.wait_for_function('!document.querySelector("#submit").disabled')
 need(response.status in ([status] if isinstance(status,int) else status),{'kind':kind,'status':response.status,'body':data})
 record={'kind':kind,'status':response.status,'request':response.request.post_data_json,'response':data,'layout':measure(page)}
 if response.status==200 and kind!='close':
  need(json.loads(page.locator('#result-json').text_content())==data,'DTO displayed verbatim')
  need(json.loads(page.locator('#dsl-json').text_content())==data['esRequest'],'DSL displayed verbatim')
  need(json.loads(page.locator('#input-json').text_content())==data['conditions'],'conditions displayed')
  need(page.locator('.card').evaluate_all('els=>els.map(el=>el.dataset.id)')==[i['id'] for i in data['items']],'all DOM IDs')
  for n,item in enumerate(data['items']):
   card=page.locator('.card').nth(n)
   need(card.locator('h3').text_content()==item['name'],'name')
   need(card.locator('.card-price').text_content()==f"{item['ticketPriceFen']/100:.2f} 元 · {item['ticketPriceFen']}分",'fen/yuan')
   need(json.loads(card.locator('.sort-values').text_content()[6:])==item['sortValues'],'full sort without rounding')
   mode=data['conditions']['search']['sortMode'];first=item['sortValues'][0]
   metric=('待定位' if first=='Infinity' else str(first)+' km') if mode=='distance' else str(first)+' 分' if mode=='price' else '相关性 '+str(first)
   displayed=card.locator('.metric').text_content()
   if mode=='distance' and first=='Infinity':need(displayed=='排序首值：待定位','missing coordinate')
   else:
    prefix='排序首值：'+('相关性 ' if mode=='relevance' else '')
    suffix=' km' if mode=='distance' else ' 分' if mode=='price' else ''
    need(displayed.startswith(prefix) and (not suffix or displayed.endswith(suffix)),'sort unit label')
    numeric=displayed[len(prefix):len(displayed)-len(suffix) if suffix else None]
    need(float(numeric)==float(first),'full numeric sort metric')
   need('score: '+('未返回' if item['score'] is None else str(item['score'])) in card.text_content(),'score')
  need(page.locator('#next').is_disabled()==(not data['hasNext']),'hasNext matches button')
  need(page.locator('#history li').count()==data['pageNumber'],'history contains every page')
  record['DOM']='all IDs/names/fen/yuan/scores/full sort/hasNext/DSL/conditions compared'
 elif response.status!=200:
  need(page.locator('.card').count()==page.locator('#history li').count()==0 and page.locator('#next').is_disabled(),'failure cleared stale cards/history')
  record['DOM']='stale cards/history cleared; no stale next'
 else:need(page.locator('#close').is_disabled(),'closed control')
 R['actions'].append(record);return data

def configure(page,mode='price',q='西湖',size='3'):
 if page.locator('#close').is_enabled():action(page,'close')
 page.locator('[name=q]').fill(q);page.locator('[name=cityCode]').select_option('ALL');page.locator('[name=budget]').fill('200');page.locator('[name=sortMode]').select_option(mode);page.locator('[name=pageSize]').select_option(size)

def complete(page,mode):
 configure(page,mode);result=action(page,'start');allids=[i['id'] for i in result['items']]
 while result['hasNext']:
  result=action(page,'next');allids += [i['id'] for i in result['items']]
 need(allids==EXPECTED[mode] and len(set(allids))==9,{'mode':mode,'allids':allids});action(page,'close')
 return allids

try:
 R['java_pid_before']=subprocess.check_output(['lsof','-t','-iTCP:18080','-sTCP:LISTEN'],text=True).strip()
 with sync_playwright() as pw:
  browser=pw.chromium.launch();R['browser']={'engine':'Chromium','version':browser.version}
  for width in [1920,1440,1024,768,390,320]:
   for theme in ['light','dark']:
    c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');page=c.new_page();observe(page)
    page.goto(APP+'/f11.html',wait_until='networkidle');page.evaluate('t=>localStorage.setItem("travel-search:theme",t)',theme);page.reload(wait_until='networkidle')
    need(page.evaluate('document.documentElement.dataset.theme')==theme,'theme')
    mode='price' if theme=='light' else 'distance';configure(page,mode)
    first=action(page,'start');ids=[i['id'] for i in first['items']]
    if width in [1440,390]:shot(page,f'{width}-{theme}-opening');shot(page,f'{width}-{theme}-first','.results')
    second=action(page,'next');third=action(page,'next');ids += [i['id'] for result in [second,third] for i in result['items']]
    need(ids==EXPECTED[mode] and not third['hasNext'],'complete three-page ID sequence')
    if width==390:shot(page,f'{width}-{theme}-last','.results');shot(page,f'{width}-{theme}-actions','.page-actions')
    action(page,'close');R['matrix'].append({'width':width,'theme':theme,'mode':mode,'ids':ids,'pages':[first['pageNumber'],second['pageNumber'],third['pageNumber']],'layout':measure(page)})
    c.close()
  c=browser.new_context(viewport={'width':390,'height':1000},reduced_motion='reduce');page=c.new_page();observe(page);page.goto(APP+'/f11.html',wait_until='networkidle')
  for mode in ['price','relevance','distance']:complete(page,mode)
  configure(page);first=action(page,'start')
  with page.expect_response(lambda r:r.url==API+'close') as event:page.locator('[name=cityCode]').select_option('HZ')
  need(event.value.status==200,'change closes old view');page.wait_for_function('!document.querySelector("#submit").disabled')
  need(page.locator('.card').count()==page.locator('#history li').count()==0 and page.locator('#next').is_disabled(),'condition change clears view')
  result=action(page,'start');need(result['total']==7 and result['pageNumber']==1,'changed condition restarts first page');action(page,'close')
  configure(page,q='火星');empty=action(page,'start');need(empty['total']==0 and not empty['hasNext'],'normal empty');action(page,'close')
  configure(page,size='2');result=action(page,'start');lengths=[len(result['items'])];allids=[x['id'] for x in result['items']]
  while result['hasNext']:result=action(page,'next');lengths.append(len(result['items']));allids += [x['id'] for x in result['items']]
  need(lengths==[2,2,2,2,1] and allids==lab.OLD,'five pages two per page');action(page,'close')
  configure(page);first=action(page,'start')
  lab.call('DELETE','/_pit',{'id':first['esRequest']['pit']['id']})
  need(action(page,'next',410)['code']=='PAGE_EXPIRED','real invalidated PIT');shot(page,'390-expired','.results');action(page,'close')
  run(['bash','projects/travel-search/labs/f11/cleanup.sh']);need(action(page,'start',502)['code']=='SEARCH_BACKEND_REJECTED','missing index');shot(page,'390-missing-index','.results')
  run(['bash','projects/travel-search/labs/f11/01-prepare.sh']);first=action(page,'start');need(first['total']==9,'reprepare recovery')
  run(['docker','compose','-f','projects/travel-search/infra/single-node/compose.yaml','stop','es'])
  need(action(page,'next',503)['code']=='SEARCH_UNAVAILABLE','connection failure clears view');shot(page,'390-unavailable','.results')
  run(['docker','compose','-f','projects/travel-search/infra/single-node/compose.yaml','up','-d','es']);run(['bash','projects/travel-search/infra/single-node/wait.sh'])
  t=time.monotonic()
  while True:
   result=action(page,'start',[200,503])
   if 'items' in result:break
   need(time.monotonic()-t<90,'same-client recovery within90s');page.wait_for_timeout(1000)
  shot(page,'390-recovered','.results');action(page,'close')
  page.locator('#theme').click();theme=page.evaluate('document.documentElement.dataset.theme');page.reload(wait_until='networkidle');need(page.evaluate('document.documentElement.dataset.theme')==theme,'theme reload')
  page.locator('[name=q]').focus();page.keyboard.press('Tab');need(page.locator('[name=cityCode]').evaluate('el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=="none"'),'actual Tab visible focus')
  page.locator('.observe summary').click();measure(page);page.locator('.observe summary').click()
  R['java_pid_after']=subprocess.check_output(['lsof','-t','-iTCP:18080','-sTCP:LISTEN'],text=True).strip();need(R['java_pid_after']==R['java_pid_before'],'same Java process')
  R['interactions']={'theme':'switch/reload','keyboard':'actual q -> Tab -> city with visible outline','paging':'3 pages, 5 pages, exact last, empty, explicit close, changed conditions reset','recovery':'real ES context release410, missing index502/reimport, ES stop503/restart with same Java process','change_close':'actual response200; cards/history/next reset'}
  c.close();browser.close()
 need(not R['js_errors'] and not R['request_failures'] and not R['direct_es_requests'],{k:R[k] for k in ['js_errors','request_failures','direct_es_requests']})
 R['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'backend/src').rglob('*') if p.is_file()}
 R['status']='passed'
except Exception:R['status']='failed';R['failure']=traceback.format_exc();raise
finally:
 R['external_operations']=lab.RECORD
 (H/'shell-review.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print(f'F11 shell passed: {len(R["matrix"])} groups, {len(R["actions"])} actual API actions')
