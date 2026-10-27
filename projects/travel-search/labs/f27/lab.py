#!/usr/bin/env python3
"""Real HTTP acceptance. Expected sets, totals and order are specified by hand."""
import argparse, copy, datetime, json, os, pathlib, urllib.request, urllib.error
HERE=pathlib.Path(__file__).resolve().parent;P=HERE.parents[1]
DATA=P/"data/f27";SEARCH=P/"search/f27";INDEX="tut-f27-hotels"
ES=os.environ.get("ES_URL","http://127.0.0.1:19227").rstrip("/")
APP=os.environ.get("APP_URL","http://127.0.0.1:18081").rstrip("/")
LOG=None;COUNT=0
TOTALS={"a01":60000,"a02":70000,"a03":80000,"a04":80000,"b01":50000,"b02":90000,
        "d01":40000,"d02":100000,"e01":80000,"f01":70000,"g01":65000,"g02":60000,"i01":65000}
REJECT={"a05":"MISSING_PRICE","c01":"STALE_INVENTORY","c02":"MISSING_NIGHT","c03":"SOLD_OUT"}
ROOTS={"relevance":["h01","h02","h03","h05","h06","h04"],
       "quality":["h03","h04","h02","h01","h05","h06"],
       "distance":["h04","h03","h01","h02","h05","h06"]}
FINAL={"relevance":["h01","h02","h05","h06","h04"],"quality":["h04","h02","h01","h05","h06"],
       "distance":["h04","h01","h02","h05","h06"]}
ROOMS_TOTAL={"h01":["a01","a02","a03","a04"],"h02":["b01","b02"],"h04":["d01","d02"],
             "h05":["e01"],"h06":["f01"]}
ROOMS_PREF={"h01":["a03","a04","a02","a01"],"h02":["b02","b01"],"h04":["d02","d01"],
            "h05":["e01"],"h06":["f01"]}
def require(ok,detail):
    if not ok:raise AssertionError(detail)
def read(path):return json.loads(path.read_text())
def request(method,path,body=None,status=200,app=False):
    global COUNT
    raw=body.encode() if isinstance(body,str) else json.dumps(body,ensure_ascii=False).encode() if body is not None else None
    url=(APP if app else ES)+path
    req=urllib.request.Request(url,data=raw,method=method,headers={"Content-Type":"application/x-ndjson" if "_bulk" in path else "application/json"})
    try:
        with urllib.request.urlopen(req,timeout=40) as r:actual=r.status;payload=r.read().decode()
    except urllib.error.HTTPError as e:actual=e.code;payload=e.read().decode()
    result=json.loads(payload);COUNT+=1
    if LOG:
        with LOG.open("a") as f:f.write(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            n=COUNT,method=method,url=url,request=body,status=actual,response=result),ensure_ascii=False)+"\n")
    require(actual in (status if isinstance(status,list) else [status]),dict(url=url,expected=status,actual=actual,response=result))
    return result
def search(name_or_body):
    q=read(SEARCH/(name_or_body+".json")) if isinstance(name_or_body,str) else name_or_body
    r=request("POST","/"+INDEX+"/_search",q)
    require(not r["timed_out"] and r["_shards"]["failed"]==0 and r["hits"]["total"]["relation"]=="eq","complete search")
    return r
def ids(r):return [h["_id"] for h in r["hits"]["hits"]]
def norm(x):
    if isinstance(x,list):return [norm(v) for v in x]
    if isinstance(x,dict):return {k:norm(v) for k,v in x.items() if not (k in ["_score","max_score"] and v is None)}
    return x
def prepare():
    v=request("GET","/");require(v["version"]["number"]=="9.4.0" and v["version"]["lucene_version"]=="10.4.0","versions")
    nodes=request("GET","/_nodes/plugins");require(len(nodes["nodes"])==1 and all(not n["plugins"] for n in nodes["nodes"].values()),"plugin-free single node")
    schema=read(SEARCH/"index.json");request("PUT","/"+INDEX,schema)
    h=request("GET","/_cluster/health/"+INDEX+"?wait_for_status=green&timeout=30s")
    require(h["status"]=="green" and not h["timed_out"] and h["number_of_nodes"]==1,"isolated green")
    b=request("POST","/"+INDEX+"/_bulk",(DATA/"hotels.ndjson").read_text())
    require(not b["errors"] and len(b["items"])==8 and all(i["create"]["result"]=="created" for i in b["items"]),"8 root hotels created")
    request("POST","/"+INDEX+"/_refresh")
    require(request("GET","/"+INDEX+"/_count")["count"]==8,"count root hotels, not nested offers")
    require(request("GET","/"+INDEX+"/_mapping")[INDEX]["mappings"]==schema["mappings"],"whole mapping exact")
    settings=request("GET","/"+INDEX+"/_settings")[INDEX]["settings"]["index"]
    require(all(settings[k]==str(v) for k,v in schema["settings"].items()),"explicit settings")
    expected=read(DATA/"hotels.json")
    docs=request("POST","/"+INDEX+"/_mget",{"ids":[h["hotel_id"] for h in expected]})["docs"]
    require(all(d["found"] and d["_source"]==s for d,s in zip(docs,expected)),"all 8 full roots/19 summaries exact")
    return dict(hotels=8,offers=19,source_mapping_settings="exact")
