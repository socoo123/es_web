#!/usr/bin/env python3
"""Author's actual F22 final two-round integration record; does not mock ES."""
import datetime,hashlib,importlib.util,json,pathlib,subprocess,traceback
HERE=pathlib.Path(__file__).resolve().parent;P=HERE.parents[1];R=P.parents[1]
spec=importlib.util.spec_from_file_location('f22lab',P/'labs/f22/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def phase(name,fn,directory=HERE):
 lab.COUNT=0;lab.LOG=directory/(name+'.jsonl');lab.LOG.parent.mkdir(parents=True,exist_ok=True);lab.LOG.write_text('')
 result=fn();lab.dump(directory/(name+'.json'),result);return result

def extras():
 rows=[];docs=json.loads((P/'data/f22/attractions.json').read_text())
 r=lab.request('POST','/'+lab.INDEX+'/_mget',{'ids':[d['attraction_id'] for d in docs]});lab.require([d['_source'] for d in r['docs']]==docs,'all 24 complete _source equal')
 lab.request('PUT','/'+lab.INDEX,json.loads((P/'search/f22/index.json').read_text()),status=400)
 r=lab.request('POST','/'+lab.INDEX+'/_bulk',(P/'data/f22/attractions.ndjson').read_text());lab.require(r['errors'] and len(r['items'])==24 and all(x['create']['status']==409 for x in r['items']),'24 per-item409')
 bad=[{},None,{'split':None,'strategy':'baseline'},{'split':'adjust','strategy':None},{'split':'','strategy':'baseline'},{'split':'ADJUST','strategy':'baseline'},{'split':'holdout','strategy':'unknown'},{'split':['adjust'],'strategy':'baseline'},{'split':'future','strategy':'candidate'},{'split':'adjust','strategy':{}}]
 for inp in bad:
  out=lab.request('POST','/api/quality/evaluate',inp,app=True,status=400);lab.require(out['code']=='INVALID_QUALITY_INPUT','invalid400')
 source=next(d for d in docs if d['attraction_id']=='a15')
 lab.request('POST','/'+lab.INDEX+'/_update/a15?refresh=true',{'doc':{'name':None}})
 out=lab.request('POST','/api/quality/evaluate',{'split':'adjust','strategy':'baseline'},app=True,status=502);lab.require(out['code']=='SEARCH_INCOMPLETE','incomplete502')
 lab.request('PUT','/'+lab.INDEX+'/_doc/a15?refresh=true',source)
 out=lab.request('POST','/api/quality/evaluate',{'split':'adjust','strategy':'baseline'},app=True);lab.require(len(out['queries'])==4,'same-process recovery')
 unjudged=dict(docs[0],attraction_id='z-unjudged',name='西湖 夜游',description='西湖 夜游 西湖 夜游 西湖 夜游')
 lab.request('PUT','/'+lab.INDEX+'/_doc/z-unjudged?refresh=true',unjudged,status=201)
 search=lab.request('POST','/'+lab.INDEX+'/_search',lab.query('西湖 夜游','baseline'));lab.require('z-unjudged' in [h['_id'] for h in search['hits']['hits']],'unjudged reaches top10')
 out=lab.request('POST','/api/quality/evaluate',{'split':'adjust','strategy':'baseline'},app=True,status=502);lab.require(out['code']=='SEARCH_INCOMPLETE','unknown grade rejected')
 lab.request('DELETE','/'+lab.INDEX+'/_doc/z-unjudged?refresh=true')
 out=lab.request('POST','/api/quality/evaluate',{'split':'adjust','strategy':'baseline'},app=True);lab.require(out['macro']['ndcg']==0.7682750212453657,'same-process recovered metrics')
 # A deliberately removed hard filter must fail the same externally checked contract.
 bad=lab.query('西湖 夜游','baseline');bad['query']['bool']['filter']=[f for f in bad['query']['bool']['filter'] if 'status' not in f.get('term',{})]
 out=lab.request('POST','/'+lab.INDEX+'/_search',bad)
 try:lab.valid_search(out,lab.selected('adjust')[0])
 except AssertionError:rows.append('missing status filter detected by hard-candidate contract')
 else:raise AssertionError('negative regression probe escaped')
 return {'status':'passed','http':lab.COUNT,'checks':['complete24 source parity','duplicate index400','Bulk24 item409','10 malformed inputs400','name-null502 and refresh recovery','unjudged top10 rejected502 and exact metric recovery',*rows],'limitations':['timeout and partial shard failure not constructed']}

def main():
 summary={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rounds':[],'before':{'jar_sha256':sha(P/'backend/target/travel-search-0.7.0.jar'),'fixture_sha256':sha(P/'data/f22/evaluation.json'),'plan_sha256':sha(P/'data/f22/decision-plan.json')},'scope':'Final jar; original isolated index removed before round1, named cleanup before round2; actual fixed ES/Java HTTP; no mocked responses'}
 try:
  for n in [1,2]:
   directory=HERE/f'round{n}';directory.mkdir(exist_ok=True)
   phase('cleanup-before',lab.cleanup,directory)
   if n==2:
    result=phase('missing-index',lambda:lab.request('POST','/api/quality/evaluate',{'split':'adjust','strategy':'baseline'},app=True,status=502),directory)
    lab.require(result['code']=='SEARCH_BACKEND_REJECTED','missing index502')
   stages={}
   for name,fn in [('prepare',lab.prepare),('adjust',lambda:lab.evaluate('adjust')),('holdout',lambda:lab.evaluate('holdout')),('boundaries',lab.edges),('java',lab.java),('assessment',lambda:lab.evaluate('assessment'))]:
    stages[name]=phase(name,fn,directory);print(f'round{n} {name}: {stages[name]["http"]} HTTP',flush=True)
   extra=phase('extra',extras,directory)
   item={'round':n,'status':'passed','teaching_http':sum(s['http'] for s in stages.values()),'java_internal_searches':16,'extra_http':extra['http'],'stages':{k:v['http'] for k,v in stages.items()},'cleanup_before_http':2,'missing_index_between_rounds':n==2,'jar_sha256':sha(P/'backend/target/travel-search-0.7.0.jar'),'evidence_sha256':{p.name:sha(p) for p in directory.glob('*.jsonl')}}
   lab.require(item['teaching_http']==70,'70 teaching requests');lab.dump(directory/'summary.json',item);summary['rounds'].append(item)
  summary['status']='passed'
 except Exception:
  summary['status']='failed';summary['failure']=traceback.format_exc();raise
 finally:
  lab.dump(HERE/'two-rounds.json',summary)
 lab.dump(HERE/'extra.json',{'status':'passed','rounds':[{"round":n,**json.loads((HERE/f'round{n}/extra.json').read_text())} for n in [1,2]],'missing_index502_and_same_process_recovery':'between round1/round2; round2 Java run uses same final jar process'})
 print('F22 final two rounds passed',flush=True)
if __name__=='__main__':main()
