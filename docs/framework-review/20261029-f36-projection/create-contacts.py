#!/usr/bin/env python3
import pathlib,json,math
from PIL import Image,ImageOps,ImageDraw
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
paths=sorted((D/'screenshots').glob('*.png'))
for run in ['01','02']:paths+=sorted((R/('projects/travel-search/review/f36/run-'+run+'/screenshots')).glob('*.png'))
C=D/'contacts';C.mkdir(exist_ok=True);idx=[]
for n,start in enumerate(range(0,len(paths),12),1):
 group=paths[start:start+12];sheet=Image.new('RGB',(1260,550*math.ceil(len(group)/3)), '#d4dae1');draw=ImageDraw.Draw(sheet)
 for i,path in enumerate(group):
  im=Image.open(path).convert('RGB');im.thumbnail((408,510));x=(i%3)*420;y=(i//3)*550
  sheet.paste(im,(x+(420-im.width)//2,y+30));draw.text((x+6,y+4),str(path.relative_to(R))[-65:],fill='#131b25')
 out=C/f'contact-{n:02d}.jpg';sheet.save(out,quality=85)
 idx.append({'contact':str(out.relative_to(R)),'originals':[str(p.relative_to(R)) for p in group]})
(D/'contact-index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'originals':len(paths),'sheets':len(idx)},ensure_ascii=False))
