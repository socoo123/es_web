#!/usr/bin/env python3
"""Final bounded repository/receipt checks for F29; no ES startup or other lesson edits."""
import ast,datetime,gzip,hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search';checks=[]
def run(args):
 p=subprocess.run(args,cwd=R,text=True,capture_output=True);row={'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};checks.append(row);assert p.returncode==0,row
run(['node','tools/check.mjs']);run(['node','tools/sync-framework-code.mjs','--check']);run(['git','diff','--check']);run(['git','diff','--cached','--check'])
for file in [*D.glob('*.py'),*(P/'labs/f29').glob('*.py')]:ast.parse(file.read_text(),filename=str(file))
run(['bash','-n','projects/travel-search/labs/f29/java.sh'])
base=['docker','compose','-f','projects/travel-search/infra/f29/compose.yaml']
run(base+['config','--quiet']);run(base+['-f','projects/travel-search/infra/f29/bootstrap.yaml','config','--quiet'])
roots=[D,R/'framework/diagrams/f29',P/'data/f29',P/'search/f29',P/'infra/f29',P/'labs/f29',P/'review/f29'];json_files=0;events=0
for root in roots:
 for file in root.rglob('*'):
  if file.suffix=='.json':json.loads(file.read_text());json_files+=1
  elif file.suffix=='.jsonl':
   for line in file.read_text().splitlines():json.loads(line);events+=1
for row in json.loads((P/'review/f29/log-normalization.json').read_text())['logs']:
 assert hashlib.sha256(gzip.decompress((P/'review/f29'/row['raw_lossless_gzip']).read_bytes())).hexdigest()==row['raw_sha256']
 assert hashlib.sha256((P/'review/f29'/row['text_display']).read_bytes()).hexdigest()==row['display_sha256']
checks.append({'python_ast':'F29 scripts only passed','json_files_parsed':json_files,'jsonl_events_parsed':events})
gen=json.loads((R/'framework/diagrams/f29/generation.json').read_text())
for path,sha in gen['sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,path
for file in ['content-review.json','http-review.json','visual-review.json','shell-review.json','workspace-state.json','code-screens.json']:
 assert json.loads((D/file).read_text())['passed'],file
html_sha=hashlib.sha256((R/'framework/f29.html').read_bytes()).hexdigest()
assert json.loads((D/'content-review.json').read_text())['sha256']['framework/f29.html']==html_sha
assert json.loads((D/'final-smoke.json').read_text())['final_html_sha256']==html_sha
assert json.loads((P/'review/f29/runtime.json').read_text())['passed']
assert json.loads((P/'review/f29/guards/summary.json').read_text())['passed']
metadata=[R/p for p in ['STATUS.md','PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_STANDARD.md','FRAMEWORK_CASES.md','framework/f29.html','framework/f28.html','framework/index.html','docs/framework-lesson-prompt.md','projects/travel-search/README.md']]
artifacts=set(metadata)
for root in roots:artifacts.update(f for f in root.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f!=D/'checks.json')
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'scope':'F29 and necessary current summaries/previous next-link only; no F30 implementation','checks':checks,'artifact_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(artifacts)},'publishing':'remote SHA and Pages build checked after commit; outside-working-tree receipt, not claimed here'}
(D/'checks.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F29 final checks passed:',len(artifacts),'artifact hashes')
