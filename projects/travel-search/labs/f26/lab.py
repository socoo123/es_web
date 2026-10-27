#!/usr/bin/env python3
"""F26 real HTTP acceptance; independent, manually specified result constants."""
import argparse, copy, datetime, json, os, pathlib, urllib.error, urllib.request
HERE=pathlib.Path(__file__).resolve().parent; P=HERE.parents[1]
DATA=P/'data/f26'; SEARCH=P/'search/f26'; INDEX='tut-f26-offers'
ES=os.environ.get('ES_URL','http://127.0.0.1:19226').rstrip('/')
APP=os.environ.get('APP_URL','http://127.0.0.1:18081').rstrip('/')
LOG=None; COUNT=0
FLAT=['o01','o05','o09','o10','o02','o03','o06','o07','o08','o16']
ROOTS=['o01','o05','o09','o10','o07','o16']
PRICE={'o01':100000,'o02':80000,'o03':90000,'o05':120000,'o06':100000,'o09':60000,'o10':60000}
def require(ok,detail):
    if not ok:raise AssertionError(detail)
def read(path):return json.loads(path.read_text())
def request(method,path,body=None,status=200,app=False):
    global COUNT
    raw=body.encode() if isinstance(body,str) else json.dumps(body,ensure_ascii=False).encode() if body is not None else None
    url=(APP if app else ES)+path
    req=urllib.request.Request(url,data=raw,method=method,headers={'Content-Type':'application/x-ndjson' if '_bulk' in path else 'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=40) as r:actual=r.status;payload=r.read().decode()
    except urllib.error.HTTPError as e:actual=e.code;payload=e.read().decode()
    result=json.loads(payload);COUNT+=1
    if LOG:
        with LOG.open('a') as f:f.write(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),n=COUNT,method=method,url=url,request=body,status=actual,response=result),ensure_ascii=False)+'\n')
    require(actual in (status if isinstance(status,list) else [status]),dict(path=path,expected=status,actual=actual,response=result))
    return result
def search(name_or_body):
    q=read(SEARCH/(name_or_body+'.json')) if isinstance(name_or_body,str) else name_or_body
    r=request('POST','/'+INDEX+'/_search',q)
    require(not r['timed_out'] and r['_shards']['failed']==0 and r['hits']['total']['relation']=='eq','complete search');return r
def ids(r):return [h['_id'] for h in r['hits']['hits']]
def norm(x):
    if isinstance(x,list):return [norm(v) for v in x]
    if isinstance(x,dict):return {k:norm(v) for k,v in x.items() if not (k in ['_score','max_score'] and v is None)}
    return x
def prepare():
    v=request('GET','/');require(v['version']['number']=='9.4.0' and v['version']['lucene_version']=='10.4.0','versions')
    nodes=request('GET','/_nodes/plugins');require(len(nodes['nodes'])==1 and all(not n['plugins'] for n in nodes['nodes'].values()),'one plugin-free node')
    schema=read(SEARCH/'index.json');request('PUT','/'+INDEX,schema)
    h=request('GET','/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s');require(h['status']=='green' and not h['timed_out'] and h['number_of_nodes']==1,'green')
    b=request('POST','/'+INDEX+'/_bulk',(DATA/'summaries.ndjson').read_text());require(not b['errors'] and len(b['items'])==16 and all(i['create']['result']=='created' for i in b['items']),'16 created')
    request('POST','/'+INDEX+'/_refresh');require(request('GET','/'+INDEX+'/_count')['count']==16,'16 roots')
    expected=copy.deepcopy(schema['mappings'])
    for prop in expected['properties'].values():
        if prop.get('doc_values') is True:prop.pop('doc_values') # ES omits this default from GET mapping
    require(request('GET','/'+INDEX+'/_mapping')[INDEX]['mappings']==expected,'whole mapping; only explicit default doc_values:true omitted by ES')
    settings=request('GET','/'+INDEX+'/_settings')[INDEX]['settings']['index'];require(all(settings[k]==str(v) for k,v in schema['settings'].items()),'explicit settings')
    summaries=read(DATA/'summaries.json');docs=request('POST','/'+INDEX+'/_mget',{'ids':[s['offer_id'] for s in summaries]})['docs']
    require(all(d['found'] and d['_source']==s for d,s in zip(docs,summaries)),'all source exact')
    return dict(documents=16,hotels=9,mapping_settings_source='exact')
