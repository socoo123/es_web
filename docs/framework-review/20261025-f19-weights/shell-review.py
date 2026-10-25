#!/usr/bin/env python3
"""F19 real browser -> Java -> ES. No mocked responses."""
import contextlib,copy,datetime,hashlib,importlib.util,json,pathlib,subprocess,traceback
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f19lab',P/'labs/f19/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
APP='http://127.0.0.1:18080'
def require(v,d):
 if not v:raise AssertionError(d)
def phase(name,action):
 with (HERE/(name+'.jsonl')).open('w') as out,contextlib.redirect_stdout(out):return action()
def shot(page,name,target=None):
 p=HERE/'screenshots'/('shell-'+name+'.png');p.parent.mkdir(exist_ok=True)
 if target:page.locator(target).first.screenshot(path=str(p),timeout=20000)
 else:page.screenshot(path=str(p),timeout=20000)
 return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'pending'}
def layout(page):
 r=page.evaluate('''() => ({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,theme:document.documentElement.dataset.theme,cards:[...document.querySelectorAll('.card')].map(e=>({id:e.dataset.id,width:e.clientWidth,scroll:e.scrollWidth})),pres:[...document.querySelectorAll('pre')].map(e=>({width:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX}))})''')
 require(r['page']<=r['viewport'] and r['body']<=r['viewport'],r);require(all(c['scroll']<=c['width'] for c in r['cards']),r);return r

def submit(page,i,expected=200,slug=None):
 for name in ['q','cityCode','mode','explainId']:
  el=page.locator('[name='+name+']')
  if name=='q':el.fill(i[name])
  else:el.select_option(i[name])
 page.locator('[name=budget]').fill(str(i['maxPriceFen']/100));page.locator('[name=nameWeight]').fill(str(i['nameWeight']))
 require(page.locator('.card').count()==0,'conditions clear cards');require(page.locator('#dsl-json').text_content()=='尚无本轮结果','conditions clear DSL')
 with page.expect_response(lambda r:r.url==APP+'/api/attractions/weight-search') as info:page.locator('#submit').click()
 response=info.value;r=response.json();require(response.status==expected,{'status':response.status,'response':r});page.wait_for_function("!document.getElementById('submit').disabled")
 if expected!=200:
  require(str(expected) in page.locator('#status').text_content(),r);require(page.locator('.card').count()==0,'error clears cards')
  for id in ['dsl-json','explain-json','result-json']:require(page.locator('#'+id).text_content()=='尚无本轮结果',id)
  return {'input':i,'status':response.status,'error':r,'layout':layout(page)}
 require(r['conditions']==i,'input');require(r['esRequest']['query']==r['explainRequest']['query'],'same complete query')
 if slug:require(lab.canonical(r['esRequest'])==lab.canonical(lab.load(slug)),slug+' actual DSL')
 for id,value in [('input-json',i),('dsl-json',r['esRequest']),('explain-json',r['explainResponse']),('result-json',r)]:require(json.loads(page.locator('#'+id).text_content())==value,id)
 require(page.locator('#total').text_content()==f"{r['total']} 份 · {r['relation']}",'total')
 cards=page.locator('.card');require(cards.count()==len(r['items']),'card count');ids=[]
 for n,item in enumerate(r['items']):
  card=cards.nth(n);ids.append(card.get_attribute('data-id'));require(ids[-1]==item['id'],'id');require(card.locator('h3').text_content()==item['name'],'name')
  require(card.locator('.description').text_content()==item['description'],'source description')
  require(card.locator('.score').text_content()=='_score = '+str(item['score']).removesuffix('.0'),'score')
  require(card.locator('.price').text_content()==f"{item['ticketPriceFen']/100:.2f} 元",'price')
  require(json.loads(card.locator('pre').text_content())==item['explanation'],'full explanation')
  children=[v for v in item['explanation'].get('details',[]) if v['value']>0]
  boxes=card.locator('.metrics');require(boxes.count()==len(children),'root contributions')
  for j,child in enumerate(children):
   require(boxes.nth(j).locator('strong').text_content()==child['description'],'contribution label')
   lab.close(float(boxes.nth(j).locator('span').text_content().split(' = ')[1]),child['value'])
 if slug:require(ids==lab.EXPECTED[slug],{'slug':slug,'ids':ids})
 matched=r['explainResponse']['matched'];require('matched='+str(matched).lower() in page.locator('#explain-note').text_content(),'matched')
 if not matched:require('不是候选得分' in page.locator('#explain-note').text_content(),'unmatched child explanation distinction')
 return {'input':i,'status':response.status,'ids':ids,'matched':matched,'layout':layout(page),'result':r}

