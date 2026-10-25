#!/usr/bin/env python3
"""Compare the lesson's full tables with fixed data and actual two-round responses."""
from html.parser import HTMLParser
import datetime
import hashlib
import json
import pathlib
import re

HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT/'projects/travel-search'
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.tables={};self.table=None;self.row=None;self.cell=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='table':self.table=a.get('id');self.tables[self.table]=[]
  elif tag=='tr' and self.table:self.row=[]
  elif tag in ['td','th'] and self.row is not None:self.cell=[]
  elif tag=='br' and self.cell is not None:self.cell.append('\n')
 def handle_data(self,s):
  if self.cell is not None:self.cell.append(s)
 def handle_endtag(self,tag):
  if tag in ['td','th'] and self.cell is not None:self.row.append(''.join(self.cell));self.cell=None
  elif tag=='tr' and self.table:self.tables[self.table].append(self.row);self.row=None
  elif tag=='table':self.table=None
html=(ROOT/'framework/f16.html').read_text();parser=Tables();parser.feed(html)
lines=(P/'data/f16/attractions.ndjson').read_text().splitlines()
expected=[]
for line in lines[1::2]:
 d=json.loads(line);expected.append([d['attraction_id'],d['name']+'\n'+d['name_en'],'、'.join(d['aliases']) or '空数组',f"{d['city_code']} / {d['status']} / {d['currency']} / {d['ticket_price_fen']}"])
assert parser.tables['samples-table'][1:]==expected
rows=[json.loads(l) for l in (P/'review/f16/round-1-aliases.jsonl').read_text().splitlines()]
searches=[r for r in rows if r['path'].endswith('/_search')]
for index,name in enumerate(['plain-cn','aliases-cn','graph-cn','aliases-sy','graph-sy']):
 fixture=json.loads((P/('search/f16/'+name+'.json')).read_text())
 actual=next(r for r in searches if r['request']==fixture)
 value='、'.join(h['_id'] for h in actual['response']['hits']['hits']) or '空'
 assert parser.tables['cn-matrix'][index+1][2]==value
rows=[json.loads(l) for l in (P/'review/f16/round-1-graph.jsonl').read_text().splitlines()]
actual=[r for r in rows if r['path'].endswith('/_analyze') and r['status']==200 and r['request'].get('analyzer')=='travel_search'][0]['response']['detail']['tokenfilters'][-1]['tokens']
expected=[[t['token'],str(t['position']),str(t['positionLength']),f"[{t['start_offset']},{t['end_offset']})"] for t in actual]
assert parser.tables['graph-tokens'][1:]==expected
searches=[r for r in rows if r['path'].endswith('/_search')]
for i,r in enumerate(searches[:3]):
 assert parser.tables['en-matrix'][i+1][1]=='、'.join(h['_id'] for h in r['response']['hits']['hits'])
execution=json.loads((P/'review/f16/execution.json').read_text())
assert execution['status']=='passed' and execution['rounds_agree']
assert [r['teaching_requests'] for r in execution['rounds']]==[87,87]
assert [r['extra']['requests'] for r in execution['rounds']]==[33,33]
assert html.count('<pre ')==19
assert html.count('<details')==10
assert html[html.index('class="drills"'):html.index('class="pitfalls"')].count('<details')==7
prose=re.sub(r'<pre\b[\s\S]*?</pre>','',html);prose=re.sub(r'<[^>]+>','',prose)
record={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','scope':'F16 author self-review and actual table comparisons; no independent reviewer',
 'reasoning':'xhigh requested but root entry cannot set or verify runtime effort',
 'checks':['11 full data rows equal fixture including raw traditional text/English/aliases/city/status/currency/price',
 'five complete Chinese ID matrix cells equal real round-1 requests','four position/length/offset rows equal actual detailed graph',
 'three complete English ID matrix cells equal actual graph/loose/phrase responses','87 teaching/33 extra counts per round equal execution records',
 'source/queries/diagrams/exercises/pitfalls/recap use same modes and boundaries','seven-part structure/7 exercises/3 pitfalls/19 code blocks/2 static diagrams',
 'query synonyms are search-only; aliases ordinary text; managed complete replacement/reload distinct from document refresh/rebuild',
 'standard+ICU here is a controlled sample, not general segmentation or whole Chinese quality claim'],
 'chinese_chars_excluding_code':len(re.findall('[\u4e00-\u9fff]',prose)),
 'limits':['self-review only; xhigh not verifiable','not a held-out quality study','multi-node/whole-site quality/performance/security not tested','search execution timeout/partial shard failure guarded but not triggered'],
 'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'framework/f16.html',P/'data/f16/judgments.json',*sorted((P/'search/f16').glob('*.json'))]}}
(HERE/'content-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('F16 content/table/source comparisons passed')
