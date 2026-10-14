#!/usr/bin/env python3
"""F02 作者验收：人工模型核对与真实 HTTP/离线阅读；不访问实验服务。"""
import copy
import datetime
import functools
import hashlib
import http.server
import json
import pathlib
import re
import threading
import traceback
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WIDTHS = [1920, 1440, 1024, 768, 390, 320]
THEMES = ["light", "dark"]


def require(value, detail):
    if not value:
        raise AssertionError(detail)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_model():
    model = json.loads((ROOT / "framework/data/f02/model.json").read_text())
    docs = model["documents"]
    query = model["query"]
    term = query["hand_query_terms"][0]
    inverted = {}
    scores = {}
    for entry in docs:
        label, document = entry["label"], entry["document"]
        require(entry["proposed_es_id"] == document["attraction_id"], entry)
        require(type(document["ticket_price_fen"]) is int and document["currency"] == "CNY", entry)
        scores[label] = sum(model["hand_score"][field + "_contains_term"]
                            for field in query["fields"] if term in entry["hand_terms"][field])
        for field, terms in entry["hand_terms"].items():
            for word in set(terms):
                inverted.setdefault(field + ":" + word, []).append(label)
    require([e["label"] for e in docs] == list("ABCDE"), "five fixed labels")
    require(docs[0]["document"] == json.loads((ROOT / "framework/data/f02/xihu.json").read_text()), "A JSON fixture")
    require(inverted["name:西湖"] == list("ACDE"), inverted)
    require(inverted["description:西湖"] == list("BDE"), inverted)
    require(inverted["name:茶园"] == ["B"] and inverted["description:游览"] == list("ABD"), inverted)
    require(scores == {"A": 3, "B": 1, "C": 3, "D": 4, "E": 4}, scores)

    def solve(items, budget=20000, fields=("name", "description")):
        candidates = [e for e in items if any(term in e["hand_terms"][f] for f in fields)]
        allowed = [e for e in candidates if e["document"]["city_code"] == "HZ"
                   and e["document"]["currency"] == "CNY" and e["document"]["status"] == "open"
                   and e["document"]["ticket_price_fen"] <= budget]
        score = lambda e: sum(model["hand_score"][f + "_contains_term"] for f in fields if term in e["hand_terms"][f])
        return {"candidates": [e["label"] for e in candidates], "allowed": [e["label"] for e in allowed],
                "relevance": [e["label"] for e in sorted(allowed, key=lambda e: (-score(e), e["document"]["attraction_id"]))],
                "price": [e["label"] for e in sorted(allowed, key=lambda e: (e["document"]["ticket_price_fen"], e["document"]["attraction_id"]))]}

    checks = {"baseline": solve(docs), "name_only": solve(docs, fields=("name",)), "budget_260": solve(docs, 26000)}
    changed = copy.deepcopy(docs)
    changed[1]["document"]["ticket_price_fen"] = 0
    checks["same_price"] = solve(changed)
    changed[1]["document"]["ticket_price_fen"] = model["update"]["to_price_fen"]
    checks["after_visible_update"] = solve(changed)
    extra = copy.deepcopy(docs)
    new = copy.deepcopy(docs[1]); new["label"] = "F"
    new["document"].update(attraction_id="a-hz-tea2", ticket_price_fen=5000)
    new["hand_terms"]["name"] = ["茶园"]
    extra.append(new)
    checks["new_F"] = solve(extra)
    require(checks["baseline"]["allowed"] == list("AB") and checks["baseline"]["relevance"] == list("AB"), checks)
    require(checks["name_only"]["candidates"] == list("ACDE") and checks["name_only"]["allowed"] == ["A"], checks)
    require(checks["budget_260"]["relevance"] == list("DAB") and checks["budget_260"]["price"] == list("ABD"), checks)
    require(checks["same_price"]["relevance"] == list("AB") and checks["same_price"]["price"] == list("BA"), checks)
    require(checks["after_visible_update"]["allowed"] == ["A"], checks)
    require(checks["new_F"]["relevance"] == list("ABF") and checks["new_F"]["price"] == list("AFB"), checks)
    return model, {"scope": "author recalculation of artificial rules, not ES output", "inverted_excerpt":
                   {key: inverted[key] for key in ["name:西湖", "description:西湖", "name:茶园", "description:游览"]},
                   "hand_scores": scores, "scenarios": checks}


