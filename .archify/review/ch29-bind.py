"""Bind current chapter, diagrams and actual validation receipts without modifying generated HTML."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
http=json.loads((out/'ch29-http-review.json').read_text());api=json.loads((out/'ch29-es-review.json').read_text());source=json.loads((out/'ch29-source-review.json').read_text());visual=json.loads((out/'ch29-visual-review.json').read_text())
assert all(d['status']=='pass' for d in [http,api,source,visual])
chapter=sha(root/'chapters/ch29.html');experiment=sha(root/'experiments/ch29.js')
assert http['chapterSha256']==source['chapterSha256']==chapter
assert http['experimentSha256']==source['experimentSha256']==api['experimentSha256']==experiment
paths=json.loads((out/'ch29-paths.json').read_text());rows=[]
for slug,path in paths.items():
 p=root/path;candidate=p.with_name('candidate.json');revision='review-2' if slug=='basic-path' else 'review-4';receipt=p.parent/revision/(slug+'.finalize.json');d=json.loads(receipt.read_text())
 assert d['ok'] and d['status']=='pass' and all(x['status']=='pass' for x in d['stages'].values())
 val=d['stages']['validate']['receipt']['validation'];assert val['checksPassed']==val['checkCount']==9 and val['errors']==val['warnings']==0
 assert d['specification']['sha256']==sha(candidate) and d['artifact']['sha256']==sha(p)
 h=next(a for a in http['artifacts'] if a['id']==slug);assert h['htmlSha256']==sha(p) and h['sourceSha256']==sha(candidate)
 delivery=json.loads(p.with_suffix('.delivery.json').read_text());assert delivery['specification']['sha256']==sha(candidate) and delivery['artifact']['sha256']==sha(p)
 rows.append({'id':slug,'mode':'workflow-v2','path':path,'candidateSha256':sha(candidate),'htmlSha256':sha(p),'currentFinalizeReceipt':str(receipt.relative_to(root)),'nativeGates':{k:v['status'] for k,v in d['stages'].items()},'showcase':val})
for file in ['ch29-scroll-review.json','ch29-mechanism-review.json']:
 d=json.loads((out/file).read_text());assert d['status']=='pass' and d['experimentSha256']==experiment
 if 'chapterSha256' in d:assert d['chapterSha256']==chapter
for capture in visual['captures']:
 assert sha(out/capture['path'])==capture['sha256']
files=[root/'chapters/ch29.html',root/'experiments/ch29.js',root/'index.html',root/'.archify/CH28-REVIEW.md',root/'.archify/ARCHIFY-LICENSE.txt']+sorted(p for p in out.glob('ch29-*') if p.name!='ch29-artifacts.json')
report={'status':'pass','kind':'current-artifact-and-evidence-binding','boundAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'chapterSha256':chapter,'experimentSha256':experiment,'diagrams':rows,'realEsApi':'two complete 32-card rounds and 10 supplementary checks per round passed; expanded auth/TLS/keys/FLS/DLS not run','nativeBrowser':'pass-current-local-file-browser','http':'pass-viewport-theme-interactions-deep-links','visualReview':'actually inspected captures; see separate visual record','license':'shared ARCHIFY-LICENSE.txt plus unchanged generated font notices','files':[{'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files]}
(out/'ch29-artifacts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS: current HTML/JSON/native receipts and source/API/HTTP/visual hashes bound.')
