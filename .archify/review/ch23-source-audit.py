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
html=(root/'chapters/ch23.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for p in json.loads((out/'ch23-paths.json').read_text()).values():
 data=json.loads((root/p).with_name('candidate.json').read_text())
 assert data['meta']['repository']['revision']==rev
 for n in data.get('nodes',data.get('states',[])):
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
# Supporting methods read for the phase, source-of-data and disk/block claims.
extra={
 'server/src/main/java/org/elasticsearch/common/unit/RelativeByteSizeValue.java':[(59,72)],
 'server/src/main/java/org/elasticsearch/cluster/routing/allocation/decider/DiskThresholdDecider.java':[(169,182),(547,558)],
 'server/src/main/java/org/elasticsearch/cluster/routing/allocation/allocator/DesiredBalanceReconciler.java':[(317,365),(487,541),(692,734)],
 'server/src/main/java/org/elasticsearch/cluster/routing/allocation/allocator/DesiredBalanceShardsAllocator.java':[(58,76),(261,268),(366,381)],
 'server/src/main/java/org/elasticsearch/cluster/routing/allocation/allocator/WeightFunction.java':[(104,133),(145,168)],
 'server/src/main/java/org/elasticsearch/cluster/routing/RoutingNodes.java':[(645,662)],
 'server/src/main/java/org/elasticsearch/rest/action/cat/RestAllocationAction.java':[(97,103),(127,135)],
 'server/src/main/java/org/elasticsearch/rest/action/admin/cluster/RestClusterAllocationExplainAction.java':[(56,91)],
 'server/src/main/java/org/elasticsearch/cluster/routing/allocation/AllocationService.java':[(825,844)]}
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
operations=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./experiments/ch23.js');console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))"],cwd=root))
ids=[e['id'] for e in operations];old=json.loads((out/'ch23-original-ids.json').read_text());slots=re.findall(r'data-exp="([^"]+)"',html)
assert len(ids)==len(set(ids))==33 and len(old)==11 and set(old)<=set(ids) and slots==ids
assert all(e.get('body') is None for e in operations if e['method'] in ['GET','HEAD'])
assert all(re.fullmatch(r'/tut-l23-(?:yellow|filter)(?:/_settings|/_doc/1)?', e['path'].split('?')[0]) for e in operations if e['method'] in ['PUT','DELETE'])
assert all(e['path'].split('?')[0]=='/_cluster/allocation/explain' for e in operations if e['method']=='POST')
report={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'inspectedLocalSourceMatchesCommittedBytes':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'luceneVersion':lucene,'originalIdsPreserved':11,'orderedUniqueOperations':33,'getAndHeadBodiesAbsent':True,'mutationsLimitedToTwoReservedIndices':True,'chapterSha256':hashlib.sha256((root/'chapters/ch23.html').read_bytes()).hexdigest(),'experimentSha256':hashlib.sha256((root/'experiments/ch23.js').read_bytes()).hexdigest(),'realEsApi':'not-run-see-ch23-es-runtime.json','claims':{'planner':'new async input; current reconcile may use prior desired balance; simulated start is not real recovery','decisions':'distinct aggregation/node orders; throttle not immediately assigned; not-preferred depends on action','relocation':'source RELOCATING stays active; paired target INITIALIZING; ordinary replica recovers from active primary','disk':'conditional headroom; forecast/relocation inputs; ordinary write block403 versus default flood block429'}}
(out/'ch23-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS:',report['fileCount'],'files /',report['rangeCount'],'pinned source ranges; original 11 IDs retained in 33 ordered operations. API not run.')
