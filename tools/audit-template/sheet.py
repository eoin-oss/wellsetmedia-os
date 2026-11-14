#!/usr/bin/env python3
"""Contact sheets of reel covers (since Feb 2026) labelled with index, views, current tag and letterbox flag.
Used to correct tags visually before a build. Output: /tmp-style scratch path given as argv[1]."""
import json, os, sys
from PIL import Image, ImageDraw
os.chdir(os.path.dirname(os.path.abspath(__file__)))
out_dir = sys.argv[1]
R = json.load(open('data/ig_reels.json')); T = json.load(open('data/ig_tags.json'))
CL = json.load(open('data/config.json')).get('client', {})                # the analysis window comes from the client config
rows = [r for r in R if CL.get('now_from', '0000') <= r['date'] < CL.get('fresh_before', '9999')]

def lb(p):
    im = Image.open(p).convert('L'); w, h = im.size; band = max(4, int(h * 0.10))
    m = lambda x: sum(x.getdata()) / (x.size[0] * x.size[1])
    return m(im.crop((0, int(h*.02), w, int(h*.02)+band))) < 14 and m(im.crop((0, h-int(h*.02)-band, w, h-int(h*.02)))) < 14

W, H, COLS, PER = 150, 267, 10, 50
for s in range(0, len(rows), PER):
    chunk = rows[s:s+PER]; nrow = (len(chunk) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * W, nrow * (H + 30)), (14, 17, 19)); dr = ImageDraw.Draw(sheet)
    for i, r in enumerate(chunk):
        x = (i % COLS) * W; y = (i // COLS) * (H + 30); p = f"img/covers/{r['code']}.jpg"
        if os.path.exists(p):
            im = Image.open(p).convert('RGB'); im = im.resize((W, int(im.height * W / im.width)))
            sheet.paste(im.crop((0, 0, W, min(H, im.height))), (x, y))
            flag = 'LB' if lb(p) else ''
        else:
            flag = 'nocover'
        tag = T.get(r['code'], ['?'])[0]
        dr.text((x + 4, y + H + 2), f"{s+i} {r['views']} {flag}", fill=(237, 233, 214))
        dr.text((x + 4, y + H + 15), f"{tag} {r['code'][:6]}", fill=(72, 160, 188))
    sheet.save(os.path.join(out_dir, f'covers_{s//PER}.jpg'), quality=80)
print(len(rows), 'reels ->', (len(rows) + PER - 1) // PER, 'sheets')
