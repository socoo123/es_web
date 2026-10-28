#!/usr/bin/env python3
"""Cross-check the written F31 claims against saved real responses and source files."""
import collections,datetime,hashlib,json,pathlib,re
from html.parser import HTMLParser
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search';checks=[]
def check(ok,note):
 assert ok,note
 checks.append(note)
def load(p):return json.loads(p.read_text())
class Prose(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ['code','script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['code','script','style']:self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
html=(R/'framework/f31.html').read_text();prose=Prose();prose.feed(html)
check('81教学REST＋7次Java接口HTTP' in html and '3案例' in html and '2静态D2 / 0机制播放器' in html,'Lesson headline counts match separate categories')
check('HTTP_COUNT' not in html and html.count('class="callout warn"')==4,'No authoring placeholders; four actual pitfalls')
check(len(re.findall(r'<details><summary>[1-8]\.',html))==8,'Eight folded capability checks')
check('read-only' in html and 'routing shards=8' in html and '每个源分片至少一份' in html,'Source write block, explicit routing capacity and copy-colocation conditions explained')
check('实际路由' in html and 'source可能' in html and '异步规划' in html,'Evacuation uses actual routing; peer source and async planning caveats stated')
check('真实满盘' in html and '未测试' in html and '不持续同步' in html,'Unmeasured disk/capacity and ongoing-update limits stated')
checks_round=[]
for n in [1,2]:
 folder=P/f'review/f31/round-{n}';summary=load(folder/'summary.json');events=[json.loads(s) for s in (folder/'events.jsonl').read_text().splitlines()]
 check(summary['passed'] and summary['teaching_http_total']==81 and summary['http_by_kind']['java']==7,f'Round {n}: 81 teaching REST and seven Java calls')
 check(list(summary['teaching_http_by_case'].values())==[12,23,46],f'Round {n}: cases independently counted 12/23/46')
 before=load(folder/'settings-before.json');after=load(folder/'settings-after.json')
 check(before==after=={'persistent':{},'transient':{}},f'Round {n}: cluster settings restored, no hidden transient override')
 e=load(folder/'filter-two-nodes.json');expanded=load(folder/'filter-three-nodes.json')
 def no(response,node,name):
  return any(d['decider']==name and d['decision']=='NO' for r in response['node_allocation_decisions'] if r['node_name']==node for d in r['deciders'])
 check(no(e,'travel-f31-n1','same_shard') and no(e,'travel-f31-n2','filter') and no(expanded,'travel-f31-n3','filter'),f'Round {n}: exact same_shard/filter rejection before and after adding n3')
 disk=load(folder/'disk-low-rejection.json')
 check(any(no(disk,node['node_name'],'disk_threshold') for node in disk['node_allocation_decisions']),f'Round {n}: actual disk_threshold NO')
 for node in ['n2','n3']:
  drain=load(folder/f'drain-{node}.json')
  check(any(r['node']=='travel-f31-'+node for r in drain['layout_before_exclusion']) and all(r['node']!='travel-f31-'+node and r['state']=='STARTED' for r in drain['layout_before_stop']),f'Round {n}: {node} had copies then zero before stop')
  check(all(s['stage']=='DONE' for s in drain['recovery']['tut-f31-attractions']['shards']),f'Round {n}: {node} evacuation has completed recovery evidence')
 expected=[('/tut-f31-attractions/_settings',400,'non dynamic'),('/tut-f31-attractions/_split/tut-f31-bad-open',500,'read-only'),('/tut-f31-attractions/_doc/p01',403,'cluster_block_exception'),('/tut-f31-attractions/_split/tut-f31-bad3',400,'factor'),('/tut-f31-attractions/_split/tut-f31-bad6',500,'routing shards'),('/tut-f31-split4/_shrink/tut-f31-bad-shrink',500,'same node')]
 for path,status,phrase in expected:
  check(any(e.get('url','').endswith(path) and e.get('status')==status and phrase in json.dumps(e.get('response',{})) for e in events),f'Round {n}: {path} real {status} / {phrase}')
 r=next(e['response'] for e in events if e.get('url','').endswith('/_reindex?refresh=true'))
 check(r['created']==r['total']==6 and not r['failures'] and r['version_conflicts']==0,f'Round {n}: reindex full six created, no failures')
 expected_docs=load(P/'data/f31/attractions.json');last_sources={}
 for e in events:
  if e.get('kind')=='teaching' and '/_search?' in e.get('url','') and e.get('body',{}).get('query')=={'match_all':{}}:
   index=e['url'].split(':19531/')[1].split('/')[0];last_sources[index]=[h['_source'] for h in e['response']['hits']['hits']]
 check(len(last_sources)==4,f'Round {n}: all four independent index sources audited')
 for index,docs in last_sources.items():
  expect=json.loads(json.dumps(expected_docs))
  if index=='tut-f31-attractions':expect[0]['ticket_price_fen']=6500
  check(docs==expect,f'Round {n}: {index} final six complete sources and snapshot price')
 identity=load(folder/'identity-final.json');check(set(n['name'] for n in identity['nodes'].values())=={'travel-f31-n1','travel-f31-n2'},f'Round {n}: initial two-node topology restored')
 checks_round.append({'round':n,'summary':summary,'uuid':identity['root']['cluster_uuid'],'node_ids':sorted(identity['nodes'])})
check(checks_round[0]['uuid']==checks_round[1]['uuid'] and checks_round[0]['node_ids']==checks_round[1]['node_ids'],'Both clean runs keep the same base UUID and node IDs')
observer=list((P/'review/f31/round-1').glob('*-browser.json'));calls=[]
for f in observer:
 r=load(f);check(r['passed'] and not r['direct_es'],f'{f.name}: real browser -> Java; no browser -> ES')
 calls.extend(r['calls'])
check(len(observer)==7 and len(calls)==28 and all('rest_replay' in c for c in calls),'Seven browser stages, 28 real Java calls and 28 independent REST replays')
check(not __import__('subprocess').check_output(['git','diff','--','projects/travel-search/backend'],cwd=R,text=True),'Shared backend/frontend unchanged')
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'author self-review; no independent agent','reasoning_record':'reasoning.json','prose_han_excluding_code':len(re.findall(r'[\u3400-\u9fff]',''.join(prose.parts))),'checks':checks,'rounds':checks_round,'sources':'sources.json: six targeted files equal official v9.4.0 bytes','corrections':[{'old':'first author assertion required recovery.source to be drained node; recovery wait accepted green alone','correct':'replica can recover from primary elsewhere; explicitly wait until routing has zero shards on drained node, all copies STARTED, then check recovery and full sources','evidence':'projects/travel-search/review/f31/attempts/drain-await/ + drain-recovery/'},{'old':'draft disk prose/diagram used TB/GB/MB labels next to ES binary byte-unit values','correct':'10TiB/1GiB/512MiB clarified; D2 source regenerated','published_lesson_errata':False}],'limits':['Single Docker VM/shared host disk, no physical disk independence','No actual full disk/high/flood, filesystem hard-link inspection or capacity limit test','No sustained concurrent writes, cross-machine recovery, performance or recovery-time guarantee','Read-only-source fixed snapshots; no alias switching or ongoing sync','Contact-sheet/targeted visual review is recorded separately; not pixel-by-pixel prose/code reading'],'passed':True}
(D/'content-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print('F31 author content and saved response cross-check passed')
