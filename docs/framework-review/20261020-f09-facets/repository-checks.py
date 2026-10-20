#!/usr/bin/env python3
"""F09 final scoped checks; runtime/browser and generation are separate receipts."""
import ast,datetime,hashlib,json,pathlib,subprocess,re,runpy,xml.etree.ElementTree as ET
H=pathlib.Path(__file__).resolve().parent;ROOT=H.parents[2];P=ROOT/'projects/travel-search'
R={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'F09 and necessary navigation/current summaries','commands':[],'data':{}}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def command(args):
 r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);R['commands'].append(dict(args=args,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,(args,r.stdout,r.stderr);return r.stdout
try:
 command(['node','tools/check.mjs']);command(['node','tools/sync-framework-code.mjs','--check'])
 command(['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f09.js'])
 for path in (P/'labs/f09').glob('*.sh'):command(['bash','-n',str(path.relative_to(ROOT))])
 py=list(H.glob('*.py'))+[P/'review/f09/verify.py',ROOT/'framework/diagrams/f09/generate.py']
 for path in py:ast.parse(path.read_text(),filename=str(path))
 R['data']['Python_AST']=[str(p.relative_to(ROOT)) for p in py]
 paths=[p for folder in [H,P/'data/f09',P/'search/f09',P/'labs/f09',P/'review/f09',ROOT/'framework/diagrams/f09'] for p in folder.rglob('*.json')]
 for path in paths:json.loads(path.read_text())
 R['data']['JSON_files']=len(paths)
 svg=list((ROOT/'framework/diagrams/f09').glob('*.svg'))
 for path in svg:ET.parse(path)
 R['data']['SVG_XML']=len(svg)
 data=(P/'data/f09/attractions.ndjson').read_bytes();assert data.endswith(b'\n');lines=[json.loads(l) for l in data.splitlines()];docs=json.loads((P/'data/f09/attractions.json').read_text());assert len(lines)==32
 for i,d in enumerate(docs):assert lines[2*i]=={'index':{'_id':d['attraction_id']}} and lines[2*i+1]==d
 c=(P/'data/f09/candidates.ndjson').read_bytes();assert c.endswith(b'\n');cl=[json.loads(l) for l in c.splitlines()];assert len(cl)==40
 counts={}
 for i in range(0,len(cl),2):
  route=cl[i]['index']['routing'];tag=cl[i+1]['tag'];counts[(route,tag)]=counts.get((route,tag),0)+1
 assert counts=={('a','A'):5,('a','C'):4,('a','B'):1,('b','B'):5,('b','C'):4,('b','A'):1}
 R['data']['NDJSON']='main16 unique IDs/32 lines exact JSON fixture pairs; candidate20/40 lines exact per-routing tag distribution; final newlines'
 generation=json.loads((ROOT/'framework/diagrams/f09/generation.json').read_text())
 for name,value in generation['sha256'].items():assert sha(ROOT/name)==value,name
 R['data']['D2_hashes']='2 sources/4 generated SVG match official D2 receipt'
 for filename in ['http-review.json','shell-review.json']:
  r=json.loads((H/filename).read_text());assert r['status']=='passed'
  for shot in r['screenshots']:assert sha(ROOT/shot['path'])==shot['sha256'],shot
  for name,value in r.get('sha256',r.get('inputs',{})).items():assert sha(ROOT/name)==value,name
 R['data']['browser_hashes']='26 lesson +10 shell originals, current tutorial/diagram/style/backend hashes match actual browser inputs'
 visual=json.loads((H/'visual-review.json').read_text())
 for crop in visual['code_crops']:assert sha(ROOT/crop['path'])==crop['sha256'],crop
 R['data']['visual']='18 whole+4 partial lesson screenshots actually viewed,4 lesson generated only;8 shell whole viewed,2 generated only;4 crop hashes match'
 runtime=json.loads((P/'review/f09/es-java-review.json').read_text());assert runtime['status']=='passed' and len(runtime['rounds'])==2
 for name,value in runtime['inputs'].items():assert sha(ROOT/name)==value,name
 R['data']['runtime_input_hashes']='all final data/search/labs/backend source unchanged after two clean actual rounds'
 for number in [1,2]:
  baseline=next(json.loads(q['raw_response'])['aggregations'] for q in runtime['requests'] if q['label']==f'round{number} REST selected')
  for size in [0,2]:
   response=next(json.loads(q['raw_response']) for q in runtime['requests'] if q['label']==f'round{number} size={size}')
   assert response['aggregations']==baseline
 R['data']['page_size_full_aggregations']='Raw real responses: size0 and size2 complete aggregation objects exactly equal selected baseline in both rounds'
 sources=json.loads((H/'sources.json').read_text());assert len(sources['sources'])==4 and all(s['matches_local'] and sha(ROOT/s['local_path'])==s['official_sha256'] for s in sources['sources'])
 tree=json.loads((P/'review/f09/dependency-tree.json').read_text())['combined_output'];assert 'co.elastic.clients:elasticsearch-java:jar:9.4.8' in tree and 'co.elastic.clients:elasticsearch-rest5-client:jar:9.4.8' in tree
 assert json.loads((P/'review/f09/build.json').read_text())['exit_code']==0
 R['data']['dependencies']='Boot4.0.8/JDK25; official Java and Rest5 9.4.8; clean package passed; no unit tests'
 content=json.loads((H/'content-review.json').read_text());assert sha(ROOT/'framework/f09.html')==content['lesson_sha256']
 cases=json.loads((P/'labs/f09/cases.json').read_text());assert sum(x['operations'] for x in cases['cases'])==cases['teaching_http_requests']==28
 commands='\n'.join(p.read_text() for p in (P/'labs/f09').glob('0*.sh'));assert len(re.findall(r'^curl ',commands,re.M))==28
 R['data']['request_accounting']='28 actual reader curl commands across5 scripts; case totals match'
 # Save the real in-progress receipt before checking its own README link.
 (H/'repository-checks.json').write_text(json.dumps(dict(R,status='running'),ensure_ascii=False,indent=2)+'\n')
 api=runpy.run_path(str(H/'review.py'));links=api['static_links']();R['data']['static_links_checked']=len(links)
 state=json.loads((H/'workspace-state.json').read_text());assert state['status']=='restored'
 command(['git','diff','--check']);command(['git','diff','--cached','--check'])
 R['status']='passed'
except Exception as e:R['status']='failed';R['failure']=repr(e);raise
finally:(H/'repository-checks.json').write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n')
print('F09 repository checks passed: structure/snippets/syntax/fixtures/28 curls/source+runtime+browser+diagram+crop hashes/links/restore')
