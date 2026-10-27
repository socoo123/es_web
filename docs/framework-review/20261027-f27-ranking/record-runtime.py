#!/usr/bin/env python3
"""Record actual build/runtime versions and source/package/HTTP byte identity."""
import datetime,gzip,hashlib,json,pathlib,subprocess,urllib.request,zipfile
R=pathlib.Path(__file__).resolve().parents[3];P=R/"projects/travel-search"
D=P/"review/f27";JDK=pathlib.Path("/tmp/es-f07-tooling/jdk-25.0.4.1+1/Contents/Home")
def sha(v):return hashlib.sha256(v).hexdigest()
def run(args):return subprocess.check_output(args,stderr=subprocess.STDOUT,text=True).splitlines()
jar=P/"backend/target/travel-search-0.7.0.jar"
r=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),application_java=run([str(JDK/"bin/java"),"-version"]),
    actual_maven_version_lines=pathlib.Path("/tmp/f27-maven-version.txt").read_text().splitlines(),
    es_bundled_java=run(["docker","exec","es-framework-f27-es-1","/usr/share/elasticsearch/jdk/bin/java","-version"]),
    java_pid=run(["lsof","-tiTCP:18081","-sTCP:LISTEN"])[0],
    image_id=run(["docker","inspect","es-framework-f27-es-1","--format","{{.Image}}"])[0],
    jar_sha256=sha(jar.read_bytes()),resources=[],logs={})
with zipfile.ZipFile(jar) as z:
    r["relevant_packaged_libraries"]=[n for n in z.namelist() if n.startswith("BOOT-INF/lib/") and any(k in n for k in ["elasticsearch","spring-boot-4","jackson-databind"])]
    for name in ["f27.html","shell-f27.js","shell-f27.css"]:
        source=(P/"backend/src/main/resources/static"/name).read_bytes()
        package=z.read("BOOT-INF/classes/static/"+name)
        http=urllib.request.urlopen("http://127.0.0.1:18081/"+name).read()
        assert source==package==http,name
        r["resources"].append(dict(name=name,sha256=sha(source),source_jar_http_bytes_equal=True))
    table=(P/"data/f27/stay-table.json").read_bytes()
    assert table==z.read("BOOT-INF/classes/f27/stay-table.json")
    r["packaged_table_sha256"]=sha(table)
for name,origin in [("build.log","/tmp/f27-build-final.log"),("dependency-tree.txt","/tmp/f27-dependency-tree.txt"),
                    ("maven-version.txt","/tmp/f27-maven-version.txt"),("java-app.log","/tmp/f27-java-final.log")]:
    raw=pathlib.Path(origin).read_bytes();gz=gzip.compress(raw,mtime=0)
    (D/(name+".gz")).write_bytes(gz)
    readable="\n".join(line.rstrip() for line in raw.decode().splitlines())+"\n"
    (D/name).write_text(readable)
    r["logs"][name]=dict(raw_sha256=sha(raw),gzip_sha256=sha(gz),readable_sha256=sha(readable.encode()),
        normalization="Readable trailing whitespace stripped; original bytes in .gz")
version=json.load(urllib.request.urlopen("http://127.0.0.1:19227/"))
r.update(es=version["version"]["number"],lucene=version["version"]["lucene_version"],spring_boot="4.0.8",
    java_api_client="9.4.8",rest5_client="9.4.8",maven_wrapper="3.3.4",maven="3.9.11",
    build="clean package BUILD SUCCESS; no test sources; No tests to run is not a test-suite pass")
assert r["es"]=="9.4.0" and r["lucene"]=="10.4.0"
assert "BUILD SUCCESS" in (D/"build.log").read_text()
assert "BUILD SUCCESS" in (D/"dependency-tree.txt").read_text()
(D/"runtime.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
print("Build/runtime versions and source/jar/HTTP resource bytes verified")
