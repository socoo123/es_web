#!/usr/bin/env python3
"""Exact local-secret scan and scoped syntax/structure checks; never prints secret values."""
import base64,datetime,gzip,json,pathlib,subprocess,hashlib
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
def git(*args):return subprocess.check_output(['git',*args],cwd=R).decode().splitlines()
candidates=sorted(set(git('diff','--name-only')+git('ls-files','--others','--exclude-standard')+git('diff','--cached','--name-only')))
secret_values=[]
for directory in [R/'projects/travel-search/infra/f35/.local',pathlib.Path('/tmp/es-f35-original-local'),pathlib.Path('/tmp/es-f35-init-failed-local')]:
 if not directory.exists():continue
 for p in directory.rglob('*'):
  if p.is_file() and (p.name.endswith('-key.txt') or 'password' in p.name or p.suffix=='.key'):
   value=p.read_bytes().strip()
   if len(value)>=12:secret_values.append(value)
   if p.name.endswith('-key.txt'):
    try:
     decoded=base64.b64decode(value,validate=True)
     if b':' in decoded:secret_values.append(decoded.split(b':',1)[1])
    except Exception:pass
leaks=[]
for name in candidates:
 p=R/name
 if not p.is_file():continue
 data=gzip.open(p,'rb').read() if p.suffix=='.gz' else p.read_bytes()
 if any(len(value)>=12 and value in data for value in secret_values):leaks.append(name)
assert not leaks,{'secret_leaks_in_files':leaks}
assert not any('/.local/' in x or '__pycache__' in x for x in candidates),'ignored secret/cache files selected'
ignore=subprocess.run(['git','check-ignore','projects/travel-search/infra/f35/.local/admin-password.txt'],cwd=R,capture_output=True,text=True);assert ignore.returncode==0
commands=[['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','framework/assets/course.js'],['bash','-n','projects/travel-search/labs/f35/requests.sh'],['python3','-m','py_compile','projects/travel-search/labs/f35/lab.py']]
for p in D.glob('*.py'):
 if p.name!='check-delivery.py':commands.append(['python3','-m','py_compile',str(p.relative_to(R))])
checks=[]
for cmd in commands:
 p=subprocess.run(cmd,cwd=R,text=True,capture_output=True);checks.append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,checks[-1]
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'secret_scan':{'scope':'all new/modified/staged files, gzip decompressed; exact password/key/private-key values from current and two restricted prior local directories','values_checked':len(secret_values),'candidate_files':len(candidates),'leak_files':[],'local_credentials_git_ignored':True},'checks':checks}
(D/'checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F35 structure/snippets/syntax and exact local-secret scan passed')
