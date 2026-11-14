"""stills from the current timeline at given seconds -> contact sheets in jobs/vsl/grabs"""
import os, sys
import rv
from PIL import Image, ImageDraw
D = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../jobs/vsl/grabs"))
os.makedirs(D, exist_ok=True)
r = rv.connect(); p = r.GetProjectManager().GetCurrentProject(); t = p.GetCurrentTimeline()
r.OpenPage("edit")
T = [float(x) for x in sys.argv[2:]]
ims = []
for s in T:
    pth = f"{D}/g{s:07.2f}.jpg"
    rv.still(p, t, s, pth, 25.0)
    im = Image.open(pth).convert("RGB").resize((480, 270)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 60, 16], fill="black"); d.text((3, 2), str(s), fill="yellow"); ims.append(im)
for k in range(0, len(ims), 20):
    S = Image.new("RGB", (1920, 1350))
    for i, im in enumerate(ims[k:k + 20]):
        S.paste(im, ((i % 4) * 480, (i // 4) * 270))
    S.save(f"{D}/{sys.argv[1]}{k // 20}.jpg")
