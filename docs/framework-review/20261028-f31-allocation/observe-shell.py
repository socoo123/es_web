#!/usr/bin/env python3
"""Author-only browser evidence at stable points in the F31 allocation experiment."""
import datetime,json,pathlib,urllib.request
from playwright.sync_api import sync_playwright
BROWSER=str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell')
def capture(stage,price,expected,app,out):
 rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'calls':[],'js_errors':[],'unexpected_http_errors':[],'direct_es':[],'screenshots':[]}
 shots=out/'screenshots';shots.mkdir(exist_ok=True)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=BROWSER,headless=True)
  rec['browser_version']=browser.version
  for width in [1440,390]:
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':900})
    context.add_init_script("localStorage.setItem('travel-search:theme',"+json.dumps(theme)+");")
    page=context.new_page()
    page.on('pageerror',lambda e:rec['js_errors'].append(str(e)))
    page.on('request',lambda r:rec['direct_es'].append(r.url) if any(':'+str(port) in r.url for port in range(19531,19534)) else None)
    page.on('response',lambda r:rec['unexpected_http_errors'].append({'url':r.url,'status':r.status}) if r.status>=400 and not (r.url.endswith('/api/attractions/search') and r.status==expected) else None)
    page.goto(app+'/',wait_until='networkidle')
    assert page.locator('html').get_attribute('data-theme')==theme
    with page.expect_response(lambda r:r.url.endswith('/api/attractions/search') and r.request.method=='POST') as response:
     page.locator('#submit').click()
    r=response.value;body=r.json();assert r.status==expected,(stage,r.status,body)
    page.wait_for_function('!document.querySelector("#submit").disabled')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.locator('details.observe').evaluate('e=>e.open=true')
    displayed=json.loads(page.locator('#result-json').text_content());assert displayed==body
    call={'width':width,'theme':theme,'status':r.status,'request':json.loads(r.request.post_data),'response':body}
    if expected==200:
     assert page.locator('#cards .card').evaluate_all('es=>es.map(e=>e.dataset.id)')==['p01','p02']
     assert page.locator('#cards .price').all_text_contents()==[f'¥{price/100:.2f} / CNY 搜索快照','¥0.00 / CNY 搜索快照']
     dsl=json.loads(page.locator('#dsl-json').text_content());assert dsl==body['esRequest']
     request=urllib.request.Request('http://127.0.0.1:19531/tut-f31-attractions/_search?allow_partial_search_results=false',data=json.dumps(dsl).encode(),method='POST',headers={'Content-Type':'application/json'})
     replay=json.load(urllib.request.urlopen(request));call['rest_replay']=replay
     assert not replay['timed_out'] and replay['_shards']['failed']==0
     assert [h['_id'] for h in replay['hits']['hits']]==['p01','p02']
     for hit,card in zip(replay['hits']['hits'],body['items']):
      s=hit['_source'];assert (card['id'],card['name'],card['cityCode'],card['ticketPriceFen'],card['currency'],card['status'])==(hit['_id'],s['name'],s['city_code'],s['ticket_price_fen'],s['currency'],s['status'])
    else:
     assert body['code']==('SEARCH_BACKEND_REJECTED' if expected==502 else 'SEARCH_UNAVAILABLE') and page.locator('#cards .card').count()==0
     assert 'error' in page.locator('#status').get_attribute('class')
     assert page.locator('#dsl-json').text_content()=='本次搜索未成功，不展示旧命中。'
    rec['calls'].append(call)
    page.locator('.results').scroll_into_view_if_needed();name=f'{stage}-{width}-{theme}.png';page.screenshot(path=str(shots/name));rec['screenshots'].append('screenshots/'+name)
    context.close()
  browser.close()
 assert not rec['js_errors'] and not rec['unexpected_http_errors'] and not rec['direct_es'],rec
 rec['passed']=True
 (out/(stage+'-browser.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
