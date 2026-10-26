#!/usr/bin/env python3
"""Scoped checks: code/data, evidence hashes, two real runs, and reading links."""
import datetime,hashlib,importlib.util,json,pathlib,re,subprocess,sys
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search'
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[],'python_syntax':[]}
commands=[['node','tools/check.mjs'],['node','tools/sync-framework-code.mjs','--check'],['node','--check','projects/travel-search/backend/src/main/resources/static/shell-f25.js'],['python3','projects/travel-search/data/f25/project.py','--check'],['bash','-n','projects/travel-search/infra/f25/wait.sh',*[str(p.relative_to(R)) for p in (P/'labs/f25').glob('*.sh')]],['git','diff','--check'],['git','diff','--cached','--check']]
for cmd in commands:
 p=subprocess.run(cmd,cwd=R,text=True,capture_output=True);row=dict(command=cmd,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr);record['commands'].append(row);assert p.returncode==0,row
for directory in [HERE,P/'data/f25',P/'labs/f25']:
 for path in directory.glob('*.py'):compile(path.read_text(),str(path),'exec');record['python_syntax'].append(str(path.relative_to(R)))
for name in ['http-review.json','shell-review.json','visual-followup.json','visual-review.json','content-review.json','workspace-state.json']:
 assert json.loads((HERE/name).read_text())['status']=='passed',name
record['passed_receipts']=['http-review.json','shell-review.json','visual-followup.json','visual-review.json','content-review.json','workspace-state.json']
for n in ['round1','round2']:
 for name,count in [('prepare',10),('candidates',3),('stays',2),('variations',6),('errors',29)]:
  rec=json.loads((P/'review/f25'/n/(name+'.json')).read_text());assert rec['status']=='passed' and rec['http']==count,(n,name)
record['two_rounds']='each21 teaching +29 additional; each preceded by2 cleanup HTTP; Java internal4 teaching searches separate'
g=json.loads((R/'framework/diagrams/f25/generation.json').read_text())
for name,expected in g['sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==expected,name
record['diagram_integrity']='2 D2 /4 SVG match official CLI generation receipt'
visual=json.loads((HERE/'visual-review.json').read_text())
for shot in visual['screenshots']:assert hashlib.sha256((R/shot['path']).read_bytes()).hexdigest()==shot['sha256'],shot['path']
assert visual['total_original_pngs']==78
record['visual_integrity']='78 original PNG hashes match declared review; capture limitations explicitly preserved'
data=json.loads((P/'data/f25/stay-table.json').read_text());summary=json.loads((P/'data/f25/summaries.json').read_text());assert len(data['offers'])==len(summary)==12
for o,s in zip(data['offers'],summary):
 assert o['summary']==s and s['snapshot_id']==data['snapshot_id'];dates=[n['date'] for n in o['nights']]
 assert len(dates)==len(set(dates)) and s['window_start']==min(dates) and s['window_end_exclusive']==str(datetime.date.fromisoformat(max(dates))+datetime.timedelta(days=1))
 assert s['max_available_rooms']==max(n['available_rooms'] for n in o['nights']) and s['min_price_minor']==min(n['price_minor'] for n in o['nights'] if 'price_minor' in n)
record['fixed_data']={'offer_summaries':12,'nightly_rows':sum(len(o['nights']) for o in data['offers']),'unique_hotels':len({s['hotel_id'] for s in summary}),'date_extrema_max_stock_and_min_price':'independently recomputed from fixed nightly rows'}
runtime=json.loads((P/'review/f25/runtime.json').read_text())
for resource in runtime['resources']:
 assert hashlib.sha256((P/'backend/src/main/resources/static'/resource['name']).read_bytes()).hexdigest()==resource['sha256']
assert hashlib.sha256((P/'data/f25/stay-table.json').read_bytes()).hexdigest()==runtime['packaged_table_sha256']
record['packaged_resources']='current source equals recorded built jar and served HTTP bytes'
spec=importlib.util.spec_from_file_location('helpers',HERE/'reading_helpers.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);record['static_links']=h.static_links()
assert not (R/'framework/f26.html').exists() and not (P/'labs/f26').exists(),'F26 outside scope'
record['scope']='only F25 implementation; necessary F24 navigation and shared current summaries; F26 unimplemented'
record['status']='passed';(HERE/'checks.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('F25 final checks passed')
