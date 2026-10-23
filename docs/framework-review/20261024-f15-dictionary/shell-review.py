#!/usr/bin/env python3
"""Actual F15 browser -> Java -> ES. No routes/mocks and no browser dictionary mutation."""
import datetime
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import time
import traceback
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROJECT = ROOT / 'projects/travel-search'
spec = importlib.util.spec_from_file_location('f15lab', PROJECT / 'labs/f15/lab.py')
lab = importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
record = {'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'Actual final-jar F15 shell; no mocked responses', 'matrix': [], 'operations': [],
          'screenshots': [], 'js_errors': [], 'direct_es_requests': [], 'transitions': [], 'status': 'running'}

def require(ok, detail):
    if not ok: raise AssertionError(detail)

def observe(page):
    page.on('pageerror', lambda error: record['js_errors'].append(str(error)))
    page.on('request', lambda request: record['direct_es_requests'].append(request.url)
            if any(':' + str(port) + '/' in request.url for port in [9200, 9201, 19200, 19214, 19215]) else None)
    def response(r):
        if r.url.endswith('/api/attractions/dictionary-search'):
            record['operations'].append({'url': r.url, 'request': json.loads(r.request.post_data), 'status': r.status, 'response': r.json()})
    page.on('response', response)

def layout(page):
    actual = page.evaluate('({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})')
    require(actual['page'] <= actual['viewport'] and actual['body'] <= actual['viewport'], actual)
    return actual

def fill(page, q='星澜湾', city='NJ', view='original', budget='100'):
    page.locator('[name=q]').fill(q)
    page.locator('[name=cityCode]').select_option(city)
    page.locator('[name=view]').select_option(view)
    page.locator('[name=budget]').fill(budget)
    require(page.locator('.card, .token').count() == 0, 'condition change clears cards/tokens')
    require(page.locator('#dsl-json').text_content() == '尚无本轮结果', 'condition change clears DSL')

def search(page, expected=200, wanted=None):
    with page.expect_response(lambda r: r.url.endswith('/api/attractions/dictionary-search'), timeout=20000) as info:
        page.locator('#submit').click()
    response = info.value
    result = response.json()
    require(response.status == expected, {'status': response.status, 'response': result})
    page.wait_for_function("!document.getElementById('submit').disabled")
    if expected == 200:
        require(page.locator('.card').evaluate_all('els=>els.map(e=>e.dataset.id)') == [i['id'] for i in result['items']], 'IDs/order')
        if wanted is not None: require([i['id'] for i in result['items']] == wanted, result)
        for i, item in enumerate(result['items']):
            card = page.locator('.card').nth(i)
            require(card.locator('h3').inner_text() == item['name'], item)
            require(card.locator('.tag').inner_text() == item['cityCode'] + ' · CNY / open', item)
            require(card.locator('.price').inner_text() == f"{item['ticketPriceFen']/100:.2f} 元", item)
        for id, key in [('query-tokens', 'queryTokens'), ('stored-tokens', 'storedTokens')]:
            require(page.locator('#' + id + ' .token').count() == len(result[key]), key)
            for i, token in enumerate(result[key]):
                node = page.locator('#' + id + ' .token').nth(i)
                require(node.locator('strong').inner_text() == token['token'], token)
                require(node.locator('small').all_text_contents() == [f"position {token['position']}", f"offset [{token['startOffset']}, {token['endOffset']})"], token)
        for id, key in [('input-json', 'conditions'), ('query-request-json', 'queryAnalysisRequest'), ('stored-request-json', 'storedVectorRequest'),
                        ('vectors-json', 'storedVectors'), ('dsl-json', 'esRequest'), ('result-json', None)]:
            require(json.loads(page.locator('#' + id).text_content()) == (result[key] if key else result), key or 'DTO')
        require(page.locator('#total').inner_text() == f"{result['total']} 份 · {result['relation']}", 'total')
        require(page.locator('#status').get_attribute('class') != 'error', 'empty success is not error')
    else:
        require(page.locator('.card, .token').count() == 0, 'failed search clears result')
        require(page.locator('#status').get_attribute('class') == 'error' and str(expected) in page.locator('#status').inner_text(), 'visible HTTP error')
        for id in ['input-json', 'query-request-json', 'stored-request-json', 'vectors-json', 'dsl-json', 'result-json']:
            require(page.locator('#' + id).text_content() == '尚无本轮结果', 'failed search clears ' + id)
    return result

def shot(page, name, target=None):
    path = HERE / 'screenshots' / (name + '.png')
    (page.locator(target) if target else page).screenshot(path=str(path))
    record['screenshots'].append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'visual_review': 'pending'})

