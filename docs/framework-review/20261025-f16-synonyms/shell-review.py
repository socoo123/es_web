#!/usr/bin/env python3
"""F16 actual browser -> final Java jar -> ES. No mocks or browser ES access."""
import contextlib
import datetime
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import traceback
from playwright.sync_api import sync_playwright

HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f16lab',PROJECT/'labs/f16/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual F16 final jar local shell; no mocked responses','matrix':[],'operations':[],'transitions':[],'screenshots':[],'js_errors':[],'direct_es_requests':[],'status':'running'}
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def observe(page):
 page.on('pageerror',lambda e:record['js_errors'].append(str(e)))
 page.on('request',lambda r:record['direct_es_requests'].append(r.url) if any(':'+str(p)+'/' in r.url for p in [9200,9201,19200,19214,19215,19216]) else None)
 def response(r):
  if r.url.endswith('/api/attractions/synonym-search'):
   record['operations'].append({'request':json.loads(r.request.post_data),'status':r.status,'response':r.json()})
 page.on('response',response)
def layout(page):
 r=page.evaluate('({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})')
 require(r['page']<=r['viewport'] and r['body']<=r['viewport'],r);return r
def fill(page,q='紫禁城',city='BJ',mode='aliases',budget='100'):
 page.locator('[name=q]').fill('')  # Ensure a real input change even on the initial default form.
 page.locator('[name=q]').fill(q);page.locator('[name=cityCode]').select_option(city)
 page.locator('[name=mode]').select_option(mode);page.locator('[name=budget]').fill(budget)
 require(page.locator('.card,.token').count()==0,'condition changes clear cards/graph')
 require(page.locator('#dsl-json').text_content()=='尚无本轮结果','condition changes clear DSL')
def search(page,wanted=None,status=200):
 with page.expect_response(lambda r:r.url.endswith('/api/attractions/synonym-search'),timeout=25000) as info:page.locator('#submit').click()
 r=info.value;value=r.json();require(r.status==status,{'status':r.status,'response':value})
 page.wait_for_function("!document.getElementById('submit').disabled")
 if status!=200:
  require(page.locator('.card,.token').count()==0,'error clears result')
  require(page.locator('#status').get_attribute('class')=='error' and str(status) in page.locator('#status').inner_text(),'error message')
  for id in ['input-json','base-request-json','query-request-json','base-analysis-json','query-analysis-json','dsl-json','result-json']:
   require(page.locator('#'+id).text_content()=='尚无本轮结果','error clears '+id)
  return value
 require(page.locator('.card').evaluate_all('els=>els.map(e=>e.dataset.id)')==[i['id'] for i in value['items']], 'IDs/order')
 if wanted is not None:require([i['id'] for i in value['items']]==wanted,value)
 for i,item in enumerate(value['items']):
  card=page.locator('.card').nth(i)
  for selector,expected in [('h3',item['name']),('.english',item['nameEn']),('.aliases','别名：'+('、'.join(item['aliases']) or '无')),
                            ('.tag',item['cityCode']+' · '+item['currency']+' / '+item['status']),('.price',f"{item['ticketPriceFen']/100:.2f} 元")]:
   require(card.locator(selector).inner_text()==expected,(selector,item))
 for id,key in [('base-tokens','baseTokens'),('query-tokens','queryTokens')]:
  require(page.locator('#'+id+' .token').count()==len(value[key]),key)
  for i,t in enumerate(value[key]):
   node=page.locator('#'+id+' .token').nth(i)
   require(node.locator('strong').inner_text()==t['token'],t)
   require(node.locator('small').all_text_contents()==[f"position {t['position']} · length {t['positionLength']}",f"offset [{t['startOffset']}, {t['endOffset']})"],t)
 for id,key in [('input-json','conditions'),('base-request-json','baseAnalysisRequest'),('query-request-json','queryAnalysisRequest'),('base-analysis-json','baseAnalysis'),('query-analysis-json','queryAnalysis'),('dsl-json','esRequest'),('result-json',None)]:
  require(json.loads(page.locator('#'+id).text_content())==(value[key] if key else value),'complete rendered '+id)
 require(page.locator('#total').inner_text()==f"{value['total']} 份 · {value['relation']}",'total')
 require(page.locator('#status').get_attribute('class')!='error','empty success is normal')
 return value
