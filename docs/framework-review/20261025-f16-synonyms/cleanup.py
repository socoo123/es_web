#!/usr/bin/env python3
"""Restore only task-owned F16 resources; preserve previous lesson/source nodes."""
import contextlib,datetime,importlib.util,json,os,pathlib,signal,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f16lab',P/'labs/f16/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
others=['es-framework-single-es-1','es-study-secure','es-study']
def states():
 values=json.loads(subprocess.check_output(['docker','inspect',*others],text=True))
 return {v['Name'].lstrip('/'):{k:v['State'][k] for k in ['Status','Running','ExitCode']} for v in values}
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F16 owned resources only','observed_initial':{'es-framework-single-es-1':'exited143','es-study-secure':'running','es-study':'exited137','F16_container':'absent'},'before_cleanup':states(),'commands':[],'status':'running'}
with (HERE/'workspace-cleanup.jsonl').open('w') as f,contextlib.redirect_stdout(f):
 stats=lab.call('GET','/'+lab.INDEX+'/_stats/search')
 record['open_contexts']=stats['indices'][lab.INDEX]['total']['search']['open_contexts'];assert record['open_contexts']==0
 lab.cleanup()
pid=12845
command=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip()
assert 'java -jar target/travel-search-0.7.0.jar' in command,command
os.kill(pid,signal.SIGTERM);record['java']={'pid':pid,'command':command,'signal':'SIGTERM'}
for _ in range(50):
 r=subprocess.run(['ps','-p',str(pid),'-o','pid='],capture_output=True,text=True)
 if not r.stdout.strip():break
 time.sleep(.1)
assert not r.stdout.strip(),'Java did not stop'
r=subprocess.run(['docker','compose','-f','infra/f16/compose.yaml','down'],cwd=P,capture_output=True,text=True)
record['commands'].append({'command':r.args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0
record['after']=states();assert record['after']==record['before_cleanup']
record['F16_container_removed']=subprocess.run(['docker','inspect','es-framework-f16-es-1'],capture_output=True).returncode!=0
assert record['F16_container_removed']
record['retained']='F16 data volume after named lesson index/set deleted, verified ICU/image cache; prior lesson and source nodes unchanged'
record['status']='passed';(HERE/'workspace-state.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F16 named cleanup404, open_contexts0, Java SIGTERM, container/network removed; other states preserved')
