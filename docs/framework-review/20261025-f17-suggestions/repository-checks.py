#!/usr/bin/env python3
"""F17 final structure, source parity, syntax and evidence hash checks."""
import datetime,hashlib,json,pathlib,subprocess,traceback
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F17 and necessary navigation/current summaries only','checks':[],'status':'running'}
def run(cmd):
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
 record['checks'].append({'command':cmd,'exit_code':r.returncode,'stdout':r.stdout.strip(),'stderr':r.stderr.strip()})
 assert r.returncode==0,record['checks'][-1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 run(['node','tools/check.mjs']);run(['node','tools/sync-framework-code.mjs','--check'])
 for p in [P/'backend/src/main/resources/static/shell-f17.js']:
  run(['node','--check',str(p.relative_to(ROOT))])
 for p in [*(P/'labs/f17').glob('*.sh'),P/'infra/f17/wait.sh']:run(['bash','-n',str(p.relative_to(ROOT))])
 for p in [*(P/'labs/f17').glob('*.py'),*(P/'review/f17').glob('*.py'),*(ROOT/'framework/diagrams/f17').glob('*.py'),*HERE.glob('*.py')]:compile(p.read_text(),str(p),'exec')
 record['checks'].append({'python_syntax':'passed; compile() without writing bytecode'})
 count=0
 for folder in [P/'search/f17',P/'data/f17',P/'review/f17',HERE,ROOT/'framework/diagrams/f17']:
  for p in folder.glob('*.json'):
   if p.name=='repository-checks.json':continue
   json.loads(p.read_text());count+=1
 for p in [P/'data/f17/attractions.ndjson',*(P/'review/f17').glob('*.jsonl'),*HERE.glob('*.jsonl')]:
  for l in p.read_text().splitlines():json.loads(l)
 record['checks'].append({'json_documents_parsed':count,'ndjson_and_receipts':'passed'})
 for relative in ['framework/diagrams/f17/generation.json','projects/travel-search/review/f17/execution.json','projects/travel-search/review/f17/runtime.json']:
  doc=json.loads((ROOT/relative).read_text())
  for path,value in doc['sha256'].items():assert sha(ROOT/path)==value,(relative,path)
  record['checks'].append({'hash_receipt':relative,'entries_verified':len(doc['sha256'])})
 shell=json.loads((HERE/'shell-review.json').read_text());http=json.loads((HERE/'http-review.json').read_text());content=json.loads((HERE/'content-review.json').read_text());resources=json.loads((HERE/'workspace-state.json').read_text())
 assert all(r['status']=='passed' for r in [shell,http,content,resources])
 assert shell['jar_sha256']==sha(P/'backend/target/travel-search-0.7.0.jar')
 for path,value in http['sha256'].items():assert sha(ROOT/path)==value,('http',path)
 for path,value in content['sha256'].items():assert sha(ROOT/path)==value,('content',path)
 record['checks'].append({'acceptance':'passed content/HTTP/local shell/resource cleanup; final jar and lesson/asset/source hashes match'})
 run(['git','diff','--check']);run(['git','diff','--cached','--check'])
 record['sha256']={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'STATUS.md',ROOT/'framework/f17.html',ROOT/'framework/f16.html',ROOT/'framework/index.html',HERE/'content-review.json',HERE/'http-review.json',HERE/'shell-review.json',HERE/'workspace-state.json',HERE/'visual-review.json',*sorted((P/'backend/src/main/java/dev/esweb/travel').glob('Suggest*.java'))]}
 record['status']='passed'
except BaseException:record['status']='failed';record['error']=traceback.format_exc();raise
finally:(HERE/'repository-checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F17 repository/source/syntax/hash checks passed')
