#!/usr/bin/env python3
"""Actual F25 HTTP receipts; manually specified ID/reason/price expectations."""
import argparse, copy, datetime, json, os, pathlib, urllib.error, urllib.request
HERE=pathlib.Path(__file__).resolve().parent; PROJECT=HERE.parents[1]
DATA=PROJECT/'data/f25'; SEARCH=PROJECT/'search/f25'; INDEX='tut-f25-offers'
ES=os.environ.get('ES_URL','http://127.0.0.1:19225').rstrip('/')
APP=os.environ.get('APP_URL','http://127.0.0.1:18081').rstrip('/')
LOG=None; COUNT=0
EXPECTED={
 'two-nights':{'o01':70000,'o04':65000,'o10':90000},
 'two-rooms':{'o01':140000,'o10':180000},
 'three-nights':{'o04':95000,'o05':75000,'o06':140000,'o10':135000},
 'one-night':{'o01':30000,'o02':10000,'o03':20000,'o04':25000,'o06':60000,'o10':45000,'o12':30000}}
REASONS={
 'two-nights':{'o02':'MISSING_NIGHT','o03':'SOLD_OUT','o05':'MIN_STAY','o06':'BUDGET_EXCEEDED','o12':'MISSING_PRICE'},
 'two-rooms':{'o02':'MISSING_NIGHT','o03':'SOLD_OUT','o04':'STOCK_SHORTAGE','o05':'MIN_STAY','o06':'BUDGET_EXCEEDED','o12':'MISSING_PRICE'},
 'three-nights':{'o01':'SOLD_OUT','o02':'MISSING_NIGHT','o03':'SOLD_OUT','o12':'MISSING_PRICE'},
 'one-night':{'o05':'MIN_STAY'}}
def require(ok, detail):
 if not ok: raise AssertionError(detail)
def read(p):return json.loads(p.read_text())
def request(method,path,body=None,status=200,app=False):
 global COUNT
 raw=body.encode() if isinstance(body,str) else json.dumps(body,ensure_ascii=False).encode() if body is not None else None
 url=(APP if app else ES)+path
 req=urllib.request.Request(url,data=raw,method=method,headers={'Content-Type':'application/x-ndjson' if '_bulk' in path else 'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=40) as r: actual=r.status; payload=r.read().decode()
 except urllib.error.HTTPError as e: actual=e.code; payload=e.read().decode()
 result=json.loads(payload);COUNT+=1
 if LOG:
  with LOG.open('a') as f:f.write(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),n=COUNT,method=method,url=url,request=body,status=actual,response=result),ensure_ascii=False)+'\n')
 require(actual in (status if isinstance(status,list) else [status]),dict(path=path,expected=status,actual=actual,response=result))
 return result
def search(q):
 r=request('POST','/'+INDEX+'/_search',q)
 require(not r['timed_out'] and r['_shards']['failed']==0 and r['hits']['total']['relation']=='eq','complete search');return r
def normalized(x):
 if isinstance(x,list):return [normalized(v) for v in x]
 if isinstance(x,dict):return {k:normalized(v) for k,v in x.items() if not (k in ['_score','max_score'] and v is None)}
 return x
def prepare():
 v=request('GET','/');require(v['version']['number']=='9.4.0' and v['version']['lucene_version']=='10.4.0','ES/Lucene')
 plugins=request('GET','/_nodes/plugins');require(all(not n['plugins'] for n in plugins['nodes'].values()),'no plugins')
 schema=read(SEARCH/'index.json');request('PUT','/'+INDEX,schema)
 h=request('GET','/_cluster/health/'+INDEX+'?wait_for_status=green&timeout=30s');require(not h['timed_out'] and h['number_of_nodes']==1 and h['status']=='green','health')
 b=request('POST','/'+INDEX+'/_bulk',(DATA/'summaries.ndjson').read_text());require(not b['errors'] and len(b['items'])==12 and all(i['create']['result']=='created' for i in b['items']),'12created')
 request('POST','/'+INDEX+'/_refresh');require(request('GET','/'+INDEX+'/_count')['count']==12,'12roots')
 require(request('GET','/'+INDEX+'/_mapping')[INDEX]['mappings']==schema['mappings'],'mapping exact')
 settings=request('GET','/'+INDEX+'/_settings')[INDEX]['settings']['index'];require(all(settings[k]==str(v) for k,v in schema['settings'].items()),'settings')
 summaries=read(DATA/'summaries.json');docs=request('POST','/'+INDEX+'/_mget',{'ids':[s['offer_id'] for s in summaries]})['docs']
 require(all(d['found'] and d['_source']==s for d,s in zip(docs,summaries)),'all summary source')
 return {'roots':12,'bulk_created':12,'mapping_settings_all_source':'exact'}
