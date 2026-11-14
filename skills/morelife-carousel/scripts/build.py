"""More Life carousel builder: the "My story" format, locked 9 Nov 2026.

One full-bleed real photo per slide, black highlight boxes with white bold sans text,
red text on the negatives, an optional red pencil underline, at most one gold box per slide,
text placed in the photo's empty space (headspace above the head, or the floor below),
gold swipe arrow on every slide but the last. 1080x1350 (4:5).
Set "format": "story" in the spec for a story sequence: 1080x1920 (9:16), no arrow.

Usage:
    python3 build.py spec.json            # renders every slide to spec["out"]
    python3 build.py spec.json --sheet    # also writes contact-sheet.jpg to check the run at a glance

Text markup inside a line:
    [[words]]   red (negatives: the pain, the problem, the fear)
    __words__   red hand-drawn pencil underline (a name or a key phrase, once per carousel)
    \n          forced line break inside the box
Punctuation straight after a marked span sticks to it ("[[a dark place]]......" has no gap).
"""
import json, math, os, random, re, sys
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageEnhance

W, H = 1080, 1350
GOLD, BLACK, WHITE, RED = (212, 173, 110), (8, 6, 5), (255, 255, 255), (228, 52, 44)
CARD_BG = (13, 8, 6)
FONTS = [  # first that exists wins: Helvetica Neue Bold on a Mac, then free fallbacks
    ("/System/Library/Fonts/HelveticaNeue.ttc", 1),
    ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
    ("/Library/Fonts/Arial Bold.ttf", 0),
    ("C:/Windows/Fonts/arialbd.ttf", 0),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0),
    ("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 0),
]


def font(size):
    for path, idx in FONTS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size, index=idx)
    return ImageFont.load_default(size)


def fill(path, fx=.5, fy=.5, zoom=1.0):
    """crop the photo to 4:5 around the focus point (fx, fy as 0-1 of the photo), optional zoom in"""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    r = W / H
    cw, ch = (int(im.height * r), im.height) if im.width / im.height > r else (im.width, int(im.width / r))
    cw, ch = int(cw / zoom), int(ch / zoom)
    x = min(max(int(im.width * fx - cw / 2), 0), im.width - cw)
    y = min(max(int(im.height * fy - ch / 2), 0), im.height - ch)
    return im.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)


