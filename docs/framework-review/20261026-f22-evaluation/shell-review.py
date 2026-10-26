#!/usr/bin/env python3
"""F22 real browser -> Java -> ES, with actual failures and same-process recovery."""
import datetime,gzip,hashlib,importlib.util,json,pathlib,subprocess,traceback
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import os
BROWSER = os.environ.get("F22_BROWSER_EXECUTABLE", str(pathlib.Path.home()/"Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search';APP='http://127.0.0.1:18081'
spec=importlib.util.spec_from_file_location('f22lab',P/'labs/f22/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
def require(v,d):
 if not v:raise AssertionError(d)
def phase(name,fn):
 lab.COUNT=0;lab.LOG=HERE/(name+'.jsonl');lab.LOG.write_text('');r=fn();return {'http':lab.COUNT,'result':r}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def shot(page,name,target=None):
 p=HERE/'screenshots'/('shell-'+name+'.png');p.parent.mkdir(exist_ok=True)
 if target:page.locator(target).first.screenshot(path=str(p),timeout=20000)
 else:page.screenshot(path=str(p),timeout=20000)
 return {'path':str(p.relative_to(R)),'sha256':sha(p),'visual_review':'pending'}
def layout(page):
 out=page.evaluate('''() => ({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,theme:document.documentElement.dataset.theme,cards:[...document.querySelectorAll('.card')].map(e=>({id:e.dataset.id,width:e.clientWidth,scroll:e.scrollWidth})),pres:[...document.querySelectorAll('pre')].map(e=>({width:e.clientWidth,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX}))})''')
 require(out['page']<=out['viewport'] and out['body']<=out['viewport'],out)
 require(all(c['scroll']<=c['width'] for c in out['cards']),out)
 return out

def submit(page,inp,expected=200):
 for name,value in inp.items():page.locator('[name='+name+']').select_option(value)
 require(page.locator('.card').count()==0 and page.locator('#macro p').count()==0,'conditions clear results')
 require(page.locator('#dsl-json').text_content()=='尚无本轮结果','conditions clear DSL')
 with page.expect_response(lambda r:r.url==APP+'/api/quality/evaluate') as info:page.locator('#submit').click()
 response=info.value;out=response.json();require(response.status==expected,{'status':response.status,'body':out})
 page.wait_for_function("!document.getElementById('submit').disabled")
 if expected!=200:
  require(str(expected) in page.locator('#status').text_content(),'visible error')
  require(page.locator('.card').count()==0 and page.locator('#macro p').count()==0,'failed result cleared')
  for id in ['input-json','dsl-json','result-json']:require(page.locator('#'+id).text_content()=='尚无本轮结果',id)
  return {'input':inp,'status':expected,'response':out,'layout':layout(page)}
 require(out['conditions']==inp,'input echo')
 require(json.loads(page.locator('#input-json').text_content())==inp,'rendered input')
 require(json.loads(page.locator('#result-json').text_content())==out,'complete rendered DTO/ES response')
 require(json.loads(page.locator('#dsl-json').text_content())==[{'id':q['id'],'request':q['esRequest']} for q in out['queries']],'complete rendered DSL')
 require(page.locator('#total').text_content()==f"{len(out['queries'])} 查询 · {out['fixtureVersion']}",'query count')
 require([e.text_content() for e in page.locator('#macro p').all()]==[f"Recall@10 = {out['macro']['recall']:.6f}",f"nDCG@10 = {out['macro']['ndcg']:.6f}"],'macro labels')
 tasks=lab.selected(inp['split']);cards=page.locator('.card');require(cards.count()==len(tasks),'card count')
 for i,(task,q) in enumerate(zip(tasks,out['queries'])):
  card=cards.nth(i);require(card.get_attribute('data-id')==task['id'] and card.locator('h3').text_content()==task['text'],'query id/text')
  require(card.locator('.intent').text_content()==task['intent'],'query intent')
  require(q['esRequest']==lab.query(task['text'],inp['strategy']),'actual DSL')
  metric=lab.metrics(q['ids'],task['ratings'])
  for key in ['recall','ndcg','dcg','ideal_dcg']:require(abs(q[key]-metric[key])<1e-12,'metric '+key)
  require(card.locator('.quality').nth(0).text_content()==f"Recall@10={q['recall']:.6f} · nDCG@10={q['ndcg']:.6f}",'query metric text')
  require(card.locator('.quality').nth(1).text_content()==f"相关 {q['relevant_retrieved']}/{q['relevant_docs']} · DCG={q['dcg']:.6f} · IDCG={q['ideal_dcg']:.6f}",'denominators')
  items=card.locator('.ranking li');require(items.count()==10,'top10 visible')
  for n,item in enumerate(items.all()):
   hit=q['esResponse']['hits']['hits'][n];grade=q['grades'][n]
   require(q['ids'][n]==hit['_id'] and grade==task['ratings'][hit['_id']],'id/grade')
   require(item.get_attribute('data-grade')==str(grade),'rendered grade')
   require(item.evaluate('e=>e.firstChild.textContent')==hit['_source']['name'],'name as text')
   require(item.locator('span').evaluate("(e,v)=>e.textContent===v.id+' · 人工等级='+v.grade+' · ES_score='+v.score",{'id':hit['_id'],'grade':grade,'score':hit['_score']}),'score and grade distinct')
 return {'input':inp,'status':200,'macro':out['macro'],'ids':{q['id']:q['ids'] for q in out['queries']},'layout':layout(page),'result':out}

record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F22 final jar actual local browser/Java/ES; no mock responses','matrix':[],'errors_and_recovery':[],'screenshots':[],'js_errors':[],'direct_es_requests':[],'api_calls':0}
try:
 pid=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip();record['java_pid_before']=pid
 # Formal two-round run leaves the exact fixture intact. Confirm before browser tests.
 lab.LOG=HERE/'shell-fixture.jsonl';lab.LOG.write_text('');r=lab.request('GET','/'+lab.INDEX+'/_count');require(r['count']==24,'fixture intact')
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=BROWSER);record['browser']={'name':'Chromium','version':browser.version}
  def context(width,theme):
   c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
   c.add_init_script(f"if(!localStorage.getItem('travel-f22:theme'))localStorage.setItem('travel-f22:theme','{theme}')")
   def request(req):
    u=urlsplit(req.url)
    if u.hostname in ['localhost','127.0.0.1','::1'] and u.port in [9200,9201,19200,19214,19215,19216,19217,19218,19219,19220,19221,19222]:record['direct_es_requests'].append(req.url)
    if req.url==APP+'/api/quality/evaluate':record['api_calls']+=1
   c.on('request',request);c.on('pageerror',lambda e:record['js_errors'].append(str(e)));return c
  for width in [1440,768,390]:
   print('Live quality observer width',width,flush=True)
   for theme in ['light','dark']:
    c=context(width,theme);page=c.new_page();page.goto(APP+'/f22.html',wait_until='networkidle');require(page.evaluate('document.documentElement.dataset.theme')==theme,'theme')
    if width in [1440,390]:record['screenshots'].append(shot(page,f'{width}-{theme}-opening'))
    for split in ['adjust','holdout','assessment']:
     for strategy in ['baseline','candidate']:
      out=submit(page,{'split':split,'strategy':strategy});out.update(width=width,theme=theme);record['matrix'].append(out)
      if width in [1440,390] and (split=='adjust' or strategy=='candidate'):
       record['screenshots'].append(shot(page,f'{width}-{theme}-{split}-{strategy}','.results'))
    page.locator('#theme').click();page.reload(wait_until='networkidle');require(page.evaluate('document.documentElement.dataset.theme')!=theme,'theme persists')
    page.locator('[name=split]').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab');require(page.locator('[name=split]').evaluate("e=>e===document.activeElement && getComputedStyle(e).outlineStyle!=='none'"),'visible actual Tab focus');c.close()
  c=context(390,'dark');page=c.new_page();page.goto(APP+'/f22.html',wait_until='networkidle')
  page.locator('[name=split]').evaluate("e=>{var o=document.createElement('option');o.value='invalid';o.textContent='非法输入探针';e.appendChild(o)}")
  record['errors_and_recovery'].append(submit(page,{'split':'invalid','strategy':'baseline'},400));record['screenshots'].append(shot(page,'390-invalid-400','.results'))
  good={'split':'adjust','strategy':'baseline'}
  record['errors_and_recovery'].append(submit(page,good))
  source=next(d for d in json.loads((P/'data/f22/attractions.json').read_text()) if d['attraction_id']=='a15')
  phase('shell-corrupt',lambda:lab.request('POST','/'+lab.INDEX+'/_update/a15?refresh=true',{'doc':{'name':None}}))
  record['errors_and_recovery'].append(submit(page,good,502));record['screenshots'].append(shot(page,'390-incomplete-502','.results'))
  phase('shell-restore-doc',lambda:lab.request('PUT','/'+lab.INDEX+'/_doc/a15?refresh=true',source))
  record['errors_and_recovery'].append(submit(page,good))
  phase('shell-delete',lambda:lab.request('DELETE','/'+lab.INDEX))
  record['errors_and_recovery'].append(submit(page,good,502));record['screenshots'].append(shot(page,'390-index-502','.results'))
  phase('shell-restore',lab.prepare);record['errors_and_recovery'].append(submit(page,good))
  stopped=subprocess.run(['docker','compose','-f',str(P/'infra/f22/compose.yaml'),'stop','es'],capture_output=True,text=True,timeout=50);require(stopped.returncode==0,stopped.stderr);record['stop']={'returncode':stopped.returncode,'stdout':stopped.stdout,'stderr':stopped.stderr}
  record['errors_and_recovery'].append(submit(page,good,503));record['screenshots'].append(shot(page,'390-unavailable-503','.results'))
  started=subprocess.run(['docker','compose','-f',str(P/'infra/f22/compose.yaml'),'start','es'],capture_output=True,text=True,timeout=30);require(started.returncode==0,started.stderr);record['start']={'returncode':started.returncode,'stdout':started.stdout,'stderr':started.stderr}
  ready=subprocess.run(['bash',str(P/'infra/f22/wait.sh')],capture_output=True,text=True,timeout=60);require(ready.returncode==0,ready.stderr);record['ready']={'returncode':ready.returncode,'stdout':ready.stdout,'stderr':ready.stderr}
  record['errors_and_recovery'].append(submit(page,good));record['screenshots'].append(shot(page,'390-recovered','.results'));c.close();browser.close()
 require(not record['js_errors'] and not record['direct_es_requests'],record)
 require(record['api_calls']==44,record['api_calls']);record['status']='passed';record['no_mock']=True
 record['java_pid_after']=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip();require(record['java_pid_after']==record['java_pid_before'],'same Java process across failures')
except Exception:
 record['status']='failed';record['failure']=traceback.format_exc();raise
finally:
 record['sha256']={str(p.relative_to(R)):sha(p) for p in [P/'backend/target/travel-search-0.7.0.jar',*sorted((P/'backend/src/main/resources/static').glob('*f22*'))]}
 full=json.dumps(record,ensure_ascii=False,indent=2).encode();target=HERE/'shell-review-full.json.gz';target.write_bytes(gzip.compress(full,mtime=0))
 record['full_record']={'path':str(target.relative_to(R)),'sha256':sha(target),'uncompressed_sha256':hashlib.sha256(full).hexdigest()}
 for row in record['matrix']+record['errors_and_recovery']:row.pop('result',None)
 (HERE/'shell-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F22 live browser passed: 36 matrix +8 error/recovery =44 actual Java calls')
