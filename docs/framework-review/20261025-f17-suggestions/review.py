#!/usr/bin/env python3
"""F17 作者验收：真实 HTTP/离线阅读；ES 运行记录在工程 review/f17。"""
import copy
import datetime
import functools
import hashlib
import http.server
import json
import pathlib
import re
import threading
import traceback
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WIDTHS = [1920, 1440, 1024, 768, 390, 320]
THEMES = ["light", "dark"]


def require(value, detail):
    if not value:
        raise AssertionError(detail)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/es_web/"):
            self.send_error(404); return
        self.path = self.path[len("/es_web"):]
        super().do_GET()

    def log_message(self, *args):
        pass


def observe(page, record):
    page.on("pageerror", lambda error: record["js_errors"].append(str(error)))
    page.on("response", lambda response: record["http_failures"].append({"url": response.url, "status": response.status}) if response.status >= 400 else None)
    page.on("requestfailed", lambda request: record["request_failures"].append({"url": request.url, "failure": request.failure}))


def diagrams(page, theme):
    page.wait_for_function("""theme => [...document.querySelectorAll('[data-d2-light]')].every(img => {
      const expected = new URL(theme === 'dark' ? img.dataset.d2Dark : img.dataset.d2Light, location.href).href;
      return img.complete && img.naturalWidth > 0 && img.currentSrc === expected && img.closest('figure').querySelector('[data-expand-d2]').href === expected;
    })""", arg=theme)
    result = page.locator("[data-d2-light]").evaluate_all("images => images.map(i => ({src:i.currentSrc, width:i.naturalWidth, height:i.naturalHeight, alt:i.alt}))")
    require(len(result) == 2, result)
    return result


def measure(page, chapter=True):
    result = page.evaluate("""chapter => {
      const art = chapter ? document.querySelector('article.chapter') : document.querySelector('main.wrap');
      const rect = art.getBoundingClientRect();
      const blocks = chapter ? [...art.querySelectorAll(':scope > header, :scope > section, :scope > footer, .lesson > h2, .d2-figure, .d2-figure > figcaption, .lesson > pre.code-block, .lesson > .code-tools')].map(el => {
        const r=el.getBoundingClientRect(); return {tag:el.tagName,id:el.id,left:r.left,right:r.right};}) : [];
      const scrollables = [...art.querySelectorAll('table.ktable, .d2-view, pre.code-block')].map(el=>{
        const initial=el.scrollLeft; el.scrollLeft=el.scrollWidth; const moved=el.scrollLeft; el.scrollLeft=initial;
        return {tag:el.tagName,id:el.id,client:el.clientWidth,scroll:el.scrollWidth,overflow:getComputedStyle(el).overflowX,moved};});
      return {viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,
        theme:document.documentElement.dataset.theme,left:rect.left,right:rect.right,width:rect.width,blocks,scrollables};
    }""", chapter)
    require(result["page"] <= result["viewport"] and result["body"] <= result["viewport"], result)
    if chapter:
        require(abs(result["width"] - min(880, result["viewport"] - (28 if result["viewport"] <= 600 else 44))) <= 1, result)
        for block in result["blocks"]:
            require(abs(block["left"] - result["left"]) <= 1 and abs(block["right"] - result["right"]) <= 1, {"misaligned":block})
        for container in result["scrollables"]:
            if container["scroll"] > container["client"] + 2:
                require(container["overflow"] in ["auto", "scroll"] and container["moved"] > 0, container)
    return result


def anchors(page):
    page.emulate_media(reduced_motion="reduce")
    page.locator(".chapter-outline summary").click()
    links = page.locator('.chapter-outline a, .diagram-jumps a[href^="#"]')
    result = []
    for i in range(links.count()):
        href = links.nth(i).get_attribute("href")
        require(page.locator(href).count() == 1, href)
        links.nth(i).click()
        evidence = page.evaluate("""href=>({href,top:document.querySelector(href).getBoundingClientRect().top,bar:document.querySelector('.topbar').getBoundingClientRect().bottom})""", href)
        require(evidence["top"] >= evidence["bar"] - 1, evidence)
        result.append(evidence)
    page.locator(".chapter-outline summary").click()
    return result


