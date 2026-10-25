#!/usr/bin/env python3
"""Real F18 browser -> final Java -> ES verification. No request mocking."""
import contextlib,copy,datetime,hashlib,importlib.util,json,pathlib,subprocess,time,traceback
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f18lab',P/'labs/f18/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
APP='http://127.0.0.1:18080'

def require(value,detail):
 if not value:raise AssertionError(detail)
def phase(name,action):
 with (HERE/(name+'.jsonl')).open('w') as out,contextlib.redirect_stdout(out):return action()
def shot(page,name,target=None):
 p=HERE/'screenshots'/('shell-'+name+'.png');(p.parent).mkdir(exist_ok=True)
 if target:page.locator(target).first.screenshot(path=str(p),timeout=20000)
 else:page.screenshot(path=str(p),timeout=20000)
 return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'pending'}
def layout(page):
 r=page.evaluate('''() => ({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,theme:document.documentElement.dataset.theme,cards:[...document.querySelectorAll('.card')].map(e=>({id:e.dataset.id,width:e.clientWidth,scroll:e.scrollWidth})),pres:[...document.querySelectorAll('pre')].map(e=>({width:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX}))})''')
 require(r['page']<=r['viewport'] and r['body']<=r['viewport'],r)
 require(all(c['scroll']<=c['width'] for c in r['cards']),r)
 return r

def submit(page,input,expected_status=200):
 page.locator('[name=q]').fill(input['q'])
 page.locator('[name=cityCode]').select_option(input['cityCode'])
 page.locator('[name=budget]').fill(str(input['maxPriceFen']/100))
 page.locator('[name=mode]').select_option(input['mode'])
 page.locator('[name=explainId]').select_option(input['explainId'])
 require(page.locator('.card').count()==0,'conditions must clear old cards')
 require(page.locator('#dsl-json').text_content()=='尚无本轮结果','conditions must clear old DSL')
 with page.expect_response(lambda r:r.url==APP+'/api/attractions/score-search') as info:page.locator('#submit').click()
 response=info.value;result=response.json();require(response.status==expected_status,{'status':response.status,'result':result})
 page.wait_for_function("!document.getElementById('submit').disabled")
 if expected_status!=200:
  require(str(expected_status) in page.locator('#status').text_content(),result)
  require(page.locator('.card').count()==0,'error clears old cards')
  require(page.locator('#result-json').text_content()=='尚无本轮结果','error clears response')
  require(page.locator('#explain-json').text_content()=='尚无本轮结果','error clears explanation')
  return {'input':input,'status':response.status,'error':result,'layout':layout(page)}
 require(result['conditions']==input,'input echo')
 require(result['esRequest']['query']==result['explainRequest']['query'],'same complete query')
 for id,value in [('input-json',input),('dsl-json',result['esRequest']),('explain-json',result['explainResponse']),('result-json',result)]:require(json.loads(page.locator('#'+id).text_content())==value,{'json':id})
 cards=page.locator('.card');require(cards.count()==len(result['items']),'card count')
 ids=[];metrics=[]
 for i,item in enumerate(result['items']):
  card=cards.nth(i);ids.append(card.get_attribute('data-id'))
  require(ids[-1]==item['id'] and card.locator('h3').text_content()==item['name'],'ID/name')
  require(card.locator('.description').text_content()==item['description'],'description source')
  require(card.locator('.score').text_content()=='_score = '+str(item['score']).removesuffix('.0'),'score')
  require(card.locator('.price').text_content()==f"{item['ticketPriceFen']/100:.2f} 元",'integer price display')
  require(json.loads(card.locator('pre').text_content())==item['explanation'],'complete explanation')
  terms=lab.terms(item['explanation']);boxes=card.locator('.metrics');require(boxes.count()==len(terms),'metric count')
  for j,(term,values) in enumerate(terms.items()):
   box=boxes.nth(j);require(box.locator('strong').text_content()==term+' · 简介词项','term label')
   for key in ['freq','n','N','dl','avgdl','idf','tf','boost','k1','b']:
    span=box.locator('span').filter(has_text=key+' = ').first
    # n and N are case-sensitive in the literal text.
    matches=[s for s in box.locator('span').all_text_contents() if s.startswith(key+' = ')]
    require(len(matches)==1,{'key':key,'matches':matches});lab.close(float(matches[0].split(' = ')[1]),values[key])
   metrics.append({'id':item['id'],'term':term,'values':values})
 matched=result['explainResponse']['matched']
 require(f'matched={str(matched).lower()}' in page.locator('#explain-note').text_content(),'matched indicator')
 if not matched:require('不是候选得分' in page.locator('#explain-note').text_content(),'unmatched root vs child explanation note')
 require(page.locator('#total').text_content()==f"{result['total']} 份 · {result['relation']}",'total')
 return {'input':input,'status':response.status,'ids':ids,'matched':matched,'metrics':metrics,'layout':layout(page),'result':result}

