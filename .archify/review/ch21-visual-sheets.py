"""Generate contact sheets only; this does not claim actual visual review."""
from pathlib import Path
import json
from PIL import Image,ImageOps,ImageDraw
out=Path(__file__).resolve().parent
report=json.loads((out/'ch21-http-review.json').read_text());files=report['captures']
for batch in range(0,len(files),4):
 rows=[]
 for name in files[batch:batch+4]:
  im=Image.open(out/name).convert('RGB');im.thumbnail((680,1200))
  box=Image.new('RGB',(700,im.height+40),'#d4dae3');box.paste(im,((700-im.width)//2,40));ImageDraw.Draw(box).text((12,12),Path(name).name,fill='black');rows.append(box)
 canvas=Image.new('RGB',(1400,sum(max(im.height for im in rows[i:i+2]) for i in range(0,len(rows),2))),'#bcc5d2');y=0
 for i in range(0,len(rows),2):
  for j,im in enumerate(rows[i:i+2]):canvas.paste(im,(j*700,y))
  y+=max(im.height for im in rows[i:i+2])
 canvas.save(out/f'ch21-contact-{batch//4+1}.png')
print('Generated',len(range(0,len(files),4)),'sheets; actual inspection required.')
