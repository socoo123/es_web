#!/usr/bin/env python3
"""Author-only real Browser -> Java -> ES evidence at F36 stable stages."""
import collections, datetime, json, pathlib, urllib.request
from playwright.sync_api import sync_playwright
BROWSER=str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell')
def capture(stage, want, app, es, alias, out):
    rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'calls':[],
         'js_errors':[],'http_errors':[],'direct_es':[],'screenshots':[]}
    shots=out/'screenshots';shots.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=BROWSER,headless=True);rec['browser']=browser.version
        for width in [1440,390]:
            for theme in ['light','dark']:
                ctx=browser.new_context(viewport={'width':width,'height':900})
                ctx.add_init_script("localStorage.setItem('travel-search:theme',"+json.dumps(theme)+");")
                page=ctx.new_page();page.on('pageerror',lambda e:rec['js_errors'].append(str(e)))
                page.on('response',lambda r:rec['http_errors'].append([r.url,r.status]) if r.status>=400 else None)
                page.on('request',lambda r:rec['direct_es'].append(r.url) if ':20036' in r.url else None)
                page.goto(app+'/',wait_until='networkidle')
                assert page.locator('html').get_attribute('data-theme')==theme
                with page.expect_response(lambda r:r.url.endswith('/api/attractions/search') and r.request.method=='POST') as response:
                    page.locator('#submit').click()
                value=response.value.json();assert response.value.status==200
                assert [(r['id'],r['ticketPriceFen']) for r in value['items']]==want
                page.wait_for_function('!document.querySelector("#submit").disabled')
                assert collections.Counter(page.locator('#cards .card').evaluate_all('es=>es.map(e=>e.dataset.id)'))==collections.Counter(x[0] for x in want)
                assert collections.Counter(page.locator('#cards .price').all_text_contents())==collections.Counter(f'¥{x[1]/100:.2f} / CNY 搜索快照' for x in want)
                page.locator('details.observe').evaluate('e=>e.open=true')
                assert json.loads(page.locator('#result-json').text_content())==value
                request=urllib.request.Request(es+'/'+alias+'/_search?allow_partial_search_results=false',
                    data=json.dumps(value['esRequest']).encode(),method='POST',headers={'Content-Type':'application/json'})
                replay=json.load(urllib.request.urlopen(request,timeout=20))
                assert [(r['_id'],r['_source']['ticket_price_fen']) for r in replay['hits']['hits']]==want
                assert replay['_shards']['failed']==0 and not replay['timed_out']
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                rec['calls'].append({'width':width,'theme':theme,'java':value,'rest_replay':replay})
                page.locator('.results').scroll_into_view_if_needed()
                name=f'{stage}-{width}-{theme}.png';page.screenshot(path=str(shots/name));rec['screenshots'].append('screenshots/'+name)
                ctx.close()
        browser.close()
    assert not rec['js_errors'] and not rec['http_errors'] and not rec['direct_es'],rec
    rec['passed']=True;(out/(stage+'-browser.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
