#!/usr/bin/env python3
"""Final scoped checks, with complete stdout/stderr receipts."""
import datetime,hashlib,importlib.util,json,pathlib,subprocess
import sys
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
commands=[['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f23.js'],['bash','-n',*[str(p.relative_to(ROOT)) for p in [P/'infra/f23/wait.sh',*sorted((P/'labs/f23').glob('*.sh'))]]],['python3','projects/travel-search/data/f23/project.py','--check'],['git','diff','--check'],['git','diff','--cached','--check']]
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[],'python_syntax':[]}
for cmd in commands:
 p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True);r={'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr};record['checks'].append(r);assert p.returncode==0,r
for directory in [HERE,P/'labs/f23',P/'data/f23']:
 for path in directory.glob('*.py'):compile(path.read_text(),str(path),'exec');record['python_syntax'].append(str(path.relative_to(ROOT)))
generation=json.loads((ROOT/'framework/diagrams/f23/generation.json').read_text())
for name,wanted in generation['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==wanted,name
record['diagram_current_hashes']='all match official-generation receipt'
for source in ['http-review.json','shell-review.json','visual-review.json','visual-detail.json','content-review.json','workspace-state.json']:
 r=json.loads((HERE/source).read_text());assert r['status']=='passed',source
record['passed_receipts']=['http-review.json','shell-review.json','visual-review.json','visual-detail.json','content-review.json','workspace-state.json']
for n in ['round1','round2']:
 for name,count in [('prepare',38),('lookup',14),('updates',28),('java',10),('errors',19)]:
  r=json.loads((P/'review/f23'/n/(name+'.json')).read_text());assert r['status']=='passed' and r['http']==count,(n,name)
record['actual_two_rounds']='90 teaching +19 additional each; cleanup and Java internal searches separate'
spec=importlib.util.spec_from_file_location('reading',HERE/'review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);record['static_links']=m.static_links()
record['status']='passed';(HERE/'checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('F23 final checks passed:',len(commands),'commands,',len(record['python_syntax']),'Python syntax checks, all evidence/diagram hashes/links')
