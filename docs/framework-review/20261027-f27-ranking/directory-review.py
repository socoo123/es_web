#!/usr/bin/env python3
"""Verify the final F27 directory summary after removing stale F21 wording."""
import datetime,functools,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright
import reading_helpers as h
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(h.Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start();rows=[]
try:
 with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=h.BROWSER)
    for width in h.WIDTHS:
        for theme in h.THEMES:
            c=browser.new_context(viewport=dict(width=width,height=1000));c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')")
            page=c.new_page();page.goto(f"http://127.0.0.1:{server.server_port}/es_web/framework/index.html",wait_until="networkidle")
            assert page.locator(".badges").inner_text().count("F01–F27 可阅读")==1
            assert page.locator('.curriculum-lesson-link[href="f27.html"][data-ch="f27"]').count()==1
            assert page.locator('a[href="f28.html"]').count()==0
            rows.append(dict(width=width,theme=theme,layout=h.measure(page,False)));c.close()
    browser.close()
 rec=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status="passed",matrix=rows,scope="Final directory current summary; F27 readable, F28 pending",static_links=h.static_links())
 (D/"directory-current-summary.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
finally:server.shutdown()
print("Final directory summary passed 12 width/theme groups and local link checks")
