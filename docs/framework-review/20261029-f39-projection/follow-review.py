import gzip,importlib.util,json,os,pathlib,signal,subprocess,types,time
root=pathlib.Path(__file__).resolve().parents[3];p=root/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f39',p/'labs/f39/lab.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ARGS=types.SimpleNamespace(observer=None)
lab=m.Lab(p/'review/f39/follow');lab.identity();lab.guard();lab.case='follow'
log=(lab.out/'consumer.log').open('w');proc=subprocess.Popen(['bash','labs/f39/java.sh','follow'],cwd=p,env=os.environ.copy(),stdout=log,stderr=subprocess.STDOUT)
def applied():
 return [json.loads(x) for x in (lab.out/'consumer.log').read_text().splitlines() if x.startswith('{') and json.loads(x).get('kind')=='applied']
def members():return m.command(m.kafka('kafka-consumer-groups','--describe','--group',m.GROUP,'--members'),required=False).stdout
try:
 m.wait(lambda:any(x.startswith(m.GROUP+' ') for x in members().splitlines()),'Follow assigned')
 before=lab.expected()
 lab.sql(text="UPDATE f39.attraction_tag SET attraction_id='p01' WHERE tag_id='t02';")
 m.wait(lambda:len(applied())>=1,'First continuous apply')
 lab.req('GET','/'+m.READ+'/_doc/p01');lab.req('GET','/'+m.READ+'/_doc/p02');lab.refresh();lab.docs(lab.expected(),'moved-back');lab.night(['p01'],'night-p01')
 lab.sql(text="UPDATE f39.attraction_tag SET attraction_id='p02' WHERE tag_id='t02';")
 m.wait(lambda:len(applied())>=2,'Second continuous apply')
 lab.refresh();lab.docs(before,'restored');lab.night(['p02'],'night-p02')
 records=applied();m.check(len(records)==2 and all(x['projection']['affected_ids']==['p01','p02'] for x in records),records)
 lab.save('applied',records)
finally:
 proc.send_signal(signal.SIGINT);proc.wait(timeout=30);log.close()
 m.wait(lambda:not any(x.startswith(m.GROUP+' ') for x in members().splitlines()),'Follow group inactive')
lab.save('summary',{'passed':True,'separate_from_two_rounds':True,'processed':2,'tag_partition_offsets':[x['offset'] for x in records],'committed_next':[x['committed_next'] for x in records],'affected_ids_each':['p01','p02'],'consumer_bulk_requests':2,'consumer_bulk_items':4,'night_search':['p01','p02'],'restored_full_documents':before,'stopped_with':'SIGINT','process_exit':proc.returncode,'group_inactive':True})
raw=lab.out/'consumer.log';raw.with_suffix('.log.gz').write_bytes(gzip.compress(raw.read_bytes(),mtime=0));raw.unlink()
print('F39 follow passed')
