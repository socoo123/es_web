#!/usr/bin/env python3
"""Point-named final cleanup after preserving full final F29 state."""
import datetime,importlib.util,json,os,pathlib,signal,socket,subprocess,time
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/travel-search';D=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lab',P/'labs/f29/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
lab.OUT=P/'review/f29/final-cleanup';lab.OUT.mkdir(exist_ok=False)
identity=lab.identity();original=json.loads((P/'review/f29/setup/identity.json').read_text());assert identity['uuid']==original['uuid'] and set(identity['nodes'])==set(original['nodes'])
for index,file in [(lab.D,'attractions'),(lab.C,'routed')]:
 r=lab.req('/'+index+'/_search','POST',{'size':20,'track_total_hits':True,'query':{'match_all':{}},'sort':[{'attraction_id':'asc'}]},kind='verification')
 expected=lab.load('data/f29/'+file+'.json');assert r['hits']['total']=={'value':6,'relation':'eq'} and not r['timed_out'] and r['_shards']['failed']==0
 for h,d in zip(r['hits']['hits'],expected):
  assert h['_source']==(d if file=='attractions' else d['source'])
  if file=='routed':assert h['_routing']==d['routing']
lab.cleanup()
pid=json.loads((P/'review/f29/process.json').read_text())['pid']
args=subprocess.check_output(['ps','-p',str(pid),'-o','args='],text=True).strip();assert 'java' in args and 'target/travel-search-0.7.0.jar' in args,args
os.kill(pid,signal.SIGTERM)
deadline=time.monotonic()+30
while time.monotonic()<deadline:
 try:
  with socket.create_connection(('127.0.0.1',18081),timeout=1):time.sleep(.3)
 except OSError:break
else:raise AssertionError('Owned Java port did not close after SIGTERM')
lab.compose('down')
for v in lab.VOLUMES:lab.command(['docker','volume','inspect',v])
secure=json.loads(subprocess.check_output(['docker','inspect','es-study-secure']))[0];after={'id':secure['Id'],'pid':secure['State']['Pid'],'started_at':secure['State']['StartedAt'],'running':secure['State']['Running'],'health':secure['State']['Health']['Status']}
before=json.loads((P/'review/f29/secure-before.json').read_text());assert before==after,[before,after]
left=subprocess.check_output(['docker','ps','-a','--filter','label=com.docker.compose.project=es-framework-f29','--format','{{.Names}}'],text=True).strip();assert not left,left
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'same_uuid_node_ids_before_cleanup':True,'full_final_source_and_routing_both_indices_equal':True,'indices_point_deleted_and_get_404':True,'owned_java_pid':pid,'java_SIGTERM_port_closed':True,'f29_containers_removed':True,'three_f29_volumes_retained':lab.VOLUMES,'other_secure_container_before_after_equal':after,'boundary':'secure-before snapshot collected after F29 initial startup; unchanged from that snapshot through final cleanup'}
(D/'workspace-state.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');lab.save('summary.json',{'passed':True,'events':len(lab.EVENTS)});print('F29 final contents verified, cleanup complete; other secure container unchanged')
