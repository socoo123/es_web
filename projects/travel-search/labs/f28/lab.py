#!/usr/bin/env python3
"""F28 bounded, isolated cluster lab. Receipts record every actual HTTP and Docker command."""
import argparse, datetime, hashlib, json, os, pathlib, subprocess, time, urllib.error, urllib.request
P=pathlib.Path(__file__).resolve().parents[2]
I=P/'infra/f28'; INDEX='tut-f28-attractions'
URLS=['http://127.0.0.1:'+str(p) for p in [19228,19229,19230]]
APP=os.environ.get('APP_URL','http://127.0.0.1:18081').rstrip('/')
NAMES=['travel-f28-01','travel-f28-02','travel-f28-03']
VOLUMES=['es-framework-f28-n'+str(i)+'-data' for i in [1,2,3]]
WRONG='es-framework-f28-wrong-data'
ROLES=[{'master'},{'master','data','ingest'},{'master','data'}]
OUT=None; EVENTS=[]
def check(ok,detail):
 if not ok: raise AssertionError(detail)
def save(name,data):
 (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def event(data):
 data={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),**data}
 EVENTS.append(data)
 with (OUT/'events.jsonl').open('a') as f:f.write(json.dumps(data,ensure_ascii=False)+'\n')
def command(args,expected=0):
 p=subprocess.run(args,cwd=P,text=True,capture_output=True)
 event({'kind':'command','args':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 if expected is not None:check(p.returncode==expected,{'command':args,'exit':p.returncode,'stderr':p.stderr})
 return p

def compose(*args,extra=None):
 c=['docker','compose','-f',str(I/'compose.yaml')]
 if extra:c+=['-f',str(I/extra)]
 return command(c+list(args))
def req(path='',method='GET',body=None,node=1,expected=200,kind='teaching',raw=False):
 base=APP if node=='java' else URLS[node]
 payload=body.encode() if isinstance(body,str) else json.dumps(body,ensure_ascii=False).encode() if body is not None else None
 headers={'Content-Type':'application/x-ndjson' if raw else 'application/json'}
 request=urllib.request.Request(base+path,data=payload,method=method,headers=headers)
 try:
  with urllib.request.urlopen(request,timeout=35) as r:status=r.status; value=json.loads(r.read())
 except urllib.error.HTTPError as e:status=e.code; value=json.loads(e.read())
 except (urllib.error.URLError,TimeoutError,ConnectionError,OSError) as e:status=0;value={'connection_error':str(e)}
 event({'kind':kind,'method':method,'url':base+path,'request':body,'status':status,'response':value})
 if expected is not None:check(status==expected,{'url':base+path,'expected':expected,'status':status,'body':value})
 return status,value

def wait(nodes=3,index=False):
 path='/_cluster/health'+('/'+INDEX if index else '')+'?wait_for_nodes='+str(nodes)+'&wait_for_status=green&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=2s'
 deadline=time.monotonic()+210
 while time.monotonic()<deadline:
  s,r=req(path,expected=None,kind='wait')
  if s==200 and r['number_of_nodes']==nodes and not r.get('timed_out') and r['status']=='green':return r
  time.sleep(2)
 raise AssertionError('cluster did not reach expected green topology; inspect events and docker logs')

def identity(label,bootstrap=False):
 roots=[req(node=n)[1] for n in range(3)]
 check({x['cluster_name'] for x in roots}=={'travel-f28-lab'},roots)
 check(len({x['cluster_uuid'] for x in roots})==1 and roots[0]['cluster_uuid']!='_na_',roots)
 check([x['name'] for x in roots]==NAMES,roots)
 check(all(x['version']['number']=='9.4.0' and x['version']['lucene_version']=='10.4.0' for x in roots),roots)
 nodes=req('/_nodes/settings,jvm?flat_settings=true')[1]['nodes']
 check(len(nodes)==3,nodes)
 for name,roles in zip(NAMES,ROLES):
  node=next(n for n in nodes.values() if n['name']==name)
  check(set(node['roles'])==roles,node)
  present='cluster.initial_master_nodes' in node['settings']
  check(present==bootstrap,{'name':name,'bootstrap_should_be':bootstrap,'settings':node['settings']})
 state=req('/_cluster/state/master_node')[1]
 check(state['master_node'] in nodes,state)
 health=req('/_cluster/health?wait_for_nodes=3&timeout=5s')[1]
 check(health['number_of_nodes']==3 and health['number_of_data_nodes']==2,health)
 result={'uuid':roots[0]['cluster_uuid'],'node_ids':{n['name']:id for id,n in nodes.items()},'roles':{n['name']:n['roles'] for n in nodes.values()},'master_node':state['master_node'],'master_name':nodes[state['master_node']]['name'],'es':roots[0]['version'],'jvm':{n['name']:n['jvm']['version'] for n in nodes.values()},'bootstrap_present':bootstrap}
 save(label+'.json',result);return result

def data_check(label):
 count=req('/'+INDEX+'/_count')[1];check(count['count']==6,count)
 allhits=req('/'+INDEX+'/_search',method='POST',body={'size':100,'track_total_hits':True,'query':{'match_all':{}},'sort':[{'attraction_id':'asc'}]})[1]
 expected=json.loads((P/'data/f28/attractions.json').read_text())
 check(allhits['hits']['total']=={'value':6,'relation':'eq'} and [h['_source'] for h in allhits['hits']['hits']]==expected,allhits)
 shards=req('/_cat/shards/'+INDEX+'?format=json&h=index,shard,prirep,state,docs,node')[1]
 check(len(shards)==4 and {s['node'] for s in shards}==set(NAMES[1:]) and all(s['state']=='STARTED' for s in shards),shards)
 for shard in ['0','1']:
  pair=[s for s in shards if s['shard']==shard]
  check(len(pair)==2 and {s['prirep'] for s in pair}=={'p','r'} and len({s['node'] for s in pair})==2 and len({s['docs'] for s in pair})==1,pair)
 check(sum(int(s['docs']) for s in shards if s['prirep']=='p')==6,shards)
 save(label+'.json',{'count':6,'sources':expected,'shards':shards});return expected

def search(node=1):
 body=json.loads((P/'search/f28/search.json').read_text())
 r=req('/'+INDEX+'/_search?allow_partial_search_results=false',method='POST',body=body,node=node)[1]
 check(r['hits']['total']=={'value':2,'relation':'eq'} and [h['_id'] for h in r['hits']['hits']]==['p01','p02'] and r['_shards']['failed']==0 and not r['timed_out'],r)
 return r

def java():
 input=json.loads((P/'search/f28/input.json').read_text())
 result=req('/api/attractions/search',method='POST',body=input,node='java')[1]
 check(result['total']==2 and result['totalRelation']=='eq' and [c['id'] for c in result['items']]==['p01','p02'],result)
 body=json.loads((P/'search/f28/search.json').read_text())
 check(result['esRequest']==body,{'java':result['esRequest'],'rest':body})
 replay=req('/'+INDEX+'/_search',method='POST',body=result['esRequest'])[1]
 check([h['_id'] for h in replay['hits']['hits']]==['p01','p02'] and replay['hits']['total']=={'value':2,'relation':'eq'} and replay['_shards']['failed']==0 and not replay['timed_out'],replay)
 for hit,card in zip(replay['hits']['hits'],result['items']):
  s=hit['_source'];check(card=={'id':hit['_id'],'name':s['name'],'cityCode':s['city_code'],'ticketPriceFen':s['ticket_price_fen'],'currency':s['currency'],'status':s['status'],'score':hit['_score']},[hit,card])
 return result

def first():
 for volume in VOLUMES+[WRONG]:
  p=command(['docker','volume','inspect',volume],expected=None)
  check(p.returncode!=0,'First-start refuses existing F28 volume: '+volume+'; use existing/restart, or explicit reset for disposable lesson data.')
 compose('up','-d',extra='bootstrap.yaml');wait();before=identity('first-identity',True)
 # Replace all containers using the steady configuration: remove bootstrap immediately.
 compose('up','-d','--force-recreate');wait();a=identity('steady-identity')
 check(before['uuid']==a['uuid'] and before['node_ids']==a['node_ids'],[before,a])
 save('first-summary.json',a)

def prepare():
 error=req('/api/attractions/search','POST',json.loads((P/'search/f28/input.json').read_text()),node='java',expected=502)[1]
 check(error['code']=='SEARCH_BACKEND_REJECTED',error)
 body=json.loads((P/'search/f28/create-index.json').read_text())
 created=req('/'+INDEX,'PUT',body)[1];check(created['acknowledged'],created)
 bulk=req('/'+INDEX+'/_bulk','POST',(P/'data/f28/attractions.ndjson').read_text(),raw=True)[1]
 check(not bulk['errors'] and len(bulk['items'])==6 and all(x['create']['result']=='created' and x['create']['status']==201 for x in bulk['items']),bulk)
 req('/'+INDEX+'/_refresh','POST');wait(index=True)
 mapping=req('/'+INDEX+'/_mapping')[1][INDEX]['mappings'];check(mapping==body['mappings'],mapping)
 settings=req('/'+INDEX+'/_settings?flat_settings=true')[1][INDEX]['settings']
 for k,v in body['settings'].items():check(settings['index.'+k]==str(v),settings)
 data_check('prepared-data')
 for n in range(3):search(n)
 java()

def restart():
 before=identity('before-restart');expected=data_check('before-data')
 compose('down')
 r=req('/api/attractions/search','POST',json.loads((P/'search/f28/input.json').read_text()),node='java',expected=503)[1]
 check(r['code']=='SEARCH_UNAVAILABLE',r)
 for volume in VOLUMES:command(['docker','volume','inspect',volume])
 compose('up','-d');wait(index=True)
 after=identity('after-restart');check(before['uuid']==after['uuid'] and before['node_ids']==after['node_ids'],[before,after])
 check(data_check('after-data')==expected,'data changed')
 search();java()

def mistake():
 before=identity('before-mistake')
 check(command(['docker','volume','inspect',WRONG],expected=None).returncode!=0,'wrong volume must be new')
 compose('stop','es3');compose('up','-d','--no-deps','es3',extra='wrong.yaml')
 deadline=time.monotonic()+150
 while time.monotonic()<deadline:
  s,b=req(node=2,expected=None,kind='wait')
  state=command(['docker','inspect','es-framework-f28-es3-1','--format','{{json .State}}']).stdout
  state=json.loads(state)
  check(state['Status'] not in ['exited','dead'],state)
  if s==200 and b['cluster_uuid']!='_na_':break
  time.sleep(2)
 else:raise AssertionError('wrong single node did not start')
 wrong=req(node=2)[1];right=req(node=1)[1]
 check(wrong['cluster_name']==right['cluster_name'] and wrong['cluster_uuid']!=right['cluster_uuid'],[wrong,right])
 wh=req('/_cluster/health',node=2)[1];check(wh['number_of_nodes']==1,wh)
 req('/'+INDEX+'/_count',node=2,expected=404)
 # Keep wrong data, correct discovery settings. Existing UUID prevents merge.
 compose('up','-d','--no-deps','--force-recreate','es3',extra='join-wrong.yaml')
 deadline=time.monotonic()+150;matched=False
 while time.monotonic()<deadline:
  p=compose('logs','--no-color','es3')
  if 'This node previously joined a cluster with UUID' in p.stdout or ('received cluster state from' in p.stdout and 'different cluster uuid' in p.stdout):
   matched=True;diagnostic='join_validation_rejected';break
  if 'fully-formed single-node cluster' in p.stdout and 'different cluster UUIDs cannot belong to the same cluster' in p.stdout:
   matched=True;diagnostic='independent_cluster_does_not_discover';break
  time.sleep(2)
 check(matched,'no diagnostic for incompatible cluster identity in real logs')
 (OUT/'wrong-discovery.log').write_text(p.stdout)
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  status,bad=req(node=2,expected=None,kind='wait')
  if status==200:break
  time.sleep(2)
 else:raise AssertionError('wrong node HTTP did not become available after join rejection')
 bad=req(node=2)[1];check(bad['cluster_uuid']==wrong['cluster_uuid'],bad)
 nodes=req('/_nodes')[1]['nodes'];check(set(n['name'] for n in nodes.values())==set(NAMES[:2]),nodes)
 # Delete ONLY the wrong empty experiment directory. Original n3-data stays intact.
 compose('stop','es3');compose('rm','-f','es3',extra='join-wrong.yaml')
 command(['docker','volume','rm',WRONG]);compose('up','-d','--no-deps','es3');wait(index=True)
 after=identity('after-mistake');check(before['uuid']==after['uuid'] and before['node_ids']==after['node_ids'],[before,after])
 data_check('recovered-data');search();java()
 save('mistake-summary.json',{'main_uuid':before['uuid'],'wrong_uuid':wrong['cluster_uuid'],'same_name':right['cluster_name'],'wrong_cluster_index_status':404,'discovery_only_did_not_merge':matched,'observed_diagnostic':diagnostic,'restored_original_node_ids':after['node_ids']})

def cleanup():
 req('/'+INDEX,'DELETE',expected=200)
 req('/'+INDEX,expected=404)

def reset(confirm):
 check(confirm,'reset requires --delete-f28-data; deletes ONLY four named disposable F28 volumes')
 compose('down')
 for volume in VOLUMES+[WRONG]:
  if command(['docker','volume','inspect',volume],expected=None).returncode==0:command(['docker','volume','rm',volume])

def main():
 global OUT
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['first','prepare','restart','mistake','cleanup','reset']);p.add_argument('--out',required=True);p.add_argument('--delete-f28-data',action='store_true');a=p.parse_args()
 OUT=pathlib.Path(a.out).resolve();OUT.mkdir(parents=True,exist_ok=False)
 try:
  if a.stage=='reset':reset(a.delete_f28_data)
  else:globals()[a.stage]()
  save('summary.json',{'stage':a.stage,'passed':True,'teaching_http':sum(e['kind']=='teaching' for e in EVENTS),'wait_http':sum(e['kind']=='wait' for e in EVENTS),'commands':sum(e['kind']=='command' for e in EVENTS),'boundaries':['one Docker VM, not three physical hosts','no routing, failure-election, capacity or performance claims','no authentication: loopback-only teaching endpoints']})
  print(json.dumps(json.loads((OUT/'summary.json').read_text()),ensure_ascii=False))
 except Exception as e:
  save('failure.json',{'stage':a.stage,'error':str(e)});raise
if __name__=='__main__':main()
