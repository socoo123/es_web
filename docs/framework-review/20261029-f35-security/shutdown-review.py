#!/usr/bin/env python3
import importlib.util,json,pathlib,subprocess
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search'
spec=importlib.util.spec_from_file_location('lab',P/'labs/f35/lab.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for action in ['cleanup']:
 subprocess.run(['python3',str(P/'labs/f35/lab.py'),action,'--out',str(P/('review/f35/final-'+action))],check=True)
lab=m.Lab(P/'review/f35/shutdown-check');lab.case='final-cleanup-check'
lab.req('GET','/'+m.INDEX,expected=404)
lab.req('GET','/_alias/'+m.READ,expected=404)
lab.req('GET','/_alias/'+m.WRITE,expected=404)
lab.req('GET','/_security/user/tut-f35-reader',expected=404)
lab.req('GET','/_security/role/tut-f35-reader',expected=404)
keys=lab.req('GET','/_security/api_key?name=tut-f35-*')['api_keys'];assert all(x['invalidated'] for x in keys)
lab.req('GET','/_security/_authenticate',auth='reader',expected=401)
subprocess.run(['python3',str(P/'labs/f35/lab.py'),'down','--out',str(P/'review/f35/final-down')],check=True)
v=json.loads(subprocess.check_output(['docker','inspect','es-study-secure']))[0]
before=json.loads((D/'existing-node-before.json').read_text())
assert v['Id']==before['id'] and v['State']['Pid']==before['state']['Pid'] and v['State']['StartedAt']==before['state']['StartedAt'] and v['RestartCount']==before['restart_count'] and v['State']['Running']
left=subprocess.check_output(['docker','ps','-aq','--filter','label=esweb.lesson=f35'],text=True).strip();assert not left
vol=[]
for name in m.VOLUMES+['es-framework-f35-certs']:
 x=json.loads(subprocess.check_output(['docker','volume','inspect',name]))[0];assert x['Labels']['esweb.lesson']=='f35';vol.append(name)
# Only the processes this lab started were stopped; check that none retain this jar/endpoint.
processes=subprocess.check_output(['ps','-ax','-o','command='],text=True).splitlines()
assert not any('/bin/java -jar '+str(P/'backend/target/travel-search-0.7.0.jar') in x for x in processes)
rec={'at':m.now(),'passed':True,'lesson_containers_remaining':0,'preserved_volumes':vol,'lesson_java_stopped':True,'resources_cleaned':['index and two aliases','native user and role','all lesson API keys invalidated'],'existing_node':{'id':v['Id'],'pid':v['State']['Pid'],'started_at':v['State']['StartedAt'],'restart_count':v['RestartCount'],'running':v['State']['Running'],'identity_pid_start_unchanged':True},'local_secret_files':'retained in ignored 0700 directory; not committed'}
(P/'review/f35/shutdown.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print('F35 resources/Java/containers cleaned; original secure node unchanged')
