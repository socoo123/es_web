"""Verify the exact pinned source ranges and ES string-hash calculation.
Run with ES_SOURCE_ROOT pointing to a clean v9.4.0 checkout.
"""
from pathlib import Path
import subprocess,json,re,hashlib,os
root=Path(__file__).resolve().parents[2]
repo=Path(os.environ.get('ES_SOURCE_ROOT','/tmp/es-ch15/es-v9.4.0'))
revision='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
assert git('rev-parse','HEAD').decode().strip()==revision
assert not git('status','--porcelain')
refs={}
def add(path,start,end):refs.setdefault(path,set()).add((start,end))
for path,start,end in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+revision+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',(root/'chapters/ch15.html').read_text()):add(path,int(start),int(end or start))
for path in json.loads((root/'.archify/review/ch15-paths.json').read_text()).values():
 spec=json.loads((root/path).with_name('candidate.json').read_text())
 for node in spec.get('nodes',spec.get('states',[])):
  for ref in node['sources']:add(ref['path'],ref['line'],ref.get('end_line',ref['line']))
def murmur_string(value):
 data=value.encode('utf-16le',errors='surrogatepass');length=len(data);h=0
 def rot(v,k):return ((v<<k)|(v>>(32-k)))&0xffffffff
 for i in range(0,length//4*4,4):
  k=int.from_bytes(data[i:i+4],'little');k=k*0xcc9e2d51&0xffffffff;k=rot(k,15);k=k*0x1b873593&0xffffffff
  h^=k;h=rot(h,13);h=(h*5+0xe6546b64)&0xffffffff
 k=int.from_bytes(data[length//4*4:],'little')
 if length%4:k=k*0xcc9e2d51&0xffffffff;k=rot(k,15);k=k*0x1b873593&0xffffffff;h^=k
 h^=length;h^=h>>16;h=h*0x85ebca6b&0xffffffff;h^=h>>13;h=h*0xc2b2ae35&0xffffffff;h^=h>>16
 return h if h<2**31 else h-2**32
test='server/src/test/java/org/elasticsearch/cluster/routing/operation/hash/murmur3/Murmur3HashFunctionTests.java'
vectors=re.findall(r'assertHash\((0x[0-9a-f]+), "([^"]+)"\)',git('show',revision+':'+test).decode())
for expected,value in vectors:assert murmur_string(value)&0xffffffff==int(expected,16),(value,expected)
add(test,18,30)
hashes={value:{'hash':murmur_string(value),'shardOf3':murmur_string(value)%3} for value in ['brown','brown-1','route-0','tenant-7']}
assert hashes['brown']=={'hash':998382972,'shardOf3':0}
assert hashes['brown-1']=={'hash':-2007555306,'shardOf3':0}
assert hashes['route-0']=={'hash':512605379,'shardOf3':2}
files=[]
for path,ranges in sorted(refs.items()):
 data=git('show',revision+':'+path);local=repo/path
 assert local.is_file() and local.read_bytes()==data,path
 lines=len(data.decode().splitlines())
 for a,b in ranges:assert 1<=a<=b<=lines,(path,a,b,lines)
 files.append({'path':path,'sha256':hashlib.sha256(data).hexdigest(),'lines':lines,'ranges':[{'line':a,'end_line':b} for a,b in sorted(ranges)]})
report={'status':'pass','repository':'https://github.com/elastic/elasticsearch.git','revision':revision,'checkoutClean':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'hashVerification':{'encoding':'UTF-16LE','algorithm':'Murmur3 x86_32 seed 0','officialVectorsPassed':len(vectors),'examples':hashes,'realApi':'verified-separately-see-ch15-es-review.json'},'chapterSha256':hashlib.sha256((root/'chapters/ch15.html').read_bytes()).hexdigest(),'realEsApi':{'firstRun':'see-ch15-es-review.json','cleanupAndRerun':'see-ch15-es-review.json','scope':'single-node; source audit does not execute API requests'}}
(root/'.archify/review/ch15-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'PASS: {report["fileCount"]} files / {report["rangeCount"]} exact pinned ranges; {len(vectors)} official hash vectors.')
