#!/usr/bin/env python3
"""Observe the existing node identity/health and VM memory without changing it."""
import datetime,json,pathlib,subprocess,time
D=pathlib.Path(__file__).resolve().parent
stop=pathlib.Path('/tmp/es-f32-monitor-stop')
def snapshot():
 c=json.loads(subprocess.check_output(['docker','inspect','es-study-secure']))[0]
 return {'id':c['Id'],'pid':c['State']['Pid'],'started_at':c['State']['StartedAt'],'running':c['State']['Running'],'health':c['State']['Health']['Status']}
before=snapshot();(D/'existing-node-before.json').write_text(json.dumps(before,indent=2)+'\n')
while not stop.exists():
 current=snapshot();row={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),**current,'unchanged':current==before}
 with (D/'existing-node-monitor.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 if current!=before:raise RuntimeError(row)
 time.sleep(5)
