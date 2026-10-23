#!/usr/bin/env python3
"""Compare visible F15 table text with real source data and recorded ES IDs."""
import datetime
import functools
import hashlib
import http.server
import importlib.util
import json
import pathlib
import re
import threading
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('f15http', HERE / 'review.py')
review = importlib.util.module_from_spec(spec); spec.loader.exec_module(review)
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(review.Handler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
record = {'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'groups': [], 'screenshots': [], 'status': 'running'}
try:
    expected_docs = json.loads((ROOT / 'projects/travel-search/data/f15/attractions.json').read_text())
    run = json.loads((ROOT / 'projects/travel-search/review/f15/execution.json').read_text())
    summary = run['rounds'][0]['summary']
    expected_matrix = [[summary[phase]['queries'][qid]['hits'] for qid in ['brand', 'bay']]
                       for phase in ['baseline', 'file-only', 'loaded', 'mixed', 'rebuilt']]
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, theme in [(1440, 'dark'), (390, 'light')]:
            context = browser.new_context(viewport={'width': width, 'height': 1000}, reduced_motion='reduce')
            context.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')")
            page = context.new_page()
            page.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f15.html', wait_until='networkidle')
            rows = page.locator('.lesson table.ktable').first.locator('tbody tr').evaluate_all('rows=>rows.map(r=>[...r.cells].map(c=>c.textContent))')
            expected = [[d['attraction_id'], d['name'], f"{d['city_code']} / {d['status']} / {d['currency']} / {d['ticket_price_fen']}"] for d in expected_docs]
            assert rows == expected
            matrix = page.locator('#results-matrix tbody tr').evaluate_all('rows=>rows.map(r=>[...r.cells].slice(1).map(c=>c.textContent))')
            parsed = [[re.findall(r'(?:hz|nj)-[a-z]+', cell) for cell in row] for row in matrix]
            assert parsed == expected_matrix
            layout = review.measure(page)
            record['groups'].append({'width': width, 'theme': theme, 'data_rows': len(rows), 'full_ID_cells': 10, 'matrix': parsed, 'layout': layout})
            for slug, target in [('matrix', '#results-matrix'), ('samples', '.lesson table.ktable')]:
                path = HERE / 'screenshots' / f'f15-{width}-{theme}-final-{slug}.png'
                page.locator(target).first.screenshot(path=str(path))
                record['screenshots'].append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'visual_review': 'pending'})
            context.close()
        browser.close()
    record['status'] = 'passed'; record['lesson_sha256'] = hashlib.sha256((ROOT / 'framework/f15.html').read_bytes()).hexdigest()
finally:
    server.shutdown(); server.server_close()
    (HERE / 'final-text-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print('F15 final source rows and full-ID matrix passed')
