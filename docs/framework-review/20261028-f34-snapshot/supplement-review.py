#!/usr/bin/env python3
"""Full embedded figures plus final directory entry/navigation evidence."""
import datetime, functools, http.server, importlib.util, json, pathlib, threading
from playwright.sync_api import sync_playwright
D = pathlib.Path(__file__).resolve().parent
ROOT = D.parents[2]
spec = importlib.util.spec_from_file_location('f34_reading', D / 'reading-review.py')
reading = importlib.util.module_from_spec(spec); spec.loader.exec_module(reading)
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(reading.Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port) + '/es_web/'
record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'figures': [], 'directory': [], 'errors': []}
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=reading.BROWSER, headless=True)
        for theme in ['light', 'dark']:
            context = browser.new_context(viewport={'width': 1440, 'height': 900})
            context.add_init_script("localStorage.setItem('es-web:theme'," + json.dumps(theme) + ');')
            page = context.new_page(); page.on('pageerror', lambda e: record['errors'].append(str(e)))
            page.goto(base + 'framework/f34.html', wait_until='networkidle'); reading.images(page, theme)
            # Element screenshots of tall figures otherwise include the viewport's sticky topbar.
            # Hide only the header for these isolated figure captures, never edit the product/assets.
            isolated = page.add_style_tag(content='.topbar{visibility:hidden!important}')
            for slug in ['replica-backup', 'restore-gates']:
                figure = page.locator('#fig-' + slug)
                target = D / 'screenshots' / ('full-' + slug + '-' + theme + '.png')
                figure.screenshot(path=str(target))
                record['figures'].append({'file': str(target.relative_to(ROOT)), 'theme': theme,
                    'box': figure.bounding_box(), 'image': figure.locator('img').get_attribute('src')})
            isolated.evaluate('e=>e.remove()')
            for width in [1440, 390, 320]:
                page.set_viewport_size({'width': width, 'height': 900})
                page.goto(base + 'framework/index.html', wait_until='networkidle')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                link = page.locator('a[data-ch="f34"]'); link.scroll_into_view_if_needed()
                assert link.get_attribute('href') == 'f34.html'
                if width in [1440, 390]:
                    target = D / 'screenshots' / f'directory-{width}-{theme}.png'
                    page.screenshot(path=str(target)); record['directory'].append(str(target.relative_to(ROOT)))
                link.click(); page.wait_for_url('**/framework/f34.html'); reading.images(page, theme)
                assert page.locator('article').get_attribute('data-ch') == 'f34'
            context.close()
        browser.close()
    assert not record['errors'], record
    record['passed'] = True
    record['isolated_capture_note'] = 'Four tall figure crops hide only the sticky page header in the browser capture; page, D2 and SVG unchanged. Earlier header-overlap crops are not used as final diagram evidence.'
finally:
    server.shutdown()
    (D / 'supplement-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print('F34 full figures and final directory checks passed')
