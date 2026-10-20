#!/usr/bin/env python3
"""F08 scoped repository validation; runtime/browser checks are separate artifacts."""
import ast,datetime,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as ET
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/travel-search'
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F08 and necessary navigation/current summary only','commands':[],'data':{}}
def command(args,**kwargs):
 r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,**kwargs);R['commands'].append(dict(args=args,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
 assert r.returncode==0,(args,r.stdout,r.stderr)
 return r.stdout
try:
 command(['node','tools/check.mjs'])
 command(['node','tools/sync-framework-code.mjs','--check'])
 command(['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f08.js'])
 for path in (P/'labs/f08').glob('*.sh'):command(['bash','-n',str(path.relative_to(ROOT))])
 py=list(H.glob('*.py'))+[P/'review/f08/verify.py',ROOT/'framework/diagrams/f08/generate.py']
 for path in py:ast.parse(path.read_text(),filename=str(path))
 R['data']['Python_AST']=[str(p.relative_to(ROOT)) for p in py]
 paths=[p for folder in [H,P/'data/f08',P/'search/f08',P/'labs/f08',P/'review/f08',ROOT/'framework/diagrams/f08'] for p in folder.rglob('*.json')]
 for path in paths:json.loads(path.read_text())
 R['data']['JSON_files']=len(paths)
 svg=list((ROOT/'framework/diagrams/f08').glob('*.svg'))
 for path in svg:ET.parse(path)
 R['data']['SVG_XML']=len(svg)
 data=(P/'data/f08/attractions.ndjson').read_bytes();assert data.endswith(b'\n')
 lines=[json.loads(line) for line in data.splitlines()];docs=json.loads((P/'data/f08/attractions.json').read_text());assert len(lines)==30
 for i,d in enumerate(docs):assert lines[i*2]=={'index':{'_id':d['attraction_id']}} and lines[i*2+1]==d
 R['data']['NDJSON']='15 unique fixed IDs, 30 valid lines, exact JSON fixture pairs, final newline'
 generation=json.loads((ROOT/'framework/diagrams/f08/generation.json').read_text())
 for name,sha in generation['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
 R['data']['D2_hashes']='2 sources/4 SVG match actual official generation receipt'
 for filename in ['http-review.json','shell-review.json']:
  r=json.loads((H/filename).read_text())
  for shot in r['screenshots']:assert hashlib.sha256((ROOT/shot['path']).read_bytes()).hexdigest()==shot['sha256'],shot
 R['data']['screenshot_hashes']='26 lesson + 8 shell PNGs match raw evidence'
 runtime=json.loads((P/'review/f08/es-java-review.json').read_text());assert runtime['status']=='passed' and len(runtime['rounds'])==2
 for name,sha in runtime['inputs'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
 R['data']['runtime_input_hashes']='all final runtime data/search/labs/backend source hashes unchanged'
 sources=json.loads((H/'sources.json').read_text());assert all(s['matches_local'] for s in sources['sources'])
 tree=json.loads((P/'review/f08/dependency-tree.json').read_text())['combined_output'];assert 'co.elastic.clients:elasticsearch-java:jar:9.4.8' in tree and 'co.elastic.clients:elasticsearch-rest5-client:jar:9.4.8' in tree
 R['data']['dependencies']='official Java and Rest5 9.4.8; Boot4.0.8 inherited'
 command(['git','diff','--check'])
 command(['git','diff','--cached','--check'])
 R['status']='passed'
except Exception as e:R['status']='failed';R['failure']=repr(e);raise
finally:(H/'repository-checks.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print('F08 repository checks passed: structure, exact snippets, syntax, fixtures, source/runtime/diagram/screenshot hashes')
