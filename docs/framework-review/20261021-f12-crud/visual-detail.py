#!/usr/bin/env python3
"""Supplementary real screenshots after overview found viewport clipping of editor messages."""
import importlib.util,json,pathlib,traceback
from playwright.sync_api import sync_playwright
H=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('f12shell',H/'shell-review.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
s.record['scope']='F12 supplementary actual browser screenshots; no mocked API; editor and results regions explicitly captured'
try:
 s.lab.restore()
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  for width in [1440,390]:
   for theme in ['light','dark']:
    c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce');c.add_init_script(f"localStorage.setItem('travel-f12:theme','{theme}')")
    p=c.new_page();s.observe(p);p.goto(s.lab.APP+'/f12.html',wait_until='networkidle');s.shot(p,f'{width}-{theme}-opening');c.close()
  c=browser.new_context(viewport={'width':390,'height':1000},reduced_motion='reduce');p=c.new_page();s.observe(p);p.goto(s.lab.APP+'/f12.html',wait_until='networkidle')
  q=c.new_page();s.observe(q);q.goto(s.lab.APP+'/f12.html',wait_until='networkidle')
  s.action(p,'#read','/d-hz-garden');s.action(q,'#read','/d-hz-garden')
  s.search(p);p.locator('#price').fill('9000');s.action(p,'#save','/d-hz-garden');s.action(p,'#read','/d-hz-garden')
  s.shot(p,'390-get9000-editor','.editor');s.shot(p,'390-search4500-results','.results')
  q.locator('#state').select_option('closed');s.action(q,'#save','/d-hz-garden',409);s.shot(q,'390-conflict-editor','.editor')
  s.action(q,'#read','/d-hz-garden');q.locator('#state').select_option('closed');s.action(q,'#save','/d-hz-garden');s.action(q,'#refresh','/refresh')
  read=s.action(q,'#read','/d-hz-garden');s.require(read['document']['ticket_price_fen']==9000 and read['document']['status']=='closed','recovery keeps winner')
  s.shot(q,'390-reread-closed-editor','.editor')
  s.search(p);s.shot(p,'390-new-view-results','.results');s.action(p,'#close','/pages/close')
  c.close();browser.close()
 s.lab.restore();s.record['status']='passed'
except Exception:
 s.record['status']='failed';s.record['failure']=traceback.format_exc();raise
finally:
 s.record['es_author_operations']=s.lab.RECORD
 (H/'visual-detail.json').write_text(json.dumps(s.record,ensure_ascii=False,indent=2)+'\n')
