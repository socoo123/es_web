#!/usr/bin/env python3
"""F08 real local shell checks. Requires prepared F08 ES index and current Java jar running."""
import datetime,hashlib,json,pathlib,subprocess,traceback,urllib.request
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search';BASE='http://127.0.0.1:18080'
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'real browser→Java→ES, F08 only','matrix':[],'scenarios':[],'screenshots':[],'requests':[],'js_errors':[]}
def need(v,d):
 if not v:raise AssertionError(d)
def shot(page,name):
 p=HERE/'screenshots'/('shell-'+name+'.png');page.screenshot(path=str(p),full_page=True)
 R['screenshots'].append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_review='pending'))
def search(page,q='西湖',budget='200',expected=None,status=200):
 page.locator('[name=q]').fill(q);page.locator('[name=budget]').fill(budget)
 with page.expect_response(lambda r:'/api/attractions/multi-search' in r.url) as info:page.locator('#submit').click()
 response=info.value;data=response.json();page.wait_for_function('!document.querySelector("#submit").disabled')
 need(response.status==status,dict(status=response.status,data=data))
 ids=page.locator('.card').evaluate_all('els=>els.map(el=>el.dataset.id)')
 if expected is not None:need(ids==expected,dict(expected=expected,actual=ids))
 if status==200:
  need(data['conditions']['q']==q and data['conditions']['maxPriceFen']==round(float(budget)*100),data)
  need([c['id'] for c in data['items']]==ids,data)
  for i,item in enumerate(data['items']):
   card=page.locator('.card').nth(i)
   need(card.locator('.price').inner_text().startswith('¥'+format(item['ticketPriceFen']/100,'.2f')),item)
   for snip in item['snippets']:
    dom=card.locator('[data-field="'+snip['field']+'"]').evaluate('el=>[...el.children].filter(c=>!c.classList.contains("field-label")).map(c=>({text:c.textContent,matched:c.tagName==="MARK"}))')
    need(dom==snip['segments'],dict(dom=dom,dto=snip))
  need(json.loads(page.locator('#dsl-json').text_content())==data['esRequest'],'observed DSL')
  need(json.loads(page.locator('#result-json').text_content())==data,'observed DTO')
 else:need(not ids and page.locator('#status').get_attribute('class')=='error','failure clears previous cards')
 need(page.locator('.card img,.card script').count()==0,'source HTML must never become elements')
 need(page.evaluate('window.__f08_xss === undefined'),'event must not run')
 need(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'no page overflow')
 R['scenarios'].append(dict(q=q,budget=budget,status=status,ids=ids,DTO=data,dom='all segments/mark/text/price/DSL/response exactly checked',xss='no img/script nodes, no event execution'))
 return data
multi=['a-hz-boundary','a-hz-guide','a-hz-plain','a-hz-tea','a-hz-xihu']
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch();R['browser']=browser.version
  for width in [1920,1440,1024,768,390,320]:
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
    context.add_init_script(f"if (!localStorage.getItem('travel-search:theme')) localStorage.setItem('travel-search:theme','{theme}')")
    page=context.new_page();page.on('pageerror',lambda e:R['js_errors'].append(str(e)));page.on('request',lambda r:R['requests'].append(dict(url=r.url,method=r.method)))
    page.goto(BASE+'/f08.html',wait_until='networkidle');need(page.locator('html').get_attribute('data-theme')==theme,'theme')
    search(page,expected=multi)
    R['matrix'].append(dict(width=width,theme=theme,page_width=page.evaluate('document.documentElement.scrollWidth'),ids=multi))
    if width in [1440,390]:shot(page,f'{width}-{theme}-results')
    if width==390 and theme=='light':
     search(page,'钱塘湖',expected=['a-hz-xihu']);shot(page,'390-light-alias')
     search(page,'火星',expected=[]);shot(page,'390-light-empty')
     search(page,budget='80',expected=[x for x in multi if x!='a-hz-boundary'])
     search(page,expected=multi)
     subprocess.run(['bash','labs/f08/cleanup.sh'],cwd=P,check=True,capture_output=True)
     search(page,expected=[],status=502);shot(page,'390-light-missing-index')
     subprocess.run(['bash','labs/f08/01-prepare.sh'],cwd=P,check=True,capture_output=True)
     search(page,expected=multi);shot(page,'390-light-recovered')
     page.locator('#theme').click();page.reload(wait_until='networkidle');need(page.locator('html').get_attribute('data-theme')=='dark','theme persistence')
     page.locator('#submit').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
     need(page.locator('#submit').evaluate('el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=="none"'),'real Tab focus')
    context.close()
  browser.close()
 need(not R['js_errors'],R['js_errors'])
 need(not any(':19200' in r['url'] or ':9200' in r['url'] for r in R['requests']),'browser must not contact ES')
 need(all(r['url'].startswith(BASE+'/') for r in R['requests']),'no outside requests or XSS image fetch')
 R['status']='passed';R['interactions']=['theme switch/reload','actual Tab focus','80 yuan migration','missing index502 clears cards','same Java process recovers after reprepare']
except Exception:R['status']='failed';R['failure']=traceback.format_exc();raise
finally:
 R['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'backend/src').rglob('*') if p.is_file()}
 (HERE/'shell-review.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print('F08 real shell passed: 12 size/theme groups, exact DTO↔DOM segments, alias/empty/budget/error/recovery')
