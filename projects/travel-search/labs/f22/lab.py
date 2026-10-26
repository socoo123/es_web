#!/usr/bin/env python3
"""F22 fixed-data lab; real HTTP logs and independent metric arithmetic."""
import argparse,copy,datetime,hashlib,json,math,os,pathlib,urllib.request,urllib.error
HERE=pathlib.Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
DATA=PROJECT/'data/f22';SEARCH=PROJECT/'search/f22'
INDEX='tut-f22-attractions';ES=os.environ.get('ES_URL','http://127.0.0.1:19222').rstrip('/')
APP=os.environ.get('APP_URL','http://127.0.0.1:18081').rstrip('/')
FIXTURE=json.loads((DATA/'evaluation.json').read_text())
LOG=None;COUNT=0

def require(ok,detail):
    if not ok: raise AssertionError(detail)

def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def request(method,path,body=None,status=200,app=False,label=''):
    global COUNT
    raw=body.encode() if isinstance(body,str) else json.dumps(body,ensure_ascii=False).encode() if body is not None else None
    headers={'Content-Type':'application/x-ndjson' if path.endswith('_bulk') else 'application/json'}
    url=(APP if app else ES)+path
    req=urllib.request.Request(url,data=raw,method=method,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=40) as response: actual=response.status;payload=response.read().decode()
    except urllib.error.HTTPError as error:actual=error.code;payload=error.read().decode()
    decoded=json.loads(payload);COUNT+=1
    record=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),n=COUNT,label=label,method=method,url=url,request=body,status=actual,response=decoded)
    if LOG:
        with LOG.open('a') as output:output.write(json.dumps(record,ensure_ascii=False)+'\n')
    require(actual in (status if isinstance(status,list) else [status]),{'expected':status,'actual':actual,'path':path,'response':decoded})
    return decoded

def query(text,strategy):
    b={'must':[{'multi_match':{'query':text,'fields':['name','description'],'type':'best_fields','operator':'or'}}],
       'filter':[{'term':{'city_code':{'value':'HZ'}}},{'term':{'status':{'value':'open'}}},{'term':{'currency':{'value':'CNY'}}},{'range':{'ticket_price_fen':{'gte':0,'lte':10000}}}],
       'minimum_should_match':'0'}
    if strategy=='candidate':b['should']=[{'match':{'name':{'query':text,'operator':'and','boost':2}}},{'match_phrase':{'name':{'query':text,'boost':4}}}]
    return {'size':10,'track_total_hits':True,'query':{'bool':b},'sort':[{'_score':{'order':'desc'}},{'attraction_id':{'order':'asc'}}]}

def selected(split):return [q for q in FIXTURE['queries'] if q['split']==split]

def rank_request(queries,strategy,metric):
    entries=[]
    for q in queries:
        entries.append({'id':q['id'],'request':query(q['text'],strategy),'ratings':[{'_index':INDEX,'_id':i,'rating':r} for i,r in q['ratings'].items()]})
    return {'requests':entries,'metric':({'recall':{'k':10,'relevant_rating_threshold':2}} if metric=='recall' else {'dcg':{'k':10,'normalize':True,'unknown_doc_rating':0}})}

def dcg(grades):return sum((2**g-1)/math.log2(i+2) for i,g in enumerate(grades))

def metrics(ids,ratings,k=10):
    require(len(ids)==len(set(ids)),'duplicate search hit')
    require(all(i in ratings for i in ids),'unjudged result; do not convert to zero')
    rel=sum(g>=2 for g in ratings.values());grades=[ratings[i] for i in ids[:k]]
    ideal=dcg(sorted(ratings.values(),reverse=True)[:k]);actual=dcg(grades)
    return {'recall':sum(g>=2 for g in grades)/rel if rel else 0.0,'ndcg':actual/ideal if ideal else 0.0,'dcg':actual,'ideal_dcg':ideal,'relevant_docs':rel,'relevant_retrieved':sum(g>=2 for g in grades),'ids':ids[:k],'grades':grades}

def valid_search(result,q):
    require(not result['timed_out'] and result['_shards']['failed']==0 and result['hits']['total']['relation']=='eq','incomplete search')
    hits=result['hits']['hits'];require(len(hits)==10 and result['hits']['total']['value']==20,'canonical query must have 20 eligible matches and 10 returned')
    for h in hits:
        s=h['_source'];require(h['_id']==s['attraction_id'] and s['city_code']=='HZ' and s['status']=='open' and s['currency']=='CNY' and 0<=s['ticket_price_fen']<=10000,'hard exclusion')
    return metrics([h['_id'] for h in hits],q['ratings'])

