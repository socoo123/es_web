#!/usr/bin/env python3
"""本课作者 HTTP 阅读验收；Playwright 不是读者工程依赖。"""
import datetime
import functools
import hashlib
import http.server
import json
import pathlib
import threading
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SHOTS = HERE / "screenshots"
SHOTS.mkdir(exist_ok=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/es_web/"):
            self.send_error(404)
            return
        self.path = self.path[len("/es_web"):]
        super().do_GET()

    def log_message(self, *args):
        pass


def run():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    base = origin + "/es_web/"
    records = []
    errors, bad_responses, requests = [], [], []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("response", lambda response: bad_responses.append({"url": response.url, "status": response.status}) if response.status >= 400 else None)
            page.on("request", lambda request: requests.append(request.url))
            for width in [1920, 1440, 1024, 768, 390, 320]:
                for theme in ["light", "dark"]:
                    page.set_viewport_size({"width": width, "height": 1000 if width > 600 else 844})
                    page.goto(base + "framework/f01.html", wait_until="networkidle")
                    page.evaluate("t => {localStorage.setItem('es-web:theme', t); location.reload()}", theme)
                    page.wait_for_load_state("networkidle")
                    page.wait_for_function("[...document.images].every(i => i.complete && i.naturalWidth > 0)")
                    measured = page.evaluate("""() => ({
                      theme: document.documentElement.dataset.theme,
                      viewport: innerWidth,
                      pageWidth: document.documentElement.scrollWidth,
                      widths: [...document.querySelectorAll('.ch-header,.goal,.lesson,.drills,.pitfalls,.recap,.ch-footer,.d2-shell')].map(el => ({width:el.getBoundingClientRect().width, left:el.getBoundingClientRect().left})),
                      codeCount: document.querySelectorAll('pre.code-block').length,
                      diagram: document.querySelector('[data-d2-light]').getAttribute('src'),
                      expand: document.querySelector('[data-expand-d2]').getAttribute('href'),
                      diagramLocalScroll: document.querySelector('.d2-view').scrollWidth > document.querySelector('.d2-view').clientWidth
                    })""")
                    assert measured["theme"] == theme
                    assert measured["pageWidth"] <= width, measured
                    assert max(x["width"] for x in measured["widths"]) <= 880.5
                    assert max(x["left"] for x in measured["widths"]) - min(x["left"] for x in measured["widths"]) <= 1
                    if width >= 1024:
                        assert abs(measured["widths"][0]["width"] - 880) <= 1
                    assert f"first-search-{theme}.svg" in measured["diagram"]
                    assert f"first-search-{theme}.svg" in measured["expand"]
                    if width < 768:
                        assert measured["diagramLocalScroll"]
                    # 展开静态图必须可访问；代码按钮复制实际 DOM 内容。
                    expanded = context.request.get(page.locator('[data-expand-d2]').get_attribute('href'))
                    assert expanded.status == 200 and '<svg' in expanded.text()
                    page.locator('.copy-code').first.click()
                    page.wait_for_function("document.querySelector('.copy-code').textContent === '已复制'")
                    assert page.locator('.copy-code').first.inner_text() == '已复制'
                    assert page.evaluate('navigator.clipboard.readText()') == page.locator('pre.code-block code').first.inner_text()
                    page.locator('.chapter-outline summary').click()
                    assert page.locator('.chapter-outline').evaluate('(el) => el.open')
                    page.locator('.chapter-outline a[href="#create"]').click()
                    assert page.url.endswith('#create')
                    page.locator('.drills summary').first.click()
                    assert page.locator('.drills details').first.evaluate('(el) => el.open')
                    if width in [1440, 390]:
                        page.evaluate('scrollTo(0,0)')
                        page.screenshot(path=str(SHOTS / f'f01-{width}-{theme}.png'))
                        if width == 1440:
                            page.locator('#fig-first-search').screenshot(path=str(SHOTS / f'f01-diagram-{theme}.png'))
                        else:
                            page.locator('pre[data-source="projects/travel-search/search/f01/index.json"]').screenshot(path=str(SHOTS / f'f01-code-390-{theme}.png'))
                    records.append(measured)

            page.goto(base + 'framework/f01.html', wait_until='networkidle')
            page.locator('.theme-toggle').click()
            assert page.locator('[data-d2-light]').get_attribute('src').endswith('light.svg')
            page.locator('.read-toggle').click()
            assert '已读' in page.locator('.read-toggle').inner_text()
            page.goto(base + 'framework/index.html', wait_until='networkidle')
            assert page.locator('.progress-text').inner_text() == '已读 1 / 1 课'
            assert 'is-read' in page.locator('.card[data-ch="f01"]').get_attribute('class')
            page.locator('.card').click()
            assert page.url.endswith('/framework/f01.html')
            page.locator('.read-toggle').click()
            page.goto(base + 'framework/index.html', wait_until='networkidle')
            assert page.locator('.progress-text').inner_text() == '已读 0 / 1 课'
            # 验证课程所有本地链接，不加载其他章节正文做内容审查。
            page.goto(base + 'framework/f01.html', wait_until='networkidle')
            local_links = page.locator('a').evaluate_all('(els) => [...new Set(els.map(el=>el.href))]')
            for url in local_links:
                if url.startswith(base) and not url.startswith(base + 'framework/f01.html#'):
                    assert context.request.get(url).status == 200, url
            assert all(':19200' not in url and ':9200' not in url for url in requests)
            # 根入口只检查链接与无溢出；保留其原有源码连接检查。
            page.goto(base, wait_until='networkidle')
            assert page.locator('a[href="framework/f01.html"]').count() == 1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            reduced = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion='reduce')
            reduced_page = reduced.new_page()
            reduced_page.goto(base + 'framework/f01.html', wait_until='networkidle')
            assert reduced_page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") != 'smooth'
            # file 预览只要求可读、主题/图可切换；不跨 origin 调服务。
            file_page = context.new_page()
            file_page.goto((ROOT / 'framework/f01.html').as_uri(), wait_until='load')
            assert file_page.locator('pre.code-block').count() >= 15
            file_page.locator('.theme-toggle').click()
            file_page.wait_for_function("document.querySelector('[data-d2-light]').complete")
            assert file_page.locator('[data-d2-light]').evaluate('(el) => el.naturalWidth') > 0
            assert not errors, errors
            assert not bad_responses, bad_responses
            result = {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      "scope": "HTTP /es_web/ framework reading; no Pages business operation",
                      "playwright": 'Chromium', "measurements": records, "js_errors": errors,
                      "http_errors": bad_responses, "interactions": ['copy', 'theme + SVG', 'expand', 'outline', 'answers', 'read/unread + index progress', 'navigation', 'local links', 'reduced motion', 'file preview'],
                      "screenshots": sorted(str(x.relative_to(ROOT)) for x in SHOTS.glob('*.png')),
                      "visual_review": "pending screenshot inspection",
                      "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in [ROOT/'framework/f01.html', ROOT/'framework/index.html', ROOT/'framework/assets/course.css', ROOT/'framework/assets/course.js']}}
            (HERE / 'http-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            browser.close()
            print('HTTP 12 组尺寸/主题和阅读交互通过；截图待实际查看')
    finally:
        server.shutdown()


if __name__ == '__main__':
    run()
