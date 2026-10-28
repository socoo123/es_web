#!/usr/bin/env python3
import datetime,gzip,hashlib,json,pathlib,subprocess,urllib.request,zipfile
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/travel-search';D=P/'review/f31'
JDK='/tmp/es-f29-tooling/jdk-25.0.4.1+1/Contents/Home'
def cmd(args,cwd=R):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT,text=True).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
assert 'BUILD SUCCESS' in gzip.decompress((D/'build.log.gz').read_bytes()).decode() and 'No tests to run' in gzip.decompress((D/'build.log.gz').read_bytes()).decode()
assert 'BUILD SUCCESS' in gzip.decompress((D/'dependency-tree.log.gz').read_bytes()).decode()
jar=P/'backend/target/travel-search-0.7.0.jar';resources=[]
with zipfile.ZipFile(jar) as z:
 for name in ['index.html','shell.js','shell.css']:
  source=(P/'backend/src/main/resources/static'/name).read_bytes();pack=z.read('BOOT-INF/classes/static/'+name)
  live=urllib.request.urlopen('http://127.0.0.1:18081/'+('' if name=='index.html' else name)).read()
  assert source==pack==live
  resources.append({'file':name,'source_jar_http_equal':True,'sha256':sha(source)})
 libs=[n for n in z.namelist() if '/lib/' in n and any(x in n for x in ['elasticsearch-','spring-boot-4'])]
containers=json.loads(cmd(['docker','inspect']+['es-framework-f31-'+n+'-1' for n in ['n1','n2','n3']]))
checks=[]
for c in containers:
 assert not c['State']['OOMKilled']
 assert c['State']['Running']==(c['Config']['Labels']['com.docker.compose.service']!='n3')
 checks.append({'name':c['Name'],'id':c['Id'],'state':c['State'],'memory_limit_bytes':c['HostConfig']['Memory'],'image_id':c['Image'],'ports':c['HostConfig']['PortBindings']})
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'application_java':cmd([JDK+'/bin/java','-version']).splitlines(),'maven_version':cmd([str(P/'backend/mvnw'),'-version'],cwd=P/'backend').splitlines(),'es_bundled_java':cmd(['docker','exec','es-framework-f31-n1-1','/usr/share/elasticsearch/jdk/bin/java','-version']).splitlines(),'docker_vm':json.loads(cmd(['docker','info','--format','{"memory_bytes":{{.MemTotal}},"cpus":{{.NCPU}}}'])),'docker_stats':cmd(['docker','stats','--no-stream','--format','{{.Name}} {{.MemUsage}}']).splitlines(),'containers':checks,'jar_sha256':sha(jar.read_bytes()),'packaged_libraries':libs,'resources':resources,'build':'clean package and dependency tree succeeded; no test source, not a test pass','reuse':'shared backend/frontend unchanged; operational requests stay in isolated lab','passed':True}
(D/'runtime.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F31 actual toolchain/runtime/resources verified')
