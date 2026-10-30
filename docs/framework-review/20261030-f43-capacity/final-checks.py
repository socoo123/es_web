#!/usr/bin/env python3
"""Final scoped repository checks; no ES mutation or new load runs."""
import datetime,hashlib,json,pathlib,re,subprocess,sys
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];records=[]
def command(args):
 p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True);records.append({'args':args,'status':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,records[-1]
command(['node','tools/check.mjs'])
command(['node','tools/sync-framework-code.mjs','--check'])
command(['bash','-n','projects/travel-search/labs/f43/java.sh'])
for p in [ROOT/'projects/travel-search/labs/f43/lab.py',*D.glob('*.py')]:command([sys.executable,'-m','py_compile',str(p)])
for extra in [[],['-f','projects/travel-search/infra/f43/bootstrap.yaml'],['-f','projects/travel-search/infra/f43/pressure.yaml']]:
 command(['docker','compose','-f','projects/travel-search/infra/f43/compose.yaml',*extra,'config','--format','json'])
command([sys.executable,str(D/'recompute.py')])
generation=json.loads((ROOT/'framework/diagrams/f43/generation.json').read_text())
for path,sha in generation['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
for source in (ROOT/'framework/diagrams/f43').glob('*.d2'):
 for args in [['fmt','--check',str(source)],['validate',str(source)]]:command(['/tmp/es-framework-d2-20261013/d2',*args])
scopes=[D,ROOT/'framework/diagrams/f43',ROOT/'projects/travel-search/labs/f43',ROOT/'projects/travel-search/infra/f43',ROOT/'projects/travel-search/search/f43',ROOT/'projects/travel-search/review/f43']
jsons=[];md_links=[]
for scope in scopes:
 for f in scope.rglob('*.json'):
  if '.local' in f.parts:continue
  json.loads(f.read_text());jsons.append(str(f.relative_to(ROOT)))
 for f in scope.rglob('*.md'):
  for link in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if re.match(r'^(?:https?:|#|mailto:)',link):continue
   target=(f.parent/link.split('#')[0]).resolve();assert target.exists() or target==D/"checks.json",(f,link);md_links.append([str(f.relative_to(ROOT)),link])
old=subprocess.check_output(['git','show','HEAD:framework/f42.html'],cwd=ROOT,text=True)
assert (ROOT/'framework/f42.html').read_text()==old.replace('<span>下一课：F43 负载与容量（待编写）</span>','<a href="f43.html">F43 负载与容量 →</a>')
files=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
assert not any(re.search(r'(?:__pycache__|/target/|/\.local/|\.pyc$|\.class$)',f) for f in files)
for name in ['http-review.json','detail-review.json','content-review.json','guards.json','recomputed.json','workspace-state.json']:
 value=json.loads((D/name).read_text());assert value.get('passed',value.get('content_review_passed_with_limits',False)),name
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'commands':records,'json_parsed':jsons,'markdown_links':md_links,'f42_only_next_link_changed':True,'no_generated_cache_or_local_identity_in_changes':True,'diagram_hashes_equal':True}
(D/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Final F43 repository checks passed')
