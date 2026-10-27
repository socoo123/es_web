#!/usr/bin/env python3
"""Contact sheets for actual screenshot inspection; no product image manipulation."""
import hashlib,json,pathlib
from PIL import Image,ImageDraw
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent
items=[]
for name in ["http-review.json","shell-review.json","visual-followup.json"]:
    if not (D/name).exists():continue
    items += json.loads((D/name).read_text())["screenshots"]
out=D/"montages";out.mkdir(exist_ok=True);manifest=[]
for offset in range(0,len(items),6):
    batch=items[offset:offset+6];sheet=Image.new("RGB",(1080,1380),"#e5e7eb");draw=ImageDraw.Draw(sheet)
    cells=[]
    for i,item in enumerate(batch):
        path=R/item["path"];assert hashlib.sha256(path.read_bytes()).hexdigest()==item["sha256"]
        with Image.open(path) as im:
            im=im.convert("RGB");im.thumbnail((340,638))
            x=(i%3)*360+10;y=(i//3)*690+36
            sheet.paste(im,(x,y));draw.text((x,y-24),path.name[:45],fill="#111827")
            cells.append(item["path"])
    path=out/f"overview-{offset//6+1:02}.png";sheet.save(path)
    manifest.append(dict(path=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),screenshots=cells))
(D/"montage-manifest.json").write_text(json.dumps(dict(screenshot_count=len(items),montages=manifest),ensure_ascii=False,indent=2)+"\n")
print(len(items),"screenshots in",len(manifest),"contact sheets")