def command(args):
    result = subprocess.run(args, cwd=PROJECT, capture_output=True, text=True)
    record['transitions'].append({'command': args, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    require(result.returncode == 0, args)

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(); record['browser'] = browser.version
        for width in [1920, 1440, 1024, 768, 390, 320]:
            print('F15 shell width', width, flush=True)
            for theme in ['light', 'dark']:
                context = browser.new_context(viewport={'width': width, 'height': 1000}, reduced_motion='reduce')
                context.add_init_script(f"localStorage.setItem('travel-f15:theme','{theme}')")
                page = context.new_page(); observe(page)
                page.goto('http://127.0.0.1:18080/f15.html', wait_until='networkidle')
                require(page.locator('h1').inner_text() == '新词进入词典，\n搜索就修好了吗？', 'F15 heading')
                if (width, theme) in [(1440, 'light'), (390, 'dark')]: shot(page, f'shell-{width}-{theme}-opening')
                fill(page); original = search(page, wanted=['nj-new'])
                require([t['token'] for t in original['storedTokens']] == ['星', '澜', '湾', '观景台'], 'old stored terms')
                require([t['token'] for t in original['queryTokens']] == ['星澜湾'], 'new query term')
                if width in [1440, 390]: shot(page, f'shell-{width}-{theme}-original', '.analysis')
                fill(page, view='rebuilt'); rebuilt = search(page, wanted=['nj-bay', 'nj-boundary', 'nj-new'])
                require([t['token'] for t in rebuilt['storedTokens']] == ['星澜湾', '观景台'], 'rebuilt stored terms')
                if width in [1440, 390]:
                    shot(page, f'shell-{width}-{theme}-rebuilt', '.analysis')
                    shot(page, f'shell-{width}-{theme}-results', '.results')
                fill(page, q='云栖里', city='HZ'); search(page, wanted=['hz-new'])
                fill(page, q='云栖里', city='HZ', view='rebuilt'); search(page, wanted=['hz-brand', 'hz-new'])
                if (width, theme) == (390, 'light'): shot(page, 'shell-390-brand-results', '.results')
                fill(page, view='rebuilt', budget='0'); search(page, wanted=['nj-bay', 'nj-new'])
                fill(page, q='！！！', view='rebuilt'); empty = search(page, wanted=[])
                require(not empty['queryTokens'], 'empty stream')
                record['matrix'].append({'width': width, 'theme': theme, 'layout': layout(page), 'scenarios': ['original bay', 'rebuilt bay', 'original brand', 'rebuilt brand', 'zero budget bay', 'empty stream']})
                # Reload/theme control uses the shell-specific preference without affecting course progress.
                page.locator('#theme').click(); switched = page.evaluate('document.documentElement.dataset.theme')
                context.clear_cookies(); page.reload(wait_until='networkidle')
                # Init script intentionally sets requested theme on reload; click and verify immediate state.
                require(switched != theme, 'actual shell theme switch')
                context.close()
        context = browser.new_context(viewport={'width': 390, 'height': 1000}, reduced_motion='reduce')
        page = context.new_page(); observe(page)
        page.goto('http://127.0.0.1:18080/f15.html', wait_until='networkidle')
        fill(page, view='rebuilt'); search(page, wanted=['nj-bay', 'nj-boundary', 'nj-new'])
        fill(page, q='   ', view='rebuilt'); search(page, 400); shot(page, 'shell-390-invalid', '.results')
        fill(page, view='rebuilt')
        lab.call('DELETE', '/' + lab.NEW)
        search(page, 502); shot(page, 'shell-390-missing-index', '.results')
        lab.rebuild()
        search(page, wanted=['nj-bay', 'nj-boundary', 'nj-new'])
        command(['docker', 'compose', '-f', 'infra/f15/compose.yaml', 'stop', 'es'])
        search(page, 503); shot(page, 'shell-390-unavailable', '.results')
        command(['docker', 'compose', '-f', 'infra/f15/compose.yaml', 'start', 'es'])
        command(['bash', 'infra/f15/wait.sh'])
        # Every actual recovery retry is recorded as its actual response.
        for attempt in range(6):
            with page.expect_response(lambda r: r.url.endswith('/api/attractions/dictionary-search')) as info:
                page.locator('#submit').click()
            response = info.value; page.wait_for_function("!document.getElementById('submit').disabled")
            require(response.status in [200, 503], 'recovery status')
            if response.status == 200: break
            time.sleep(0.5)
        else: raise AssertionError('same Java process did not recover')
        search(page, wanted=['nj-bay', 'nj-boundary', 'nj-new']); shot(page, 'shell-390-recovered', '.results')
        layout(page)
        page.locator('#theme').click(); theme = page.evaluate('document.documentElement.dataset.theme')
        page.reload(wait_until='networkidle')
        require(page.evaluate('document.documentElement.dataset.theme') == theme, 'shell theme persists without init override')
        context.close(); browser.close()
    require(not record['js_errors'] and not record['direct_es_requests'], 'no JS errors or browser→ES calls')
    record['status'] = 'passed'
    record['same_java_process_recovery'] = True
except Exception:
    record['status'] = 'failed'; record['failure'] = traceback.format_exc(); raise
finally:
    (HERE / 'shell-recovery.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in lab.CALLS))
    record['sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (PROJECT / 'backend/src/main/resources/static').glob('*f15*')}
    (HERE / 'shell-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print('Actual F15 shell passed', len(record['matrix']), 'groups', len(record['operations']), 'API calls')
