#!/usr/bin/env python3
"""F12手工实验。打印真实请求/响应，动态使用刚读取的版本；Python标准库。"""
import copy, datetime, json, pathlib, sys, urllib.request, urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[2]
ES='http://127.0.0.1:19200';APP='http://127.0.0.1:18080';GRAD_APP='http://127.0.0.1:18081'
INDEX='tut-f12-attractions';GRAD='tut-f12-graduation';BASE='/api/attractions/changes';RECORD=[]
def load(path):return json.loads((ROOT/path).read_text())
def call(method,path,body=None,*,app=False,graduation=False,expected=200,ndjson=None):
 data=(ROOT/ndjson).read_bytes() if ndjson else None if body is None else json.dumps(body,ensure_ascii=False).encode()
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 req=urllib.request.Request((GRAD_APP if graduation and app else APP if app else ES)+path,data=data,method=method,
                           headers={'Content-Type':'application/x-ndjson' if ndjson else 'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=35) as r:status,raw=r.status,r.read().decode()
 except urllib.error.HTTPError as e:status,raw=e.code,e.read().decode()
 result=json.loads(raw)
 item={'started_at':start,'method':method,'path':path,'target':('graduation-Java' if graduation else 'Java') if app else 'ES',
       'request':ndjson if ndjson else body,'status':status,'response':result}
 RECORD.append(item);print(json.dumps(item,ensure_ascii=False),flush=True)
 if status!=expected:raise RuntimeError(f'{method} {path}: expected {expected}, got {status}')
 return result

def refresh(index=INDEX):assert call('POST',f'/{index}/_refresh')['_shards']['failed']==0
def ids(r):return [h['_id'] for h in r['hits']['hits']]
def search():return call('POST',f'/{INDEX}/_search',load('search/f12/search.json'))
def version(r):return {'seqNo':r['seqNo'],'primaryTerm':r['primaryTerm']}
def es_version(r):return f"if_seq_no={r['_seq_no']}&if_primary_term={r['_primary_term']}"
def restore():
 r=call('POST',f'/{INDEX}/_bulk',ndjson='data/f12/attractions.ndjson')
 assert not r['errors'] and all(i['index']['result'] in ['created','updated'] for i in r['items']);refresh()
def prepare(graduation=False):
 index=GRAD if graduation else INDEX;data='graduation' if graduation else 'attractions';count=8 if graduation else 4
 v=call('GET','/');assert v['version']['number']=='9.4.0' and v['version']['lucene_version']=='10.4.0'
 assert call('PUT',f'/{index}',load('search/f12/index.json'))['acknowledged']
 h=call('GET',f'/_cluster/health/{index}?wait_for_status=green&timeout=30s');assert h['status']=='green' and not h['timed_out']
 r=call('POST',f'/{index}/_bulk',ndjson=f'data/f12/{data}.ndjson')
 assert not r['errors'] and len(r['items'])==count and all(i['index']['result']=='created' for i in r['items'])
 refresh(index);assert call('GET',f'/{index}/_count')['count']==count

def crud():
 restore();assert ids(search())==['d-hz-walk','d-hz-garden','d-hz-boat']
 path=f'/{INDEX}/_doc/d-hz-new';new=load('search/f12/new-document.json')
 assert call('PUT',path,new,expected=201)['result']=='created'
 assert call('GET',path)['_source']==new
 assert 'd-hz-new' not in ids(search())
 refresh();assert ids(search())==['d-hz-walk','d-hz-new','d-hz-garden','d-hz-boat']
 call('PUT',f'/{INDEX}/_create/d-hz-new',new,expected=409)
 # Index is a full replacement. This deliberately incomplete document is a counterexample.
 assert call('PUT',path,{'ticket_price_fen':3500})['result']=='updated'
 assert call('GET',path)['_source']=={'ticket_price_fen':3500}
 assert 'd-hz-new' in ids(search());refresh();assert 'd-hz-new' not in ids(search())
 assert call('PUT',path,load('search/f12/replacement.json'))['result']=='updated'
 refresh();assert 'd-hz-new' in ids(search())
 assert call('POST',f'/{INDEX}/_update/d-hz-garden',load('search/f12/price-patch.json'))['result']=='updated'
 g=call('GET',f'/{INDEX}/_doc/d-hz-garden')['_source'];assert g['ticket_price_fen']==9000 and g['name']=='湖滨花园'
 assert 'd-hz-garden' in ids(search());refresh();assert 'd-hz-garden' not in ids(search())
 call('POST',f'/{INDEX}/_update/d-hz-boat',load('search/f12/close-patch.json'))
 assert call('GET',f'/{INDEX}/_doc/d-hz-boat')['_source']['status']=='closed'
 assert 'd-hz-boat' in ids(search());refresh();assert ids(search())==['d-hz-walk','d-hz-new']
 assert call('DELETE',path)['result']=='deleted';assert not call('GET',path,expected=404)['found']
 assert 'd-hz-new' in ids(search());refresh();assert ids(search())==['d-hz-walk']
 assert call('DELETE',path,expected=404)['result']=='not_found'
 call('POST',f'/{INDEX}/_update/d-hz-new',{'doc':{'status':'closed'}},expected=404)
 restore()

def conflict():
 restore();path=f'/{INDEX}/_doc/d-hz-garden';update=f'/{INDEX}/_update/d-hz-garden'
 a=call('GET',path);b=call('GET',path);assert (a['_seq_no'],a['_primary_term'])==(b['_seq_no'],b['_primary_term'])
 assert call('POST',update+'?'+es_version(a),{'doc':{'ticket_price_fen':6500}})['result']=='updated'
 r=call('POST',update+'?'+es_version(b),{'doc':{'status':'closed'}},expected=409)
 assert r['error']['type']=='version_conflict_engine_exception'
 fresh=call('GET',path);assert fresh['_source']['ticket_price_fen']==6500 and fresh['_source']['status']=='open'
 assert call('POST',update+'?'+es_version(fresh),{'doc':{'status':'closed'}})['result']=='updated'
 old=search();assert next(h for h in old['hits']['hits'] if h['_id']=='d-hz-garden')['_source']['ticket_price_fen']==4500
 refresh();assert ids(search())==['d-hz-walk','d-hz-boat']
 call('DELETE',path+'?'+es_version(a),expected=409)
 fresh=call('GET',path);assert fresh['_source']['ticket_price_fen']==6500 and fresh['_source']['status']=='closed'
 call('DELETE',path+'?'+es_version(fresh));call('GET',path,expected=404)
 restore()

def start(input=None,graduation=False):return call('POST',BASE+'/pages/start',input or load('search/f12/input.json'),app=True,graduation=graduation)
def close(r,graduation=False):return call('POST',BASE+'/pages/close',{'cursor':r['cursor']},app=True,graduation=graduation)
def compare_page(r):
 rest=call('POST','/_search',r['esRequest'])
 assert r['total']==rest['hits']['total']['value'] and r['totalRelation']==rest['hits']['total']['relation']=='eq'
 assert [(x['id'],x['ticketPriceFen'],x['score'],x['sortValues']) for x in r['items']]==[(h['_id'],h['_source']['ticket_price_fen'],h['_score'],h['sort']) for h in rest['hits']['hits']]
 return rest

def java():
 restore();p=BASE+'/d-hz-new';doc=load('search/f12/new-document.json')
 made=call('POST',p+'/create',doc,app=True);assert made['result']=='created'
 call('POST',p+'/create',doc,app=True,expected=409)
 g=call('GET',p,app=True);assert g['document']==call('GET',f'/{INDEX}/_doc/d-hz-new')['_source']==doc
 replaced=call('PUT',p,dict(version(g),document=load('search/f12/replacement.json')),app=True);assert replaced['result']=='updated'
 call('PATCH',p,dict(version(g),ticketPriceFen=4000),app=True,expected=409)
 fresh=call('GET',p,app=True)
 changed=call('PATCH',p,dict(version(fresh),ticketPriceFen=4000),app=True);assert changed['result']=='updated'
 assert call('GET',p,app=True)['document']['name']=='湖滨新展馆（二期）'
 old=start();compare_page(old);assert old['total']==3;close(old)
 call('POST',BASE+'/refresh',app=True)
 view=start();compare_page(view);assert view['total']==4
 rest=call('POST',BASE+'/pages/next',{'cursor':view['cursor'],'afterPage':1,'conditions':load('search/f12/input.json')},app=True);compare_page(rest)
 assert [x['id'] for page in [view,rest] for x in page['items']]==['d-hz-walk','d-hz-new','d-hz-garden','d-hz-boat'];close(view)
 call('DELETE',p,version(fresh),app=True,expected=409)
 latest=call('GET',p,app=True);assert call('DELETE',p,version(latest),app=True)['result']=='deleted'
 call('GET',p,app=True,expected=404);call('POST',BASE+'/refresh',app=True)
 final=start();assert final['total']==3;close(final)

def graduation():
 # Read the task first. This is the after-attempt reference implementation, not the task prompt.
 prepare(True);input=load('search/f12/graduation-input.json')
 first=start(input,True);compare_page(first)
 assert [x['id'] for x in first['items']]==['g-hz-free','g-hz-garden'] and first['total']==3
 path=BASE+'/g-hz-garden';g=call('GET',path,app=True,graduation=True)
 call('PATCH',path,dict(version(g),ticketPriceFen=7000),app=True,graduation=True)
 assert call('GET',f'/{GRAD}/_doc/g-hz-garden')['_source']['ticket_price_fen']==7000
 before=start(input,True);assert before['total']==3;compare_page(before);close(before,True)
 call('POST',BASE+'/refresh',app=True,graduation=True)
 # Existing PIT keeps the original page sequence and original prices.
 second=call('POST',BASE+'/pages/next',{'cursor':first['cursor'],'afterPage':1,'conditions':input},app=True,graduation=True)
 compare_page(second);assert [x['id'] for x in second['items']]==['g-hz-museum'] and not second['hasNext']
 assert first['items'][1]['ticketPriceFen']==4500;close(first,True)
 live=start(input,True);compare_page(live);assert [x['id'] for x in live['items']]==['g-hz-free','g-hz-museum'];close(live,True)
 g=call('GET',BASE+'/g-hz-museum',app=True,graduation=True)
 call('PATCH',BASE+'/g-hz-museum',dict(version(g),status='closed'),app=True,graduation=True)
 call('POST',BASE+'/refresh',app=True,graduation=True)
 live=start(input,True);compare_page(live);assert [x['id'] for x in live['items']]==['g-hz-free'];close(live,True)
 assert call('GET',f'/{GRAD}/_count')['count']==8

if __name__=='__main__':
 scenario=sys.argv[1]
 try:{'prepare':prepare,'crud':crud,'conflict':conflict,'java':java,'graduation':graduation}[scenario]()
 finally:
  if len(sys.argv)>2:pathlib.Path(sys.argv[2]).write_text(json.dumps({'scenario':scenario,'requests':len(RECORD),'operations':RECORD},ensure_ascii=False,indent=2)+'\n')
 print(f'{scenario}: {len(RECORD)} HTTP requests; passed',file=sys.stderr)
