#!/usr/bin/env python3
"""F29 author self-review and bounded evidence consistency check."""
import datetime,hashlib,json,pathlib,re
from html.parser import HTMLParser
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.figures=0;self.pre=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='figure':self.figures+=1
  if tag=='pre':self.pre+=1
page=(R/'framework/f29.html').read_text();parser=Page();parser.feed(page)
assert len(parser.ids)==len(set(parser.ids)) and parser.figures==2
assert len(re.findall(r'<section class="(?:goal|lesson|drills|pitfalls|recap)"',page))==5
assert page.count('<details>')>=8 and page.count('callout warn')==4
for text in ['floorMod','创建版本','routing_missing_exception','document_missing_exception','_only_nodes','profile','city_code','源码字节核对','F30']:
 assert text in page,text
fixtures=json.loads((P/'data/f29/routed.json').read_text());routes=json.loads((P/'data/f29/routes.json').read_text())
assert routes=={'right':'HZ','wrong':'SH','collision':'FZ','expected_shards':{'HZ':0,'SH':1,'FZ':0}}
for name,docs in [('attractions',[{'source':d} for d in json.loads((P/'data/f29/attractions.json').read_text())]),('routed',fixtures)]:
 b=(P/f'data/f29/{name}.ndjson').read_bytes();assert b.endswith(b'\n');lines=[json.loads(x) for x in b.splitlines()]
 assert len(lines)==12 and len(docs)==6
 for i,d in enumerate(docs):
  meta={'_id':d['source']['attraction_id']}
  if 'routing' in d:meta['routing']=d['routing']
  assert lines[2*i]=={'create':meta} and lines[2*i+1]==d['source']
summary=[]
for number in [1,2]:
 round=P/f'review/f29/round-{number}'
 counts=[]
 for action in ['default','routing','reads']:
  s=json.loads((round/action/'summary.json').read_text());assert s['passed'];counts.append(s['counts']['teaching'])
 assert counts==[21,28,13],counts
 j=json.loads((round/'java/summary.json').read_text());assert j['passed'] and j['sdk_calls']==13 and j['verification_http']==5
 default=json.loads((round/'default/default-proof.json').read_text());routing=json.loads((round/'routing/routing-proof.json').read_text());reads=json.loads((round/'reads/reads-proof.json').read_text())
 assert default['search_ids']==['p01','p02'] and routing['routes']['HZ']==routing['routes']['FZ']!=routing['routes']['SH']
 assert routing['same_shard_wrong_get_found'] and reads['filtered_ids']==['r01','r02'] and reads['wrong_routing_ids']==[]
 assert {c['primary'] for c in reads['copies']}=={True,False} and all(c['shards']['total']==1 for c in reads['copies'])
 summary.append({'round':number,'teaching_http':sum(counts),'case_http':counts,'sdk_calls':13,'verification_http':5,'actual_default_shards':default['actual_document_shards'],'copies':reads['copies']})
prose=re.sub(r'<pre\b[\s\S]*?</pre>','',page);prose=re.sub('<[^>]+>','',prose)
review=[
 {'topic':'范围与业务因果','verdict':'通过','basis':'先解释资料定位与搜索范围；仅F29，F30为遗留问题；没有新Controller或前端功能声称。'},
 {'topic':'分片组与创建版本','verdict':'通过','basis':'2主1副、逻辑6份与物理拷贝分开；新建普通未分区且无resize限定，新旧公式以索引创建版本分支。'},
 {'topic':'错值与业务路由','verdict':'通过','basis':'HZ/FZ同片、HZ/SH跨片，每轮实际_search_shards；400必填与404跨片/同片成功区分；同_id跨片重复并点名恢复。'},
 {'topic':'范围与读取拷贝','verdict':'通过','basis':'全索引2组/限定1组；FZ同组仍被城市filter剔除；_only_nodes/profile实际执行节点与primary字段关联，不拿候选列表证明执行。'},
 {'topic':'Java契约与展示壳','verdict':'通过','basis':'独立官方客户端完整CRUD/搜索/错误分支，query builder复用F07；路由是地址参数。原展示壳只观测默认索引，没有routing输入；REST独立重放核对。'},
 {'topic':'可复现与边界','verdict':'通过','basis':'固定JSON/NDJSON、fresh输出、显式refresh、逐项created、点名清理后重做；真实调用与源码/图/阅读分列；无性能/故障容灾结论。'}]
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'reviewer':'root author self-review, not independent review','reasoning_entry':'cannot set/read back latest gpt-6.1-sol/max; reasoning.json','chinese_characters_without_code':len(re.findall('[\u4e00-\u9fff]',prose)),'figures':parser.figures,'code_blocks':parser.pre,'drills':8,'pitfalls':4,'rounds':summary,'review':review,'corrections_during_authoring':['Selected SH as cross-shard value after FZ proved same-shard; fixed Java constants/fixtures accordingly before formal rounds.','Replaced sequential full→limited diagram boxes with one explicit independent-request comparison card.','Included full routed mapping and duplicate PUT body; fixed Java excerpt boundaries.'],'published_lesson_errata':'No prior F29 lesson existed; no old lesson content changed except F28 next link.','sha256':{'framework/f29.html':hashlib.sha256(page.encode()).hexdigest()}}
(D/'content-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F29 author self-review/evidence consistency passed')
