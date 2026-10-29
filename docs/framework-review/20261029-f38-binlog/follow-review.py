#!/usr/bin/env python3
"""Additional check for the reader's persistent follow mode, after the two formal drains."""
import datetime,gzip,importlib.util,json,os,pathlib,signal,subprocess,time
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f38lab',P/'labs/f38/lab.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 out=P/'review/f38/follow';lab=m.Lab(out);lab.case='follow-additional';log=(out/'consumer.log').open('w')
 proc=subprocess.Popen(['bash','labs/f38/java.sh','follow'],cwd=P,stdout=log,stderr=subprocess.STDOUT)
 def price(expected):
  m.check(proc.poll() is None,'Consumer exited')
  r=lab.req('GET','/'+m.READ+'/_doc/p04',record=False)
  return r['_source']['ticket_price_fen']==expected
 try:
  lab.sql(text="UPDATE travel_f38.attraction SET ticket_price_fen=1900 WHERE attraction_id='p04';")
  m.wait(lambda:price(1900),'follow applies first live update',45)
  lab.save('first',lab.req('GET','/'+m.READ+'/_doc/p04'))
  lab.sql(text="UPDATE travel_f38.attraction SET ticket_price_fen=1800 WHERE attraction_id='p04';")
  m.wait(lambda:price(1800),'follow applies restored price',45)
  lab.save('restored',lab.req('GET','/'+m.READ+'/_doc/p04'))
  # ES acknowledgment precedes commit; wait for the log's per-record post-commit receipt.
  m.wait(lambda:'"committed_next":13' in (out/'consumer.log').read_text(),'follow commits both updates',30)
 finally:
  proc.send_signal(signal.SIGINT)
  try:proc.wait(timeout=15)
  except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=15)
  log.close()
 # Ctrl+C is an abrupt JVM stop in this small main; wait until Kafka expires its membership.
 def inactive():
  r=m.command(m.kafka('kafka-consumer-groups','--describe','--group',m.GROUP),required=False)
  return 'has no active members' in r.stderr
 m.wait(inactive,'Stopped follow group has no active member',60)
 lab.refresh();want=lab.expected();lab.docs(want,'final-full-fields');pos=lab.position('positions')
 events=lab.inspect('events');m.check(len(events)==13,events)
 applied=[json.loads(s) for s in (out/'consumer.log').read_text().splitlines() if s.startswith('{')]
 m.check(len(applied)==2 and [e['offset'] for e in applied]==[11,12] and applied[-1]['committed_next']==13,applied)
 lab.save('summary',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'mode':'follow','new_records':applied,'price_observation_fen':[1800,1900,1800],'final_complete_documents':want,'stopped_process_exit_code':proc.returncode,'member_expiry_waited':True,'separate_from_formal_rounds':True})
 raw=out/'consumer.log';raw.with_suffix('.log.gz').write_bytes(gzip.compress(raw.read_bytes(),mtime=0));raw.unlink()
 print('F38 persistent follow mode applied two live updates and preserved complete final state')
if __name__=='__main__':main()
