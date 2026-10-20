#!/usr/bin/env python3
"""Real local shell acceptance, separate from static Pages reading and API rounds."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import verify as api

HERE=pathlib.Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
ROOT=HERE.parents[3]
OUT=ROOT/'docs/framework-review/20261020-f07-java'
RECORD={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Real local Boot shell → Java → ES; not Pages',
        'matrix':[],'requests':[],'js_errors':[],'screenshots':[],'direct_es_browser_requests':[]}

def require(value,detail):
    if not value:raise AssertionError(detail)

def shot(page,name):
    path=OUT/'screenshots'/f'shell-{name}.png';path.parent.mkdir(exist_ok=True,parents=True)
    page.screenshot(path=str(path),full_page=True)
    RECORD['screenshots'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visual_review':'pending'})

def submit(page,expected):
    with page.expect_response(lambda r:r.url.endswith('/api/attractions/search')) as info:
        page.locator('#submit').click()
    response=info.value
    result=response.json()
    page.wait_for_function('!document.querySelector("#submit").disabled')
    RECORD['requests'].append({'url':response.url,'status':response.status,'input':response.request.post_data_json,'response':result})
    require(response.status==200,result)
    require(page.locator('.card').evaluate_all('els=>els.map(e=>e.dataset.id)')==expected,result)
    require([x['id'] for x in result['items']]==expected,result)
    require(result['total']==len(expected) and result['totalRelation']=='eq',result)
    require(json.loads(page.locator('#dsl-json').text_content())==result['esRequest'],'actual DSL observation')
    require(json.loads(page.locator('#input-json').text_content())==result['conditions'],'input/conditions match')
    require(json.loads(page.locator('#result-json').text_content())==result,'response observation')
    for i,item in enumerate(result['items']):
        require(page.locator('.card .price').nth(i).inner_text().startswith('¥'+format(item['ticketPriceFen']/100,'.2f')),item)
    return result

def main():
    api.command(api.COMPOSE+['up','-d','es']);api.wait(api.ES+'/')
    api.request(api.ES,'/'+api.INDEX,expected=404,label='shell refuses existing index')
    api.command(['bash','labs/f07/01-prepare.sh'])
    process=None
    try:
        with (HERE/'shell-java.log').open('w') as log:
            env=dict(os.environ,ES_URL=api.ES,ES_INDEX=api.INDEX,APP_PORT='18080')
            process=subprocess.Popen([str(pathlib.Path(os.environ['JAVA_HOME'])/'bin/java'),'-jar','backend/target/travel-search-0.7.0.jar'],
                cwd=PROJECT,env=env,stdout=log,stderr=subprocess.STDOUT)
            api.wait(api.APP+'/api/health')
            with sync_playwright() as pw:
                browser=pw.chromium.launch()
                RECORD['browser']={'engine':'Chromium','version':browser.version}
                for width in [1920,1440,1024,768,390,320]:
                    for theme in ['light','dark']:
                        context=browser.new_context(viewport={'width':width,'height':1000},reduced_motion='reduce')
                        context.add_init_script(f"if(!localStorage.getItem('travel-search:theme'))localStorage.setItem('travel-search:theme','{theme}')")
                        page=context.new_page();page.on('pageerror',lambda e:RECORD['js_errors'].append(str(e)))
                        page.on('request',lambda r:RECORD['direct_es_browser_requests'].append(r.url) if urlsplit(r.url).port in [19200,9200,9201] else None)
                        page.goto(api.APP+'/',wait_until='networkidle')
                        require(page.locator('.card').count()==0,'no fabricated initial cards')
                        first=submit(page,['a-hz-boundary','a-hz-tea','a-hz-xihu'])
                        page.locator('.observe summary').click()
                        require(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'no shell page overflow')
                        if width in [1440,390]:shot(page,f'{width}-{theme}-results')
                        page.locator('[name=budget]').fill('80')
                        second=submit(page,['a-hz-tea','a-hz-xihu'])
                        require(second['conditions']['maxPriceFen']==8000,'yuan/fen conversion')
                        page.locator('[name=budget]').fill('200');page.locator('[name=q]').fill('火星')
                        submit(page,[])
                        require('找到 0' in page.locator('#status').inner_text(),'empty is normal')
                        if width==390 and theme=='light':shot(page,'390-light-empty')
                        page.locator('[name=q]').fill('西湖');page.locator('[name=radiusKm]').fill('1')
                        submit(page,['a-hz-boundary','a-hz-xihu'])
                        page.locator('[name=radiusKm]').fill('3');submit(page,['a-hz-boundary','a-hz-tea','a-hz-xihu'])
                        page.locator('#submit').focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab')
                        require(page.locator('#submit').evaluate("e=>e===document.activeElement&&getComputedStyle(e).outlineStyle!=='none'"),'real keyboard focus')
                        page.locator('#theme').click();page.reload(wait_until='networkidle')
                        require(page.locator('html').get_attribute('data-theme')!=theme,'theme persists')
                        RECORD['matrix'].append({'width':width,'theme':theme,'inputs':['200 yuan','80 yuan','empty','1km','restored'],
                            'no_page_overflow':True,'actual_network':True,'IDs_prices_DSL_DTO':'passed','keyboard_theme_reload':'passed'})
                        context.close()
                context=browser.new_context(viewport={'width':390,'height':1000},reduced_motion='reduce')
                page=context.new_page();page.goto(api.APP+'/',wait_until='networkidle')
                submit(page,['a-hz-boundary','a-hz-tea','a-hz-xihu'])
                api.command(api.COMPOSE+['stop','es'])
                try:
                    with page.expect_response(lambda r:r.url.endswith('/api/attractions/search')) as info:page.locator('#submit').click()
                    response=info.value;result=response.json()
                    page.wait_for_function('!document.querySelector("#submit").disabled')
                    require(response.status==503 and result['code']=='SEARCH_UNAVAILABLE',result)
                    require(page.locator('.card').count()==0,'failure clears old cards')
                    require(page.locator('#status').get_attribute('class')=='error','visible error')
                    page.locator('.observe summary').click();shot(page,'390-light-unavailable')
                    RECORD['failure']={'status':response.status,'response':result,'old_cards':0,'same_java_pid':process.pid}
                finally:
                    api.command(api.COMPOSE+['up','-d','es']);api.wait(api.ES+'/')
                api.request(api.ES,f'/_cluster/health/{api.INDEX}?wait_for_status=green&timeout=30s')
                submit(page,['a-hz-boundary','a-hz-tea','a-hz-xihu'])
                shot(page,'390-light-recovered')
                RECORD['recovery']={'same_java_pid':process.pid,'IDs':['a-hz-boundary','a-hz-tea','a-hz-xihu']}
                context.close();browser.close()
        require(not RECORD['js_errors'] and not RECORD['direct_es_browser_requests'],RECORD)
        RECORD['status']='passed'
    finally:
        if process:
            process.terminate();process.wait(timeout=20)
        api.request(api.ES,'/'+api.INDEX,'DELETE',label='shell named cleanup')
        RECORD['setup_and_recovery_requests']=api.RECORD
        RECORD['final']={'lesson_index_exists':api.probe(api.ES+'/'+api.INDEX),'java_running':api.probe(api.APP+'/api/health'),'volume':'preserved'}
        (OUT/'shell-review.json').write_text(json.dumps(RECORD,ensure_ascii=False,indent=2)+'\n')
    print('F07 real local shell passed: 12 width/theme groups, exact IDs/prices/observations, stop/recovery, browser never accesses ES')

if __name__=='__main__':
    try:main()
    except Exception as error:
        RECORD['status']='failed';RECORD['failure_detail']=repr(error)
        (OUT/'shell-review.json').write_text(json.dumps(RECORD,ensure_ascii=False,indent=2)+'\n')
        raise
