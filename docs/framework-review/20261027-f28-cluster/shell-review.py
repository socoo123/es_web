#!/usr/bin/env python3
"""Actual browser -> existing F07 Java service -> F28 three-node index."""
import datetime,json,os,pathlib,urllib.request
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2]
BROWSER=os.environ.get('F28_BROWSER_EXECUTABLE',str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
REC={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'calls':[],'js_errors':[],'http_errors':[],'direct_browser_es':[],'screenshots':[],'scope':'existing F07 shell, unchanged Java code, F28 ES_INDEX and es2 endpoint; success and independent budget observation only; no browser fault-injection claims'}
def check(ok,detail):
 if not ok:raise AssertionError(detail)
def main():
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=BROWSER,headless=True)
  for width in [1440,390]:
   for theme in ['light','dark']:
    context=browser.new_context(viewport={'width':width,'height':900})
    context.add_init_script("localStorage.setItem('travel-search:theme',"+json.dumps(theme)+");")
    page=context.new_page()
    page.on('pageerror',lambda e:REC['js_errors'].append(str(e)))
    page.on('response',lambda r:REC['http_errors'].append({'url':r.url,'status':r.status}) if r.status>=400 else None)
    page.on('request',lambda r:REC['direct_browser_es'].append(r.url) if any(':'+str(port) in r.url for port in [19228,19229,19230]) else None)
    page.goto('http://127.0.0.1:18081/',wait_until='networkidle')
    check(page.locator('html').get_attribute('data-theme')==theme,theme)
    for budget,ids in [('200',['p01','p02']),('50',['p02'])]:
     page.locator('[name="budget"]').fill(budget)
     with page.expect_response(lambda r:r.url.endswith('/api/attractions/search') and r.request.method=='POST') as response:
      page.locator('#submit').click()
     r=response.value;body=r.json();check(r.status==200 and [c['id'] for c in body['items']]==ids,body)
     page.wait_for_function('ids=>[...document.querySelectorAll("#cards .card")].map(e=>e.dataset.id).join()===ids.join()',arg=ids)
     check(page.locator('#cards .price').all_text_contents()==(['¥60.00 / CNY 搜索快照','¥0.00 / CNY 搜索快照'] if budget=='200' else ['¥0.00 / CNY 搜索快照']),'prices')
     check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'shell overflow')
     page.locator('details.observe').evaluate('e=>e.open=true')
     displayed=json.loads(page.locator('#result-json').text_content());dsl=json.loads(page.locator('#dsl-json').text_content());submitted=json.loads(page.locator('#input-json').text_content())
     check(displayed==body and dsl==body['esRequest'] and submitted==body['conditions'],body)
     req=urllib.request.Request('http://127.0.0.1:19229/tut-f28-attractions/_search?allow_partial_search_results=false',data=json.dumps(dsl).encode(),method='POST',headers={'Content-Type':'application/json'})
     replay=json.load(urllib.request.urlopen(req));check([h['_id'] for h in replay['hits']['hits']]==ids and replay['_shards']['failed']==0 and not replay['timed_out'],'REST replay')
     for hit,card in zip(replay['hits']['hits'],body['items']):check(hit['_score']==card['score'],'score')
     REC['calls'].append({'width':width,'theme':theme,'budget_yuan':budget,'java_status':r.status,'input':submitted,'java_response':body,'rest_replay':replay,'display_equal_response':True})
     page.locator('.results').scroll_into_view_if_needed();path=D/'screenshots'/f'shell-{width}-{theme}-{budget}.png';page.screenshot(path=str(path));REC['screenshots'].append(str(path.relative_to(ROOT)))
    context.close()
  browser.close()
 check(not REC['js_errors'] and not REC['http_errors'] and not REC['direct_browser_es'],REC)
 REC['passed']=True;REC['actual_java_calls']=len(REC['calls']);REC['extra_author_rest_replays']=len(REC['calls'])
 (D/'shell-review.json').write_text(json.dumps(REC,ensure_ascii=False,indent=2)+'\n');print('F28 existing shell, 8 actual Java calls and separate REST replays passed')
if __name__=='__main__':main()