def prepare():
    version=request('GET','/');require(version['version']['number']=='9.4.0' and version['version']['lucene_version']=='10.4.0','version')
    plugins=request('GET','/_nodes/plugins');require(all(not n['plugins'] for n in plugins['nodes'].values()),'plugins')
    created=request('PUT','/'+INDEX,json.loads((SEARCH/'index.json').read_text()));require(created['acknowledged'],'created')
    health=request('GET','/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s');require(not health['timed_out'] and health['status']=='green' and health['number_of_nodes']==1,'health')
    bulk=request('POST','/'+INDEX+'/_bulk',(DATA/'attractions.ndjson').read_text());require(not bulk['errors'] and len(bulk['items'])==24 and all(i['create']['result']=='created' for i in bulk['items']),'Bulk24')
    request('POST','/'+INDEX+'/_refresh');require(request('GET','/'+INDEX+'/_count')['count']==24,'count24')
    mapping=request('GET','/'+INDEX+'/_mapping')[INDEX]['mappings'];require(mapping==json.loads((SEARCH/'index.json').read_text())['mappings'],'mapping')
    settings=request('GET','/'+INDEX+'/_settings')[INDEX]['settings']['index'];require(settings['number_of_shards']=='1' and settings['number_of_replicas']=='0' and settings['refresh_interval']=='-1','settings')
    return {'status':'passed','http':COUNT,'docs':24}

def evaluate(split):
    qs=selected(split);report={'split':split,'strategies':{},'frozen_plan_sha256':sha(DATA/'decision-plan.json'),'fixture_sha256':sha(DATA/'evaluation.json')}
    for strategy in ['baseline','candidate']:
        per={}
        for q in qs:
            result=request('POST','/'+INDEX+'/_search',query(q['text'],strategy),label=q['id']+'/'+strategy)
            per[q['id']]=valid_search(result,q)
        macro={m:sum(v[m] for v in per.values())/len(per) for m in ['recall','ndcg']}
        for metric in ['recall','ndcg']:
            result=request('POST','/'+INDEX+'/_rank_eval',rank_request(qs,strategy,metric),label=split+'/'+strategy+'/'+metric)
            require(not result.get('failures') and set(result['details'])=={q['id'] for q in qs},'HTTP200 may contain failed cases')
            require(abs(result['metric_score']-macro[metric])<1e-12,'macro mismatch')
            for qid,detail in result['details'].items():
                require(not detail['unrated_docs'] and len(detail['hits'])==10,'judged coverage/length')
                require([h['hit']['_id'] for h in detail['hits']]==per[qid]['ids'],'rank_eval order')
                require(abs(detail['metric_score']-per[qid][metric])<1e-12,'per-query mismatch')
        report['strategies'][strategy]={'queries':per,'macro':macro}
    b=report['strategies']['baseline'];c=report['strategies']['candidate']
    report['delta']={m:c['macro'][m]-b['macro'][m] for m in ['recall','ndcg']}
    report['query_ndcg_deltas']={qid:c['queries'][qid]['ndcg']-b['queries'][qid]['ndcg'] for qid in b['queries']}
    if split=='adjust':report['passes_adjust_gate']=report['delta']['ndcg']>=.01 and report['delta']['recall']>=-1e-12
    elif split=='holdout':
        report['passes_holdout_gate']=all(d>=-1e-12 for d in report['delta'].values()) and min(report['query_ndcg_deltas'].values())>=-.05
        report['decision']='candidate remains only a hypothesis; keep baseline' if not report['passes_holdout_gate'] else 'choose candidate for this fixed teaching fixture only; no population claim; grade0 top results still unresolved'
    report['http']=COUNT;report['status']='passed';return report

def edges():
    q=selected('adjust')[0];canonical=rank_request([q],'baseline','ndcg')
    normal=request('POST','/'+INDEX+'/_rank_eval',canonical)
    drop=copy.deepcopy(canonical);first=normal['details'][q['id']]['hits'][0]['hit']['_id'];drop['requests'][0]['ratings']=[r for r in drop['requests'][0]['ratings'] if r['_id']!=first]
    unknown=request('POST','/'+INDEX+'/_rank_eval',drop);require(unknown['details'][q['id']]['unrated_docs']==[{'_index':INDEX,'_id':first}],'missing label not zero')
    short=copy.deepcopy(canonical);short['requests'][0]['request']['query']={'ids':{'values':['a01','a02']}};short['requests'][0]['ratings']=[{'_index':INDEX,'_id':i,'rating':3} for i in ['a01','a02','a03']]
    out=request('POST','/'+INDEX+'/_rank_eval',short);require(out['metric_score']==1,'ES9.4.0 short ideal length')
    full=metrics(['a01','a02'],{'a01':3,'a02':3,'a03':3});require(full['ndcg']<1,'full ideal sees missed a03')
    zero=copy.deepcopy(canonical);zero['requests'][0]['request']['query']={'match_none':{}}
    out=request('POST','/'+INDEX+'/_rank_eval',zero);require(out['metric_score']==0,'empty hits nDCG0')
    norel=copy.deepcopy(canonical)
    for rating in norel['requests'][0]['ratings']:rating['rating']=0
    for metric in [{'recall':{'k':10,'relevant_rating_threshold':2}},{'dcg':{'k':10,'normalize':True,'unknown_doc_rating':0}}]:
        norel['metric']=metric;out=request('POST','/'+INDEX+'/_rank_eval',norel);require(out['metric_score']==0,'no relevant docs convention0')
    narrow=query(q['text'],'baseline');narrow['query']['bool']['must']=[{'match':{'name':{'query':'西湖 雨天','operator':'and'}}}]
    out=request('POST','/'+INDEX+'/_search',narrow);require(out['hits']['total']['value']==1 and out['hits']['hits'][0]['_id']=='a09','lexical candidate miss')
    out=request('POST','/'+INDEX+'/_search',query('西湖 雨天','baseline'));require(out['hits']['total']['value']==20,'restore broad candidates')
    broken=copy.deepcopy(canonical);broken['metric']['dcg']['k']=-1
    request('POST','/'+INDEX+'/_rank_eval',broken,status=400)
    partial=copy.deepcopy(canonical);bad=copy.deepcopy(partial['requests'][0]);bad['id']='bad-number';bad['request']['query']={'term':{'ticket_price_fen':'not-a-number'}};partial['requests'].append(bad)
    out=request('POST','/'+INDEX+'/_rank_eval',partial);require('bad-number' in out['failures'] and len(out['details'])==1,'partial failures HTTP200')
    restored=request('POST','/'+INDEX+'/_rank_eval',canonical);require(not restored['failures'] and restored['details'][q['id']]['unrated_docs']==[],'recovery')
    return {'status':'passed','http':COUNT,'short_es_ndcg':1,'short_standard_ndcg':full['ndcg'],'unrated_id':first,'partial_http200_detected':True,'no_relevant_policy':'main queries all have positive labels; zero relevant grouped separately, not a perfect score'}

