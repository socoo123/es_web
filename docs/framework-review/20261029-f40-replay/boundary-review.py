#!/usr/bin/env python3
"""Author-only final classifier/REST probes after run-06, before F40 cleanup."""
import copy,datetime,hashlib,json,os,pathlib,subprocess,tempfile,urllib.error,urllib.request
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/travel-search';D=pathlib.Path(__file__).resolve().parent
JAVA=pathlib.Path(os.environ['JAVA_HOME'])/'bin'
OUT=P/'review/f40/boundary'
def check(ok,detail):
 if not ok:raise AssertionError(detail)
def run(args,expected=0):
 r=subprocess.run([str(x) for x in args],cwd=P,text=True,capture_output=True,timeout=90)
 check(r.returncode==expected,{'command':[str(x) for x in args],'code':r.returncode,'stdout':r.stdout[-2000:],'stderr':r.stderr[-2000:]})
 return {'exit_code':r.returncode,'records':[json.loads(x) for x in r.stdout.splitlines() if x.startswith('{')],'stderr':r.stderr}
def save(name,value):(OUT/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def req(method,path,body=None,expected=200):
 request=urllib.request.Request('http://127.0.0.1:20440'+path,method=method,data=None if body is None else json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(request,timeout=15) as response:status=response.status;value=json.load(response)
 except urllib.error.HTTPError as e:status=e.code;value=json.load(e)
 check(status==expected,{'status':status,'value':value});return value
def main():
 OUT.mkdir(exist_ok=False)
 check(json.loads((P/'review/f40/run-06/summary.json').read_text())['passed'],'Run-06 must finish first')
 cp='backend/target/classes:'+ (P/'backend/target/f40-classpath.txt').read_text().strip()+':'+(P/'labs/f40/target/projection-classpath.txt').read_text().strip()
 with tempfile.TemporaryDirectory(prefix='f40-final-classes-') as temp:
  run([JAVA/'javac','--release','25','-cp',cp,'-d',temp,P/'labs/f40/java/F40Consumer.java',D/'F40BoundaryProbe.java'])
  def java(*args):return run([JAVA/'java','-Xmx128m','-cp',temp+':'+cp,*args])
  def inspect():return java('F40Consumer','inspect')['records'][-1]['positions']
  def dlq():return [v for v in java('F40Consumer','dlq')['records'] if v['kind']=='event']
  before=inspect();original_dlq=dlq();check(len(original_dlq)==1,'Expected original real DLQ only')
  events=json.loads((P/'review/f40/run-06/final-events.json').read_text())
  p02=next(e for e in events if (lambda v:v['after']['attraction_id']=='p02' and v['after']['revision']==4)(json.loads(e['value'])))
  envelope=json.loads(p02['value']);document=json.loads(envelope['after']['document']);document['ticket_price_fen']=1201
  envelope['after']['document']=json.dumps(document,ensure_ascii=False)
  fixture={'topic':p02['origin']['topic'],'synthetic_offset':1000000,'key':p02['key'],'value':json.dumps(envelope,ensure_ascii=False),'should_block':True,'synthetic_fixture':True,'note':'Deliberately conflicting payload for already-applied p02 revision 4; not a source broker record.'}
  save('same-revision-conflict-fixture',fixture)
  result=java('F40BoundaryProbe',str(OUT/'same-revision-conflict-fixture.json'));save('same-revision-conflict-result',result)
  check(any(v['kind']=='item' and v['status']==400 and 'script_exception' in v['error'] for v in result['records']),result)
  check(len(dlq())==1,'Script conflict must block even with park enabled, not DLQ')
  before_document=req('GET','/tut-f40-attractions-v001/_doc/p02')['_source'];check(before_document['ticket_price_fen']==1200,before_document)
  stale=java('F40Consumer','repair',str(P/'review/f40/run-06/reviewed-repair.json'));save('stale-repair-noop',stale)
  check(any(v['kind']=='item' and v['result']=='noop' for v in stale['records']),stale)
  # Test the public repair-file command's refusal to relabel a newer source state.
  rejected=run([os.environ.get('F40_PYTHON','python3'),'labs/f40/lab.py','repair-file','--out',str(OUT/'repair-file-rejected')],expected=1)
  check('Newer source state exists' in rejected['stderr'],rejected);save('newer-source-repair-rejected',rejected)
  envelope=copy.deepcopy(envelope);after=envelope['after'];after['attraction_id']='p04';after['revision']=1
  document.update(attraction_id='p04',sync_revision=1,ticket_price_fen='broken');after['document']=json.dumps(document,ensure_ascii=False)
  fixture.update(synthetic_offset=1000001,value=json.dumps(envelope,ensure_ascii=False),should_block=False,note='Synthetic p04 mapping failure; no matching PostgreSQL/Kafka source record. Never committed to source group.')
  save('mapping-data-fixture',fixture);result=java('F40BoundaryProbe',str(OUT/'mapping-data-fixture.json'));save('mapping-data-result',result)
  check(any(v['kind']=='parked' for v in result['records']),result);check(len(dlq())==2,'Mapping data failure not durably parked')
  req('GET','/tut-f40-attractions-v001/_doc/p04',expected=404)
  # REST sample uses exactly the real immutable v2 document bytes for its hash.
  sample=json.loads((P/'search/f40/guard-example.json').read_text())
  old=next(json.loads(e['value'])['after'] for e in events if (lambda v:v['after']['attraction_id']=='p01' and v['after']['revision']==2)(json.loads(e['value'])))
  check(sample['script']['params']['document']['sync_hash']==hashlib.sha256(old['document'].encode()).hexdigest(),'REST sample fingerprint differs from real immutable source')
  response=req('POST','/tut-f40-attractions-write/_update/p01?require_alias=true&retry_on_conflict=3',sample);check(response['result']=='noop',response);save('rest-guard-replay',response)
  check(req('GET','/tut-f40-attractions-v001/_doc/p02')['_source']==before_document,'Boundary probe changed p02')
  after=inspect();check(before==after,{'before':before,'after':after})
  save('dlq-after',dlq());save('summary',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'source_positions_before':before,'source_positions_after':after,'real_source_records_added':0,'synthetic_fixtures':2,'script_conflict_blocked_not_parked':True,'mapping_failure_durably_parked':True,'dlq_count_before':1,'dlq_count_after':2,'stale_repair_noop':True,'newer_source_repair_file_rejected':True,'rest_sample_exact_fingerprint_and_noop':True,'p02_unchanged':True,'synthetic_p04_not_created':True})
 print('F40 final mapping/script classifier, stale repair, newer-source refusal and REST sample passed')
if __name__=='__main__':main()