def shot(page, name, target=None):
    path = HERE / "screenshots" / (name + ".png")
    if target:
        header = page.locator(".topbar")
        if header.count():
            header.evaluate("el=>el.style.visibility='hidden'")
        try:
            page.locator(target).first.screenshot(path=str(path), timeout=20000)
        finally:
            if header.count():
                header.evaluate("el=>el.style.visibility=''")
    else:
        page.screenshot(path=str(path), timeout=20000)
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "visual_review": "pending"}


def static_links():
    checked = []
    for name in ['framework/f17.html', 'framework/f16.html', 'framework/index.html', 'framework/diagrams/f17/README.md',
                 'projects/travel-search/README.md', 'projects/travel-search/labs/f17/README.md', 'projects/travel-search/review/f17/README.md',
                 'docs/framework-review/20261025-f17-suggestions/README.md']:
        path=ROOT/name
        contents=path.read_text()
        links=re.findall(r'(?:href|src|data-d2-light|data-d2-dark)="([^"]+)"',contents) if path.suffix=='.html' else re.findall(r'\]\(([^)]+)\)',contents)
        for link in links:
            parsed=urlsplit(link)
            if parsed.scheme or parsed.netloc: continue
            target=path.parent/unquote(parsed.path) if parsed.path else path
            require(target.exists(), {'file':name,'link':link})
            if parsed.fragment and target.suffix=='.html':
                require(f'id="{parsed.fragment}"' in target.read_text(), {'missing_anchor':link})
            checked.append({'file':name,'link':link})
    return checked