def collapse():
    flat=search('all');r=search('collapse');without=search('without-meal')
    require(ids(flat)==FLAT and ids(r)==ROOTS,'flat/collapsed ID order')
    for x in [flat,r]:require(x['hits']['total']=={'value':10,'relation':'eq'} and x['aggregations']['candidate_hotels']['value']==6,'10 documents and 6 estimated hotels unchanged by collapse')
    require(ids(without)[0]=='o04' and without['hits']['total']['value']==12,'unqualified room-only low price')
    count=request('POST','/'+INDEX+'/_count',{'query':read(SEARCH/'all.json')['query']});require(count['count']==10,'count is offers')
    exact=sorted({h['_source']['hotel_id'] for h in flat['hits']['hits']});require(exact==['h01','h02','h03','h04','h05','h09'],'complete candidate hotel set')
    return dict(flat=ids(flat),collapsed=ids(r),documents=10,exact_candidate_hotels=exact,cardinality_observed=6,without_meal_first='o04')
def inner():
    rs={n:search(n) for n in ['inner-one','collapse','inner-all','inner-desc']}
    expected={'inner-one':['o01'],'collapse':['o01','o02'],'inner-all':['o01','o02','o03'],'inner-desc':['o03']}
    for name,r in rs.items():
        require(ids(r)==ROOTS,'inner sort/size must not change representative or group order')
        first=r['hits']['hits'][0];i=first['inner_hits']['offers']['hits']
        require(i['total']=={'value':3,'relation':'eq'} and [h['_id'] for h in i['hits']]==expected[name],'h01 matching offers and explicit limit/order')
        require(all(h['_source']['meal']=='breakfast' and h['_source']['hotel_id']=='h01' for h in i['hits']),'original query scope plus group key')
        require(first['_source']['min_price_minor']==10000,'outer start price stays 10000')
    full=rs['inner-all']
    groups={'h01':['o01','o02','o03'],'h02':['o05','o06'],'h03':['o07','o08'],'h04':['o09'],'h05':['o10'],'h09':['o16']}
    for hit in full['hits']['hits']:
        h=hit['_source']['hotel_id'];inner=hit['inner_hits']['offers']['hits']
        require([v['_id'] for v in inner['hits']]==groups[h] and inner['total']['value']==len(groups[h]),'all groups complete original-query expansion')
    return dict(h01_inner_ids=expected,total=3,outer='o01',nested=False)
def verify(mode,r):
    require(r['conditions']=={'mode':mode} and r['snapshotId']=='f26-20261027-v1','contract')
    require(r['esRequest']==read(SEARCH/(mode+'.json')),'complete Java DSL exactly equals canonical REST')
    replay=search(r['esRequest']);require(norm(replay['hits'])==norm(r['esResponse']['hits']),'all IDs/source/order/sort/total/inner_hits REST == Java')
    require(r['candidateOfferTotal']==10 and r['candidateHotelEstimate']==6,'candidate counts')
    require(all((d['offerId'] in PRICE and d['totalMinor']==PRICE[d['offerId']] and d['reason']=='ACCEPTED') or
                (d['offerId'] in {'o07':'MISSING_NIGHT','o08':'SOLD_OUT','o16':'MIN_STAY'} and d['reason']=={'o07':'MISSING_NIGHT','o08':'SOLD_OUT','o16':'MIN_STAY'}[d['offerId']] and d['totalMinor'] is None) for d in r['decisions']),'independent exact totals/reasons')
    table={o['summary']['offer_id']:o['nights'] for o in read(DATA/'stay-table.json')['offers']}
    require(all(d['nights']==table[d['offerId']] for d in r['decisions']),'all actual nightly rows exact')
    expected={'top-offers':[('h01','o01',100000),('h02','o05',120000)],
      'top-hotels':[('h01','o02',80000),('h02','o06',100000)],
      'all':[('h04','o09',60000),('h05','o10',60000),('h01','o02',80000),('h02','o06',100000)]}[mode]
    require([(h['hotelId'],h['minimumOfferId'],h['minimumTotalMinor']) for h in r['hotels']]==expected,'independent hotel minimum and order constants')
    accepted={'h01':['o02','o03','o01'],'h02':['o06','o05'],'h04':['o09'],'h05':['o10']}
    for h in r['hotels']:
        require(h['acceptedOfferIds']==([h['minimumOfferId']] if mode=='top-offers' else accepted[h['hotelId']]),'every accepted offer and within-hotel total order')
    require((r['inspectedOfferCount'],r['inspectedHotelCount'],r['acceptedOfferCount'],r['displayedHotelCount'])=={'top-offers':(2,2,2,2),'top-hotels':(5,2,5,2),'all':(10,6,7,4)}[mode],'all count scopes')
    require(r['completeCandidateSet']==(mode=='all'),'coverage flag')
    return dict(mode=mode,hotels=expected,inspected=r['inspectedOfferCount'],complete=r['completeCandidateSet'])
