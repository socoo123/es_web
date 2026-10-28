#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,math
from PIL import Image,ImageOps,ImageDraw
D=Path(__file__).resolve().parent;S=D/'screenshots';files=sorted(p for p in S.glob('*.png') if p.name.startswith(('java-code-','shell-','final-')));records=[]
for part in range(math.ceil(len(files)/12)):
 group=files[part*12:(part+1)*12];sheet=Image.new('RGB',(1200,1360),'#e6e9ed');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(group):
  im=ImageOps.contain(Image.open(p).convert('RGB'),(390,310));x=i%3*400;y=i//3*340;sheet.paste(im,(x+(400-im.width)//2,y+24));draw.text((x+4,y+4),p.name,fill='#111111')
 target=D/f'extra-contact-{part+1}.jpg';sheet.save(target,quality=90);records.append({'contact':target.name,'screenshots':[p.name for p in group]})
(D/'extra-contacts.json').write_text(json.dumps({'groups':records,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+'\n');print(len(files),'extra actual screenshots in',len(records),'contacts')
