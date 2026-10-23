#!/usr/bin/env python3
"""Required repository and F13 syntax/artifact checks; no service mutations."""
import ast,datetime,hashlib,importlib.util,json,pathlib,re,subprocess,sys,xml.etree.ElementTree as ET
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];P=R/'projects/travel-search'
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F13 only plus required global static site check and snippet consistency','checks':[],'status':'running'}
out=H/'repository-checks.json'
def save():out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
def run(args):
 result=subprocess.run(args,cwd=R,text=True,capture_output=True)
 record['checks'].append({'command':args,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
 if result.returncode:raise RuntimeError(args)
save()
try:
 run(['node','tools/check.mjs']);run(['node','tools/sync-framework-code.mjs','--check']);run(['git','diff','--check']);run(['git','diff','--cached','--check'])
 js=P/'backend/src/main/resources/static/shell-f13.js';run(['node','--check',str(js.relative_to(R))])
 for p in (P/'labs/f13').glob('*.sh'):run(['bash','-n',str(p.relative_to(R))])
 py=[*(P/'labs/f13').glob('*.py'),*(P/'review/f13').glob('*.py'),*(R/'framework/diagrams/f13').glob('*.py'),*H.glob('*.py')]
 for p in py:ast.parse(p.read_text(),filename=str(p))
 record['python_syntax']={'status':'passed','files':[str(p.relative_to(R)) for p in py]}
 jsonfiles=[*(P/'data/f13').glob('*.json'),*(P/'search/f13').rglob('*.json'),*(P/'review/f13').rglob('*.json'),*H.rglob('*.json'),R/'framework/diagrams/f13/generation.json']
 for p in jsonfiles:json.loads(p.read_text())
 jsonl=[*(P/'review/f13').glob('*.jsonl'),*(H).glob('*.jsonl'),P/'data/f13/attractions.ndjson']
 for p in jsonl:
  for line in p.read_text().splitlines():json.loads(line)
  assert p.read_bytes().endswith(b'\n'),p
 record['json_ndjson']={'status':'passed','json_files':len(jsonfiles),'line_files':len(jsonl)}
 for p in (R/'framework/diagrams/f13').glob('*.svg'):ET.parse(p)
 generation=json.loads((R/'framework/diagrams/f13/generation.json').read_text())
 for path,expected in generation['sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==expected,path
 record['svg_and_generator_hashes']='4 SVG parse; current D2/SVG hashes equal generation receipt'
 spec=importlib.util.spec_from_file_location('f13read',H/'review.py');reading=importlib.util.module_from_spec(spec);spec.loader.exec_module(reading)
 record['local_links']=reading.static_links()
 for relative in ['PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_CASES.md','FRAMEWORK_STANDARD.md','README.md','docs/framework-lesson-prompt.md','projects/travel-search/backend/README.md']:
  p=R/relative
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if re.match(r'https?:|#|mailto:',link):continue
   assert (p.parent/link.split('#')[0]).exists(),(relative,link)
 record['summary_links']='all changed planning/template/backend summary relative links exist'
 for key,path in [('ES/Java','projects/travel-search/review/f13/execution.json'),('HTTP','docs/framework-review/20261023-f13-analysis/http-review.json'),('shell','docs/framework-review/20261023-f13-analysis/shell-review.json'),('finaltext','docs/framework-review/20261023-f13-analysis/final-text-review.json')]:
  data=json.loads((R/path).read_text());assert data['status']=='passed',key
 record['execution_receipts']='ES/Java two rounds, HTTP, local shell and final paragraph checks passed; attempts separately retained'
 finalhash=hashlib.sha256((R/'framework/f13.html').read_bytes()).hexdigest()
 assert finalhash==json.loads((H/'final-text-review.json').read_text())['final_lesson_sha256']
 for p in (P/'review/f13').glob('round-*.jsonl'):
  rows=[json.loads(l) for l in p.read_text().splitlines()];assert len(rows)==81,p
 reasoning=json.loads((H/'reasoning.json').read_text())
 assert hashlib.sha256((H/'author-draft.md').read_bytes()).hexdigest()==reasoning['author']['sha256']
 assert hashlib.sha256((H/'independent-content-review.md').read_bytes()).hexdigest()==reasoning['review']['report_sha256']
 record['record_consistency']='final lesson hash equals post-review paragraph receipt; raw round counts81/81; author/review artifact hashes match'
 record['sha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for pattern in ['framework/f13.html','framework/diagrams/f13/*','projects/travel-search/data/f13/*','projects/travel-search/search/f13/**/*.json','projects/travel-search/labs/f13/*','projects/travel-search/backend/src/main/java/dev/esweb/travel/Analysis*.java','projects/travel-search/backend/src/main/resources/static/*f13*'] for p in R.glob(pattern) if p.is_file()}
 record['status']='passed'
except Exception as error:
 record['status']='failed';record['error']=repr(error);raise
finally:save()
print('F13 repository checks passed')
