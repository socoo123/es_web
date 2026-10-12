"""Execute ch20 registered requests twice, validate real responses, and point-clean."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess,json,urllib.request,urllib.error,os,hashlib,sys,math
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
endpoint=os.environ.get('ES_ENDPOINT','http://localhost:9200').rstrip('/')
ops=json.loads(subprocess.check_output(['node','-e','global.window={};require(process.argv[1]);console.log(JSON.stringify(Object.values(window.ESEXPERIMENTS)))',str(root/'experiments/ch20.js')]))
identity=[{k:e.get(k) for k in ['id','method','path','body']} for e in ops];name='/tut-l20-bm25'
def req(m,p,b=None):
 assert m not in ['GET','HEAD'] or b is None
 data=b.encode() if isinstance(b,str) else json.dumps(b).encode() if b is not None else None
 r=urllib.request.Request(endpoint+p,data=data,method=m,headers={'Content-Type':'application/x-ndjson' if '_bulk' in p else 'application/json'})
 try:
  with urllib.request.urlopen(r,timeout=30) as s:status=s.status;raw=s.read().decode()
 except urllib.error.HTTPError as s:status=s.code;raw=s.read().decode()
 return {'status':status,'response':json.loads(raw) if raw else None}
file=out/'ch20-es-review.json'
def save():file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if '--validate-only' in sys.argv or '--reuse-collected' in sys.argv:report=json.loads(file.read_text());assert report['registeredRequests']==identity
else:
 version=req('GET','/');v=version['response']['version'];assert (v['number'],v['lucene_version'],v['build_hash'])==('9.4.0','10.4.0','2e8528e92361c3399724226deaf2b46f933e925b')
 nodes=req('GET','/_nodes?filter_path=nodes.*.version');assert len(nodes['response']['nodes'])==1
 initial=req('HEAD',name);assert initial['status']==404,'Start from empty chapter index; point-clean before rerun.'
 report={'kind':'real-es-api','endpoint':endpoint,'version':version,'nodes':nodes,'reviewedAt':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'registeredRequests':identity,'initialResource':initial,'runs':[]}
 for n in [1,2]:
  run={'run':n,'operations':[]};report['runs'].append(run)
  for e in ops:
   r=req(e['method'],e['path'],e.get('body'));run['operations'].append({**{k:e.get(k) for k in ['id','method','path','body']},**r});report['status']='collected-validation-pending';save();print(n,e['id'],r['status'],flush=True)
def flatten(e):return [e]+[n for d in e.get('details',[]) for n in flatten(d)]
def close(a,b):assert math.isclose(a,b,rel_tol=2e-6,abs_tol=2e-7),(a,b)
def stat(e,N,n,dl=2,avg=2):
 nodes=flatten(e)
 def val(prefix):return next(x['value'] for x in nodes if x['description'].startswith(prefix))
 for k,t in [('boost',2.2),('N,',N),('n,',n),('dl,',dl),('avgdl,',avg),('k1,',1.2),('b,',.75)]:close(val(k),t)
for run in report['runs']:
 rows={int(r['id'].split('-')[1]):r for r in run['operations']}
 assert [{k:r.get(k) for k in ['id','method','path','body']} for r in run['operations']]==identity
 for n,r in rows.items():assert r['status']==(404 if n==17 else 400 if n==25 else 201 if n in [9,28] else 200),(n,r)
 def R(n):return rows[n]['response']
 def hits(n):return R(n)['hits']['hits']
 def scores(n,ids,values):
  hs=hits(n);assert [h['_id'] for h in hs]==ids,(n,hs)
  for h,v in zip(hs,values):close(h['_score'],v)
 assert R(0)['acknowledged'] and R(0)['shards_acknowledged'] and R(11)['acknowledged']
 assert R(12)['status']=='green' and not R(12)['timed_out'] and R(12)['active_primary_shards']==1
 setting=R(13)[name[1:]]['settings'];expected=next(e['body'] for e in ops if e['id'].startswith('ch20-00-'))
 for k,v in [('number_of_shards','1'),('number_of_replicas','0'),('auto_expand_replicas','false'),('refresh_interval','-1'),('requests.cache.enable','false'),('default_pipeline','_none'),('final_pipeline','_none'),('mapping.source.mode','stored')]:assert setting['index.'+k]==v
 normalized=json.loads(json.dumps(expected['mappings']));normalized['properties']['title'].pop('norms');normalized['properties']['views'].pop('doc_values');assert R(13)[name[1:]]['mappings']==normalized
 assert not R(1)['errors'] and all(i['index']['result']=='created' and i['index']['status']==201 for i in R(1)['items'])
 docs=R(14)['docs'];a,b=[d['term_vectors']['title'] for d in docs]
 assert a['field_statistics']==b['field_statistics']=={'sum_doc_freq':3,'doc_count':2,'sum_ttf':4}
 assert a['terms']['elasticsearch']['term_freq']==1 and a['terms']['tutorial']['term_freq']==1 and b['terms']['elasticsearch']['term_freq']==2
 assert a['terms']['elasticsearch']['doc_freq']==2 and a['terms']['tutorial']['doc_freq']==1
 scores(2,['b','a'],[.25069216,.18232156]);scores(3,['a','b'],[.8754687,.25069216]);scores(4,['b','a'],[.25069216,.18232156])
 for hit in hits(4):close(hit['_explanation']['value'],hit['_score']);stat(hit['_explanation'],2,2)
 assert R(5)['matched'];close(R(5)['explanation']['value'],.18232156);stat(R(5)['explanation'],2,2)
 assert R(15)['hits']['total']['value']==2 and len(hits(15))==1 and hits(15)[0]['_id']=='a' and '_explanation' in hits(15)[0]
 assert not R(16)['matched'] and R(16)['explanation']['value']==0
 assert not R(17)['matched'] and R(17)['_id']=='missing' and 'explanation' not in R(17)
 scores(6,['b','a'],[.5013843,.36464313]);scores(18,['b','a'],[25.069216,8.754687]);scores(19,['a','b'],[.18232156,0])
 assert len(hits(20))==2 and {h['_id'] for h in hits(20)}=={'a','b'} and all(h['_score']==2 for h in hits(20))
 assert [h['_id'] for h in hits(7)]==['b','a'] and all(h['_score'] is None for h in hits(7)) and [h['sort'] for h in hits(7)]==[[100],[10]]
 scores(8,['b','a'],[.25069216,.8754687]);assert [h['sort'] for h in hits(8)]==[[100],[10]]
 scores(21,['a','b'],[.8754687,.25069216]);scores(22,['b','a'],[.25069216,.18232156]);scores(23,['a','b'],[4.559665,.25069216]);scores(24,['a','b'],[4.559665,.25069216])
 assert any('secondaryWeight' in x['description'] for x in flatten(hits(23)[0]['_explanation']))
 assert all('sort' not in h for n in [21,24] for h in hits(n))
 assert 'Cannot use [sort] option in conjunction with [rescore]' in json.dumps(R(25))
 scores(26,['b','a'],[.25069216,.18232156]);assert R(9)['result']==R(28)['result']=='created'
 scores(10,['b','a'],[.646255,.4700036])
 for n in [27,29]:assert R(n)['matched'];close(R(n)['explanation']['value'],.4700036);stat(R(n)['explanation'],3,2)
 run.update(status='pass',verified=['30-exact-registered-requests','explicit-settings-mapping','fresh-fixed-ids-and-field-TF-DF','BM25-Legacy-boost2.2-and-full-tree-parameters','two-explain-entries-window-nonmatch-missing','constant-views-zero-replace','field-sort-track-scores-score-sort','local-rescore-window1-versus2','score-sort-allowed-field-sort-rejected','request-options-do-not-persist','field-docCount3-versus-index-docCount4','point-clean-then-rebuild'])
if '--validate-only' not in sys.argv:
 report['supplemental']=[]
 def observe(label,m,p,b=None):
  r=req(m,p,b);report['supplemental'].append({'name':label,'method':m,'path':p,'body':b,**r});save();return r
 create=ops[0];bulk=next(e for e in ops if e['id'].startswith('ch20-01-'))
 assert observe('fresh-setup',create['method'],create['path'],create['body'])['response']['acknowledged']
 repeat=observe('repeat-create',create['method'],create['path'],create['body']);assert repeat['status']==400 and repeat['response']['error']['type']=='resource_already_exists_exception'
 first=observe('fresh-bulk',bulk['method'],bulk['path'],bulk['body']);assert all(i['index']['status']==201 for i in first['response']['items'])
 e=next(e for e in ops if e['id'].startswith('ch20-22-'));b=json.loads(json.dumps(e['body']));b['rescore']['query']['query_weight']=2
 r=observe('window-outside-still-multiplies-query-weight','POST',name+'/_search',b);hs=r['response']['hits']['hits'];close(hs[0]['_score'],.5013843);close(hs[1]['_score'],.36464313)
 r=observe('score-asc-not-allowed','POST',name+'/_search',{'query':{'match_all':{}},'sort':[{'_score':'asc'}],'rescore':e['body']['rescore']});assert r['status']==400
 w=observe('unrefreshed-write','PUT',name+'/_doc/unrefreshed',{'title':'elasticsearch tutorial','views':3});assert w['status']==201
 assert observe('realtime-get-unrefreshed','GET',name+'/_doc/unrefreshed')['response']['found']
 r=observe('explain-unrefreshed-not-realtime','POST',name+'/_explain/unrefreshed',{'query':{'match':{'title':'elasticsearch'}}});assert r['status']==404
 assert observe('explicit-refresh','POST',name+'/_refresh')['status']==200
 assert observe('explain-after-refresh','POST',name+'/_explain/unrefreshed',{'query':{'match':{'title':'elasticsearch'}}})['response']['matched']
 repeat=observe('repeat-bulk','POST',bulk['path'],bulk['body']);assert all(i['index']['result']=='updated' and i['index']['status']==200 for i in repeat['response']['items'])
 assert observe('cleanup','DELETE',name)['response']['acknowledged']
 assert observe('repeat-cleanup','DELETE',name)['status']==404
else:assert len(report['supplemental'])==13
report['postCleanup']=req('HEAD',name);assert report['postCleanup']['status']==404
report.update(status='pass',requestIdentityVerified=True,experimentSha256=hashlib.sha256((root/'experiments/ch20.js').read_bytes()).hexdigest());save();print('PASS: two rounds x30 cards, 13 supplemental real observations; chapter index absent.')
