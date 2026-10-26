#!/usr/bin/env python3
"""Run after push/build: verify exact GitHub commit and live Pages bytes/interactions.
Writes outside the worktree by default so final git cleanliness can be verified.
"""
import argparse,datetime,hashlib,importlib.util,json,pathlib,subprocess,urllib.request
from playwright.sync_api import sync_playwright
import sys
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('reading',HERE/'reading_helpers.py');reading=importlib.util.module_from_spec(spec);spec.loader.exec_module(reading)
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def api(path):return json.loads(subprocess.check_output(['gh','api',path],cwd=ROOT,text=True))
def sha(b):return hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--out',default='/tmp/es-f25-publication.json');a=p.parse_args();base='https://socoo123.github.io/es_web/'
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expected_commit':a.sha,'assets':[],'matrix':[],'js_errors':[],'request_failures':[],'business_requests':[],'f24_theme_loads':[],'http_failures':[]}
try:
 r['local_head']=git('rev-parse','HEAD');r['git_status_before']=git('status','--porcelain');require(r['local_head']==a.sha and not r['git_status_before'],'exact clean local commit')
 r['remote_head']=git('ls-remote','origin','refs/heads/main').split()[0];require(r['remote_head']==a.sha,'remote exact SHA')
 r['pages_build']=api('repos/socoo123/es_web/pages/builds/latest');require(r['pages_build']['commit']==a.sha and r['pages_build']['status']=='built' and not r['pages_build'].get('error',{}).get('message'),'exact Pages build')
 paths=['framework/f25.html','framework/f24.html','framework/index.html','framework/diagrams/f25/nights-light.svg','framework/diagrams/f25/nights-dark.svg','framework/diagrams/f25/verify-light.svg','framework/diagrams/f25/verify-dark.svg','framework/diagrams/f25/generation.json','framework/diagrams/f25/verify.d2','framework/assets/course.js','framework/assets/course.css','projects/travel-search/data/f25/stay-table.json','projects/travel-search/search/f25/two-nights.json','projects/travel-search/backend/src/main/java/dev/esweb/travel/StaySearchService.java']
 for name in paths:
  request=urllib.request.Request(base+name+'?audit='+a.sha,headers={'Cache-Control':'no-cache','User-Agent':'F25-pages-verification'})
  with urllib.request.urlopen(request,timeout=30) as response:body=response.read();status=response.status
  local=(ROOT/name).read_bytes();require(status==200 and body==local,'online byte match '+name);r['assets'].append({'path':name,'status':status,'sha256':sha(body),'local_sha256':sha(local),'bytes':len(body)})
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=reading.BROWSER);r['browser']={'engine':'Chromium','version':browser.version}
  for width in [1440,390,320]:
   for theme in ['light','dark']:
    c=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce',permissions=['clipboard-read','clipboard-write']);c.add_init_script(f"if(!localStorage.getItem('es-web:theme'))localStorage.setItem('es-web:theme','{theme}')")
    c.add_init_script('''window.__f25ImageChanges=[];new MutationObserver(events=>{for(const e of events){if(e.target.tagName==='IMG' && e.oldValue && e.oldValue!==e.target.getAttribute('src'))window.__f25ImageChanges.push({old:new URL(e.oldValue,location.href).href,current:e.target.src});}}).observe(document,{subtree:true,attributes:true,attributeFilter:['src'],attributeOldValue:true});''')
    group={'width':width,'initial_theme':theme}
    page=c.new_page();page.on('response',lambda response:r['http_failures'].append({'url':response.url,'status':response.status}) if response.status>=400 else None);page.on('pageerror',lambda e:r['js_errors'].append(str(e)));page.on('requestfailed',lambda req,g=group.copy():r['request_failures'].append({'group':g,'url':req.url,'failure':req.failure}))
    c.on('request',lambda req:r['business_requests'].append(req.url) if any(x in req.url for x in ['127.0.0.1','localhost:','/api/stay/inspect']) else None)
    page.goto(base+'framework/f25.html?audit='+a.sha,wait_until='networkidle');reading.diagrams(page,theme);layout=reading.measure(page);anchors=reading.anchors(page)
    for fold in page.locator('details').all():fold.locator('summary').click();require(fold.get_attribute('open') is not None,'fold opens');fold.locator('summary').click()
    page.locator('.theme-toggle').click();other='dark' if theme=='light' else 'light';reading.diagrams(page,other);page.reload(wait_until='networkidle');reading.diagrams(page,other)
    page.locator('.read-toggle').click();page.reload(wait_until='networkidle');require(page.locator('.read-toggle').evaluate("e=>e.classList.contains('is-on')"),'read persists')
    page.locator('.pager a[href="f24.html"]').click();page.wait_for_load_state('networkidle');require(page.locator('.pager a[href="f25.html"]').count()==1,'F24 next')
    f24_images=reading.diagrams(page,other)
    r['f24_theme_loads'].append({'group':group.copy(),'loaded_images':f24_images,'src_changes':page.evaluate('window.__f25ImageChanges')})
    page.locator('.pager a[href="f25.html"]').click();page.wait_for_load_state('networkidle');page.locator('.pager a[href="index.html"]').click();page.wait_for_load_state('networkidle');require(page.locator('[data-ch="f25"]').evaluate("e=>e.classList.contains('is-read')"),'directory read badge');page.locator('.curriculum-lesson-link[href="f25.html"]').click();page.wait_for_load_state('networkidle')
    require(page.locator('a[href="f26.html"]').count()==0,'F26 pending without broken link')
    r['matrix'].append({'width':width,'initial_theme':theme,'layout':layout,'anchors':len(anchors),'folds':page.locator('details').count(),'theme_reload_progress_navigation':'passed'})
    if width==390 and theme=='dark':
     copies=[]
     for selector in ['pre[data-source$="two-nights.json"]','pre[data-source$="two-nights-input.json"]','pre[data-source$="StaySearchService.java"]']:
      pre=page.locator(selector).first;pre.evaluate("e=>{let a=e.parentElement;while(a){if(a.tagName==='DETAILS')a.open=true;a=a.parentElement;}}");expected=pre.locator('code').text_content();pre.locator('xpath=preceding-sibling::div[1]').locator('.copy-code').click();page.wait_for_function('s=>navigator.clipboard.readText().then(v=>v===s)',arg=expected);copies.append({'selector':selector,'copied_exact':True})
     r['clipboard']=copies
     for link in page.locator('[data-expand-d2]').all():
      with page.expect_popup() as info:link.click()
      popup=info.value;popup.wait_for_load_state('load');require(popup.locator('svg').first.is_visible(),'online SVG popup');popup.close()
     r['diagram_popups']='both actual live SVGs opened';page.evaluate('scrollTo(0,0)');page.screenshot(path='/tmp/es-f25-pages-390-dark.png');r['screenshot']={'path':'/tmp/es-f25-pages-390-dark.png','sha256':sha(pathlib.Path('/tmp/es-f25-pages-390-dark.png').read_bytes())}
    c.close()
  browser.close()
 # Preserve every abort. A src replacement is accepted only with same-group
 # MutationObserver old->new evidence AND a successfully decoded final image.
 r['verified_theme_cancellations']=[];r['unexplained_request_failures']=[]
 for failure in r['request_failures']:
  proofs=[proof for proof in r['f24_theme_loads'] if proof['group']==failure['group']]
  match=next(({'failure':failure,'change':change,'loaded_replacement':image} for proof in proofs for change in proof['src_changes'] for image in proof['loaded_images']
   if failure['failure']=='net::ERR_ABORTED' and failure['url']==change['old']
   and change['current']==image['src'] and image['width']>0 and image['height']>0
   and failure['url'] in [base+'framework/diagrams/f24/'+slug+'-'+t+'.svg' for slug in ['same-entry','price-scope'] for t in ['light','dark']]),None)
  if match:r['verified_theme_cancellations'].append(match)
  else:r['unexplained_request_failures'].append(failure)
 require(not r['http_failures'] and not r['js_errors'] and not r['unexplained_request_failures'] and not r['business_requests'],'online JS/network/business isolation; each accepted abort requires actual replacement proof')
 r['git_status_after']=git('status','--porcelain');require(not r['git_status_after'],'final clean tree');r['remote_head_after']=git('ls-remote','origin','refs/heads/main').split()[0];require(r['remote_head_after']==a.sha,'remote unchanged');r['status']='passed'
finally:pathlib.Path(a.out).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('Exact commit/Pages build +14 byte-identical live assets +6 browser groups passed; clean tree:',a.sha)
