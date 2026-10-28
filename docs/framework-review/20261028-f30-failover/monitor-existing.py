#!/usr/bin/env python3
import datetime,json,pathlib,subprocess,time
D=pathlib.Path(__file__).resolve().parent
baseline=json.loads((D/'existing-node-restored.json').read_text())
while not pathlib.Path('/tmp/f30-monitor-stop').exists():
 c=json.loads(subprocess.check_output(['docker','inspect','es-study-secure']))[0]
 r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'id':c['Id'],'pid':c['State']['Pid'],'started_at':c['State']['StartedAt'],'running':c['State']['Running'],'health':c['State']['Health']['Status']}
 r['unchanged_since_restoration']=r['id']==baseline['id'] and r['pid']==baseline['pid'] and r['started_at']==baseline['started_at'] and r['running'] and r['health']=='healthy'
 with (D/'existing-node-monitor.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
 if not r['unchanged_since_restoration']:raise RuntimeError(r)
 time.sleep(5)
