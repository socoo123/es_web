#!/usr/bin/env python3
"""Actual browser -> Java -> isolated F27 ES, including real error recovery."""
import datetime,hashlib,importlib.util,json,pathlib,subprocess,traceback
from playwright.sync_api import sync_playwright
import reading_helpers as h
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/"projects/travel-search"
spec=importlib.util.spec_from_file_location("f27lab",P/"labs/f27/lab.py")
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
CASES=["relevance-price","relevance-preferred","quality-price","distance-price","hard-preferred","top-quality","independent"]
def require(ok,detail):
    if not ok:raise AssertionError(detail)
def shot(page,name,selector):
    p=HERE/"screenshots"/("shell-"+name+".png");p.parent.mkdir(exist_ok=True)
    page.locator(selector).screenshot(path=str(p))
    return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_review="pending")
def run():
    rec=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),matrix=[],calls=[],screenshots=[],
        js_errors=[],request_failures=[],browser_es_calls=[],http_errors=[])
    rec["java_pid_before"]=subprocess.check_output(["lsof","-tiTCP:18081","-sTCP:LISTEN"],text=True).strip()
    lab.LOG=HERE/"shell-es-operations.jsonl";require(not lab.LOG.exists(),"fresh ES log")
    def submit(page,name,status=200,invalid=False):
        i=lab.read(P/f"search/f27/{name}-input.json")
        page.select_option("#q",i["q"]);page.select_option("#hotel-sort",i["hotelSort"])
        page.select_option("#room-sort",i["roomSort"]);page.select_option("#scope","invalid" if invalid else i["scope"])
        page.set_checked("#breakfast",i["requireBreakfast"]);page.set_checked("#flexible",i["requireFlexible"])
        require(page.locator("#cards .hotel").count()==0 and page.locator("#result-json").text_content()=="尚无本轮结果","changes clear old cards/evidence")
        with page.expect_response(lambda r:r.url.endswith("/api/hotel-ranking/inspect")) as pending:page.locator("#submit").click()
        response=pending.value;body=response.json();require(response.status==status,dict(name=name,status=response.status,body=body))
        page.wait_for_function('!document.querySelector("#submit").disabled')
        if status==200:
            order,rooms,counts=lab.expected(name)
            require(body["conditions"]==i and [x["hotelId"] for x in body["hotels"]]==order,"actual hotel order/conditions")
            require((body["candidateHotelTotal"],body["inspectedHotelCount"],body["inspectedOfferCount"],body["acceptedOfferCount"])==counts,"all count scopes")
            require(body["esRequest"]==lab.read(P/f"search/f27/{name}.json"),"whole canonical DSL")
            require(json.loads(page.locator("#result-json").text_content())==body and
                json.loads(page.locator("#dsl-json").text_content())==body["esRequest"],"actual UI raw response and DSL equal HTTP")
            cards=page.locator("#cards .hotel");require(cards.count()==len(order),"card count")
            for k,hotel in enumerate(body["hotels"]):
                card=cards.nth(k);hid=hotel["hotelId"];chosen=rooms[hid][0]
                require(card.get_attribute("data-hotel-id")==hid,"hotel identity")
                require(card.locator("li").evaluate_all("es=>es.map(e=>e.dataset.offerId)")==rooms[hid],"full within-hotel room order")
                require(chosen in card.locator(".price").inner_text() and
                    f'¥{lab.TOTALS[chosen]/100:.2f}' in card.locator(".price").inner_text(),"selected room total")
                require(f'最低总价 ¥{min(lab.TOTALS[v] for v in rooms[hid])/100:.2f}' in card.inner_text(),"minimum independently labeled")
                if name=="distance-price" and hid=="h06":require("缺坐标（排末尾）" in card.inner_text(),"missing coordinates friendly label")
            require(page.locator("#decisions p").count()==body["inspectedOfferCount"],"all inspected decisions displayed")
            require(body["completeCandidateSet"]==(i["scope"]=="all"),"coverage")
        else:
            require(page.locator("#cards .hotel").count()==0 and page.locator("#decisions p").count()==0
                and page.locator("#result-json").text_content()=="尚无本轮结果","failed calls clear all previous result evidence")
            require(str(status) in page.locator("#status").inner_text() and body["code"] in page.locator("#status").inner_text(),"real error shown")
        layout=page.evaluate("({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})")
        require(layout["page"]<=layout["viewport"] and layout["body"]<=layout["viewport"],layout)
        rec["calls"].append(dict(case=name,status=response.status,response=body,layout=layout))
        return layout
    def observe(page):
        page.on("pageerror",lambda e:rec["js_errors"].append(str(e)))
        page.on("requestfailed",lambda r:rec["request_failures"].append(dict(url=r.url,failure=r.failure)))
        page.on("request",lambda r:rec["browser_es_calls"].append(r.url) if any(s in r.url for s in [":19227",":9200",":9201"]) else None)
        page.on("response",lambda r:rec["http_errors"].append(dict(url=r.url,status=r.status)) if r.status>=400 else None)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=h.BROWSER);rec["browser"]=dict(engine="Chromium",version=browser.version)
            for width in [1440,768,390,320]:
                print("Shell",width,flush=True)
                for theme in ["light","dark"]:
                    c=browser.new_context(viewport=dict(width=width,height=1000),reduced_motion="reduce")
                    c.add_init_script(f"if(!localStorage.getItem('travel-f27-theme'))localStorage.setItem('travel-f27-theme','{theme}')")
                    page=c.new_page();observe(page);page.goto("http://127.0.0.1:18081/f27.html",wait_until="networkidle")
                    require(page.locator("html").get_attribute("data-theme")==theme,"initial theme")
                    if width in [1440,320]:rec["screenshots"].append(shot(page,f"{width}-{theme}-form","#search-form"))
                    for name in CASES:
                        layout=submit(page,name);rec["matrix"].append(dict(width=width,theme=theme,case=name,layout=layout))
                        if (width==1440 and theme=="light" and name in ["relevance-price","relevance-preferred","hard-preferred","top-quality","independent"]) or (width==320 and theme=="dark" and name=="distance-price"):
                            rec["screenshots"].append(shot(page,f"{width}-{theme}-{name}",".results"))
                    page.locator("#theme").click();other="dark" if theme=="light" else "light"
                    require(page.locator("html").get_attribute("data-theme")==other,"theme switches")
                    page.reload(wait_until="networkidle");require(page.locator("html").get_attribute("data-theme")==other,"theme persists")
                    c.close()
            c=browser.new_context(viewport=dict(width=390,height=1000));page=c.new_page();observe(page)
            page.goto("http://127.0.0.1:18081/f27.html",wait_until="networkidle")
            page.locator("#scope").evaluate("e=>e.add(new Option('验收非法输入','invalid'))")
            submit(page,"relevance-price",400,True);rec["screenshots"].append(shot(page,"400",".results"))
            submit(page,"relevance-price")
            original=lab.read(P/"data/f27/hotels.json")[0];bad=dict(original);bad["snapshot_id"]="old"
            lab.put("h01",bad)
            try:
                submit(page,"relevance-price",502);rec["screenshots"].append(shot(page,"502-source",".results"))
            finally:lab.cleanup();lab.prepare()
            submit(page,"relevance-price")
            lab.request("DELETE","/tut-f27-hotels")
            try:
                submit(page,"relevance-price",502);rec["screenshots"].append(shot(page,"502-index",".results"))
            finally:lab.prepare()
            submit(page,"relevance-price")
            compose=["docker","compose","-f",str(P/"infra/f27/compose.yaml")]
            subprocess.run(compose+["stop","es"],check=True,capture_output=True)
            try:
                submit(page,"relevance-price",503);rec["screenshots"].append(shot(page,"503",".results"))
            finally:
                subprocess.run(compose+["up","-d"],check=True,capture_output=True)
                subprocess.run(["bash",str(P/"infra/f27/wait.sh")],check=True)
            submit(page,"relevance-price");c.close();browser.close()
        rec["java_pid_after"]=subprocess.check_output(["lsof","-tiTCP:18081","-sTCP:LISTEN"],text=True).strip()
        require(rec["java_pid_before"]==rec["java_pid_after"],"same actual Java process, including failure/recovery")
        require(not rec["js_errors"] and not rec["request_failures"] and not rec["browser_es_calls"],"no JS/network errors or browser direct ES")
        require(sorted(x["status"] for x in rec["http_errors"])==[400,502,502,503],"only deliberate real HTTP failures")
        rec["es_operation_count"]=lab.COUNT;rec["status"]="passed"
    except Exception as e:
        rec["status"]="failed";rec["error"]=str(e);rec["traceback"]=traceback.format_exc();raise
    finally:(HERE/"shell-review.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    print("F27 shell passed",len(rec["matrix"]),"matrix calls,",len(rec["calls"]),"total browser Java calls,",rec["es_operation_count"],"ES HTTP operations")
if __name__=="__main__":run()
