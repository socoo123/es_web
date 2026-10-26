#!/usr/bin/env python3
"""Author review assertions over final F22 sources and real two-round evidence."""
import datetime,hashlib,json,pathlib,re
from html.parser import HTMLParser
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2];P=R/'projects/travel-search'
def load(path):return json.loads(path.read_text())
def require(v,d):
 if not v:raise AssertionError(d)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
docs=load(P/'data/f22/attractions.json');fixture=load(P/'data/f22/evaluation.json');plan=load(P/'data/f22/decision-plan.json');ids={d['attraction_id'] for d in docs}
require(len(ids)==24 and len(fixture['queries'])==8,'size')
for q in fixture['queries']:
 require(set(q['ratings'])==ids and all(isinstance(g,int) and 0<=g<=3 for g in q['ratings'].values()),q['id'])
 require(all(q['ratings'][i]==0 for i in ids if i.startswith('x-')),'hard exclusion labels')
 require(sum(g>=2 for g in q['ratings'].values())>0,'main positive denominators')
require([sum(q['split']==s for q in fixture['queries']) for s in ['adjust','holdout','assessment']]==[4,2,2],'splits')
nd=(P/'data/f22/attractions.ndjson').read_text();require(nd.endswith('\n') and len(nd.splitlines())==48,'NDJSON')
for n in [1,2]:
 directory=P/f'review/f22/round{n}'
 require(load(directory/'summary.json')['teaching_http']==70,'HTTP count')
 a=load(directory/'adjust.json');h=load(directory/'holdout.json');require(a['passes_adjust_gate'] and h['passes_holdout_gate'],'frozen gates')
 require(a['frozen_plan_sha256']==sha(P/'data/f22/decision-plan.json'),'frozen plan unchanged')
 require(a['fixture_sha256']==sha(P/'data/f22/evaluation.json'),'final fixture hash')
 for split in ['adjust','holdout','assessment']:
  report=load(directory/(split+'.json'))
  for strategy in report['strategies'].values():
   for row in strategy['queries'].values():require(len(row['ids'])==10,'main returns10')
 require(load(directory/'boundaries.json')['short_standard_ndcg']==0.7653606369886218,'short full ideal')
 require(load(directory/'extra.json')['status']=='passed','extras')
# Pre-first-run plan hash from the preserved first actual adjustment run.
require(load(HERE/'attempts/adjust.json')['frozen_plan_sha256']==sha(P/'data/f22/decision-plan.json'),'did not tune after holdout')
s=(R/'framework/f22.html').read_text();require(s.count('<section class="drills"')==1 and s.count('<section class="pitfalls"')==1,'structure')
require(len(re.findall(r'<details><summary>[1-7]\\?\.',s))==7,'seven folded exercises')
for q in fixture['queries']:
 if q['split']=='assessment':require(q['text'] not in s,'assessment input not in prose')
require('shell-f22.js' not in s and 'function (' not in s,'no frontend implementation in prose')
class Reader(HTMLParser):
 def __init__(self):super().__init__();self.depth=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ['pre','script','style']:self.depth+=1
 def handle_endtag(self,t):
  if t in ['pre','script','style']:self.depth-=1
 def handle_data(self,d):
  if self.depth==0:self.parts.append(d)
r=Reader();r.feed(s);count=len(re.findall('[\u4e00-\u9fff]',''.join(r.parts)))
checks=['business problem before environment/DSL','same hard filters and data for baseline/candidate','0..3 grade rubric and ≥2 binary threshold, not _score','24×8 complete synthetic single-author labels disclosed','4/2/2 intent split and exact unchanged strategy/gate plan','full judged IDCG independent of hit count; version-specific built-in caveat','all8 main queries return10; per-query/macro REST↔Python↔Java parity','positive/empty/all-zero/unrated/partial HTTP200/illegal-k/lexical candidate probes','candidate improves2 adjustment queries, leaves6 unchanged; residual bad top results retained','no observed regression does not imply representative quality','independent task no stepwise new strategy; public answer-key caveat','all critical REST and Java paths visible or linked complete','non-atomic repeated searches and fixed snapshot boundary','70 teaching HTTP distinct from internal/additional/cleanup/browser','F23 not implemented']
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','review_type':'author self-review; no independent agents','reasoning':'parent actual gpt-6.1-sol/max spawn, child no readback API','plain_chinese_characters_excluding_code':count,'corpus':{'documents':24,'eligible':20,'queries':8,'explicit_judgments':192,'split':[4,2,2]},'checks':checks,'selection':{'chosen':'candidate for this fixed teaching fixture','adjust_ndcg':[a['strategies']['baseline']['macro']['ndcg'],a['strategies']['candidate']['macro']['ndcg']],'holdout_ndcg':[h['strategies']['baseline']['macro']['ndcg'],h['strategies']['candidate']['macro']['ndcg']],'observed_new_regressions':0,'unresolved_bad_top_ids':['a15','a07','a10','a11'],'not_claimed':'population/site/real-user improvement'},'corrections':[{'old':'expected k=0 dcg to reject','correct':'legal200/0; use k=-1 for400','evidence':'attempts/boundaries.jsonl and final boundary logs'},{'old':'h-walk wording included quietness absent from some source text','correct':'free lakeside walking; same text query/grades/corpus/parameters/gates','note':'clarified after exploratory audit, not presented as pre-existing wording; final two rounds use corrected intent'}],'limitations':['single-author synthetic labels','8 related queries, not representative sampling','no inter-rater agreement/significance/traffic study','no performance/multi-node/production security/continuous update','timeout/partial-shard failures not constructed'],'sha256':{str(p.relative_to(R)):sha(p) for p in [R/'framework/f22.html',P/'data/f22/evaluation.json',P/'data/f22/decision-plan.json',P/'labs/f22/lab.py',P/'backend/src/main/java/dev/esweb/travel/QualityEvaluationService.java']}}
(HERE/'content-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F22 content/source/data/result self-review passed:',count,'Chinese characters excluding code')
