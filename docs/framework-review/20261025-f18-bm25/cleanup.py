#!/usr/bin/env python3
"""Restore this run's F18 resources only; leave preexisting nodes and the empty volume."""
import contextlib,datetime,hashlib,importlib.util,json,os,pathlib,signal,subprocess,time
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];P=R/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f18lab',P/'labs/f18/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F18 only; other nodes preserved','before':json.loads((H/'workspace-before.json').read_text())}
with (H/'cleanup.jsonl').open('w') as out,contextlib.redirect_stdout(out):
 s=lab.call('GET','/'+lab.INDEX+'/_stats/search')
 assert s['_all']['primaries']['search']['open_contexts']==0
 lab.cleanup()
record['open_contexts_before_delete']=0;record['named_index_deleted_and_GET404']=True
pids=subprocess.check_output(['lsof','-tiTCP:18080','-sTCP:LISTEN'],text=True).split();assert len(pids)==1
pid=int(pids[0]);cmd=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip();assert 'java -jar target/travel-search-0.7.0.jar' in cmd,cmd
record['java']={'pid':pid,'command':cmd,'jar_sha256':hashlib.sha256((P/'backend/target/travel-search-0.7.0.jar').read_bytes()).hexdigest()}
os.kill(pid,signal.SIGTERM)
for n in range(80):
 if subprocess.run(['kill','-0',str(pid)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:break
 time.sleep(.2)
else:raise AssertionError('Java did not exit after SIGTERM')
record['java']['normal_SIGTERM_exit']=True
r=subprocess.run(['docker','compose','-f',str(P/'infra/f18/compose.yaml'),'down'],text=True,capture_output=True,timeout=45);assert r.returncode==0,r.stderr
record['compose_down']={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'volumes_removed':False}
record['docker_after']=subprocess.check_output(['docker','ps','-a','--format','{{.Names}} {{.Status}} {{.Ports}}'],text=True).splitlines()
assert not any(line.startswith('es-framework-f18-') for line in record['docker_after'])
assert any(line.startswith('es-study-secure Up') for line in record['docker_after'])
assert any(line.startswith('es-framework-single-es-1 Exited') for line in record['docker_after'])
assert any(line.startswith('es-study Exited') for line in record['docker_after'])
record['empty_volume_retained']=subprocess.check_output(['docker','volume','inspect','es-framework-f18_f18-data','--format','{{.Name}}'],text=True).strip()
record['status']='passed';(H/'workspace-state.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F18 index/Java/container/network cleaned; empty volume and preexisting nodes preserved')
