#!/usr/bin/env python3
from PIL import Image,ImageOps,ImageDraw
import json,pathlib
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
paths=sorted((D/'screenshots').glob('*.png'))+sorted((R/'projects/travel-search/review/f30/round1/screenshots').glob('*.png'))
records=[]
for b in range(0,len(paths),12):
 group=paths[b:b+12];sheet=Image.new('RGB',(4*320,3*330),'#e6e6e6');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(group):
  thumb=ImageOps.contain(Image.open(p).convert('RGB'),(310,298));x=(i%4)*320;y=(i//4)*330
  sheet.paste(thumb,(x+(320-thumb.width)//2,y+23));draw.text((x+4,y+3),p.stem[:43],fill='#202020')
 name=f'contact-{b//12+1}.jpg';sheet.save(D/name,quality=90);records.append({'image':name,'sources':[str(p.relative_to(R)) for p in group]})
(D/'contact-sheets.json').write_text(json.dumps(records,indent=2)+'\n');print('Contact sheets',len(records),'from',len(paths),'PNGs')
