#!/usr/bin/env python3
import datetime,gzip,hashlib,importlib.util,json,os,pathlib,subprocess,urllib.request,zipfile
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search';B=P/'backend'
spec=importlib.util.spec_from_file_location('lab',P/'labs/f35/lab.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
lab=m.Lab(P/'review/f35/runtime-check');lab.case='runtime'
java=pathlib.Path(os.environ['JAVA_HOME'])/'bin';classpath=str(B/'target/classes')+':'+(B/'target/f35-classpath.txt').read_text().strip()
def cmd(args):return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT).strip()
rec={'at':m.now(),'java_application':cmd([str(java/'java'),'-version']).splitlines(),'maven':cmd([str(B/'mvnw'),'-v']).splitlines(),'build':'clean package, classpath and dependency tree passed; no test source, not a unit-test pass','containers':[]}
try:
 lab.identity();rec['loaded_certificates']=lab.req('GET','/_ssl/certificates')
 rec['node_tls_settings']=lab.req('GET','/_nodes/settings?flat_settings=true')['nodes']
 for name in ['n1','n2']:
  v=json.loads(cmd(['docker','inspect','es-framework-f35-'+name+'-1']))[0]
  rec['containers'].append({'name':v['Name'],'id':v['Id'],'state':v['State'],'image_id':v['Image'],'memory_limit':v['HostConfig']['Memory'],'ports':v['NetworkSettings']['Ports']})
 rec['es_bundled_java']=cmd(['docker','exec','es-framework-f35-n1-1','/usr/share/elasticsearch/jdk/bin/java','-version']).splitlines()
 rec['docker_stats']=cmd(['docker','stats','--no-stream','--format','{{.Name}} {{.MemUsage}}']).splitlines()
 info=json.loads(cmd(['docker','info','--format','{{json .}}']));rec['docker_vm']={'memory_bytes':info['MemTotal'],'cpus':info['NCPU']}
 rec['openssl_version']=cmd(['openssl','version'])
 rec['server_certificate']=cmd(['openssl','x509','-in',str(m.LOCAL/'n1/server.crt'),'-noout','-subject','-issuer','-dates','-ext','subjectAltName']).splitlines()
 rec['jar_sha256']=hashlib.sha256((B/'target/travel-search-0.7.0.jar').read_bytes()).hexdigest()
 lab.start_app('runtime-resources')
 with zipfile.ZipFile(B/'target/travel-search-0.7.0.jar') as z:
  rec['packaged_libraries']=[p for p in z.namelist() if p.endswith('.jar') and any(x in p for x in ['spring-boot-4','elasticsearch-java','elasticsearch-rest5'])]
  rec['resources']=[]
  for name in ['index.html','shell.js','shell.css']:
   source=(B/'src/main/resources/static'/name).read_bytes();packed=z.read('BOOT-INF/classes/static/'+name);response=urllib.request.urlopen(m.APP+'/'+name).read()
   assert source==packed==response
   rec['resources'].append({'file':name,'source_jar_http_equal':True,'sha256':hashlib.sha256(source).hexdigest()})
  assert z.read('BOOT-INF/classes/dev/esweb/travel/EsConfiguration.class')==(B/'target/classes/dev/esweb/travel/EsConfiguration.class').read_bytes()
 rec['java_client_class_matches_package']=True
 dest=pathlib.Path('/tmp/es-f35-factory-review');dest.mkdir(exist_ok=True)
 subprocess.run([str(java/'javac'),'-cp',classpath,'-d',str(dest),str(D/'FactoryReview.java')],check=True,capture_output=True,text=True)
 probe=cmd([str(java/'java'),'-cp',str(dest)+':'+classpath,'FactoryReview',str(m.LOCAL/'ca.crt'),str(m.LOCAL/'reader-key.txt')]);rec['factory_review']=json.loads(probe)
 assert rec['factory_review']['rejected_insecure_or_partial_configurations']==6
 rec['passed']=True
finally:
 lab.stop_app();(P/'review/f35/runtime.json').write_text(json.dumps(m.redact(rec),ensure_ascii=False,indent=2)+'\n')
gzip.open(P/'review/f35/build.log.gz','wt').write(pathlib.Path('/tmp/es-f35-build.log').read_text())
print('F35 build/package/runtime/factory evidence passed')
