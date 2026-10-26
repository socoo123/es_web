#!/usr/bin/env python3
"""One canonical catalog -> four immutable lesson projections. --check never writes."""
import argparse,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
catalog=json.loads((HERE/'catalog.json').read_text())
main=[{k:v for k,v in h.items() if k!='rooms'} for h in catalog]
offers=[dict(**{k:v for k,v in h.items() if k!='rooms'},**{k:v for k,v in r.items() if k!='rates'},**p) for h in catalog for r in h['rooms'] for p in r['rates']]
files={'hotels.json':main,'object.json':catalog,'nested.json':catalog,'offers.json':offers}
check='--check' in __import__('sys').argv
for filename,rows in files.items():
 text=json.dumps(rows,ensure_ascii=False,indent=2)+'\n'
 id_field='offer_id' if filename=='offers.json' else 'hotel_id'
 bulk=''.join(json.dumps({'create':{'_id':r[id_field]}},ensure_ascii=False)+'\n'+json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
 for name,content in [(filename,text),(filename.replace('.json','.ndjson'),bulk)]:
  path=HERE/name
  if check:
   assert path.read_text()==content, name
  else:path.write_text(content)
assert len(catalog)==3 and sum(len(h['rooms']) for h in catalog)==5 and len(offers)==8
print('F23 canonical projections agree: 3 hotels / 5 rooms / 8 offers')
