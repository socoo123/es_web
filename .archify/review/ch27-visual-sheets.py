"""Create contact sheets for inspecting the real final captures; no pass claim."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
out=Path(__file__).resolve().parent
sets=[['hero-desktop-light','hero-desktop-dark','hero-mobile-light','hero-mobile-dark'],['query-plan-standalone-light','query-plan-standalone-dark','query-plan-embedded-light','query-plan-embedded-dark'],['avg-pages-standalone-light','avg-pages-standalone-dark','avg-pages-embedded-light','avg-pages-embedded-dark'],['query-plan-mobile-light','query-plan-mobile-dark','avg-pages-mobile-light','avg-pages-mobile-dark'],['experiment-mobile-light','experiment-mobile-dark','source-table-mobile-light','source-table-mobile-dark'],['mechanism-desktop-light','mechanism-desktop-dark','mechanism-mobile-light','mechanism-mobile-dark'],[f'step-{i:02}-light' for i in range(1,8)]]
rows=[]
for i,names in enumerate(sets,1):
 tiles=[]
 for name in names:
  im=Image.open(out/('ch27-'+name+'.png')).convert('RGB');scale=min(720/im.width,1);im=im.resize((int(im.width*scale),int(im.height*scale)));tiles.append(im)
 height=max(t.height for t in tiles)+30;sheet=Image.new('RGB',(1440,height*((len(tiles)+1)//2)),(225,229,235));draw=ImageDraw.Draw(sheet)
 for j,(name,im) in enumerate(zip(names,tiles)):
  x=(j%2)*720;y=(j//2)*height;draw.text((x+10,y+8),name,fill=(0,0,0));sheet.paste(im,(x,y+30))
 path=f'ch27-visual-sheet-{i}.png';sheet.save(out/path);rows.append({'sheet':path,'captures':['ch27-'+n+'.png' for n in names]})
(out/'ch27-visual-sheets.json').write_text(json.dumps({'status':'capture-only-pending-human-image-inspection','sheets':rows},indent=2)+'\n');print('Created 7 contact sheets: 24 final chapter/diagram captures + all 7 mechanism snapshots.')
