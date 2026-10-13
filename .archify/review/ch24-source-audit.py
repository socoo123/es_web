"""Check exact citations against clean ES 9.4.0 committed bytes; API status separate."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,subprocess,re,os,hashlib
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
repo=Path(os.environ.get('ES_SOURCE_ROOT','/workspace/scratch/es-v9.4.0'));rev='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
assert git('rev-parse','HEAD').decode().strip()==rev and not git('status','--porcelain')
assert git('remote','get-url','origin').decode().strip()=='https://github.com/elastic/elasticsearch.git'
refs={}
def add(p,a,b):refs.setdefault(p,set()).add((int(a),int(b)))
html=(root/'chapters/ch24.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for p in json.loads((out/'ch24-paths.json').read_text()).values():
 d=json.loads((root/p).with_name('candidate.json').read_text());assert d['meta']['repository']['revision']==rev
 for n in d['nodes']:
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
extra={
 'index/engine/InternalEngine.java':[(642,684),(3684,3699)],
 'index/engine/SoftDeletesPolicy.java':[(104,138)],
 'indices/recovery/RecoverySourceHandler.java':[(1181,1227),(1038,1082)],
 'indices/recovery/RecoverySettings.java':[(199,264)],
 'cluster/metadata/MetadataIndexStateService.java':[(169,175),(964,986)],
 'action/admin/cluster/snapshots/status/SnapshotStats.java':[(193,237)],
 'indices/recovery/plan/PeerOnlyRecoveryPlannerService.java':[(30,53)],
 'index/shard/StoreRecovery.java':[(420,435),(467,500)]}
for p,rs in extra.items():
 for a,b in rs:add('server/src/main/java/org/elasticsearch/'+p,a,b)
files=[]
for p,rs in sorted(refs.items()):
 data=git('show',rev+':'+p);assert (repo/p).read_bytes()==data,p
 lines=len(data.decode().splitlines())
 for a,b in rs:assert 1<=a<=b<=lines,(p,a,b,lines)
 files.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(rs)]})
versions=git('show',rev+':build-tools-internal/version.properties').decode();assert re.search(r'^lucene\s*=\s*(\S+)',versions,re.M).group(1)=='10.4.0'
ops=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch24.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root));ids=[e['id'] for e in ops];old=json.loads((out/'ch24-original-ids.json').read_text());assert len(ids)==len(set(ids))==57 and len(old)==20 and set(old)<=set(ids)
assert re.findall(r'data-exp="([^"]+)"',html)==ids
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD'])
for e in ops:
 path=e['path'].split('?')[0]
 if e['method'] in ['PUT','POST','DELETE']:
  assert path=='/_cluster/allocation/explain' or re.fullmatch(r'/tut-l24-(?:rec|gap|restored)(?:/_(?:doc/1|settings|flush|refresh|close|open))?',path) or re.fullmatch(r'/_snapshot/tut-l24-repo(?:/s[12](?:/_restore)?|/_verify)?',path),(e['id'],path)
for id in ['ch24-00-setup','ch24-11-gap-setup']:
 e=next(e for e in ops if e['id']==id);assert e['body']['settings']['number_of_shards']==1 and e['body']['settings']['number_of_replicas']==0 and e['body']['settings']['auto_expand_replicas']=='false' and e['body']['mappings']['properties']['marker']['type']=='keyword'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'inspectedLocalSourceMatchesCommittedBytes':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'luceneVersion':'10.4.0','originalIdsPreserved':20,'orderedUniqueOperations':57,'getAndHeadBodiesAbsent':True,'mutationsLimitedToNamedChapterResources':True,'chapterSha256':sha(root/'chapters/ch24.html'),'experimentSha256':sha(root/'experiments/ch24.js'),'realEsApi':'not-run-see-ch24-es-runtime.json','claims':{'baseline':'safe commit can precede latest commit; peer history interval differs from local translog uncommitted','history':'InternalEngine Lucene changes snapshot; lease soft-delete retention; no tlog file copy','localPreparation':'temporary local Engine before request, closed before prepare network Engine','concurrency':'initiateTracking before maxSeqNo sampling; finalize and route activation distinct','files':'isSame hash/writerUuid and grouped segment diff; plan may use snapshots','snapshots':'complete references, inline small contents, surviving-reference deletion; qualified registration outcomes'}}
(out/'ch24-source-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('PASS:',r['fileCount'],'files /',r['rangeCount'],'pinned source ranges; 20 stable IDs / 57 ordered operations. Real API not run.')
