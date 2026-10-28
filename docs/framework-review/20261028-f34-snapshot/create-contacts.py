#!/usr/bin/env python3
"""QA contact sheets from actual browser screenshots; originals stay untouched."""
import json,pathlib
from PIL import Image,ImageOps,ImageDraw
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];C=D/'contact';C.mkdir(exist_ok=True)
files=[R/x for x in json.loads((D/'http-review.json').read_text())['screenshots']]
files+=sorted((R/'projects/travel-search/review/f34/run-01/screenshots').glob('*.png'))
files+=sorted((R/'projects/travel-search/review/f34/run-02/screenshots').glob('*.png'))
index=[]
for start in range(0,len(files),8):
 chunk=files[start:start+8];sheet=Image.new('RGB',(1200,4*425),(225,229,234));draw=ImageDraw.Draw(sheet)
 for i,path in enumerate(chunk):
  img=Image.open(path).convert('RGB');img=ImageOps.contain(img,(590,390))
  x=(i%2)*600;y=(i//2)*425;sheet.paste(img,(x+(600-img.width)//2,y+28))
  label=path.parent.parent.name+'/'+path.name if '/run-' in str(path) else path.name
  draw.text((x+6,y+7),label,fill=(25,30,40))
 target=C/f'contact-{start//8+1:02d}.jpg';sheet.save(target,quality=90)
 index.append({'contact':str(target.relative_to(R)),'screenshots':[str(x.relative_to(R)) for x in chunk]})
(D/'contact-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
print(len(files),'original screenshots in',len(index),'contact sheets')
