#!/usr/bin/env python3
"""F28 author's content/evidence review. Independent review is not claimed."""
import datetime,hashlib,html,json,pathlib,re
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search'
def read(p):return json.loads(p.read_text())
def check(ok,detail):
 if not ok:raise AssertionError(detail)
page=(R/'framework/f28.html').read_text()
for section in ['goal','lesson','drills','pitfalls','recap']:check(re.search(r'<section class="'+section+'"',page),section)
check(page.count('data-d2-light=')==2,'two static diagrams')
check(page.count('<div class="callout warn">')==4,'four pitfalls')
drills=page.split('<section class="drills"')[1].split('</section>')[0];check(drills.count('<details>')==8,'eight drills')
for m in re.finditer(r'<pre\b([^>]*)><code[^>]*>([\s\S]*?)</code></pre>',page):
 attrs,body=m.groups();source=re.search('data-source="([^"]+)"',attrs)
 if source:
  lines=(R/source[1]).read_text().rstrip().splitlines();interval=re.search('data-lines="(\d+)-(\d+)"',attrs)
  if interval:lines=lines[int(interval[1])-1:int(interval[2])]
  check(html.unescape(body)=='\n'.join(lines),source[1])
check(not re.search(r'data-source="[^"]*\.js"',page),'no frontend code taught')
check(not (R/'framework/f29.html').exists(),'F29 not implemented')
rounds=[]
for n in [1,2]:
 base=P/f'review/f28/round{n}';stages={};events=[]
 for stage,total in [('first',12),('prepare',14),('restart',22),('mistake',24)]:
  summary=read(base/stage/'summary.json');check(summary['passed'] and summary['teaching_http']==total,summary)
  rows=[json.loads(x) for x in (base/stage/'events.jsonl').read_text().splitlines()]
  check(sum(r['kind']=='teaching' for r in rows)==total,stage);events.extend(rows);stages[stage]=summary
  for row in rows:
   if row.get('status')==200 and row.get('method')=='POST' and '/_search' in row.get('url',''):
    response=row['response'];check(not response['timed_out'] and response['_shards']['failed']==0,row['url'])
 identities=[read(base/path) for path in ['first/first-identity.json','first/steady-identity.json','restart/before-restart.json','restart/after-restart.json','mistake/before-mistake.json','mistake/after-mistake.json']]
 check(len({x['uuid'] for x in identities})==1,'same UUID within round')
 check(all(x['node_ids']==identities[0]['node_ids'] for x in identities),'original node IDs persisted')
 check(identities[0]['bootstrap_present'] and all(not x['bootstrap_present'] for x in identities[1:]),'bootstrap removed')
 expected=read(P/'data/f28/attractions.json')
 for path in ['prepare/prepared-data.json','restart/before-data.json','restart/after-data.json','mistake/recovered-data.json']:
  data=read(base/path);check(data['count']==6 and data['sources']==expected,path)
  shards=data['shards'];check(len(shards)==4 and sum(s['prirep']=='p' for s in shards)==2,path)
  check({s['node'] for s in shards}=={'travel-f28-02','travel-f28-03'},path)
  for id in ['0','1']:
   pair=[s for s in shards if s['shard']==id];check(len(pair)==2 and len({s['node'] for s in pair})==2 and {s['prirep'] for s in pair}=={'p','r'},pair)
 mistake=read(base/'mistake/mistake-summary.json');check(mistake['wrong_uuid']!=identities[0]['uuid'] and mistake['discovery_only_did_not_merge'],mistake)
 check(mistake['observed_diagnostic'] in ['join_validation_rejected','independent_cluster_does_not_discover'],mistake)
 log=(base/'mistake/wrong-discovery.log').read_text();check(mistake['wrong_uuid'] in log,log[:100])
 java=[r for r in events if r['kind']=='teaching' and ':18081/' in r.get('url','')]
 check([r['status'] for r in java]==[502,200,503,200,200],java)
 for row in java:
  if row['status']==200:check(row['response']['esRequest']==read(P/'search/f28/search.json'),'Java complete DSL')
 for row in events:
  if row['kind']=='teaching' and row.get('method')=='POST' and row.get('url','').endswith('/_bulk'):
   b=row['response'];check(not b['errors'] and len(b['items'])==6 and all(i['create']['status']==201 for i in b['items']),b)
 rounds.append({'round':n,'uuid':identities[0]['uuid'],'node_ids':identities[0]['node_ids'],'master_initial':identities[1]['master_name'],'master_after_restart':identities[3]['master_name'],'master_after_mistake':identities[-1]['master_name'],'wrong_uuid':mistake['wrong_uuid'],'observed_diagnostic':mistake['observed_diagnostic'],'teaching_http':sum(x['teaching_http'] for x in stages.values()),'wait_http':sum(x['wait_http'] for x in stages.values()),'java_calls':5,'java_statuses':[502,200,503,200,200],'case_http':[26,22,24],'stages':stages})
