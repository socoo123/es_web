#!/usr/bin/env python3
"""Verify the actual reader curl sequence separately from the two formal lab runs."""
import collections,datetime,json,pathlib,re
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/travel-search';D=P/'review/f34/manual'
s=(D/'responses.txt').read_text();decoder=json.JSONDecoder();values=[]
while s.strip():
 s=s.lstrip();v,n=decoder.raw_decode(s);values.append(v);s=s[n:]
commands=[x for x in (P/'labs/f34/requests.sh').read_text().splitlines() if x.startswith('curl ')]
assert len(commands)==len(values),(len(commands),len(values))
errors=[v for v in values if isinstance(v,dict) and 'error' in v]
assert collections.Counter((v['status'],v['error']['type']) for v in errors)=={(500,'repository_exception'):1,(500,'snapshot_restore_exception'):2}
assert not any(isinstance(v,dict) and v.get('timed_out') for v in values)
java=[v for v in values if isinstance(v,dict) and 'esRequest' in v]
rows=[[(x['id'],x['ticketPriceFen']) for x in v['items']] for v in java]
assert rows==[[('p01',6000),('p02',0)],[('p01',6500)],[('p01',6500)],[('p01',6000),('p02',0)]],rows
rec=[]
for command,value in zip(commands,values):
 if 'tut-f34-partial-risk/_count' in command:assert value['count']==0
 if '/tut-f34-risk/_count' in command:assert value['count']==1
 if 'tut-f34-restore-attractions-v001/_count' in command:assert value['count']==6
 if 'tut-f34-attractions-v001/_count' in command:assert value['count']==5
 if 'search/f34/fields.json' in command:
  expected=json.loads((P/'data/f34/v001.json').read_text())
  if '_only_nodes' in command:expected=[json.loads((P/'data/f34/p01-updated.json').read_text())]+expected[2:]
  assert [h['_source'] for h in value['hits']['hits']]==expected
  assert not value['timed_out'] and value['_shards']['failed']==0
 rec.append({'command':command,'response':value})
(D/'sequence.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
summary={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'actual_curl_responses':len(values),'java_searches':4,'java_rows':rows,'expected_errors':[{'status':x['status'],'type':x['error']['type'],'reason':x['error']['reason']} for x in errors],'source_count':5,'complete_restored_count':6,'partial_risk_count':0,'original_risk_count':1,'health_timeouts':0,'scope':'Actual requests.sh executed once after exact cleanup; manual initial snapshot synchronous. Not a third formal lab run; no browser observer attached.'}
(D/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))
