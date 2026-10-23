#!/usr/bin/env python3
"""Actual F13 browser -> Java -> ES; no routes or mocked responses."""
import contextlib
import datetime
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import traceback
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROJECT = ROOT / 'projects/travel-search'
spec = importlib.util.spec_from_file_location('f13lab', PROJECT / 'labs/f13/lab.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
record = {'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'F13 actual browser/Java/ES; no mocked responses', 'matrix': [], 'operations': [],
          'screenshots': [], 'js_errors': [], 'direct_es_requests': [], 'status': 'running'}


def require(ok, info):
    if not ok:
        raise AssertionError(info)


def observe(page):
    page.on('pageerror', lambda e: record['js_errors'].append(str(e)))
    page.on('request', lambda r: record['direct_es_requests'].append(r.url)
            if ':19200/' in r.url or ':9200/' in r.url else None)
    def response(r):
        if r.url.endswith('/api/attractions/analysis-search'):
            record['operations'].append({'url': r.url, 'request': json.loads(r.request.post_data),
                                         'status': r.status, 'response': r.json()})
    page.on('response', response)


def search(page, expected=200):
    with page.expect_response(lambda r: r.url.endswith('/api/attractions/analysis-search'), timeout=20000) as info:
        page.locator('#submit').click()
    response = info.value
    require(response.status == expected, {'status': response.status, 'body': response.json()})
    page.wait_for_function("!document.getElementById('submit').disabled")
    result = response.json()
    if expected == 200:
        require(page.locator('.card').count() == len(result['items']), 'card count')
        require(page.locator('.card').evaluate_all('els=>els.map(e=>e.dataset.id)') == [c['id'] for c in result['items']], 'IDs/order')
        for i, card in enumerate(result['items']):
            actual = page.locator('.card').nth(i)
            require(actual.locator('h3').inner_text() == card['name'], card)
            require(actual.locator('.price').inner_text() == f"{card['ticketPriceFen']/100:.2f} 元", card)
            require(actual.locator('.tag').inner_text() == card['cityCode'] + ' · CNY / open', card)
        for id, key in [('index-tokens', 'indexTokens'), ('search-tokens', 'searchTokens')]:
            require(page.locator('#' + id + ' .token').count() == len(result[key]), key)
            for i, token in enumerate(result[key]):
                node = page.locator('#' + id + ' .token').nth(i)
                require(node.locator('strong').inner_text() == token['token'], token)
                require(node.locator('small').all_text_contents() == [f"position {token['position']}",
                    f"offset [{token['startOffset']}, {token['endOffset']})"], token)
        for id, key in [('input-json', 'conditions'), ('index-request-json', 'indexAnalysisRequest'),
                        ('search-request-json', 'searchAnalysisRequest'), ('dsl-json', 'esRequest')]:
            require(json.loads(page.locator('#' + id).text_content()) == result[key], key)
        require(json.loads(page.locator('#result-json').text_content()) == result, 'DTO')
        require(page.locator('#total').inner_text() == f"{result['total']} 份 · {result['relation']}", 'total')
        require(page.locator('#status').get_attribute('class') != 'error', 'empty success is not an error')
    else:
        require(page.locator('.card, .token').count() == 0, 'failed request clears old cards/tokens')
        require(page.locator('#status').get_attribute('class') == 'error', 'error visible')
        require(str(expected) in page.locator('#status').inner_text(), 'HTTP status visible')
        require(page.locator('#dsl-json').text_content() == '尚无本轮结果', 'failed request clears old DSL')
    return result


def shot(page, name, selector=None):
    path = HERE / 'screenshots' / ('shell-' + name + '.png')
    if selector:
        page.locator(selector).screenshot(path=str(path))
    else:
        page.screenshot(path=str(path))
    record['screenshots'].append({'path': str(path.relative_to(ROOT)),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'visual_review': 'pending'})


def layout(page):
    dimensions = page.evaluate('({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})')
    require(dimensions['page'] <= dimensions['viewport'] and dimensions['body'] <= dimensions['viewport'], dimensions)
    return dimensions


def run():
    with (HERE / 'shell-setup.jsonl').open('w') as output, contextlib.redirect_stdout(output):
        lab.cleanup(); lab.prepare()
    compose = ['docker', 'compose', '-f', str(PROJECT / 'infra/single-node/compose.yaml')]
    es_stopped = False
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            record['browser'] = {'engine': 'Chromium', 'version': browser.version}
            for width in [1920, 1440, 1024, 768, 390, 320]:
                for theme in ['light', 'dark']:
                    print('F13 shell', width, theme, flush=True)
                    context = browser.new_context(viewport={'width': width, 'height': 1000}, reduced_motion='reduce')
                    context.add_init_script(f"localStorage.setItem('travel-f13:theme','{theme}')")
                    page = context.new_page(); observe(page)
                    page.goto(lab.APP + '/f13.html', wait_until='networkidle')
                    require(page.locator('html').get_attribute('data-theme') == theme, 'theme')
                    zero = search(page); require(zero['total'] == 0, 'mismatch')
                    if width in [1440, 390]:
                        page.evaluate('scrollTo(0,0)'); shot(page, f'{width}-{theme}-opening')
                        shot(page, f'{width}-{theme}-mismatch', '.analysis')
                    page.locator('[name=mode]').select_option('aligned')
                    require(page.locator('.card, .token').count() == 0, 'input change clears')
                    aligned = search(page); require([c['id'] for c in aligned['items']] == lab.FOUR, 'AND4')
                    if width in [1440, 390]:
                        shot(page, f'{width}-{theme}-aligned', '.results')
                    page.locator('[name=mode]').select_option('phrase')
                    phrase = search(page); require([c['id'] for c in phrase['items']] == lab.FOUR[:3], 'phrase3')
                    record['matrix'].append({'width': width, 'theme': theme, 'layout': layout(page),
                        'case_counts': [0, 4, 3], 'comparison': 'all tokens/position/offset, cards IDs/order/names/city/fen-yuan, analysis requests/DSL/DTO exact'})
                    context.close()
            context = browser.new_context(viewport={'width': 390, 'height': 1000}, reduced_motion='reduce')
            page = context.new_page(); observe(page); page.goto(lab.APP + '/f13.html', wait_until='networkidle')
            page.locator('[name=q]').fill('PALACE-MUSEUM'); page.locator('[name=mode]').select_option('aligned')
            require(search(page)['total'] == 2, 'English aligned')
            page.locator('[name=mode]').select_option('case-sensitive')
            require(search(page)['total'] == 0, 'English case sensitive'); shot(page, '390-case-sensitive', '.analysis')
            page.locator('[name=q]').fill('故宫'); page.locator('[name=mode]').select_option('aligned')
            page.locator('[name=cityCode]').select_option('SY'); require(search(page)['items'][0]['id'] == 'sy-palace', 'SY')
            page.locator('[name=cityCode]').select_option('BJ'); page.locator('[name=budget]').fill('50')
            budget = search(page); require([c['id'] for c in budget['items']] == ['bj-punctuation', 'bj-separated'], 'budget changes do not improve analyzer')
            page.locator('[name=budget]').fill('100'); page.locator('[name=q]').fill('！！！')
            require(search(page)['searchTokens'] == [], 'empty token stream'); shot(page, '390-empty-tokens', '.analysis')
            page.locator('[name=q]').fill('   ')
            require(search(page, 400)['code'] == 'INVALID_ANALYSIS_INPUT', '400'); shot(page, '390-invalid', '.results')
            page.locator('[name=q]').fill('故宫'); search(page)
            with (HERE / 'shell-recovery.jsonl').open('w') as output, contextlib.redirect_stdout(output):
                lab.call('DELETE', '/' + lab.INDEX)
            require(search(page, 502)['code'] == 'SEARCH_BACKEND_REJECTED', 'missing index'); shot(page, '390-missing-index', '.results')
            with (HERE / 'shell-recovery.jsonl').open('a') as output, contextlib.redirect_stdout(output):
                lab.prepare()
            require(search(page)['total'] == 4, 'index rebuild same Java process')
            subprocess.run(compose + ['stop', 'es'], check=True, capture_output=True, timeout=45)
            es_stopped = True
            require(search(page, 503)['code'] == 'SEARCH_UNAVAILABLE', 'actual stopped ES'); shot(page, '390-unavailable', '.results')
            subprocess.run(compose + ['up', '-d', 'es'], check=True, capture_output=True, timeout=45)
            subprocess.run(['bash', str(PROJECT / 'infra/single-node/wait.sh')], check=True, capture_output=True, timeout=60)
            es_stopped = False
            require(search(page)['total'] == 4, 'ES restart same Java process'); shot(page, '390-recovered', '.results')
            page.locator('#theme').click(); theme = page.locator('html').get_attribute('data-theme')
            page.reload(wait_until='networkidle'); require(page.locator('html').get_attribute('data-theme') == theme, 'theme persists')
            page.locator('#theme').focus(); page.keyboard.press('Tab'); page.keyboard.press('Shift+Tab')
            require(page.locator('#theme').evaluate("e=>e===document.activeElement && getComputedStyle(e).outlineStyle!=='none'"), 'actual keyboard focus')
            record['interactions'] = {'input_change': 'stale data cleared', 'errors': [400, 502, 503],
                'recovery': 'actual named index rebuild and ES container stop/restart, same Java process',
                'theme': 'switch/reload persists', 'keyboard': 'real Tab/Shift+Tab visible focus'}
            context.close(); browser.close()
        require(not record['js_errors'] and not record['direct_es_requests'], record)
        record['status'] = 'passed'
    except Exception:
        record['status'] = 'failed'; record['failure'] = traceback.format_exc(); raise
    finally:
        if es_stopped:
            subprocess.run(compose + ['up', '-d', 'es'], check=True, capture_output=True, timeout=45)
            subprocess.run(['bash', str(PROJECT / 'infra/single-node/wait.sh')], check=True, capture_output=True, timeout=60)
        record['sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for pattern in ['projects/travel-search/backend/src/main/java/dev/esweb/travel/Analysis*.java',
                            'projects/travel-search/backend/src/main/resources/static/*f13*',
                            'projects/travel-search/backend/target/travel-search-0.7.0.jar']
            for p in ROOT.glob(pattern) if p.is_file()}
        (HERE / 'shell-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(f"F13 shell passed: {len(record['matrix'])} groups, {len(record['operations'])} actual API calls, {len(record['screenshots'])} PNGs awaiting visual inspection")


if __name__ == '__main__':
    run()
