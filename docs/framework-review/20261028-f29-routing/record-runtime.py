#!/usr/bin/env python3
import datetime,hashlib,json,pathlib,subprocess,urllib.request,zipfile
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/travel-search';D=P/'review/f29'
JDK='/tmp/es-f29-tooling/jdk-25.0.4.1+1/Contents/Home'
def cmd(args):return subprocess.check_output(args,cwd=R,stderr=subprocess.STDOUT,text=True).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
jar=P/'backend/target/travel-search-0.7.0.jar';resources=[]
with zipfile.ZipFile(jar) as z:
 for name in ['index.html','shell.js','shell.css']:
  source=(P/'backend/src/main/resources/static'/name).read_bytes();pack=z.read('BOOT-INF/classes/static/'+name)
  live=urllib.request.urlopen('http://127.0.0.1:18081/'+('' if name=='index.html' else name)).read()
  assert source==pack==live;resources.append({'file':name,'source_jar_http_equal':True,'sha256':sha(source)})
 libs=[n for n in z.namelist() if '/lib/' in n and any(x in n for x in ['elasticsearch-','spring-boot-4'])]
for f in ['build.log','dependency-tree.txt']:assert 'BUILD SUCCESS' in (D/f).read_text(),f
mvn=(D/'maven-version.txt').read_text();assert 'Java version: 25.0.4.1' in mvn and 'Maven 3.9.11' in mvn
archive=pathlib.Path('/tmp/es-f29-tooling/jdk.tar.gz');official=pathlib.Path('/tmp/es-f29-tooling/jdk.sha256.txt').read_text().split()[0];assert sha(archive.read_bytes())==official
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'application_java':cmd([JDK+'/bin/java','-version']).splitlines(),'maven':mvn.splitlines(),'es_bundled_java':cmd(['docker','exec','es-framework-f29-es1-1','/usr/share/elasticsearch/jdk/bin/java','-version']).splitlines(),'image_id':cmd(['docker','image','inspect','docker.elastic.co/elasticsearch/elasticsearch:9.4.0','--format','{{.Id}}']),'docker_vm':json.loads(cmd(['docker','info','--format','{"memory_bytes":{{.MemTotal}},"cpus":{{.NCPU}}}'])),'jar_sha256':sha(jar.read_bytes()),'packaged_libraries':libs,'resources':resources,'java_pid':json.loads((D/'process.json').read_text())['pid'],'build':'clean package and classpath generation passed; no test sources, No tests to run is not a test pass','reuse':'shared backend/service/frontend unchanged; independent RoutingLab.java uses official client and existing F07 request builder','toolchain_recovery':{'old_jdk_missing_file':'lib/jvm.cfg; initial build failed, attempts log retained','adoptium_version_api_http':404,'official_package_url':'https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.4.1%2B1/OpenJDK25U-jdk_aarch64_mac_hotspot_25.0.4.1_1.tar.gz','official_archive_sha256_verified':official},'scope':'single endpoint; no HA client/fault/performance claim'}
if (D/'log-normalization.json').exists():rec['maven_log_preservation']=json.loads((D/'log-normalization.json').read_text())
(D/'runtime.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F29 actual runtime/build/static resources and official archive checks passed')