def run():
    record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F17 static tutorial reading; Java/ES and local shell recorded separately',
            'reasoning':{'requested':'xhigh','actual':'not configurable or verifiable in root session','content_review':'author self-review only; no separate agent; root effort unavailable'},
            'static_links':[],'matrix':[],'regression':[],'independent_diagrams':[],'screenshots':[],
            'js_errors':[],'http_failures':[],'request_failures':[],'business_requests':[]}
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/es_web/'
    (HERE/'screenshots').mkdir(exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            record['browser']={'engine':'Chromium','version':browser.version}
            for width in WIDTHS:
                print(f'HTTP reading width {width}',flush=True)
                for theme in THEMES:
                    context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce',permissions=['clipboard-read','clipboard-write'])
                    context.add_init_script(f"localStorage.setItem('es-web:theme','{theme}')")
                    def route_request(route):
                        url=urlsplit(route.request.url)
                        if url.hostname in {'localhost','127.0.0.1','::1'} and url.port in {9200,9201,19200,19214,19215,8080,18080}:
                            record['business_requests'].append(route.request.url);route.abort()
                        else: route.continue_()
                    context.route('**/*',route_request)
                    page=context.new_page();observe(page,record)
                    page.goto(base+'framework/f17.html',wait_until='networkidle')
                    images=diagrams(page,theme)
                    anchor_record=anchors(page)
                    folds=[]
                    for fold in page.locator('details').all():
                        fold.locator('summary').click()
                        require(fold.get_attribute('open') is not None,'fold opens')
                        expanded=measure(page)
                        folds.append({'summary':fold.locator('summary').inner_text(),'expanded_page_width':expanded['page'],'viewport':width})
                        fold.locator('summary').click()
                    require(page.locator('.drills details').count()==7, 'seven exercises')
                    image_sizes=page.locator('[data-d2-light]').evaluate_all('images=>images.map(i=>({width:i.getBoundingClientRect().width,parent:i.parentElement.clientWidth,min:getComputedStyle(i).minWidth}))')
                    require(all(i['width']<=i['parent'] for i in image_sizes),image_sizes)
                    code_blocks=page.locator('pre.code-block').count()
                    require(code_blocks==page.locator('.copy-code').count(),'copy controls')
                    record['matrix'].append({'width':width,'theme':theme,'layout':measure(page),'images':images,'image_sizes':image_sizes,'anchors':anchor_record,'folds':folds,'code_blocks':code_blocks})
                    if width in [1440,390]:
                        page.evaluate('window.scrollTo(0,0)')
                        record['screenshots'].append(shot(page,f'f17-{width}-{theme}-opening'))
                        for slug in ['choices','guard']:
                            record['screenshots'].append(shot(page,f'f17-{width}-{theme}-{slug}',f'#fig-{slug}'))
                        record['screenshots'].append(shot(page,f'f17-{width}-{theme}-near','pre[data-source="projects/travel-search/search/f17/completion.json"]'))
                        record['screenshots'].append(shot(page,f'f17-{width}-{theme}-java-query','pre[data-source="projects/travel-search/backend/src/main/java/dev/esweb/travel/SuggestSearchService.java"]'))
                    if width==320 and theme=='light':
                        record['screenshots'].append(shot(page,'f17-320-light-choices','#fig-choices'))
                    if width==390 and theme=='dark':
                        page.locator('.drills details').nth(3).locator('summary').click()
                        record['screenshots'].append(shot(page,'f17-390-dark-exercises','.drills'))
                        page.locator('.drills details').nth(3).locator('summary').click()
                    page.goto(base+'framework/index.html',wait_until='networkidle')
                    require(page.locator('.curriculum-lesson-link[href="f17.html"][data-ch="f17"]').count()==1,'F17 entry')
                    record['regression'].append({'page':'directory','width':width,'theme':theme,'layout':measure(page,False)})
                    page.goto(base+'framework/f16.html',wait_until='networkidle')
                    require(page.locator('.pager a[href="f17.html"]').count()==1,'F16 next')
                    record['regression'].append({'page':'F16','width':width,'theme':theme,'layout':measure(page)})
                    context.close()
            context=browser.new_context(viewport={'width':1440,'height':1000},permissions=['clipboard-read','clipboard-write'])
            page=context.new_page();observe(page,record)
            page.goto(base+'framework/f17.html',wait_until='networkidle')
            page.evaluate("localStorage.setItem('es-web:read',JSON.stringify({'f01':true,'f01-v2':true,'f02':true,'f03':true,'f04':true,'f05':true,'f06':true,'f07':true,'f08':true,'f09':true,'f10':true,'f11':true,'f12':true,'f16':true}));localStorage.setItem('es-web:theme','light')")
            page.reload(wait_until='networkidle')
            copies=[]
            for i in range(page.locator('.copy-code').count()):
                block=page.locator('pre.code-block code').nth(i)
                expected=block.text_content()
                enclosing=block.locator('xpath=ancestor::details[1]')
                if enclosing.count(): enclosing.locator('summary').click()
                page.locator('.copy-code').nth(i).click()
                page.wait_for_function('expected=>navigator.clipboard.readText().then(value=>value===expected)',arg=expected)
                require(page.evaluate('navigator.clipboard.readText()')==expected, {'clipboard_block':i})
                if enclosing.count(): enclosing.locator('summary').click()
                copies.append({'block':i,'label':page.locator('pre.code-block').nth(i).get_attribute('data-label'),'copied_exact':True})
            record['clipboard']=copies
            page.locator('.copy-code').first.focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
            require(page.locator('.copy-code').first.evaluate("el=>el===document.activeElement && getComputedStyle(el).outlineStyle!=='none'"),'visible keyboard focus')
            page.locator('.theme-toggle').click();diagrams(page,'dark')
            page.reload(wait_until='networkidle');diagrams(page,'dark')
            page.locator('.read-toggle').click();page.reload(wait_until='networkidle')
            require(page.locator('.read-toggle').evaluate("el=>el.classList.contains('is-on')"),'progress persists')
            page.locator('.pager a[href="index.html"]').click();page.wait_for_url(base+'framework/index.html')
            require(page.locator('[data-ch="f17"]').evaluate("el=>el.classList.contains('is-read')"),'directory badge')
            page.locator('.curriculum-lesson-link[href="f17.html"]').click();page.wait_for_url(base+'framework/f17.html')
            page.locator('.read-toggle').click()
            require(page.evaluate("JSON.parse(localStorage.getItem('es-web:read'))")=={'f01':True,'f01-v2':True,'f02':True,'f03':True,'f04':True,'f05':True,'f06':True,'f07':True,'f08':True,'f09':True,'f10':True,'f11':True,'f12':True,'f16':True},'other read keys remain')
            page.locator('.pager a[href="f16.html"]').click();page.wait_for_url(base+'framework/f16.html');page.wait_for_load_state('networkidle');diagrams(page,'dark')
            page.locator('.pager a[href="f17.html"]').click();page.wait_for_url(base+'framework/f17.html');page.wait_for_load_state('networkidle');diagrams(page,'dark')
            require(page.locator('a[href="f18.html"]').count()==0,'no nonexistent F18 link')
            for link in page.locator('[data-expand-d2]').all():
                with page.expect_popup() as info:link.click()
                popup=info.value;popup.wait_for_load_state('load')
                require('-dark.svg' in popup.url and popup.locator('svg').first.is_visible(),'actual diagram popup')
                popup.close()
            record['interactions']={'theme':'switch, reload, both images and expand links','keyboard':'copy focus outline after actual Tab',
                'progress':'mark, reload, badge, unmark; old f01/f01-v2/f02/f03/f04/f05/f06/f07/f08/f09/f10/f16 keys preserved','navigation':'directory ↔ F17, F16 ↔ F17; both diagram popups','next':'F18 pending with no broken link'}
            for width in [1440,1600,1920,2048]:
                page.set_viewport_size({'width':width,'height':1000})
                for theme in THEMES:
                    for slug in ['choices','guard']:
                        page.goto(base+f'framework/diagrams/f17/{slug}-{theme}.svg',wait_until='load')
                        require(page.locator('svg').first.is_visible(),'standalone svg loaded')
                        record['independent_diagrams'].append({'width':width,'theme':theme,'slug':slug,'loaded':True})
                        if width==1440:record['screenshots'].append(shot(page,f'f17-independent-{slug}-{theme}','svg'))
            offline_context=browser.new_context(viewport={'width':390,'height':1000})
            offline_page=offline_context.new_page()
            try:
                offline_page.goto((ROOT/'framework/f17.html').as_uri(),wait_until='load')
                theme=offline_page.evaluate('document.documentElement.dataset.theme');diagrams(offline_page,theme)
                offline_page.locator('.theme-toggle').click()
                theme2=offline_page.evaluate('document.documentElement.dataset.theme');diagrams(offline_page,theme2)
                require(theme!=theme2,'offline theme')
                record['offline']={'status':'passed','themes':[theme,theme2],'layout':measure(offline_page)}
            except Exception as error:
                if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(error):raise
                record['offline']={'status':'blocked','reason':str(error),'verified':False}
            finally:
                offline_context.close()
            page.goto(base+'framework/f17.html',wait_until='networkidle')
            page.emulate_media(reduced_motion='reduce')
            require(page.evaluate('getComputedStyle(document.documentElement).scrollBehavior')!='smooth','reduced motion')
            record['reduced_motion']='HTTP prefers-reduced-motion active, no smooth scroll; static diagrams; no player'
            context.close();browser.close()
        require(not record['js_errors'] and not record['http_failures'] and not record['request_failures'] and not record['business_requests'],{k:record[k] for k in ['js_errors','http_failures','request_failures','business_requests']})
        record['sha256']={str(p.relative_to(ROOT)):sha(p) for pattern in ['framework/f17.html','framework/diagrams/f17/*','framework/assets/course.css','framework/assets/course.js','framework/index.html','framework/f16.html'] for p in ROOT.glob(pattern) if p.is_file()}
        record['status']='passed'
    except Exception:
        record['status']='failed';record['failure']=traceback.format_exc();raise
    finally:
        server.shutdown();server.server_close()
        (HERE/'http-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    try:
        record['static_links']=static_links()
    except Exception:
        record['status']='failed';record['failure']=traceback.format_exc();raise
    finally:
        (HERE/'http-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(f"F17 HTTP passed: {len(record['matrix'])} lesson groups, {len(record['regression'])} regression groups, {len(record['clipboard'])} actual copies, {len(record['screenshots'])} PNGs pending visual review")

if __name__=='__main__':
    run()
