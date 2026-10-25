#!/usr/bin/env python3
"""F17 real ES/Java evidence. Each request and full response is emitted as JSONL."""
import datetime
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

PROJECT = pathlib.Path(__file__).resolve().parents[2]
ES = os.environ.get('ES_URL', 'http://127.0.0.1:19217').rstrip('/')
APP = os.environ.get('APP_URL', 'http://127.0.0.1:18080').rstrip('/')
INDEX = 'tut-f17-attractions'
CALLS, RESULTS = [], {}


def load(name): return json.loads((PROJECT / ('search/f17/' + name + '.json')).read_text())

def call(method, path, body=None, expected=200, app=False, ndjson=False):
    data = body.encode() if ndjson else json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    request = urllib.request.Request((APP if app else ES) + path, data=data, method=method,
        headers={'Content-Type': 'application/x-ndjson' if ndjson else 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response: status, raw = response.status, response.read()
    except urllib.error.HTTPError as error: status, raw = error.code, error.read()
    value = json.loads(raw)
    row = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'target': 'Java' if app else 'ES',
           'method': method, 'path': path, 'request': body, 'status': status, 'response': value}
    CALLS.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
    assert status in (expected if isinstance(expected, tuple) else (expected,)), (method, path, status, expected)
    return value


def refresh(): assert call('POST', '/' + INDEX + '/_refresh')['_shards']['failed'] == 0

def options(r):
    assert not r['timed_out'] and r['_shards']['failed'] == 0
    return r['suggest'].get('places', r['suggest'].get('completion#places'))[0]['options']

def hits(r):
    assert not r['timed_out'] and r['_shards']['failed'] == 0
    assert r['hits']['total']['relation'] == 'eq'
    assert len(r['hits']['hits']) == r['hits']['total']['value']
    return r['hits']['hits']

def search(name, expected, suggest=False):
    r=call('POST','/'+INDEX+'/_search',load(name))
    rows=options(r) if suggest else hits(r)
    found=[h['_id'] for h in rows]
    assert found==expected,(name,found,expected)
    RESULTS[name]=found
    if suggest: RESULTS[name+':text-weight']=[(x['text'],x['_score']) for x in rows]
    return r

def analyze(field,text):
    body={'field':field,'text':text}
    r=call('POST','/'+INDEX+'/_analyze',body)
    RESULTS['analyze:'+field+':'+text]=r['tokens']
    return r['tokens']

def prepare():
    v=call('GET','/')['version'];assert (v['number'],v['lucene_version'])==('9.4.0','10.4.0')
    nodes=call('GET','/_nodes/plugins')['nodes'];assert len(nodes)==1
    assert not next(iter(nodes.values()))['plugins']
    r=call('PUT','/'+INDEX,load('index'));assert r['acknowledged'] and r['shards_acknowledged']
    r=call('GET','/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s');assert not r['timed_out'] and r['status']=='green'
    r=call('POST','/'+INDEX+'/_bulk',(PROJECT/'data/f17/attractions.ndjson').read_text(),ndjson=True)
    assert len(r['items'])==14 and not r['errors']
    assert all(i['create']['status']==201 and i['create']['result']=='created' for i in r['items'])
    refresh();assert call('GET','/'+INDEX+'/_count')['count']==14
    mapping=call('GET','/'+INDEX+'/_mapping')[INDEX]['mappings']
    expected=load('index')['mappings']
    # ES serializes an equal search analyzer as the explicit non-default analyzer only.
    mapping['properties']['suggest'].setdefault('search_analyzer',mapping['properties']['suggest']['analyzer'])
    mapping['properties']['name_sayt'].setdefault('doc_values',False)
    expected['properties']['name_sayt']['doc_values']=False
    for c in mapping['properties']['suggest']['contexts']: c['type']=c['type'].lower()
    assert mapping==expected,(mapping,expected)
    settings=call('GET','/'+INDEX+'/_settings')[INDEX]['settings']['index']
    assert (settings['number_of_shards'],settings['number_of_replicas'],settings['refresh_interval'])==('1','0','-1')
    assert settings['analysis']==load('index')['settings']['analysis']
    for field in ['name_sayt','name_sayt._2gram','name_sayt._3gram','name_sayt._index_prefix']:
        analyze(field,'故宫博物院')
    assert [t['token'] for t in RESULTS['analyze:name_sayt:故宫博物院']]==list('故宫博物院')
    assert [t['token'] for t in RESULTS['analyze:name_sayt._2gram:故宫博物院']]==['故 宫','宫 博','博 物','物 院']
    search('completion-unsafe',['bj-closed','sy-palace','bj-palace','bj-gate','bj-same-a','bj-same-b'],True)
    search('completion',['bj-palace','bj-gate','bj-same-a','bj-same-b'],True)
    search('completion-text-dedup',['bj-palace','bj-gate','bj-same-a'],True)
    search('completion-middle',[],True)
    search('sayt',['bj-gate','bj-infix','bj-palace','bj-same-a','bj-same-b'])
    search('sayt-middle',['bj-palace'])

def pinyin():
    assert [t['token'] for t in analyze('name','GuGong')]==['gugong']
    assert [t['token'] for t in analyze('pinyin_full','GuGong')]==['gugong']
    # Normalization is not transliteration: the keyword field leaves Chinese intact.
    assert [t['token'] for t in analyze('pinyin_full','故宫')]==['故宫']
    search('main-pinyin',[])
    expected=['bj-garden','bj-gate','bj-palace','bj-same-a','bj-same-b']
    search('pinyin',expected);search('initials',expected)

def fuzzy():
    for name,expected in [('exact-typo',[]),('fuzzy-long',['bj-pond','bj-temple']),('fuzzy-short',['bj-river','bj-west']),
            ('fuzzy-auto-short',[]),('guarded-short',[]),('guarded-long',['bj-pond','bj-temple']),
            ('sayt-typo',['bj-garden','bj-pond','bj-temple']),('sayt-final-typo',[])]:search(name,expected)
    for slug in ['sayt-typo','sayt-final-typo']:
        r=call('POST','/'+INDEX+'/_validate/query?rewrite=true&explain=true',{'query':load(slug)['query']})
        assert r['valid'] and r['_shards']['failed']==0
        RESULTS[slug+':rewrite']=r['explanations'][0]['explanation']
    search('completion',['bj-palace','bj-gate','bj-same-a','bj-same-b'],True)
    assert call('POST','/'+INDEX+'/_update/bj-gate',load('close-gate'))['result']=='updated'
    r=call('GET','/'+INDEX+'/_doc/bj-gate');assert r['_source']['status']=='closed'
    assert r['_source']['suggest']['contexts']['scope']==['BJ|closed']
    search('completion',['bj-palace','bj-gate','bj-same-a','bj-same-b'],True)
    refresh()
    search('completion',['bj-palace','bj-same-a','bj-same-b'],True)
    search('sayt',['bj-infix','bj-palace','bj-same-a','bj-same-b'])

def canonical(x):
    if isinstance(x,list):return [canonical(v) for v in x]
    if not isinstance(x,dict):return x
    if set(x)=={'context'}:return x['context']
    x={k:canonical(v) for k,v in x.items()}
    if 'term' in x:
        x['term']={k:v['value'] if isinstance(v,dict) and set(v)=={'value'} else v for k,v in x['term'].items()}
    if 'sort' in x:
        x['sort']=[{k:v['order'] if isinstance(v,dict) and set(v)=={'order'} else v for k,v in s.items()} for s in x['sort']]
    if isinstance(x.get('track_total_hits'),dict):x['track_total_hits']=x['track_total_hits'].get('enabled')
    return x

def verify_java(input, expected):
    r=call('POST','/api/attractions/suggestions',input,app=True)
    assert r['conditions']==input and r['normalizedQ']==input['q'].strip().lower()
    actual=call('POST','/'+INDEX+'/_search',r['esRequest'])
    suggest=input['mode']=='completion'
    rows=options(actual) if suggest else hits(actual)
    by_id={}
    for h in rows:
        src=h['_source'];id=h['_id']
        by_id.setdefault(id,{'id':id,'name':src['name'],'pinyinFull':src['pinyin_full'],'pinyinInitials':src['pinyin_initials'],
            'cityCode':src['city_code'],'ticketPriceFen':src['ticket_price_fen'],'currency':src['currency'],'status':src['status'],
            'score':h['_score'],'suggestionText':h['text'] if suggest else None,'sortValues':[] if suggest else h['sort']})
    assert r['items']==list(by_id.values()),r
    assert [i['id'] for i in r['items']]==expected,(input,r,expected)
    assert r['rawCandidateCount']==len(rows) and r['returnedCount']==len(by_id) and r['deduplication']=='business-id'
    assert r['candidateLimit']==(10 if suggest else 20)
    if suggest: assert r['total'] is None and r['relation']=='not_available'
    else: assert r['total']==actual['hits']['total']['value'] and r['relation']==actual['hits']['total']['relation']
    # Typed Java response is reserialized, may emit optional defaults; compare complete meaningful hit fields.
    java_rows=options(r['esResponse']) if suggest else hits(r['esResponse'])
    assert [(h['_id'],h['_source'],h['_score'],h.get('sort'),h.get('text')) for h in java_rows]==[(h['_id'],h['_source'],h['_score'],h.get('sort'),h.get('text')) for h in rows]
    RESULTS['Java:'+input['mode']+':'+input['q']+':'+input['cityCode']]=expected
    return r

def java_check():
    tests=[('completion',['bj-palace','bj-same-a','bj-same-b']),('middle',['bj-palace']),
        ('pinyin',['bj-garden','bj-palace','bj-same-a','bj-same-b']),('initials',['bj-garden','bj-palace','bj-same-a','bj-same-b']),
        ('typo',['bj-pond','bj-temple']),('short',['bj-river','bj-west']),('guarded',[]),('exact',[]),('city',['sy-palace']),
        ('guarded-long',['bj-pond','bj-temple']),('sayt',['bj-infix','bj-palace','bj-same-a','bj-same-b'])]
    for slug,wanted in tests:verify_java(load('input-'+slug),wanted)

def cleanup():
    call('DELETE','/'+INDEX,expected=(200,404))
    call('GET','/'+INDEX,expected=404)

if __name__=='__main__':
    {'prepare':prepare,'pinyin':pinyin,'fuzzy':fuzzy,'java':java_check,'cleanup':cleanup}[sys.argv[1]]()
