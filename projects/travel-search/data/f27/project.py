#!/usr/bin/env python3
"""F27: one hotel document; immutable synthetic offer/night snapshot."""
import argparse, copy, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
P = HERE.parents[1]
SNAPSHOT = "f27-20261027-v1"
REFERENCE = "2026-10-27T08:00:00+08:00"
def dump(value): return json.dumps(value, ensure_ascii=False, indent=2) + "\n"
def generate():
    # quality is a synthetic, already approved signal on [0,1000], not a star rating.
    specs = [
        ("h01","西湖湖畔酒店","西湖 湖畔 酒店","安静 湖景 住宿",930,30.26),
        ("h02","西湖城北酒店","西湖 城北 酒店","便捷 商务 住宿",950,30.26),
        ("h03","西湖山居酒店","西湖 山居 酒店","山景 安静 住宿",990,30.251),
        ("h04","城南园景酒店","城南 园景 酒店","西湖 交通 方便",970,30.25),
        ("h05","西湖江湾酒店","西湖 江湾 酒店","江景 安静 住宿",930,30.27),
        ("h06","西湖远郊酒店","西湖 远郊 酒店","山景 商务 住宿",None,None),
        ("h07","运河桥畔酒店","运河 桥畔 酒店","古街 步行 住宿",940,30.28),
        ("h08","运河古街酒店","运河 古街 酒店","古街 便捷 住宿",940,30.28),
    ]
    hotels=[]
    for hid,name,search,description,quality,lat in specs:
        s=dict(hotel_id=hid,hotel_name=name,name_search=search,description=description,
               city_code="HZ",hotel_status="open",snapshot_id=SNAPSHOT,offers=[])
        if quality is not None:s["quality_signal"]=quality
        if lat is not None:s["location"]={"lat":lat,"lon":120.15}
        hotels.append(s)
    by_id={h["hotel_id"]:h for h in hotels}
    # offer, hotel, room, breakfast?, flexible?, Nov1, Nov2, exception
    rows=[
      ("a01","h01","r11",False,False,30000,30000,None),
      ("a02","h01","r12",True,False,35000,35000,None),
      ("a03","h01","r13",True,True,40000,40000,None),
      ("a04","h01","r14",True,True,40000,40000,None),
      ("a05","h01","r15",True,True,10000,None,None),
      ("b01","h02","r21",False,True,25000,25000,None),
      ("b02","h02","r22",True,True,45000,45000,None),
      ("c01","h03","r31",True,True,10000,10000,"stale"),
      ("c02","h03","r32",True,True,10000,10000,"missing"),
      ("c03","h03","r33",True,True,5000,5000,"sold"),
      ("d01","h04","r41",False,False,20000,20000,None),
      ("d02","h04","r42",True,True,50000,50000,None),
      ("e01","h05","r51",True,True,40000,40000,None),
      ("e02","h05","r52",True,True,5000,5000,"double"),
      ("f01","h06","r61",False,True,35000,35000,None),
      ("g01","h07","r71",True,True,32500,32500,None),
      ("g02","h07","r72",True,False,30000,30000,None),
      ("i01","h08","r81",True,True,32500,32500,None),
      ("i02","h08","r82",True,True,7500,7500,"USD"),
    ]
    offers=[]
    for oid,hid,room,bf,flex,p1,p2,exception in rows:
        summary=dict(offer_id=oid,room_id=room,rate_plan_id=("bf" if bf else "room")+"-"+("flex" if flex else "nonref"),
            offer_status="active",bed_type="double" if exception=="double" else "twin",capacity=2,
            meal="breakfast" if bf else "none",cancellation="flexible" if flex else "nonref",
            currency="USD" if exception=="USD" else "CNY",window_start="2026-11-01",
            window_end_exclusive="2026-11-03",max_available_rooms=3)
        by_id[hid]["offers"].append(summary)
        nights=[]
        for day,price in [(1,p1),(2,p2)]:
            if exception=="missing" and day==2:continue
            nights.append(dict(date=f"2026-11-0{day}",price_minor=price,
                available_rooms=0 if exception=="sold" and day==2 else 3,min_stay_arrival=1,
                inventory_as_of="2026-10-27T07:40:00+08:00" if exception=="stale" else "2026-10-27T07:58:00+08:00"))
        offers.append(dict(hotel_id=hid,summary=summary,nights=nights))
    return dict(snapshot_id=SNAPSHOT,reference_time=REFERENCE,max_inventory_age_seconds=300,
        check_in="2026-11-01",check_out="2026-11-03",timezone="Asia/Shanghai",rooms=1,adults_per_room=2,
        hotels=hotels,offers=offers)
