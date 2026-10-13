"""HTTP review of the planning diagram; this fixture is not a course page.

Run from the repository root with Python + Playwright + Chromium installed:
    python docs/framework-diagrams/review.py
"""
from datetime import datetime
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo
import json
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PREFIX = "/docs/framework-diagrams/"


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path != "/_framework-diagram-review.html":
            return super().do_GET()
        theme = parse_qs(url.query).get("theme", ["light"])[0]
        assert theme in ("light", "dark")
        body = f"""<!doctype html><html lang="zh-CN" data-theme="{theme}">
<meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>规划图 HTTP 验证夹具</title><link rel="stylesheet" href="/assets/css/style.css">
<link rel="stylesheet" href="/assets/css/chapter-diagrams.css">
<style>main{{padding-top:24px}}.diagram-view{{overflow-x:auto}}
.diagram-view img{{display:block;width:100%;min-width:720px;height:auto}}
figure{{margin:0}}figcaption{{padding-top:12px}}</style>
<main class="wrap chapter-visual"><article class="chapter"><h1>旅游门户系统分工</h1>
<p>规划概念图 · 箭头表示请求或数据流；课程与链路尚未实现。</p>
<figure><div class="diagram-view"><img alt="业务请求与日志驱动搜索投影"
src="{PREFIX}travel-system-{theme}.svg"></div>
<figcaption>数据库负责业务事务与精确报价，ES 提供搜索投影。
窄屏可在图内横向滚动，或<a href="{PREFIX}travel-system-{theme}.svg"
target="_blank" rel="noopener">展开图解 ↗</a>。</figcaption></figure>
</article></main></html>""".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}"
report = {
    "scope": "planning-diagram-only; course pages and real data chain not tested",
    "reviewedAt": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
    "sha256": {
        name: sha256((OUT / name).read_bytes()).hexdigest()
        for name in ["travel-system.d2", "travel-system-light.svg", "travel-system-dark.svg"]
    },
    "standalone": [], "fixture": [], "screenshots": [], "errors": [],
    "visualReview": "pending actual image inspection",
}
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("pageerror", lambda error: report["errors"].append(str(error)))
        page.on("response", lambda response: report["errors"].append(
            f"{response.status}: {response.url}") if response.status >= 400 else None)
        for theme in ["light", "dark"]:
            page.set_viewport_size({"width": 1440, "height": 900})
            assert page.goto(base + PREFIX + f"travel-system-{theme}.svg").status == 200
            page.evaluate("document.fonts.ready")
            bounds = page.evaluate("""() => {
              const svg = document.querySelector('svg'), box = svg.viewBox.baseVal;
              const text = [...svg.querySelectorAll('text')].map(e => {
                const b = e.getBBox(); return {text:e.textContent,x:b.x,y:b.y,width:b.width,height:b.height};
              });
              return {width:box.width,height:box.height,text};
            }""")
            assert bounds["text"]
            for item in bounds["text"]:
                assert item["x"] >= 0 and item["y"] >= 0, item
                assert item["x"] + item["width"] <= bounds["width"] + 1, item
                assert item["y"] + item["height"] <= bounds["height"] + 1, item
            report["standalone"].append({"theme": theme, **bounds})
            name = f"standalone-{theme}.png"
            page.screenshot(path=str(OUT / name))
            report["screenshots"].append(name)
            for width in [1440, 1024, 390, 320]:
                page.set_viewport_size({"width": width, "height": 844})
                assert page.goto(base + f"/_framework-diagram-review.html?theme={theme}").status == 200
                page.locator("img").evaluate("e => e.decode()")
                result = page.evaluate("""() => {
                  const article=document.querySelector('article'), view=document.querySelector('.diagram-view');
                  const a=article.getBoundingClientRect(), image=document.querySelector('img');
                  return {viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,
                    articleWidth:a.width,imageWidth:image.getBoundingClientRect().width,
                    viewWidth:view.clientWidth,viewScrollWidth:view.scrollWidth,
                    imageLoaded:image.complete&&image.naturalWidth>0};
                }""")
                assert result["pageWidth"] <= width, result
                assert result["articleWidth"] <= 880.01 and result["imageLoaded"], result
                if width < 600:
                    assert result["viewScrollWidth"] > result["viewWidth"], result
                report["fixture"].append({"theme": theme, **result})
                if width in [1440, 390]:
                    name = f"fixture-{width}-{theme}.png"
                    page.screenshot(path=str(OUT / name), full_page=True)
                    report["screenshots"].append(name)
                with page.expect_popup() as opened:
                    page.locator("figcaption a").click()
                popup = opened.value
                popup.wait_for_load_state()
                assert popup.url.endswith(f"travel-system-{theme}.svg")
                assert popup.evaluate("document.documentElement.localName") == "svg"
                assert popup.locator("svg").first.is_visible()
                popup.close()
        assert not report["errors"], report["errors"]
        browser.close()
    report["httpResult"] = "pass"
finally:
    server.shutdown()
    (OUT / "review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"result": report.get("httpResult"), "fixtureChecks": len(report["fixture"]),
                  "standaloneChecks": len(report["standalone"]), "visualReview": report["visualReview"]}))