def candidates():
 r=search(read(SEARCH/'two-nights.json'));ids=[h['_id'] for h in r['hits']['hits']]
 require(ids==['o01','o02','o03','o04','o05','o06','o10','o12'],'8 candidate offers')
 for id in ['o02','o03']:
  s=request('GET','/'+INDEX+'/_doc/'+id)['_source'];require(s['window_start']=='2026-11-01' and s['window_end_exclusive']=='2026-11-04' and s['max_available_rooms']==3,'extrema not continuity')
 return {'ids':ids,'false_positive_summaries':['o02 missing Nov2','o03 zero Nov2'],'naive_min_times_nights_o01':60000,'actual_two_night_one_room_o01':70000}
def verify(name,r):
 i=read(SEARCH/(name+'-input.json'));require(r['conditions']==i and r['snapshotId']=='f25-20261026-v1','input/snapshot')
 require(r['esRequest']==read(SEARCH/(name+'.json')),'whole Java DSL == canonical REST')
 replay=search(r['esRequest']);require(normalized(replay['hits'])==r['esResponse']['hits'],'replayed all hits/source/order/sort/total; only null scoring omitted')
 expected_ids=['o01','o02','o03','o04','o05','o06','o10','o12']
 require(r['candidateTotal']==8 and [d['offerId'] for d in r['decisions']]==expected_ids,'all eight in stable ID order')
 require({d['offerId']:d['totalMinor'] for d in r['decisions'] if d['reason']=='ACCEPTED'}==EXPECTED[name],'manual accepted prices')
 require({d['offerId']:d['reason'] for d in r['decisions'] if d['reason']!='ACCEPTED'}==REASONS[name],'manual rejected reasons')
 require(r['acceptedTotal']==len(EXPECTED[name]),'accepted count is offer count')
 table={o['summary']['offer_id']:o for o in read(DATA/'stay-table.json')['offers']}
 days=[(datetime.date.fromisoformat(i['checkIn'])+datetime.timedelta(days=n)).isoformat() for n in range((datetime.date.fromisoformat(i['checkOut'])-datetime.date.fromisoformat(i['checkIn'])).days)]
 for d in r['decisions']:
  o=table[d['offerId']];bydate={row['date']:row for row in o['nights']}
  require(d['nights']==[dict(date=day,availableRooms=bydate.get(day,{}).get('available_rooms'),priceMinor=bydate.get(day,{}).get('price_minor'),minStayArrival=bydate.get(day,{}).get('min_stay_arrival')) for day in days],'every nightly field, checkout excluded')
  s=o['summary'];require([d[k] for k in ['hotelId','hotelName','roomId','planId','currency']]==[s[k] for k in ['hotel_id','hotel_name','room_id','rate_plan_id','currency']],'identity no stitching')
  if d['reason']=='ACCEPTED':require(d['totalMinor']==sum(n['priceMinor']*i['rooms'] for n in d['nights']),'all nights times room count')
  if d['reason'] not in ['ACCEPTED','BUDGET_EXCEEDED']:require(d['totalMinor'] is None,'no partial total presented')
 if name=='two-nights':
  require(r['decisions'][0]['nights'][1]['minStayArrival']==5 and r['decisions'][0]['reason']=='ACCEPTED','min stay only on arrival')
  require(r['decisions'][5]['totalMinor']==130000,'budget for whole stay')
 return {'scenario':name,'candidate_ids':expected_ids,'accepted_minor':EXPECTED[name],'rejected':REASONS[name],'nights':days,'complete_REST_Java_replay':True}
