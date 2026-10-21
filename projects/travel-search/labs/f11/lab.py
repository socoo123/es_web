#!/usr/bin/env python3
"""F11手工实验：自动搬运真实PIT/完整sort；每次打印完整请求和响应。仅Python标准库。"""
import copy, json, os, pathlib, sys, urllib.request, urllib.error
ROOT = pathlib.Path(__file__).resolve().parents[2]
ES = 'http://127.0.0.1:19200'
APP = 'http://127.0.0.1:18080'
INDEX = 'tut-f11-attractions'
RECORD = []

def load(path): return json.loads((ROOT/path).read_text())
def call(method, path, body=None, *, app=False, expected=200, ndjson=None):
    data = (ROOT/ndjson).read_bytes() if ndjson else None if body is None else json.dumps(body, ensure_ascii=False).encode()
    headers = {'Content-Type':'application/x-ndjson' if ndjson else 'application/json'}
    request = urllib.request.Request((APP if app else ES)+path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request,timeout=35) as response: status,raw=response.status,response.read().decode()
    except urllib.error.HTTPError as error: status,raw=error.code,error.read().decode()
    result=json.loads(raw)
    record={'method':method,'path':path,'target':'Java' if app else 'ES','request':json.loads(data) if data and not ndjson else ndjson,
            'status':status,'response':result}
    RECORD.append(record)
    print(json.dumps(record,ensure_ascii=False),flush=True)
    if status != expected: raise RuntimeError(f'{method} {path}: expected {expected}, got {status}')
    return result

def search(body, pit=False, expected=200):
    return call('POST','/_search' if pit else f'/{INDEX}/_search',body,expected=expected)
def ids(response): return [h['_id'] for h in response['hits']['hits']]
def restore():
    result=call('POST',f'/{INDEX}/_bulk',ndjson='data/f11/attractions.ndjson')
    assert not result['errors'] and len(result['items'])==16
    assert call('POST',f'/{INDEX}/_refresh')['_shards']['failed']==0

def offsets():
    body=load('search/f11/page.json');allids=[]
    for offset in [0,3,6]:
        page=search(dict(body,**{'from':offset}));allids+=ids(page)
    assert allids==OLD and len(set(allids))==9
    error=search(load('search/f11/window-error.json'),expected=400)
    assert 'Result window is too large' in json.dumps(error)

def view():
    restore()
    body=load('search/f11/page.json');pitbody=load('search/f11/pit-page.json')
    plain=search(body);assert ids(plain)==OLD[:3]
    pit=call('POST',f'/{INDEX}/_pit?keep_alive=1m&allow_partial_search_results=false')['id']
    closed=False
    try:
        pitbody['pit']={'id':pit,'keep_alive':'1m'}
        fixed=search(pitbody,True);pit=fixed.get('pit_id',pit)
        fixedids=ids(fixed);fixedprices=[h['_source']['ticket_price_fen'] for h in fixed['hits']['hits']]
        moved=call('POST',f'/{INDEX}/_bulk',ndjson='data/f11/move-prices.ndjson')
        assert not moved['errors'] and all(x['index']['result']=='updated' for x in moved['items'])
        assert call('POST',f'/{INDEX}/_refresh')['_shards']['failed']==0
        offsetids=ids(plain)
        for offset in [3,6]: offsetids+=ids(search(dict(body,**{'from':offset})))
        afterids=ids(plain);after=plain['hits']['hits'][-1]['sort']
        for _ in range(2):
            result=search(dict(body,search_after=after));afterids+=ids(result);after=result['hits']['hits'][-1]['sort']
        assert offsetids==afterids==BROKEN
        for _ in range(2):
            pitbody['pit']['id']=pit
            pitbody['search_after']=fixed['hits']['hits'][-1]['sort']
            fixed=search(pitbody,True);pit=fixed.get('pit_id',pit)
            fixedids+=ids(fixed);fixedprices += [h['_source']['ticket_price_fen'] for h in fixed['hits']['hits']]
        assert fixedids==OLD and fixedprices==[0,0,1000,1000,1000,1000,8000,10000,20000]
        live=search(dict(body,size=20));assert ids(live)==NEW
        bad=copy.deepcopy(pitbody);bad['pit']['id']=pit;bad['search_after']=fixed['hits']['hits'][-1]['sort'][:2]
        search(bad,True,expected=400)
        assert call('DELETE','/_pit',{'id':pit})['succeeded'];closed=True
        search(dict(pitbody,pit={'id':pit,'keep_alive':'1m'}),True,expected=404)
    finally:
        # Close only this experiment's latest PIT, including on failed assertions.
        try:
            if not closed: call('DELETE','/_pit',{'id':pit})
        finally: restore()

def java():
    for mode in ['price','relevance','distance']:
        conditions=load(f'search/f11/input-{mode}.json')
        result=call('POST','/api/attractions/pages/start',conditions,app=True)
        cursor=result['cursor'];allids=[]
        try:
            while True:
                # Replay the exact Java request through REST in the SAME PIT.
                rest=search(result['esRequest'],True)
                assert [(x['id'],x['sortValues'],x['ticketPriceFen'],x['score']) for x in result['items']] == [
                    (x['_id'],x['sort'],x['_source']['ticket_price_fen'],x['_score']) for x in rest['hits']['hits']]
                assert result['total']==rest['hits']['total']['value']==9 and result['totalRelation']=='eq'
                allids += [x['id'] for x in result['items']]
                if not result['hasNext']: break
                result=call('POST','/api/attractions/pages/next',{'cursor':cursor,'afterPage':result['pageNumber'],'conditions':conditions},app=True)
            assert len(allids)==len(set(allids))==9
            if mode=='price': assert allids==OLD
            call('POST','/api/attractions/pages/next',{'cursor':cursor,'afterPage':result['pageNumber'],'conditions':conditions},app=True,expected=409)
        finally: call('POST','/api/attractions/pages/close',{'cursor':cursor},app=True)
        call('POST','/api/attractions/pages/next',{'cursor':cursor,'afterPage':1,'conditions':conditions},app=True,expected=410)
    conditions=load('search/f11/input-price.json')
    result=call('POST','/api/attractions/pages/start',conditions,app=True);cursor=result['cursor']
    try:
        changed=copy.deepcopy(conditions);changed['search']['cityCode']='HZ'
        call('POST','/api/attractions/pages/next',{'cursor':cursor,'afterPage':1,'conditions':changed},app=True,expected=409)
        call('POST','/api/attractions/pages/next',{'cursor':cursor,'afterPage':2,'conditions':conditions},app=True,expected=409)
    finally: call('POST','/api/attractions/pages/close',{'cursor':cursor},app=True)

OLD=['a-fz-xihu','a-hz-xihu','a-hz-far','a-hz-guide','a-hz-missing-location','a-hz-plain','a-hz-tea','a-sh-exhibit','a-hz-boundary']
BROKEN=OLD[:6]+['a-sh-exhibit','a-hz-far','a-hz-boundary']
NEW=['a-fz-xihu','a-hz-xihu','a-hz-tea','a-hz-guide','a-hz-missing-location','a-hz-plain','a-sh-exhibit','a-hz-far','a-hz-boundary']
if __name__=='__main__':
    scenario=sys.argv[1]
    try: {'offsets':offsets,'view':view,'java':java}[scenario]()
    finally:
        if len(sys.argv)>2: pathlib.Path(sys.argv[2]).write_text(json.dumps({'scenario':scenario,'requests':len(RECORD),'operations':RECORD},ensure_ascii=False,indent=2)+'\n')
    print(f'{scenario}: {len(RECORD)} HTTP requests; passed',file=sys.stderr)
