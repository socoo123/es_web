#!/usr/bin/env python3
"""Run after push/build: verify exact GitHub commit and live Pages bytes/interactions.
Writes outside the worktree by default so final git cleanliness can be verified.
"""
import argparse,datetime,hashlib,importlib.util,json,pathlib,subprocess,urllib.request
from playwright.sync_api import sync_playwright
import sys
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('reading',HERE/'review.py');reading=importlib.util.module_from_spec(spec);spec.loader.exec_module(reading)
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def api(path):return json.loads(subprocess.check_output(['gh','api',path],cwd=ROOT,text=True))
def sha(b):return hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--out',default='/tmp/es-f23-publication.json');a=p.parse_args();base='https://socoo123.github.io/es_web/'
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expected_commit':a.sha,'assets':[],'matrix':[],'js_errors':[],'request_failures':[],'business_requests':[]}
try:
 r['local_head']=git('rev-parse','HEAD');r['git_status_before']=git('status','--porcelain');require(r['local_head']==a.sha and not r['git_status_before'],'exact clean local commit')
 r['remote_head']=git('ls-remote','origin','refs/heads/main').split()[0];require(r['remote_head']==a.sha,'remote exact SHA')
 r['pages_build']=api('repos/socoo123/es_web/pages/builds/latest');require(r['pages_build']['commit']==a.sha and r['pages_build']['status']=='built' and not r['pages_build'].get('error',{}).get('message'),'exact Pages build')
 paths=['framework/f23.html','framework/f22.html','framework/index.html','framework/diagrams/f23/boundaries-light.svg','framework/diagrams/f23/boundaries-dark.svg','framework/diagrams/f23/updates-light.svg','framework/diagrams/f23/updates-dark.svg','framework/diagrams/f23/generation.json','framework/diagrams/f23/updates.d2','framework/assets/course.js','framework/assets/course.css','projects/travel-search/data/f23/catalog.json','projects/travel-search/search/f23/offers-flex.json','projects/travel-search/backend/src/main/java/dev/esweb/travel/ModelSearchService.java']
 for name in paths:
  request=urllib.request.Request(base+name+'?audit='+a.sha,headers={'Cache-Control':'no-cache','User-Agent':'F23-pages-verification'})
  with urllib.request.urlopen(request,timeout=30) as response:body=response.read();status=response.status
  local=(ROOT/name).read_bytes();require(status==200 and body==local,'online byte match '+name);r['assets'].append({'path':name,'status':status,'sha256':sha(body),'local_sha256':sha(local),'bytes':len(body)})
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=reading.BROWSER);r['browser']={'engine':'Chromium','version':browser.version}
  for width in [1440,390,320]:
   for theme in ['light','dark']:
    c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce',permissions=['clipboard-read','clipboard-write']);c.add_init_script(f"if(!localStorage.getItem('es-web:theme'))localStorage.setItem('es-web:theme','{theme}')")
    page=c.new_page();page.on('pageerror',lambda e:r['js_errors'].append(str(e)));page.on('requestfailed',lambda req:r['request_failures'].append({'url':req.url,'failure':req.failure}))
    c.on('request',lambda req:r['business_requests'].append(req.url) if any(x in req.url for x in ['127.0.0.1','localhost:','/api/model/inspect']) else None)
    page.goto(base+'framework/f23.html?audit='+a.sha,wait_until='networkidle');reading.diagrams(page,theme);layout=reading.measure(page);anchors=reading.anchors(page)
    for fold in page.locator('details').all():fold.locator('summary').click();require(fold.get_attribute('open') is not None,'fold opens');fold.locator('summary').click()
    page.locator('.theme-toggle').click();other='dark' if theme=='light' else 'light';reading.diagrams(page,other);page.reload(wait_until='networkidle');reading.diagrams(page,other)
    page.locator('.read-toggle').click();page.reload(wait_until='networkidle');require(page.locator('.read-toggle').evaluate("e=>e.classList.contains('is-on')"),'read persists')
    page.locator('.pager a[href="f22.html"]').click();page.wait_for_load_state('networkidle');require(page.locator('.pager a[href="f23.html"]').count()==1,'F22 next')
    page.locator('.pager a[href="f23.html"]').click();page.wait_for_load_state('networkidle');page.locator('.pager a[href="index.html"]').click();page.wait_for_load_state('networkidle');require(page.locator('[data-ch="f23"]').evaluate("e=>e.classList.contains('is-read')"),'directory read badge');page.locator('.curriculum-lesson-link[href="f23.html"]').click();page.wait_for_load_state('networkidle')
    require(page.locator('a[href="f24.html"]').count()==0,'F24 pending without broken link')
    r['matrix'].append({'width':width,'initial_theme':theme,'layout':layout,'anchors':len(anchors),'folds':page.locator('details').count(),'theme_reload_progress_navigation':'passed'})
    if width==390 and theme=='dark':
     copies=[]
     for selector in ['pre[data-source$="room-nested.json"]','pre[data-source$="offers-flex.json"]','pre[data-source$="ModelSearchService.java"]']:
      pre=page.locator(selector);expected=pre.locator('code').text_content();pre.locator('xpath=preceding-sibling::div[1]').locator('.copy-code').click();page.wait_for_function('s=>navigator.clipboard.readText().then(v=>v===s)',arg=expected);copies.append({'selector':selector,'copied_exact':True})
     r['clipboard']=copies
     for link in page.locator('[data-expand-d2]').all():
      with page.expect_popup() as info:link.click()
      popup=info.value;popup.wait_for_load_state('load');require(popup.locator('svg').first.is_visible(),'online SVG popup');popup.close()
     r['diagram_popups']='both actual live SVGs opened'
    c.close()
  browser.close()
 require(not r['js_errors'] and not r['request_failures'] and not r['business_requests'],'online JS/network/business isolation')
 r['git_status_after']=git('status','--porcelain');require(not r['git_status_after'],'final clean tree');r['remote_head_after']=git('ls-remote','origin','refs/heads/main').split()[0];require(r['remote_head_after']==a.sha,'remote unchanged');r['status']='passed'
finally:pathlib.Path(a.out).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('Exact commit/Pages build +14 byte-identical live assets +6 browser groups passed; clean tree:',a.sha)
