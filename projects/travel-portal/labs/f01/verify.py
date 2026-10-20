"""Real F01 cases and HTTP lesson review. Run after npm ci/build and mvnw package.

Requires Python + playwright==1.63.0 + Chromium. Owns only the processes it starts.
Ports 8080/5173 must be free. Reports do not claim ES/DB/search/quote verification.
"""
from datetime import datetime
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from zoneinfo import ZoneInfo
import json
import os
import signal
import socket
import subprocess
import threading
import time

from playwright.sync_api import sync_playwright, expect

PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT.parents[1]
OUT = PROJECT / 'review/f01'
OUT.mkdir(parents=True, exist_ok=True)
JAR = PROJECT / 'backend/target/travel-portal-0.1.0.jar'
API = 'http://127.0.0.1:8080/api/health'
APP = 'http://127.0.0.1:5173/'
HEALTH = {'status': 'UP', 'service': 'travel-portal', 'stage': 'F01'}
report = {'reviewedAt': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
          'scope': 'F01 routes/contracts/real Java health only; no ES/DB/search/quote',
          'rounds': [], 'layout': [], 'screenshots': [], 'pageErrors': [],
          'visualReview': 'pending actual image inspection'}
processes, handles = [], []


def start(command, cwd, log):
    handle = (OUT / log).open('a')
    handles.append(handle)
    process = subprocess.Popen(command, cwd=cwd, stdout=handle, stderr=handle, start_new_session=True)
    processes.append(process)
    return process


def stop(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)


def wait_http(url, process=None):
    end = time.monotonic() + 45
    while time.monotonic() < end:
        if process and process.poll() is not None:
            raise RuntimeError(f'process exited: {url}; inspect review logs')
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return response.read()
        except Exception:
            time.sleep(0.2)
    raise RuntimeError('not ready: ' + url)


def java():
    process = start(['java', '-jar', str(JAR)], PROJECT / 'backend', 'java.log')
    assert json.loads(wait_http(API, process)) == HEALTH
    return process


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def translate_path(self, path):
        # Exercise the repository's GitHub Pages prefix.
        if path.startswith('/es_web/'):
            path = path[len('/es_web'):]
        return super().translate_path(path)


def screenshot(page, name, locator=None):
    target = locator or page
    target.screenshot(path=str(OUT / name))
    report['screenshots'].append(name)


