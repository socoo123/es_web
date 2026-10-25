#!/usr/bin/env python3
"""Author evidence runner. Reader uses labs/f19 scripts or manual requests."""
import contextlib,copy,datetime,hashlib,importlib.util,json,pathlib,traceback
P=pathlib.Path(__file__).resolve().parents[2];HERE=P/'review/f19'
s=importlib.util.spec_from_file_location('f19lab',P/'labs/f19/lab.py');lab=importlib.util.module_from_spec(s);s.loader.exec_module(lab)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F19 only; final Java jar / real ES9.4.0 / two named-cleanup rounds','rounds':[]}
def phase(folder,name,action):
 start=len(lab.CALLS)
 with (folder/(name+'.jsonl')).open('w') as out,contextlib.redirect_stdout(out):value=action()
 return {'file':str((folder/(name+'.jsonl')).relative_to(P)),'requests':len(lab.CALLS)-start},value

def extras():
 docs=json.loads((P/'data/f19/attractions.json').read_text())
 for d in docs:assert lab.call('GET','/'+lab.INDEX+'/_doc/'+d['attraction_id'])['_source']==d
 lab.call('PUT','/'+lab.INDEX,lab.load('index'),expected=400)
 base=lab.load('input-tuned')
 bad=[('q',''),('q',' '*3),('q','西'*61),('q',None),('cityCode','XX'),('cityCode',None),
 ('maxPriceFen',-1),('maxPriceFen',1.5),('maxPriceFen',100000001),('maxPriceFen',None),
 ('mode','other'),('mode',None),('nameWeight',0),('nameWeight',51),('nameWeight',1.5),('nameWeight',None),
 ('explainId','hz-no-such'),('explainId','../hz-exact'),('explainId',None)]
 for key,value in bad:
  i=dict(base);i[key]=value
  assert lab.call('POST','/api/attractions/weight-search',i,app=True,expected=400)['code']=='INVALID_WEIGHT_INPUT'
 # Corrupt only this course's fixed sample, verify service field contract and same-process restoration.
 lab.call('POST','/'+lab.INDEX+'/_update/hz-exact',{'doc':{'description':None}})
 lab.call('POST','/'+lab.INDEX+'/_refresh')
 assert lab.call('POST','/api/attractions/weight-search',base,app=True,expected=502)['code']=='SEARCH_INCOMPLETE'
 lab.call('PUT','/'+lab.INDEX+'/_doc/hz-exact',docs[0]);lab.call('POST','/'+lab.INDEX+'/_refresh')
 assert lab.call('POST','/api/attractions/weight-search',base,app=True)['items'][0]['id']=='hz-exact'
 i=dict(base,q='！！！')
 assert lab.call('POST','/api/attractions/weight-search',i,app=True)['total']==0

try:
 for number in [1,2]:
  folder=HERE/('round-'+str(number));folder.mkdir(exist_ok=True);lab.RESULTS.clear()
  row={'round':number,'cleanup_before':phase(folder,'cleanup-before',lab.cleanup)[0],'teaching':[]}
  row['teaching'].append(phase(folder,'01-levels',lab.prepare)[0])
  if number==2:
   row['same_java_process_recovery']=phase(folder,'recovery',lambda:lab.call('POST','/api/attractions/weight-search',lab.load('input-tuned'),app=True))[0]
  for name,action in [('02-weights',lab.weights),('03-gates',lab.gates),('04-java',lab.java_check)]:row['teaching'].append(phase(folder,name,action)[0])
  row['additional']=phase(folder,'additional',extras)[0]
  row['cleanup_after']=phase(folder,'cleanup-after',lab.cleanup)[0]
  if number==1:
   row['missing_index']=phase(folder,'missing-index',lambda:lab.call('POST','/api/attractions/weight-search',lab.load('input-tuned'),app=True,expected=502))[0]
  row['summary']=copy.deepcopy(lab.RESULTS);row['teaching_requests']=sum(x['requests'] for x in row['teaching']);assert row['teaching_requests']==92
  record['rounds'].append(row);print('Round',number,'passed:',row['teaching_requests'],'teaching,',row['additional']['requests'],'additional',flush=True)
 a,b=[r['summary'] for r in record['rounds']];lab.same(a,b)
 record['two_round_comparison']='complete token/positions/offsets/stored terms, IDs/order/combiner values and Java summaries match; internal doc ordinals excluded from summary'
 record['status']='passed'
 # Derived teaching summaries, kept separate from full raw responses.
 (HERE/'ranking-summary.json').write_text(json.dumps({k:v for k,v in a.items() if k in lab.EXPECTED},ensure_ascii=False,indent=2)+'\n')
 (HERE/'explain-summary.json').write_text(json.dumps({k:a[k] for k in ['both_combination','exact_contributions']},ensure_ascii=False,indent=2)+'\n')
except Exception:
 record['status']='failed';record['traceback']=traceback.format_exc();raise
finally:
 record['jar_sha256']=hashlib.sha256((P/'backend/target/travel-search-0.7.0.jar').read_bytes()).hexdigest()
 (HERE/'es-java-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