def static_links():
    checked = []
    files = ["framework/f02.html", "framework/f01.html", "framework/index.html", "README.md", "PLAN.md",
             "FRAMEWORK_PLAN.md", "FRAMEWORK_CASES.md", "FRAMEWORK_STANDARD.md", "docs/framework-lesson-prompt.md",
             "framework/data/f02/README.md", "framework/diagrams/f02/README.md", str(HERE.relative_to(ROOT) / "README.md")]
    for name in files:
        file = ROOT / name; contents = file.read_text()
        links = re.findall(r'(?:href|src|data-d2-light|data-d2-dark)="([^"]+)"', contents) if file.suffix == ".html" else re.findall(r'\]\(([^)]+)\)', contents)
        for target in links:
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            require((file.parent / unquote(parsed.path)).exists(), {"file": name, "target": target})
            checked.append({"file": name, "target": target})
    receipt = json.loads((ROOT / "framework/diagrams/f02/generation.json").read_text())
    for name, digest in receipt["sha256"].items():
        require(sha(ROOT / name) == digest, {"diagram_receipt_mismatch": name})
    require((ROOT / ".nojekyll").exists(), ".nojekyll")
    return checked


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/es_web/"):
            self.send_error(404); return
        self.path = self.path[len("/es_web"):]
        super().do_GET()

    def log_message(self, *args):
        pass


def observe(page, record):
    page.on("pageerror", lambda error: record["js_errors"].append(str(error)))
    page.on("response", lambda response: record["http_failures"].append({"url": response.url, "status": response.status}) if response.status >= 400 else None)
    page.on("requestfailed", lambda request: record["request_failures"].append({"url": request.url, "failure": request.failure}))


def diagrams(page, theme):
    page.wait_for_function("""theme => [...document.querySelectorAll('[data-d2-light]')].every(img => {
      const expected = new URL(theme === 'dark' ? img.dataset.d2Dark : img.dataset.d2Light, location.href).href;
      return img.complete && img.naturalWidth > 0 && img.currentSrc === expected && img.closest('figure').querySelector('[data-expand-d2]').href === expected;
    })""", arg=theme)
    result = page.locator("[data-d2-light]").evaluate_all("images => images.map(i => ({src:i.currentSrc, width:i.naturalWidth, height:i.naturalHeight, alt:i.alt}))")
    require(len(result) == 2, result)
    return result


def measure(page, chapter=True):
    result = page.evaluate("""chapter => {
      const art = chapter ? document.querySelector('article.chapter') : document.querySelector('main.wrap');
      const rect = art.getBoundingClientRect();
      const blocks = chapter ? [...art.querySelectorAll(':scope > header, :scope > section, :scope > footer, .lesson > h2, .d2-figure, .d2-figure > figcaption, pre.code-block, .code-tools')].map(el => {
        const r=el.getBoundingClientRect(); return {tag:el.tagName,id:el.id,left:r.left,right:r.right};}) : [];
      const scrollables = [...art.querySelectorAll('table.ktable, .d2-view, pre.code-block')].map(el=>{
        const initial=el.scrollLeft; el.scrollLeft=el.scrollWidth; const moved=el.scrollLeft; el.scrollLeft=initial;
        return {tag:el.tagName,id:el.id,client:el.clientWidth,scroll:el.scrollWidth,overflow:getComputedStyle(el).overflowX,moved};});
      return {viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,
        theme:document.documentElement.dataset.theme,left:rect.left,right:rect.right,width:rect.width,blocks,scrollables};
    }""", chapter)
    require(result["page"] <= result["viewport"] and result["body"] <= result["viewport"], result)
    if chapter:
        require(abs(result["width"] - min(880, result["viewport"] - (28 if result["viewport"] <= 600 else 44))) <= 1, result)
        for block in result["blocks"]:
            require(abs(block["left"] - result["left"]) <= 1 and abs(block["right"] - result["right"]) <= 1, {"misaligned":block})
        for container in result["scrollables"]:
            if container["scroll"] > container["client"] + 2:
                require(container["overflow"] in ["auto", "scroll"] and container["moved"] > 0, container)
    return result


def anchors(page):
    page.emulate_media(reduced_motion="reduce")
    page.locator(".chapter-outline summary").click()
    links = page.locator(".chapter-outline a, .diagram-jumps a")
    result = []
    for i in range(links.count()):
        href = links.nth(i).get_attribute("href")
        require(page.locator(href).count() == 1, href)
        links.nth(i).click()
        evidence = page.evaluate("""href=>({href,top:document.querySelector(href).getBoundingClientRect().top,bar:document.querySelector('.topbar').getBoundingClientRect().bottom})""", href)
        require(evidence["top"] >= evidence["bar"] - 1, evidence)
        result.append(evidence)
    page.locator(".chapter-outline summary").click()
    return result


