#!/usr/bin/env python3
"""Author evidence: reuse F07 through the real browser -> Java -> ES path."""
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(sys.argv[1]).resolve()
BROWSER = str(pathlib.Path.home() / 'Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell')
env = dict(os.environ, ES_URL='http://127.0.0.1:20945', ES_INDEX='tut-f45-attractions-read', ES_CA_FILE='', ES_API_KEY_FILE='', APP_PORT='18095')
stage = sys.argv[2]
record = {'stage': stage, 'js_errors': [], 'direct_es': [], 'observations': []}
with (OUT / ('observer-' + stage + '-java.log')).open('w') as log:
    process = subprocess.Popen(['java', '-Xms32m', '-Xmx160m', '-jar', 'backend/target/travel-search-0.7.0.jar'], cwd=ROOT / 'projects/travel-search', env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        for _ in range(120):
            try:
                urllib.request.urlopen('http://127.0.0.1:18095/', timeout=1).close()
                break
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                assert process.poll() is None, 'Java exited during startup'
                time.sleep(.25)
        else:
            raise TimeoutError('Observer startup')
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=BROWSER, headless=True)
            record['browser'] = browser.version
            for width, theme in [(1440, 'light'), (390, 'dark')]:
                ctx = browser.new_context(viewport={'width': width, 'height': 900})
                ctx.add_init_script("localStorage.setItem('travel-search:theme'," + json.dumps(theme) + ');')
                page = ctx.new_page()
                page.on('pageerror', lambda e: record['js_errors'].append(str(e)))
                page.on('request', lambda r: record['direct_es'].append(r.url) if ':20945' in r.url else None)
                page.goto('http://127.0.0.1:18095/', wait_until='networkidle')
                page.locator('[name=q]').fill('江岸')
                with page.expect_response(lambda r: r.url.endswith('/api/attractions/search') and r.request.method == 'POST') as reply:
                    page.locator('#submit').click()
                assert reply.value.status == 200
                value = reply.value.json()
                expected = [('n01', 6000), ('n02', 4000), ('n03', 2000), ('n06', 3500), ('n08', 2500)] if stage == 'initial' else [('n01', 4500), ('n03', 2000), ('n06', 3500), ('n08', 2500)]
                assert value['total'] == len(expected)
                assert [(i['id'], i['ticketPriceFen']) for i in value['items']] == expected
                request = urllib.request.Request('http://127.0.0.1:20945/tut-f45-attractions-read/_search?allow_partial_search_results=false',
                    data=json.dumps(value['esRequest'], ensure_ascii=False).encode(), headers={'Content-Type': 'application/json'}, method='POST')
                with urllib.request.urlopen(request, timeout=20) as response:
                    rest = json.load(response)
                assert rest['hits']['total']['value'] == len(expected)
                assert [(h['_id'], h['_source']['ticket_price_fen']) for h in rest['hits']['hits']] == expected
                page.wait_for_function('!document.querySelector("#submit").disabled')
                assert sorted(page.locator('#cards .card').evaluate_all('es=>es.map(e=>e.dataset.id)')) == [i[0] for i in expected]
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                page.locator('.results').scroll_into_view_if_needed()
                name = f'observer-{stage}-{width}-{theme}.png'
                page.screenshot(path=str(OUT / name))
                record['observations'].append({'width': width, 'theme': theme, 'java': value, 'rest': rest, 'screenshot': name})
                ctx.close()
            browser.close()
        assert not record['js_errors'] and not record['direct_es'], record
        record['passed'] = True
    finally:
        process.terminate()
        process.wait(timeout=15)
        record['java_pid'] = process.pid
        record['java_stopped'] = True
        (OUT / ('observer-' + stage + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print('F45 observer passed')
