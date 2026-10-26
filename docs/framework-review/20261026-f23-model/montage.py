#!/usr/bin/env python3
"""Readable labeled screenshot overview for author visual QA; originals preserved."""
import json,pathlib,math
from PIL import Image,ImageOps,ImageDraw,ImageFont
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
paths=sorted((HERE/'screenshots').glob('*.png'));out=HERE/'contact-sheets';out.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
manifest=[]
for n in range(0,len(paths),6):
 group=paths[n:n+6];tiles=[]
 for p in group:
  im=Image.open(p).convert('RGB');thumb=ImageOps.contain(im,(520,1100))
  tile=Image.new('RGB',(550,1160),'#d6d6d6');tile.paste(thumb,((550-thumb.width)//2,45));ImageDraw.Draw(tile).text((10,10),p.stem[:58],font=font,fill='black');tiles.append(tile)
 sheet=Image.new('RGB',(550*3,1160*2),'white')
 for i,t in enumerate(tiles):sheet.paste(t,((i%3)*550,(i//3)*1160))
 target=out/f'overview-{n//6+1:02}.jpg';sheet.save(target,quality=90)
 manifest.append({'path':str(target.relative_to(ROOT)),'screenshots':[str(p.relative_to(ROOT)) for p in group],'opened_for_review':False})
(HERE/'montage-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(len(paths),'PNGs in',len(manifest),'overviews')
