"""Check final receipts against current bytes and bind all chapter evidence."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,subprocess
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=json.loads((out/'ch30-paths.json').read_text())
gates=[];revisions={'search-handoffs':'review-4','reading-loop':'review-3'}
for name,relative in paths.items():
 html=root/relative;candidate=html.with_name('candidate.json');receipt=html.parent/revisions[name]/(name+'.finalize.json')
 d=json.loads(receipt.read_text());assert d['ok'] and d['status']=='pass'
 assert d['specification']['sha256']==sha(candidate) and d['artifact']['sha256']==sha(html)
 for stage in ['validate','deliver','check','browser-check']:assert d['stages'][stage]['status']=='pass' and d['stages'][stage]['exitCode']==0
 strict=d['stages']['check']['receipt'];assert len(strict['checks'])==9 and all(c['ok'] for c in strict['checks'])
 assert strict['composition']['summary']=={'errors':0,'warnings':0}
 gates.append({'id':name,'receipt':str(receipt.relative_to(root)),'sourceSha256':sha(candidate),'htmlSha256':sha(html),'checksPassed':9,'errors':0,'warnings':0,'nativeBrowserCheck':'pass'})
for p in ['ch30-http-review.json','ch30-source-review.json','ch30-scroll-review.json','ch30-visual-review.json']:
 d=json.loads((out/p).read_text());assert d['status'] in ['pass','reviewed']
 assert d['chapterSha256']==sha(root/'chapters/ch30.html') and d['experimentSha256']==sha(root/'experiments/ch30.js'),p
es=json.loads((out/'ch30-es-review.json').read_text());assert es['status']=='pass' and es['experimentSha256']==sha(root/'experiments/ch30.js') and es['operationCountPerRound']==20 and len(es['rounds'])==2
checks=[]
for cmd in [['node','--check','experiments/ch30.js'],['node','tools/figwidth.mjs','.archify/review/ch30-mechanism-snapshots.html'],['node','tools/check.mjs']]:
 r=subprocess.run(cmd,cwd=root,capture_output=True,text=True);assert r.returncode==0,r.stderr;checks.append({'command':cmd,'exitCode':r.returncode,'output':r.stdout})
(out/'ch30-site-check.json').write_text(json.dumps({'status':'pass','checkedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'checks':checks},ensure_ascii=False,indent=2)+'\n')
files={root/'chapters/ch30.html',root/'experiments/ch30.js',root/'STATUS.md',root/'.archify/CH30-REVIEW.md',root/'.archify/ARCHIFY-LICENSE.txt',root/'.nojekyll'}
for html in paths.values():files.update(p for p in (root/html).parent.rglob('*') if p.is_file())
for p in out.glob('ch30-*'):
 if p.is_file():files.add(p)
 elif p.is_dir():files.update(q for q in p.rglob('*') if q.is_file())
files.discard(out/'ch30-artifacts.json')
report={'status':'pass','boundAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'currentGates':gates,'separateValidation':['source','real API','official native gates','independent HTTP','visual image inspection','local scroll','site checks'],'files':[{'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)],'initialRevision':'ch30-initial-visual and older native revisions are historical, not current evidence'}
(out/'ch30-artifacts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS: current two showcase9/9/native gates, source/HTTP/visual/API bindings and final site checks;',len(files),'hashed files.')
