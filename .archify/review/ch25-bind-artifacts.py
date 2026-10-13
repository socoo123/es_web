"""Bind current artifacts and actual visual inspection; keep API/native limits explicit."""
from pathlib import Path
import json,hashlib,re,subprocess
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
visual=json.loads((out/'ch25-visual-review.json').read_text());assert visual['status']=='reviewed'
for c in visual['captures']:assert sha(out/c['path'])==c['sha256'],c['path']
for p in ['chapters/ch25.html','experiments/ch25.js']:assert sha(root/p)==visual['files'][p]
checks={}
for name in ['http','scroll','source','mechanism']:
 d=json.loads((out/f'ch25-{name}-review.json').read_text());assert d['status']=='pass';checks[name]='pass'
 assert d['experimentSha256']==sha(root/'experiments/ch25.js')
 if name!='mechanism':assert d['chapterSha256']==sha(root/'chapters/ch25.html')
api=json.loads((out/'ch25-es-runtime.json').read_text());assert api['status']=='not-run' and api['responsesSynthesized'] is False and api['startupErrors']
checks['realEsApi']='not-run-official-runtime-startup-failed'
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch25.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root));ids=[e['id'] for e in ops]
old=json.loads((out/'ch25-original-ids.json').read_text());assert len(ids)==len(set(ids))==29 and len(old)==14 and set(old)<=set(ids)
assert re.findall(r'data-exp="([^"]+)"',(root/'chapters/ch25.html').read_text())==ids
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD']) and (root/'.nojekyll').is_file()
diagrams=[]
for slug,p in json.loads((out/'ch25-paths.json').read_text()).items():
 p=root/p;c=p.with_name('candidate.json');receipt=p.with_suffix('.finalize.json');d=json.loads(receipt.read_text())
 assert d['ok'] is False and d['failedStage']=='browser-check'
 assert d['specification']['sha256']==sha(c) and d['artifact']['sha256']==sha(p)
 for key in ['validate','deliver','check']:assert d['stages'][key]['status']=='pass'
 v=d['stages']['validate']['receipt']['validation'];assert v['checksPassed']==v['checkCount']==9 and v['errors']==v['warnings']==0
 check=d['stages']['check']['receipt'];assert len(check['checks'])==9 and all(c['ok'] for c in check['checks']) and check['composition']['summary']=={'errors':0,'warnings':0}
 assert d['stages']['browser-check']['status']=='fail' and 'ERR_BLOCKED_BY_ADMINISTRATOR' in json.dumps(d['stages']['browser-check'])
 diagrams.append({'slug':slug,'candidate':str(c.relative_to(root)),'candidateSha256':sha(c),'html':str(p.relative_to(root)),'htmlSha256':sha(p),'receipt':str(receipt.relative_to(root)),'gates':{k:s['status'] for k,s in d['stages'].items()},'finalizeOverall':'fail-native-file-navigation-policy'})
checks['nativeBrowserCheck']='fail-file-navigation-blocked-by-administrator'
files=[root/'chapters/ch25.html',root/'experiments/ch25.js',root/'index.html',root/'STATUS.md',root/'.archify/CH24-REVIEW.md',root/'.archify/ARCHIFY-LICENSE.txt']
files+=sorted(p for p in out.glob('ch25-*') if p.is_file() and p.name!='ch25-artifacts.json')
for d in diagrams:files+=sorted(p for p in (root/d['html']).parent.rglob('*') if p.is_file())
report={'status':'verified-with-recorded-runtime-limits','kind':'final-artifact-binding','checks':checks,'originalIdsPreserved':14,'orderedUniqueOperations':29,'diagrams':diagrams,'actualVisualReview':'reviewed-see-ch25-visual-review.json','files':[{'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files],'limitations':['Real ES requests and repeatability not run because official runtime failed at missing proc file.','Native browser-check failed at managed file navigation policy; independent HTTP pass does not replace it.']}
(out/'ch25-artifacts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Bound final sources, native/HTTP records, 14/29 IDs and actual captures. Real ES and native file-browser limits remain explicit.')
