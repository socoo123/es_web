#!/usr/bin/env python3
"""Scoped final checks and exact-secret exclusion; never prints secret values."""
from pathlib import Path
import ast,datetime,hashlib,json,subprocess
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[]}
def command(args,cwd=R):
 x=subprocess.run(args,cwd=cwd,text=True,capture_output=True);row={'args':args,'exit_code':x.returncode,'stdout':x.stdout,'stderr':x.stderr};rec['commands'].append(row);assert x.returncode==0,row
try:
 command(['node','tools/check.mjs']);command(['node','tools/sync-framework-code.mjs','--check']);command(['git','diff','--check']);command(['git','diff','--cached','--check'])
 command(['bash','-n','projects/travel-search/labs/f42/java.sh'])
 command(['docker','compose','-f','projects/travel-search/infra/f42/compose.yaml','config','--quiet'])
 scripts=[R/'projects/travel-search/labs/f42/lab.py',*D.glob('*.py')]
 for p in scripts:ast.parse(p.read_text(),filename=str(p))
 rec['python_ast']=[str(p.relative_to(R)) for p in scripts]
 generation=json.loads((R/'framework/diagrams/f42/generation.json').read_text());assert generation['passed']
 for name,want in generation['sha256'].items():assert hashlib.sha256((R/'framework/diagrams/f42'/name).read_bytes()).hexdigest()==want,name
 rec['diagram_hashes_match']=True
 for name in ['run-03','run-04']:
  s=json.loads((R/'projects/travel-search/review/f42'/name/'summary.json').read_text());assert s['passed'] and s['source_events']==15 and s['final_next']==15 and s['http_operations']==65
  final=json.loads((R/'projects/travel-search/review/f42'/name/'final-documents.json').read_text())
  assert {k:(v['sync_revision'],v['sync_deleted']) for k,v in final.items()}=={'p01':(5,False),'p02':(3,True),'p03':(1,False),'p04':(2,False)}
 for name in ['http-review.json','supplement-review.json','visual-review.json']:
  assert json.loads((D/name).read_text())['passed'],name
 assert json.loads((R/'projects/travel-search/review/f42/shutdown.json').read_text())['passed']
 # Enumerate modified/new paths; only F42 and explicit current summaries/nav.
 changed=subprocess.check_output(['git','diff','--name-only'],cwd=R,text=True).splitlines()
 new=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
 staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R,text=True).splitlines()
 paths=sorted(set(changed+new+staged))
 roots=['docs/framework-review/20261030-f42-reconcile/','framework/diagrams/f42/']+['projects/travel-search/'+d+'/f42/' for d in ['cdc','data','infra','labs','review','search']]
 files=['FRAMEWORK_PLAN.md','FRAMEWORK_STANDARD.md','PLAN.md','STATUS.md','docs/framework-lesson-prompt.md','framework/f41.html','framework/f42.html','framework/index.html','projects/travel-search/README.md']
 assert all(p in files or any(p.startswith(x) for x in roots) for p in paths),'Out-of-scope files'
 assert not any('/.local/' in p or '/target/' in p or '__pycache__' in p or p.endswith('.pyc') for p in paths)
 rec['scope']={'files_checked':len(paths),'outside_scope':[],'no_local_secrets_or_build_outputs':True}
 secrets=[]
 for p in (R/'projects/travel-search/infra/f42/.local').iterdir():
  v=p.read_text().strip();secrets.append(v.split('=',1)[1] if p.name=='cdc.properties' else v)
 assert all(len(v)>30 for v in secrets)
 for name in paths:
  p=R/name
  if not p.is_file():continue
  b=p.read_bytes();assert not any(v.encode() in b for v in secrets),'Secret found in '+name
 rec['exact_local_secret_scan']={'values_checked':len(secrets),'files_checked':len(paths),'matches':0,'secret_values_printed':False}
 manifest={name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in paths if (R/name).is_file() and name not in [str((D/'checks.json').relative_to(R)),str((D/'delivery-artifacts.json').relative_to(R))]}
 (D/'delivery-artifacts.json').write_text(json.dumps({'at':rec['at'],'sha256':manifest},ensure_ascii=False,indent=2)+'\n')
 rec['passed']=True
finally:(D/'checks.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print('F42 final checks passed; scope, hashes, exact-secret scan and real evidence verified')
