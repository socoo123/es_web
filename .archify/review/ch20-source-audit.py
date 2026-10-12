"""Verify cited ranges against clean, committed ES v9.4.0 bytes."""
from pathlib import Path
import json,subprocess,re,os,hashlib
root=Path(__file__).resolve().parents[2];repo=Path(os.environ.get('ES_SOURCE_ROOT','/tmp/es-ch15/es-v9.4.0'));rev='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
assert git('rev-parse','HEAD').decode().strip()==rev and not git('status','--porcelain')
refs={}
def add(p,a,b):refs.setdefault(p,set()).add((int(a),int(b)))
for p,a,b in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+rev+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',(root/'chapters/ch20.html').read_text()):add(p,a,b or a)
for path in json.loads((root/'.archify/review/ch20-paths.json').read_text()).values():
 for n in json.loads((root/path).with_name('candidate.json').read_text())['nodes']:
  for s in n['sources']:add(s['path'],s['line'],s.get('end_line',s['line']))
files=[]
for path,ranges in sorted(refs.items()):
 b=git('show',rev+':'+path);assert (root/'es-src'/path).read_bytes()==b;lines=len(b.decode().splitlines())
 for a,z in ranges:assert 1<=a<=z<=lines,(path,a,z,lines)
 files.append({'path':path,'sha256':hashlib.sha256(b).hexdigest(),'ranges':[{'line':a,'end_line':z} for a,z in sorted(ranges)]})
report={'status':'pass','repository':'https://github.com/elastic/elasticsearch.git','revision':rev,'checkoutClean':True,'inspectedLocalSourceMatchesCommittedBytes':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'chapterSha256':hashlib.sha256((root/'chapters/ch20.html').read_bytes()).hexdigest(),'realEsApi':'separate ch20-es-review.json; two rounds of registered requests'}
(root/'.archify/review/ch20-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS:',report['fileCount'],'files /',report['rangeCount'],'pinned source ranges')
