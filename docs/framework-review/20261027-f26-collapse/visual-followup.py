#!/usr/bin/env python3
"""Targeted screenshots for horizontal scrolling and shell controls."""
import datetime,functools,hashlib,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright
import reading_helpers as h
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2]
rec=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),screenshots=[],checks=[])
def shot(page,name,target):
    p=HERE/'screenshots'/('followup-'+name+'.png');page.locator('.topbar').evaluate("e=>e.style.visibility='hidden'") if page.locator('.topbar').count() else None
    page.locator(target).first.screenshot(path=str(p));rec['screenshots'].append(dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_review='pending'))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(h.Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=h.BROWSER)
        for width,theme in [(390,'dark'),(320,'light')]:
            c=browser.new_context(viewport=dict(width=width,height=1000));c.add_init_script(f"if(!localStorage.getItem('es-web:theme'))localStorage.setItem('es-web:theme','{theme}')")
            page=c.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f26.html',wait_until='networkidle')
            for name,target in [('sample','#samples-table'),('scope','#scope-table'),('recap','#recap-table'),('java','pre[data-label^="Java · 完整性"]')]:
                el=page.locator(target).first;el.evaluate('e=>e.scrollLeft=e.scrollWidth');rec['checks'].append(dict(width=width,theme=theme,target=target,scroll=el.evaluate('e=>({left:e.scrollLeft,max:e.scrollWidth-e.clientWidth})')));shot(page,f'{width}-{theme}-{name}-right',target)
            c.close()
        for width,theme in [(1440,'light'),(390,'dark')]:
            c=browser.new_context(viewport=dict(width=width,height=1000));c.add_init_script(f"if(!localStorage.getItem('travel-f26-theme'))localStorage.setItem('travel-f26-theme','{theme}')")
            page=c.new_page();page.goto('http://127.0.0.1:18081/f26.html',wait_until='networkidle');shot(page,f'shell-{width}-{theme}-form','main > form');c.close()
        browser.close()
    rec['status']='passed'
finally:server.shutdown();(HERE/'visual-followup.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
