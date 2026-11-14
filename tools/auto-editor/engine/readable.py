"""Readability gate. HARD RULE (Eoin 23 Oct 2026): every piece of on-screen text in every video must be readable,
and the editor checks it itself instead of leaving it to his eye. Any mode can use both checks:

 1. pre-build  zone_lum / zone_ok: how bright the part of an image is that text will sit on, before anything is
    built (cover-crop aware). White text needs the zone dark enough for MIN_RATIO.
 2. post-build qa(manifest): pulls a Resolve still at the middle of every text item and measures the contrast between
    the letters and what sits right around them (outline + shadow count, so outlined white text on a light wall passes
    and bare white text on white sand fails). Prints every failure with its timestamp; exit 1 if any.

Manifest (json, written by the builder):
  {"timeline": "<name>", "items": [{"t": sec, "box": [x0, y0, x1, y1], "rgb": [r, g, b], "label": "...", "min": 3.0}]}
Usage: python3 readable.py <manifest.json> [<manifest.json> ...]"""
import json, os, sys, time
import numpy as np
from PIL import Image, ImageFilter

MIN_RATIO = 3.0   # WCAG large-text contrast; titles and captions are all large text


def lum(a):
    """relative luminance of an sRGB array in 0..1"""
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def ratio(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def zone_lum(path, cell_w, cell_h, fy0, fy1, fx0=0.0, fx1=1.0):
    """mean luminance of the fraction box (fx0..fx1, fy0..fy1) of a cell_w x cell_h cover-cropped image"""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    ca = cell_w / cell_h
    cw, ch = (h * ca, h) if w / h > ca else (w, w / ca)
    x0, y0 = (w - cw) / 2, (h - ch) / 2
    c = im.crop((int(x0 + fx0 * cw), int(y0 + fy0 * ch), int(x0 + fx1 * cw), int(y0 + fy1 * ch)))
    return float(lum(np.asarray(c).astype(float) / 255).mean())


def zone_ok(path, rgb, cell_w, cell_h, fy0, fy1, fx0=0.0, fx1=1.0, min_ratio=MIN_RATIO):
    tl = float(lum(np.array(rgb, dtype=float)))
    bl = zone_lum(path, cell_w, cell_h, fy0, fy1, fx0, fx1)
    return ratio(tl, bl) >= min_ratio, ratio(tl, bl), bl


def measure(still, box, rgb):
    """contrast between the text and the ring 2-7px around its letters (outline/shadow included)"""
    im = Image.open(still).convert("RGB")
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    crop = im.crop((max(0, x0), max(0, y0), min(im.width, x1), min(im.height, y1)))
    a = np.asarray(crop).astype(float) / 255
    dist = np.sqrt(((a - np.array(rgb)) ** 2).sum(-1))
    mask = dist < 0.22
    if mask.mean() < 0.004:
        return None  # text not found in the box
    m = Image.fromarray((mask * 255).astype(np.uint8))
    outer = np.asarray(m.filter(ImageFilter.MaxFilter(15))) > 0
    inner = np.asarray(m.filter(ImageFilter.MaxFilter(5))) > 0
    ring = outer & ~inner
    L = lum(a)
    tl = float(np.median(L[mask]))
    bl = float(np.percentile(L[ring], 60)) if ring.any() else float(L.mean())
    return ratio(tl, bl)


def grab(timeline_name, secs, out):
    sys.path.insert(0, os.path.dirname(__file__))
    from resolve import connect
    r = connect()
    p = r.GetProjectManager().GetCurrentProject()
    t = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == timeline_name)
    p.SetCurrentTimeline(t)
    r.OpenPage("edit")
    fps = float(t.GetSetting("timelineFrameRate"))
    os.makedirs(out, exist_ok=True)
    paths = []
    for s in secs:
        f = t.GetStartFrame() + int(s * fps)
        fr = int(round(fps))
        hh, rem = divmod(f, fr * 3600); mm, rem = divmod(rem, fr * 60); ss, ff = divmod(rem, fr)
        t.SetCurrentTimecode(f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}")
        time.sleep(0.8)
        path = f"{out}/q{s:07.2f}.jpg"
        ok = p.ExportCurrentFrameAsStill(path)
        if not ok:  # one retry: the viewer sometimes lags a page switch
            time.sleep(1.5); ok = p.ExportCurrentFrameAsStill(path)
        paths.append(path if ok else None)
    return paths


def qa(manifest_path):
    m = json.load(open(manifest_path))
    items = m["items"]
    out = os.path.join(os.path.dirname(os.path.abspath(manifest_path)), "readable")  # Resolve resolves relative paths against its own cwd
    stills = grab(m["timeline"], [it["t"] for it in items], out)
    fails = []
    for it, st in zip(items, stills):
        r = measure(st, it["box"], it["rgb"]) if st else None
        need = it.get("min", MIN_RATIO)
        if r is None or r < need:
            fails.append(f"  {it['t']:6.2f}s  {it['label'][:40]:40s}  " + ("text not found" if r is None else f"contrast {r:.2f} < {need}"))
    print(f"{m['timeline']}: {len(items) - len(fails)}/{len(items)} readable")
    for f in fails:
        print(f)
    return not fails


if __name__ == "__main__":
    ok = all([qa(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
