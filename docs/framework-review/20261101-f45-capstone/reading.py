#!/usr/bin/env python3
"""F45 HTTP/file reading, representative screenshots, and the existing reader controls."""
import functools
import http.server
import json
import pathlib
import threading
from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).resolve().parent
ROOT = D.parents[2]
BROWSER = str(pathlib.Path.home() / 'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell')
REC = {'viewports': [], 'screenshots': [], 'js_errors': [], 'http_errors': [], 'business_requests': []}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith('/es_web/'):
            self.send_error(404); return
        self.path = self.path[len('/es_web'):]
        super().do_GET()

    def log_message(self, *args):
        pass


def images(page, theme):
    page.wait_for_function("theme=>[...document.querySelectorAll('[data-d2-light]')].every(i=>i.complete&&i.naturalWidth>0&&i.currentSrc===new URL(theme==='dark'?i.dataset.d2Dark:i.dataset.d2Light,location.href).href&&i.closest('figure').querySelector('[data-expand-d2]').href===i.currentSrc)", arg=theme)


def shot(page, name, selector=None):
    if selector:
        page.locator(selector).scroll_into_view_if_needed()
    page.screenshot(path=str(D / 'screenshots' / (name + '.png')))
    REC['screenshots'].append(name + '.png')


def main():
    (D / 'screenshots').mkdir(exist_ok=True)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/es_web/'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=BROWSER, headless=True)
            REC['browser'] = browser.version
            for width in [1920, 1440, 1024, 768, 390, 320]:
                for theme in ['light', 'dark']:
                    ctx = browser.new_context(viewport={'width': width, 'height': 900}, permissions=['clipboard-read', 'clipboard-write'])
                    ctx.add_init_script("localStorage.setItem('es-web:theme'," + json.dumps(theme) + ');')
                    page = ctx.new_page()
                    page.on('pageerror', lambda e: REC['js_errors'].append(str(e)))
                    page.on('response', lambda r: REC['http_errors'].append([r.url, r.status]) if r.status >= 400 else None)
                    page.on('request', lambda r: REC['business_requests'].append(r.url) if '/api/' in r.url or ':20945' in r.url or ':18095' in r.url else None)
                    page.goto(base + 'framework/f45.html', wait_until='networkidle')
                    images(page, theme)
                    value = page.evaluate("""()=>{let a=document.querySelector('article.chapter'),r=a.getBoundingClientRect();return{column:r.width,scroll:document.documentElement.scrollWidth,blocks:[...a.querySelectorAll(':scope>header,:scope>section,:scope>footer,.d2-figure,.lesson>pre')].map(e=>{let b=e.getBoundingClientRect();return Math.max(Math.abs(b.left-r.left),Math.abs(b.right-r.right))})}}""")
                    assert value['scroll'] <= width and value['column'] <= 880.1 and max(value['blocks']) <= 1, value
                    if width >= 1024:
                        assert value['column'] == 880, value
                    if width == 390:
                        assert value['column'] == 362, value
                    REC['viewports'].append({'width': width, 'theme': theme, **value})
                    if (width, theme) in [(1440, 'light'), (1440, 'dark'), (390, 'light'), (320, 'dark')]:
                        shot(page, f'{width}-{theme}-opening')
                    if (width, theme) in [(1440, 'light'), (320, 'dark')]:
                        for id in ['fig-sync-boundary', 'task', 'data', 'fig-source-question', 'java']:
                            shot(page, f'{width}-{theme}-{id}', '#' + id)
                    if width == 320:
                        for selector in ['.ktable']:
                            el = page.locator(selector).first
                            assert el.evaluate("e=>{e.scrollLeft=e.scrollWidth-e.clientWidth;return e.scrollLeft>0&&['auto','scroll'].includes(getComputedStyle(e).overflowX)}"), selector
                    ctx.close()
            ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, permissions=['clipboard-read', 'clipboard-write'])
            page = ctx.new_page(); page.goto(base + 'framework/f45.html', wait_until='networkidle')
            page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
            REC['copied_blocks'] = page.locator('pre.code-block').count()
            for i in range(REC['copied_blocks']):
                pre = page.locator('pre.code-block').nth(i)
                pre.locator('xpath=preceding-sibling::*[1]').get_by_role('button', name='复制代码').click()
                assert page.evaluate('navigator.clipboard.readText()') == pre.locator('code').text_content()
            for id in page.locator('a[href^="#"]').evaluate_all('es=>es.map(e=>e.hash.slice(1))'):
                assert page.locator('[id="' + id + '"]').count() == 1
            page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=false)')
            for detail in [page.locator('details').first, page.locator('#drills details').first]:
                detail.locator('summary').click(); assert detail.get_attribute('open') is not None
                detail.locator('summary').click(); assert detail.get_attribute('open') is None
            page.locator('.theme-toggle').click(); images(page, 'dark')
            page.reload(wait_until='networkidle'); images(page, 'dark')
            page.locator('.read-toggle').click()
            assert page.evaluate("JSON.parse(localStorage.getItem('es-web:read'))") == {'f45': True}
            page.goto(base + 'framework/index.html')
            assert 'is-read' in page.locator('a[data-ch="f45"]').get_attribute('class')
            page.locator('a[data-ch="f45"]').click(); images(page, 'dark')
            page.locator('.pager a').first.click()
            assert page.url.endswith('/framework/f44.html')
            assert not page.locator('.read-toggle').evaluate("e=>e.classList.contains('is-on')")
            page.locator('.pager a').last.click(); assert page.url.endswith('/framework/f45.html')
            page.locator('.read-toggle').click()
            assert page.evaluate("JSON.parse(localStorage.getItem('es-web:read'))") == {}
            page.locator('.pager a').last.click()
            assert page.url.endswith('/chapters/ch01.html')
            page.go_back(wait_until='networkidle')
            REC['links'] = []
            for url in page.locator('a[href]').evaluate_all('es=>[...new Set(es.map(e=>e.href))]'):
                if url.startswith(base) and '#' not in url:
                    assert ctx.request.get(url).status == 200, url
                    REC['links'].append(url.removeprefix(base))
            ctx.close()
            for theme in ['light', 'dark']:
                ctx = browser.new_context(viewport={'width': 390, 'height': 900}, reduced_motion='reduce')
                ctx.add_init_script("localStorage.setItem('es-web:theme'," + json.dumps(theme) + ');')
                page = ctx.new_page(); page.goto((ROOT / 'framework/f45.html').as_uri(), wait_until='networkidle'); images(page, theme)
                assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == 'auto'
                page.locator('.theme-toggle').focus(); assert page.locator('.theme-toggle').evaluate('e=>e===document.activeElement')
                ctx.close()
            browser.close()
        assert not REC['js_errors'] and not REC['http_errors'] and not REC['business_requests'], REC
        REC['controls'] = 'copy, outline/drill, theme+reload, read+directory+isolation, previous/next, file, reduced-motion, focus passed'
        REC['passed'] = True
    finally:
        server.shutdown()
        (D / 'reading.json').write_text(json.dumps(REC, ensure_ascii=False, indent=2) + '\n')
    print('F45 reading checks passed')


if __name__ == '__main__':
    main()
