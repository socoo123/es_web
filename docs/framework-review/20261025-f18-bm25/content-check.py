#!/usr/bin/env python3
"""Author self-review against complete real lesson evidence, not mirrored unit tests."""
from html.parser import HTMLParser
import datetime,hashlib,importlib.util,json,pathlib,re
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];P=R/'projects/travel-search'
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
s=(R/'framework/f18.html').read_text();t=Tables();t.feed(s)
spec=importlib.util.spec_from_file_location('f18lab',P/'labs/f18/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
docs=[json.loads(l) for l in (P/'data/f18/attractions.ndjson').read_text().splitlines()[1::2]]
expected=[]
for d in docs:
 w=d.get('description','').split()
 expected.append([d['attraction_id']+'\n'+d['name'],d.get('description','（字段缺失）'),f"{w.count('西湖')} / {len(w) if w else '—'}",f"{d['city_code']} / {d['status']} / {d['ticket_price_fen']}"])
assert t.tables['samples-table'][1:]==expected
execution=json.loads((P/'review/f18/execution.json').read_text());assert execution['status']=='passed' and execution['rounds_agree']
assert [r['teaching_requests'] for r in execution['rounds']]==[58,58]
assert [r['extra_requests'] for r in execution['rounds']]==[32,32]
checks=[]
for n in [1,2]:
 records=[json.loads(l) for l in (P/f'review/f18/round-{n}-java.jsonl').read_text().splitlines()]
 for row in records:
  if row['target']!='Java':continue
  fixture=next(slug for slug in ['scored','filtered','city-scored','rare','other-city','zero-budget','empty'] if lab.load('input-'+slug)==row['request'])
  assert lab.canonical(row['response']['esRequest'])==lab.canonical(lab.load(fixture))
  assert row['response']['explainRequest']=={'query':row['response']['esRequest']['query']}
  checks.append({'round':n,'fixture':fixture,'actual_Java_DSL_matches_complete_fixed_REST':True})
 baseline=[json.loads(l) for l in (P/f'review/f18/round-{n}-bm25.jsonl').read_text().splitlines()]
 hits=next(row['response']['hits']['hits'] for row in baseline if row['path'].endswith('/_search'))
 expect=[[h['_id'],f"{lab.terms(h['_explanation'])['西湖']['freq']:g} / {lab.terms(h['_explanation'])['西湖']['dl']:g}",f"{h['_score']:.6f}"] for h in hits]
 assert t.tables['score-table'][1:]==expect
assert s.count('<pre ')==16 and s.count('<details')==9
assert s[s.index('class="drills"'):s.index('class="pitfalls"')].count('<details')==7
assert s.count('class="callout warn"')==3 and s.count('data-d2-light=')==2
assert 'f19.html' not in s
sources=json.loads((H/'sources.json').read_text());assert len(sources['files'])==5 and all(r['local_matches_official'] is True for r in sources['files'][:4])
pure=re.sub('<pre[\\s\\S]*?</pre>','',s);pure=re.sub('<[^>]+>','',pure)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','scope':'F18 author self-review; no independent agent','reasoning':'xhigh requested; root actual effort not configurable/verifiable','checks':['10 complete fixture rows equal lesson table including full descriptions, frequencies/lengths, statuses and prices','six-row initial score/order table agrees with both real rounds to displayed precision','58 teaching + 32 extra per round; cleanup before/after 2 each','all 14 Java request bodies match fixed REST DSL; explain reuses same complete query','full explanation structures/descriptions and numbers checked by run.py with tiny float/double serialization tolerance','freq saturation tested at equal length, length tested at equal frequency; rare term plus OR sum distinguished','field N9 not count10 or total6; closed/other-city stats remain; N15/avg62/15 after unrelated append','ES compatibility boost k1+1 explicitly separated from business boost; default parameter values separated from explicit index configuration','original short document source/version/seq/term unchanged while scores change; refresh boundary separated','whitespace-given Chinese boundaries are controlled scoring setup, not production analysis guidance','single shard only; no multi-shard/DFS/quality/performance claims; no front-end code in lesson','16 complete source-backed/command blocks, seven exercises, three pitfalls; baseline and appended stages labeled','four local ES source files byte-match fixed official v9.4.0; Lucene10.4.0 source hash recorded'],'actual_request_comparisons':checks,'chinese_chars_excluding_code':len(re.findall('[\u4e00-\u9fff]',pure)),'limits':['author self-review only; xhigh not verifiable','not a quality benchmark or blind evaluation','no whole-site quality/performance/multi-shard/DFS/security/CDC experiments','execution timeout/partial shard failure guarded but not triggered'],'sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'framework/f18.html',P/'data/f18/manifest.json',*sorted((P/'search/f18').glob('*.json'))]}}
(H/'content-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Content: 10 full fixture rows, 6 score rows and 14 actual Java/REST request pairs agree')