def query(hotel_sort="relevance",hard=False,scope="all",q="西湖"):
    filters=[{"term":{"offers."+k:{"value":v}}} for k,v in
        [("offer_status","active"),("bed_type","twin"),("currency","CNY")]]
    if hard:filters += [{"term":{"offers."+k:{"value":v}}} for k,v in [("meal","breakfast"),("cancellation","flexible")]]
    filters += [
        {"range":{"offers.capacity":{"gte":2.0}}},
        {"range":{"offers.window_start":{"lte":"2026-11-01"}}},
        {"range":{"offers.window_end_exclusive":{"gte":"2026-11-03"}}},
        {"range":{"offers.max_available_rooms":{"gte":1.0}}}]
    nested={"nested":{"path":"offers","score_mode":"none","query":{"bool":{"filter":filters}},
        "inner_hits":{"name":"eligible_offers","size":20,"sort":[{"offers.offer_id":{"order":"asc"}}]}}}
    sort={"relevance":{"_score":{"order":"desc"}},
          "quality":{"quality_signal":{"order":"desc","missing":"_last"}},
          "distance":{"_geo_distance":{"location":[{"lat":30.25,"lon":120.15}],"order":"asc","unit":"m",
                      "distance_type":"arc","mode":"min","ignore_unmapped":False}}}[hotel_sort]
    return dict(size=100 if scope=="all" else 2,track_total_hits=True,track_scores=True,
        query={"bool":{"must":[{"multi_match":{"query":q,"fields":["name_search^5","description"],
                        "type":"best_fields","operator":"and"}}],
          "filter":[{"term":{k:{"value":v}}} for k,v in [("city_code","HZ"),("hotel_status","open")]]+[nested]}},
        sort=[sort,{"hotel_id":{"order":"asc"}}])
def artifacts():
    table=generate()
    offer_props={k:{"type":"keyword"} for k in ["offer_id","room_id","rate_plan_id","offer_status","bed_type","meal","cancellation","currency"]}
    offer_props.update({k:{"type":"integer","coerce":False} for k in ["capacity","max_available_rooms"]})
    offer_props.update({k:{"type":"date","format":"strict_date"} for k in ["window_start","window_end_exclusive"]})
    props={k:{"type":"keyword"} for k in ["hotel_id","hotel_name","city_code","hotel_status","snapshot_id"]}
    props.update({k:{"type":"text","analyzer":"whitespace"} for k in ["name_search","description"]})
    props.update(quality_signal={"type":"integer","coerce":False},location={"type":"geo_point"},
                 offers={"type":"nested","dynamic":"strict","properties":offer_props})
    schema=dict(settings=dict(number_of_shards=1,number_of_replicas=0,refresh_interval="-1"),
                mappings=dict(dynamic="strict",properties=props))
    out={HERE/"stay-table.json":dump(table),HERE/"hotels.json":dump(table["hotels"]),
         HERE/"hotels.ndjson":"".join(json.dumps(v,ensure_ascii=False)+"\n" for h in table["hotels"] for v in [{"create":{"_id":h["hotel_id"]}},h]),
         P/"search/f27/index.json":dump(schema)}
    cases=[
      ("relevance-price",dict(hotelSort="relevance",roomSort="total",requireBreakfast=False,requireFlexible=False,scope="all",q="西湖")),
      ("relevance-preferred",dict(hotelSort="relevance",roomSort="preferred",requireBreakfast=False,requireFlexible=False,scope="all",q="西湖")),
      ("quality-price",dict(hotelSort="quality",roomSort="total",requireBreakfast=False,requireFlexible=False,scope="all",q="西湖")),
      ("distance-price",dict(hotelSort="distance",roomSort="total",requireBreakfast=False,requireFlexible=False,scope="all",q="西湖")),
      ("hard-preferred",dict(hotelSort="relevance",roomSort="preferred",requireBreakfast=True,requireFlexible=True,scope="all",q="西湖")),
      ("top-quality",dict(hotelSort="quality",roomSort="total",requireBreakfast=False,requireFlexible=False,scope="top2",q="西湖")),
      ("independent",dict(hotelSort="quality",roomSort="preferred",requireBreakfast=True,requireFlexible=True,scope="all",q="运河"))]
    for name,i in cases:
        out[P/f"search/f27/{name}-input.json"]=dump(i)
        out[P/f"search/f27/{name}.json"]=dump(query(i["hotelSort"],i["requireBreakfast"] and i["requireFlexible"],i["scope"],i["q"]))
    return out
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");args=ap.parse_args()
    for path,value in artifacts().items():
        if args.check:assert path.read_text()==value,path
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value)
    print("F27 fixed hotel/night snapshot and DSL "+("match" if args.check else "generated"))