record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F19 final jar / real browser Java ES; static tutorial reading recorded separately','matrix':[],'errors_and_recovery':[],'screenshots':[],'js_errors':[],'direct_es_requests':[],'api_calls':0}
try:
 phase('shell-setup',lab.prepare)
 with sync_playwright() as pw:
  b=pw.chromium.launch();record['browser']={'name':'Chromium','version':b.version}
  def context(width,theme):
   c=b.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
   c.add_init_script(f"if(!localStorage.getItem('travel-f19:theme')) localStorage.setItem('travel-f19:theme','{theme}')")
   def request(req):
    u=urlsplit(req.url)
    if u.hostname in ['localhost','127.0.0.1','::1'] and u.port in [9200,9201,19200,19214,19215,19216,19217,19218,19219]:record['direct_es_requests'].append(req.url)
    if req.url==APP+'/api/attractions/weight-search':record['api_calls']+=1
   c.on('request',request);c.on('pageerror',lambda e:record['js_errors'].append(str(e)));return c
  slugs=['sum','best','tie','tuned','optional','required','weighted','night-low','night-medium','night-tuned','spaced','other-city','zero-budget','empty']
  cases=[(s,lab.load('input-'+s),s) for s in slugs]
  for id in ['hz-closed','hz-expensive']:
   i=lab.load('input-tuned');i['explainId']=id;cases.append((id,i,None))
  for width in [1440,768,390]:
   print('Live observer width',width,flush=True)
   for theme in ['light','dark']:
    c=context(width,theme);page=c.new_page();page.goto(APP+'/f19.html',wait_until='networkidle');require(page.evaluate('document.documentElement.dataset.theme')==theme,'theme')
    if width in [1440,390]:record['screenshots'].append(shot(page,f'{width}-{theme}-opening'))
    for name,i,slug in cases:
     out=submit(page,i,slug=slug);out.update(width=width,theme=theme,case=name);record['matrix'].append(out)
     if name in ['hz-closed','hz-expensive']:require(not out['matched'],'excluded explanation')
     if width in [1440,390] and name in ['best','tuned','optional','night-tuned']:record['screenshots'].append(shot(page,f'{width}-{theme}-{name}','.results'))
    page.locator('#theme').click();page.reload(wait_until='networkidle');require(page.evaluate('document.documentElement.dataset.theme')!=theme,'theme reload')
    page.locator('[name=q]').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab');require(page.locator('[name=q]').evaluate("el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=='none'"),'actual keyboard focus');c.close()
  c=context(390,'dark');page=c.new_page();page.goto(APP+'/f19.html',wait_until='networkidle');page.locator('#search-form').evaluate('f=>f.noValidate=true')
  invalid=lab.load('input-tuned');invalid['q']=''
  record['errors_and_recovery'].append(submit(page,invalid,400));record['screenshots'].append(shot(page,'390-invalid-400','.results'))
  record['errors_and_recovery'].append(submit(page,lab.load('input-tuned')))
  def corrupt():
   lab.call('POST','/'+lab.INDEX+'/_update/hz-exact',{'doc':{'description':None}});lab.call('POST','/'+lab.INDEX+'/_refresh')
  phase('shell-corrupt',corrupt);record['errors_and_recovery'].append(submit(page,lab.load('input-tuned'),502));record['screenshots'].append(shot(page,'390-incomplete-502','.results'))
  def restore_doc():
   d=json.loads((P/'data/f19/attractions.json').read_text())[0];lab.call('PUT','/'+lab.INDEX+'/_doc/hz-exact',d);lab.call('POST','/'+lab.INDEX+'/_refresh')
  phase('shell-restore-doc',restore_doc);record['errors_and_recovery'].append(submit(page,lab.load('input-tuned')))
  phase('shell-delete',lambda:lab.call('DELETE','/'+lab.INDEX));record['errors_and_recovery'].append(submit(page,lab.load('input-tuned'),502));record['screenshots'].append(shot(page,'390-index-502','.results'))
  def restore():
   lab.call('PUT','/'+lab.INDEX,lab.load('index'));r=lab.call('POST','/'+lab.INDEX+'/_bulk',(P/'data/f19/attractions.ndjson').read_text(),ndjson=True);require(not r['errors'],'restore bulk');lab.call('POST','/'+lab.INDEX+'/_refresh')
  phase('shell-restore',restore);record['errors_and_recovery'].append(submit(page,lab.load('input-tuned')))
  r=subprocess.run(['docker','compose','-f',str(P/'infra/f19/compose.yaml'),'stop','es'],capture_output=True,text=True,timeout=50);require(r.returncode==0,r.stderr);record['stop']=r.__dict__
  record['errors_and_recovery'].append(submit(page,lab.load('input-tuned'),503));record['screenshots'].append(shot(page,'390-unavailable-503','.results'))
  r=subprocess.run(['docker','compose','-f',str(P/'infra/f19/compose.yaml'),'start','es'],capture_output=True,text=True,timeout=30);require(r.returncode==0,r.stderr);record['start']=r.__dict__
  r=subprocess.run(['bash',str(P/'infra/f19/wait.sh')],capture_output=True,text=True,timeout=60);require(r.returncode==0,r.stderr);record['ready']=r.__dict__
  record['errors_and_recovery'].append(submit(page,lab.load('input-tuned')));record['screenshots'].append(shot(page,'390-recovered','.results'));c.close();b.close()
 require(not record['js_errors'] and not record['direct_es_requests'],record)
 require(record['api_calls']==104,record['api_calls']);record['status']='passed';record['no_mock']=True
except Exception:
 record['status']='failed';record['failure']=traceback.format_exc();raise
finally:
 record['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'backend/target/travel-search-0.7.0.jar',*sorted((P/'backend/src/main/resources/static').glob('*f19*'))]}
 (HERE/'shell-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Live observer passed: 96 matrix, 104 actual Java API calls; 400/502 incomplete/502 missing/503 and recovery')
