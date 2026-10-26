#!/usr/bin/env python3
"""One fixed quote snapshot -> ES summaries and the packaged Java nightly table."""
import datetime, json, pathlib, sys
D = pathlib.Path(__file__).resolve().parent
S = D.parents[1] / 'search/f25'
SNAPSHOT = 'f25-20261026-v1'
DATES = ['2026-11-01', '2026-11-02', '2026-11-03']
CHECK = '--check' in sys.argv
def emit(path, content):
    if CHECK:
        assert path.read_text() == content, f'Generated artifact differs: {path}'
    else:
        path.write_text(content)
def dump(path, value):
    emit(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def main():
    S.mkdir(parents=True, exist_ok=True)
    offers = []
    def add(num, prices, stocks=(3,3,3), dates=DATES, mins=None, **extra):
        oid = f'o{num:02d}'
        nights = [dict(date=d, available_rooms=s, min_stay_arrival=(mins or [1]*len(dates))[i],
                       **({'price_minor':p} if p is not None else {}))
                  for i,(d,p,s) in enumerate(zip(dates,prices,stocks))]
        summary = dict(offer_id=oid, hotel_id=f'h{num:02d}', hotel_name=f'湖畔旅舍{num:02d}',
                       room_id=f'r{num:02d}', city_code='HZ', hotel_status='open', offer_status='active',
                       bed_type='twin', capacity=2, meal='breakfast', cancellation='flexible',
                       rate_plan_id='bf-flex', currency='CNY', snapshot_id=SNAPSHOT,
                       window_start=min(dates), window_end_exclusive=str(datetime.date.fromisoformat(max(dates))+datetime.timedelta(days=1)),
                       max_available_rooms=max(stocks), min_price_minor=min(p for p in prices if p is not None))
        summary.update(extra)
        offers.append(dict(summary=summary, nights=nights))
    add(1, [30000,40000,99900], (3,3,0), mins=[1,5,1])
    add(2, [10000,10000], (3,3), [DATES[0],DATES[2]])
    add(3, [20000,20000,20000], (3,0,3))
    add(4, [25000,40000,30000], (3,1,3))
    add(5, [20000,25000,30000], (2,2,2), mins=[3,1,1])
    add(6, [60000,70000,10000])
    add(7, [5000,5000,5000], currency='USD')
    add(8, [10000,10000,10000], capacity=1)
    add(9, [10000,10000,10000], hotel_status='paused')
    add(10,[45000,45000,45000], (2,2,2))
    add(11,[10000,10000], (3,3), DATES[1:], hotel_id='h02', hotel_name='湖畔旅舍02', room_id='r02b')
    add(12,[30000,None,30000])
    dump(D/'stay-table.json', dict(snapshot_id=SNAPSHOT, hotel_zone='Asia/Shanghai', offers=offers))
    summaries = [o['summary'] for o in offers]
    dump(D/'summaries.json', summaries)
    emit(D/'summaries.ndjson', ''.join(json.dumps({'create':{'_id':s['offer_id']}})+'\n'+json.dumps(s,ensure_ascii=False)+'\n' for s in summaries))
    props = {k:{'type':'keyword'} for k in summaries[0] if k not in ['capacity','max_available_rooms','min_price_minor','window_start','window_end_exclusive']}
    props.update({k:{'type':'integer','coerce':False} for k in ['capacity','max_available_rooms']})
    props['min_price_minor']={'type':'long','coerce':False}
    props.update({k:{'type':'date','format':'strict_date'} for k in ['window_start','window_end_exclusive']})
    dump(S/'index.json', {'settings':{'number_of_shards':1,'number_of_replicas':0,'refresh_interval':'-1'},'mappings':{'dynamic':'strict','properties':props}})
    scenarios = {
        'two-nights':dict(checkIn=DATES[0],checkOut=DATES[2],rooms=1,adultsPerRoom=2,budgetMinor=120000),
        'two-rooms':dict(checkIn=DATES[0],checkOut=DATES[2],rooms=2,adultsPerRoom=2,budgetMinor=240000),
        'three-nights':dict(checkIn=DATES[0],checkOut='2026-11-04',rooms=1,adultsPerRoom=2,budgetMinor=200000),
        'one-night':dict(checkIn=DATES[0],checkOut=DATES[1],rooms=1,adultsPerRoom=2,budgetMinor=120000),
    }
    for name,i in scenarios.items():
        dump(S/(name+'-input.json'),i)
        fs=[{'term':{k:{'value':v}}} for k,v in dict(city_code='HZ',hotel_status='open',offer_status='active',bed_type='twin',meal='breakfast',cancellation='flexible',rate_plan_id='bf-flex',currency='CNY').items()]
        fs += [{'range':{'capacity':{'gte':float(i['adultsPerRoom'])}}},
               {'range':{'window_start':{'lte':i['checkIn']}}},
               {'range':{'window_end_exclusive':{'gte':i['checkOut']}}},
               {'range':{'max_available_rooms':{'gte':float(i['rooms'])}}}]
        dump(S/(name+'.json'),dict(size=100,track_total_hits=True,query={'bool':{'filter':fs}},sort=[{'offer_id':{'order':'asc'}}]))
    dump(D/'contract.json',dict(snapshot_id=SNAPSHOT,unit='CNY integer fen per room per night; budget for all rooms / nights',
         interval='hotel local date [checkIn,checkOut), Asia/Shanghai; no UTC/24h arithmetic',
         selection='one fixed offer/room/plan/currency throughout; no room switching; same adultsPerRoom in each room',
         rules='min_stay_arrival on arrival date only; each night stock >= rooms; missing date/price rejects; no checkout-night charge',
         summary='date extrema and max stock are necessary only, not continuous availability; min price is display metadata, never the total',
         coverage='all returned candidates verified; size100 and total eq/length guard; no hotel collapse or price ranking',
         excludes='taxes, fees, children, rate rounding, CTA/CTD, live supply, booking/stock deduction, production transactions'))
if __name__ == '__main__': main()