def shot(page,name,target=None):
 path=HERE/'screenshots'/(name+'.png');path.parent.mkdir(exist_ok=True)
 (page.locator(target) if target else page).screenshot(path=str(path))
 record['screenshots'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_review':'pending'})
def command(args):
 r=subprocess.run(args,cwd=PROJECT,capture_output=True,text=True)
 record['transitions'].append({'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});require(r.returncode==0,args)
def restore():
 lab.call('PUT','/'+lab.INDEX,lab.load('index'))
 r=lab.call('GET','/_cluster/health/'+lab.INDEX+'?wait_for_status=green&timeout=30s');require(not r['timed_out'] and r['status']=='green','recovered')
 r=lab.call('POST','/'+lab.INDEX+'/_bulk',(PROJECT/'data/f16/attractions.ndjson').read_text(),ndjson=True)
 require(not r['errors'] and all(i['create']['result']=='created' for i in r['items']),'restore bulk')
 lab.call('POST','/'+lab.INDEX+'/_update/bj-palace',lab.load('alias-update'));lab.refresh()
try:
 with (HERE/'shell-setup.jsonl').open('w') as f,contextlib.redirect_stdout(f):
  lab.cleanup();lab.prepare();lab.graph();lab.changes()
 with sync_playwright() as pw:
  browser=pw.chromium.launch();record['browser']=browser.version
  for width in [1920,1440,1024,768,390,320]:
   print('F16 shell width',width,flush=True)
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
    context.add_init_script(f"localStorage.setItem('travel-f16:theme','{theme}')")
    page=context.new_page();observe(page);page.goto('http://127.0.0.1:18080/f16.html',wait_until='networkidle')
    require(page.locator('h1').inner_text()=='叫法变了，\n找到的还是它吗？','F16 heading')
    if (width,theme) in [(1440,'light'),(390,'dark')]:shot(page,f'shell-{width}-{theme}-opening')
    fill(page);search(page,['bj-palace','bj-wall'])
    if width in [1440,390]:shot(page,f'shell-{width}-{theme}-aliases','.results')
    fill(page,mode='graph');search(page,lab.CN)
    fill(page,q='PALACE museum',mode='phrase');search(page,['bj-palace'])
    if width in [1440,390]:
     shot(page,f'shell-{width}-{theme}-graph','.analysis');shot(page,f'shell-{width}-{theme}-phrase','.results')
    fill(page,q='！！！',mode='graph');search(page,[])
    record['matrix'].append({'width':width,'theme':theme,'layout':layout(page),'core_modes':'aliases/graph/phrase/empty'})
    context.close()
  context=browser.new_context(viewport={'width':390,'height':1000});page=context.new_page();observe(page)
  page.goto('http://127.0.0.1:18080/f16.html',wait_until='networkidle')
  cases=[('PALACE museum','BJ','graph',['bj-palace','bj-tail']),('PALACE museum','BJ','loose',['bj-gap','bj-palace','bj-reverse','bj-tail']),
         ('PALACE museum','BJ','late',[]),('故宮','BJ','plain',[]),('故宮','BJ','graph',lab.CN),
         ('故宮','BJ','late',['bj-palace','bj-theme','bj-traditional']),('紫禁城','SY','aliases',[]),('紫禁城','SY','graph',['sy-palace']),
         ('皇家旧宫','BJ','aliases',['bj-palace']),('皇城旧称','BJ','graph',lab.CN)]
  for q,city,mode,wanted in cases:
   fill(page,q,city,mode);search(page,wanted)
   if mode=='loose':shot(page,'shell-390-loose','.results')
  fill(page,mode='graph',budget='0');search(page,['bj-traditional']);shot(page,'shell-390-zero-budget','.results')
  page.locator('[name=q]').evaluate("el=>el.removeAttribute('maxlength')")
  fill(page,q='x'*61);search(page,status=400);shot(page,'shell-390-invalid')
  with (HERE/'shell-recovery.jsonl').open('w') as f,contextlib.redirect_stdout(f):lab.call('DELETE','/'+lab.INDEX)
  fill(page);search(page,status=502);shot(page,'shell-390-missing-index')
  with (HERE/'shell-recovery.jsonl').open('a') as f,contextlib.redirect_stdout(f):restore()
  fill(page);search(page,['bj-palace','bj-wall'])
  command(['docker','compose','-f','infra/f16/compose.yaml','stop','es'])
  fill(page);search(page,status=503);shot(page,'shell-390-unavailable')
  command(['docker','compose','-f','infra/f16/compose.yaml','up','-d','es']);command(['bash','infra/f16/wait.sh'])
  fill(page);search(page,['bj-palace','bj-wall']);shot(page,'shell-390-recovered','.results')
  original=page.evaluate('document.documentElement.dataset.theme');page.locator('#theme').click()
  toggled=page.evaluate('document.documentElement.dataset.theme');require(original!=toggled,'theme toggle')
  page.reload(wait_until='networkidle');require(page.evaluate('document.documentElement.dataset.theme')==toggled,'theme reload')
  record['interactions']={'theme':'switch and reload','conditions':'all input changes clear old graph/cards/requests','errors':'400/502/real stopped-ES503 and same Java process recovery','source':'card raw traditional text retained','analysis':'both current-input chains; complete detail and graph edges rendered'}
  require(not record['js_errors'] and not record['direct_es_requests'], 'no JS errors/direct browser ES calls')
  context.close();browser.close()
 record['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for pattern in ['backend/src/main/java/dev/esweb/travel/Synonym*.java','backend/src/main/resources/static/*f16*','backend/target/travel-search-0.7.0.jar'] for p in PROJECT.glob(pattern) if p.is_file()}
 record['status']='passed'
except BaseException:
 record['status']='failed';record['error']=traceback.format_exc();raise
finally:
 (HERE/'shell-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F16 shell passed',len(record['matrix']),'groups',len(record['operations']),'actual API calls')
