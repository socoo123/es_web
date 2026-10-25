#!/usr/bin/env python3
"""F19 scoped final static/syntax/hash checks; live checks have separate receipts."""
import ast,datetime,gzip,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;P=ROOT/'projects/travel-search'
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F19 project/tutorial and necessary navigation/current summaries; no checker modifications','commands':[]}
def check(args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);r['commands'].append({'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,r['commands'][-1]
for args in [['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f19.js']]:check(args)
for p in sorted((P/'labs/f19').glob('*.sh'))+[P/'infra/f19/wait.sh']:check(['bash','-n',str(p.relative_to(ROOT))])
r['python_syntax']=[];r['json_syntax']=[]
for folder in [HERE,P/'labs/f19',P/'review/f19']:
 for p in folder.rglob('*.py'):ast.parse(p.read_text(),filename=str(p));r['python_syntax'].append(str(p.relative_to(ROOT)))
for folder in [HERE,ROOT/'framework/diagrams/f19',P/'search/f19',P/'data/f19',P/'review/f19']:
 for p in folder.rglob('*.json'):json.loads(p.read_text());r['json_syntax'].append(str(p.relative_to(ROOT)))
for name in ['http-review','shell-review','visual-detail','visual-review','content-review','workspace-state']:assert json.loads((HERE/(name+'.json')).read_text())['status'].startswith('passed'),name
rt=json.loads((P/'review/f19/runtime.json').read_text())
for path,expected in rt['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
for log in rt['raw_maven_logs']:assert hashlib.sha256(gzip.decompress((ROOT/log['raw_gzip']).read_bytes())).hexdigest()==log['raw_uncompressed_sha256']
for name in ['http-review','shell-review','visual-detail']:
 for shot in json.loads((HERE/(name+'.json')).read_text())['screenshots']:assert hashlib.sha256((ROOT/shot['path']).read_bytes()).hexdigest()==shot['sha256'],shot['path']
for path,expected in json.loads((HERE/'visual-review.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
for c in json.loads((HERE/'contact-sheets.json').read_text()):assert hashlib.sha256((ROOT/c['path']).read_bytes()).hexdigest()==c['sha256']
for path,expected in json.loads((ROOT/'framework/diagrams/f19/generation.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
s=json.loads((HERE/'shell-review.json').read_text());a=s['full_record'];assert hashlib.sha256((ROOT/a['path']).read_bytes()).hexdigest()==a['sha256'];assert hashlib.sha256(gzip.decompress((ROOT/a['path']).read_bytes())).hexdigest()==a['uncompressed_sha256']
j=json.loads((P/'review/f19/es-java-review.json').read_text());assert j['status']=='passed' and len(j['rounds'])==2 and all(x['teaching_requests']==92 for x in j['rounds'])
assert j['jar_sha256']==rt['sha256']['projects/travel-search/backend/target/travel-search-0.7.0.jar']==s['sha256']['projects/travel-search/backend/target/travel-search-0.7.0.jar']
http=json.loads((HERE/'http-review.json').read_text());assert len(http['matrix'])==12 and len(http['regression'])==24 and len(http['independent_diagrams'])==16 and len(http['clipboard'])==16
assert len(s['matrix'])==96 and s['api_calls']==104 and not s['direct_es_requests'] and not s['js_errors'];assert json.loads((HERE/'visual-detail.json').read_text())['api_calls']==3
paths=[]
for folder in [HERE,ROOT/'framework/diagrams/f19',P/'labs/f19',P/'search/f19',P/'data/f19',P/'infra/f19',P/'review/f19']:
 paths.extend(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=HERE/'repository-checks.json')
paths.extend(ROOT/p for p in ['AGENTS.md','PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_STANDARD.md','FRAMEWORK_CASES.md','STATUS.md','docs/framework-lesson-prompt.md','framework/f19.html','framework/f18.html','framework/index.html','framework/assets/course.css','projects/travel-search/README.md','projects/travel-search/backend/README.md'])
paths.extend((P/'backend/src/main/java/dev/esweb/travel').glob('Weight*.java'));paths.extend((P/'backend/src/main/resources/static').glob('*f19*'))
r['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))};r['hash_checks']='runtime/jar/build raw logs, final D2, screenshots/contact sheets, full browser gzip and DSL/counter receipts all passed';r['status']='passed'
(HERE/'repository-checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('F19 repository checks passed:',len(r['sha256']),'file hashes,',len(r['python_syntax']),'Python files,',len(r['json_syntax']),'JSON files')
