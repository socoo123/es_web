#!/usr/bin/env python3
"""Two actual Java calls to inspect readable first-query cards and average bars."""
import datetime,json,pathlib,importlib.util
from playwright.sync_api import sync_playwright
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('f22shell',HERE/'shell-review.py')
# Do not import shell-review (its main workflow executes); reuse read-only HTTP screenshot helper instead.
spec=importlib.util.spec_from_file_location('f22read',HERE/'review.py');read=importlib.util.module_from_spec(spec);spec.loader.exec_module(read)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'2 actual Java calls; first card and macro text visual supplement','api_calls':0,'screenshots':[],'rows':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=read.BROWSER)
 for width,theme,split in [(1440,'light','holdout'),(390,'dark','adjust')]:
  c=b.new_context(viewport={'width':width,'height':1000});c.add_init_script(f"localStorage.setItem('travel-f22:theme','{theme}')");p=c.new_page();p.goto('http://127.0.0.1:18081/f22.html',wait_until='networkidle')
  p.locator('[name=split]').select_option(split);p.locator('[name=strategy]').select_option('candidate')
  with p.expect_response(lambda r:r.url.endswith('/api/quality/evaluate')) as info:p.locator('#submit').click()
  r=info.value;read.require(r.status==200,'actual card query');out=r.json();record['api_calls']+=1
  p.wait_for_function("!document.getElementById('submit').disabled")
  read.require(json.loads(p.locator('#result-json').text_content())==out,'complete card DTO')
  record['rows'].append({'width':width,'theme':theme,'input':out['conditions'],'macro':out['macro'],'first_ids':out['queries'][0]['ids']})
  for slug,target in [('card','.card'),('macro','#macro')]:record['screenshots'].append(read.shot(p,f'card-{width}-{theme}-{split}-{slug}',target))
  c.close()
 b.close()
record['status']='passed';(HERE/'card-detail.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('2 actual Java card detail calls passed')
