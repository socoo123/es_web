#!/usr/bin/env python3
"""F09 real browser→Java→ES; requires current jar and a prepared F09 main index."""
import datetime,hashlib,json,pathlib,subprocess,traceback,urllib.request
from playwright.sync_api import sync_playwright
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/travel-search';BASE='http://127.0.0.1:18080'
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F09 real shell only','matrix':[],'scenarios':[],'screenshots':[],'requests':[],'js_errors':[]}
def need(v,d):
 if not v:raise AssertionError(d)
def shot(page,name):
 p=H/'screenshots'/('shell-'+name+'.png');page.screenshot(path=str(p),full_page=True)
 R['screenshots'].append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_review='pending'))
def submit(page,q='西湖',cities=('HZ',),themes=('lake','culture'),budget='200',ids=None,status=200):
 page.locator('[name=q]').fill(q);page.locator('[name=budget]').fill(budget)
 for name,values in [('cityCodes',cities),('themes',themes)]:
  for box in page.locator('[name='+name+']').all():box.set_checked(box.get_attribute('value') in values)
 with page.expect_response(lambda r:'/api/attractions/facet-search' in r.url) as info:page.locator('#submit').click()
 response=info.value;dto=response.json();page.wait_for_function('!document.querySelector("#submit").disabled')
 need(response.status==status,dict(status=response.status,data=dto))
 actual=page.locator('.card').evaluate_all('els=>els.map(el=>el.dataset.id)');need(actual==ids,dict(expected=ids,actual=actual))
 if status==200:
  need(dto['conditions']==dict(q=q,cityCodes=list(cities),themes=list(themes),maxPriceFen=round(float(budget)*100)),dto)
  need([c['id'] for c in dto['items']]==actual,dto)
  need(json.loads(page.locator('#dsl-json').text_content())==dto['esRequest'],'observed DSL')
  need(json.loads(page.locator('#result-json').text_content())==dto,'observed DTO')
  for i,card in enumerate(dto['items']):
   el=page.locator('.card').nth(i);need(el.locator('h3').inner_text()==card['name'],'name')
   need(el.locator('.price').inner_text().startswith('¥'+format(card['ticketPriceFen']/100,'.2f')),card)
   need(el.locator('.themes').inner_text()==(' / '.join(card['themes']) or '未填主题'),card)
  for name,group in [('cityCodes',dto['cities']),('themes',dto['themes'])]:
   counts={b['key']:b['docCount'] for b in group['buckets']}
   for el in page.locator('[name='+name+']').all():
    key=el.get_attribute('value');need(page.locator('#count-'+name+'-'+key).inner_text()==str(counts.get(key,0)),dict(name=name,key=key,dto=group))
  for b in dto['prices']:need(page.locator('#prices [data-key="'+b['key']+'"]').inner_text().endswith('：'+str(b['docCount'])),b)
  note=page.locator('#scope-note').inner_text();need('城市计数范围：'+str(dto['cities']['scopeTotal']) in note and '主题计数范围：'+str(dto['themes']['scopeTotal']) in note and '未填主题 '+str(dto['missingThemeCount']) in note,note)
 else:
  need(page.locator('#status').get_attribute('class')=='error' and page.locator('.choice output').all_inner_texts()==['—']*7,'clear old counts')
  need(page.locator('#prices').text_content()=='' and page.locator('#scope-note').text_content()=='','clear old ranges/scopes')
 need(page.locator('.card img,.card script').count()==0,'no source HTML elements')
 need(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'no page overflow')
 R['scenarios'].append(dict(q=q,cities=cities,themes=themes,budget=budget,status=status,ids=actual,DTO=dto,checked='all option counts, scopes, missing theme, card names/prices/themes, range counts, actual DSL/DTO'))
 return dto
selected=['a-hz-boundary','a-hz-far','a-hz-guide','a-hz-xihu'];all_ids=['a-fz-xihu','a-hz-boundary','a-hz-far','a-hz-guide','a-hz-missing-location','a-hz-plain','a-hz-tea','a-hz-xihu','a-sh-exhibit']
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch();R['browser']=browser.version
  for width in [1920,1440,1024,768,390,320]:
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
    context.add_init_script(f"if (!localStorage.getItem('travel-search:theme')) localStorage.setItem('travel-search:theme','{theme}')")
    page=context.new_page();page.on('pageerror',lambda e:R['js_errors'].append(str(e)));page.on('request',lambda r:R['requests'].append(dict(url=r.url,method=r.method)))
    page.goto(BASE+'/f09.html',wait_until='networkidle');need(page.locator('html').get_attribute('data-theme')==theme,'theme')
    submit(page,ids=selected);R['matrix'].append(dict(width=width,theme=theme,page_width=page.evaluate('document.documentElement.scrollWidth'),ids=selected))
    if width in [1440,390]:shot(page,f'{width}-{theme}-selected')
    if width==390 and theme=='light':
     submit(page,cities=('HZ','FZ'),ids=['a-fz-xihu']+selected);shot(page,'390-light-multi-city')
     submit(page,themes=('lake','walk'),ids=['a-hz-guide','a-hz-missing-location','a-hz-xihu']);shot(page,'390-light-overlap')
     submit(page,cities=(),themes=(),ids=all_ids);shot(page,'390-light-unselected')
     submit(page,cities=(),themes=(),budget='100',ids=[x for x in all_ids if x!='a-hz-boundary'])
     submit(page,q='火星',ids=[]);shot(page,'390-light-empty')
     submit(page,ids=selected)
     raw=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:19200/tut-f09-attractions',method='DELETE')).read().decode();R['error_trigger']={'method':'DELETE','index':'tut-f09-attractions','raw_response':raw}
     submit(page,ids=[],status=502);shot(page,'390-light-missing-index')
     result=subprocess.run(['bash','labs/f09/01-prepare.sh'],cwd=P,check=True,capture_output=True,text=True);R['recovery_prepare']={'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
     submit(page,ids=selected);shot(page,'390-light-recovered')
     page.locator('#theme').click();page.reload(wait_until='networkidle');need(page.locator('html').get_attribute('data-theme')=='dark','theme persistence')
     page.locator('#submit').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab');need(page.locator('#submit').evaluate('el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=="none"'),'actual keyboard outline')
    context.close()
  browser.close()
 need(not R['js_errors'],R['js_errors']);need(all(r['url'].startswith(BASE+'/') for r in R['requests']),'no direct ES/outside request')
 R['status']='passed';R['interactions']=['checkbox multiselect and clear','overlap counts not sum','100-yuan range boundary','normal empty set and zero buckets','missing index502 clears all old data','same Java process recovers after fixture reimport','theme reload','actual Tab focus']
except Exception:R['status']='failed';R['failure']=traceback.format_exc();raise
finally:
 R['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'backend/src').rglob('*') if p.is_file()}
 (H/'shell-review.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print('F09 shell passed: 12 size/theme groups, exact counts/scopes/cards/ranges/DSL/DTO; multiselect/overlap/empty/error/recovery')
