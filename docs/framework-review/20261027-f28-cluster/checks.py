#!/usr/bin/env python3
"""Bounded final checks for F28 and necessary shared metadata; no ES restarts."""
import ast,datetime,gzip,hashlib,json,pathlib,subprocess,shutil
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search';checks=[]
def run(args):
 p=subprocess.run(args,cwd=R,text=True,capture_output=True);row={'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};checks.append(row);assert p.returncode==0,row
run(['node','tools/check.mjs']);run(['node','tools/sync-framework-code.mjs','--check']);run(['git','diff','--cached','--check'])
python_files=list((P/'labs/f28').glob('*.py'))+list(D.glob('*.py'))
for p in python_files:ast.parse(p.read_text(),filename=str(p))
checks.append({'python_ast':len(python_files),'passed':True,'actual_runtime_scripts':'lab.py/content-review.py/runtime/cleanup used python3.11; reading/shell actual Python/Playwright versions in http-review.json'})
for p in (P/'labs/f28').glob('*.sh'):run(['bash','-n',str(p.relative_to(R))])
base=['docker','compose','-f',str((P/'infra/f28/compose.yaml').relative_to(R))]
for extra in [None,'bootstrap.yaml','wrong.yaml','join-wrong.yaml']:
 cmd=base.copy()
 if extra:cmd+=['-f',str((P/'infra/f28'/extra).relative_to(R))]
 run(cmd+['config','--quiet'])
docs=json.loads((P/'data/f28/attractions.json').read_text());lines=(P/'data/f28/attractions.ndjson').read_bytes();assert lines.endswith(b'\n')
nd=[json.loads(x) for x in lines.splitlines()];assert len(nd)==12 and len(docs)==6
for i,doc in enumerate(docs):assert nd[2*i]=={'create':{'_id':doc['attraction_id']}} and nd[2*i+1]==doc
checks.append({'six_source_ndjson_pairs_exact':True,'final_newline':True})
roots=[D,R/'framework/diagrams/f28',P/'data/f28',P/'search/f28',P/'infra/f28',P/'labs/f28',P/'review/f28'];json_count=0;event_count=0
for root in roots:
 for p in root.rglob('*'):
  if p.suffix=='.json':json.loads(p.read_text());json_count+=1
  elif p.name.endswith('.jsonl'):
   for line in p.read_text().splitlines():json.loads(line);event_count+=1
  elif p.name.endswith('.jsonl.gz'):
   for line in gzip.decompress(p.read_bytes()).splitlines():json.loads(line);event_count+=1
for row in json.loads((P/'review/f28/attempts/compressed-events.json').read_text()):assert hashlib.sha256(gzip.decompress((R/row['gzip']).read_bytes())).hexdigest()==row['sha256']
checks.append({'parsed_json_files':json_count,'parsed_jsonl_events_including_lossless_archives':event_count,'exploration_gzip_raw_hashes_equal':True})
gen=json.loads((R/'framework/diagrams/f28/generation.json').read_text())
for path,sha in gen['sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha
for file in ['content-review.json','http-review.json','visual-review.json','shell-review.json','workspace-state.json']:
 rec=json.loads((D/file).read_text());assert rec.get('passed',rec.get('status')=='passed'),file
for folder in [P/'labs/f28/__pycache__',D/'__pycache__']:
 if folder.exists():shutil.rmtree(folder)
metadata=[R/x for x in ['STATUS.md','PLAN.md','FRAMEWORK_STANDARD.md','FRAMEWORK_PLAN.md','FRAMEWORK_CASES.md','framework/f28.html','framework/f27.html','framework/index.html','docs/framework-lesson-prompt.md','projects/travel-search/README.md']]
artifacts=set(metadata)
for root in roots:artifacts.update(p for p in root.rglob('*') if p.is_file() and p!=D/'checks.json')
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'scope':'F28 plus only necessary previous navigation/current summaries; no F29 implementation','checks':checks,'artifact_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(artifacts)},'publishing':'not claimed here; git remote SHA and Pages checked after commit; receipt outside working tree'}
(D/'checks.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F28 final checks passed:',len(artifacts),'artifact hashes')
