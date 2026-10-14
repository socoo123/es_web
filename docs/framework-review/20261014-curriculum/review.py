#!/usr/bin/env python3
"""作者用：本轮规划与入口阅读验收，不运行 ES 或业务演示站。"""
import datetime
import functools
import hashlib
import http.server
import json
import pathlib
import re
import threading
from html import unescape
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith('/es_web/'):
            self.send_error(404)
            return
        self.path = self.path[len('/es_web'):]
        super().do_GET()

    def log_message(self, *args):
        pass


def run():
    plan = (ROOT / 'FRAMEWORK_PLAN.md').read_text()
    directory = (ROOT / 'framework/index.html').read_text()
    cases = (ROOT / 'FRAMEWORK_CASES.md').read_text()
    plan_rows = re.findall(r'^\| (F\d{2}) \| (.*?) \| (.*?) \|$', plan, re.M)
    case_ids = re.findall(r'^\| (F\d{2}) \|', cases, re.M)
    expected = [f'F{i:02}' for i in range(1, 46)]
    assert [r[0] for r in plan_rows] == case_ids == expected
    directory_rows = re.findall(r'curriculum-no">(F\d{2})</span><h3>(.*?)</h3>.*?</div><p>(.*?)</p>', directory)
    assert [(n, unescape(t), unescape(d)) for n, t, d in directory_rows] == plan_rows
    assert len(re.findall(r'id="stage-\d"', directory)) == 8
    assert not re.search(r'href="f(?:0[2-9]|[1-4]\d)\.html"', directory)
    for filename in ['FRAMEWORK_PLAN.md', 'FRAMEWORK_CASES.md', 'FRAMEWORK_STANDARD.md',
                     'PLAN.md', 'README.md', 'AGENTS.md', 'CLAUDE.md', 'CHAPTER_STANDARD.md',
                     'docs/framework-lesson-prompt.md', 'projects/travel-search/README.md']:
        contents = (ROOT / filename).read_text()
        assert contents.count('```') % 2 == 0, filename
        for target in re.findall(r'\]\(([^)]+)\)', contents):
            if re.match(r'https?://|#|mailto:', target):
                continue
            local = target.split('#')[0]
            assert (ROOT / filename).parent.joinpath(local).exists(), (filename, target)

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/es_web/'
    measurements, errors, failures, requests, screenshots = [], [], [], [], []
    shot_dir = HERE / 'screenshots'
    shot_dir.mkdir(exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for width in [1920, 1440, 1024, 768, 390, 320]:
                for theme in ['light', 'dark']:
                    context = browser.new_context(viewport={'width': width, 'height': 1000 if width > 600 else 900})
                    context.add_init_script(f"localStorage.setItem('es-web:theme', '{theme}')")
                    page = context.new_page()
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    page.on('response', lambda r: failures.append({'url': r.url, 'status': r.status}) if r.status >= 400 else None)
                    page.on('request', lambda r, current=page: requests.append({'page': current.url, 'url': r.url}))
                    page.goto(base + 'framework/index.html', wait_until='networkidle')
                    assert page.locator('.curriculum-list > li').count() == 45
                    assert page.locator('.curriculum-stage').count() == 8
                    assert page.locator('.curriculum-status').all_text_contents() == ['待编写'] * 45
                    measure = page.evaluate('''() => {
                      const main = document.querySelector('main');
                      const cs = getComputedStyle(main);
                      return { viewport: innerWidth, pageWidth: document.documentElement.scrollWidth,
                        readingWidth: main.getBoundingClientRect().width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight),
                        theme: document.documentElement.dataset.theme,
                        stageWidths: [...document.querySelectorAll('.curriculum-stage')].map(e => e.getBoundingClientRect().width) };
                    }''')
                    assert measure['pageWidth'] <= width, measure
                    assert measure['readingWidth'] <= 880.1, measure
                    assert measure['theme'] == theme, measure
                    assert all(abs(w - measure['readingWidth']) <= 1 for w in measure['stageWidths']), measure
                    measurements.append(measure)
                    page.locator('.theme-toggle').click()
                    assert page.locator('html').get_attribute('data-theme') != theme
                    page.locator('.theme-toggle').click()
                    assert page.locator('html').get_attribute('data-theme') == theme
                    page.emulate_media(reduced_motion='reduce')
                    for stage in range(1, 9):
                        page.locator(f'.curriculum-nav a[href="#stage-{stage}"]').click()
                        page.wait_for_function(f"location.hash === '#stage-{stage}'")
                        page.wait_for_function(f"document.querySelector('#stage-{stage}').getBoundingClientRect().top >= document.querySelector('.topbar').getBoundingClientRect().bottom")
                    page.emulate_media(reduced_motion='no-preference')
                    page.goto(base + 'framework/index.html', wait_until='networkidle')
                    if width in [1440, 390]:
                        for slug, selector in [('opening', '.hero'), ('courses', '#stage-2'), ('intro', '#new-f01')]:
                            if slug != 'opening':
                                page.locator(selector).scroll_into_view_if_needed()
                            name = f'curriculum-{width}-{theme}-{slug}.png'
                            page.screenshot(path=str(shot_dir / name))
                            screenshots.append(name)
                    # 本轮改动首页入口与旧课提示；共用 CSS 对旧课的有限回归。
                    for path in ['index.html', 'framework/f01.html']:
                        page.goto(base + path, wait_until='networkidle')
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (path, width, theme)
                        if path.startswith('framework/'):
                            assert page.locator('.legacy-course-note').is_visible()
                            assert page.locator('[data-d2-light]').count() == 1
                        else:
                            assert page.locator('.cta-actions a[href="framework/index.html"]').count() == 1
                    context.close()
            reduced = browser.new_context(viewport={'width': 390, 'height': 900}, reduced_motion='reduce')
            page = reduced.new_page()
            page.goto(base + 'framework/index.html', wait_until='networkidle')
            assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == 'auto'
            page.locator('.curriculum-nav a[href="#stage-5"]').click()
            assert page.evaluate('location.hash') == '#stage-5'
            reduced.close()
            local = browser.new_page(viewport={'width': 390, 'height': 900})
            local.goto((ROOT / 'framework/index.html').as_uri(), wait_until='load')
            assert local.locator('.curriculum-list > li').count() == 45
            assert local.evaluate('document.documentElement.scrollWidth <= innerWidth')
            browser.close()
        assert not errors, errors
        assert not failures, failures
        local_requests = [r for r in requests if any(f':{port}' in r['url'] for port in [19200, 9200, 9201, 8080])]
        framework_requests = [r for r in local_requests if '/framework/' in r['page']]
        assert not framework_requests, framework_requests
        files = ['framework/index.html', 'framework/f01.html', 'framework/assets/course.css', 'index.html',
                 'FRAMEWORK_PLAN.md', 'FRAMEWORK_CASES.md', 'FRAMEWORK_STANDARD.md']
        record = {
            'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'scope': 'curriculum planning and reading entry, no lesson rewrite or ES execution',
            'structure': '45 ordered lessons identical across plan/cases/directory; 8 stages; local links/fences checked',
            'http_prefix': '/es_web/', 'browser': 'Playwright Chromium', 'measurements': measurements,
            'interactions': ['theme toggles', 'all 8 stage anchors with headings below fixed topbar', 'home route', 'legacy notice', 'reduced motion', 'file preview'],
            'regression': 'home and legacy F01 page overflow at all 12 viewport/theme combinations; old diagram asset reference retained',
            'js_errors': errors, 'http_failures': failures, 'framework_business_requests': framework_requests,
            'existing_source_home_connection_probes': local_requests,
            'screenshots': screenshots, 'visual_review': 'pending human image inspection',
            'hashes': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files},
            'not_run': ['ES/Java/plugins/cluster/CDC', 'business demo shell', 'diagram generation'],
        }
        (HERE / 'http-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
        print('PASS: 45 lessons / 8 stages; 12 viewport-theme pairs; home/legacy regression; 12 screenshots pending visual review')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    run()
