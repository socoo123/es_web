#!/usr/bin/env python3
"""Point-named F22 cleanup; retain all volumes/images and the existing secure node."""
import datetime,hashlib,importlib.util,json,os,pathlib,signal,socket,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f22lab',P/'labs/f22/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
def run(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=50);r.check_returncode();return {'args':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
def listening(port):
 try:
  with socket.create_connection(('127.0.0.1',port),timeout=1):return True
 except OSError:return False
before=json.loads((HERE/'workspace-before.json').read_text());record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pending','scope':'only F22 named index, own Java process, compose service/network; no volume/image deletion'}
lab.LOG=HERE/'cleanup-final.jsonl';lab.LOG.write_text('');lab.COUNT=0
stats=lab.request('GET','/_nodes/stats/indices/search?filter_path=nodes.*.indices.search.open_contexts');lab.require(all(n['indices']['search']['open_contexts']==0 for n in stats['nodes'].values()),'open contexts0');record['open_contexts']=stats
before_cleanup=lab.COUNT;record['index_cleanup']=lab.cleanup();record['index_cleanup']['raw_counter_including_prior_stats']=lab.COUNT;record['index_cleanup']['http']=lab.COUNT-before_cleanup
pid=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip();expected=json.loads((HERE/'shell-review.json').read_text())['java_pid_after'];lab.require(pid==expected,'only verified own Java PID')
command=subprocess.check_output(['ps','-p',pid,'-o','command='],text=True).strip();lab.require('projects/travel-search/backend/target/travel-search-0.7.0.jar' in command,'own jar command')
os.kill(int(pid),signal.SIGTERM)
for _ in range(50):
 if not listening(18081):break
 time.sleep(.1)
lab.require(not listening(18081),'own Java port closed');record['java']={'pid':pid,'command':command,'signal':'SIGTERM','port18081':'closed'}
record['compose_down']=run(['docker','compose','-f',str(P/'infra/f22/compose.yaml'),'down'])
lab.require(not listening(19222),'own ES port closed')
remaining=run(['docker','ps','-a','--filter','name=es-framework-f22-es-1','--format','{{.ID}}'])['stdout'].strip();lab.require(not remaining,'F22 container removed')
volume=json.loads(subprocess.check_output(['docker','volume','inspect','es-framework-f22_f22-data'],text=True))[0]
record['retained']={'volume':volume['Name'],'images':'no image removal commands; existing official cache retained','other_resources':'no other index, node, container or volume mutated'}
after=json.loads(subprocess.check_output(['docker','inspect','es-study-secure'],text=True))[0];original=before['containers'][0]
lab.require(original['Id']==after['Id'],'existing node identity')
for key in ['Status','Running','Pid','StartedAt']:lab.require(original['State'][key]==after['State'][key],'existing node '+key)
lab.require(after['State']['Health']['Status']=='healthy','existing node healthy after')
record['existing_node']={'Id':after['Id'],'Name':after['Name'],'State':{k:after['State'][k] for k in ['Status','Running','Pid','StartedAt']},'HealthStatus':after['State']['Health']['Status'],'comparison':'Id/Status/Running/Pid/StartedAt unchanged; healthy after; before normalized health field was lost by receipt normalization, not inferred from missing field'}
record['ports']={'18081':listening(18081),'19222':listening(19222),'existing9201':listening(9201)};record['http']=lab.COUNT;record['status']='passed'
(HERE/'workspace-state.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F22 index404, contexts0, own Java/ES stopped; volume/image kept; existing node identity/start/PID unchanged and healthy')
