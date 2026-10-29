#!/usr/bin/env python3
"""F40 scoped delivery checks; no service mutation or future lesson edits."""
import ast,datetime,gzip,hashlib,json,pathlib,re,subprocess
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search'
REC={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[]}
def check(ok,detail):
 if not ok:raise AssertionError(detail)
def command(args):
 r=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=90)
 REC['commands'].append({'args':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});check(r.returncode==0,REC['commands'][-1]);return r.stdout
def main():
 command(['node','tools/check.mjs']);command(['node','tools/sync-framework-code.mjs','--check'])
 command(['node','--check','framework/assets/course.js']);command(['bash','-n','projects/travel-search/labs/f40/java.sh']);command(['git','diff','--check'])
 scripts=list((P/'labs/f40').glob('*.py'))+list(D.glob('*.py'))
 for path in scripts:ast.parse(path.read_text(),filename=str(path))
 REC['python_ast']=[str(x.relative_to(R)) for x in scripts]
 for sub in ['run-03','run-04','run-05','run-06']:
  run=P/'review/f40'/sub;summary=json.loads((run/'summary.json').read_text());check(summary['passed'],sub)
  check(summary['source_events']==17 and summary['worker_runs']==21 and summary['http_requests']==53,summary)
  check(summary['final_revisions']=={'p01':11,'p02':4,'p03':2},summary)
  for value in summary['final_positions'].values():check(value['committed_next']==value['observed_end'],value)
  http=[json.loads(x) for x in (run/'http.jsonl').read_text().splitlines()];check(len(http)==53,[sub,len(http)])
  events=json.loads((run/'final-events.json').read_text());check(len(events)==17,sub)
  check(sum(json.loads(e['value'])['op']=='r' for e in events)==3,sub)
  partial=json.loads((run/'partial-block.json').read_text());check(partial['exit_code']==1,sub)
  check([v['status'] for v in partial['records'] if v['kind']=='item']==[200,400,200],partial)
  check(not any(v['kind']=='commit' for v in partial['records']),partial)
  crash=json.loads((run/'crash-after-es.json').read_text());check(crash['exit_code']==40,sub)
  empty=json.loads((run/'restart-empty.json').read_text());check(empty['records'][-1]['processed']==0,sub)
 REC['final_consumer_rounds']=['run-05','run-06'];REC['additional_browser_rounds']=['run-03','run-04']
 for filename in ['http-review.json','supplement-review.json','visual-review.json','content-review.json']:
  check(json.loads((D/filename).read_text())['passed'],filename)
 boundary=json.loads((P/'review/f40/boundary/summary.json').read_text());check(boundary['passed'] and boundary['source_positions_before']==boundary['source_positions_after'],boundary)
 generation=json.loads((R/'framework/diagrams/f40/generation.json').read_text());check(generation['passed'],'D2')
 for name,value in generation['sha256'].items():check(hashlib.sha256((R/'framework/diagrams/f40'/name).read_bytes()).hexdigest()==value,name)
 sources=json.loads((D/'source-evidence.json').read_text());check(all(f['http_status']==200 and f['local_matches'] for f in sources['files']),sources)
 # Changed tracked files plus untracked nonignored scope; no recursive scanning of old lessons.
 tracked=command(['git','diff','--name-only']).splitlines();new=command(['git','ls-files','--others','--exclude-standard']).splitlines()
 files=sorted(set(tracked+new));allowed={'STATUS.md','FRAMEWORK_PLAN.md','FRAMEWORK_STANDARD.md','docs/framework-lesson-prompt.md','framework/index.html','framework/f39.html','framework/f40.html'}
 prefixes=['docs/framework-review/20261029-f40-replay/','framework/diagrams/f40/']+['projects/travel-search/'+x+'/f40/' for x in ['infra','labs','cdc','data','search','review']]
 check(all(f in allowed or any(f.startswith(prefix) for prefix in prefixes) for f in files),'Unrelated changed files')
 check(not any('/.local/' in f or '/target/' in f or '__pycache__/' in f or f.endswith('.class') for f in files),'Generated/private files included')
 secret_paths=[P/'infra/f40/.local/pg-password.txt',P/'infra/f40/.local/cdc.properties'];secrets=[]
 for path in secret_paths:
  raw=path.read_text().strip();secrets.append((raw.split('=',1)[1] if path.suffix=='.properties' else raw).encode())
 for f in files:
  raw=(R/f).read_bytes()
  if f.endswith('.gz'):raw=gzip.decompress(raw)
  check(all(secret not in raw for secret in secrets),'Actual local secret found in '+f)
 REC['actual_secret_values_absent']=True;REC['changed_scope_files']=len(files)
 check(json.loads((P/'review/f40/cleanup-final/summary.json').read_text())['passed'],'Cleanup final')
 check(json.loads((P/'review/f40/down/summary.json').read_text())['passed'],'Down')
 check(json.loads((P/'review/f40/shutdown.json').read_text())['passed'],'Shutdown identity/ports')
 REC['passed']=True
 (D/'checks.json').write_text(json.dumps(REC,ensure_ascii=False,indent=2)+'\n')
 # The manifest excludes itself and Python cache/private/build directories.
 files=sorted(set(files+['docs/framework-review/20261029-f40-replay/checks.json']))
 entries={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in files if f!='docs/framework-review/20261029-f40-replay/delivery-artifacts.json'}
 (D/'delivery-artifacts.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':entries},ensure_ascii=False,indent=2)+'\n')
 print('F40 site/snippets/syntax, four runs/two final rounds, source/diagram hashes, scoped files and actual secret exclusion passed')
if __name__=='__main__':main()