record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F18 live local observer; browser calls Java, final jar calls real ES','matrix':[],'stage_comparison':[],'errors_and_recovery':[],'screenshots':[],'js_errors':[],'direct_es_requests':[],'api_calls':0}
try:
 phase('shell-setup',lab.prepare)
 with sync_playwright() as pw:
  browser=pw.chromium.launch();record['browser']={'name':'Chromium','version':browser.version}
  def context(width,theme):
   c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
   c.add_init_script(f"if(!localStorage.getItem('travel-f18:theme')) localStorage.setItem('travel-f18:theme','{theme}')")
   def request(req):
    u=urlsplit(req.url)
    if u.hostname in ['localhost','127.0.0.1','::1'] and u.port in [9200,9201,19200,19214,19215,19216,19217,19218]:record['direct_es_requests'].append(req.url)
    if req.url==APP+'/api/attractions/score-search':record['api_calls']+=1
   c.on('request',request);c.on('pageerror',lambda e:record['js_errors'].append(str(e)))
   return c
  c=context(1440,'light');page=c.new_page();page.goto(APP+'/f18.html',wait_until='networkidle')
  first=submit(page,lab.load('input-scored'));require(first['metrics'][0]['values']['N']==9,'initial N')
  record['stage_comparison'].append(first);record['screenshots'].append(shot(page,'1440-light-initial','.results'))
  phase('shell-append',lab.unrelated)
  second=submit(page,lab.load('input-scored'));require(second['metrics'][0]['values']['N']==15,'appended N')
  require(first['ids']==second['ids'] and first['result']['items'][0]['score']!=second['result']['items'][0]['score'],'same candidates changed score')
  record['stage_comparison'].append(second);c.close()
  cases=[(slug,lab.load('input-'+slug)) for slug in ['scored','filtered','city-scored','rare','other-city','zero-budget','empty']]
  for id in ['hz-closed','hz-missing','hz-other']:
   i=lab.load('input-scored');i['explainId']=id;cases.append((id,i))
  i=lab.load('input-zero-budget');i['explainId']='hz-night';cases.append(('price-excluded',i))
  for width in [1440,768,390]:
   print('Live observer width',width,flush=True)
   for theme in ['light','dark']:
    c=context(width,theme);page=c.new_page();page.goto(APP+'/f18.html',wait_until='networkidle')
    require(page.evaluate('document.documentElement.dataset.theme')==theme,'theme')
    if width in [1440,390]:record['screenshots'].append(shot(page,f'{width}-{theme}-opening'))
    for name,input in cases:
     out=submit(page,input);out.update({'width':width,'theme':theme,'case':name});record['matrix'].append(out)
     if name in ['hz-closed','hz-missing','hz-other','price-excluded']:require(not out['matched'],'excluded explanation')
     if width in [1440,390] and name in ['scored','filtered','rare']:
      record['screenshots'].append(shot(page,f'{width}-{theme}-{name}','.results'))
    page.locator('#theme').click();page.reload(wait_until='networkidle')
    require(page.evaluate('document.documentElement.dataset.theme')!=theme,'theme persists after reload')
    page.locator('[name=q]').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
    require(page.locator('[name=q]').evaluate("el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=='none'"),'actual keyboard focus')
    c.close()
  c=context(390,'dark');page=c.new_page();page.goto(APP+'/f18.html',wait_until='networkidle')
  page.locator('#search-form').evaluate('f=>f.noValidate=true')
  invalid=lab.load('input-scored');invalid['q']=''
  record['errors_and_recovery'].append(submit(page,invalid,400));record['screenshots'].append(shot(page,'390-invalid-400','.results'))
  phase('shell-delete',lambda:lab.call('DELETE','/'+lab.INDEX))
  record['errors_and_recovery'].append(submit(page,lab.load('input-scored'),502));record['screenshots'].append(shot(page,'390-index-502','.results'))
  def restore():
   lab.call('PUT','/'+lab.INDEX,lab.load('index'))
   for file in ['attractions','unrelated']:
    r=lab.call('POST','/'+lab.INDEX+'/_bulk',(P/f'data/f18/{file}.ndjson').read_text(),ndjson=True);require(not r['errors'],'restore bulk')
   lab.refresh()
  phase('shell-restore',restore)
  record['errors_and_recovery'].append(submit(page,lab.load('input-scored')))
  record['stop']=subprocess.run(['docker','compose','-f',str(P/'infra/f18/compose.yaml'),'stop','es'],capture_output=True,text=True,timeout=50).__dict__
  record['errors_and_recovery'].append(submit(page,lab.load('input-scored'),503));record['screenshots'].append(shot(page,'390-unavailable-503','.results'))
  record['start']=subprocess.run(['docker','compose','-f',str(P/'infra/f18/compose.yaml'),'start','es'],capture_output=True,text=True,timeout=30).__dict__
  ready=subprocess.run(['bash',str(P/'infra/f18/wait.sh')],capture_output=True,text=True,timeout=60);require(ready.returncode==0,ready.stderr);record['ready']={'stdout':ready.stdout,'returncode':ready.returncode}
  recovery=submit(page,lab.load('input-scored'));record['errors_and_recovery'].append(recovery)
  record['screenshots'].append(shot(page,'390-recovered','.results'))
  c.close();browser.close()
 require(not record['js_errors'] and not record['direct_es_requests'],record)
 require(record['api_calls']==73,record['api_calls'])
 record['status']='passed';record['no_mock']=True
except Exception:
 record['status']='failed';record['failure']=traceback.format_exc();raise
finally:
 # CompletedProcess.__dict__ contains only args, stdout, stderr, returncode.
 record['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'backend/target/travel-search-0.7.0.jar',*sorted((P/'backend/src/main/resources/static').glob('*f18*'))]}
 (HERE/'shell-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Live observer passed: 66 matrix cases, 73 actual Java API calls, baseline/append and 400/502/503 recovery')
