#!/usr/bin/env python3
"""Author-only cleanup of resources started for F28; compare the pre-existing secure node."""
import datetime,importlib.util,json,os,pathlib,signal,subprocess,time,urllib.error,urllib.request
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];P=ROOT/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f28lab',P/'labs/f28/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
def cmd(args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);return {'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def record_secure():
 state=json.loads(subprocess.check_output(['docker','inspect','es-study-secure','--format','{{json .State}}'],text=True));return {k:state[k] for k in ['Pid','StartedAt','Running','Status']}|{'HealthStatus':state['Health']['Status']}
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[],'scope':'Only F28 index/Java PID/compose containers and network; preserve three normal volumes/image and original secure node.'}
before=json.loads(pathlib.Path('/tmp/f28-secure-before.json').read_text());before={k:before[k] for k in ['Pid','StartedAt','Running','Status']}|{'HealthStatus':before['Health']['Status']}
rec['pre_existing_secure_before']=before
lab.OUT=P/'review/f28/final-integrity';lab.OUT.mkdir(exist_ok=False)
identity=lab.identity('identity');expected=json.loads((P/'review/f28/round2/first/steady-identity.json').read_text());assert identity['uuid']==expected['uuid'] and identity['node_ids']==expected['node_ids']
lab.data_check('data');lab.search();lab.java();lab.save('summary.json',{'passed':True,'original_round2_uuid':identity['uuid'],'all_six_sources_exact':True,'representative_rest_java':'p01/p02','teaching_http':sum(r['kind']=='teaching' for r in lab.EVENTS),'not_part_of_main_72':True})
rec['final_identity']=identity
for i in [1,2,3]:
 s=json.loads(subprocess.check_output(['docker','inspect',f'es-framework-f28-es{i}-1','--format','{{json .State}}'],text=True));assert s['Running'] and not s['OOMKilled'];rec.setdefault('f28_before_cleanup',[]).append({'node':i,'running':s['Running'],'oom_killed':s['OOMKilled'],'started_at':s['StartedAt']})
# Point-name index cleanup, then stop ONLY the app process verified as this run's jar/listener.
lab.OUT=P/'review/f28/final-cleanup';lab.OUT.mkdir(exist_ok=False);lab.EVENTS=[];lab.cleanup();lab.save('summary.json',{'passed':True,'http_requests':2,'deleted_only':lab.INDEX,'GET_after_delete':404})
app=json.loads((P/'review/f28/runtime.json').read_text());pid=int(app['java_pid_from_log'])
proc=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip();assert '/tmp/es-f07-tooling/' in proc and '-jar target/travel-search-0.7.0.jar' in proc
listener=subprocess.check_output(['lsof','-nP','-iTCP:18081','-sTCP:LISTEN','-t'],text=True).strip();assert listener==str(pid)
os.kill(pid,signal.SIGTERM)
for _ in range(100):
 time.sleep(.1)
 if subprocess.run(['lsof','-nP','-iTCP:18081','-sTCP:LISTEN','-t'],capture_output=True).returncode!=0:break
else:raise AssertionError('Java port did not close')
rec['java_cleanup']={'pid':pid,'command_verified':proc,'signal':'SIGTERM','port_18081_closed':True}
p=cmd(['docker','compose','-f',str(P/'infra/f28/compose.yaml'),'down']);rec['commands'].append(p);assert p['exit_code']==0
p=cmd(['docker','ps','-a','--filter','label=com.docker.compose.project=es-framework-f28','--format','{{.Names}}']);rec['commands'].append(p);assert p['exit_code']==0 and not p['stdout'].strip()
p=cmd(['docker','network','inspect','es-framework-f28_default']);rec['commands'].append(p);assert p['exit_code']!=0
for volume in lab.VOLUMES:
 p=cmd(['docker','volume','inspect',volume]);rec['commands'].append(p);assert p['exit_code']==0
p=cmd(['docker','volume','inspect',lab.WRONG]);rec['commands'].append(p);assert p['exit_code']!=0
rec['pre_existing_secure_after']=record_secure();assert rec['pre_existing_secure_after']==before
rec['secure_unchanged_fields']=['Pid','StartedAt','Running','Status','HealthStatus'];rec['secure_container_id_not_claimed']='Baseline captured State only; no initial container ID available.'
rec['passed']=True;rec['preserved_volumes']=lab.VOLUMES;rec['wrong_volume_absent']=True
(D/'workspace-state.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F28 final data verified; index/app/containers/network cleaned; three volumes retained; pre-existing secure node unchanged')