def check_tables(page, model, verification):
    for entry in model["documents"]:
        label, doc = entry["label"], entry["document"]
        cells = page.locator(f'[data-sample="{label}"] td').all_text_contents()
        require(cells == [label + " · " + doc["name"], f'{doc["city_code"]} / {doc["ticket_price_fen"]} / {doc["status"]}', doc["description"]], cells)
        terms = page.locator(f'[data-terms="{label}"] td').all_text_contents()
        require(terms == [label, " / ".join(entry["hand_terms"]["name"]), " / ".join(entry["hand_terms"]["description"])], terms)
        require(int(page.locator(f'[data-score="{label}"] td').nth(2).inner_text()) == verification["hand_scores"][label], label)
    for key, labels in verification["inverted_excerpt"].items():
        require(page.locator(f'[data-inverted="{key}"] td').nth(2).inner_text() == "、".join(labels), key)
    require(json.loads(page.locator("pre code").inner_text()) == model["documents"][0]["document"], "visible JSON matches model")


def shot(page, name, target=None):
    path = HERE / "screenshots" / (name + ".png")
    if target:
        header = page.locator(".topbar")
        if header.count():
            header.evaluate("el=>el.style.visibility='hidden'")
        try:
            page.locator(target).first.screenshot(path=str(path), timeout=20000)
        finally:
            if header.count():
                header.evaluate("el=>el.style.visibility=''")
    else:
        page.screenshot(path=str(path), timeout=20000)
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "visual_review": "pending"}


