#!/usr/bin/env python3
"""Check fixed F27 data, then clean only this lesson's resources."""
import datetime,importlib.util,json,os,pathlib,signal,socket,subprocess,time
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/"projects/travel-search"
spec=importlib.util.spec_from_file_location("f27cleanup",P/"labs/f27/lab.py");lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
lab.LOG=D/"workspace-es-before-cleanup.jsonl";assert not lab.LOG.exists()
expected=json.loads((P/"data/f27/hotels.json").read_text())
docs=lab.request("POST","/tut-f27-hotels/_mget",{"ids":[h["hotel_id"] for h in expected]})["docs"]
assert all(d["found"] and d["_source"]==s for d,s in zip(docs,expected))
count=lab.request("GET","/tut-f27-hotels/_count")["count"];assert count==8
stats=lab.request("GET","/tut-f27-hotels/_stats/search")
assert stats["_all"]["total"]["search"]["open_contexts"]==0
runtime=json.loads((P/"review/f27/runtime.json").read_text())
pid=int(subprocess.check_output(["lsof","-tiTCP:18081","-sTCP:LISTEN"],text=True).strip())
assert pid==int(runtime["java_pid"])
command=subprocess.check_output(["ps","-p",str(pid),"-o","command="],text=True).strip()
assert "-jar target/travel-search-0.7.0.jar" in command
subprocess.run(["python3",str(P/"labs/f27/lab.py"),"cleanup","--out",str(P/"review/f27/final-cleanup")],check=True)
os.kill(pid,signal.SIGTERM)
for _ in range(50):
    try:os.kill(pid,0)
    except ProcessLookupError:break
    time.sleep(0.1)
else:raise AssertionError("Own Java process did not exit after SIGTERM")
subprocess.run(["docker","compose","-f",str(P/"infra/f27/compose.yaml"),"down"],check=True,capture_output=True)
vol=subprocess.check_output(["docker","volume","inspect","es-framework-f27_f27-data","--format","{{.Name}}"],text=True).strip()
before=json.loads(pathlib.Path("/tmp/f27-secure-before.json").read_text())
after=json.loads(subprocess.check_output(["docker","inspect","es-study-secure","--format","{{json .}}"],text=True))
def safe(d):return dict(id=d["Id"],name=d["Name"],started_at=d["State"]["StartedAt"],pid=d["State"]["Pid"],running=d["State"]["Running"],health=d["State"]["Health"]["Status"])
assert safe(before)==safe(after) and after["State"]["Running"] and after["State"]["Health"]["Status"]=="healthy"
closed={}
for port in [18081,19227]:
    with socket.socket() as s:s.settimeout(1);closed[str(port)]=s.connect_ex(("127.0.0.1",port))!=0
assert all(closed.values())
rec=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status="passed",before_cleanup=dict(hotels=count,all_8_sources_exact=True,nested_summaries=19,open_search_contexts=0,inspection_http=lab.COUNT),
    own_java=dict(pid=pid,command=command,stopped_by="SIGTERM",port_closed=closed["18081"]),
    f27=dict(index="tut-f27-hotels",delete_confirmed_get_404=True,container_network="removed by own compose down",volume_preserved=vol,image_preserved=runtime["image_id"],port_closed=closed["19227"]),
    unrelated_secure_node=dict(before=safe(before),after=safe(after),unchanged=True))
(D/"workspace-state.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
print("F27 sources checked, own index/Java/container/network cleaned; volume/image and secure node preserved")
