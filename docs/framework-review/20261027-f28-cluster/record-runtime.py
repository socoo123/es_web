#!/usr/bin/env python3
import datetime,hashlib,json,pathlib,subprocess,urllib.request,zipfile
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/travel-search';D=P/'review/f28'
def command(args):return subprocess.check_output(args,cwd=R,stderr=subprocess.STDOUT,text=True).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
jar=P/'backend/target/travel-search-0.7.0.jar';jdk='/tmp/es-f07-tooling/jdk-25.0.4.1+1/Contents/Home/bin/java'
with zipfile.ZipFile(jar) as z:
 resources=[]
 for name in ['index.html','shell.js','shell.css']:
  source=(P/'backend/src/main/resources/static'/name).read_bytes();pack=z.read('BOOT-INF/classes/static/'+name)
  live=urllib.request.urlopen('http://127.0.0.1:18081/'+('' if name=='index.html' else name)).read()
  assert source==pack==live
  resources.append({'file':name,'source_jar_http_bytes_equal':True,'sha256':sha(source)})
 libs=[n for n in z.namelist() if '/lib/' in n and any(x in n for x in ['elasticsearch-','spring-boot-4'])]
actual_mvn=(D/'maven-version.txt').read_text();build=(D/'build.log').read_text();deps=(D/'dependency-tree.txt').read_text()
assert 'BUILD SUCCESS' in build and 'BUILD SUCCESS' in deps
assert 'Java version: 25.0.4.1' in actual_mvn and 'Apache Maven 3.9.11' in actual_mvn
for value in ['4.0.8','9.4.8']:assert value in deps
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'application_java':command([jdk,'-version']).splitlines(),'maven_version':actual_mvn.splitlines(),'es_bundled_java':command(['docker','exec','es-framework-f28-es1-1','/usr/share/elasticsearch/jdk/bin/java','-version']).splitlines(),'image_id':command(['docker','image','inspect','docker.elastic.co/elasticsearch/elasticsearch:9.4.0','--format','{{.Id}}']),'docker_vm':json.loads(command(['docker','info','--format','{"memory_bytes":{{.MemTotal}},"cpus":{{.NCPU}}}'])),'jar_sha256':sha(jar.read_bytes()),'packaged_libraries':libs,'resources':resources,'java_pid_from_log':__import__('re').search(r'Starting TravelSearchApplication.*PID (\d+)',(D/'java-app.log').read_text()).group(1),'build':'clean package passed; no test sources: No tests to run is NOT a test pass','reuse':'F07 Java code and shell unchanged; ES_URL=19229, ES_INDEX=tut-f28-attractions; single endpoint, no HA client claim','logs_sha256':{p.name:sha(p.read_bytes()) for p in [D/'build.log',D/'dependency-tree.txt',D/'maven-version.txt']}}
(D/'runtime.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F28 actual build/runtime/resource checks passed')
