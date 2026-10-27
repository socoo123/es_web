#!/usr/bin/env python3
"""Actual right-edge scroll and narrow card screenshots after visual review."""
import datetime,functools,hashlib,http.server,json,pathlib,threading
from playwright.sync_api import sync_playwright
import reading_helpers as h
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent
rec=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),screenshots=[],scrolls=[],java_calls=[])
def require(ok,detail):
    if not ok:raise AssertionError(detail)
def shot(page,name,locator):
    p=D/"screenshots"/(name+".png")
    locator.screenshot(path=str(p))
    return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_review="pending")
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),functools.partial(h.Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=h.BROWSER)
    for width,theme,selectors in [(320,"light",["#samples-table","#room-table","#fig-layers .d2-view"]),
                                   (390,"dark",["#recap-table","#fig-coverage .d2-view"])]:
        c=browser.new_context(viewport=dict(width=width,height=1000));c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')")
        page=c.new_page();page.goto(f"http://127.0.0.1:{server.server_port}/es_web/framework/f27.html",wait_until="networkidle");h.diagrams(page,theme)
        selectors += ['pre[data-source$="HotelRankingService.java"][data-lines="84-114"]']
        for j,selector in enumerate(selectors):
            locator=page.locator(selector)
            value=locator.evaluate("e=>{e.scrollLeft=e.scrollWidth;return {left:e.scrollLeft,client:e.clientWidth,scroll:e.scrollWidth}}")
            require(value["left"]>0 and abs(value["left"]-(value["scroll"]-value["client"]))<2,value)
            rec["scrolls"].append(dict(width=width,theme=theme,selector=selector,actual=value))
            page.locator(".topbar").evaluate("e=>e.style.visibility='hidden'")
            rec["screenshots"].append(shot(page,f"followup-{width}-{theme}-right-{j+1}",locator))
            page.locator(".topbar").evaluate("e=>e.style.visibility=''")
        c.close()
    for theme in ["light","dark"]:
        c=browser.new_context(viewport=dict(width=320,height=1000));c.add_init_script(f"localStorage.setItem('travel-f27-theme','{theme}')")
        page=c.new_page();page.goto("http://127.0.0.1:18081/f27.html",wait_until="networkidle")
        page.select_option("#hotel-sort","distance")
        with page.expect_response(lambda r:r.url.endswith("/api/hotel-ranking/inspect")) as pending:page.locator("#submit").click()
        response=pending.value;body=response.json();require(response.status==200 and [x["hotelId"] for x in body["hotels"]]==["h04","h01","h02","h05","h06"],"actual distance call")
        page.wait_for_function('!document.querySelector("#submit").disabled')
        rec["java_calls"].append(dict(theme=theme,status=response.status,response=body))
        for hotel in ["h04","h06"]:
            card=page.locator(f'[data-hotel-id="{hotel}"]')
            if hotel=="h06":require("缺坐标（排末尾）" in card.inner_text(),"friendly missing distance")
            rec["screenshots"].append(shot(page,f"followup-shell-320-{theme}-{hotel}",card))
        c.close()
    browser.close()
 rec["status"]="passed"
finally:
 server.shutdown();(D/"visual-followup.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
print("Right-edge scrolling and 2 additional real Java calls recorded")
