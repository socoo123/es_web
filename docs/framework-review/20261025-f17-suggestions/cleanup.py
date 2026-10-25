#!/usr/bin/env python3
"""Restore only resources created for F17; preserve the empty lesson volume and caches."""
import contextlib,datetime,hashlib,importlib.util,json,os,pathlib,signal,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f17lab',P/'labs/f17/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F17-only resource restore; other lessons untouched','status':'running'}
def run(cmd):
 r=subprocess.run(cmd,capture_output=True,text=True,check=True);return {'command':cmd,'stdout':r.stdout.strip(),'stderr':r.stderr.strip(),'exit_code':r.returncode}
with (HERE/'workspace-cleanup.jsonl').open('w') as f,contextlib.redirect_stdout(f):
 r=lab.call('GET','/'+lab.INDEX+'/_stats/search');assert r['indices'][lab.INDEX]['total']['search']['open_contexts']==0
 lab.cleanup()
record['index']={'name':lab.INDEX,'delete':'acknowledged','subsequent_get':404,'open_contexts_before_delete':0}
pids=subprocess.run(['lsof','-t','-nP','-iTCP:18080','-sTCP:LISTEN'],capture_output=True,text=True,check=True).stdout.split()
assert len(pids)==1
pid=int(pids[0]);cmd=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip()
assert cmd=='/tmp/es-f07-tooling/jdk-25.0.4.1+1/Contents/Home/bin/java -jar projects/travel-search/backend/target/travel-search-0.7.0.jar',cmd
os.kill(pid,signal.SIGTERM)
for n in range(100):
 try:os.kill(pid,0)
 except ProcessLookupError:break
 time.sleep(.1)
else:raise AssertionError('Java did not stop after SIGTERM')
record['java']={'pid':pid,'command':cmd,'signal':'SIGTERM','stopped':True,'final_log_sha256':hashlib.sha256((P/'review/f17/java.log').read_bytes()).hexdigest()}
record['compose_down']=run(['docker','compose','-f',str(P/'infra/f17/compose.yaml'),'down'])
record['remaining_containers']=run(['docker','ps','-a','--format','{{.Names}} {{.Status}} {{.Ports}}'])
record['volume']=run(['docker','volume','inspect','--format','{{.Name}}','es-framework-f17_f17-data'])
record['preserved']=['empty F17 volume; no lesson index remains','official ES image and tooling caches','es-framework-single-es-1 remains stopped','es-study remains stopped','es-study-secure remains running']
assert 'es-framework-f17-es-1' not in record['remaining_containers']['stdout']
record['status']='passed';(HERE/'workspace-state.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F17 named index removed/404, Java SIGTERM, container/network removed; other nodes preserved')
