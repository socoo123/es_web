"""F20 scoped final checks and artifact consistency. Does not run/pretend live tests."""
import ast,datetime,gzip,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;P=ROOT/'projects/travel-search'
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F20 and necessary current navigation/progress; checker unchanged','commands':[]}
def check(args):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);r['commands'].append({'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,r['commands'][-1]
def hash(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for c in [['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f20.js'],['git','diff','--check']]:check(c)
for p in sorted((P/'labs/f20').glob('*.sh'))+[P/'infra/f20/wait.sh']:check(['bash','-n',str(p.relative_to(ROOT))])
r['python_syntax']=[];r['json_syntax']=[];r['jsonl_syntax']=[]
folders=[HERE,ROOT/'framework/diagrams/f20',P/'labs/f20',P/'data/f20',P/'search/f20',P/'review/f20',P/'infra/f20']
for folder in folders:
 for p in folder.rglob('*.py'):ast.parse(p.read_text(),filename=str(p));r['python_syntax'].append(str(p.relative_to(ROOT)))
 for p in folder.rglob('*.json'):json.loads(p.read_text());r['json_syntax'].append(str(p.relative_to(ROOT)))
 for p in folder.rglob('*.jsonl'):
  for line in p.read_text().splitlines():json.loads(line)
  r['jsonl_syntax'].append(str(p.relative_to(ROOT)))
for name in ['http-review','shell-review','visual-detail','visual-review','content-review','workspace-state']:assert json.loads((HERE/(name+'.json')).read_text())['status'].startswith('passed'),name
runtime=json.loads((P/'review/f20/runtime.json').read_text())
for path,h in runtime['sha256'].items():assert hash(ROOT/path)==h,path
for log in runtime['raw_maven_logs']:assert hashlib.sha256(gzip.decompress((ROOT/log['raw_gzip']).read_bytes())).hexdigest()==log['raw_uncompressed_sha256']
for name in ['http-review','shell-review','visual-detail']:
 rec=json.loads((HERE/(name+'.json')).read_text())
 for row in rec['screenshots']:assert hash(ROOT/row['path'])==row['sha256']
for name in ['http-review','shell-review','visual-review']:
 for path,h in json.loads((HERE/(name+'.json')).read_text())['sha256'].items():assert hash(ROOT/path)==h,path
for path,h in json.loads((ROOT/'framework/diagrams/f20/generation.json').read_text())['sha256'].items():assert hash(ROOT/path)==h,path
for row in json.loads((HERE/'contact-sheets.json').read_text()):assert hash(ROOT/row['path'])==row['sha256']
s=json.loads((HERE/'shell-review.json').read_text());full=s['full_record'];assert hash(ROOT/full['path'])==full['sha256'];assert hashlib.sha256(gzip.decompress((ROOT/full['path']).read_bytes())).hexdigest()==full['uncompressed_sha256']
a=json.loads((P/'review/f20/es-java-review.json').read_text());assert a['status']=='passed' and len(a['rounds'])==2 and all(v['teaching_requests']==79 and v['additional']['requests']==35 for v in a['rounds'])
jar='projects/travel-search/backend/target/travel-search-0.7.0.jar';assert a['jar_sha256']==runtime['sha256'][jar]==s['sha256'][jar]
http=json.loads((HERE/'http-review.json').read_text());assert (len(http['matrix']),len(http['regression']),len(http['independent_diagrams']),len(http['clipboard']))==(12,24,16,16)
assert len(s['matrix'])==90 and s['api_calls']==98 and not s['direct_es_requests'] and not s['js_errors'];assert json.loads((HERE/'visual-detail.json').read_text())['api_calls']==3
v=json.loads((HERE/'visual-review.json').read_text());assert (v['original_pngs'],v['contact_sheets_viewed'],len(v['individually_opened']))==(65,9,15)
paths=[p for folder in folders for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=HERE/'repository-checks.json']
paths.extend(ROOT/p for p in ['STATUS.md','PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_CASES.md','FRAMEWORK_STANDARD.md','docs/framework-lesson-prompt.md','framework/f20.html','framework/f19.html','framework/index.html','projects/travel-search/README.md','projects/travel-search/backend/README.md'])
paths.extend((P/'backend/src/main/java/dev/esweb/travel').glob('Signal*.java'));paths.extend((P/'backend/src/main/resources/static').glob('*f20*'))
r['sha256']={str(p.relative_to(ROOT)):hash(p) for p in sorted(set(paths))};r['status']='passed';r['consistency']='final tutorial/source/data/D2/screenshots/runtime jar and complete live receipts agree; no product edits after final corresponding checks'
(HERE/'repository-checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('F20 final scoped checks passed; final jar/source/data/diagrams/browser evidence hashes agree')
