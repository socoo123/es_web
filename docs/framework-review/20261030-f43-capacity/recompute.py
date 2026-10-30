#!/usr/bin/env python3
"""Audit retained measurements without sending any requests to ES."""
import gzip,hashlib,json,math,pathlib
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];R=ROOT/'projects/travel-search/review/f43'
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def percentile(v,p):return sorted(v)[math.ceil(len(v)*p)-1] if v else None
def close(a,b):assert abs(a-b)<1e-7,(a,b)
records=[]
for round in ['run-01','run-02']:
 p=R/round;manifest=read(p/'archive-manifest.json')
 for f in manifest['files']:
  stored=(p/f['stored']).read_bytes();assert hashlib.sha256(stored).hexdigest()==f['stored_sha256']
  original=gzip.decompress(stored) if f['stored'].endswith('.gz') else stored
  assert hashlib.sha256(original).hexdigest()==f['original_sha256'] and len(original)==f['original_bytes']
 for f in p.glob('c02-*.json*'):
  v=read(f)
  if not isinstance(v,dict) or 'searchers' not in v or 'samples' not in v:continue
  samples=v['samples'];secs=v['admission_window_seconds'];span=v['elapsed_including_drain_seconds']
  assert not v['failures'] and span>=secs and max(x['end_seconds'] for x in samples)<=span
  for x in samples:
   assert x['measured']==(x['start_seconds']>=0) and x['start_seconds']<secs
   close(x['ms'],(x['end_seconds']-x['start_seconds'])*1000)
  for kind in ['search','update']:
   group=[s for s in samples if s['measured'] and s['kind']==kind];good=[s for s in group if s['ok']];reported=v[kind]
   assert len(group)==reported['requests'] and len(good)==reported['successes'] and reported['failed']==0
   close(sum(s['units'] for s in good)/span,reported['successful_units_per_second'])
   for q in [.5,.95,.99]:
    actual=percentile([s['ms'] for s in group],q);label=f'p{int(q*100)}_ms'
    if actual is None:assert reported[label] is None
    else:close(actual,reported[label])
  for worker in {x['worker'] for x in samples}:
   owned=sorted((x for x in samples if x['worker']==worker),key=lambda x:x['start_seconds'])
   assert all(a['end_seconds']<=b['start_seconds'] for a,b in zip(owned,owned[1:]))
  records.append({'round':round,'name':v['name'],'samples':len(samples),'latencies_throughput_and_serial_workers_equal':True})
 for f in p.glob('c0*.json*'):
  v=read(f)
  if not isinstance(v,dict) or 'batch' not in v or 'samples' not in v:continue
  assert sum(s['successes'] for s in v['samples'])==v['successes']
  assert sum(s['failures'] for s in v['samples'])==v['failures']
  assert v['successes']+v['failures']==v['documents']
  close(v['successes']/v['elapsed_seconds'],v['successful_docs_per_second'])
  for q in [.5,.95,.99]:close(percentile([s['ms'] for s in v['samples']],q),v[f'bulk_p{int(q*100)}_ms'])
  if f.name.startswith('c03-rejected'):
   assert v['successes']==0 and v['failures']==2000
   assert sum(s['attempts'] for s in v['samples'])==16
   assert sum(s['rejected_attempt_items'] for s in v['samples'])==8000
   assert all(t['http']==429 for s in v['samples'] for t in s['trace'] if 'http' in t)
for n in [2000,10000]:
 a=read(R/f'run-01/corpus-{n}.json');b=read(R/f'run-02/corpus-{n}.json');assert a==b
(D/'recomputed.json').write_text(json.dumps({'passed':True,'records':records,'checks':['All archived file hashes and original gzip bytes','Raw per-request timings and measured cohort','Nearest-rank p50/p95/p99 and success throughput including drain','One in-flight request per worker','Bulk logical success/failure and 16 actual rejected API invocations','Corpus hashes identical across independent clean runs']},ensure_ascii=False,indent=2)+'\n')
print('Retained measurement audit passed')