def scenario(name):return verify(name,request('POST','/api/stay/inspect',read(SEARCH/(name+'-input.json')),app=True))
def stays():return {'reports':[scenario('two-nights')],'java_internal_searches':1}
def variations():return {'reports':[scenario(n) for n in ['two-rooms','three-nights','one-night']],'java_internal_searches':3}
def errors():
 request('PUT','/'+INDEX,read(SEARCH/'index.json'),status=400)
 b=request('POST','/'+INDEX+'/_bulk',(DATA/'summaries.ndjson').read_text());require(b['errors'] and len(b['items'])==12 and all(i['create']['status']==409 for i in b['items']),'12conflicts')
 valid=read(SEARCH/'two-nights-input.json')
 bad=[{},dict(valid,checkOut=valid['checkIn']),dict(valid,checkIn='2026-10-31'),dict(valid,checkOut='2026-11-05'),dict(valid,checkIn='2026-02-30'),dict(valid,rooms=0),dict(valid,rooms=1.5),dict(valid,adultsPerRoom=5),dict(valid,budgetMinor=-1),dict(valid,budgetMinor=None)]
 for body in bad:request('POST','/api/stay/inspect',body,status=400,app=True)
 original=read(DATA/'summaries.json')[0]; altered=dict(original,snapshot_id='wrong')
 request('PUT','/'+INDEX+'/_doc/o01',altered);request('POST','/'+INDEX+'/_refresh')
 r=request('POST','/api/stay/inspect',valid,status=502,app=True);require(r['code']=='SEARCH_INCOMPLETE','snapshot mismatch blocked')
 request('PUT','/'+INDEX+'/_doc/o01',original);request('POST','/'+INDEX+'/_refresh');scenario('two-nights')
 # Exercise the size100 completeness guard before any unknown offer is projected.
 bulk=''
 for n in range(101):bulk+=json.dumps({'create':{'_id':f'probe{n:03d}'}})+'\n'+json.dumps(dict(original,offer_id=f'probe{n:03d}'))+'\n'
 b=request('POST','/'+INDEX+'/_bulk',bulk);require(not b['errors'],'candidate limit fixtures');request('POST','/'+INDEX+'/_refresh')
 r=request('POST','/api/stay/inspect',valid,status=502,app=True);require(r['code']=='SEARCH_INCOMPLETE','truncated candidate set blocked')
 q=read(SEARCH/'two-nights.json');r=search(q);require(r['hits']['total']=={'value':109,'relation':'eq'} and len(r['hits']['hits'])==100,'109total100returned')
 b=request('POST','/'+INDEX+'/_bulk',''.join(json.dumps({'delete':{'_id':f'probe{n:03d}'}})+'\n' for n in range(101)));require(not b['errors'],'remove exact probes')
 request('POST','/'+INDEX+'/_refresh');scenario('two-nights')
 bad_source=dict(original,unexpected='strict');request('PUT','/'+INDEX+'/_doc/bad',bad_source,status=400)
 require(request('GET','/'+INDEX+'/_count')['count']==12,'12 roots restored')
 return {'invalid_inputs':len(bad),'repeat_create_http':400,'repeat_bulk_item_conflicts':12,'snapshot_mismatch':502,'limit_guard':{'total':109,'returned':100,'status':502},'recovery':'exact source/12 roots/default prices restored'}
def cleanup():
 request('DELETE','/'+INDEX,status=[200,404]);request('GET','/'+INDEX,status=404)
 return {'deleted_only':[INDEX]}
def main():
 global LOG
 p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','candidates','stays','variations','errors','cleanup']);p.add_argument('--out',default=os.environ.get('F25_OUT',str(PROJECT/'review/f25/latest')));a=p.parse_args()
 out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True);LOG=out/(a.command+'.jsonl');require(not LOG.exists(),'preserve receipts; use a new F25_OUT')
 result=globals()[a.command]();result.update(status='passed',http=COUNT,at=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/(a.command+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'command':a.command,'http':COUNT,'status':'passed'}))
if __name__=='__main__':main()
