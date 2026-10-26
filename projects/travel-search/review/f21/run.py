#!/usr/bin/env python3
"""Author evidence runner. Reader uses labs/f21 scripts or manual requests."""
import contextlib,copy,datetime,hashlib,importlib.util,json,pathlib,traceback
P=pathlib.Path(__file__).resolve().parents[2];HERE=P/'review/f21'
s=importlib.util.spec_from_file_location('f21lab',P/'labs/f21/lab.py');lab=importlib.util.module_from_spec(s);s.loader.exec_module(lab)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F21 only; final Java jar / real ES9.4.0 / two named-cleanup rounds','rounds':[]}
def phase(folder,name,action):
 start=len(lab.CALLS)
 with (folder/(name+'.jsonl')).open('w') as out,contextlib.redirect_stdout(out):value=action()
 return {'file':str((folder/(name+'.jsonl')).relative_to(P)),'requests':len(lab.CALLS)-start},value

def extras():
 docs=json.loads((P/'data/f21/attractions.json').read_text())
 for d in docs:assert lab.call('GET','/'+lab.INDEX+'/_doc/'+d['attraction_id'])['_source']==d
 lab.call('PUT','/'+lab.INDEX,lab.load('index'),expected=400)
 r=lab.call('POST','/'+lab.INDEX+'/_bulk',(P/'data/f21/attractions.ndjson').read_text(),ndjson=True)
 assert r['errors'] and len(r['items'])==14 and all(x['create']['status']==409 for x in r['items'])
 base=lab.load('input-sum')
 bad=[('q',''),('q',' '*3),('q','西'*61),('q',None),('cityCode','XX'),('cityCode',None),
 ('maxPriceFen',-1),('maxPriceFen',1.5),('maxPriceFen',100000001),('maxPriceFen',None),
 ('latitude',91),('latitude',None),('longitude',181),('longitude',None),
 ('radiusKm',0),('radiusKm',-1),('radiusKm',101),('mode','other'),('mode',None),
 ('sortMode','bad'),('sortMode',None),('explainId','hz-absent'),('explainId','../hz-near'),('explainId',None)]
 for key,value in bad:
  i=dict(base);i[key]=value
  assert lab.call('POST','/api/attractions/decay-search',i,app=True,expected=400)['code']=='INVALID_DECAY_INPUT'
 lab.call('POST','/'+lab.INDEX+'/_update/hz-far',{'doc':{'name':None}});lab.call('POST','/'+lab.INDEX+'/_refresh')
 assert lab.call('POST','/api/attractions/decay-search',base,app=True,expected=502)['code']=='SEARCH_INCOMPLETE'
 lab.call('PUT','/'+lab.INDEX+'/_doc/hz-far',docs[0]);lab.call('POST','/'+lab.INDEX+'/_refresh')
 assert lab.call('POST','/api/attractions/decay-search',base,app=True)['items'][0]['id']=='hz-near'
 assert lab.call('POST','/api/attractions/decay-search',dict(base,q='！！！'),app=True)['total']==0
 # Exact fixed-millisecond eligibility: origin itself allowed, one millisecond later excluded.
 for date,count in [('2026-10-01T00:00:00.000Z',10),('2026-10-01T00:00:00.001Z',9)]:
  lab.call('POST','/'+lab.INDEX+'/_update/hz-future',{'doc':{'verified_at':date}});lab.call('POST','/'+lab.INDEX+'/_refresh')
  assert lab.call('POST','/api/attractions/decay-search',base,app=True)['total']==count
 lab.call('PUT','/'+lab.INDEX+'/_doc/hz-future',next(d for d in docs if d['attraction_id']=='hz-future'));lab.call('POST','/'+lab.INDEX+'/_refresh')

try:
 for number in [1,2]:
  folder=HERE/('round-'+str(number));folder.mkdir(exist_ok=True);lab.RESULTS.clear()
  row={'round':number,'cleanup_before':phase(folder,'cleanup-before',lab.cleanup)[0],'teaching':[]}
  row['teaching'].append(phase(folder,'01-decay',lab.prepare)[0])
  if number==2:
   row['same_java_process_recovery']=phase(folder,'recovery',lambda:lab.call('POST','/api/attractions/decay-search',lab.load('input-sum'),app=True))[0]
  for name,action in [('02-combine',lab.scoring),('03-sort',lab.edges),('04-java',lab.java_check)]:row['teaching'].append(phase(folder,name,action)[0])
  row['additional']=phase(folder,'additional',extras)[0]
  row['cleanup_after']=phase(folder,'cleanup-after',lab.cleanup)[0]
  if number==1:
   row['missing_index']=phase(folder,'missing-index',lambda:lab.call('POST','/api/attractions/decay-search',lab.load('input-sum'),app=True,expected=502))[0]
  row['summary']=copy.deepcopy(lab.RESULTS);row['teaching_requests']=sum(x['requests'] for x in row['teaching']);assert row['teaching_requests']==88
  record['rounds'].append(row);print('Round',number,'passed:',row['teaching_requests'],'teaching,',row['additional']['requests'],'additional',flush=True)
 a,b=[r['summary'] for r in record['rounds']];lab.same(a,b)
 record['two_round_comparison']='fixed IDs/order/scores/decay components and all sort values and Java summaries match; internal doc ordinals excluded from summary'
 record['status']='passed'
 # Derived teaching summaries, kept separate from full raw responses.
 (HERE/'ranking-summary.json').write_text(json.dumps({k:v for k,v in a.items() if k in lab.EXPECTED},ensure_ascii=False,indent=2)+'\n')
 (HERE/'explain-summary.json').write_text(json.dumps({k:a[k] for k in ['components','zero_weight_fallback_score']},ensure_ascii=False,indent=2)+'\n')
except Exception:
 record['status']='failed';record['traceback']=traceback.format_exc();raise
finally:
 record['jar_sha256']=hashlib.sha256((P/'backend/target/travel-search-0.7.0.jar').read_bytes()).hexdigest()
 (HERE/'es-java-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
