#!/usr/bin/env python3
import datetime,gzip,hashlib,json,os,pathlib,subprocess,urllib.request,zipfile
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/travel-search';D=P/'review/f32'
JDK='/tmp/es-f29-tooling/jdk-25.0.4.1+1/Contents/Home'
def cmd(args,cwd=R):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
build=gzip.decompress((D/'build.log.gz').read_bytes()).decode() if (D/'build.log.gz').exists() else (D/'build.log').read_text()
assert 'BUILD SUCCESS' in build and 'No tests to run' in build
tree=gzip.decompress((D/'dependency-tree.log.gz').read_bytes()).decode() if (D/'dependency-tree.log.gz').exists() else (D/'dependency-tree.log').read_text()
assert 'BUILD SUCCESS' in tree
jar=P/'backend/target/travel-search-0.7.0.jar';resources=[]
with zipfile.ZipFile(jar) as z:
 for name in ['index.html','shell.js','shell.css']:
  source=(P/'backend/src/main/resources/static'/name).read_bytes();pack=z.read('BOOT-INF/classes/static/'+name)
  live=urllib.request.urlopen('http://127.0.0.1:18082/'+('' if name=='index.html' else name)).read()
  assert source==pack==live
  resources.append({'file':name,'source_jar_http_equal':True,'sha256':sha(source)})
 libs=[n for n in z.namelist() if '/lib/' in n and any(x in n for x in ['elasticsearch-','spring-boot-4'])]
containers=json.loads(cmd(['docker','inspect']+['es-framework-f32-'+n+'-1' for n in ['n1','n2']]))
checks=[]
for c in containers:
 assert not c['State']['OOMKilled']
 assert c['State']['Running']
 checks.append({'name':c['Name'],'id':c['Id'],'state':c['State'],'memory_limit_bytes':c['HostConfig']['Memory'],'image_id':c['Image'],'ports':c['HostConfig']['PortBindings']})
pid=[line[1:] for line in cmd(['lsof','-nP','-iTCP:18082','-sTCP:LISTEN','-Fp']).splitlines() if line.startswith('p')]
assert len(pid)==1
pid=int(pid[0])
assert (D/'application.log').read_text().count('Started TravelSearchApplication')==1
rec={'application_pid':pid,'application_single_start_log':True,'application_index_config':'tut-f32-attractions-read','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'application_java':cmd([JDK+'/bin/java','-version']).splitlines(),'maven_version':cmd([str(P/'backend/mvnw'),'-version'],cwd=P/'backend').splitlines(),'es_bundled_java':cmd(['docker','exec','es-framework-f32-n1-1','/usr/share/elasticsearch/jdk/bin/java','-version']).splitlines(),'docker_vm':json.loads(cmd(['docker','info','--format','{"memory_bytes":{{.MemTotal}},"cpus":{{.NCPU}}}'])),'docker_stats':cmd(['docker','stats','--no-stream','--format','{{.Name}} {{.MemUsage}}']).splitlines(),'containers':checks,'jar_sha256':sha(jar.read_bytes()),'packaged_libraries':libs,'resources':resources,'build':'clean package and dependency tree succeeded; no test source, not a test pass','reuse':'shared backend/frontend unchanged; operational requests stay in isolated lab','passed':True}
(D/'runtime.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F32 actual toolchain/runtime/resources verified')
