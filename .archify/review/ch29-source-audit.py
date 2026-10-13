"""Audit fixed source bytes, cited line ranges and stable/ordered registrations.
Semantic conclusions were checked by reading the named target methods; byte checks are separate.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,re,subprocess,hashlib,os
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
repo=Path(os.environ.get('ES_SOURCE_ROOT','/tmp/es-ch15/es-v9.4.0'));rev='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
assert git('rev-parse','HEAD').decode().strip()==rev and not git('status','--porcelain')
assert git('remote','get-url','origin').decode().strip()=='https://github.com/elastic/elasticsearch.git'
refs={}
def add(p,a,b):refs.setdefault(p,set()).add((int(a),int(b)))
html=(root/'chapters/ch29.html').read_text()
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',html):add(p,a,b or a)
for path in json.loads((out/'ch29-paths.json').read_text()).values():
 d=json.loads((root/path).with_name('candidate.json').read_text());assert d['meta']['repository']['revision']==rev
 for node in d['nodes']:
  assert node['sources']
  for s in node['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
files=[]
for p,ranges in sorted(refs.items()):
 data=git('show',rev+':'+p);assert (repo/p).read_bytes()==data,p
 lines=len(data.decode().splitlines())
 for a,b in ranges:assert 1<=a<=b<=lines,(p,a,b,lines)
 files.append({'path':p,'sha256':hashlib.sha256(data).hexdigest(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(ranges)]})
version=git('show',rev+':build-tools-internal/version.properties').decode();assert re.search(r'^lucene\s*=\s*(\S+)',version,re.M).group(1)=='10.4.0'
ops=json.loads(subprocess.check_output(['node','-e','global.window={};require("./experiments/ch29.js");console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))'],cwd=root));ids=[e['id'] for e in ops]
assert len(ids)==len(set(ids))==32 and set(json.loads((out/'ch29-original-ids.json').read_text()))<=set(ids)
assert re.findall(r'<div class="exp-slot" data-exp="([^"]+)"',html)==ids==json.loads((out/'ch29-operation-order.json').read_text())
assert all('endpoint' in e and 'auth' in e for e in ops)
assert all(e.get('body') is None for e in ops if e['method'] in ['GET','HEAD'])
for e in ops:
 if e['method'] in ['PUT','POST','DELETE']:
  path=e['path'].split('?')[0]
  assert path.startswith(('/tut-l29-','/_security/user/tut-l29-','/_security/role/tut-l29-')) or path in ['/_security/user/_has_privileges','/_security/api_key'],e
  assert '*' not in path,e
  if path=='/_security/api_key':assert e['endpoint'].endswith(':9200'),e
assert next(e for e in ops if e['id']=='ch29-21-create-data')['body']['settings']=={'number_of_shards':1,'number_of_replicas':0,'refresh_interval':'-1'}
assert next(e for e in ops if e['id']=='ch29-07-role')['body']['cluster']==[]
report={'status':'pass','kind':'pinned-source-and-registration-audit','reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'luceneVersion':'10.4.0','originalIdsPreserved':19,'orderedUniqueOperations':32,'getAndHeadBodiesAbsent':True,'explicitEndpointAndAuth':True,'chapterSha256':hashlib.sha256((root/'chapters/ch29.html').read_bytes()).hexdigest(),'experimentSha256':hashlib.sha256((root/'experiments/ch29.js').read_bytes()).hexdigest(),'realEsApi':'pass-see-ch29-es-review.json','semanticReview':'Target methods manually read; source byte/line audit verifies identity, not semantic entailment by itself.','claims':{'chain':'optional plugin before ServiceAccount/OAuth2/ApiKey/Realms; CONTINUE includes unsuccessful; SUCCESS stops; TERMINATE/errors finish','realm':'default list differs from successful-realm cache order; Basic shared by username/password realms','wrongBasic':'consumeNullUser sends authenticationFailed; not chain CONTINUE aggregation','nullToken':'fallback condition, not synonymous with never extracting any credentials; bogus key evidenced','authorization':'cluster checks or same-user grant; concrete index resource access control','disabled':'tested handler routes absent; no constructed anonymous superuser','challenges':'configured by Realms/token/API key; token defaults to HTTP TLS enablement','cleanup':'delete native user clears realm cache; repeated user/role DELETE returns404 foundfalse','coverage':'ordinary local HTTP/single native read role; no multi-node/custom realms, run-as, secondary auth, real keys, FLS/DLS or performance tests'}}
(out/'ch29-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS:',len(files),'files /',report['rangeCount'],'pinned ranges; 19 stable IDs / 32 ordered cards.')
