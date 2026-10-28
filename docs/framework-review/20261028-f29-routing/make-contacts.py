#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,math
from PIL import Image,ImageOps,ImageDraw
D=Path(__file__).resolve().parent;S=D/'screenshots';records=[]
files=sorted(S.glob('*.png'))
for part in range(math.ceil(len(files)/12)):
 group=files[part*12:(part+1)*12];sheet=Image.new('RGB',(1200,4*340),'#e6e9ed');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(group):
  image=Image.open(p).convert('RGB');thumb=ImageOps.contain(image,(390,310));x=(i%3)*400;y=(i//3)*340
  sheet.paste(thumb,(x+(400-thumb.width)//2,y+24));draw.text((x+5,y+3),p.name,fill='#111111')
 path=D/f'contact-{part+1}.jpg';sheet.save(path,quality=90)
 records.append({'contact':path.name,'screenshots':[p.name for p in group]})
(D/'contact-sheets.json').write_text(json.dumps({'groups':records,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+'\n')
print(len(files),'actual screenshots in',len(records),'overview contact sheets')
