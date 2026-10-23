#!/usr/bin/env python3
"""F15 final repository gates; does not modify lesson or generated diagrams."""
import ast
import datetime
import hashlib
import json
import pathlib
import subprocess

HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F15 and required repository/fragment gates','commands':[],'hash_groups':[],'status':'running'}
def command(args):
    r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
    record['commands'].append({'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    assert r.returncode==0,args
try:
    command(['node','tools/check.mjs'])
    command(['node','tools/sync-framework-code.mjs','--check'])
    command(['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f15.js'])
    for p in [ROOT/'projects/travel-search/infra/f15/wait.sh',*sorted((ROOT/'projects/travel-search/labs/f15').glob('*.sh'))]:
        command(['bash','-n',str(p.relative_to(ROOT))])
    command(['git','diff','--check'])
    record['python_syntax']=[]
    for directory in [HERE,ROOT/'framework/diagrams/f15',ROOT/'projects/travel-search/infra/f15',ROOT/'projects/travel-search/labs/f15',ROOT/'projects/travel-search/review/f15']:
        for p in directory.glob('*.py'):
            ast.parse(p.read_text(),filename=str(p));record['python_syntax'].append(str(p.relative_to(ROOT)))
    for source,key in [('projects/travel-search/review/f15/execution.json','sha256'),('framework/diagrams/f15/generation.json','sha256'),
                       ('docs/framework-review/20261024-f15-dictionary/content-review.json','sha256'),('docs/framework-review/20261024-f15-dictionary/http-review.json','sha256'),
                       ('projects/travel-search/review/f15/build/runtime.json','sha256')]:
        data=json.loads((ROOT/source).read_text());checked=[]
        for name,expected in data[key].items():
            p=pathlib.Path(name);p=p if p.is_absolute() else ROOT/p
            assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,(source,name)
            checked.append(name)
        record['hash_groups'].append({'receipt':source,'checked_files':checked})
    record['receipt_states']={}
    for name in ['http-review.json','shell-review.json','final-text-review.json','workspace-state.json']:
        state=json.loads((HERE/name).read_text())['status'];assert state=='passed',(name,state)
        record['receipt_states'][name]=state
    assert (ROOT/'.nojekyll').exists()
    record['nojekyll']=True;record['status']='passed'
finally:
    (HERE/'repository-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F15 repository, snippets, syntax and final receipt hashes passed')
