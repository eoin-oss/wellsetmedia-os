"""Story sequence renderer: turns the editable page's saved frames into final JPGs.
1080x1920 for stories; doc "format": "carousel" gives 1080x1350 (4:5) slides.

It mirrors the page's CSS exactly (cover crop + object-position + zoom about the focus point,
box sizes, padding, gaps, top/bottom anchoring), so what Eoin or the client approved on the page
is what gets exported.

Usage:
    python3 render.py story.json photos_dir out_dir [--sheet]

story.json = the page's db doc {"frames": [...], "theme": {...}} (ArtifactData get, out_dir).
photos_dir = full-resolution photos; a frame's "photo" matches a file by lowercase stem.
Text markup per line: [[red words]] (pain), {{green words}} (the win), a line starting "! " is a red box (hook); a line starting "* " is the accent box. One line = one box.
"""
import json, math, os, re, sys
from PIL import Image, ImageOps, ImageDraw, ImageFont

W, H = 1080, 1920
BLACK, WHITE, RED, GREEN = (8, 6, 5), (255, 255, 255), (228, 52, 44), (52, 211, 102)
FONTS = [("/System/Library/Fonts/HelveticaNeue.ttc", 1),
         ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
         ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0)]


def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(size):
    for p, i in FONTS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size, index=i)
    return ImageFont.load_default(size)


def find_photo(d, stem):
    for f in os.listdir(d):
        if os.path.splitext(f)[0].lower() == stem.lower() and not f.startswith("._"):
            return os.path.join(d, f)
    raise SystemExit(f"photo not found: {stem} in {d}")


def plate(path, fx, fy, zoom):
    """CSS: object-fit:cover; object-position:fx fy; transform:scale(zoom) origin (fx,fy) of the frame"""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    iw, ih = im.size
    s = max(W / iw, H / ih)
    offx, offy = (W - iw * s) * fx, (H - ih * s) * fy
    ox, oy = fx * W, fy * H
    x0f, y0f = ox - ox / zoom, oy - oy / zoom            # frame point shown at the frame's top-left
    x1f, y1f = ox + (W - ox) / zoom, oy + (H - oy) / zoom
    box = ((x0f - offx) / s, (y0f - offy) / s, (x1f - offx) / s, (y1f - offy) / s)
    return im.resize((W, H), Image.LANCZOS, box=box)


def segs(text, base):
    out = []
    for part in re.split(r"(\[\[.*?\]\]|\{\{.*?\}\})", text):
        if part:
            if part.startswith("[["): out.append((part[2:-2], RED))
            elif part.startswith("{{"): out.append((part[2:-2], GREEN))
            else: out.append((part, base))
    return out


def wrap(d, sg, f, maxw):
    words, prev = [], ""
    for t, c in sg:
        for j, w in enumerate([w for w in t.split(" ") if w]):
            glue = j == 0 and prev and not prev.endswith(" ") and not t.startswith(" ")
            words.append((w, c, glue))
        prev = t
    rows, cur = [], []
    for it in words:
        if it[2] and cur:
            cur.append(it); continue
        trial = " ".join(x[0] for x in cur + [it])
        if cur and d.textlength(trial, font=f) > maxw:
            rows.append(cur); cur = [it]
        else:
            cur.append(it)
    return rows + [cur] if cur else rows


