#!/usr/bin/env python3
"""F24 real browser -> same Java PID -> isolated ES, including faults and recovery."""
import copy,datetime,gzip,hashlib,importlib.util,json,pathlib,subprocess,traceback
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import reading_helpers as h
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search';APP='http://127.0.0.1:18081'
spec=importlib.util.spec_from_file_location('f24lab',P/'labs/f24/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
MODES=lab.MODES;C=lab.read(P/'data/f24/contract.json')
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def layout(page):
 r=page.evaluate('''() => ({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,theme:document.documentElement.dataset.theme,cards:[...document.querySelectorAll('.card')].map(e=>({id:e.dataset.id,width:e.clientWidth,scroll:e.scrollWidth})),pres:[...document.querySelectorAll('pre')].map(e=>({width:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX}))})''');require(r['page']<=r['viewport'] and r['body']<=r['viewport'] and all(c['scroll']<=c['width'] for c in r['cards']),r);return r
def shot(page,name,target=None):
 p=HERE/'screenshots'/('shell-'+name+'.png');p.parent.mkdir(exist_ok=True)
 if target:page.locator(target).first.screenshot(path=str(p),timeout=20000)
 else:page.screenshot(path=str(p),timeout=20000)
 return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'pending'}
def submit(page,mode,status=200):
 page.locator('[name=mode]').select_option(mode);require(page.locator('.card').count()==0 and page.locator('#dsl-json').text_content()=='尚无本轮结果','change clears results')
 with page.expect_response(lambda r:r.url==APP+'/api/nested/inspect',timeout=60000) as info:page.locator('#submit').click()
 response=info.value;out=response.json();require(response.status==status,{'expected':status,'actual':response.status,'out':out});page.wait_for_function("!document.getElementById('submit').disabled")
 if status!=200:
  require(str(status) in page.locator('#status').text_content() and page.locator('.card').count()==0,'visible failure and no stale cards')
  for i in ['input-json','dsl-json','result-json']:require(page.locator('#'+i).text_content()=='尚无本轮结果','no stale '+i)
  return {'mode':mode,'status':status,'response':out,'layout':layout(page)}
 require(out['conditions']=={'mode':mode},'echo');require(json.loads(page.locator('#result-json').text_content())==out,'full DTO visible');require(json.loads(page.locator('#dsl-json').text_content())==out['esRequest'],'actual DSL visible');require(json.loads(page.locator('#input-json').text_content())==out['conditions'],'input visible')
 require([c['id'] for c in out['items']]==C['expected'][mode] and out['total']==len(C['expected'][mode]),'IDs/total');cards=page.locator('.card');require(cards.count()==len(out['items']),'card count');require(page.locator('#total').text_content()==str(out['total'])+' 家酒店 · '+out['model'],'unit hotels')
 for i,item in enumerate(out['items']):
  card=cards.nth(i);text=card.text_content();require(card.get_attribute('data-id')==item['id'] and card.locator('h3').text_content()==item['hotelName'],'identity text');require(item['source']==out['esResponse']['hits']['hits'][i]['_source'],'exact source');require('根_source含全部'+str(len(item['source']['rooms']))+'条报价' in text,'source untrimmed')
  if mode in ['object','split']:require('故意错误对照' in text and len(item['offers'])==0,'not sold as eligible')
  else:
   require('合格报价共 '+str(item['matchingOffers'])+' 条；inner_hits展示前 1 条' in text,'counts')
   inner=out['esResponse']['hits']['hits'][i]['inner_hits']['eligible']['hits'];require(item['matchingOffers']==inner['total']['value'],'inner total')
   for off in item['offers']:
    s=off['source'];require(s==inner['hits'][0]['_source'],'actual inner source');require('合格报价 CNY '+f"{s['price_minor']/100:.2f}"+' / 单晚' in text,'price unit')
    for key in ['offer_id','room_id','room_name','bed_type','meal','cancellation','rate_plan_id','currency','offer_status','service_date','snapshot_at']:require(str(s[key]) in text,'visible '+key)
  if mode.endswith('-sort'):require('排序值 CNY '+f"{item['sortPriceMinor']/100:.2f}"+' / 单晚' in text,'actual sort value');require(item['sortPriceMinor']==out['esResponse']['hits']['hits'][i]['sort'][0],'actual price')
  if mode=='filtered-sort':require(item['sortPriceMinor']==item['offers'][0]['priceMinor'],'sort and selected price agree')
 return {'mode':mode,'status':200,'ids':C['expected'][mode],'result':out,'layout':layout(page)}
def phase(name,fn):
 lab.COUNT=0;lab.LOG=HERE/(name+'.jsonl');require(not lab.LOG.exists(),'preserve prior '+name);value=fn();return {'http':lab.COUNT,'result':value}
def restore(hotel):
 lab.request('PUT','/tut-f24-nested/_doc/'+hotel['hotel_id'],hotel);lab.request('POST','/tut-f24-nested/_refresh')
