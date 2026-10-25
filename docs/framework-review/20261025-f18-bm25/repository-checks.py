#!/usr/bin/env python3
"""F18 bounded repository verification; no network/runtime mutation."""
import ast,datetime,gzip,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as ET
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];P=R/'projects/travel-search'
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F18 and required index/previous/current-summary entry points only','commands':[],'python_syntax':[],'json_files':0,'jsonl_rows':0,'svg_files':0}
commands=[['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f18.js'],['git','diff','--check'],['docker','compose','-f','projects/travel-search/infra/f18/compose.yaml','config','--quiet']]
for p in [*sorted((P/'labs/f18').glob('*.sh')),P/'infra/f18/wait.sh']:commands.append(['bash','-n',str(p.relative_to(R))])
for command in commands:
 p=subprocess.run(command,cwd=R,capture_output=True,text=True);record['commands'].append({'command':command,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,(command,p.stdout,p.stderr)
for folder in [H,P/'labs/f18',P/'review/f18']:
 for p in folder.glob('*.py'):ast.parse(p.read_text(),filename=str(p));record['python_syntax'].append(str(p.relative_to(R)))
for folder in [H,P/'data/f18',P/'search/f18',P/'review/f18',R/'framework/diagrams/f18']:
 for p in folder.rglob('*.json'):
  if p.name=='repository-checks.json':continue
  json.loads(p.read_text());record['json_files']+=1
 for p in folder.rglob('*.jsonl'):
  for line in p.read_text().splitlines():json.loads(line);record['jsonl_rows']+=1
for p in (R/'framework/diagrams/f18').glob('*.svg'):ET.parse(p);record['svg_files']+=1
assert record['svg_files']==4
for receipt in [P/'review/f18/execution.json',P/'review/f18/runtime.json',H/'shell-review.json',H/'workspace-state.json']:
 d=json.loads(receipt.read_text())
 if 'status' in d:assert d['status']=='passed',str(receipt)
jar=P/'backend/target/travel-search-0.7.0.jar';digest=hashlib.sha256(jar.read_bytes()).hexdigest()
assert json.loads((P/'review/f18/execution.json').read_text())['java_jar_sha256']==digest
for receipt in [P/'review/f18/runtime.json',H/'shell-review.json']:
 assert json.loads(receipt.read_text())['sha256']['projects/travel-search/backend/target/travel-search-0.7.0.jar']==digest
for receipt in [R/'framework/diagrams/f18/generation.json',H/'content-review.json']:
 d=json.loads(receipt.read_text())
 for name,digest in d['sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
changed=sorted(set(subprocess.check_output(['git','diff','--name-only'],cwd=R,text=True).splitlines()+subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R,text=True).splitlines()))
record['tracked_changes']=changed
allowed={'STATUS.md','PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_CASES.md','FRAMEWORK_STANDARD.md','docs/framework-lesson-prompt.md','framework/assets/course.css','framework/f17.html','framework/index.html','projects/travel-search/README.md','projects/travel-search/backend/README.md'}
allowed.update({'framework/f18.html',*[f'projects/travel-search/backend/src/main/java/dev/esweb/travel/{n}.java' for n in ['ScoreInput','ScoreAttraction','ScoreSearchService','ScoreController']],*[f'projects/travel-search/backend/src/main/resources/static/{n}' for n in ['f18.html','shell-f18.js','shell-f18.css']]})
prefixes=['docs/framework-review/20261025-f18-bm25/','framework/diagrams/f18/',*[f'projects/travel-search/{n}/f18/' for n in ['data','search','labs','infra','review']]]
assert all(name in allowed or any(name.startswith(prefix) for prefix in prefixes) for name in changed),changed
for log in json.loads((P/'review/f18/runtime.json').read_text())['raw_maven_logs']:
 raw=gzip.decompress((R/log['raw_gzip']).read_bytes());assert hashlib.sha256(raw).hexdigest()==log['raw_uncompressed_sha256']
 assert (R/log['readable']).read_bytes()==b'\n'.join(line.rstrip(b' \t') for line in raw.split(b'\n'))
record['status']='passed'
paths=[R/'framework/f18.html',R/'framework/f17.html',R/'framework/index.html',R/'framework/assets/course.css',R/'STATUS.md',*sorted((P/'backend/src/main/java/dev/esweb/travel').glob('Score*.java')),*sorted((P/'backend/src/main/resources/static').glob('*f18*'))]
for folder in [P/'data/f18',P/'search/f18',P/'labs/f18',P/'infra/f18',R/'framework/diagrams/f18']:paths.extend(p for p in sorted(folder.glob('*')) if p.is_file())
record['sha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(H/'repository-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F18 repository checks passed; final jar/diagram/input hashes agree')