def stays():
    return [verify(mode,request('POST','/api/collapse/inspect',{'mode':mode},app=True)) for mode in ['top-offers','top-hotels','all']]
def put(id,s):return request('PUT','/'+INDEX+'/_doc/'+id+'?refresh=true',s,status=[200,201])
def errors():
    r=request('PUT','/'+INDEX,read(SEARCH/'index.json'),400);require(r['error']['type']=='resource_already_exists_exception','duplicate index')
    r=request('POST','/'+INDEX+'/_bulk',(DATA/'summaries.ndjson').read_text());require(r['errors'] and all(i['create']['status']==409 for i in r['items']),'bulk16 conflicts')
    for body in [{},{'mode':None},{'mode':'wrong'},{'mode':''},{'mode':5},[]]:
        require(request('POST','/api/collapse/inspect',body,400,True)['code']=='INVALID_COLLAPSE_INPUT','400 input')
    for field in ['not_mapped','window_start']:
        q=read(SEARCH/'collapse.json');q['collapse']['field']=field;request('POST','/'+INDEX+'/_search',q,400)
    q=read(SEARCH/'collapse.json');q['search_after']=[10000,'h01','o01'];request('POST','/'+INDEX+'/_search',q,400)
    request('POST','/'+INDEX+'/_search?scroll=1m',read(SEARCH/'collapse.json'),400)
    s=read(DATA/'summaries.json')[0];bad=copy.deepcopy(s);bad['unexpected']=True
    request('PUT','/'+INDEX+'/_doc/f26-bad',bad,400)
    bad=copy.deepcopy(s);bad['snapshot_id']='stale';put('o01',bad)
    require(request('POST','/api/collapse/inspect',{'mode':'all'},502,True)['code']=='SEARCH_INCOMPLETE','stale source rejected')
    put('o01',s);verify('all',request('POST','/api/collapse/inspect',{'mode':'all'},app=True))
    # Independent group expansion and full set size guards; never label truncated minima exact.
    for mode,n in [('top-hotels',11),('all',101)]:
        ops=[];test_ids=[]
        for i in range(n):
            id=f'f26-overflow-{i:03}';test_ids.append(id);doc=copy.deepcopy(s);doc.update(offer_id=id,min_price_minor=999999 if mode=='top-hotels' else 5000)
            ops.extend([{'create':{'_id':id}},doc])
        raw=''.join(json.dumps(x)+'\n' for x in ops);r=request('POST','/'+INDEX+'/_bulk?refresh=true',raw);require(not r['errors'],'injected candidates')
        if mode=='top-hotels':
            expanded=search('top-hotels');first=expanded['hits']['hits'][0];inner=first['inner_hits']['offers']['hits']
            require(ids(expanded)==['o01','o05'] and first['_source']==s and inner['total']=={'value':14,'relation':'eq'} and len(inner['hits'])==10,'known representative source passes; group is independently proven truncated before Java guard')
        require(request('POST','/api/collapse/inspect',{'mode':mode},502,True)['code']=='SEARCH_INCOMPLETE','truncation guard')
        raw=''.join(json.dumps({'delete':{'_id':id}})+'\n' for id in test_ids);r=request('POST','/'+INDEX+'/_bulk?refresh=true',raw);require(not r['errors'],'point-named remove injected candidates')
        verify(mode,request('POST','/api/collapse/inspect',{'mode':mode},app=True))
    return dict(duplicate_index=400,bulk_conflicts=16,invalid_inputs=6,invalid_collapse=4,strict=400,stale_source=502,inner_and_full_truncation=502,recovered=True)
def cleanup():
    request('DELETE','/'+INDEX,status=[200,404]);r=request('GET','/'+INDEX, status=404)
    require(r['error']['type']=='index_not_found_exception','confirmed absent');return {'deleted':INDEX,'get_after':404}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('section',choices=['prepare','collapse','inner','stays','errors','cleanup']);ap.add_argument('--out',required=True);args=ap.parse_args()
    out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True);LOG=out/(args.section+'.jsonl');require(not LOG.exists(),'use a fresh receipt directory')
    value=globals()[args.section]();receipt=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),section=args.section,http_requests=COUNT,result=value)
    (out/(args.section+'.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
