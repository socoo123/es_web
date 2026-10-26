#!/usr/bin/env python3
"""Produce Bulk create lines from the canonical fixed hotels.json; --check does not write."""
import argparse,json,pathlib
D=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();rows=json.loads((D/'hotels.json').read_text())
assert len(rows)==9 and len({h['hotel_id'] for h in rows})==9
entries=[r for h in rows for r in h['rooms']];assert len(entries)==16 and len({r['offer_id'] for r in entries})==16
assert all('rates' not in r and isinstance(r['capacity'],int) and ('price_minor' not in r or isinstance(r['price_minor'],int)) for r in entries)
ndjson=''.join(json.dumps({'create':{'_id':h['hotel_id']}},ensure_ascii=False)+'\n'+json.dumps(h,ensure_ascii=False)+'\n' for h in rows)
target=D/'hotels.ndjson'
if a.check:assert target.read_text()==ndjson,'Bulk file differs from canonical hotels.json'
else:target.write_text(ndjson)
print('F24 canonical 9 hotels /16 offer entries and Bulk projection consistent')
