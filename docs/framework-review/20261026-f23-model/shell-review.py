#!/usr/bin/env python3
"""F23 actual browser -> Java -> ES, fixed source projection and recovery."""
import copy,datetime,gzip,hashlib,importlib.util,json,os,pathlib,subprocess,traceback
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search';APP='http://127.0.0.1:18081'
BROWSER=os.environ.get('F23_BROWSER_EXECUTABLE',str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
spec=importlib.util.spec_from_file_location('f23lab',P/'labs/f23/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
MODES=['hotel','object','nested','offers-flex','offers-budget'];EXPECTED={'hotel':['h01'],'object':['h01'],'nested':['h01'],'offers-flex':['o101','o201'],'offers-budget':['o102','o104','o203']}
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def phase(name,fn):
 lab.COUNT=0;lab.LOG=HERE/(name+'.jsonl');require(not lab.LOG.exists(),'preserve previous '+name);r=fn();return {'http':lab.COUNT,'result':r}
def layout(page):
 r=page.evaluate('''() => ({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,theme:document.documentElement.dataset.theme,cards:[...document.querySelectorAll('.card')].map(e=>({id:e.dataset.id,width:e.clientWidth,scroll:e.scrollWidth})),pres:[...document.querySelectorAll('pre')].map(e=>({width:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX}))})''')
 require(r['page']<=r['viewport'] and r['body']<=r['viewport'],r);require(all(c['scroll']<=c['width'] for c in r['cards']),r);return r
def shot(page,name,target=None):
 p=HERE/'screenshots'/('shell-'+name+'.png');p.parent.mkdir(exist_ok=True)
 if target:page.locator(target).first.screenshot(path=str(p),timeout=20000)
 else:page.screenshot(path=str(p),timeout=20000)
 return {'path':str(p.relative_to(R)),'sha256':sha(p),'visual_review':'pending'}
def submit(page,mode,status=200):
 page.locator('[name=mode]').select_option(mode)
 require(page.locator('.card').count()==0 and page.locator('#dsl-json').text_content()=='尚无本轮结果','input change clears old results')
 with page.expect_response(lambda r:r.url==APP+'/api/model/inspect') as info:page.locator('#submit').click()
 response=info.value;out=response.json();require(response.status==status,{'expected':status,'actual':response.status,'out':out})
 page.wait_for_function("!document.getElementById('submit').disabled")
 if status!=200:
  require(str(status) in page.locator('#status').text_content() and page.locator('.card').count()==0,'visible error and cleared cards')
  for i in ['input-json','dsl-json','result-json']:require(page.locator('#'+i).text_content()=='尚无本轮结果','cleared '+i)
  return {'mode':mode,'status':status,'out':out,'layout':layout(page)}
 require(out['conditions']=={'mode':mode},'condition echo')
 require(json.loads(page.locator('#result-json').text_content())==out,'complete DTO/typed client response rendered')
 require(json.loads(page.locator('#input-json').text_content())==out['conditions'],'input rendered')
 require(json.loads(page.locator('#dsl-json').text_content())==out['esRequest'],'actual full DSL rendered')
 cards=page.locator('.card');require(cards.count()==len(EXPECTED[mode]),'card count')
 require([x['id'] for x in out['items']]==EXPECTED[mode] and out['total']==len(EXPECTED[mode]),'IDs/total')
 label=str(out['total'])+(' 条报价' if out['model']=='offers' else ' 家酒店')+' · '+out['model']
 require(page.locator('#total').text_content()==label,'unit of count')
 for i,item in enumerate(out['items']):
  card=cards.nth(i);s=item['source'];hit=out['esResponse']['hits']['hits'][i]
  require(card.get_attribute('data-id')==item['id'] and hit['_id']==item['id'] and hit['_source']==s,'card/source/hit exact')
  require(card.locator('h3').text_content()==s['hotel_name'],'name text')
  text=card.text_content()
  require(s['hotel_id'] in text and s['hotel_status'] in text,'hotel identity/status')
  if out['model']=='offers':
   require(card.locator('.price').text_content()==f"{s['currency']} {s['price_minor']/100:.2f} / 单晚",'amount/currency/unit')
   for key in ['offer_id','room_id','room_name','bed_type','rate_plan_id','meal','cancellation','service_date','offer_status','snapshot_at']:require(str(s[key]) in text,'rendered '+key)
  elif out['model']!='hotels':
   require(card.locator('li').count()==len(s['rooms']),'all source rooms, no automatic filtering')
   for room in s['rooms']:require(room['room_id'] in text and room['room_name'] in text,'room identity')
   require('rates为object' in text,'scope boundary visible')
  else:require('不含房型' in text,'hotel only boundary')
 return {'mode':mode,'status':200,'ids':EXPECTED[mode],'layout':layout(page),'result':out}
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F23 final jar real local browser/Java/ES; no mocked responses','matrix':[],'errors_and_recovery':[],'screenshots':[],'js_errors':[],'direct_es_requests':[],'api_calls':0}
try:
 record['java_pid_before']=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=BROWSER);record['browser']={'engine':'Chromium','version':browser.version,'executable':BROWSER}
  def context(width,theme):
   c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
   c.add_init_script(f"if(!localStorage.getItem('travel-f23:theme'))localStorage.setItem('travel-f23:theme','{theme}')")
   def request(req):
    u=urlsplit(req.url)
    if u.hostname in ['localhost','127.0.0.1','::1'] and u.port in [9200,9201,19200,19214,19215,19216,19217,19218,19219,19220,19221,19222,19223]:record['direct_es_requests'].append(req.url)
    if req.url==APP+'/api/model/inspect':record['api_calls']+=1
   c.on('request',request);c.on('pageerror',lambda e:record['js_errors'].append(str(e)));return c
  for width in [1440,768,390,320]:
   print('Live model observer width',width,flush=True)
   for theme in ['light','dark']:
    c=context(width,theme);page=c.new_page();page.goto(APP+'/f23.html',wait_until='networkidle');require(page.evaluate('document.documentElement.dataset.theme')==theme,'initial theme')
    if width in [1440,390]:record['screenshots'].append(shot(page,f'{width}-{theme}-opening'))
    if width==320:record['screenshots'].append(shot(page,f'{width}-{theme}-form','#search-form'))
    for mode in MODES:
     out=submit(page,mode);out.update(width=width,theme=theme);record['matrix'].append(out)
     if width in [1440,390]:record['screenshots'].append(shot(page,f'{width}-{theme}-{mode}','.results'))
    page.locator('#theme').click();page.reload(wait_until='networkidle');require(page.evaluate('document.documentElement.dataset.theme')!=theme,'theme persists')
    page.locator('[name=mode]').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab');require(page.locator('[name=mode]').evaluate("e=>e===document.activeElement && getComputedStyle(e).outlineStyle!=='none'"),'actual Tab visible focus');c.close()
  c=context(390,'dark');page=c.new_page();page.goto(APP+'/f23.html',wait_until='networkidle')
  page.locator('[name=mode]').evaluate("e=>{var o=document.createElement('option');o.value='invalid';o.textContent='非法输入探针';e.appendChild(o)}")
  record['errors_and_recovery'].append(submit(page,'invalid',400));record['screenshots'].append(shot(page,'390-invalid-400','.results'))
  record['errors_and_recovery'].append(submit(page,'offers-flex'))
  source=next(d for d in json.loads((P/'data/f23/offers.json').read_text()) if d['offer_id']=='o101')
  phase('shell-corrupt-offer',lambda:lab.request('POST','/tut-f23-offers/_update/o101?refresh=true',{'doc':{'hotel_name':None}}))
  record['errors_and_recovery'].append(submit(page,'offers-flex',502));record['screenshots'].append(shot(page,'390-incomplete-502','.results'))
  phase('shell-restore-offer',lambda:lab.request('PUT','/tut-f23-offers/_doc/o101?refresh=true',source));record['errors_and_recovery'].append(submit(page,'offers-flex'))
  nested=json.loads((P/'data/f23/nested.json').read_text())[0];corrupt=copy.deepcopy(nested);corrupt['rooms'][0]['rates']=None
  phase('shell-corrupt-room',lambda:lab.request('PUT','/tut-f23-nested/_doc/h01?refresh=true',corrupt))
  record['errors_and_recovery'].append(submit(page,'nested',502));record['screenshots'].append(shot(page,'390-room-502','.results'))
  phase('shell-restore-room',lambda:lab.request('PUT','/tut-f23-nested/_doc/h01?refresh=true',nested));record['errors_and_recovery'].append(submit(page,'nested'))
  phase('shell-delete',lambda:lab.request('DELETE','/tut-f23-offers'))
  record['errors_and_recovery'].append(submit(page,'offers-flex',502));record['screenshots'].append(shot(page,'390-index-502','.results'))
  def restore():
   lab.request('PUT','/tut-f23-offers',lab.read(lab.SEARCH/'offers-index.json'))
   b=lab.request('POST','/tut-f23-offers/_bulk',(lab.DATA/'offers.ndjson').read_text());require(not b['errors'],'restore bulk')
   lab.request('POST','/tut-f23-offers/_refresh')
  phase('shell-restore-index',restore);record['errors_and_recovery'].append(submit(page,'offers-flex'))
  for action in ['stop','start']:
   p=subprocess.run(['docker','compose','-f',str(P/'infra/f23/compose.yaml'),action,'es'],text=True,capture_output=True,timeout=50);require(p.returncode==0,p.stderr);record[action]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
   if action=='stop':
    record['errors_and_recovery'].append(submit(page,'offers-flex',503));record['screenshots'].append(shot(page,'390-unavailable-503','.results'))
   else:
    ready=subprocess.run(['bash',str(P/'infra/f23/wait.sh')],text=True,capture_output=True,timeout=60);require(ready.returncode==0,ready.stderr);record['ready']={'returncode':ready.returncode,'stdout':ready.stdout,'stderr':ready.stderr}
    record['errors_and_recovery'].append(submit(page,'offers-flex'));record['screenshots'].append(shot(page,'390-recovered','.results'))
  c.close();browser.close()
 require(not record['js_errors'] and not record['direct_es_requests'],record)
 require(record['api_calls']==50,record['api_calls'])
 record['java_pid_after']=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip();require(record['java_pid_before']==record['java_pid_after'],'same Java process recovery')
 record['status']='passed';record['no_mock']=True
except Exception:record['status']='failed';record['failure']=traceback.format_exc();raise
finally:
 record['sha256']={str(p.relative_to(R)):sha(p) for p in [P/'backend/target/travel-search-0.7.0.jar',*sorted((P/'backend/src/main/resources/static').glob('*f23*'))]}
 full=json.dumps(record,ensure_ascii=False,indent=2).encode();target=HERE/'shell-review-full.json.gz';target.write_bytes(gzip.compress(full,mtime=0));record['full_record']={'path':str(target.relative_to(R)),'sha256':sha(target),'uncompressed_sha256':hashlib.sha256(full).hexdigest()}
 for row in record['matrix']+record['errors_and_recovery']:row.pop('result',None)
 (HERE/'shell-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F23 live browser passed: 40 matrix +10 errors/recoveries =50 actual Java calls')
