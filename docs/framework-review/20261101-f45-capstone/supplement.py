"""Final two-width checks with reference sections expanded; no business apps."""
import functools
import http.server
import json
import threading
from reading import D, ROOT, BROWSER, Handler, images
from playwright.sync_api import sync_playwright

result = {'screenshots': [], 'viewports': [], 'js_errors': []}
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=BROWSER, headless=True)
        for width, theme in [(1440, 'light'), (320, 'dark')]:
            ctx = browser.new_context(viewport={'width': width, 'height': 900})
            ctx.add_init_script("localStorage.setItem('es-web:theme'," + json.dumps(theme) + ');')
            page = ctx.new_page()
            page.on('pageerror', lambda e: result['js_errors'].append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f45.html', wait_until='networkidle')
            images(page, theme)
            page.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            result['viewports'].append({'width': width, 'theme': theme, 'all_reference_sections_open': True,
                'code_blocks': page.locator('pre.code-block').count(), 'no_page_overflow': True})
            for target in ['hotel-results', 'sync-results']:
                el = page.locator('#' + target)
                el.scroll_into_view_if_needed()
                page.evaluate('scrollBy(0,-100)')
                name = f'final-{width}-{theme}-{target}.png'
                page.screenshot(path=str(D / 'screenshots' / name))
                result['screenshots'].append(name)
                if width == 320:
                    assert el.evaluate("e=>{e.scrollLeft=e.scrollWidth-e.clientWidth;return e.scrollLeft>0&&['auto','scroll'].includes(getComputedStyle(e).overflowX)}")
                    name = f'final-{width}-{theme}-{target}-right.png'
                    page.screenshot(path=str(D / 'screenshots' / name))
                    result['screenshots'].append(name)
            ctx.close()
        browser.close()
    assert not result['js_errors'], result
    result['passed'] = True
finally:
    server.shutdown()
    (D / 'supplement.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print('F45 expanded reference checks passed')
