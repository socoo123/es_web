#!/usr/bin/env python3
"""Final F16 gates, without changing source or generated assets."""
import ast
import datetime
import hashlib
import json
import pathlib
import subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F16 repository, fragments, syntax and actual receipt hashes','commands':[],'hash_groups':[],'status':'running'}
def command(args):
 r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
 record['commands'].append({'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 assert r.returncode==0,args
try:
 command(['node','tools/check.mjs']);command(['node','tools/sync-framework-code.mjs','--check'])
 command(['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f16.js'])
 for p in [ROOT/'projects/travel-search/infra/f16/wait.sh',*sorted((ROOT/'projects/travel-search/labs/f16').glob('*.sh'))]:command(['bash','-n',str(p.relative_to(ROOT))])
 command(['git','diff','--check']);command(['git','diff','--cached','--check'])
 record['python_syntax']=[]
 for directory in [HERE,ROOT/'framework/diagrams/f16',ROOT/'projects/travel-search/infra/f16',ROOT/'projects/travel-search/labs/f16',ROOT/'projects/travel-search/review/f16']:
  for p in directory.glob('*.py'):ast.parse(p.read_text(),filename=str(p));record['python_syntax'].append(str(p.relative_to(ROOT)))
 for source in ['projects/travel-search/review/f16/execution.json','projects/travel-search/review/f16/runtime.json','framework/diagrams/f16/generation.json',
                'docs/framework-review/20261025-f16-synonyms/content-review.json','docs/framework-review/20261025-f16-synonyms/http-review.json','docs/framework-review/20261025-f16-synonyms/shell-review.json']:
  data=json.loads((ROOT/source).read_text());checked=[]
  for name,expected in data['sha256'].items():
   p=pathlib.Path(name);p=p if p.is_absolute() else ROOT/p
   assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,(source,name);checked.append(name)
  record['hash_groups'].append({'receipt':source,'files':checked})
 record['receipt_states']={}
 for name in ['content-review.json','http-review.json','shell-review.json','visual-detail.json','visual-review.json','workspace-state.json']:
  state=json.loads((HERE/name).read_text())['status'];assert state=='passed',(name,state);record['receipt_states'][name]=state
 assert (ROOT/'.nojekyll').exists();record['nojekyll']=True;record['status']='passed'
finally:(HERE/'repository-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F16 repository, fragments, syntax and input/asset/receipt hashes passed')
