#!/usr/bin/env python3
"""Two real F17 rounds with named cleanup, full HTTP receipts and REST/Java parity."""
import contextlib,datetime,hashlib,importlib.util,json,pathlib,traceback
HERE=pathlib.Path(__file__).resolve().parent;PROJECT=HERE.parents[1];ROOT=PROJECT.parents[1]
spec=importlib.util.spec_from_file_location('f17lab',PROJECT/'labs/f17/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F17 ES9.4.0/Lucene10.4.0 stock single node, Boot4/JDK25','rounds':[],'status':'running'}
def logged(name,fn):
 lab.CALLS.clear();lab.RESULTS.clear()
 with (HERE/name).open('w') as f,contextlib.redirect_stdout(f):fn()
 return {'path':str((HERE/name).relative_to(ROOT)),'requests':len(lab.CALLS),'results':dict(lab.RESULTS)}
def extra():
 good=lab.load('input-completion')
 for delta in [{'q':''},{'q':' '},{'q':'x'*61},{'q':None},{'cityCode':'NJ'},{'cityCode':None},{'mode':None},{'mode':'arbitrary'},
               {'q':'g','mode':'pinyin'},{'q':'g'*41,'mode':'pinyin'},{'q':'故宫','mode':'pinyin'},{'q':'gu gong','mode':'pinyin'}]:
  r=lab.call('POST','/api/attractions/suggestions',dict(good,**delta),expected=400,app=True);assert r['code']=='INVALID_SUGGEST_INPUT'
 lab.verify_java(dict(good,q='！！！',mode='sayt'),[])
 lab.verify_java(dict(good,q='  GuGong ',mode='pinyin'),['bj-garden','bj-palace','bj-same-a','bj-same-b'])
 docs=[json.loads(l) for l in (PROJECT/'data/f17/attractions.ndjson').read_text().splitlines()[1::2]]
 for d in docs:
  expected=dict(d)
  if d['attraction_id']=='bj-gate':expected.update(lab.load('close-gate')['doc'])
  assert lab.call('GET','/'+lab.INDEX+'/_doc/'+d['attraction_id'])['_source']==expected
 lab.call('PUT','/'+lab.INDEX,lab.load('index'),expected=400)
 # Real inconsistent projection: changing status alone leaves the old completion scope.
 lab.call('POST','/'+lab.INDEX+'/_update/bj-palace',{'doc':{'status':'closed'}})
 lab.refresh()
 r=lab.call('GET','/'+lab.INDEX+'/_doc/bj-palace');assert r['_source']['status']=='closed' and r['_source']['suggest']['contexts']['scope']==['BJ|open']
 r=lab.call('POST','/api/attractions/suggestions',good,expected=502,app=True);assert r['code']=='SEARCH_INCOMPLETE'
 lab.verify_java(lab.load('input-middle'),[])
 original=next(d for d in docs if d['attraction_id']=='bj-palace')
 assert lab.call('PUT','/'+lab.INDEX+'/_doc/bj-palace',original)['result']=='updated'
 lab.refresh();lab.verify_java(good,['bj-palace','bj-same-a','bj-same-b'])
 # Missing index is a backend rejection, not successful empty candidates.
 lab.call('DELETE','/'+lab.INDEX)
 r=lab.call('POST','/api/attractions/suggestions',good,expected=502,app=True);assert r['code']=='SEARCH_BACKEND_REJECTED'
 lab.call('PUT','/'+lab.INDEX,lab.load('index'))
 r=lab.call('GET','/_cluster/health/'+lab.INDEX+'?wait_for_status=green&timeout=30s');assert not r['timed_out']
 r=lab.call('POST','/'+lab.INDEX+'/_bulk',(PROJECT/'data/f17/attractions.ndjson').read_text(),ndjson=True)
 assert not r['errors'] and len(r['items'])==14 and all(i['create']['result']=='created' for i in r['items'])
 lab.call('POST','/'+lab.INDEX+'/_update/bj-gate',lab.load('close-gate'));lab.refresh()
 lab.verify_java(good,['bj-palace','bj-same-a','bj-same-b'])
 r=lab.call('GET','/'+lab.INDEX+'/_stats/search');assert r['indices'][lab.INDEX]['total']['search']['open_contexts']==0
 lab.RESULTS.update(stale_context_502_and_same_process_recovery=True,missing_index_502_and_same_process_recovery=True,open_contexts=0)
try:
 for number in [1,2]:
  print('F17 round',number,flush=True)
  row={'number':number,'cleanup_before':logged(f'round-{number}-cleanup-before.jsonl',lab.cleanup),'teaching':[]}
  for stage,fn in [('prefix',lab.prepare),('pinyin',lab.pinyin),('fuzzy',lab.fuzzy),('java',lab.java_check)]:
   row['teaching'].append(dict(stage=stage,**logged(f'round-{number}-{stage}.jsonl',fn)))
  row['extra']=logged(f'round-{number}-extra.jsonl',extra)
  row['cleanup_after']=logged(f'round-{number}-cleanup-after.jsonl',lab.cleanup)
  row['teaching_requests']=sum(r['requests'] for r in row['teaching']);row['status']='passed';record['rounds'].append(row)
 assert [v['results'] for v in record['rounds'][0]['teaching']]==[v['results'] for v in record['rounds'][1]['teaching']]
 record['rounds_agree']=True;record['status']='passed'
 record['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder,glob in [('labs/f17','*'),('search/f17','*.json'),('data/f17','*'),('infra/f17','*'),('backend/src/main/java/dev/esweb/travel','Suggest*.java'),('backend/src/main/resources/static','*f17*')] for p in (PROJECT/folder).glob(glob) if p.is_file()}
except BaseException:record['status']='failed';record['error']=traceback.format_exc();raise
finally:(HERE/'execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Two real rounds passed',[(r['teaching_requests'],r['extra']['requests']) for r in record['rounds']])
