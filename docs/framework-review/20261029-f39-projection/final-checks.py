#!/usr/bin/env python3
"""F39 delivery checks: static/build/live receipts and exact artifact/secret scope."""
import ast, collections, datetime, gzip, hashlib, json, pathlib, stat, subprocess
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];P=ROOT/'projects/travel-search';R=P/'review/f39'
def read(p):return json.loads(p.read_text())
def check(ok,detail):
 if not ok:raise AssertionError(detail)
def run(args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
 check(p.returncode==0,{'args':args,'stderr':p.stderr,'stdout':p.stdout})
 return {'args':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def main():
 rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[]}
 for args in [['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['bash','-n','projects/travel-search/labs/f39/java.sh','projects/travel-search/labs/f39/requests.sh'],['git','diff','--check']]:rec['commands'].append(run(args))
 python_files=[P/'labs/f39/lab.py',*D.glob('*.py')]
 for p in python_files:ast.parse(p.read_text(),filename=str(p))
 rec['python_syntax']=[str(p.relative_to(ROOT)) for p in python_files]
 gen=read(ROOT/'framework/diagrams/f39/generation.json')
 for name,digest in gen['sha256'].items():check(hashlib.sha256((ROOT/'framework/diagrams/f39'/name).read_bytes()).hexdigest()==digest,name)
 check(all(x['exit_code']==0 for x in gen['runs']),gen)
 rec['diagram_hashes_and_generation']=True
 for key in ['http-review','supplement-review','visual-review','content-review']:
  check(read(D/(key+'.json'))['passed'],key)
 rec['reading_visual_content_receipts']=True
 rec['rounds']=[]
 stages=['initial','shared','transferred','empty-tags','closed','root-deleted','reopened']
 for round in ['02','03']:
  folder=R/('run-'+round);summary=read(folder/'summary.json')
  check(summary['passed'] and summary['kafka_events']==20 and summary['consumer_bulk_requests']==17 and summary['consumer_bulk_items']==20,summary)
  lines=[json.loads(x) for x in (folder/'http.jsonl').read_text().splitlines()]
  teaching=[r for r in lines if r['case']!='identity'];counts=collections.Counter(r['base'] for r in teaching)
  check(len(teaching)==45 and counts=={'http://127.0.0.1:20339':35,'http://127.0.0.1:18339':3,'http://127.0.0.1:18089':7},counts)
  calls=[]
  for stage in stages:
   obs=read(folder/(stage+'-browser.json'));check(obs['passed'] and len(obs['calls'])==4,stage);calls+=obs['calls']
  check(read(folder/'c02-naive-residual.json')['hits']['total']['value']==2,'Negative case')
  check([x['_id'] for x in read(folder/'c02-fixed-night.json')['hits']['hits']]==['p02'],'Fixed case')
  check(summary['final_documents']['p01']['tags']==[] and summary['final_documents']['p02']['tags']==['亲水','夜景'],'Final fields')
  positions=summary['final_positions']
  check({k.rsplit('.',1)[1]:v['committed_next'] for k,v in positions.items()}=={'city':3,'attraction':8,'attraction_tag':9},positions)
  rec['rounds'].append({'round':round,'teaching_http':len(teaching),'consumer_bulk_requests':17,'consumer_bulk_items':20,'browser_searches':len(calls),'independent_rest_replays':len(calls),'passed':True})
 check(read(R/'cleanup-02/summary.json')['passed'] and read(R/'cleanup-final/summary.json')['passed'],'Cleanup receipts')
 for file in ['follow/summary.json','rest-bulk-replay.json','build.json','shutdown.json']:check(read(R/file)['passed'],file)
 check(read(R/'shutdown.json')['existing_container_unchanged'],'Existing container')
 for f in ['backend-build.log.gz','projection-dependencies.log.gz']:check(b'BUILD SUCCESS' in gzip.decompress((R/f).read_bytes()),f)
 rec['follow_rest_build_cleanup_shutdown']=True
 runtime=read(R/'runtime.json')
 for name,digest in runtime['artifact_sha256'].items():check(hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name)
 rec['runtime_source_hashes_current']=True
 dirs=[D,ROOT/'framework/diagrams/f39',P/'cdc/f39',P/'data/f39',P/'search/f39',P/'infra/f39',P/'labs/f39',R]
 files=[p for directory in dirs for p in directory.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.local','target','__pycache__'])]
 shared=['STATUS.md','PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_STANDARD.md','docs/framework-lesson-prompt.md','framework/f38.html','framework/f39.html','framework/index.html','projects/travel-search/.gitignore','projects/travel-search/README.md']
 files+=list(map(lambda f:ROOT/f,shared));files=sorted(set(files))
 secrets_dir=P/'infra/f39/.local'
 check(stat.S_IMODE(secrets_dir.stat().st_mode)==0o700,'Secret directory mode')
 values=[]
 for f in secrets_dir.iterdir():
  check(stat.S_IMODE(f.stat().st_mode)==0o600,'Secret file mode')
  run(['git','check-ignore',str(f.relative_to(ROOT))])
  content=f.read_text().strip()
  values.append(content if f.name=='pg-password.txt' else dict(x.split('=',1) for x in content.splitlines())['password'])
 for file in files:
  data=file.read_bytes()
  if file.suffix=='.gz':data+=gzip.decompress(data)
  check(not any(value.encode() in data for value in values),'Actual secret leaked in '+str(file.relative_to(ROOT)))
 check(len(values)==3,'Three secrets')
 rec['actual_secrets_excluded_ignored_correct_modes']=True
 rec['scoped_file_count']=len(files);rec['passed']=True
 (D/'checks.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
 files=sorted(set(files+[D/'checks.json']))
 artifacts={str(f.relative_to(ROOT)):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files if f.name!='delivery-artifacts.json'}
 (D/'delivery-artifacts.json').write_text(json.dumps({'at':rec['at'],'scope':'F39 and necessary navigation/progress; excludes local credentials and build output','artifacts':artifacts},ensure_ascii=False,indent=2)+'\n')
 print('F39 final checks passed:',len(artifacts),'scoped artifacts')
if __name__=='__main__':main()
