#!/usr/bin/env python3
import datetime,hashlib,json,os,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];D=ROOT/'framework/diagrams/f27'
CLI=os.environ.get('D2_BIN','/tmp/es-framework-d2-20261013/d2');checks=[]
for slug in ['layers','coverage']:
 source=str((D/(slug+'.d2')).relative_to(ROOT))
 commands=[['fmt',source],['fmt','--check',source],['validate',source]]
 commands += [['--layout=dagre','--theme='+str(t),'--pad=24','--timeout=30',source,str((D/(slug+'-'+theme+'.svg')).relative_to(ROOT))] for theme,t in [('light',4),('dark',201)]]
 for args in commands:
  p=subprocess.run([CLI]+args,cwd=ROOT,text=True,capture_output=True);r={'command':[CLI]+args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};checks.append(r);assert p.returncode==0,r
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'generator':subprocess.check_output([CLI,'--version'],text=True).strip(),'cli_sha256':hashlib.sha256(pathlib.Path(CLI).read_bytes()).hexdigest(),'layout':'dagre','themes':{'light':4,'dark':201},'checks':checks,'artifact_edits':'official CLI only; D2 source edits, no manual SVG edits','scope':'hotel and within-hotel room order; full vs top2 coverage; conceptual arrows, no performance claim','sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir() if p.suffix in ['.d2','.svg']}}
(D/'generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('D2 fmt / validate / 4 exports passed')
