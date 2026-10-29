#!/usr/bin/env python3
"""Run the reader's actual curl stages once, independently of the formal Python flow."""
import importlib.util,json,pathlib,re,subprocess,os
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f35',P/'labs/f35/lab.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
D=P/'review/f35/manual';D.mkdir(exist_ok=False)
rec={'curl_stages':[],'passed':False}
def stage(name,args,statuses):
 p=subprocess.run(['bash','labs/f35/requests.sh',name]+args,cwd=P,capture_output=True,text=True)
 assert p.returncode==0,(name,p.stderr)
 text='\n'.join(x for x in p.stdout.splitlines() if not x.startswith('F35 '));decoder=json.JSONDecoder();rows=[]
 while text.strip():
  text=text.lstrip();body,end=decoder.raw_decode(text);text=text[end:].lstrip();match=re.match(r'HTTP (\d+)\s*',text);assert match,(name,text[:80]);text=text[match.end():]
  rows.append({'status':int(match[1]),'response':body})
 assert [x['status'] for x in rows]==statuses,(name,[x['status'] for x in rows])
 rec['curl_stages'].append({'stage':name,'responses':rows})
 return rows
lab=m.Lab(P/'review/f35/manual-java');lab.case='manual-java'
try:
 prep=stage('prepare',[str(P/'review/f35/manual-cleanup'),str(P/'review/f35/manual-credentials')],[200]*4)
 assert not prep[2]['response']['errors'] and all(next(iter(x.values()))['status']==201 for x in prep[2]['response']['items'])
 perm=stage('permissions',[],[200,200,403,403,403,200,200,403,403,403,200])
 assert perm[1]['response']['hits']['total']['value']==6
 lab.start_app('manual-after-update');lab.app_search('manual-after-update',[('p01',6500)])
 stage('repair',[],[200,201,200]);lab.app_search('manual-after-repair',[('p01',6000),('p02',0)])
 for action in ['revoke','rotate']:
  r=subprocess.run(['python3','labs/f35/lab.py',action,'--out',str(P/('review/f35/manual-'+action))],cwd=P,capture_output=True,text=True);assert r.returncode==0,r.stderr
  lab.app_search('manual-after-'+action,[],502)
 lab.start_app('manual-after-restart');lab.app_search('manual-after-restart',[('p01',6000),('p02',0)])
 r=subprocess.run(['curl','-sS','--cacert',str(m.LOCAL/'wrong-ca.crt'),m.ES+'/_security/_authenticate'],capture_output=True,text=True)
 assert r.returncode==60;rec['wrong_ca_curl']={'exit_code':r.returncode,'http_status':None,'stderr':r.stderr}
 for mode,status in [('no-credential',401),('admin',200)]:
  args=['curl','-sS','--cacert',str(m.LOCAL/'ca.crt')] if mode=='no-credential' else ['curl','-sS','--config',str(m.LOCAL/'admin.curl')]
  r=subprocess.run(args+[m.ES+'/_security/_authenticate','-w','\n%{http_code}'],capture_output=True,text=True);assert r.returncode==0
  body,code=r.stdout.rsplit('\n',1);assert int(code)==status
  rec[mode+'-curl']={'status':status,'response':json.loads(body)}
 rec['passed']=True
finally:
 lab.stop_app();(D/'summary.json').write_text(json.dumps(m.redact(rec),ensure_ascii=False,indent=2)+'\n')
print('F35 actual manual curl stages + Java rotation passed')