server = None
try:
    assert JAR.exists(), 'run ./mvnw -B package first'
    for port in [8080, 5173]:
        with socket.socket() as probe:
            assert probe.connect_ex(('127.0.0.1', port)) != 0, f'port {port} already occupied; stop your own service first'
    backend = java()
    frontend = start(['npm', 'run', 'dev'], PROJECT / 'frontend', 'vite.log')
    wait_http(APP, frontend)
    assert json.loads(wait_http(APP + 'api/health')) == HEALTH
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    site = f'http://127.0.0.1:{server.server_port}/es_web/'

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, permissions=['clipboard-read', 'clipboard-write'])
        page = context.new_page()
        page.on('pageerror', lambda error: report['pageErrors'].append(str(error)))
        for round_number in [1, 2]:
            page.goto(APP)
            page.get_by_role('link', name='寻找景点').click()
            page.get_by_role('button', name='生成景点搜索请求').click()
            expected = {'keyword': '西湖', 'cityCode': '330100', 'maxPriceCent': 20000,
                        'sort': 'relevance', 'page': 1, 'pageSize': 10}
            assert json.loads(page.get_by_test_id('request-json').inner_text()) == expected
            page.get_by_label('门票预算上限').fill('200.05')
            page.get_by_label('目的地').select_option('110100')
            page.get_by_role('button', name='生成景点搜索请求').click()
            expected.update(maxPriceCent=20005, cityCode='110100')
            assert json.loads(page.get_by_test_id('request-json').inner_text()) == expected
            page.get_by_label('门票预算上限').fill('0')
            page.get_by_role('button', name='生成景点搜索请求').click()
            assert json.loads(page.get_by_test_id('request-json').inner_text())['maxPriceCent'] == 0
            page.get_by_label('门票预算上限').fill('-1')
            assert not page.get_by_label('门票预算上限').evaluate('e => e.checkValidity()')

            page.goto(APP)
            page.get_by_role('link', name='安排住宿').click()
            page.get_by_label('目的地').select_option('110100')
            page.get_by_role('button', name='查看房型请求').click()
            expect(page.get_by_role('heading', level=1)).to_have_text('2 晚 · 2 人 · 1 间房')
            stay = {'cityCode': '110100', 'checkIn': '2027-05-01', 'checkOut': '2027-05-03', 'guests': 2, 'rooms': 1}
            assert json.loads(page.get_by_test_id('request-json').inner_text()) == stay
            assert 'checkIn=2027-05-01' in page.url and 'rooms=1' in page.url
            page.reload()
            assert json.loads(page.get_by_test_id('request-json').inner_text()) == stay
            if round_number == 1:
                screenshot(page, 'project-rooms-1440.png')
            page.get_by_role('link', name='修改入住条件').click()
            expect(page.get_by_label('目的地')).to_have_value('110100')
            expect(page.get_by_label('入住日期')).to_have_value('2027-05-01')
            expect(page.get_by_label('入住人数')).to_have_value('2')
            page.get_by_label('离店日期').fill('2027-05-01')
            page.get_by_role('button', name='查看房型请求').click()
            expect(page.get_by_role('alert')).to_contain_text('离店日必须晚于入住日')
            for route in ['#/rooms', '#/rooms?cityCode=330100&checkIn=2027-02-30&checkOut=2027-03-03&guests=2&rooms=1',
                          '#/rooms?cityCode=330100&checkIn=2027-05-01&checkOut=2027-05-03&guests=2.5&rooms=1']:
                page.goto(APP + route)
                expect(page.get_by_role('alert')).to_be_visible()
                expect(page.get_by_test_id('request-json')).to_have_count(0)

            page.goto(APP)
            page.get_by_role('button', name='检查 Java 连接').click()
            expect(page.get_by_role('status')).to_contain_text('Java 已连接')
            stop(backend)
            page.get_by_role('button', name='检查 Java 连接').click()
            expect(page.get_by_role('status')).to_contain_text('连接失败')
            if round_number == 1:
                screenshot(page, 'project-health-failure.png')
            backend = java()
            page.get_by_role('button', name='重试连接').click()
            expect(page.get_by_role('status')).to_contain_text('Java 已连接')
            report['rounds'].append({'round': round_number, 'f01-c01': 'pass', 'f01-c02': 'pass', 'f01-c03': 'pass',
                                    'directJavaResponse': json.loads(wait_http(API)), 'proxyResponse': json.loads(wait_http(APP + 'api/health'))})

        lesson = site + 'framework/f01.html'
        for theme in ['light', 'dark']:
            for width in [1920, 1440, 1024, 768, 390, 320]:
                page.set_viewport_size({'width': width, 'height': 1000})
                page.goto(lesson)
                page.evaluate('(t) => localStorage.setItem("es-web:theme",t)', theme)
                page.reload()
                page.locator('[data-d2-light]').evaluate('e => e.decode()')
                result = page.evaluate('''() => {
                  const article=document.querySelector('article'), box=article.getBoundingClientRect();
                  const sections=[...article.querySelectorAll(':scope>section,:scope>header,:scope>footer')].map(e=>e.getBoundingClientRect());
                  return {viewport:innerWidth,pageWidth:document.documentElement.scrollWidth,column:box.width,
                    aligned:sections.every(s=>Math.abs(s.x-box.x)<1 && Math.abs(s.width-box.width)<1),
                    codeBlocks:document.querySelectorAll('pre.code-block').length};
                }''')
                assert result['pageWidth'] <= width and result['column'] <= 880.01 and result['aligned'], result
                assert page.locator('[data-d2-light]').get_attribute('src').endswith(theme + '.svg')
                assert page.locator('[data-expand-d2]').get_attribute('href').endswith(theme + '.svg')
                report['layout'].append({'theme': theme, **result})
                if width in [1440, 390]:
                    screenshot(page, f'lesson-{width}-{theme}.png')
                    screenshot(page, f'diagram-{width}-{theme}.png', page.locator('#fig-f01-health'))
                    page.locator('#attractions').scroll_into_view_if_needed()
                    screenshot(page, f'code-{width}-{theme}.png')
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.goto(site + f'framework/diagrams/f01/health-path-{theme}.svg')
            page.evaluate('document.fonts.ready')
            assert page.evaluate('''() => {const s=document.querySelector('svg'),v=s.viewBox.baseVal;
              return [...s.querySelectorAll('text')].every(e=>{const b=e.getBBox();return b.x>=0 && b.y>=0 && b.x+b.width<=v.width+1 && b.y+b.height<=v.height+1})}''')

        page.goto(lesson)
        page.get_by_role('button', name='复制代码', exact=True).first.click()
        assert page.evaluate('navigator.clipboard.readText()') == page.locator('pre.code-block code').first.inner_text()
        page.get_by_role('button', name='标记本课已读').click()
        assert page.evaluate('JSON.parse(localStorage.getItem("es-web:read")).f01')
        page.goto(site + 'framework/index.html')
        expect(page.locator('.progress-text')).to_have_text('已读 1 / 1 课')
        page.goto(site)
        # Source statistics count only chNN cards, even with framework entry links.
        expect(page.locator('.progress-text')).to_have_text('已读 0 / 30 课')
        page.goto(lesson)
        page.get_by_role('button', name='深色', exact=False).click() if page.locator('html').get_attribute('data-theme') == 'light' else page.get_by_role('button', name='浅色', exact=False).click()
        assert page.locator('[data-d2-light]').get_attribute('src').endswith(page.locator('html').get_attribute('data-theme') + '.svg')
        with page.expect_popup() as opened:
            page.locator('[data-expand-d2]').click()
        popup = opened.value
        popup.wait_for_load_state()
        assert popup.url.endswith('.svg')
        popup.close()
        context2 = browser.new_context(reduced_motion='reduce')
        reduced = context2.new_page()
        reduced.goto(lesson)
        assert reduced.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
        assert reduced.locator('html').evaluate('e=>getComputedStyle(e).scrollBehavior') != 'smooth'
        reduced.goto((ROOT / 'framework/f01.html').as_uri())
        expect(reduced.locator('h1')).to_have_text('先把旅游门户跑起来')
        expect(reduced.locator('[data-d2-light]')).to_be_visible()
        context2.close()

        for width in [1440, 390, 320]:
            page.set_viewport_size({'width': width, 'height': 1000})
            page.goto(site + 'framework/labs/travel-portal/index.html')
            expect(page.get_by_text('在线静态预览', exact=True)).to_be_visible()
            expect(page.get_by_role('button', name='检查 Java 连接')).to_have_count(0)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            if width != 320:
                screenshot(page, f'preview-{width}-light.png')
                page.get_by_role('button', name='深色', exact=True).click()
                screenshot(page, f'preview-{width}-dark.png')
        assert not report['pageErrors'], report['pageErrors']
        report['interaction'] = {'copy': 'pass', 'themeAndExpand': 'pass', 'readProgress': 'pass',
                                 'prefix': '/es_web/', 'fileLesson': 'pass', 'reducedMotion': 'pass', 'preview': 'pass'}
        browser.close()
    paths = [ROOT / 'framework/f01.html', *sorted((PROJECT / 'frontend/src').glob('*')),
             PROJECT / 'frontend/package-lock.json', PROJECT / 'backend/pom.xml',
             *sorted((ROOT / 'framework/diagrams/f01').glob('*.d2')),
             *sorted((ROOT / 'framework/diagrams/f01').glob('*.svg'))]
    report['sha256'] = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths}
    report['result'] = 'pass'
finally:
    for process in reversed(processes):
        stop(process)
    for handle in handles:
        handle.close()
    if server:
        server.shutdown()
    (OUT / 'api-browser.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('F01: two real case rounds, Java restart recovery, lesson/preview HTTP checks passed')
