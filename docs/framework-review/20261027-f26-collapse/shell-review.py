#!/usr/bin/env python3
"""Real local shell -> Java -> isolated ES; no mocked responses."""
import datetime,hashlib,importlib.util,json,pathlib,subprocess,traceback
from playwright.sync_api import sync_playwright
import reading_helpers as h
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f26lab',P/'labs/f26/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
def require(ok,detail):
    if not ok:raise AssertionError(detail)
def shot(page,name,selector):
    p=HERE/'screenshots'/('shell-'+name+'.png');p.parent.mkdir(exist_ok=True)
    page.locator(selector).screenshot(path=str(p))
    return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),visual_review='pending')
def run():
    rec=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),calls=[],matrix=[],screenshots=[],js_errors=[],request_failures=[],browser_es_calls=[],http_errors=[])
    pid=subprocess.check_output(['lsof','-tiTCP:18081','-sTCP:LISTEN'],text=True).strip();rec['java_pid_before']=pid
    lab.LOG=HERE/'shell-es-operations.jsonl';require(not lab.LOG.exists(),'fresh ES receipt file')
    expected={'top-offers':[('h01','o01',100000),('h02','o05',120000)],'top-hotels':[('h01','o02',80000),('h02','o06',100000)],'all':[('h04','o09',60000),('h05','o10',60000),('h01','o02',80000),('h02','o06',100000)]}
    expected_counts={'top-offers':(2,2,2,2),'top-hotels':(5,2,5,2),'all':(10,6,7,4)}
    def submit(page,mode,status=200):
        page.select_option('#mode',mode);require(page.locator('#cards .hotel').count()==0 and page.locator('#result-json').text_content()=='尚无本轮结果','change clears all stale evidence')
        with page.expect_response(lambda r:r.url.endswith('/api/collapse/inspect')) as pending:page.locator('#submit').click()
        response=pending.value;body=response.json();require(response.status==status,body);page.wait_for_function('!document.querySelector("#submit").disabled')
        if status==200:
            actual=[(v['hotelId'],v['minimumOfferId'],v['minimumTotalMinor']) for v in body['hotels']];require(actual==expected[mode],'hotel IDs/minimum/total order')
            require((body['inspectedOfferCount'],body['inspectedHotelCount'],body['acceptedOfferCount'],body['displayedHotelCount'])==expected_counts[mode],'all count scopes')
            require(body['candidateOfferTotal']==10 and body['candidateHotelEstimate']==6,'candidate counts')
            require(body['esRequest']==lab.read(P/f'search/f26/{mode}.json'),'whole DSL exact')
            require(json.loads(page.locator('#result-json').text_content())==body and json.loads(page.locator('#dsl-json').text_content())==body['esRequest'],'actual observed JSON == HTTP response')
            cards=page.locator('#cards .hotel');require(cards.count()==len(actual),'cards')
            for i,(hotel,offer,total) in enumerate(actual):
                card=cards.nth(i);require(card.get_attribute('data-hotel-id')==hotel and offer in card.inner_text() and f'¥{total/100:.2f}' in card.inner_text(),'card amount and identity == Java response')
            require(page.locator('#decisions p').count()==body['inspectedOfferCount'],'every inspected offer visible')
        else:
            require(page.locator('#cards .hotel').count()==0 and page.locator('#decisions p').count()==0 and page.locator('#result-json').text_content()=='尚无本轮结果','failed request clears all previous cards and evidence')
            require(str(status) in page.locator('#status').inner_text() and body['code'] in page.locator('#status').inner_text(),'actual status/error displayed')
        layout=page.evaluate('({viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth})');require(layout['page']<=layout['viewport'] and layout['body']<=layout['viewport'],layout)
        call=dict(mode=mode,status=response.status,response=body,layout=layout);rec['calls'].append(call);return call
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=h.BROWSER);rec['browser']=dict(engine='Chromium',version=browser.version)
            for width in [1440,768,390,320]:
                for theme in ['light','dark']:
                    c=browser.new_context(viewport=dict(width=width,height=1000),reduced_motion='reduce');c.add_init_script(f"if(!localStorage.getItem('travel-f26-theme'))localStorage.setItem('travel-f26-theme','{theme}')")
                    page=c.new_page();page.on('pageerror',lambda e:rec['js_errors'].append(str(e)));page.on('requestfailed',lambda r:rec['request_failures'].append(dict(url=r.url,error=r.failure)))
                    page.on('request',lambda r:rec['browser_es_calls'].append(r.url) if any(s in r.url for s in [':19226',':9200',':9201']) else None)
                    page.on('response',lambda r:rec['http_errors'].append(dict(url=r.url,status=r.status)) if r.status>=400 else None)
                    page.goto('http://127.0.0.1:18081/f26.html',wait_until='networkidle');require(page.locator('html').get_attribute('data-theme')==theme,'actual shell theme')
                    for mode in ['top-offers','top-hotels','all']:
                        call=submit(page,mode);rec['matrix'].append(dict(width=width,theme=theme,mode=mode,layout=call['layout']))
                        if (width==1440 and theme=='light') or (width==320 and theme=='dark' and mode=='all'):
                            rec['screenshots'].append(shot(page,f'{width}-{theme}-{mode}', '.results'))
                    page.locator('#theme').click();other='dark' if theme=='light' else 'light';require(page.locator('html').get_attribute('data-theme')==other,'theme toggles');page.reload(wait_until='networkidle');require(page.locator('html').get_attribute('data-theme')==other,'theme persists')
                    c.close()
            c=browser.new_context(viewport=dict(width=390,height=1000));page=c.new_page()
            page.on('pageerror',lambda e:rec['js_errors'].append(str(e)))
            page.on('request',lambda r:rec['browser_es_calls'].append(r.url) if ':19226' in r.url else None)
            page.goto('http://127.0.0.1:18081/f26.html',wait_until='networkidle')
            page.locator('#mode').evaluate("e=>e.add(new Option('无效输入（验收注入）','invalid'))")
            submit(page,'invalid',400);rec['screenshots'].append(shot(page,'400','.results'));submit(page,'all')
            original=lab.read(P/'data/f26/summaries.json')[0];bad=dict(original);bad.pop('hotel_name');lab.put('o01',bad)
            try:submit(page,'all',502);rec['screenshots'].append(shot(page,'502-source','.results'))
            finally:lab.put('o01',original)
            submit(page,'all')
            lab.request('DELETE','/tut-f26-offers')
            try:submit(page,'all',502);rec['screenshots'].append(shot(page,'502-index','.results'))
            finally:lab.prepare()
            submit(page,'all')
            compose=['docker','compose','-f',str(P/'infra/f26/compose.yaml')]
            subprocess.run(compose+['stop','es'],check=True,capture_output=True)
            try:submit(page,'all',503);rec['screenshots'].append(shot(page,'503','.results'))
            finally:
                subprocess.run(compose+['up','-d'],check=True,capture_output=True)
                subprocess.run(['bash',str(P/'infra/f26/wait.sh')],check=True)
            submit(page,'all');c.close();browser.close()
        rec['java_pid_after']=subprocess.check_output(['lsof','-tiTCP:18081','-sTCP:LISTEN'],text=True).strip();require(pid==rec['java_pid_after'],'same Java PID through errors and recovery')
        require(not rec['js_errors'] and not rec['request_failures'] and not rec['browser_es_calls'],'no JS/network/direct ES calls')
        require(len(rec['calls'])==32,'24 matrix + 4 errors + 4 recoveries')
        rec['actual_java_calls']=len(rec['calls']);rec['es_http_operations']=lab.COUNT;rec['status']='passed'
    except Exception as e:rec['status']='failed';rec['error']=str(e);rec['traceback']=traceback.format_exc();raise
    finally:(HERE/'shell-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
    print('F26 actual shell',len(rec['calls']),'Java requests; ES operations',lab.COUNT)
if __name__=='__main__':run()
