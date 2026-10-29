#!/usr/bin/env python3
"""Final scoped F38 receipts and repository checks; does not repeat the database cases."""
import datetime,gzip,hashlib,json,pathlib,subprocess
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search';O=P/'review/f38'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks=[]
 commands=[['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['git','diff','--check'],['git','diff','--cached','--check'],['bash','-n','projects/travel-search/labs/f38/java.sh','projects/travel-search/labs/f38/requests.sh'],['python3','-m','py_compile','projects/travel-search/labs/f38/lab.py']+['docs/framework-review/20261029-f38-binlog/'+n+'.py' for n in ['reading-review','supplement-review','observe-shell','follow-review','create-contacts','final-checks']]]
 for args in commands:
  r=subprocess.run(args,cwd=R,text=True,capture_output=True);checks.append(dict(command=args,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stdout+r.stderr
 for run in ['run-02','run-03']:
  s=json.loads((O/run/'summary.json').read_text());assert s['passed'] and s['cases']==3 and s['kafka_event_count']==11 and s['consumer_final']['committed_next']==11
  h=[json.loads(s) for s in (O/run/'http.jsonl').read_text().splitlines()]
  lesson=[x for x in h if x['case']!='identity'];assert len(lesson)==41 and sum(x['base'].endswith(':20238') for x in lesson)==26 and sum(x['base'].endswith(':18238') for x in lesson)==10 and sum(x['base'].endswith(':18088') for x in lesson)==5
  applied=[]
  for file in ['c01-apply','c02-change-apply','c02-delete-apply','c03-resume-apply']:
   applied += [e for e in json.loads((O/run/(file+'.json')).read_text()) if e['kind']=='applied' and e['result']!='tombstone']
  assert len(applied)==9
 for name in ['follow/summary','cleanup-final/summary','down/summary','shutdown']:
  assert json.loads((O/(name+'.json')).read_text())['passed'],name
 content=json.loads((D/'content-review.json').read_text());assert content['passed']
 http=json.loads((D/'http-review.json').read_text());assert http['passed'] and len(http['copies'])==content['page_statistics']['code_blocks']==23 and http['details_toggled']==19 and len(http['viewports'])==12
 assert json.loads((D/'supplement-review.json').read_text())['passed']
 assert json.loads((D/'visual-review.json').read_text())['passed']
 gen=json.loads((R/'framework/diagrams/f38/generation.json').read_text());assert gen['passed']
 for name,digest in gen['sha256'].items():assert sha(R/name)==digest,name
 # Compare actual secrets privately, including compressed logs; do not emit their values.
 secret_dir=P/'infra/f38/.local';secrets=[(secret_dir/'mysql-password.txt').read_text().strip(),(secret_dir/'cdc.properties').read_text().strip().split('=',1)[1]]
 candidates=[R/n for n in ['STATUS.md','PLAN.md','FRAMEWORK_STANDARD.md','docs/framework-lesson-prompt.md','framework/f37.html','framework/f38.html','framework/index.html','projects/travel-search/.gitignore','projects/travel-search/README.md','projects/travel-search/infra/f38/compose.yaml']]
 for folder in [D,O,P/'labs/f38',P/'cdc/f38',P/'data/f38',P/'search/f38',R/'framework/diagrams/f38']:
  candidates.extend(f for f in folder.rglob('*') if f.is_file() and '__pycache__' not in f.parts and 'target' not in f.parts)
 for path in candidates:
  raw=gzip.open(path,'rb').read() if path.suffix=='.gz' else path.read_bytes()
  assert all(s.encode() not in raw for s in secrets),'Local secret found in scoped artifact'
 names=['mysql-password.txt','admin.cnf','cdc.cnf','cdc.properties']
 ignored=subprocess.run(['git','check-ignore']+['projects/travel-search/infra/f38/.local/'+n for n in names],cwd=R,text=True,capture_output=True)
 assert ignored.returncode==0 and len(ignored.stdout.splitlines())==4
 assert secret_dir.stat().st_mode&0o777==0o700 and all(f.stat().st_mode&0o777==0o600 for f in secret_dir.iterdir())
 runtime=json.loads((O/'runtime.json').read_text())
 for name,digest in runtime['artifact_sha256'].items():assert sha(P/name)==digest,name
 runtime['kafka_classpath_artifacts']=[dict(name=pathlib.Path(f).name,bytes=pathlib.Path(f).stat().st_size,sha256=sha(pathlib.Path(f))) for f in (P/'labs/f38/target/kafka-classpath.txt').read_text().strip().split(':')]
 (O/'runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n')
 ps=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines();assert not any(n.startswith('es-framework-f38-') for n in ps)
 shutdown=json.loads((O/'shutdown.json').read_text());assert len(shutdown['preserved_named_volumes'])==3 and shutdown['unrelated_container_identity_and_start_unchanged']
 record=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),commands=checks,final_rounds_verified=['run-02','run-03'],http_calls_per_formal_round=41,consumer_writes_per_formal_round=9,credentials_absent_from_scoped_artifacts=True,secrets_ignored_and_modes_verified=True,f38_services_removed=True,preserved_named_volumes=shutdown['preserved_named_volumes'],other_running_containers=ps,passed=True)
 (D/'checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 artifacts=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256={str(p.relative_to(R)):sha(p) for p in candidates if p.suffix not in ['.png','.jpg'] and p.name not in ['checks.json','delivery-artifacts.json']},passed=True)
 (D/'delivery-artifacts.json').write_text(json.dumps(artifacts,ensure_ascii=False,indent=2)+'\n')
 print('F38 final repository, receipts, source hashes, credentials exclusion and scoped shutdown checks passed')
if __name__=='__main__':main()
