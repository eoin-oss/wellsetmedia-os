"""Preview of the layered edit at given timeline seconds: each layer is rendered by Resolve (preview.py) and the
layers are stacked here into one contact sheet, for review only (the edit itself lives in Resolve).
Usage: python3 stack_preview.py <source video> <out.jpg> <sec> [<sec> ...]"""
import os, subprocess, sys, tempfile
from PIL import Image
from preview import render

src, out, secs = sys.argv[1], sys.argv[2], [float(s) for s in sys.argv[3:]]
tmp = tempfile.mkdtemp(dir=os.path.dirname(out))
layers = {tr: render(tr, secs, tmp) for tr in (2, 3, 4, 5, 6)}
tiles = []
for k, s in enumerate(secs):
    fp = f"{tmp}/base_{k}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s), "-i", src, "-frames:v", "1", fp], check=True)
    im = Image.open(fp).convert("RGBA")
    for tr in (2, 3, 4, 5, 6):
        p = layers[tr][k]
        if p:
            im.alpha_composite(Image.open(p).convert("RGBA").resize(im.size))
    tiles.append(im.convert("RGB").resize((960, 540)))
cols = 2 if len(tiles) > 1 else 1
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (960 * cols, 540 * rows))
for i, t in enumerate(tiles):
    sheet.paste(t, (960 * (i % cols), 540 * (i // cols)))
sheet.save(out, quality=88)
print(out)
