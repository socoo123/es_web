#!/usr/bin/env python3
import json,pathlib
from PIL import Image,ImageDraw
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];S=D/'screenshots';OUT=D/'contacts';OUT.mkdir(exist_ok=True)
NAMES=['f43-1440-light-opening.png','f43-390-dark-opening.png','results-1440-light-bulk-results.png','results-1440-dark-mixed-results.png','results-390-light-mixed-results-left.png','results-390-dark-mixed-results.png','results-320-dark-resource-results.png','results-320-light-drills.png','whole-measurement-light.png','whole-measurement-dark.png','whole-compare-light.png','whole-compare-dark.png']
files=[S/n for n in NAMES]+sorted((ROOT/'projects/travel-search/review/f43/run-02/screenshots').glob('*.png'));records=[]
for k in range(0,len(files),4):
 page=Image.new('RGB',(1280,1500),'#c9c9c9');draw=ImageDraw.Draw(page)
 for j,f in enumerate(files[k:k+4]):
  im=Image.open(f).convert('RGB');im.thumbnail((630,710));page.paste(im,((j%2)*640+(640-im.width)//2,(j//2)*750+34));draw.text(((j%2)*640+8,(j//2)*750+7),f.name,fill='black')
 dest=OUT/f'contact-{k//4+1:02d}.jpg';page.save(dest,quality=88);records.append({'file':str(dest.relative_to(ROOT)),'sources':[str(f.relative_to(ROOT)) for f in files[k:k+4]]})
(D/'contacts.json').write_text(json.dumps(records,indent=2)+'\n')