def card(path):
    """dark More Life ground with a screenshot / header image centred (for a podcast, a post, a doc)"""
    s = Image.new("RGB", (W, H), CARD_BG)
    im = Image.open(path).convert("RGB")
    im = im.resize((1000, int(im.height * 1000 / im.width)), Image.LANCZOS)
    s.paste(im, ((W - im.width) // 2, (H - im.height) // 2 - 40))
    return s


def parse(text, default):
    """markup -> [(text, colour, underline)]"""
    segs = []
    for part in re.split(r"(\[\[.*?\]\]|__.*?__)", text):
        if not part:
            continue
        if part.startswith("[["):
            segs.append((part[2:-2], RED, False))
        elif part.startswith("__"):
            segs.append((part[2:-2], default, True))
        else:
            segs.append((part, default, False))
    return segs


def layout(d, segs, f, maxw):
    """-> rows of (word, colour, glued_to_previous, underline); wraps on spaces, keeps colours"""
    words, prev = [], ""
    for t, c, u in segs:
        for k, part in enumerate(t.split("\n")):
            if k:
                words.append(("\n", c, False, u))
            for j, w in enumerate([w for w in part.split(" ") if w]):
                glue = j == 0 and k == 0 and prev and not prev.endswith(" ") and not t.startswith(" ")
                words.append((w, c, glue, u))
        prev = t
    rows, cur = [], []
    for item in words:
        if item[0] == "\n":
            rows.append(cur); cur = []; continue
        if item[2] and cur:
            cur.append(item); continue
        trial = " ".join(x[0] for x in cur + [item])
        if cur and d.textlength(trial, font=f) > maxw:
            rows.append(cur); cur = [item]
        else:
            cur.append(item)
    return rows + [cur]


def pencil(d, x0, x1, y):
    """hand-drawn pencil underline: two slightly wavy red strokes"""
    rnd = random.Random(7)
    for k, (dy, w) in enumerate(((0, 5), (5, 3))):
        n = 28
        pts = [(x0 + (x1 - x0) * j / n,
                y + dy + 2.2 * math.sin(j / n * 7 + k) + rnd.uniform(-.8, .8) - 3 * j / n) for j in range(n + 1)]
        d.line(pts, fill=RED, width=w, joint="curve")


def draw_group(img, lines, at, y0, size=42, maxw=880):
    """stack of boxes; at="top" puts the first box's top at y0, at="bottom" puts the last box's bottom at y0"""
    d = ImageDraw.Draw(img); f = font(size)
    lh, padx, pady, gap = int(size * 1.22), 24, 11, 14
    blocks = []
    for ln in lines:
        gold = ln.get("box", "k") == "g"
        blocks.append((layout(d, parse(ln["text"], BLACK if gold else WHITE), f, maxw), gold))
    total = sum(len(r) * lh + 2 * pady for r, _ in blocks) + gap * (len(blocks) - 1)
    y = y0 if at == "top" else y0 - total
    sp = d.textlength(" ", font=f)
    boxes = []
    for rows, gold in blocks:
        widths = [sum(d.textlength(t[0], font=f) for t in r) + sp * (len(r) - 1 - sum(1 for t in r[1:] if t[2]))
                  for r in rows]
        bw, bh = max(widths) + 2 * padx, len(rows) * lh + 2 * pady
        x0 = (W - bw) / 2
        d.rounded_rectangle((x0, y, x0 + bw, y + bh), radius=12, fill=GOLD if gold else BLACK)
        boxes.append((x0, y, x0 + bw, y + bh))
        for i, (r, rw) in enumerate(zip(rows, widths)):
            x, ul = (W - rw) / 2, []
            ty = y + pady + i * lh + 2
            for n, t in enumerate(r):
                w, c, _, u = t
                nxt_glued = n + 1 < len(r) and r[n + 1][2]
                d.text((x, ty), w, font=f, fill=c)
                tw = d.textlength(w, font=f)
                if u:
                    ul.append((x, x + tw + (sp if n + 1 < len(r) and r[n + 1][3] else 0)))
                x += tw + (0 if nxt_glued else sp)
            if ul:
                pencil(d, ul[0][0] - 4, max(e for _, e in ul) + 4, ty + size * 1.16)
        y += bh + gap
    return boxes


def arrow(img):
    d = ImageDraw.Draw(img); x, y = W - 120, H - 52
    d.line((x, y, x + 64, y), fill=GOLD, width=6)
    d.line((x + 40, y - 20, x + 66, y), fill=GOLD, width=6)
    d.line((x + 40, y + 20, x + 66, y), fill=GOLD, width=6)


def lint(spec):
    """the house rules, checked on the words before anything renders"""
    issues = []
    texts = [ln["text"] for s in spec["slides"] for g in s["groups"] for ln in g["lines"]]
    for i, s in enumerate(spec["slides"], 1):
        golds = sum(1 for g in s["groups"] for ln in g["lines"] if ln.get("box") == "g")
        if golds > 1:
            issues.append(f"slide {i}: {golds} gold boxes (max 1)")
        if len(s["groups"]) and sum(len(g["lines"]) for g in s["groups"]) > 5:
            issues.append(f"slide {i}: more than 5 boxes, cut it down")
    for t in texts:
        if "\u2014" in t or "\u2013" in t:
            issues.append(f"dash found (no em/en dashes): {t[:50]}")
    if not any("LIMITLESS" in t for t in texts):
        issues.append("no 'Comment LIMITLESS' CTA on the last slide")
    if sum(t.count("__") // 2 for t in texts) > 1:
        issues.append("more than one pencil underline in the carousel")
    return issues


def main():
    global W, H
    spec_path = sys.argv[1]
    spec = json.load(open(spec_path))
    story = spec.get("format") == "story"
    if story:
        W, H = 1080, 1920
    base = os.path.dirname(os.path.abspath(spec_path))
    rel = lambda p: p if os.path.isabs(os.path.expanduser(p)) else os.path.join(base, p)
    out = os.path.expanduser(spec.get("out", os.path.join(base, "export")))
    out = out if os.path.isabs(out) else os.path.join(base, out)
    if story:
        for i, sl in enumerate(spec["slides"], 1):
            for g in sl["groups"]:
                if (g.get("at", "top") == "top" and g["y"] < 250) or (g.get("at") == "bottom" and g["y"] > 1580):
                    print(f"CHECK: story frame {i}: text inside the top 250px / bottom 340px (IG covers it)")
    for msg in lint(spec):
        print("CHECK:", msg)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".jpg"):
            os.remove(os.path.join(out, f))
    n = len(spec["slides"])
    files = []
    for i, sl in enumerate(spec["slides"], 1):
        if "card" in sl:
            s = card(os.path.expanduser(rel(sl["card"])))
        else:
            fx, fy = sl.get("focus", [.5, .5])
            s = ImageEnhance.Brightness(fill(os.path.expanduser(rel(sl["photo"])), fx, fy, sl.get("zoom", 1.0))).enhance(.94)
        for g in sl["groups"]:
            draw_group(s, g["lines"], g.get("at", "top"), g["y"], size=sl.get("size", 42))
        if i < n and not story:
            arrow(s)
        p = os.path.join(out, f"{i:02d}.jpg")
        s.save(p, quality=95); files.append(p)
    if "--sheet" in sys.argv:
        cols, tw = 4, 270
        th = int(tw * H / W)
        rows = math.ceil(n / cols)
        sheet = Image.new("RGB", (cols * tw + (cols + 1) * 10, rows * th + (rows + 1) * 10), (20, 20, 20))
        for k, p in enumerate(files):
            sheet.paste(Image.open(p).resize((tw, th)), (10 + (k % cols) * (tw + 10), 10 + (k // cols) * (th + 10)))
        sheet.save(os.path.join(base, "contact-sheet.jpg"), quality=90)
    print(out, n)


if __name__ == "__main__":
    main()
