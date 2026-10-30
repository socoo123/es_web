#!/usr/bin/env python3
"""Additional real-ES synthetic target fixtures; excluded from 15 source events."""
import datetime,importlib.util,json,pathlib
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('f42',R/'projects/travel-search/labs/f42/lab.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 lab=m.Lab(R/'projects/travel-search/review/f42/extra-rejections');lab.identity();lab.case='synthetic-rejections'
 before=lab.positions();original=lab.req('GET','/'+m.INDEX['v1']+'/_doc/p01')['_source'];rec={'at':m.now(),'fixtures':[]}
 def refuse(kind):
  report=lab.audit('final');assert report['findings'][0]['kind']==kind
  try:lab.repair('final')
  except AssertionError as e:assert 'No automatic repair' in str(e);rec['fixtures'].append({'kind':kind,'rejected':str(e),'findings':report['findings']})
  else:raise AssertionError('Repair unexpectedly accepted a synthetic target')
 try:
  bad=dict(original);bad['sync_revision']=999;lab.req('PUT','/'+m.INDEX['v1']+'/_doc/p01',bad)
  refuse('ahead_revision')
 finally:lab.req('PUT','/'+m.INDEX['v1']+'/_doc/p01',original)
 unknown={'attraction_id':'p99','sync_revision':1,'sync_deleted':True,'sync_hash':'synthetic-unknown','projection_schema':1}
 try:
  lab.req('PUT','/'+m.INDEX['v1']+'/_doc/p99',unknown,expected=201);refuse('unexpected')
 finally:lab.req('DELETE','/'+m.INDEX['v1']+'/_doc/p99')
 assert lab.audit('final')['clean'];after=lab.positions();assert before['end']==after['end']==15 and before['committed_next']==after['committed_next']
 rec.update(before=before,after=after,source_events_added=0,restored_and_clean=True,passed=True)
 lab.save('summary',rec);lab.close();print('F42 extra real target rejections and restore passed')
if __name__=='__main__':main()
