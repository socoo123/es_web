#!/usr/bin/env python3
"""Two complete, named-cleanup F16 rounds; real endpoints, no mocks."""
import contextlib
import datetime
import hashlib
import importlib.util
import json
import pathlib
import traceback

HERE=pathlib.Path(__file__).resolve().parent
PROJECT=HERE.parents[1]
ROOT=PROJECT.parents[1]
spec=importlib.util.spec_from_file_location('f16lab',PROJECT/'labs/f16/lab.py')
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F16 real single-node ES9.4.0/ICU9.4.0 + Boot4/JDK25','rounds':[],'sha256':{},'status':'running'}
def logged(name,fn):
 lab.CALLS.clear();lab.RESULTS.clear()
 with (HERE/name).open('w') as f,contextlib.redirect_stdout(f):fn()
 return {'path':str((HERE/name).relative_to(ROOT)),'requests':len(lab.CALLS),'results':dict(lab.RESULTS)}
def extra():
 good={'q':'紫禁城','cityCode':'BJ','maxPriceFen':10000,'mode':'aliases'}
 for delta in [{'q':''},{'q':' '},{'q':'x'*61},{'cityCode':'NJ'},{'maxPriceFen':-1},
               {'maxPriceFen':0.5},{'maxPriceFen':100000001},{'mode':'arbitrary'},{'q':None},{'mode':None}]:
  r=lab.call('POST','/api/attractions/synonym-search',dict(good,**delta),expected=400,app=True)
  assert r['code']=='INVALID_SYNONYM_INPUT'
 for delta,wanted in [({'q':'！！！'},[]),({'mode':'graph','maxPriceFen':0},['bj-traditional'])]:
  r=lab.call('POST','/api/attractions/synonym-search',dict(good,**delta),app=True)
  assert [i['id'] for i in r['items']]==wanted
 lines=(PROJECT/'data/f16/attractions.ndjson').read_text().splitlines()
 for line in lines[1::2]:
  expected=json.loads(line)
  if expected['attraction_id']=='bj-palace': expected['aliases']=['紫禁城','皇家旧宫']
  r=lab.call('GET','/'+lab.INDEX+'/_doc/'+expected['attraction_id'])
  assert r['_source']==expected
 lab.call('PUT','/'+lab.INDEX,lab.load('index'),expected=400)
 lab.call('DELETE','/'+lab.INDEX)
 r=lab.call('POST','/api/attractions/synonym-search',good,expected=502,app=True)
 assert r['code']=='SEARCH_BACKEND_REJECTED'
 # Restore exactly this lesson, without restarting Java or overwriting another index.
 assert lab.call('PUT','/'+lab.INDEX,lab.load('index'))['acknowledged']
 r=lab.call('GET','/_cluster/health/'+lab.INDEX+'?wait_for_status=green&timeout=30s');assert not r['timed_out'] and r['status']=='green'
 r=lab.call('POST','/'+lab.INDEX+'/_bulk',(PROJECT/'data/f16/attractions.ndjson').read_text(),ndjson=True)
 assert not r['errors'] and all(i['create']['result']=='created' for i in r['items'])
 lab.call('POST','/'+lab.INDEX+'/_update/bj-palace',lab.load('alias-update'))
 lab.refresh()
 r=lab.call('POST','/api/attractions/synonym-search',good,app=True)
 assert [i['id'] for i in r['items']]==['bj-palace','bj-wall']
 r=lab.call('GET','/'+lab.INDEX+'/_stats/search')
 assert r['indices'][lab.INDEX]['total']['search']['open_contexts']==0
 lab.RESULTS['restored_after_502_in_same_Java_process']=True
 lab.RESULTS['open_contexts']=0
try:
 for number in [1,2]:
  print('F16 round',number,flush=True)
  row={'number':number,'cleanup_before':logged(f'round-{number}-cleanup-before.jsonl',lab.cleanup),'teaching':[]}
  for stage,fn in [('aliases',lab.prepare),('graph',lab.graph),('changes',lab.changes),('java',lab.java_check)]:
   row['teaching'].append(dict(stage=stage,**logged(f'round-{number}-{stage}.jsonl',fn)))
  row['extra']=logged(f'round-{number}-extra.jsonl',extra)
  row['cleanup_after']=logged(f'round-{number}-cleanup-after.jsonl',lab.cleanup)
  row['teaching_requests']=sum(v['requests'] for v in row['teaching'])
  row['status']='passed';record['rounds'].append(row)
 # Deterministic observations compare token position/length/offset/type and all ID sequences.
 assert [r['results'] for r in record['rounds'][0]['teaching']]==[r['results'] for r in record['rounds'][1]['teaching']]
 record['rounds_agree']=True
 for directory,pattern in [('search/f16','*.json'),('data/f16','*'),('infra/f16','*'),('labs/f16','*'),('backend/src/main/java/dev/esweb/travel','Synonym*.java'),('backend/src/main/resources/static','*f16*')]:
  for p in (PROJECT/directory).glob(pattern):
   if p.is_file():record['sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 record['status']='passed'
except BaseException:
 record['status']='failed';record['error']=traceback.format_exc();raise
finally:
 (HERE/'execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F16 two complete rounds passed',[(r['teaching_requests'],r['extra']['requests']) for r in record['rounds']])
