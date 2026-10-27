#!/usr/bin/env python3
import datetime,hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search'
r=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),commands=[],python_syntax=[],json_syntax=[])
commands=[['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f27.js'],['python3','projects/travel-search/data/f27/project.py','--check'],['bash','-n','projects/travel-search/infra/f27/wait.sh',*[str(p.relative_to(R)) for p in (P/'labs/f27').glob('*.sh')]],['git','diff','--check'],['git','diff','--cached','--check']]
for args in commands:
    p=subprocess.run(args,cwd=R,text=True,capture_output=True);r['commands'].append(dict(command=args,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,r['commands'][-1]
for directory in [D,P/'labs/f27',P/'data/f27']:
    for p in directory.glob('*.py'):compile(p.read_text(),str(p),'exec');r['python_syntax'].append(str(p.relative_to(R)))
for directory in [D,P/'data/f27',P/'search/f27',P/'review/f27',R/'framework/diagrams/f27']:
    for p in directory.rglob('*.json'):json.loads(p.read_text());r['json_syntax'].append(str(p.relative_to(R)))
    for p in directory.rglob('*.jsonl'):
        for line in p.read_text().splitlines():json.loads(line)
        r['json_syntax'].append(str(p.relative_to(R)))
generation=json.loads((R/'framework/diagrams/f27/generation.json').read_text())
for name,value in generation['sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==value,name
r['diagram_hashes']='all current 2 sources and 4 generated SVGs match generation receipt';r['status']='passed'
(D/'checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('F27 checks passed')
