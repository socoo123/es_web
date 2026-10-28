#!/usr/bin/env python3
import datetime,hashlib,json,pathlib,py_compile,subprocess,tempfile
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];checks=[]
for args in [['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['docker','compose','-f','projects/travel-search/infra/f30/compose.yaml','config','-q'],['docker','compose','-f','projects/travel-search/infra/f30/compose.yaml','-f','projects/travel-search/infra/f30/bootstrap.yaml','config','-q'],['git','diff','--check']]:
 p=subprocess.run(args,cwd=R,text=True,capture_output=True);checks.append({'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,checks[-1]
python_files=list(D.glob('*.py'))+list((R/'projects/travel-search/labs/f30').glob('*.py'))
with tempfile.TemporaryDirectory(prefix="f30-syntax-") as syntax_dir:
 for n,p in enumerate(python_files):py_compile.compile(str(p),cfile=str(pathlib.Path(syntax_dir)/(str(n)+".pyc")),doraise=True)
json_count=0;jsonl_lines=0
for folder in [D,R/'projects/travel-search/review/f30',R/'projects/travel-search/data/f30',R/'projects/travel-search/search/f30',R/'framework/diagrams/f30']:
 for p in folder.rglob('*.json'):
  json.loads(p.read_text());json_count+=1
 for p in folder.rglob('*.jsonl'):
  for line in p.read_text().splitlines():json.loads(line);jsonl_lines+=1
 for p in folder.rglob('*.ndjson'):
  assert p.read_bytes().endswith(b'\n')
  for line in p.read_text().splitlines():json.loads(line);jsonl_lines+=1
for file,sha in json.loads((R/'framework/diagrams/f30/generation.json').read_text())['sha256'].items():
 assert hashlib.sha256((R/file).read_bytes()).hexdigest()==sha,file
assert not subprocess.check_output(['git','diff','--','projects/travel-search/backend'],cwd=R,text=True)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'python_files':[str(p.relative_to(R)) for p in python_files],'json_files':json_count,'jsonl_ndjson_lines':jsonl_lines,'diagram_hashes_match':True,'shared_backend_unchanged':True,'java':'actual clean build, runtime and FailureProbe recorded separately; no test sources','passed':True}
(D/'checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('F30 final static/source/JSON/Compose checks passed')
