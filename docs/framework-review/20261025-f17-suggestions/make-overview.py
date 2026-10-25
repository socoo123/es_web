from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2];O=D/'overview';O.mkdir(exist_ok=True)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
paths=sorted((D/'screenshots').glob('*.png'))
for k in range(0,len(paths),8):
 chunk=paths[k:k+8];canvas=Image.new('RGB',(1600,2200),'#dedede');draw=ImageDraw.Draw(canvas)
 for n,p in enumerate(chunk):
  im=Image.open(p).convert('RGB');im.thumbnail((380,1010))
  x=(n%4)*400+10;y=(n//4)*1100+50
  canvas.paste(im,(x+(380-im.width)//2,y));draw.text((x,y-40),p.stem[:38],fill='black',font=font)
 canvas.save(O/(f'{k//8+1:02}.jpg'),quality=88)
print(len(paths),'screenshots in',len(list(O.glob('*.jpg'))),'overview sheets')
