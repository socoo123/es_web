#!/usr/bin/env python3
import datetime,gzip,hashlib,json,pathlib,py_compile,subprocess,tempfile
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];checks=[]
commands=[['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['docker','compose','-f','projects/travel-search/infra/f31/compose.yaml','--profile','extra','config','-q'],['docker','compose','-f','projects/travel-search/infra/f31/compose.yaml','-f','projects/travel-search/infra/f31/bootstrap.yaml','--profile','extra','config','-q'],['git','diff','--check'],['git','diff','--cached','--check']]
for args in commands:
 p=subprocess.run(args,cwd=R,text=True,capture_output=True);checks.append({'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,checks[-1]
python_files=list(D.glob('*.py'))+list((R/'projects/travel-search/labs/f31').glob('*.py'))
with tempfile.TemporaryDirectory(prefix='f31-syntax-') as syntax:
 for n,p in enumerate(python_files):py_compile.compile(str(p),cfile=str(pathlib.Path(syntax)/(str(n)+'.pyc')),doraise=True)
json_files=0;jsonl_lines=0
for folder in [D,R/'projects/travel-search/review/f31',R/'projects/travel-search/data/f31',R/'projects/travel-search/search/f31',R/'framework/diagrams/f31']:
 for p in folder.rglob('*.json'):json.loads(p.read_text());json_files+=1
 for p in list(folder.rglob('*.jsonl'))+list(folder.rglob('*.ndjson')):
  assert p.read_bytes().endswith(b'\n'),p
  for line in p.read_text().splitlines():json.loads(line);jsonl_lines+=1
for file,sha in json.loads((R/'framework/diagrams/f31/generation.json').read_text())['sha256'].items():assert hashlib.sha256((R/file).read_bytes()).hexdigest()==sha,file
for file,sha in json.loads((D/'visual-review.json').read_text())['sha256'].items():assert hashlib.sha256((R/file).read_bytes()).hexdigest()==sha,file
for line in (D/'existing-node-monitor.jsonl').read_text().splitlines():assert json.loads(line)['unchanged']
for p in [D/'content-review.json',D/'http-review.json',D/'visual-review.json',D/'workspace-state.json',R/'projects/travel-search/review/f31/runtime.json']:assert json.loads(p.read_text())['passed'],p
for log in json.loads((R/'projects/travel-search/review/f31/log-archives.json').read_text())['logs']:
 archive=R/'projects/travel-search/review/f31'/log['archive'];raw=gzip.decompress(archive.read_bytes())
 assert hashlib.sha256(raw).hexdigest()==log['uncompressed_sha256'] and hashlib.sha256(archive.read_bytes()).hexdigest()==log['gzip_sha256']
 assert b'BUILD SUCCESS' in raw
assert (R/'.nojekyll').exists()
assert not subprocess.check_output(['git','diff','--','projects/travel-search/backend'],cwd=R,text=True)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'python_files':[str(p.relative_to(R)) for p in python_files],'json_files':json_files,'jsonl_ndjson_lines':jsonl_lines,'diagram_and_visual_hashes_match':True,'shared_backend_unchanged':True,'nojekyll_present':True,'java':'actual clean build/dependency tree/runtime separately recorded; no test source','passed':True}
(D/'checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('F31 final checks passed')
