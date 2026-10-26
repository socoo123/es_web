#!/usr/bin/env python3
"""Pointed F24 cleanup with preservation proof for pre-existing node, volumes and images."""
import datetime,gzip,importlib.util,json,os,pathlib,signal,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search';spec=importlib.util.spec_from_file_location('lab',P/'labs/f24/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
def require(ok,detail):
 if not ok:raise AssertionError(detail)
def run(args,cwd=R):
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True);require(p.returncode==0,dict(command=args,output=p.stdout,error=p.stderr));return {'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
before=json.loads((HERE/'workspace-before.json').read_text());before['containers']=[{k:c[k] for k in ['Id','Name','Image','State']} for c in before['containers']];(HERE/'workspace-before.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n')
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preserve':'all previous containers/volumes/images; remove only F24 indices, own Java, F24 compose container/network'}
lab.LOG=HERE/'post-shell-canonical.jsonl';require(not lab.LOG.exists(),'preserve previous log');lab.COUNT=0;rows=lab.read(P/'data/f24/hotels.json');checks=[]
for m in ['object','nested']:
 docs=lab.request('POST','/tut-f24-'+m+'/_mget',{'ids':[h['hotel_id'] for h in rows]})['docs'];require(all(d['found'] and d['_source']==h for d,h in zip(docs,rows)),'all source canonical after faults')
 stats=lab.request('GET','/tut-f24-'+m+'/_stats/search')['_all']['total']['search'];require(stats['open_contexts']==0,'zero search contexts');checks.append({'model':m,'all_9_source_docs_exact':True,'open_contexts':0})
rec['post_shell']={'http':lab.COUNT,'checks':checks};(HERE/'post-shell-canonical.json').write_text(json.dumps(dict(status='passed',**rec['post_shell']),ensure_ascii=False,indent=2)+'\n')
rec['delete_indices']=run(['python3','labs/f24/lab.py','cleanup','--out',str(P/'review/f24/final-cleanup')],P)
pid=int((P/'review/f24/java.pid').read_text());actual=subprocess.check_output(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],text=True).strip();require(actual==str(pid),'only own Java PID');cmd=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True);require('travel-search-0.7.0.jar' in cmd,'expected jar');os.kill(pid,signal.SIGTERM)
for _ in range(80):
 if not subprocess.run(['lsof','-t','-iTCP:18081','-sTCP:LISTEN'],capture_output=True,text=True).stdout.strip():break
 time.sleep(.2)
else:raise RuntimeError('Java listener still present')
rec['java']={'pid':pid,'signal':'SIGTERM','listener_closed':True};(P/'review/f24/java.pid').unlink()
rec['compose_down']=run(['docker','compose','-f','infra/f24/compose.yaml','down'],P)
rec['f24_containers_remaining']=subprocess.check_output(['docker','ps','-a','--filter','label=com.docker.compose.project=es-framework-f24','--format','{{.ID}}'],text=True).splitlines();require(not rec['f24_containers_remaining'],'F24 containers removed')
rec['f24_networks_remaining']=subprocess.check_output(['docker','network','ls','--filter','label=com.docker.compose.project=es-framework-f24','-q'],text=True).splitlines();require(not rec['f24_networks_remaining'],'F24 networks removed')
rec['listeners']={str(p):subprocess.run(['lsof','-t',f'-iTCP:{p}','-sTCP:LISTEN'],capture_output=True,text=True).stdout.strip() for p in [19224,18081]};require(all(not v for v in rec['listeners'].values()),'own ports closed')
after=json.loads(subprocess.check_output(['docker','inspect','es-study-secure'],text=True))[0];old=before['containers'][0];rec['old_node']={k:after[k] for k in ['Id','Name','Image','State']};require(after['Id']==old['Id'] and after['State']['StartedAt']==old['State']['StartedAt'] and after['State']['Pid']==old['State']['Pid'] and after['State']['Running'] and after['State']['Health']['Status']=='healthy','old secure node unchanged and healthy')
volumes=subprocess.check_output(['docker','volume','ls','-q'],text=True).splitlines();images=subprocess.check_output(['docker','image','ls','-q','--no-trunc'],text=True).splitlines();require(set(before['volumes'])<=set(volumes),'old volumes preserved');require(set(before['images'])<=set(images),'old images preserved');require('es-framework-f24_f24-data' in volumes,'own volume retained');rec['volumes']={'all_preexisting_retained':True,'f24_volume_retained':True};rec['images']={'all_preexisting_retained':True,'no_image_deletion':True}
for name in ['java-app.log','build-initial.log']:
 p=P/'review/f24'/name
 if p.exists():
  raw=p.read_bytes();gzip.open(str(p)+'.gz','wb').write(raw);p.write_text('\n'.join(line.rstrip() for line in raw.decode().splitlines())+'\n')
rec['status']='passed';(HERE/'workspace-state.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F24 source/context verification, pointed cleanup and old-resource preservation passed')
