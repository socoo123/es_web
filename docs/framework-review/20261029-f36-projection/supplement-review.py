#!/usr/bin/env python3
"""Click final directory/lesson/diagram navigation and inspect expanded code layout."""
import functools,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(R))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/';rec={'navigation':[],'expanded_views':[]}
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=str(pathlib.Path.home()/'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'),headless=True)
        page=browser.new_page(viewport={'width':1440,'height':900})
        page.goto(base+'framework/index.html',wait_until='networkidle')
        page.locator('a[data-ch="f36"]').click();page.wait_for_url('**/f36.html');rec['navigation'].append('directory -> f36')
        page.locator('.pager a[href="f35.html"]').click();page.wait_for_url('**/f35.html')
        page.locator('.pager a[href="f36.html"]').click();page.wait_for_url('**/f36.html');rec['navigation'].append('f36 -> f35 -> f36')
        for theme in ['light','dark']:
            page.evaluate('t=>document.documentElement.dataset.theme=t',theme)
            page.wait_for_function('t=>[...document.querySelectorAll("[data-d2-light]")].every(i=>i.complete&&i.currentSrc.endsWith("-"+t+".svg"))',arg=theme)
            for i in range(2):
                with page.expect_popup() as pop:page.locator('[data-expand-d2]').nth(i).click()
                popup=pop.value;popup.wait_for_load_state('networkidle');assert popup.url.endswith('-'+theme+'.svg');popup.close()
                rec['navigation'].append(f'{theme} diagram {i+1} expanded')
        for width in [1440,390,320]:
            page.set_viewport_size({'width':width,'height':900});page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            rec['expanded_views'].append({'width':width,'pre':page.locator('pre.code-block').count(),'document_overflow':False})
        page.locator('#java').scroll_into_view_if_needed();page.screenshot(path=str(D/'screenshots/supplement-320-expanded-java.png'))
        browser.close()
    rec['passed']=True
finally:
    server.shutdown();(D/'supplement-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print('F36 final navigation/expand/all-details layouts passed')