def hotels():
    result={}
    for mode in ROOTS:
        r=search(mode+"-price")
        require(ids(r)==ROOTS[mode] and r["hits"]["total"]=={"value":6,"relation":"eq"},"six candidate hotel order "+mode)
        for hit in r["hits"]["hits"]:
            inner=hit["inner_hits"]["eligible_offers"]["hits"]
            require(inner["total"]["relation"]=="eq" and inner["total"]["value"]==len(inner["hits"]),"complete matched offers")
        result[mode]=[dict(hotel=h["_id"],score=h["_score"],sort=h["sort"],
            offers=[v["_source"]["offer_id"] for v in h["inner_hits"]["eligible_offers"]["hits"]["hits"]]) for h in r["hits"]["hits"]]
    scores={h["hotel"]:h["score"] for h in result["relevance"]}
    require(len({scores[k] for k in ["h01","h02","h03","h05","h06"]})==1 and scores["h04"]<scores["h01"],"name weight vs description, explicit tie")
    ds={h["hotel"]:h["sort"][0] for h in result["distance"]}
    require(ds["h01"]==ds["h02"] and ds["h04"]==0 and ds["h05"]>ds["h01"],"distance ties and order")
    return result
def expected(name):
    if name=="independent":return ["h07","h08"],{"h07":["g01"],"h08":["i01"]},(2,2,2,2)
    if name=="hard-preferred":
        return ["h01","h02","h05","h04"],{"h01":["a03","a04"],"h02":["b02"],"h05":["e01"],"h04":["d02"]},(5,5,9,5)
    if name=="top-quality":return ["h04"],{"h04":["d01","d02"]},(6,2,5,2)
    mode=read(SEARCH/(name+"-input.json"))["hotelSort"]
    return FINAL[mode],ROOMS_PREF if name=="relevance-preferred" else ROOMS_TOTAL,(6,6,14,10)
def verify(name,r):
    i=read(SEARCH/(name+"-input.json"))
    require(r["conditions"]==i and r["snapshotId"]=="f27-20261027-v1" and r["referenceTime"]=="2026-10-27T00:00:00Z","conditions/snapshot/fixed clock")
    require(r["esRequest"]==read(SEARCH/(name+".json")),"whole Java request == canonical REST")
    replay=search(r["esRequest"])
    require(norm(replay["hits"])==norm(r["esResponse"]["hits"]),"all hotel/nested IDs/source/score/sort/total REST == Java")
    order,rooms,counts=expected(name)
    require([h["hotelId"] for h in r["hotels"]]==order,"independent final hotel order "+name)
    require((r["candidateHotelTotal"],r["inspectedHotelCount"],r["inspectedOfferCount"],r["acceptedOfferCount"])==counts,"named count scopes "+name)
    require(r["completeCandidateSet"]==(i["scope"]=="all"),"coverage")
    table={o["summary"]["offer_id"]:o for o in read(DATA/"stay-table.json")["offers"]}
    for d in r["decisions"]:
        oid=d["offerId"]
        require(d["nights"]==table[oid]["nights"] and d["hotelId"]==table[oid]["hotel_id"],"exact nightly evidence/identity")
        s=table[oid]["summary"]
        require((d["roomId"],d["ratePlanId"],d["meal"],d["cancellation"])==tuple(s[k] for k in ["room_id","rate_plan_id","meal","cancellation"]),"all offer fields")
        if oid in TOTALS:require(d["reason"]=="ACCEPTED" and d["totalMinor"]==TOTALS[oid],"independent integer sum "+oid)
        else:require(d["reason"]==REJECT[oid] and d["totalMinor"] is None,"independent rejection "+oid)
    for h in r["hotels"]:
        selected=rooms[h["hotelId"]][0]
        require([d["offerId"] for d in h["rooms"]]==rooms[h["hotelId"]],"within hotel full room order")
        require(h["selectedOfferId"]==selected and h["selectedTotalMinor"]==TOTALS[selected]
            and h["minimumTotalMinor"]==min(TOTALS[v] for v in rooms[h["hotelId"]]),"selected vs minimum room")
    return dict(case=name,hotels=order,rooms={h["hotelId"]:[v["offerId"] for v in h["rooms"]] for h in r["hotels"]},
        selected=[(h["selectedOfferId"],h["selectedTotalMinor"],h["minimumTotalMinor"]) for h in r["hotels"]],counts=counts,complete=r["completeCandidateSet"])