def java():
    rows=[]
    for split in ['adjust','holdout','assessment']:
        for strategy in ['baseline','candidate']:
            out=request('POST','/api/quality/evaluate',{'split':split,'strategy':strategy},app=True)
            require(out['conditions']=={'split':split,'strategy':strategy},'input echo')
            qs=selected(split);require(len(out['queries'])==len(qs),'query count')
            for q,actual in zip(qs,out['queries']):
                req=actual['esRequest'];require(req==query(q['text'],strategy),'Java DSL semantic parity')
                rest=request('POST','/'+INDEX+'/_search',req)
                score=valid_search(rest,q);require(actual['id']==q['id'] and actual['ids']==score['ids'] and actual['grades']==score['grades'],'Java order/grades')
                for m in ['recall','ndcg','dcg','ideal_dcg']:require(abs(actual[m]-score[m])<1e-10,{'Java metric':m})
                rh=rest['hits']['hits'];jh=actual['esResponse']['hits']['hits']
                require(len(rh)==len(jh) and all(a['_id']==b['_id'] and a['_source']==b['_source'] and abs(a['_score']-b['_score'])<1e-6 and a['sort']==b['sort'] for a,b in zip(rh,jh)),'Java complete projection')
            for metric in ['recall','ndcg']:require(abs(out['macro'][metric]-sum(q[metric] for q in out['queries'])/len(qs))<1e-12,'Java macro')
            rows.append({'split':split,'strategy':strategy,'macro':out['macro']})
    return {'status':'passed','http':COUNT,'rows':rows,'note':'Java endpoint executes one actual ES search per query; REST replays separately, fixed data only, no cross-request snapshot guarantee'}

def cleanup():
    request('DELETE','/'+INDEX,status=[200,404]);request('GET','/'+INDEX,status=404)
    return {'status':'passed','http':COUNT,'deleted_only':INDEX}

def generate():
    for q in FIXTURE['queries']:
        for strategy in ['baseline','candidate']:dump(SEARCH/f"{q['id']}-{strategy}.json",query(q['text'],strategy))
    for split in ['adjust','holdout','assessment']:
        for strategy in ['baseline','candidate']:
            for metric in ['recall','ndcg']:dump(SEARCH/f'{split}-{strategy}-{metric}.json',rank_request(selected(split),strategy,metric))
    # Compact explicit ratings keep the full executable example readable.
    out=rank_request([selected('adjust')[0]],'candidate','ndcg')
    text=json.dumps(out,ensure_ascii=False,indent=2)
    import re
    text=re.sub(r'\{\n\s+"_index": "([^"]+)",\n\s+"_id": "([^"]+)",\n\s+"rating": (\d)\n\s+\}',lambda m:'{"_index": "'+m[1]+'", "_id": "'+m[2]+'", "rating": '+m[3]+'}',text)
    (SEARCH/'example-ndcg.json').write_text(text+'\n')
    return {'generated':'fixed requests from explicit fixture; not an ES verification'}

def main():
    global LOG
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','adjust','holdout','assessment','edges','java','cleanup','generate']);parser.add_argument('--log');parser.add_argument('--out');a=parser.parse_args()
    if a.log:LOG=pathlib.Path(a.log);LOG.parent.mkdir(parents=True,exist_ok=True)
    stage={'prepare':prepare,'adjust':lambda:evaluate('adjust'),'holdout':lambda:evaluate('holdout'),'assessment':lambda:evaluate('assessment'),'edges':edges,'java':java,'cleanup':cleanup,'generate':generate}[a.stage]
    result=stage()
    if a.out:dump(pathlib.Path(a.out),result)
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
