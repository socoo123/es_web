"""Execute only ch19's registered requests twice; retain real response evidence."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess,json,urllib.request,urllib.error,os,hashlib,sys,math
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
endpoint=os.environ.get('ES_ENDPOINT','http://localhost:9200').rstrip('/')
ops=json.loads(subprocess.check_output(['node','-e','global.window={};require(process.argv[1]);console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))',str(root/'experiments/ch19.js')]))
identity=[{k:e.get(k) for k in ['id','method','path','body']} for e in ops];names=['tut-l19-'+n for n in ['shop','s0','s1','card']]
def req(m,p,b=None):
 assert b is None or m not in ['GET','HEAD']
 data=b.encode() if isinstance(b,str) else json.dumps(b).encode() if b is not None else None
 r=urllib.request.Request(endpoint+p,data=data,method=m,headers={'Content-Type':'application/x-ndjson' if '_bulk' in p else 'application/json'})
 try:
  with urllib.request.urlopen(r,timeout=30) as s:status=s.status;raw=s.read().decode()
 except urllib.error.HTTPError as s:status=s.code;raw=s.read().decode()
 return {'status':status,'response':json.loads(raw) if raw else None}
file=out/'ch19-es-review.json'
def save():file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if '--validate-only' in sys.argv:report=json.loads(file.read_text());assert report['registeredRequests']==identity
else:
 version=req('GET','/');v=version['response']['version'];assert (v['number'],v['lucene_version'],v['build_hash'])==('9.4.0','10.4.0','2e8528e92361c3399724226deaf2b46f933e925b')
 nodes=req('GET','/_nodes?filter_path=nodes.*.version');assert len(nodes['response']['nodes'])==1
 report={'kind':'real-es-api','endpoint':endpoint,'version':version,'nodes':nodes,'reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'registeredRequests':identity,'runs':[],'initialResources':[{'path':'/'+n,**req('HEAD','/'+n)} for n in names]}
 assert all(r['status']==404 for r in report['initialResources']),'Start from empty chapter resources; point-clean known resources before rerunning.'
 for n in [1,2]:
  run={'run':n,'operations':[]};report['runs'].append(run)
  for e in ops:
   r=req(e['method'],e['path'],e.get('body'));run['operations'].append({**{k:e.get(k) for k in ['id','method','path','body']},**r});report['status']='collected-validation-pending';save();print(n,e['id'],r['status'],flush=True)
for run in report['runs']:
 rows={int(r['id'].split('-')[1]):r for r in run['operations']}
 def R(n):return rows[n]['response']
 def agg(n,key='top'):return R(n)['aggregations'][key]
 def buckets(n,key='top'):return [(b['key'],b['doc_count']) for b in agg(n,key)['buckets']]
 for n,r in rows.items():assert r['status']==200,(n,r)
 assert [{k:r.get(k) for k in ['id','method','path','body']} for r in run['operations']]==identity
 for n in [0,4,5,12,16]:assert R(n)['acknowledged']
 for n,count in [(17,1),(20,2),(26,1)]:assert R(n)['status']=='green' and not R(n)['timed_out'] and R(n)['active_primary_shards']==count
 for n,count in [(1,8),(6,11),(7,11),(13,20)]:assert not R(n)['errors'] and len(R(n)['items'])==count and all(i['index']['status']==201 and i['index']['result']=='created' for i in R(n)['items'])
 assert buckets(2,'by_category')==[('books',3),('electronics',3),('clothing',2)]
 for b,target in zip(agg(2,'by_category')['buckets'],[24.99,349.99,64.99]):assert math.isclose(b['avg_price']['value'],target,abs_tol=0.0001)
 assert [b['doc_count'] for b in agg(3,'by_month')['buckets']]==[2,2,3,1]
 assert [b['key_as_string'] for b in agg(3,'by_month')['buckets']]==[f'2024-0{i}-01T00:00:00.000Z' for i in range(1,5)]
 assert buckets(3,'price_ranges')==[('*-50.0',4),('50.0-200.0',2),('200.0-*',2)]
 assert R(18)['hits']['total']['value']==8 and [h['_id'] for h in R(18)['hits']['hits']]==['2'] and buckets(18,'by_category')==buckets(2,'by_category')
 assert R(19)['hits']['total']['value']==3 and not R(19)['hits']['hits'] and buckets(19,'by_category')==[('books',3)]
 for n,expected in [(21,[('apple',6),('banana',3),('cherry',2)]),(22,[('apple',4),('date',4),('cherry',3)]),(8,[('apple',10),('cherry',5),('date',4),('banana',3)]),(9,[('apple',10),('date',4)]),(10,[('apple',10),('cherry',5)]),(11,[('apple',10),('cherry',5),('date',4)]),(23,[('apple',10),('banana',3)]),(24,[('cherry',5)]),(25,[('date',4)])]:assert buckets(n)==expected,(n,R(n))
 for n,other,error in [(8,0,0),(9,8,7),(10,7,0),(11,3,5),(23,9,0)]:assert agg(n)['sum_other_doc_count']==other and agg(n)['doc_count_error_upper_bound']==error,(n,R(n))
 assert [b['doc_count_error_upper_bound'] for b in agg(9)['buckets']]==[0,3]
 assert [b['doc_count_error_upper_bound'] for b in agg(10)['buckets']]==[0,0]
 # bucket_sort does not add its own removed buckets back into terms.sum_other.
 assert agg(24)['sum_other_doc_count']==7 and agg(25)['sum_other_doc_count']==0
 assert R(29)['hits']['total']['value']==10 and agg(29,'price_avg')['value']==4.2 and agg(29,'price_sum')['value']==42 and agg(29,'price_count')['value']==10
 assert buckets(14,'users')==[('u-1',1),('u-10',1)] and agg(14,'users')['sum_other_doc_count']==18 and agg(14,'users')['doc_count_error_upper_bound']==0
 assert len(buckets(27,'users'))==20 and all(c==1 for _,c in buckets(27,'users')) and agg(27,'users')['sum_other_doc_count']==0
 assert buckets(28,'users')==buckets(14,'users') and R(28)['profile']['shards'] and all(sh['aggregations'] for sh in R(28)['profile']['shards'])
 assert len(R(15)['nodes'])==1 and all({'request','parent','fielddata'}<=set(node['breakers']) for node in R(15)['nodes'].values())
 run['status']='pass';run['verified']=['30-real-registered-requests','three-local-health-waits','fixed-ID-created-and-refreshed','eight-docs-category-avg-float-tolerance','month-range-bucket-rules','hits-window-independent-and-query-input-scope','two-shard-local-global-counts','lost-cherry-error7-other8-per-bucket0-3','default-cherry-error0-other7','capacity-floor-exact-counts-with-conservative-error5','key-order-error0','pipeline-only-sees-retained-buckets-no-recount-of-other','weighted-avg42-over10','logical-cardinality20-versus-return2','profile-actual-aggregator','local-node-cumulative-breakers','point-clean-and-rebuild']
if '--validate-only' not in sys.argv:
 report['repeatabilityChecks']=[]
 def observe(name,m,p,b=None):
  r=req(m,p,b);report['repeatabilityChecks'].append({'name':name,'method':m,'path':p,'body':b,**r});save();return r
 for create,write in [(0,1),(4,6),(5,7),(12,13)]:
  c=next(e for e in ops if int(e['id'].split('-')[1])==create);b=next(e for e in ops if int(e['id'].split('-')[1])==write)
  assert observe('fresh-create',c['method'],c['path'],c['body'])['response']['acknowledged']
  s=observe('actual-settings','GET',c['path']+'/_settings?flat_settings=true')['response'][c['path'][1:]]['settings']
  for k,val in [('number_of_shards','1'),('number_of_replicas','0'),('auto_expand_replicas','false'),('refresh_interval','-1'),('requests.cache.enable','false'),('default_pipeline','_none'),('final_pipeline','_none'),('mapping.source.mode','stored')]:assert s['index.'+k]==val
  mapping=observe('actual-mapping','GET',c['path']+'/_mapping')['response'][c['path'][1:]]['mappings'];assert mapping==c['body']['mappings']
  repeat=observe('repeat-create',c['method'],c['path'],c['body']);assert repeat['status']==400 and repeat['response']['error']['type']=='resource_already_exists_exception'
  fresh=observe('fresh-bulk',b['method'],b['path'],b['body']);again=observe('repeat-bulk',b['method'],b['path'],b['body'])
  assert all(i['index']['result']=='created' and i['index']['status']==201 for i in fresh['response']['items'])
  assert all(i['index']['result']=='updated' and i['index']['status']==200 for i in again['response']['items'])
 for n in [2,8,14]:
  e=next(e for e in ops if int(e['id'].split('-')[1])==n);r=observe('same-counts-after-repeat-bulk',e['method'],e['path'],e['body']);original=next(row for row in report['runs'][0]['operations'] if row['id']==e['id']);assert r['response']==original['response']
 assert observe('cleanup','DELETE','/'+','.join(names))['response']['acknowledged']
 repeat=observe('repeat-cleanup','DELETE','/'+','.join(names));assert repeat['status']==404 and repeat['response']['error']['type']=='index_not_found_exception'
else:assert len(report['repeatabilityChecks'])==29
report['postCleanup']=[{'path':'/'+n,**req('HEAD','/'+n)} for n in names];assert all(r['status']==404 for r in report['postCleanup'])
report.update({'status':'pass','requestIdentityVerified':True,'experimentSha256':hashlib.sha256((root/'experiments/ch19.js').read_bytes()).hexdigest()});save()
print('PASS: two runs x 30 real requests, 29 repeatability observations; four resources absent.')
