#!/usr/bin/env python3
"""Author verification: two real, named-cleanup rounds. Requires ES and final Java jar running."""
import contextlib,copy,datetime,hashlib,importlib.util,json,pathlib,traceback
HERE=pathlib.Path(__file__).resolve().parent
P=HERE.parents[1]
spec=importlib.util.spec_from_file_location('f18lab',P/'labs/f18/lab.py')
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
D=P.parents[1]/'docs/framework-review/20261025-f18-bm25'

def phase(label,action):
 before=len(lab.CALLS)
 with (HERE/(label+'.jsonl')).open('w') as out,contextlib.redirect_stdout(out):action()
 return len(lab.CALLS)-before

def extra():
 base=lab.load('input-scored')
 invalid=[('q',None),('q',''),('q',' '),('q','x'*61),('cityCode',None),('cityCode','hz'),
          ('maxPriceFen',-1),('maxPriceFen',1.5),('maxPriceFen',100000001),('mode','boost'),
          ('explainId','hz-unknown'),('explainId',None)]
 for key,value in invalid:
  i=copy.deepcopy(base);i[key]=value
  r=lab.call('POST','/api/attractions/score-search',i,expected=400,app=True)
  assert r['code']=='INVALID_SCORE_INPUT'
 expected=[json.loads(l) for l in (P/'data/f18/attractions.ndjson').read_text().splitlines()[1::2]]
 for d in expected:assert lab.call('GET','/'+lab.INDEX+'/_source/'+d['attraction_id'])==d
 lab.call('PUT','/'+lab.INDEX,lab.load('index'),expected=400)
 lab.call('DELETE','/'+lab.INDEX)
 r=lab.call('POST','/api/attractions/score-search',base,expected=502,app=True)
 assert r['code']=='SEARCH_BACKEND_REJECTED'
 lab.call('PUT','/'+lab.INDEX,lab.load('index'))
 for file in ['attractions','unrelated']:
  r=lab.call('POST','/'+lab.INDEX+'/_bulk',(P/f'data/f18/{file}.ndjson').read_text(),ndjson=True)
  assert not r['errors']
 lab.refresh()
 lab.verify_java('scored',lab.SCORED)

record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F18 only; all calls real HTTP, no mocks','rounds':[],'java_jar_sha256':hashlib.sha256((P/'backend/target/travel-search-0.7.0.jar').read_bytes()).hexdigest()}
try:
 first=None
 for n in [1,2]:
  lab.RESULTS.clear()
  start=phase(f'round-{n}-cleanup-before',lab.cleanup)
  counts={key:phase(f'round-{n}-{key}',action) for key,action in [('bm25',lab.prepare),('contexts',lab.contexts),('unrelated',lab.unrelated),('java',lab.java_check)]}
  expected_counts={'bm25':21,'contexts':6,'unrelated':10,'java':21}
  assert counts==expected_counts,(counts,expected_counts)
  summary=copy.deepcopy(lab.RESULTS)
  added=phase(f'round-{n}-extra',extra)
  end=phase(f'round-{n}-cleanup-after',lab.cleanup)
  if first is None:first=summary
  else:lab.same(first,summary)
  record['rounds'].append({'round':n,'status':'passed','teaching':counts,'teaching_requests':sum(counts.values()),'extra_requests':added,'cleanup_requests':{'before':start,'after':end},'results':summary})
 record['rounds_agree']=True
 record['status']='passed'
 # Real response excerpts for the lesson, separate from hand-authored expectations.
 rows=[json.loads(l) for l in (HERE/'round-1-bm25.jsonl').read_text().splitlines()]
 before=next(r['response'] for r in rows if r['path'].endswith('/_search'))
 e=next(r['response'] for r in rows if r['path'].endswith('/_explain/hz-short'))
 (HERE/'explain-short.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
 summary={'id':'hz-short','matched':e['matched'],'score':e['explanation']['value'],**lab.terms(e['explanation'])['西湖']}
 (HERE/'explain-short-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 record['sha256']={str(p.relative_to(P.parents[1])):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['data/f18','search/f18','labs/f18'] for p in sorted((P/folder).glob('*')) if p.is_file()}
except Exception:
 record['status']='failed';record['failure']=traceback.format_exc();raise
finally:
 (HERE/'execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Two rounds passed: 58 teaching requests each; complete REST/Java explanations and relative scores verified')
