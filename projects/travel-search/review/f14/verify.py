#!/usr/bin/env python3
"""Author: two full stock→plugin rounds. Only the F14 node/index is changed."""
import copy,datetime,hashlib,importlib.util,json,pathlib,subprocess,time,traceback,urllib.request
HERE=pathlib.Path(__file__).resolve().parent;PROJECT=HERE.parents[1];ROOT=PROJECT.parents[1]
spec=importlib.util.spec_from_file_location('f14lab',PROJECT/'labs/f14/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
BASE=['docker','compose','-f','infra/f14/compose.yaml'];FULL=BASE+['-f','infra/f14/compose.plugins.yaml']
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F14 only; fixed judgments and packaged analyzers; no quality/performance benchmark','rounds':[],'transitions':[],'status':'running'}
def save(): (HERE/'execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
def command(args):
 r=subprocess.run(args,cwd=PROJECT,text=True,capture_output=True)
 record['transitions'].append({'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});save()
 assert r.returncode==0,args

def switch(plugins):
 command((FULL if plugins else BASE)+['stop','es'])
 command((FULL if plugins else BASE)+['up','-d','--force-recreate','--no-build','es'])
 command(['bash','infra/f14/wait.sh'])

def extra(phase):
 valid={'q':'故宫','cityCode':'BJ','maxPriceFen':10000,'candidate':'standard'}
 if phase=='baseline':
  assert lab.call('POST','/api/attractions/analyzer-search',valid,app=True)['total']==4
  for c in ['smartcn','icu','ik-smart','ik-max']:
   lab.call('POST','/api/attractions/analyzer-search',{**valid,'candidate':c},expected=502,app=True)
  lab.cleanup()
  lab.call('PUT','/'+lab.INDEX,lab.load('search/f14/index-plugins.json'),expected=400)
  lab.call('GET','/'+lab.INDEX,expected=404)
 else:
  for patch in [{'q':''},{'q':'   '},{'q':'故'*61},{'candidate':'custom'},{'cityCode':'HZ'},{'maxPriceFen':-1},{'maxPriceFen':100000001},{'maxPriceFen':1.5},{'q':None},{'candidate':None}]:
   lab.call('POST','/api/attractions/analyzer-search',{**valid,**patch},expected=400,app=True)
  for c in ['standard','smartcn','icu','ik-smart','ik-max']:
   a=lab.call('POST','/api/attractions/analyzer-search',{**valid,'q':'长江','cityCode':'NJ','maxPriceFen':0,'candidate':c},app=True)
   assert [i['id'] for i in a['items']]==([] if c=='ik-smart' else ['nj-bridge'])
   empty=lab.call('POST','/api/attractions/analyzer-search',{**valid,'q':'！！！','candidate':c},app=True)
   assert empty['total']==0 and not empty['queryTokens']
  source=lab.call('GET','/'+lab.INDEX+'/_doc/bj-cafe')['_source']
  assert source==next(d for d in lab.load('data/f14/attractions.json') if d['attraction_id']=='bj-cafe')
  lab.call('POST','/'+lab.INDEX+'/_analyze',{'analyzer':'missing_f14','text':'故宫'},expected=400)
  mapping=lab.call('GET','/'+lab.INDEX+'/_mapping')[lab.INDEX]['mappings']
  assert mapping['properties']['name']['analyzer']=='standard'
  lab.cleanup()
  lab.call('POST','/api/attractions/analyzer-search',valid,expected=502,app=True)
  lab.prepare(True)
  assert lab.call('POST','/api/attractions/analyzer-search',valid,app=True)['total']==4
  lab.cleanup()

try:
 lab.cleanup()
 (HERE/'initial-cleanup.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in lab.CALLS))
 for number in [1,2]:
  lab.CALLS.clear();phases={}
  try:
   switch(False)
   start=len(lab.CALLS);lab.prepare();lab.inventory();matrix=lab.compare();phases['baseline']=len(lab.CALLS)-start
   assert phases['baseline']==20
   extra('baseline')
   switch(True)
   start=len(lab.CALLS);lab.prepare(True);lab.inventory(True);matrix=lab.compare(True);phases['plugins']=len(lab.CALLS)-start
   assert phases['plugins']==64
   start=len(lab.CALLS);lab.java();phases['java_rest']=len(lab.CALLS)-start;assert phases['java_rest']==24
   extra('plugins')
   record['rounds'].append({'round':number,'status':'passed','teaching_calls':sum(phases.values()),'phases':phases,'all_client_calls':len(lab.CALLS),'additional_calls':len(lab.CALLS)-108})
  finally:
   (HERE/f'round-{number}.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in lab.CALLS));save()
 record['status']='passed'
 record['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for pattern in ['projects/travel-search/data/f14/*','projects/travel-search/search/f14/**/*.json','projects/travel-search/labs/f14/*','projects/travel-search/backend/src/main/java/dev/esweb/travel/Analyzer*.java'] for p in ROOT.glob(pattern) if p.is_file()}
except Exception:
 record['status']='failed';record['failure']=traceback.format_exc();raise
finally:save()
print('F14 two stock→plugin rounds passed')
