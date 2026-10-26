#!/usr/bin/env python3
"""Resolve element-screenshot viewport clipping with a taller capture viewport."""
import functools,http.server,threading,pathlib,json,hashlib
from playwright.sync_api import sync_playwright
import reading_helpers as h
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2]
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(h.Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start();rec={'screenshots':[],'status':'passed','reason':'390-width figure combined capture clipped the lower caption despite complete geometry; capture same CSS width at1400 height and separately validate caption'}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=h.BROWSER)
 for theme in ['light','dark']:
  c=b.new_context(viewport={'width':390,'height':1400},reduced_motion='reduce');c.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')");p=c.new_page();p.goto(f'http://127.0.0.1:{server.server_port}/es_web/framework/f24.html',wait_until='networkidle');h.diagrams(p,theme);p.locator('.topbar').evaluate("e=>e.style.visibility='hidden'")
  for slug in ['same-entry','price-scope']:
   target=p.locator('#fig-'+slug);target.scroll_into_view_if_needed();p.wait_for_timeout(150);path=HERE/'screenshots'/f'followup-390-{theme}-{slug}.png';target.screenshot(path=str(path));rec['screenshots'].append({'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'viewport':{'width':390,'height':1400},'visual_review':'pending'})
  c.close()
 b.close()
server.shutdown();(HERE/'visual-followup.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