def execute(name):return verify(name,request("POST","/api/hotel-ranking/inspect",read(SEARCH/(name+"-input.json")),app=True))
def rooms():return [execute(n) for n in ["relevance-price","relevance-preferred","hard-preferred"]]
def boundary():return [execute(n) for n in ["quality-price","distance-price","top-quality","independent"]]
def put(id,s):return request("PUT","/"+INDEX+"/_doc/"+id+"?refresh=true",s,status=[200,201])
def errors():
    r=request("PUT","/"+INDEX,read(SEARCH/"index.json"),400)
    require(r["error"]["type"]=="resource_already_exists_exception","duplicate index")
    r=request("POST","/"+INDEX+"/_bulk",(DATA/"hotels.ndjson").read_text())
    require(r["errors"] and all(v["create"]["status"]==409 for v in r["items"]),"8 create conflicts despite HTTP 200")
    base=read(SEARCH/"relevance-price-input.json")
    bodies=[{},[],dict(base,q=""),dict(base,q=None),dict(base,hotelSort="price"),dict(base,roomSort="wrong"),
            dict(base,scope="page2"),dict(base,requireBreakfast=None),dict(base,requireFlexible=5),
            dict(base,requireFlexible="true")]
    for body in bodies:require(request("POST","/api/hotel-ranking/inspect",body,400,True)["code"]=="INVALID_HOTEL_RANKING_INPUT","invalid input")
    s=read(DATA/"hotels.json")[0];bad=copy.deepcopy(s);bad["unexpected"]=True
    request("PUT","/"+INDEX+"/_doc/f27-bad",bad,400)
    # A changed ES projection is a request-level integrity failure, distinct from a known old nightly row.
    bad=copy.deepcopy(s);bad["snapshot_id"]="old";put("h01",bad)
    require(request("POST","/api/hotel-ranking/inspect",base,502,True)["code"]=="SEARCH_INCOMPLETE","altered snapshot refused")
    # Rebuild the fixed corpus after document mutations; restoring _source alone does
    # not restore term statistics while deleted Lucene documents remain in segments.
    cleanup();prepare();execute("relevance-price")
    # Confirm root count truncation before any unknown-source guard can run.
    injected=[f"f27-overflow-{i:03}" for i in range(101)]
    raw=""
    for id in injected:
        d=copy.deepcopy(s);d["hotel_id"]=id
        raw+=json.dumps({"create":{"_id":id}})+"\n"+json.dumps(d,ensure_ascii=False)+"\n"
    r=request("POST","/"+INDEX+"/_bulk?refresh=true",raw);require(not r["errors"],"overflow created")
    probe=search("relevance-price");require(probe["hits"]["total"]["value"]==107 and len(probe["hits"]["hits"])==100,"actual 107/100 truncation")
    require(request("POST","/api/hotel-ranking/inspect",base,502,True)["code"]=="SEARCH_INCOMPLETE","full mode fails on truncation")
    raw="".join(json.dumps({"delete":{"_id":id}})+"\n" for id in injected)
    require(not request("POST","/"+INDEX+"/_bulk?refresh=true",raw)["errors"],"point-named overflow removal")
    cleanup();prepare();execute("relevance-price")
    # Single hard conditions are independent: neither is secretly enabled by preferred sorting.
    for field,expected_ids in [
        ("requireBreakfast",{"h01":["a02","a03","a04"],"h02":["b02"],"h05":["e01"],"h04":["d02"]}),
        ("requireFlexible",{"h01":["a03","a04"],"h02":["b01","b02"],"h05":["e01"],"h06":["f01"],"h04":["d02"]})]:
        body=dict(base);body[field]=True
        r=request("POST","/api/hotel-ranking/inspect",body,app=True)
        require({h["hotelId"]:[d["offerId"] for d in h["rooms"]] for h in r["hotels"]}==expected_ids,"single hard condition "+field)
        require(norm(search(r["esRequest"])["hits"])==norm(r["esResponse"]["hits"]),"single-flag Java REST exact replay")
    return dict(duplicate=400,bulk_conflicts=8,invalid_inputs=len(bodies),strict=400,changed_source=502,
        full_overflow="107 roots/100 returned -> 502",single_hard_conditions="both independent",recovered=True)
def cleanup():
    request("DELETE","/"+INDEX,status=[200,404]);r=request("GET","/"+INDEX,status=404)
    require(r["error"]["type"]=="index_not_found_exception","absent")
    return dict(deleted=INDEX,get_after=404)
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("section",choices=["prepare","hotels","rooms","boundary","errors","cleanup"])
    ap.add_argument("--out",required=True);args=ap.parse_args();out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True)
    LOG=out/(args.section+".jsonl");require(not LOG.exists(),"fresh receipt path required")
    value=globals()[args.section]();receipt=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        section=args.section,http_requests=COUNT,result=value)
    (out/(args.section+".json")).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(receipt,ensure_ascii=False))