def command(args):
 p=subprocess.run(args,cwd=P,text=True,capture_output=True);require(p.returncode==0,dict(command=args,stdout=p.stdout,stderr=p.stderr));return {'command':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def run():
 rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'actual local browser/Java/ES, no mocked responses','matrix':[],'errors_and_recovery':[],'screenshots':[],'js_errors':[],'direct_es_requests':[],'api_calls':0};full=[]
 try:
  rec['java_pid_before']=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip()
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=h.BROWSER);rec['browser']={'engine':'Chromium','version':browser.version}
   for width in [1440,768,390,320]:
    print('Shell',width,flush=True)
    for theme in ['light','dark']:
     ctx=browser.new_context(viewport={'width':width,'height':1000});ctx.add_init_script(f"if(!localStorage.getItem('travel-f24:theme'))localStorage.setItem('travel-f24:theme','{theme}')");page=ctx.new_page();page.on('pageerror',lambda e:rec['js_errors'].append(str(e)))
     def req(r):
      if r.url==APP+'/api/nested/inspect':rec['api_calls']+=1
      u=urlsplit(r.url)
      if u.hostname in ['127.0.0.1','localhost'] and u.port in [19224,9200,9201]:rec['direct_es_requests'].append(r.url)
     page.on('request',req);page.goto(APP+'/f24.html',wait_until='networkidle');require(page.locator('html').get_attribute('data-theme')==theme,'shell theme');layout(page)
     for mode in MODES:
      report=submit(page,mode);full.append({'width':width,'theme':theme,**report});rec['matrix'].append({'width':width,'theme':theme,'mode':mode,'ids':report['ids'],'layout':report['layout']})
     if width in [1440,390,320]:
      rec['screenshots'].append(shot(page,f'{width}-{theme}-filtered'));rec['screenshots'].append(shot(page,f'{width}-{theme}-cards','#cards'))
     page.locator('#theme').click();require(page.locator('html').get_attribute('data-theme')!=theme,'theme switch');page.reload(wait_until='networkidle');require(page.locator('html').get_attribute('data-theme')!=theme,'shell reload persists');ctx.close()
   ctx=browser.new_context(viewport={'width':390,'height':1000});page=ctx.new_page();page.on('pageerror',lambda e:rec['js_errors'].append(str(e)));page.on('request',lambda r:rec.__setitem__('api_calls',rec['api_calls']+1) if r.url==APP+'/api/nested/inspect' else None);page.goto(APP+'/f24.html',wait_until='networkidle')
   page.locator('[name=mode]').evaluate("e=>e.add(new Option('invalid','invalid'))");rec['errors_and_recovery'].append(submit(page,'invalid',400));rec['errors_and_recovery'].append(submit(page,'filtered-sort'))
   canonical=next(x for x in lab.read(P/'data/f24/hotels.json') if x['hotel_id']=='h03')
   bad=copy.deepcopy(canonical);bad['hotel_name']=None;rec['root_corruption']=phase('shell-corrupt-hotel',lambda:restore(bad));rec['errors_and_recovery'].append(submit(page,'filtered-sort',502));rec['screenshots'].append(shot(page,'502-incomplete'));rec['root_restore']=phase('shell-restore-hotel',lambda:restore(canonical));rec['errors_and_recovery'].append(submit(page,'filtered-sort'))
   bad=copy.deepcopy(canonical);bad['rooms'][0]['room_name']=None;rec['inner_corruption']=phase('shell-corrupt-inner',lambda:restore(bad));rec['errors_and_recovery'].append(submit(page,'filtered-sort',502));rec['inner_restore']=phase('shell-restore-inner',lambda:restore(canonical));rec['errors_and_recovery'].append(submit(page,'filtered-sort'))
   rec['delete_index']=phase('shell-delete-index',lambda:lab.request('DELETE','/tut-f24-nested'));rec['errors_and_recovery'].append(submit(page,'filtered-sort',502))
   def restore_index():
    lab.request('PUT','/tut-f24-nested',lab.read(P/'search/f24/nested-index.json'));b=lab.request('POST','/tut-f24-nested/_bulk',(P/'data/f24/hotels.ndjson').read_text());require(not b['errors'],'restore bulk');lab.request('POST','/tut-f24-nested/_refresh')
   rec['restore_index']=phase('shell-restore-index',restore_index);rec['errors_and_recovery'].append(submit(page,'filtered-sort'))
   rec['stop_es']=command(['docker','compose','-f','infra/f24/compose.yaml','stop','-t','5','es']);rec['errors_and_recovery'].append(submit(page,'filtered-sort',503));rec['screenshots'].append(shot(page,'503-stopped'));rec['start_es']=command(['docker','compose','-f','infra/f24/compose.yaml','start','es']);rec['wait_es']=command(['bash','infra/f24/wait.sh']);rec['errors_and_recovery'].append(submit(page,'filtered-sort'));rec['screenshots'].append(shot(page,'recovered'))
   rec['java_pid_after']=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip();require(rec['java_pid_before']==rec['java_pid_after'],'same app process across faults');ctx.close();browser.close()
  require(not rec['js_errors'] and not rec['direct_es_requests'] and rec['api_calls']==50,'50 actual Java calls, no direct ES/JS errors');rec['status']='passed'
 except Exception as e:rec['status']='failed';rec['error']=str(e);rec['traceback']=traceback.format_exc();raise
 finally:
  with gzip.open(HERE/'shell-review-full.json.gz','wt') as f:json.dump({'matrix':full,'errors':rec['errors_and_recovery']},f,ensure_ascii=False)
  # Preserve full successful results in gzip; concise receipt retains actual IDs and statuses.
  for r in rec['errors_and_recovery']:r.pop('result',None)
  (HERE/'shell-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
 print('F24 actual shell passed 40 matrix +10 fault/recovery calls, same PID')
if __name__=='__main__':run()
