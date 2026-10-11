"""Verify the chapter's exact pinned source ranges against committed bytes."""
from pathlib import Path
import subprocess,json,re,hashlib
root=Path(__file__).resolve().parents[2];repo=Path('/workspace/scratch/es-v9.4.0')
revision='2e8528e92361c3399724226deaf2b46f933e925b'
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
assert git('rev-parse','HEAD').decode().strip()==revision
assert not git('status','--porcelain')
refs={}
def add(path,start,end):refs.setdefault(path,set()).add((start,end))
for path,start,end in re.findall(r'https://github.com/elastic/elasticsearch/blob/'+revision+r'/([^"#]+)#L(\d+)(?:-L(\d+))?',(root/'chapters/ch14.html').read_text()):add(path,int(start),int(end or start))
for path in json.loads((root/'.archify/review/ch14-paths.json').read_text()).values():
 for node in json.loads((root/path).with_name('candidate.json').read_text())['nodes']:
  for ref in node['sources']:add(ref['path'],ref['line'],ref.get('end_line',ref['line']))
files=[]
for path,ranges in sorted(refs.items()):
 data=git('show',revision+':'+path);local=repo/path
 if local.is_file():assert local.read_bytes()==data,path
 lines=len(data.decode().splitlines())
 for a,b in ranges:assert 1<=a<=b<=lines,(path,a,b,lines)
 files.append({'path':path,'sha256':hashlib.sha256(data).hexdigest(),'lines':lines,'localCheckoutPresent':local.is_file(),'ranges':[{'line':a,'end_line':b} for a,b in sorted(ranges)]})
report={'status':'pass','repository':'https://github.com/elastic/elasticsearch.git','revision':revision,'checkoutClean':True,'fileCount':len(files),'rangeCount':sum(len(f['ranges']) for f in files),'files':files,'chapterSha256':hashlib.sha256((root/'chapters/ch14.html').read_bytes()).hexdigest(),'realEsApi':{'firstRun':'not-run','cleanupAndRerun':'not-run','reason':'9200 connection refused; runtime missing /proc/self/coredump_filter'}}
(root/'.archify/review/ch14-source-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'PASS: {report["fileCount"]} files / {report["rangeCount"]} exact pinned ranges; committed bytes and bounds verified.')
