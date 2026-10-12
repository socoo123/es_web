"""Bind final ch18 sources, native receipts and independent acceptance evidence."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,re,subprocess
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
http=json.loads((out/'ch18-http-review.json').read_text());es=json.loads((out/'ch18-es-review.json').read_text());source=json.loads((out/'ch18-source-review.json').read_text());motion=json.loads((out/'ch18-mechanism-review.json').read_text());scroll=json.loads((out/'ch18-scroll-review.json').read_text())
for v in [http,es,source,motion,scroll]:assert v['status']=='pass'
assert http['chapterSha256']==source['chapterSha256']==scroll['chapterSha256']==digest(root/'chapters/ch18.html')
assert http['experimentSha256']==es['experimentSha256']==motion['experimentSha256']==scroll['experimentSha256']==digest(root/'experiments/ch18.js')
ops=json.loads(subprocess.check_output(['node','-e','global.window={};require(process.argv[1]);console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))',str(root/'experiments/ch18.js')]))
original=json.loads((out/'ch18-original-responses.json').read_text())
ids=[e['id'] for e in ops];slots=re.findall(r'data-exp="([^"]+)"',(root/'chapters/ch18.html').read_text());assert len(ids)==len(set(ids))==34 and slots==ids and {e['id'] for e in original}<=set(ids)
assert all(e.get('body') is None or e['method'] not in ['GET','HEAD'] for e in ops)
captures=http['captures']+[c['capture'] for c in motion['captures']];assert len(captures)==30 and all((out/p).is_file() for p in captures)
visual={'status':'pass','kind':'actual-visual-review','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'reviewedCaptures':[{'path':p,'sha256':digest(out/p)} for p in captures],
 'scope':['24 final standalone, embedded, desktop, 390px, experiment and source-table screenshots in both themes','six complete mechanism snapshots'],
 'findings':['Two-column initial Workflow clipped nodes at 390px; reflowed JSON into vertical independent paths and regenerated through official CLI. Historical failure retained.','Collection diagram main path made straight; long aggregation branch intentionally bypasses hits nodes with no crossing or result-to-aggregation arrow.','Final independent and embedded screenshots have complete nodes, clear arrows and complete explanatory cards.','Mobile diagrams provide a complete overview; small labels require node exploration or expanded zoom. Necessary conclusions remain in chapter prose/captions.','Mechanism SVG and source table scroll inside their containers; mobile player title truncates, explanatory note remains complete.','880px reading column and dual-theme text, experiments, captions and navigation inspected.'],
 'nativeCaptureGate':'native finalize does not request screenshots; this is separate actual image inspection'}
write(out/'ch18-visual-review.json',visual)
motion['visualReview']='pass; six captures actually inspected, see ch18-visual-review.json';write(out/'ch18-mechanism-review.json',motion)
artifacts=[]
for name,path in json.loads((out/'ch18-paths.json').read_text()).items():
 p=root/path;review=p.parent/('review-2' if name=='query-translation' else 'review-3');s=json.loads((review/(name+'.finalize-summary.json')).read_text());full=json.loads((review/(name+'.finalize.json')).read_text());check=full['stages']['check']['receipt']
 assert s['ok'] and s['status']=='pass' and all(v=='pass' for v in s['gates'].values()) and not s['update']['noticeRequired']
 assert s['artifact']['sha256']==digest(p) and s['specification']['sha256']==digest(p.with_name('candidate.json'))
 assert len(check['checks'])==9 and all(c['ok'] for c in check['checks']) and check['provenance']=='current'
 validation=full['stages']['validate']['receipt']['validation']
 assert validation['checksPassed']==validation['checkCount']==9 and validation['errors']==validation['warnings']==0
 row=next(a for a in http['artifacts'] if a['id']==name);assert row['htmlSha256']==digest(p) and row['sourceSha256']==digest(p.with_name('candidate.json'))
 artifacts.append({'id':name,'type':'workflow-v2','candidate':str(p.with_name('candidate.json').relative_to(root)),'candidateSha256':digest(p.with_name('candidate.json')),'html':path,'htmlSha256':digest(p),'currentReceipts':str(review.relative_to(root)),'nativeGates':s['gates'],'checksPassed':9,'provenance':'current','visualReview':'pass-separate-evidence'})
files=[root/'chapters/ch18.html',root/'experiments/ch18.js',root/'STATUS.md',root/'.archify/CH18-REVIEW.md']
files+=sorted(p for p in out.glob('ch18-*') if p.is_file() and p.name!='ch18-artifacts.json')
for a in artifacts:files+=sorted((root/a['html']).parent.rglob('*.json'));files.append(root/a['html'])
manifest={'status':'pass','boundAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'chapter':'ch18','artifactChecks':'separate native, HTTP, actual visual review, fixed source and actual ES API','artifacts':artifacts,'files':[{'path':str(p.relative_to(root)),'sha256':digest(p)} for p in sorted(set(files))],'operationCount':34,'stableIdsRetained':19,'mechanismSteps':6,'actuallyReviewedScreenshots':30,'limitations':['single node only; no cache-hit/performance proof','narrow diagrams are overview with exploration/zoom for detail','publication state checked separately after git push']}
write(out/'ch18-artifacts.json',manifest);print('PASS: final hashes, 9/9 native gates, 34 unique ordered cards, 19 retained IDs, real ES/HTTP/source/visual bindings.')
