#!/usr/bin/env python3
"""Translate the lesson's bounded SQL projection file into ES Bulk NDJSON."""
import json, pathlib, sys
if len(sys.argv)!=2: raise SystemExit('Usage: python3 labs/f36/to-bulk.py projection.ndjson')
records=[json.loads(line) for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if line.strip()]
if not 1<=len(records)<=100: raise SystemExit('This teaching converter accepts 1..100 records')
seen=set();lines=[]
for r in records:
    op,id=r['op'],r['id']
    if id in seen or op not in ['index','delete']: raise SystemExit('Invalid/duplicate projection operation')
    seen.add(id)
    if op=='index' and (r['document']['attraction_id']!=id or r['document']['status']!='open'):
        raise SystemExit('Projection ID/status mismatch')
    if op=='delete' and r['document'] is not None: raise SystemExit('Delete must have null document')
    lines.append(json.dumps({op:{'_id':id}},ensure_ascii=False))
    if op=='index':lines.append(json.dumps(r['document'],ensure_ascii=False))
sys.stdout.write('\n'.join(lines)+'\n')
