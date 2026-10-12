"""Run only ch17 registered requests twice, substituting actual PIT IDs/sort arrays."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess,json,urllib.request,urllib.error,hashlib,os,sys,copy
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
endpoint=os.environ.get('ES_ENDPOINT','http://localhost:9200').rstrip('/')
ops=json.loads(subprocess.check_output(['node','-e','global.window={};require(process.argv[1]);console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))',str(root/'experiments/ch17.js')]))
def req(m,p,b=None):
 data=b.encode() if isinstance(b,str) else json.dumps(b).encode() if b is not None else None
 r=urllib.request.Request(endpoint+p,data=data,method=m,headers={'Content-Type':'application/x-ndjson' if '_bulk' in p else 'application/json'})
 try:
  with urllib.request.urlopen(r,timeout=40) as s:status=s.status;raw=s.read().decode()
 except urllib.error.HTTPError as s:status=s.code;raw=s.read().decode()
 return {'status':status,'response':json.loads(raw) if raw else None}
identity=[{k:e.get(k) for k in ['id','method','path','body']} for e in ops]
file=out/'ch17-es-review.json'
if '--validate-only' in sys.argv:
 report=json.loads(file.read_text());assert report['registeredRequests']==identity
else:
 version=req('GET','/');v=version['response']['version'];assert (v['number'],v['lucene_version'],v['build_hash'])==('9.4.0','10.4.0','2e8528e92361c3399724226deaf2b46f933e925b')
 nodes=req('GET','/_nodes?filter_path=nodes.*.version');assert len(nodes['response']['nodes'])==1
 report={'kind':'real-es-api','endpoint':endpoint,'version':version,'nodes':nodes,'reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'experimentSha256':hashlib.sha256((root/'experiments/ch17.js').read_bytes()).hexdigest(),'registeredRequests':identity,'preCleanup':[],'runs':[]}
 for name in ['tut-l17-timeout','tut-l17-pit']:report['preCleanup'].append({'path':'/'+name,**req('DELETE','/'+name+'?ignore_unavailable=true')})
 for n in [1,2]:
  pit=None;lastsort=None;run={'run':n,'operations':[]};report['runs'].append(run)
  for e in ops:
   b=copy.deepcopy(e.get('body'));num=int(e['id'].split('-')[1])
   if isinstance(b,dict) and 'pit' in b:b['pit']['id']=pit
   if num==26:b['search_after']=lastsort
   if num==14:b['id']=pit
   result=req(e['method'],e['path'],b)
   row={'id':e['id'],'method':e['method'],'path':e['path'],'body':b,**result};run['operations'].append(row)
   v=result['response']
   if num==8:pit=v.get('id')
   if isinstance(v,dict) and 'pit_id' in v:pit=v['pit_id']
   if num==10:lastsort=v['hits']['hits'][-1]['sort']
   print(n,e['id'],result['status'],('timed_out='+str(v.get('timed_out'))) if isinstance(v,dict) and 'timed_out' in v else '',flush=True)
   report['status']='collected-validation-pending';file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for run in report['runs']:
 rows={int(r['id'].split('-')[1]):r for r in run['operations']}
 def R(n):return rows[n]['response']
 for n,r in rows.items():assert r['status']=={5:429,11:201,27:404,30:400}.get(n,200),(n,r)
 for n in [0,6,16,17,22]:assert R(n)['acknowledged']
 for n in [18,24]:assert R(n)['status']=='green' and not R(n)['timed_out'] and R(n)['active_primary_shards']==1
 st=R(19)['tut-l17-timeout']['settings'];assert st['index.refresh_interval']=='-1' and st['index.requests.cache.enable']=='false'
 for n,c in [(1,3),(3,3000),(7,5)]:assert not R(n)['errors'] and len(R(n)['items'])==c and all(i['index']['status']==201 for i in R(n)['items'])
 assert [t['token'] for t in R(20)['tokens']]==['quick','brown']
 assert R(21)['valid'] and 'title:quick' in R(21)['explanations'][0]['explanation'] and 'title:brown' in R(21)['explanations'][0]['explanation']
 def ids(n):return [h['_id'] for h in R(n)['hits']['hits']]
 assert ids(23)==['1'] and 'highlight' in R(23)['hits']['hits'][0]
 prof=json.dumps(R(23)['profile']);assert 'n:[' in prof,prof
 explanation=json.dumps(R(23)['hits']['hits'][0]['_explanation']);assert 'n:[' in explanation,explanation
 assert not R(2)['timed_out'] and R(2)['hits']['total']=={'value':3,'relation':'eq'}
 assert R(28)['count']==3003 and not R(29)['timed_out'] and R(29)['hits']['total']['value']==3003
 assert R(30)['error']['type']=='search_phase_execution_exception' and 'maximum number of statements' in json.dumps(R(30))
 assert R(4)['timed_out'] and R(5)['error']['type']=='search_phase_execution_exception' and R(5)['error']['root_cause'][0]['type']=='search_timeout_exception'
 def contexts(n):return R(n)['indices']['tut-l17-pit']['primaries']['search']['open_contexts']
 assert contexts(9)==contexts(25)+1 and contexts(15)==contexts(25)
 assert R(8)['_shards']['successful']==1 and ids(10)==['1','2'] and len(R(10)['hits']['hits'][-1]['sort'])==2 and R(10)['hits']['total']['value']==3
 assert R(11)['result']=='created' and ids(26)==['4'] and R(26)['hits']['total']['value']==3
 assert rows[26]['body']['search_after']==R(10)['hits']['hits'][-1]['sort']
 assert ids(12)==['1','2','4'] and ids(31)==['3'] and ids(13)==['1','2','4','new'] and R(13)['hits']['total']['value']==4
 assert R(14)=={'succeeded':True,'num_freed':1}
 assert R(27)['error']['type']=='search_phase_execution_exception' and R(27)['error']['root_cause'][0]['type']=='search_context_missing_exception'
 # Only manual substitutions may differ from registration; each later request consumes the latest PIT token.
 token=None
 for registered,actual in zip(identity,run['operations']):
  expected=copy.deepcopy(registered['body']);num=int(registered['id'].split('-')[1])
  if isinstance(expected,dict) and 'pit' in expected:expected['pit']['id']=token
  if num==26:expected['search_after']=R(10)['hits']['hits'][-1]['sort']
  if num==14:expected['id']=token
  assert actual['body']==expected and actual['method']==registered['method'] and actual['path']==registered['path']
  if num==8:token=actual['response']['id']
  if isinstance(actual['response'],dict) and 'pit_id' in actual['response']:token=actual['response']['pit_id']
 run['status']='pass';run['verified']=['32-status-codes','explicit-settings-health-and-mapping','analyze-and-validate-query','alias-filter-profile-explain-highlight','script-loop-400-distinct-from-timeout','legal-script-baseline-3003','timed-out-partial-200-and-strict-429','local-context-baseline-plus-one-back-to-baseline','latest-pit-id-every-request','complete-sort-search-after','old-view-three-new-view-four','same-pit-new-query','close-one-and-closed-id-404','both-indexes-cleaned']
report['postCleanup']=[{'path':'/'+name,**req('HEAD','/'+name)} for name in ['tut-l17-timeout','tut-l17-pit','tut-l17-filtered']]
assert all(r['status']==404 for r in report['postCleanup'])
report['status']='pass';report['requestIdentityVerified']=True;report['reviewedExperimentSha256']=hashlib.sha256((root/'experiments/ch17.js').read_bytes()).hexdigest();file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: two runs × 32 actual requests; chapter resources absent.')
