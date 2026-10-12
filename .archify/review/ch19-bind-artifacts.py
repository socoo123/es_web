"""Bind checked artifacts; require an existing, current actual visual-review record."""
from pathlib import Path
import json,hashlib,re,subprocess
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
visual=json.loads((out/'ch19-visual-review.json').read_text());assert visual['status']=='reviewed'
for c in visual['captures']:assert sha(out/c['path'])==c['sha256']
for p in ['chapters/ch19.html','experiments/ch19.js']:assert sha(root/p)==visual['files'][p]
checks={}
for name in ['http','scroll','es','source']:
 d=json.loads((out/f'ch19-{name}-review.json').read_text());assert d['status']=='pass';checks[name]='pass'
for name in ['http','scroll','source']:
 d=json.loads((out/f'ch19-{name}-review.json').read_text());assert d['chapterSha256']==sha(root/'chapters/ch19.html')
for name in ['http','scroll','es','mechanism']:
 d=json.loads((out/f'ch19-{name}-review.json').read_text());assert d['experimentSha256']==sha(root/'experiments/ch19.js')
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch19.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root));ids=[e['id'] for e in ops]
old=json.loads((out/'ch19-original-ids.json').read_text());assert len(ids)==30 and len(set(ids))==30 and len(old)==17 and set(old)<=set(ids)
slots=re.findall(r'data-exp="([^"]+)"',(root/'chapters/ch19.html').read_text());assert slots==ids
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD']);assert (root/'.nojekyll').is_file()
diagrams=[]
for slug,p in json.loads((out/'ch19-paths.json').read_text()).items():
 p=root/p;c=p.with_name('candidate.json');receipt=p.parent/'review-2'/f'{slug}.finalize.json';d=json.loads(receipt.read_text());assert d['ok'] and all(s['status']=='pass' for s in d['stages'].values())
 assert d['specification']['sha256']==sha(c) and d['artifact']['sha256']==sha(p)
 for stage in ['validate','check']:
  r=d['stages'][stage]['receipt'];v=r.get('validation',r.get('checks',{}))
  if stage=='validate':assert v['checksPassed']==v['checkCount']==9 and v['errors']==v['warnings']==0
  else:assert len(r['checks'])==9 and all(c['ok'] for c in r['checks']) and r['composition']['summary']=={'errors':0,'warnings':0}
 diagrams.append({'slug':slug,'candidate':str(c.relative_to(root)),'candidateSha256':sha(c),'html':str(p.relative_to(root)),'htmlSha256':sha(p),'receipt':str(receipt.relative_to(root)),'gates':{k:s['status'] for k,s in d['stages'].items()}})
files=[root/'chapters/ch19.html',root/'experiments/ch19.js',root/'STATUS.md',root/'.archify/CH19-REVIEW.md',root/'.archify/ARCHIFY-LICENSE.txt']
files+=sorted(p for p in out.glob('ch19-*') if p.is_file() and p.name!='ch19-artifacts.json')
for d in diagrams:files+=sorted(p for p in (root/d['html']).parent.rglob('*') if p.is_file())
report={'status':'pass','kind':'final-artifact-binding','checks':checks,'originalIdsPreserved':17,'uniqueOrderedOperations':30,'diagrams':diagrams,'visualReview':'actual-reviewed-see-ch19-visual-review.json','files':[{'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files]}
(out/'ch19-artifacts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS: final diagrams, native receipts, API/HTTP/source records, actual captures, and 17/30 IDs bound.')
