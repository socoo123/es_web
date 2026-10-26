#!/usr/bin/env python3
"""Create labeled QA contact sheets; original PNGs remain untouched."""
import hashlib,json,pathlib
from PIL import Image,ImageDraw
HERE=pathlib.Path(__file__).resolve().parent;R=HERE.parents[2]
rows=[]
for source in ['http-review.json','shell-review.json','visual-detail.json']:
 for shot in json.loads((HERE/source).read_text())['screenshots']:
  p=R/shot['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==shot['sha256'];rows.append(dict(shot,receipt=source))
out=HERE/'montages';out.mkdir(exist_ok=True);manifest=[]
for offset in range(0,len(rows),6):
 group=rows[offset:offset+6];canvas=Image.new('RGB',(1500,1800),'#e7e7e7');d=ImageDraw.Draw(canvas)
 for j,row in enumerate(group):
  im=Image.open(R/row['path']).convert('RGB');im.thumbnail((480,830));x=(j%3)*500+(500-im.width)//2;y=(j//3)*900+50;canvas.paste(im,(x,y));d.text(((j%3)*500+10,(j//3)*900+8),pathlib.Path(row['path']).name,fill='#111111');d.text(((j%3)*500+10,(j//3)*900+24),f'original {Image.open(R/row["path"]).size}',fill='#111111')
 name=f'overview-{offset//6+1:02}.png';canvas.save(out/name);manifest.append({'overview':str((out/name).relative_to(R)),'screenshots':group,'review':'pending'})
(HERE/'montage-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('screenshots',len(rows),'contact sheets',len(manifest))
