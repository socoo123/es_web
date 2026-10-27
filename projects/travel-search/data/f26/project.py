#!/usr/bin/env python3
"""F26 fixed two-night snapshot; generated summaries never imply stay eligibility."""
import argparse, copy, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
P = HERE.parents[1]
SNAPSHOT = 'f26-20261027-v1'
def dump(value): return json.dumps(value, ensure_ascii=False, indent=2)+'\n'
def generate():
    rows = []
    # offer, hotel, Nov1 price, Nov2 price, Nov2 stock, explicit exception
    specs = [('o01','h01',10000,90000,3,None),('o02','h01',40000,40000,3,None),
      ('o03','h01',45000,45000,3,None),('o04','h01',5000,5000,3,'no-breakfast'),
      ('o05','h02',20000,100000,3,None),('o06','h02',50000,50000,3,None),
      ('o07','h03',60000,None,3,'missing-night'),('o08','h03',65000,65000,0,None),
      ('o09','h04',30000,30000,3,None),('o10','h05',30000,30000,3,None),
      ('o11','h06',15000,15000,3,'USD'),('o12','h06',10000,10000,3,'nonref'),
      ('o13','h07',10000,10000,3,'paused'),('o14','h08',None,None,3,'missing-price'),
      ('o15','h02',60000,60000,3,'no-breakfast'),('o16','h09',70000,70000,3,'min-stay')]
    names={'h01':'湖畔酒店','h02':'运河酒店','h03':'山居酒店','h04':'城南酒店','h05':'江湾酒店',
           'h06':'花园酒店','h07':'古街酒店','h08':'林间酒店','h09':'长住酒店'}
    for oid,hid,p1,p2,stock,exception in specs:
        s=dict(offer_id=oid,hotel_id=hid,hotel_name=names[hid],room_id='r'+oid[1:],
            rate_plan_id='bf-flex',snapshot_id=SNAPSHOT,city_code='HZ',hotel_status='open',
            offer_status='active',bed_type='twin',meal='breakfast',cancellation='flexible',
            currency='CNY',capacity=2,window_start='2026-11-01',window_end_exclusive='2026-11-03',max_available_rooms=3)
        if exception=='no-breakfast': s['meal']='none';s['rate_plan_id']='room-flex'
        if exception=='USD': s['currency']='USD'
        if exception=='nonref': s['cancellation']='nonref';s['rate_plan_id']='bf-nonref'
        if exception=='paused': s['hotel_status']='paused'
        prices=[v for v in [p1,p2] if v is not None]
        if prices:s['min_price_minor']=min(prices)
        nights=[dict(date='2026-11-01',price_minor=p1,available_rooms=3,min_stay_arrival=3 if exception=='min-stay' else 1)]
        if exception=='missing-night':
            nights.append(dict(date='2026-11-03',price_minor=p1,available_rooms=3,min_stay_arrival=1))
            s['window_end_exclusive']='2026-11-04'
        if exception!='missing-night':nights.append(dict(date='2026-11-02',price_minor=p2,available_rooms=stock,min_stay_arrival=1))
        rows.append(dict(summary=s,nights=nights))
    return dict(snapshot_id=SNAPSHOT,check_in='2026-11-01',check_out='2026-11-03',
                timezone='Asia/Shanghai',rooms=1,adults_per_room=2,offers=rows)
def artifacts():
    table=generate(); summaries=[o['summary'] for o in table['offers']]
    kw=['offer_id','hotel_id','room_id','rate_plan_id','snapshot_id','city_code','hotel_status','offer_status','bed_type','meal','cancellation','currency']
    props={k:{'type':'keyword','doc_values':True} for k in kw}
    props['hotel_name']={'type':'keyword'}
    props.update({k:{'type':'integer','coerce':False} for k in ['capacity','max_available_rooms']})
    props['min_price_minor']={'type':'long','coerce':False}
    props.update({k:{'type':'date','format':'strict_date'} for k in ['window_start','window_end_exclusive']})
    schema=dict(settings=dict(number_of_shards=1,number_of_replicas=0,refresh_interval='-1'),mappings=dict(dynamic='strict',properties=props))
    filters=[{'term':{k:{'value':v}}} for k,v in [('city_code','HZ'),('hotel_status','open'),('offer_status','active'),('bed_type','twin'),('meal','breakfast'),('cancellation','flexible'),('currency','CNY')]]
    filters += [{'range':{'capacity':{'gte':2.0}}},{'range':{'window_start':{'lte':'2026-11-01'}}},
                {'range':{'window_end_exclusive':{'gte':'2026-11-03'}}},{'range':{'max_available_rooms':{'gte':1.0}}}, {'exists':{'field':'min_price_minor'}}]
    sort=[{k:{'order':'asc'}} for k in ['min_price_minor','hotel_id','offer_id']]
    base=dict(size=100,track_total_hits=True,query={'bool':{'filter':filters}},sort=sort,
              aggregations={'candidate_hotels':{'cardinality':{'field':'hotel_id','precision_threshold':100}}})
    queries={'all':base,'top-offers':dict(copy.deepcopy(base),size=2)}
    for name,size,inner in [('collapse',10,2),('inner-one',10,1),('inner-all',10,10),('top-hotels',2,10)]:
        q=copy.deepcopy(base);q.update(size=size,collapse={'field':'hotel_id','inner_hits':[{'name':'offers','size':inner,'sort':sort}]});queries[name]=q
    q=copy.deepcopy(queries['collapse']);q['query']['bool']['filter']=[f for f in filters if 'meal' not in f.get('term',{})];queries['without-meal']=q
    q=copy.deepcopy(queries['inner-one']);q['collapse']['inner_hits'][0]['sort']=[{'min_price_minor':{'order':'desc'}},{'offer_id':{'order':'asc'}}];queries['inner-desc']=q
    out={HERE/'stay-table.json':dump(table),HERE/'summaries.json':dump(summaries),
         HERE/'summaries.ndjson':''.join(json.dumps(v,ensure_ascii=False)+'\n' for s in summaries for v in [{'create':{'_id':s['offer_id']}},s]),
         P/'search/f26/index.json':dump(schema)}
    out.update({P/f'search/f26/{name}.json':dump(q) for name,q in queries.items()})
    for mode in ['all','top-offers','top-hotels']:out[P/f'search/f26/{mode}-input.json']=dump({'mode':mode})
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    for path,value in artifacts().items():
        if args.check:assert path.read_text()==value,path
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value)
    print('F26 fixed snapshot and DSL '+('match' if args.check else 'generated'))
