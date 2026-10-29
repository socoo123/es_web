#!/usr/bin/env python3
"""Final F37 repository/delivery checks. Re-running does not re-run the database lab."""
import datetime,gzip,hashlib,json,pathlib,subprocess
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search';O=P/'review/f37'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 checks=[]
 for cmd in [['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['git','diff','--check'],['git','diff','--cached','--check'],['bash','-n','projects/travel-search/labs/f37/java.sh','projects/travel-search/labs/f37/requests.sh'],['python3','-m','py_compile','projects/travel-search/labs/f37/lab.py','docs/framework-review/20261029-f37-wal/follow-review.py','docs/framework-review/20261029-f37-wal/reading-review.py','docs/framework-review/20261029-f37-wal/observe-shell.py','docs/framework-review/20261029-f37-wal/create-contacts.py']]:
  r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);checks.append({'command':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,r.stderr
 for run in ['run-02','run-03']:
  r=json.loads((O/run/'summary.json').read_text());assert r['passed'] and r['cases']==3 and r['kafka_event_count']==11 and r['consumer_final']['committed_next']==11
 for file in ['follow/summary.json','cleanup-final/summary.json','down/summary.json']:
  assert json.loads((O/file).read_text())['passed'],file
 http=json.loads((D/'http-review.json').read_text());assert http['passed'] and len(http['copies'])==22 and len(http['viewports'])==12
 gen=json.loads((R/'framework/diagrams/f37/generation.json').read_text());assert gen['passed']
 for name,value in gen['sha256'].items():assert sha(R/name)==value,name
 # Compare raw local secrets privately; emit no values. This includes compressed build evidence.
 secret_dir=P/'infra/f37/.local';secret_values=[(secret_dir/'pg-password.txt').read_text().strip(),(secret_dir/'cdc.properties').read_text().strip().split('=',1)[1]]
 candidates=[R/'framework/f37.html']
 for directory in [D,O,P/'labs/f37',P/'cdc/f37',P/'data/f37',R/'framework/diagrams/f37',P/'search/f37']:
  candidates += [f for f in directory.rglob('*') if f.is_file() and '__pycache__' not in f.parts and 'target' not in f.parts]
 for path in candidates:
  raw=gzip.open(path,'rb').read() if path.suffix=='.gz' else path.read_bytes()
  assert all(s.encode() not in raw for s in secret_values),'Actual local credential found in artifact'
 ignored=subprocess.run(['git','check-ignore','projects/travel-search/infra/f37/.local/pg-password.txt','projects/travel-search/infra/f37/.local/cdc.properties'],cwd=R,capture_output=True,text=True)
 assert ignored.returncode==0 and len(ignored.stdout.splitlines())==2
 assert secret_dir.stat().st_mode&0o777==0o700
 assert all(f.stat().st_mode&0o777==0o600 for f in secret_dir.iterdir())
 runtime=json.loads((O/'runtime.json').read_text());cp=(P/'labs/f37/target/kafka-classpath.txt').read_text().strip().split(':')
 runtime['kafka_classpath_artifacts']=[{'name':pathlib.Path(f).name,'bytes':pathlib.Path(f).stat().st_size,'sha256':sha(pathlib.Path(f))} for f in cp]
 (O/'runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n')
 ps=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines();assert not any(n.startswith('es-framework-f37-') for n in ps)
 volumes=subprocess.check_output(['docker','volume','ls','--format','{{.Name}}'],text=True).splitlines()
 preserved=[v for v in volumes if v in ['es-framework-f37_pg-data','es-framework-f37_kafka-data','es-framework-f37_es-data']];assert len(preserved)==3
 delivery={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':{str(p.relative_to(R)):sha(p) for p in candidates if p.suffix not in ['.png','.jpg'] and p.name not in ['checks.json','delivery-artifacts.json']},'passed':True}
 (D/'delivery-artifacts.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2)+'\n')
 (D/'checks.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':checks,'final_rounds_verified':['run-02','run-03'],'credentials_absent_in_artifacts':True,'secrets_ignored_and_modes_verified':True,'f37_services_removed':True,'preserved_named_volumes':preserved,'other_running_containers':ps,'passed':True},ensure_ascii=False,indent=2)+'\n')
 print('F37 final repository, receipts, source hashes, credentials exclusion and scoped shutdown checks passed')
if __name__=='__main__':main()
