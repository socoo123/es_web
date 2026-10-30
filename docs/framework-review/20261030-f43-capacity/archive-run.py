#!/usr/bin/env python3
"""Archive complete raw responses with lossless gzip; do not replace measurements."""
import argparse,datetime,gzip,hashlib,json,pathlib
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2]
p=argparse.ArgumentParser();p.add_argument('source',type=pathlib.Path);p.add_argument('destination',type=pathlib.Path)
a=p.parse_args();a.destination.mkdir(parents=True,exist_ok=False)
records=[]
for f in sorted(a.source.rglob('*')):
 if not f.is_file():continue
 rel=f.relative_to(a.source);data=f.read_bytes();target=a.destination/rel
 if len(data)>131072 or f.suffix=='.jsonl':target=target.with_name(target.name+'.gz');payload=gzip.compress(data,compresslevel=6,mtime=0)
 else:payload=data
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
 records.append({'original':str(rel),'stored':str(target.relative_to(a.destination)),'original_bytes':len(data),'stored_bytes':len(payload),'original_sha256':hashlib.sha256(data).hexdigest(),'stored_sha256':hashlib.sha256(payload).hexdigest()})
if (a.source/'summary.json').exists():
 s=json.loads((a.source/'summary.json').read_text());http=[json.loads(x) for x in (a.source/'http.jsonl').read_text().splitlines()]
 metrics={'python_coordinator_http':len(http),'python_coordinator_statuses':dict(__import__('collections').Counter(x['status'] for x in http)),
          'java_measured_bulk_attempts':0,'java_extra_warmup_bulk':0,'java_after_import_refresh_and_search':0,
          'mixed_all_http':0,'mixed_measured_http':0,'mixed_successful_measured_http':0,'monitor_http':0,
          'observed_app_api_calls':2,'observed_app_es_searches':2,'application_asset_and_readiness_requests':'excluded; not exhaustively counted',
          'compose_startup_polling':'excluded; readiness polling separate from measurement',
          'clock_basis':'mixed request starts in [0, admission window), denominator includes tail drain'}
 for f in a.source.glob('*.json'):
  v=json.loads(f.read_text())
  if isinstance(v,dict) and isinstance(v.get('samples'),list):
   if 'batch' in v:
    metrics['java_measured_bulk_attempts']+=sum(x['attempts'] for x in v['samples'])
    if v['index']!='tut-f43-pressure':metrics['java_extra_warmup_bulk']+=1;metrics['java_after_import_refresh_and_search']+=2
   elif 'searchers' in v:
    metrics['mixed_all_http']+=len(v['samples']);metrics['mixed_measured_http']+=sum(x['measured'] for x in v['samples']);metrics['mixed_successful_measured_http']+=sum(x['measured'] and x['ok'] for x in v['samples'])
  if isinstance(v,dict) and f.name.endswith('-browser.json'):metrics['observed_app_api_calls']+=len(v['calls']);metrics['observed_app_es_searches']+=len(v['calls'])
 for f in a.source.glob('c02-*-resources.json'):metrics['monitor_http']+=len(json.loads(f.read_text()))
 metrics['known_es_http']=sum(metrics[k] for k in ['python_coordinator_http','java_measured_bulk_attempts','java_extra_warmup_bulk','java_after_import_refresh_and_search','mixed_all_http','monitor_http','observed_app_es_searches'])
 (a.destination/'http-accounting.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
(a.destination/'archive-manifest.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compression':'gzip level6; mtime0; lossless','files':records},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'destination':str(a.destination),'files':len(records),'stored_bytes':sum(x['stored_bytes'] for x in records)}))
