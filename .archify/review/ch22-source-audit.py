"""Verify chapter and diagram references against clean, committed ES 9.4.0 bytes.
API behavior remains untested when the official runtime cannot start.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,subprocess,re,os,hashlib
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
repo=Path(os.environ.get('ES_SOURCE_ROOT','/workspace/scratch/es-v9.4.0'))
rev='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
assert git('rev-parse','HEAD').decode().strip()==rev
assert not git('status','--porcelain'), 'Source checkout must be clean'
assert git('remote','get-url','origin').decode().strip()=='https://github.com/elastic/elasticsearch.git'
refs={}
def add(p,a,b):refs.setdefault(p,set()).add((int(a),int(b)))
html=(root/'chapters/ch22.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for p in json.loads((out/'ch22-paths.json').read_text()).values():
 data=json.loads((root/p).with_name('candidate.json').read_text())
 assert data['meta']['repository']['revision']==rev
 for n in data['nodes']:
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
# Connected API/read/default evidence inspected in addition to the visible links.
extra={
 'server/src/main/java/org/elasticsearch/action/admin/cluster/state/TransportClusterStateAction.java':[(59,83),(92,120)],
 'server/src/main/java/org/elasticsearch/rest/action/admin/cluster/RestClusterGetSettingsAction.java':[(46,69),(82,93)],
 'server/src/main/java/org/elasticsearch/cluster/ClusterState.java':[(279,285),(646,654),(733,742)],
 'server/src/main/java/org/elasticsearch/rest/action/cat/RestMasterAction.java':[(48,59)],
 'server/src/main/java/org/elasticsearch/cluster/coordination/CoordinationState.java':[(603,621),(552,564),(572,585)],
 'server/src/main/java/org/elasticsearch/cluster/coordination/Reconfigurator.java':[(34,56)],
 'server/src/main/java/org/elasticsearch/cluster/coordination/Coordinator.java':[(130,136),(2050,2062),(2097,2135)],
 'server/src/main/java/org/elasticsearch/cluster/node/DiscoveryNodeRole.java':[(216,236)]}
for p,rr in extra.items():
 for a,b in rr:add(p,a,b)
files=[]
for p,ranges in sorted(refs.items()):
 data=git('show',rev+':'+p);assert (repo/p).read_bytes()==data,p
 lines=len(data.decode().splitlines())
 for a,b in ranges:assert 1<=a<=b<=lines,(p,a,b,lines)
 files.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(ranges)]})
versions=git('show',rev+':build-tools-internal/version.properties').decode()
lucene=re.search(r'^lucene\s*=\s*(\S+)',versions,re.M).group(1);assert lucene=='10.4.0'
operations=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch22.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root))
ids=[e['id'] for e in operations];old=json.loads((out/'ch22-original-ids.json').read_text());slots=re.findall(r'data-exp="([^"]+)"',html)
assert len(ids)==len(set(ids))==18 and len(old)==10 and set(old)<=set(ids) and slots==ids
assert all(e.get('body') is None for e in operations if e['method'] in ['GET','HEAD'])
assert all(e['path'].split('?')[0] in ['/tut-l22-vote','/tut-l22-vote/_mapping'] for e in operations if e['method'] in ['PUT','POST','DELETE'])
report={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'inspectedLocalSourceMatchesCommittedBytes':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'luceneVersion':lucene,'originalIdsPreserved':10,'orderedUniqueOperations':18,'getAndHeadBodiesAbsent':True,'mutationsLimitedToReservedIndex':True,'chapterSha256':hashlib.sha256((root/'chapters/ch22.html').read_bytes()).hexdigest(),'experimentSha256':hashlib.sha256((root/'experiments/ch22.js').read_bytes()).hexdigest(),'realEsApi':'not-run-see-ch22-es-runtime.json','claims':{'localParameter':'deprecated and ignored; default local applied state','snapshotTerm':'distinct from node currentTerm history','publication':'default strategy majority acceptance, optional beforeCommit hook; apply later','roles':'eligible role distinct from actual voting configuration; voting-only has transfer exceptions'}}
(out/'ch22-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS:',report['fileCount'],'files /',report['rangeCount'],'pinned source ranges; original 10 IDs retained in 18 ordered operations. API not run.')
