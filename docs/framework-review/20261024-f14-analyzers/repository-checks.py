#!/usr/bin/env python3
"""Final F14 artifact consistency and required repository static checks."""
import ast,datetime,hashlib,importlib.util,json,pathlib,re,subprocess,traceback,xml.etree.ElementTree as ET
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT/'projects/travel-search'
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F14 plus required global static/snippet checks, necessary summary/navigation links only','checks':[],'status':'running'}
def save():(HERE/'repository-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
def run(args):
 r=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);record['checks'].append({'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,args
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save()
try:
 run(['node','tools/check.mjs']);run(['node','tools/sync-framework-code.mjs','--check']);run(['git','diff','--check']);run(['git','diff','--cached','--check'])
 run(['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f14.js'])
 for p in [*(PROJECT/'labs/f14').glob('*.sh'),PROJECT/'infra/f14/wait.sh']:run(['bash','-n',str(p.relative_to(ROOT))])
 py=[*(PROJECT/'labs/f14').glob('*.py'),*(PROJECT/'review/f14').glob('*.py'),*(PROJECT/'infra/f14').glob('*.py'),*(ROOT/'framework/diagrams/f14').glob('*.py'),*HERE.glob('*.py')]
 for p in py:ast.parse(p.read_text(),filename=str(p))
 record['python_syntax']=[str(p.relative_to(ROOT)) for p in py]
 for folder in [PROJECT/'data/f14',PROJECT/'search/f14',PROJECT/'infra/f14',PROJECT/'review/f14',HERE,ROOT/'framework/diagrams/f14']:
  for p in folder.rglob('*.json'):
   if '.artifacts' not in p.parts:json.loads(p.read_text())
  for p in [*folder.rglob('*.jsonl'),*folder.rglob('*.ndjson')]:
   assert p.read_bytes().endswith(b'\n'),p
   for line in p.read_text().splitlines():json.loads(line)
 record['json_ndjson']='all F14 inputs/receipts parse; line-oriented files have final newline'
 for p in (ROOT/'framework/diagrams/f14').glob('*.svg'):ET.parse(p)
 for path,digest in json.loads((ROOT/'framework/diagrams/f14/generation.json').read_text())['sha256'].items():assert sha(ROOT/path)==digest,path
 record['diagrams']='4 SVG XML parse; all D2/SVG hashes equal generation receipt'
 spec=importlib.util.spec_from_file_location('f14read',HERE/'review.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
 record['static_links']=reader.static_links()
 for name in ['STATUS.md','PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_CASES.md','FRAMEWORK_STANDARD.md','README.md','docs/framework-lesson-prompt.md','projects/travel-search/backend/README.md']:
  p=ROOT/name
  for href in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if not re.match('https?:|#|mailto:',href):assert (p.parent/href.split('#')[0]).exists(),(name,href)
 record['summary_links']='all relative links in changed summaries and prompt exist'
 execution=json.loads((PROJECT/'review/f14/execution.json').read_text());assert execution['status']=='passed' and len(execution['rounds'])==2
 for row in execution['rounds']:
  assert row['teaching_calls']==108 and row['all_client_calls']==152 and row['additional_calls']==44
  assert len((PROJECT/f'review/f14/round-{row["round"]}.jsonl').read_text().splitlines())==152
 for path,digest in execution['sha256'].items():assert sha(ROOT/path)==digest,path
 for name in ['http-review.json','shell-review.json','final-text-review.json']:
  j=json.loads((HERE/name).read_text());assert j['status']=='passed',name
  for shot in j['screenshots']:assert sha(ROOT/shot['path'])==shot['sha256'],shot['path']
 shell=json.loads((HERE/'shell-review.json').read_text());assert len(shell['operations'])==84 and len(shell['matrix'])==12
 for path,digest in shell['sha256'].items():assert sha(ROOT/path)==digest,path
 actual=sha(ROOT/'framework/f14.html')
 for name in ['final-text-review.json','content-review.json','reasoning.json']:assert json.loads((HERE/name).read_text())['final_lesson_sha256']==actual,name
 visual=json.loads((HERE/'visual-review.json').read_text());assert visual['raw_png_count']==46 and visual['individual_open_count']==12
 for shot in visual['screenshots']:assert sha(ROOT/shot['path'])==shot['sha256']
 for path,digest in visual['overview_sha256'].items():assert sha(ROOT/path)==digest,path
 assert json.loads((HERE/'workspace-state.json').read_text())['status']=='restored'
 assert json.loads((PROJECT/'review/f14/mismatch.json').read_text())['exit_code']==70
 runtime=json.loads((PROJECT/'review/f14/build/runtime.json').read_text())
 for path,digest in runtime['sha256'].items():assert sha(pathlib.Path(path) if pathlib.Path(path).is_absolute() else ROOT/path)==digest,path
 record['evidence']='2×152 real calls; teaching108 each; shell84; browser/source/screenshot/build hashes match; final paragraph hash current; workspace restored'
 record['sha256']={str(p.relative_to(ROOT)):sha(p) for pattern in ['framework/f14.html','framework/diagrams/f14/*','projects/travel-search/data/f14/*','projects/travel-search/search/f14/**/*.json','projects/travel-search/labs/f14/*','projects/travel-search/infra/f14/*','projects/travel-search/backend/src/main/java/dev/esweb/travel/Analyzer*.java','projects/travel-search/backend/src/main/resources/static/*f14*'] for p in ROOT.glob(pattern) if p.is_file()}
 record['status']='passed'
except Exception:
 record['status']='failed';record['failure']=traceback.format_exc();raise
finally:save()
print('F14 final repository checks passed')