def group(img, text, at, y0, size, accent, accent_ink):
    lines = [l.strip() for l in (text or "").split("\n") if l.strip()]
    if not lines:
        return
    d = ImageDraw.Draw(img); f = font(size)
    lh, padx, pady, gap = size * 1.22, 24, 11, 14
    blocks = []
    for ln in lines:
        acc = ln.startswith("* ")
        hot = ln.startswith("! ")                 # red box, white text: the hook line
        t = ln[2:] if (acc or hot) else ln
        sg = segs(t, accent_ink if acc else WHITE)
        if hot: sg = [(s, WHITE) for s, c in sg]
        if acc: sg = [(s, (21, 128, 61) if c == GREEN else c) for s, c in sg]   # darker green on the light accent box
        blocks.append((wrap(d, sg, f, 880), "hot" if hot else acc))
    total = sum(len(r) * lh + 2 * pady for r, _ in blocks) + gap * (len(blocks) - 1)
    y = y0 if at == "top" else y0 - total
    sp = d.textlength(" ", font=f)
    for rows, acc in blocks:
        widths = [sum(d.textlength(w, font=f) for w, _, _ in r) + sp * (len(r) - 1 - sum(1 for t in r[1:] if t[2]))
                  for r in rows]
        bw, bh = max(widths) + 2 * padx, len(rows) * lh + 2 * pady
        x0 = (W - bw) / 2
        d.rounded_rectangle((x0, y, x0 + bw, y + bh), radius=12, fill=RED if acc == "hot" else accent if acc else BLACK)
        for i, (r, rw) in enumerate(zip(rows, widths)):
            x = (W - rw) / 2; ty = y + pady + i * lh + (lh - size) / 2 - size * 0.06
            for n, (w, c, _) in enumerate(r):
                d.text((x, ty), w, font=f, fill=c)
                glued = n + 1 < len(r) and r[n + 1][2]
                x += d.textlength(w, font=f) + (0 if glued else sp)
        y += bh + gap


def lint(frames, carousel=False):
    out = []
    lo, hi = (80, 1270) if carousel else (250, 1580)
    for i, fr in enumerate(frames, 1):
        txt = (fr.get("top") or "") + "\n" + (fr.get("bottom") or "")
        lines = [l.strip() for l in txt.split("\n") if l.strip()]
        if sum(l.startswith("* ") for l in lines) > 1:
            out.append(f"frame {i}: more than one accent box")
        if len(lines) > 5:
            out.append(f"frame {i}: {len(lines)} boxes (max 5)")
        if "—" in txt or "–" in txt:
            out.append(f"frame {i}: em/en dash")
        if not carousel and i < len(frames) and lines and not lines[-1].endswith("..."):
            out.append(f"frame {i}: last box doesn't end on '...'")
        if fr.get("topY", 999) < lo or fr.get("botY", 0) > hi:
            out.append(f"frame {i}: text outside the safe area ({lo} to {hi})")
    return out


def main():
    doc = json.load(open(sys.argv[1]))
    doc = doc.get("data", doc)
    photos, out = sys.argv[2], os.path.expanduser(sys.argv[3])
    th = doc.get("theme", {})
    accent, ink = hexrgb(th.get("accent", "#ffffff")), hexrgb(th.get("accentInk", "#080605"))
    global H
    carousel = doc.get("format") == "carousel"
    H = 1350 if carousel else 1920
    frames = doc["frames"]
    for m in lint(frames, carousel):
        print("CHECK:", m)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".jpg"):
            os.remove(os.path.join(out, f))
    files = []
    for i, fr in enumerate(frames, 1):
        img = plate(find_photo(photos, fr["photo"]), fr.get("fx", .5), fr.get("fy", .5), fr.get("zoom", 1) or 1)
        sz = int(fr.get("size", 42))
        group(img, fr.get("top"), "top", fr.get("topY", 270), sz, accent, ink)
        group(img, fr.get("bottom"), "bottom", fr.get("botY", 1560), sz, accent, ink)
        p = os.path.join(out, f"{i:02d}.jpg"); img.save(p, quality=95); files.append(p)
    if "--sheet" in sys.argv:
        tw = 270; t_h = int(tw * H / W); cols = min(4, len(files)); rows = math.ceil(len(files) / cols)
        sh = Image.new("RGB", (cols * tw + (cols + 1) * 10, rows * t_h + (rows + 1) * 10), (20, 20, 20))
        for k, p in enumerate(files):
            sh.paste(Image.open(p).resize((tw, t_h)), (10 + (k % cols) * (tw + 10), 10 + (k // cols) * (t_h + 10)))
        sh.save(os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "contact-sheet.jpg"), quality=90)
    print(out, len(files))


if __name__ == "__main__":
    main()
