#!/usr/bin/env python3
"""Scoped final checks, evidence integrity and fixed query/data consistency."""
import datetime,hashlib,importlib.util,json,pathlib,re,subprocess,sys
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
commands=[['node','tools/check.mjs'],['node','tools/figwidth.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f24.js'],['bash','-n','projects/travel-search/infra/f24/wait.sh',*[str(p.relative_to(ROOT)) for p in sorted((P/'labs/f24').glob('*.sh'))]],['python3','projects/travel-search/data/f24/project.py','--check'],['git','diff','--check'],['git','diff','--cached','--check']]
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[],'python_syntax':[]}
for cmd in commands:
 p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True);r={'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr};record['checks'].append(r);assert p.returncode==0,r
for directory in [HERE,P/'labs/f24',P/'data/f24']:
 for path in directory.glob('*.py'):compile(path.read_text(),str(path),'exec');record['python_syntax'].append(str(path.relative_to(ROOT)))
g=json.loads((ROOT/'framework/diagrams/f24/generation.json').read_text())
for name,wanted in g['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==wanted,name
record['diagram_hashes']='2D2/4SVG all match official-generation receipt'
for name in ['http-review.json','shell-review.json','visual-review.json','visual-detail.json','visual-followup.json','content-review.json','workspace-state.json']:
 r=json.loads((HERE/name).read_text());assert r['status']=='passed',name
record['passed_receipts']=['http-review.json','shell-review.json','visual-review.json','visual-detail.json','visual-followup.json','content-review.json','workspace-state.json']
for n in ['round1','round2']:
 for name,count in [('prepare',20),('matching',10),('sorting',6),('java',10),('errors',13)]:
  r=json.loads((P/'review/f24'/n/(name+'.json')).read_text());assert r['status']=='passed' and r['http']==count,(n,name)
record['two_rounds']='46 teaching +13 additional each; cleanup and Java internal searches separately counted'
for shot in json.loads((HERE/'visual-review.json').read_text())['screenshots']:
 assert hashlib.sha256((ROOT/shot['path']).read_bytes()).hexdigest()==shot['sha256'],shot['path']
record['visual_current_hashes']='84 original PNGs intact and reviewed by declared method'
spec=importlib.util.spec_from_file_location('helpers',HERE/'reading_helpers.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);record['static_links']=m.static_links()
read=lambda name:json.loads((P/'search/f24'/name).read_text())
eligible=read('eligible.json');fixed=read('filtered-sort.json');matched=read('matched.json')
assert fixed['query']['bool']['filter'][2]['nested']['query']==eligible==fixed['sort'][0]['rooms.price_minor']['nested']['filter']==matched['query']['bool']['filter'][2]['nested']['query']
assert fixed['query']['bool']['filter'][2]['nested']['inner_hits']==matched['query']['bool']['filter'][2]['nested']['inner_hits']
record['qualification_consistency']='complete shared predicate identical in query and sort; inner_hits attached to same query and explicitly price/offer sorted'
assert not (ROOT/'framework/f25.html').exists() and not (P/'labs/f25').exists(),'F25 must remain unstarted'
record['next_course']='F25 not implemented; prompt advanced only'
record['status']='passed';(HERE/'checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('F24 final scoped checks passed')
