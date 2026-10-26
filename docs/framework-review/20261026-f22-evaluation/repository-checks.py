#!/usr/bin/env python3
"""F22 repository checks; these do not replace ES/Java/browser/visual execution."""
import concurrent.futures,datetime,hashlib,json,pathlib,py_compile,subprocess
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search'
def require(v,d):
 if not v:raise AssertionError(d)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
commands=[['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f22.js'],['git','diff','--check'],['git','diff','--cached','--check']]
commands += [['bash','-n',str(p.relative_to(R))] for p in sorted((P/'labs/f22').glob('*.sh'))]+[['bash','-n','projects/travel-search/infra/f22/wait.sh']]
def command(args):
 r=subprocess.run(args,cwd=R,capture_output=True,text=True);return {'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:results=list(executor.map(command,commands))
for row in results:require(row['exit_code']==0,row)
python_files=[*HERE.glob('*.py'),P/'labs/f22/lab.py',P/'review/f22/run.py',R/'framework/diagrams/f22/generate.py']
for p in python_files:py_compile.compile(str(p),doraise=True)
roots=[HERE,P/'data/f22',P/'search/f22',P/'review/f22',R/'framework/diagrams/f22'];json_count=0;jsonl_lines=0
for root in roots:
 for p in root.rglob('*.json'):load(p);json_count+=1
 for p in root.rglob('*.jsonl'):
  for line in p.read_text().splitlines():json.loads(line);jsonl_lines+=1
required=['content-review.json','http-review.json','shell-review.json','visual-detail.json','card-detail.json','visual-review.json','workspace-state.json']
for f in required:require(load(HERE/f)['status']=='passed',f)
for n in [1,2]:
 j=load(P/f'review/f22/round{n}/summary.json');require(j['teaching_http']==70 and j['extra_http']==23,'round counts')
 require(j['jar_sha256']==sha(P/'backend/target/travel-search-0.7.0.jar'),'final jar used both rounds')
runtime=load(P/'review/f22/runtime.json');require(runtime['sha256']['projects/travel-search/backend/target/travel-search-0.7.0.jar']==sha(P/'backend/target/travel-search-0.7.0.jar'),'runtime artifact')
require('BUILD SUCCESS' in (P/'review/f22/build.log').read_text(),'real build')
for token in ['spring-boot-starter-webmvc:jar:4.0.8','elasticsearch-java:jar:9.4.8','elasticsearch-rest5-client:jar:9.4.8']:require(token in (P/'review/f22/dependency-tree.txt').read_text(),token)
generation=load(R/'framework/diagrams/f22/generation.json')
require(all(x['exit_code']==0 for x in generation['checks']) and generation['generator']=='v0.9.0','D2 formal CLI')
for name,value in generation['sha256'].items():require(sha(R/name)==value,'D2 hash '+name)
http=load(HERE/'http-review.json')
for name,value in http['sha256'].items():require(sha(R/name)==value,'last HTTP asset '+name)
contacts=load(HERE/'contact-sheets.json');require(contacts['sources']==81 and len(contacts['contacts'])==11,'visual count')
for item in contacts['contacts']:
 require(sha(R/item['path'])==item['sha256'],'contact hash')
 for source in item['sources']:require(sha(R/source['source'])==source['sha256'],'reviewed PNG unchanged')
visual=load(HERE/'visual-review.json')
for item in visual['individually_opened']:require(sha(R/item['path'])==item['sha256'],'individually viewed PNG unchanged')
require(len(http['matrix'])==12 and len(http['regression'])==24 and len(http['clipboard'])==12 and len(http['independent_diagrams'])==16,'HTTP matrix')
shell=load(HERE/'shell-review.json');require(len(shell['matrix'])==36 and shell['api_calls']==44 and shell['java_pid_before']==shell['java_pid_after'],'shell matrix')
require(load(HERE/'card-detail.json')['api_calls']==2,'detail calls')
require(not (R/'framework/f23.html').exists() and not (P/'labs/f23').exists(),'F23 not started')
# Scope whitelist includes only the current lesson and necessary previous navigation/shared integration.
shared={'FRAMEWORK_CASES.md','FRAMEWORK_PLAN.md','FRAMEWORK_STANDARD.md','PLAN.md','STATUS.md','docs/framework-lesson-prompt.md','framework/f21.html','framework/index.html','projects/travel-search/README.md','projects/travel-search/backend/pom.xml','projects/travel-search/labs/f21/README.md'}
prefixes=['docs/framework-review/20261026-f22-evaluation/','framework/diagrams/f22/','projects/travel-search/data/f22/','projects/travel-search/search/f22/','projects/travel-search/labs/f22/','projects/travel-search/infra/f22/','projects/travel-search/review/f22/','projects/travel-search/backend/src/main/java/dev/esweb/travel/Quality']
new_static={'framework/f22.html','projects/travel-search/backend/src/main/resources/static/f22.html','projects/travel-search/backend/src/main/resources/static/shell-f22.css','projects/travel-search/backend/src/main/resources/static/shell-f22.js'}
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=R,text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
for name in changed:require(name in shared or name in new_static or any(name.startswith(prefix) for prefix in prefixes),'out of scope '+name)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','commands':results,'python_syntax_files':[str(p.relative_to(R)) for p in python_files],'json_files_parsed':json_count,'jsonl_lines_parsed':jsonl_lines,'checks':['final jar hash identical in runtime and both rounds','real build/dependency tree retained','all required execution receipts passed','D2/last HTTP assets/reviewed PNGs unchanged','12/24/12/16 HTTP,36 shell/44+2 real API calls','F23 absent','changes restricted to F22 and necessary previous/shared integration'],'scope_paths':sorted(set(changed)),'limitations':'static/syntax/hash checks do not replace real ES/Java/browser/visual evidence'}
(HERE/'repository-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F22 repository checks passed: site/snippets/JS/Bash/Python/JSON/evidence hashes/scope; F23 absent')
