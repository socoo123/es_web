#!/usr/bin/env python3
import json,math,pathlib
from PIL import Image,ImageDraw
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2]
paths=json.loads((D/'http-review.json').read_text())['screenshots']
for f in sorted((R/'projects/travel-search/review/f31/round-1').glob('*-browser.json')):
 for name in json.loads(f.read_text())['screenshots']:paths.append(str((f.parent/name).relative_to(R)))
paths+=json.loads((D/'extra-screenshots.json').read_text())['screenshots']
records=[]
for page in range(math.ceil(len(paths)/12)):
 group=paths[page*12:(page+1)*12];sheet=Image.new('RGB',(1230,1160),'#dfe5eb');draw=ImageDraw.Draw(sheet)
 for i,name in enumerate(group):
  with Image.open(R/name) as src:
   im=src.convert('RGB');im.thumbnail((390,250))
  x=10+(i%3)*410;y=10+(i//3)*290
  sheet.paste(im,(x+(390-im.width)//2,y+25))
  draw.text((x,y),str(page*12+i+1)+': '+pathlib.Path(name).name[:53],fill='black')
 path=D/f'contact-{page+1}.jpg';sheet.save(path,quality=87)
 records.append({'contact':str(path.relative_to(R)),'screenshots':group})
(D/'contact-sheets.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print('Contacts:',len(records),'screenshots:',len(paths))
