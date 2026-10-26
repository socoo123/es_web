"""F21 scoped final syntax, snippets, hashes and real-receipt consistency; never fabricates live checks."""
import ast,datetime,gzip,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;P=ROOT/'projects/travel-search'
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F21 plus necessary current navigation/progress; shared checker unchanged','commands':[]}
def check(args):
 v=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);r['commands'].append({'command':args,'exit_code':v.returncode,'stdout':v.stdout,'stderr':v.stderr});assert v.returncode==0,r['commands'][-1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for args in [['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f21.js'],['git','diff','--check']]:check(args)
for p in sorted((P/'labs/f21').glob('*.sh'))+[P/'infra/f21/wait.sh']:check(['bash','-n',str(p.relative_to(ROOT))])
folders=[HERE,ROOT/'framework/diagrams/f21',P/'labs/f21',P/'data/f21',P/'search/f21',P/'review/f21',P/'infra/f21'];r['syntax']={'python':[],'json':[],'jsonl':[]}
for folder in folders:
 for p in folder.rglob('*.py'):ast.parse(p.read_text(),filename=str(p));r['syntax']['python'].append(str(p.relative_to(ROOT)))
 for p in folder.rglob('*.json'):json.loads(p.read_text());r['syntax']['json'].append(str(p.relative_to(ROOT)))
 for p in folder.rglob('*.jsonl'):
  for line in p.read_text().splitlines():json.loads(line)
  r['syntax']['jsonl'].append(str(p.relative_to(ROOT)))
for name in ['http-review','shell-review','visual-detail','visual-review','content-review','workspace-state','sources']:
 assert json.loads((HERE/(name+'.json')).read_text())['status'].startswith('passed'),name
for file in [HERE/'http-review.json',HERE/'shell-review.json',HERE/'content-review.json',HERE/'visual-review.json',ROOT/'framework/diagrams/f21/generation.json',P/'review/f21/runtime.json']:
 for path,expected in json.loads(file.read_text())['sha256'].items():assert sha(ROOT/path)==expected,(file,path)
for name in ['http-review','shell-review','visual-detail']:
 for row in json.loads((HERE/(name+'.json')).read_text())['screenshots']:assert sha(ROOT/row['path'])==row['sha256']
for row in json.loads((HERE/'contact-sheets.json').read_text()):assert sha(ROOT/row['path'])==row['sha256'] and row['status'].startswith('actually viewed')
runtime=json.loads((P/'review/f21/runtime.json').read_text())
for log in runtime['raw_maven_logs']:assert hashlib.sha256(gzip.decompress((ROOT/log['raw_gzip']).read_bytes())).hexdigest()==log['raw_uncompressed_sha256']
shell=json.loads((HERE/'shell-review.json').read_text());full=shell['full_record'];assert sha(ROOT/full['path'])==full['sha256'];assert hashlib.sha256(gzip.decompress((ROOT/full['path']).read_bytes())).hexdigest()==full['uncompressed_sha256']
actual=json.loads((P/'review/f21/es-java-review.json').read_text());assert actual['status']=='passed' and len(actual['rounds'])==2 and all(v['teaching_requests']==88 and v['additional']['requests']==55 for v in actual['rounds'])
jar='projects/travel-search/backend/target/travel-search-0.7.0.jar';assert actual['jar_sha256']==runtime['sha256'][jar]==shell['sha256'][jar]
assert len(shell['matrix'])==102 and shell['api_calls']==110 and not shell['direct_es_requests'] and not shell['js_errors'];assert json.loads((HERE/'visual-detail.json').read_text())['api_calls']==4
http=json.loads((HERE/'http-review.json').read_text());assert (len(http['matrix']),len(http['regression']),len(http['independent_diagrams']),len(http['clipboard']))==(12,24,16,14)
visual=json.loads((HERE/'visual-review.json').read_text());assert (visual['original_pngs'],visual['contact_sheets_viewed'],len(visual['individually_opened']))==(76,10,16)
assert not (ROOT/'framework/f22.html').exists(),'F22 not implemented by this scope'
paths=[p for folder in folders for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=HERE/'repository-checks.json']
paths.extend(ROOT/name for name in ['STATUS.md','PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_CASES.md','FRAMEWORK_STANDARD.md','docs/framework-lesson-prompt.md','framework/f21.html','framework/f20.html','framework/index.html','projects/travel-search/README.md','projects/travel-search/backend/README.md'])
paths.extend((P/'backend/src/main/java/dev/esweb/travel').glob('Decay*.java'));paths.extend((P/'backend/src/main/resources/static').glob('*f21*'))
r['sha256']={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))};r['status']='passed';r['consistency']='Final tutorial/source/data/D2/runtime jar and actual two-round/browser/visual receipts agree; no checker modification'
(HERE/'repository-checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('F21 final repository checks passed; snippets, current sources, final jar and actual receipts agree')
