#!/usr/bin/env python3
"""F14: the same documents, judgments and filters for every installed analyzer."""
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

PROJECT = pathlib.Path(__file__).resolve().parents[2]
INDEX = 'tut-f14-attractions'
ES = os.environ.get('ES_URL', 'http://127.0.0.1:19214').rstrip('/')
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18080').rstrip('/')
CALLS = []

def load(path): return json.loads((PROJECT / path).read_text())
def call(method, path, body=None, expected=200, app=False, ndjson=False):
    data = body.encode() if ndjson else (json.dumps(body, ensure_ascii=False).encode() if body is not None else None)
    request = urllib.request.Request((APP if app else ES)+path, data=data, method=method,
        headers={'Content-Type':'application/x-ndjson' if ndjson else 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response: status, raw = response.status, response.read()
    except urllib.error.HTTPError as error: status, raw = error.code, error.read()
    result = json.loads(raw)
    row = {'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':'Java' if app else 'ES',
        'method':method,'path':path,'request':body,'status':status,'response':result}
    CALLS.append(row); print(json.dumps(row,ensure_ascii=False),flush=True)
    assert status == expected, (method,path,status,expected)
    return result

def ids(response):
    assert response['timed_out'] is False and response['_shards']['failed']==0
    assert response['hits']['total']['relation']=='eq'
    hits=response['hits']['hits']; assert len(hits)==response['hits']['total']['value']
    return [h['_id'] for h in hits]

def tokens(response):
    return [(t['token'],t['position'],t['start_offset'],t['end_offset']) for t in response['tokens']]

def prepare(plugins=False):
    v=call('GET','/')['version']; assert (v['number'],v['lucene_version'])==('9.4.0','10.4.0')
    assert call('PUT','/'+INDEX,load('search/f14/index-plugins.json' if plugins else 'search/f14/index-baseline.json'))['acknowledged']
    h=call('GET','/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s')
    assert h['status']=='green' and not h['timed_out']
    b=call('POST','/'+INDEX+'/_bulk',(PROJECT/'data/f14/attractions.ndjson').read_text(),ndjson=True)
    assert not b['errors'] and len(b['items'])==12
    assert all(i['index']['status']==201 and i['index']['result']=='created' for i in b['items'])
    assert call('POST','/'+INDEX+'/_refresh')['_shards']['failed']==0
    assert call('GET','/'+INDEX+'/_count')['count']==12

def inventory(plugins=False):
    nodes=call('GET','/_nodes/plugins')['nodes']; assert len(nodes)==1
    names=sorted(p['name'] for n in nodes.values() for p in n['plugins'])
    assert all(p['version']=='9.4.0' for n in nodes.values() for p in n['plugins'])
    assert names==(['analysis-icu','analysis-ik','analysis-smartcn'] if plugins else []),names
    expected=load('search/f14/index-plugins.json' if plugins else 'search/f14/index-baseline.json')
    mapping=call('GET','/'+INDEX+'/_mapping')[INDEX]['mappings']
    # The API may omit search_analyzer when equal to analyzer.
    def normalize(node):
        if isinstance(node,dict):
            if node.get('type')=='text':node.setdefault('search_analyzer',node['analyzer'])
            for child in list(node.values()):normalize(child)
    normalize(mapping); assert mapping==expected['mappings']
    settings=call('GET','/'+INDEX+'/_settings')[INDEX]['settings']['index']
    assert (settings['number_of_shards'],settings['number_of_replicas'],settings['refresh_interval'])==('1','0','-1')

def compare(plugins=False, checking=True):
    candidates=load('search/f14/candidates.json')
    if not plugins: candidates={'standard':candidates['standard']}
    judgments=load('data/f14/judgments.json')['queries']; matrix={}
    expected=load('search/f14/expected.json') if checking else None
    for name,(field,analyzer) in candidates.items():
        streams={}
        for q in judgments:
            streams[q['id']]=tokens(call('POST','/'+INDEX+'/_analyze',{'analyzer':analyzer,'text':q['q']}))
        if plugins:
            for sample in ['北京故宫博物院','南京市长江大桥','Ｃａｆｅ 城市咖啡馆']:
                streams[sample]=tokens(call('POST','/'+INDEX+'/_analyze',{'analyzer':analyzer,'text':sample}))
        results={}
        for q in judgments:
            hits=ids(call('POST','/'+INDEX+'/_search',load(f'search/f14/{name}/{q["id"]}.json')))
            relevant=q['relevant']
            results[q['id']]={'hits':hits,'missed':sorted(set(relevant)-set(hits)),'unwanted':sorted(set(hits)-set(relevant))}
        matrix[name]={'tokens':streams,'queries':results}
        if checking:
            assert results==expected[name]['queries'],name
            for key,value in streams.items(): assert value==[tuple(t) for t in expected[name]['tokens'][key]],(name,key,value)
    if not plugins:
        for analyzer in ['smartcn','icu_analyzer','ik_smart']:
            error=call('POST','/'+INDEX+'/_analyze',{'analyzer':analyzer,'text':'故宫'},expected=400)
            assert 'analyzer' in json.dumps(error)
    return matrix

def java():
    candidates=load('search/f14/candidates.json');judgments=load('data/f14/judgments.json')['queries']
    for candidate,qid in [('standard','palace'),('smartcn','palace'),('icu','palace'),('ik-smart','river'),('ik-max','river'),('icu','cafe')]:
        q=next(q for q in judgments if q['id']==qid)
        inp={k:q[k] for k in ['q','cityCode','maxPriceFen']};inp['candidate']=candidate
        result=call('POST','/api/attractions/analyzer-search',inp,app=True)
        assert result['conditions']==inp and result['field']==candidates[candidate][0]
        for key,requestkey in [('queryTokens','queryAnalysisRequest'),('sampleTokens','sampleAnalysisRequest')]:
            rest=call('POST','/'+INDEX+'/_analyze',result[requestkey])
            assert [(t['token'],t['position'],t['startOffset'],t['endOffset']) for t in result[key]]==tokens(rest)
        rest=call('POST','/'+INDEX+'/_search',result['esRequest'])
        wanted=load('search/f14/expected.json')[candidate]['queries'][qid]['hits']
        assert ids(rest)==wanted==[i['id'] for i in result['items']]
        assert result['total']==len(wanted) and result['relation']=='eq'
        for item,hit in zip(result['items'],rest['hits']['hits'],strict=True):
            assert (item['name'],item['cityCode'],item['ticketPriceFen'],item['score'],item['sortValues'])==(hit['_source']['name'],hit['_source']['city_code'],hit['_source']['ticket_price_fen'],hit['_score'],hit['sort'])

def cleanup():
    try: call('DELETE','/'+INDEX)
    except AssertionError:
        if CALLS[-1]['status']!=404:raise
    assert call('GET','/'+INDEX,expected=404)['status']==404

if __name__=='__main__':
    action=sys.argv[1]
    if action=='prepare-baseline':prepare()
    elif action=='prepare-plugins':prepare(True)
    elif action=='baseline':inventory();compare()
    elif action=='compare':inventory(True);compare(True)
    elif action=='java':java()
    elif action=='cleanup':cleanup()
    else:raise SystemExit('Unknown action')