check(rounds[0]['uuid']!=rounds[1]['uuid'],'new volumes create new UUID across rounds')
check(read(P/'review/f28/between-rounds/index/summary.json')['teaching_http']==2,'explicit index cleanup')
check(read(P/'review/f28/between-rounds/volumes/summary.json')['passed'],'explicit four named volume reset')
for row in read(R/'framework/diagrams/f28/generation.json')['checks']:check(row['exit_code']==0,row)
for path,sha in read(R/'framework/diagrams/f28/generation.json')['sha256'].items():check(hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,path)
for row in read(D/'sources.json')['fixed_version_sources']:check(row['official_bytes_equal_local_v940'],row)
chinese=len(re.findall(r'[\u4e00-\u9fff]',re.sub(r'<[^>]+>','',re.sub(r'<pre\b[\s\S]*?</pre>','',page))))
checks=[
 ('业务位置','从F27的单进程进入运行拓扑；用相同查询和完整数据证明身份/角色/副本，Pages与本机服务职责明确。'),
 ('身份','同名不等于同UUID，三入口/三成员/实际master交叉核对，跨独立轮次UUID不同、每轮内部一致。'),
 ('角色与端口','三个master候选/两个data/一个ingest；每节点都协调，master与当选master分开；宿主HTTP与容器transport地址空间明确。'),
 ('首启与持久重启','初始名单只在新卷首启；实际移除后重建/完整重启，保留原UUID与node ID。master和主副归属允许变化。'),
 ('业务数据','2P+2R、p/r不同数据节点、全6份_source/字段/计数、固定查询三入口p01/p02、60元/0元，不以green或_count代替完整内容。'),
 ('Java','复用F07无新增Controller；完整查询/失败分支及客户端/异常源码可见，DSL与REST精确相等并实际重放，单入口客户端不声称HA。'),
 ('反例与恢复','专用错误空卷形成另一UUID，改seed不合并；实际日志区分明确拒绝和独立集群不发现；只删错误空卷、挂回原卷后完整核对。'),
 ('章节边界','无F29实现，不教routing或故障选举；同Docker VM不证明跨机器容灾，ingest只核角色，不冒称管道执行。'),
 ('可读与重做','880px、双主题、局部滚动/展开、复制、独立已读、8折叠练习/4陷阱；重启与删除数据重做明确分开。')]
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','reviewer':'root author self-review','independent_review':False,'reasoning_runtime':'See reasoning.json; requested gpt-6.1-sol/max cannot be set/read back by this entry point.','chinese_chars_outside_code':chinese,'cases':3,'teaching_http_per_round':72,'diagrams':2,'players':0,'drills':8,'pitfalls':4,'rounds':rounds,'checks':[{'topic':a,'finding':b} for a,b in checks],'limitations':['one Docker VM, no physical-host fault tolerance','no routing/failure election/scaling/capacity/performance/security/CDC validation','ingest role only, no pipeline execution','unchanged single ES_URL Java client, no automatic endpoint discovery/failover','HTTP reading, actual visual review, Java build and ES cluster receipts are separate']}
(D/'content-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F28 full author content/evidence self-review passed; no independent review claimed')
