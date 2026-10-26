#!/usr/bin/env python3
"""Remove only F23 named indices/app/container/network, retain volumes/images/preexisting node."""
import datetime,json,os,pathlib,signal,socket,subprocess,time
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
def run(cmd,timeout=45):
 p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=timeout);return {'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def closed(port):
 s=socket.socket();s.settimeout(1)
 try:return s.connect_ex(('127.0.0.1',port))!=0
 finally:s.close()
before=json.loads((HERE/'workspace-before.json').read_text());runtime=json.loads((P/'review/f23/runtime.json').read_text());r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F23 named resources only; preserve all preexisting volumes/images and es-study-secure','baseline_timing':'workspace-before captured after creating F23 starter files but before F23 Docker up; initial pre-work git status was observed clean separately'}
r['delete']=run(['python3',str(P/'labs/f23/lab.py'),'cleanup','--out',str(P/'review/f23/final-cleanup')]);assert r['delete']['returncode']==0,r['delete']
pid=int(runtime['java_pid']);cmd=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip();assert 'java' in cmd and 'travel-search-0.7.0.jar' in cmd,cmd
os.kill(pid,signal.SIGTERM)
for _ in range(60):
 if closed(18081):break
 time.sleep(.2)
r['java']={'pid':pid,'signal':'SIGTERM','port18081_closed':closed(18081)};assert r['java']['port18081_closed']
r['compose_down']=run(['docker','compose','-f',str(P/'infra/f23/compose.yaml'),'down']);assert r['compose_down']['returncode']==0,r['compose_down']
r['port19223_closed']=closed(19223);assert r['port19223_closed']
r['f23_container_absent']=subprocess.run(['docker','inspect','es-framework-f23-es-1'],capture_output=True).returncode!=0
r['f23_network_absent']=subprocess.run(['docker','network','inspect','es-framework-f23_default'],capture_output=True).returncode!=0
assert r['f23_container_absent'] and r['f23_network_absent']
x=json.loads(subprocess.check_output(['docker','inspect','es-study-secure']))[0];st=x['State'];current={'name':x['Name'],'id':x['Id'],'started_at':st['StartedAt'],'pid':st['Pid'],'running':st['Running'],'health':st.get('Health',{}).get('Status')}
prior=before['preserved_container'];r['preserved_container_before']=prior;r['preserved_container_after']=current
for key in ['name','id','started_at','pid','running']:assert current[key]==prior[key],key
assert current['health']=='healthy';r['preserved_node_unchanged_and_currently_healthy']=True
r['volumes_after']=subprocess.check_output(['docker','volume','ls','-q'],text=True).splitlines();assert set(before['volumes_before']).issubset(r['volumes_after']);assert 'es-framework-f23_f23-data' in r['volumes_after'];r['preexisting_volumes_retained']=True;r['f23_volume_retained']='es-framework-f23_f23-data'
r['images_after']=subprocess.check_output(['docker','image','ls','--format','{{.ID}} {{.Repository}}:{{.Tag}}'],text=True).splitlines();assert set(before['images_before']).issubset(r['images_after']);r['preexisting_images_retained']=True;r['status']='passed'
(HERE/'workspace-state.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('F23 indices GET404; Java/19223 closed; container/network removed; volume/image + preexisting secure node retained')