def run():
    model, verification = check_model()
    record = {"recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "scope":"F02 concept reading; no ES runtime validation",
              "reasoning": {"requested":"xhigh", "actual":"not configurable or verifiable in root session", "content_review":"author self-review; no independent agent"},
              "model_review": verification, "static_links": static_links(), "matrix": [], "regression": [], "independent_diagrams": [],
              "screenshots": [], "js_errors": [], "http_failures": [], "request_failures": [], "business_requests": []}
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    base = origin + "/es_web/"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            record["browser"] = {"engine":"Chromium", "version":browser.version}
            for width in WIDTHS:
                for theme in THEMES:
                    context = browser.new_context(viewport={"width":width,"height":1000}, reduced_motion="reduce", permissions=["clipboard-read","clipboard-write"])
                    context.add_init_script(f"localStorage.setItem('es-web:theme', '{theme}')")
                    def route_request(route):
                        url = urlsplit(route.request.url)
                        if url.hostname in {"localhost","127.0.0.1","::1"} and url.port in {9200,9201,19200,8080}:
                            record["business_requests"].append(route.request.url); route.abort()
                        else:
                            route.continue_()
                    context.route("**/*", route_request)
                    page = context.new_page(); observe(page, record)
                    page.goto(base + "framework/f02.html", wait_until="networkidle")
                    images = diagrams(page, theme)
                    check_tables(page, model, verification)
                    anchor_record = anchors(page)
                    exercise_records = []
                    for exercise in page.locator(".drills details").all():
                        exercise.locator("summary").click()
                        require(exercise.get_attribute("open") is not None, "exercise does not open")
                        exercise_records.append(exercise.locator("summary").inner_text())
                        exercise.locator("summary").click()
                    require(len(exercise_records) == 7, exercise_records)
                    record["matrix"].append({"width":width,"theme":theme,"layout":measure(page),"images":images,"anchors":anchor_record,"folds":exercise_records})
                    if width in [1440,390]:
                        page.evaluate("window.scrollTo(0,0)")
                        record["screenshots"].append(shot(page,f"f02-{width}-{theme}-opening"))
                        record["screenshots"].append(shot(page,f"f02-{width}-{theme}-samples","#sample-table"))
                        record["screenshots"].append(shot(page,f"f02-{width}-{theme}-terms","#terms-table"))
                        record["screenshots"].append(shot(page,f"f02-{width}-{theme}-diagram","#fig-search-path"))
                        record["screenshots"].append(shot(page,f"f02-{width}-{theme}-visibility","#fig-visibility"))
                        page.locator(".drills details").nth(2).locator("summary").click()
                        page.locator(".drills details").nth(5).locator("summary").click()
                        record["screenshots"].append(shot(page,f"f02-{width}-{theme}-exercises",".drills"))
                    # Necessary navigation pages only; no other chapter work.
                    page.goto(base + "framework/index.html", wait_until="networkidle")
                    require(page.locator('.curriculum-lesson-link[href="f02.html"][data-ch="f02"]').count() == 1, "F02 directory entry")
                    record["regression"].append({"page":"directory", "width":width,"theme":theme,"layout":measure(page, False)})
                    page.goto(base + "framework/f01.html", wait_until="networkidle")
                    require(page.locator('.pager a[href="f02.html"]').count() == 1, "F01 next lesson")
                    record["regression"].append({"page":"F01", "width":width,"theme":theme,"layout":measure(page)})
                    context.close()
            # Clipboard, theme persistence, keyboard, progress and actual navigation.
            context = browser.new_context(viewport={"width":1440,"height":1000}, permissions=["clipboard-read","clipboard-write"])
            page = context.new_page(); observe(page, record)
            page.goto(base + "framework/f02.html", wait_until="networkidle")
            page.evaluate("localStorage.setItem('es-web:read',JSON.stringify({'f01':true,'f01-v2':true}));localStorage.setItem('es-web:theme','light')")
            page.reload(wait_until="networkidle")
            page.locator(".copy-code").click()
            require(json.loads(page.evaluate("navigator.clipboard.readText()")) == model["documents"][0]["document"], "actual clipboard")
            page.locator(".copy-code").focus()
            page.keyboard.press("Tab")
            page.keyboard.press("Shift+Tab")
            require(page.locator(".copy-code").evaluate("el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=='none'"), "keyboard focus visible")
            page.locator(".theme-toggle").click(); diagrams(page,"dark")
            page.reload(wait_until="networkidle"); diagrams(page,"dark")
            page.locator(".read-toggle").click()
            page.reload(wait_until="networkidle")
            require(page.locator(".read-toggle").evaluate("el=>el.classList.contains('is-on')"), "F02 read persistence")
            page.locator('.pager a[href="index.html"]').click(); page.wait_for_url(base+"framework/index.html")
            require(page.locator('[data-ch="f02"]').evaluate("el=>el.classList.contains('is-read')"), "directory read badge")
            page.locator('.curriculum-lesson-link[href="f02.html"]').click(); page.wait_for_url(base+"framework/f02.html")
            page.locator(".read-toggle").click()
            require(page.evaluate("JSON.stringify(JSON.parse(localStorage.getItem('es-web:read'))) ") == '{"f01":true,"f01-v2":true}', "unread preserves other keys")
            page.locator('.pager a[href="f01.html"]').click(); page.wait_for_url(base+"framework/f01.html")
            page.locator('.pager a[href="f02.html"]').click(); page.wait_for_url(base+"framework/f02.html")
            require(page.locator('a[href="f03.html"]').count() == 0, "no nonexistent F03 link")
            # Open each diagram through its current-theme link in a real new tab.
            for link in page.locator("[data-expand-d2]").all():
                with page.expect_popup() as popup_info:
                    link.click()
                popup = popup_info.value; popup.wait_for_load_state("load")
                require(popup.locator("svg").count() >= 1 and "-dark.svg" in popup.url, popup.url)
                popup.close()
            record["interactions"] = {"clipboard":"actual copied JSON equals fixture", "theme":"switch + reload + both image/expand links",
                "keyboard":"copy focus outline", "progress":"mark, reload, directory badge, unmark; f01/f01-v2 keys preserved",
                "navigation":"directory/F01/F02 actual links + both dark diagram popups", "next":"F03 labelled pending; no broken link"}
            # Standalone figures at all required desktop widths, both themes.
            for width in [1440,1600,1920,2048]:
                page.set_viewport_size({"width":width,"height":1000})
                for theme in THEMES:
                    for slug in ["search-path","visibility"]:
                        page.goto(base+f"framework/diagrams/f02/{slug}-{theme}.svg",wait_until="load")
                        record["independent_diagrams"].append({"width":width,"theme":theme,"slug":slug,
                            "loaded":page.locator("svg").first.is_visible()})
                        if width == 1440:
                            record["screenshots"].append(shot(page,f"f02-independent-{slug}-{theme}","svg"))
            # file:// assets and theme switching, plus reduced-motion style.
            page.set_viewport_size({"width":390,"height":1000})
            page.goto((ROOT/"framework/f02.html").as_uri(),wait_until="load")
            theme = page.evaluate("document.documentElement.dataset.theme"); diagrams(page,theme)
            page.locator(".theme-toggle").click()
            theme2 = page.evaluate("document.documentElement.dataset.theme"); diagrams(page,theme2)
            require(theme != theme2, "offline theme switch")
            page.emulate_media(reduced_motion="reduce")
            require(page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") != "smooth", "reduced motion")
            record["offline"] = {"themes":[theme,theme2],"layout":measure(page),"reduced_motion":"no smooth scrolling; no mechanism player"}
            context.close(); browser.close()
        require(not record["js_errors"] and not record["http_failures"] and not record["request_failures"] and not record["business_requests"], record)
        record["sha256"] = {str(p.relative_to(ROOT)):sha(p) for pattern in ["framework/f02.html","framework/data/f02/*","framework/diagrams/f02/*", "framework/assets/course.css", "framework/assets/course.js", "framework/index.html", "framework/f01.html"] for p in ROOT.glob(pattern) if p.is_file()}
        record["status"] = "passed"
    except Exception:
        record["status"] = "failed"; record["failure"] = traceback.format_exc()
        raise
    finally:
        server.shutdown(); server.server_close()
        (HERE/"http-review.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print(f"F02 model + HTTP passed: {len(record['matrix'])} lesson groups, {len(record['regression'])} navigation groups, {len(record['independent_diagrams'])} standalone diagrams; {len(record['screenshots'])} PNGs pending visual review")


if __name__ == "__main__":
    run()
