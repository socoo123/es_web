"""Bind delivered bytes, native gates, real API requests, HTTP checks and inspected images."""
from pathlib import Path
import json,hashlib,re,subprocess
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
visual=json.loads((out/'ch27-visual-review.json').read_text());assert visual['status']=='reviewed'
for c in visual['captures']:assert sha(out/c['path'])==c['sha256'],c['path']
for p in ['chapters/ch27.html','experiments/ch27.js']:assert sha(root/p)==visual['files'][p]
checks={}
for name in ['http','scroll','source','mechanism']:
 d=json.loads((out/f'ch27-{name}-review.json').read_text());assert d['status']=='pass';checks[name]='pass'
 assert d['experimentSha256']==sha(root/'experiments/ch27.js')
 if name!='mechanism':assert d['chapterSha256']==sha(root/'chapters/ch27.html')
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch27.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root));ids=[e['id'] for e in ops]
old=json.loads((out/'ch27-original-ids.json').read_text());assert len(ids)==len(set(ids))==42 and len(old)==14 and set(old)<=set(ids)
assert re.findall(r'data-exp="([^"]+)"',(root/'chapters/ch27.html').read_text())==ids
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD']) and (root/'.nojekyll').is_file()
api=json.loads((out/'ch27-es-review.json').read_text());assert api['status']=='pass' and api['finalResourcesAbsent'] and api['experimentSha256']==sha(root/'experiments/ch27.js')
assert len(api['rounds'])==2 and len(api['supplemental'])==13
for row in api['rounds']:
 assert row['status']=='pass' and len(row['records'])==42
 for spec,rec in zip(ops,row['records']):
  assert rec['verification']=='pass' and all(rec.get(k)==spec.get(k) for k in ['id','method','path','body'])
  if 'health' in rec['id']:assert rec['response']['number_of_nodes']==1
assert all(r['verification']=='pass' for r in api['supplemental'])
checks['realEsApi']='pass-84-requests-plus-13-supplemental-single-node'
diagrams=[]
for slug,p in json.loads((out/'ch27-paths.json').read_text()).items():
 p=root/p;c=p.with_name('candidate.json');receipt=p.parent/('review-2/avg-pages.finalize.json' if slug=='avg-pages' else 'query-plan.finalize.json');d=json.loads(receipt.read_text())
 assert d['ok'] is True and d['status']=='pass' and d['specification']['sha256']==sha(c) and d['artifact']['sha256']==sha(p)
 assert all(s['status']=='pass' for s in d['stages'].values())
 v=d['stages']['validate']['receipt']['validation'];assert v['checksPassed']==v['checkCount']==9 and v['errors']==v['warnings']==0
 check=d['stages']['check']['receipt'];assert len(check['checks'])==9 and all(c['ok'] for c in check['checks']) and check['composition']['summary']=={'errors':0,'warnings':0}
 assert d['update']['noticeRequired'] is False
 diagrams.append({'slug':slug,'type':'workflow-v2','candidate':str(c.relative_to(root)),'candidateSha256':sha(c),'html':str(p.relative_to(root)),'htmlSha256':sha(p),'receipt':str(receipt.relative_to(root)),'gates':{k:s['status'] for k,s in d['stages'].items()},'showcaseChecks':'9/9, zero errors/warnings','finalizeOverall':'pass'})
checks['nativeBrowserCheck']='pass-exact-artifact-file-snapshot'
files=[root/'chapters/ch27.html',root/'experiments/ch27.js',root/'index.html',root/'STATUS.md',root/'.archify/CH27-REVIEW.md',root/'.archify/ARCHIFY-LICENSE.txt']
files+=sorted(p for p in out.glob('ch27-*') if p.is_file() and p.name!='ch27-artifacts.json')
for directory in root.glob('.archify/*-ch27-*'):files+=sorted(p for p in directory.rglob('*') if p.is_file())
report={'status':'verified','kind':'final-artifact-binding','checks':checks,'originalIdsPreserved':14,'orderedUniqueOperations':42,'diagrams':diagrams,'actualVisualReview':'reviewed-see-ch27-visual-review.json','apiBinding':'Exact current registry bytes and all 84 id/method/path/body records match. API chapter hash is its execution-time HTML snapshot; final diagrams/score documentation edits were verified by source and HTTP afterward.','files':[{'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files],'limitations':['Single-node API does not verify cross-machine Exchange, network behavior, parallel scaling, or performance.','Actual asynchronous submission/results lifecycle, authenticated permission failures, and explicit _source result retrieval not run.','Mobile diagrams are complete overviews; fine labels use node exploration/zoom/expand and adjacent prose.']}
(out/'ch27-artifacts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: final bytes bound; 14 original IDs / 42 operations; native9/9; 84 API +13 supplemental; HTTP and actual visual review.')
