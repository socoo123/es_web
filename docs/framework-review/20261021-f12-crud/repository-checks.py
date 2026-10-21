#!/usr/bin/env python3
"""Final F12 repository gates; no ES/browser execution is substituted by these checks."""
import datetime,hashlib,importlib.util,json,pathlib,subprocess,traceback,xml.etree.ElementTree as ET
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];P=R/'projects/travel-search'
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','checks':[]}
receipt=H/'repository-checks.json';receipt.write_text(json.dumps(record)+'\n')
def require(value,info):
 if not value:raise AssertionError(info)
def check(command):
 r=subprocess.run(command,cwd=R,text=True,capture_output=True);record['checks'].append({'command':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});require(r.returncode==0,command)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 for cmd in [['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check',str(P/'backend/src/main/resources/static/shell-f12.js')],['git','diff','--check']]:check(cmd)
 py=list((P/'labs/f12').glob('*.py'))+list((P/'review/f12').glob('*.py'))+list(H.glob('*.py'))+list((R/'framework/diagrams/f12').glob('*.py'))
 for path in py:compile(path.read_text(),str(path),'exec')
 record['python_syntax']={'files':[str(p.relative_to(R)) for p in py],'status':'passed'}
 for p in (P/'labs/f12').glob('*.sh'):check(['bash','-n',str(p)])
 for folder in [P/'data/f12',P/'search/f12',P/'review/f12',H,R/'framework/diagrams/f12']:
  for p in folder.rglob('*.json'):json.loads(p.read_text())
 for p in (R/'framework/diagrams/f12').glob('*.svg'):ET.parse(p)
 for p in (P/'data/f12').glob('*.ndjson'):
  raw=p.read_text();require(raw.endswith('\n'),p);lines=[json.loads(line) for line in raw.splitlines()];require(len(lines)%2==0,p)
  for a,b in zip(lines[::2],lines[1::2]):require(a['index']['_id']==b['attraction_id'],p)
 record['json_svg_ndjson']='parsed; NDJSON terminal newline, alternating index/source and fixed ID equality verified'
 for p in (R/'framework/diagrams/f12').glob('*.d2'):
  check(['/tmp/es-framework-d2-20261013/d2','fmt','--check',str(p)]);check(['/tmp/es-framework-d2-20261013/d2','validate',str(p)])
 for receipt_path in [R/'framework/diagrams/f12/generation.json',P/'review/f12/es-java-review.json',H/'http-review.json',H/'shell-review.json']:
  evidence=json.loads(receipt_path.read_text());hashes=evidence['sha256']
  for name,value in hashes.items():require(digest(R/name)==value,{'receipt':str(receipt_path),'changed_input':name})
 record['input_hashes']='generation, two ES/Java rounds, HTTP reading and shell source hashes all still match final inputs'
 visual=json.loads((H/'visual-review.json').read_text())
 for item in visual['screenshots']+visual['overview_sheets']:require(digest(R/item['path'])==item['sha256'],item['path'])
 record['screenshots']={'source_pngs':len(visual['screenshots']),'overview_pngs':len(visual['overview_sheets']),'all_hashes_match':True}
 spec=importlib.util.spec_from_file_location('httpcheck',H/'review.py');http=importlib.util.module_from_spec(spec);spec.loader.exec_module(http)
 record['final_relative_links']=http.static_links()
 record['status']='passed'
except Exception:
 record['status']='failed';record['failure']=traceback.format_exc();raise
finally:
 receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 # Remove only bytecode caches produced in this lesson's new directories.
 for folder in [P/'labs/f12',P/'review/f12',H,R/'framework/diagrams/f12']:
  for cache in folder.rglob('__pycache__'):
   for p in cache.glob('*.pyc'):p.unlink()
   if not list(cache.iterdir()):cache.rmdir()
print('F12 final repository checks:',record['status'])
