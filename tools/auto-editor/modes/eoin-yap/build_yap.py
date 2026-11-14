"""eoin-yap mode: Eoin's personal yap reels (talking head, music already on the take), built natively in Resolve.
Look from the 23 Oct reference (coachkyle, Big Boy Maxxing): a landscape image card above the head that hard-cuts on
every beat, a keyword written into the image's dead space (white / orange alternating), a Helvetica title card with
tightened tracking over a 3-image strip on the open, and small boxed captions under the chin (said words white,
upcoming grey). Everything sits inside the Instagram Reels safe zone (hard rule, asserted below).
V1 the take (1.04 push, shifted down so the card clears the cap), audio untouched (music is already on it);
V2 image cards + title; V3 captions.
Usage: python3 build_yap.py a [b]   (builds into the CURRENT project, one timeline per take)"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
AE = os.path.abspath(os.path.join(HERE, "../.."))
sys.path.insert(0, os.path.join(AE, "engine"))
sys.path.insert(0, HERE)
from PIL import Image, ImageFont
import fusion
import readable
from fusion import Comp, A, P, L, q
from resolve import connect, find_clip
from beats import TAKES

W, H, FPS = 1080, 1920, 30
fusion.W, fusion.H = W, H
fusion.TEXT_DIV = 1450.0 * 1080 / 1920
CARDS = os.path.join(AE, "jobs/yap-assets/cards")
JOB = os.path.join(AE, "jobs")
MTP_DRB = "/Volumes/Extreme SSD/personal brand directory/asssets/Motiontext-pro-v1/davinci-resolve-version21+/MotionText Pro V1.drb"
FONT = "Helvetica"
FONT_FILE, BOLD = "/System/Library/Fonts/Helvetica.ttc", 1
TRACK = 0.94                                   # title/keyword letter spacing, a touch tighter than default

# ---- palette: teal / orange, a hint of olive, kept basic -------------------------------------------------------
WHITE = (1, 1, 1)
ORANGE = (0.95, 0.45, 0.13)                  # a touch redder (Eoin 23 Oct)
TEAL = (0.12, 0.62, 0.62)
OLIVE_INK = (0.10, 0.11, 0.07)                 # caption box: near-black with an olive cast
GREY = (0.62, 0.62, 0.60)

# ---- Instagram Reels safe zone (1080x1920), HARD RULE ----------------------------------------------------------
SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT = 250, 1440, 60
SAFE_RIGHT_TOP, SAFE_RIGHT_LOW = 1020, 940      # the like/comment rail sits on the right below ~y 1000


def assert_safe(name, x0, y0, x1, y1):
    right = SAFE_RIGHT_TOP if y1 <= 1000 else SAFE_RIGHT_LOW
    if x0 < SAFE_LEFT or y0 < SAFE_TOP or y1 > SAFE_BOTTOM or x1 > right:
        sys.exit(f"IG safe zone broken by {name}: ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")


# ---- layout ----------------------------------------------------------------------------------------------------
CARD_X0, CARD_X1, CARD_Y0, CARD_Y1 = 70, 1010, 252, 604     # image card: above the head
CW, CH = CARD_X1 - CARD_X0, CARD_Y1 - CARD_Y0
CX, CY = (CARD_X0 + CARD_X1) / 2, (CARD_Y0 + CARD_Y1) / 2
CAP_Y, CAP_PX, CAP_H = 646, 48, 60                           # captions just under the image card
AROLL_ZOOM = 1.04
AROLL_TILT = -round((AROLL_ZOOM - 1) * H / 2)                # push down so the top edge stays at 0 (no black bar)
assert_safe("image card", CARD_X0, CARD_Y0, CARD_X1, CARD_Y1)
assert_safe("caption band", 140, CAP_Y - CAP_H / 2, 940, CAP_Y + CAP_H / 2)
assert CAP_Y - CAP_H / 2 > CARD_Y1, "captions must sit below the card, never under it"


def measure(s, px):
    f = ImageFont.truetype(FONT_FILE, 100, index=BOLD)
    return max(f.getlength(l) for l in s.split("\n")) * px / 100


def fit_px(s, width, cap):
    return min(cap, 100 * width / measure(s, 100))


# ---- words -----------------------------------------------------------------------------------------------------
def words(take):
    W_ = json.load(open(os.path.join(JOB, f"yap-{take}", "words.json")))
    return [{"w": w["w"].strip(), "s": w["start"], "e": w["end"]} for w in W_ if w["w"].strip()]


def norm(s):
    return re.sub(r"[^\w']", "", s.lower())


def cue(W_, word, occ):
    hits = [w for w in W_ if norm(w["w"]) == word]
    if len(hits) < occ:
        sys.exit(f"cue word not found: {word} #{occ}")
    return max(0.0, hits[occ - 1]["s"] - 1 / FPS)


def chunks(W_):
    """2 to 4 words: break on punctuation or a pause once there are 2, never past 4 words / 26 characters"""
    out, cur = [], []
    for i, w in enumerate(W_):
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        nxt = W_[i + 1] if i + 1 < len(W_) else None
        if not nxt or len(cur) >= 4 or len(txt + " " + nxt["w"]) > 26:
            out.append(cur); cur = []
        elif len(cur) >= 2 and (re.search(r"[.,?!]$", w["w"]) or nxt["s"] - w["e"] > 0.35):
            out.append(cur); cur = []
    fixed = []
    for ch in out:
        if len(ch) == 1 and fixed and len(fixed[-1]) < 4 and ch[0]["s"] - fixed[-1][-1]["e"] < 0.6:
            fixed[-1] = fixed[-1] + ch
        else:
            fixed.append(ch)
    return fixed


def cap_text(ch):
    return " ".join(x["w"] for x in ch).rstrip(".")


# ---- comps -----------------------------------------------------------------------------------------------------
def loader(c, name, path):
    c.tool(name, "Loader", {})
    c.tools[-1] = (name, c.tools[-1][1].replace("Inputs = {", "Clips = {\n\t\t\t\tClip {\n\t\t\t\t\tFilename = " + q(path) +
                   ",\n\t\t\t\t\tFormatID = \"JpegFormat\",\n\t\t\t\t\tLength = 1,\n\t\t\t\t\tLoop = 1,\n\t\t\t\t}\n\t\t\t},\n\t\t\tInputs = {", 1))
    return name


def masked(c, merge_name, mask):
    for k, (n, t) in enumerate(c.tools):
        if n == merge_name:
            c.tools[k] = (n, t.replace("\n\t\t\t},", ",\n\t\t\t\tEffectMask = Input { SourceOp = " + q(mask) + ", Source = \"Mask\", },\n\t\t\t},", 1))


def put_image(c, bg, key, cx, cy, cw, ch, gain=1.0):
    """image covers a cw x ch rect centred on (cx, cy), square corners, natural colour"""
    path = os.path.join(CARDS, key + ".jpg")
    pw, ph = Image.open(path).size
    n = re.sub(r"\W", "", key) + str(len(c.tools))
    ld = loader(c, "L" + n, path)
    g = c.tool("G" + n, "BrightnessContrast", {"Input": L(ld), "Contrast": 0.06, "Gain": gain})
    m = c.rect("M" + n, cx, cy, cw, ch)
    mg = c.merge("C" + n, bg, g, center=P(cx, cy), size=max(cw / pw, ch / ph))
    masked(c, mg, m)
    return mg


def text(c, bg, name, s, x, y, size, rgb=WHITE, spacing=TRACK, line=0.022, end=None, alpha=1.0):
    """Helvetica Bold with a thin dark outline so it holds on any image"""
    tx = c.text(name, s, x, y, size, rgb=rgb, a=alpha, style="Bold", font=FONT, spacing=spacing, end=end)
    if line:
        extra = (f"Enabled2 = Input {{ Value = 1, }},\n\t\t\t\tThickness2 = Input {{ Value = {line}, }},\n\t\t\t\t"
                 f"Red2 = Input {{ Value = 0.04, }},\n\t\t\t\tGreen2 = Input {{ Value = 0.05, }},\n\t\t\t\tBlue2 = Input {{ Value = 0.03, }},\n\t\t\t\t"
                 f"Alpha2 = Input {{ Value = {0.85 * alpha}, }},\n\t\t\t\t")
        for k, (n, t) in enumerate(c.tools):
            if n == tx:
                c.tools[k] = (n, t.replace("Inputs = {\n\t\t\t\t", "Inputs = {\n\t\t\t\t" + extra, 1))
    return c.merge(name + "M", bg, tx)


POS = {"L": (0.25, 0.5), "R": (0.75, 0.5), "T": (0.5, 0.2), "B": (0.5, 0.8), "C": (0.5, 0.5),
       "TL": (0.27, 0.24), "TR": (0.73, 0.24), "BL": (0.27, 0.76), "BR": (0.73, 0.76)}


def keyword(c, bg, s, pos, rgb):
    fx, fy = POS[pos]
    room = 0.44 * CW if pos in ("L", "R", "TL", "TR", "BL", "BR") else 0.86 * CW
    size = fit_px(s, room, 88)
    x, y = CARD_X0 + fx * CW, CARD_Y0 + fy * CH
    lines = s.count("\n") + 1
    half_h = size * 0.62 * lines
    y = min(max(y, CARD_Y0 + 14 + half_h), CARD_Y1 - 14 - half_h)      # never spill off the card
    w = measure(s, size)
    x = min(max(x, CARD_X0 + 24 + w / 2), CARD_X1 - 24 - w / 2)
    assert_safe("keyword " + s, x - w / 2, y - half_h, x + w / 2, y + half_h)
    return text(c, bg, "Key", s, x, y, size, rgb=rgb)


def beat_comp(n, key, kw=None, pos=None, rgb=None):
    """image only: Eoin 23 Oct, no words on the images, the captions carry what he says"""
    c = Comp(n)
    out = put_image(c, c.canvas(), "library" if key == "end" else key, CX, CY, CW, CH)
    return c.text_out(out)


HALO_A, HALO_LINE, HALO_BLUR = 0.85, 0.14, 1.4      # tuned against engine/readable.py on his lightest wall


def halo(c, bg, name, s, x, y, size, spacing, style="Bold", a=HALO_A, line=HALO_LINE, blur=HALO_BLUR):
    """soft dark halo behind text so it reads on any background (HARD RULE: readable everywhere)"""
    tx = c.text(name, s, x, y, size, rgb=(0, 0, 0), a=a, style=style, font=FONT, spacing=spacing)
    extra = (f"Enabled2 = Input {{ Value = 1, }},\n\t\t\t\tThickness2 = Input {{ Value = {line}, }},\n\t\t\t\t"
             f"Red2 = Input {{ Value = 0, }},\n\t\t\t\tGreen2 = Input {{ Value = 0, }},\n\t\t\t\tBlue2 = Input {{ Value = 0, }},\n\t\t\t\t"
             f"Alpha2 = Input {{ Value = {a}, }},\n\t\t\t\t")
    for k, (n, t) in enumerate(c.tools):
        if n == tx:
            c.tools[k] = (n, t.replace("Inputs = {\n\t\t\t\t", "Inputs = {\n\t\t\t\t" + extra, 1))
    return c.merge(name + "M", bg, c.tool(name + "B", "Blur", {"Input": L(tx), "XBlurSize": blur}))


def soft_text(c, bg, name, s, x, y, size, rgb=WHITE, spacing=0.9, blur=0.3, glow=0.18, sh_a=0.55, sh_blur=None):
    """the viral soft Helvetica: slight blur on the letters, a soft glow bleeding out, a faint blurred shadow under it"""
    sh = c.text(name + "Sh", s, x, y + size * 0.05, size, rgb=(0, 0, 0), a=sh_a, style="Bold", font=FONT, spacing=spacing)
    shb = c.tool(name + "ShB", "Blur", {"Input": L(sh), "XBlurSize": sh_blur or blur * 6})
    tx = c.text(name, s, x, y, size, rgb=rgb, style="Bold", font=FONT, spacing=spacing)
    tb = c.tool(name + "B", "Blur", {"Input": L(tx), "XBlurSize": blur})
    tg = c.tool(name + "G", "SoftGlow", {"Input": L(tb), "Gain": glow, "XGlowSize": 3})
    out = c.merge(name + "ShM", bg, shb)
    return c.merge(name + "M", out, tg)


def title_geo(title, sub):
    gap, y0, y1 = 10, CARD_Y0, 452
    size = fit_px(title, 0.94 * CW, 118) / 0.93  # measured at normal tracking; 0.9 spacing pulls it in ~7%
    ty = y1 + 4
    ssz = fit_px(sub, 0.8 * CW, 44)
    return {"gap": gap, "y0": y0, "y1": y1, "w": (CW - 2 * gap) / 3, "size": size, "ty": ty, "ssz": ssz,
            "sy": ty + size * 0.5 + ssz * 0.9, "tw": measure(title, size * 0.93), "sw": measure(sub, ssz)}


def title_comp(n, title, sub, keys):
    """3-image strip, big Helvetica title overlapping its bottom edge, orange subtitle under it"""
    c = Comp(n)
    out = c.canvas()
    g = title_geo(title, sub)
    gap, y0, y1, w, size, ty, ssz, sy = (g[k] for k in ("gap", "y0", "y1", "w", "size", "ty", "ssz", "sy"))
    for i, k in enumerate(keys):
        out = put_image(c, out, k, CARD_X0 + w / 2 + i * (w + gap), (y0 + y1) / 2, w, y1 - y0)
    out = soft_text(c, out, "Title", title, CX, ty, size, rgb=WHITE)
    assert_safe("title", CX - measure(title, size) / 2, ty - size * 0.6, CX + measure(title, size) / 2, ty + size * 0.6)
    assert sy + ssz * 0.6 < CAP_Y - CAP_H / 2, "title subtitle would hit the captions"
    out = halo(c, out, "SubHalo", sub, CX, sy, ssz, 0.98, a=1.0, line=0.24, blur=1.0)  # orange is mid-bright: darker, tighter halo
    out = soft_text(c, out, "Sub", sub, CX, sy, ssz, rgb=ORANGE, spacing=0.98, glow=0.08)  # same softness as the title; title tracking ran the small words together
    return c.text_out(out)


def caption_comp(n, s, reveal):
    """Helvetica Bold, white, thin black outline, just under the image (plain: grey unsaid words vanished on his wall)"""
    c = Comp(n)
    out = c.canvas()
    w = measure(s, CAP_PX)
    assert_safe("caption " + s, CX - w / 2, CAP_Y - CAP_H / 2, CX + w / 2, CAP_Y + CAP_H / 2)

    def endf(f):
        v = 0.0
        for fr, e in reveal:
            if f >= fr:
                v = e
        return v
    out = halo(c, out, "CapHalo", s, CX, CAP_Y, CAP_PX, 1.0)
    out = text(c, out, "Cap", s, CX, CAP_Y, CAP_PX, rgb=WHITE, spacing=1.0, line=0.03)
    return c.text_out(out)


def cap_plan(W_, total):
    """[(start, end, words, text)] for every caption"""
    C, out = chunks(W_), []
    for j, ch in enumerate(C):
        a = max(0.0, ch[0]["s"] - 1 / FPS)
        nxt = C[j + 1][0]["s"] - 1 / FPS if j + 1 < len(C) else min(total, ch[-1]["e"] + 0.5)
        b = nxt if nxt - ch[-1]["e"] < 0.6 else ch[-1]["e"] + 0.25
        if round(b * FPS) - round(a * FPS) >= 3:
            out.append((a, b, ch, cap_text(ch)))
    return out


# ---- readability (HARD RULE: engine/readable.py) ---------------------------------------------------------------
def pre_check(take):
    """before Resolve is touched: every strip image must be dark enough where the white title sits on it"""
    title, sub, keys = TAKES[take]["title"]
    g = title_geo(title, sub)
    top = max(g["y0"], g["ty"] - g["size"] * 0.5)          # glyph band of the title inside the strip
    fy0 = (top - g["y0"]) / (g["y1"] - g["y0"])
    bad = []
    for i, k in enumerate(keys):
        cell_x0 = CARD_X0 + i * (g["w"] + g["gap"])
        tx0, tx1 = CX - g["tw"] / 2, CX + g["tw"] / 2       # only the part of the cell the title actually covers
        fx0, fx1 = max(0, (tx0 - cell_x0) / g["w"]), min(1, (tx1 - cell_x0) / g["w"])
        if fx1 <= fx0:
            continue
        ok, r, bl = readable.zone_ok(os.path.join(CARDS, k + ".jpg"), WHITE, g["w"], g["y1"] - g["y0"], fy0, 1.0, fx0, fx1)
        if not ok:
            bad.append(f"{k} (under the title: brightness {bl:.2f}, contrast {r:.2f})")
    if bad:
        sys.exit(f"take {take}: title unreadable over " + ", ".join(bad) + ": swap the image")


def write_manifest(take, timeline):
    T = TAKES[take]
    title, sub, _ = T["title"]
    g = title_geo(title, sub)
    beats, W_, total = plan(take)
    t_end = beats[1][0]
    items = [{"t": round(t_end / 2, 2), "label": "title " + title, "rgb": list(WHITE),
              "box": [CX - g["tw"] / 2 - 12, g["ty"] - g["size"] * 0.6, CX + g["tw"] / 2 + 12, g["ty"] + g["size"] * 0.6]},
             {"t": round(t_end / 2, 2), "label": "subtitle " + sub, "rgb": list(ORANGE),
              "box": [CX - g["sw"] / 2 - 12, g["sy"] - g["ssz"] * 0.75, CX + g["sw"] / 2 + 12, g["sy"] + g["ssz"] * 0.75]}]
    for a, b, ch, s in cap_plan(W_, total):
        w = measure(s, CAP_PX)
        items.append({"t": round((a + b) / 2, 2), "label": "cap " + s, "rgb": list(WHITE),
                      "box": [CX - w / 2 - 12, CAP_Y - CAP_H / 2, CX + w / 2 + 12, CAP_Y + CAP_H / 2]})
    path = os.path.join(JOB, f"yap-{take}", "text_manifest.json")
    json.dump({"timeline": timeline, "items": items}, open(path, "w"), indent=0)
    return path


# ---- Resolve ---------------------------------------------------------------------------------------------------
def place(mp, t, carrier, rec, d, track):
    # the MTP carrier is a 24fps title: on the 30fps timeline a span of n source frames lands as n * 30/24
    cfps = float(carrier.GetClipProperty("FPS") or FPS) or FPS
    est = d * cfps / FPS
    best = None
    for span in sorted({max(1, round(est) + k) for k in (0, -1, 1, -2, 2)}, key=lambda s: abs(s - est)):
        res = mp.AppendToTimeline([{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": span, "trackIndex": track, "recordFrame": rec}])
        item = res[0] if res else None
        if not item:
            continue
        got = item.GetDuration()
        if got == d:
            return item
        t.DeleteClips([item])
        if got < d and (best is None or got > best[1]):
            best = (span, got)
    if best:  # no exact hit: longest span that still fits
        res = mp.AppendToTimeline([{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": best[0], "trackIndex": track, "recordFrame": rec}])
        return res[0] if res else None
    return None


def check_comp(src, path):
    """refuse any comp that could hang Fusion on import: repeated node names (a merge feeding itself froze
    Resolve twice on 23 Oct), links to nodes that don't exist, or a node linking to itself"""
    names = re.findall(r"^\t\t(\w+) = ", src, re.M)
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        sys.exit(f"duplicate Fusion node names {dup} in {path}")
    blocks = re.split(r"^\t\t(?=\w+ = )", src, flags=re.M)
    for b in blocks[1:]:
        me = b.split(" =", 1)[0]
        for ref in re.findall(r'SourceOp = "(\w+)"', b):
            if ref == me or ref not in names:
                sys.exit(f"bad Fusion link {me} -> {ref} in {path}")


def attach(item, src, path):
    check_comp(src, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(src)
    item.ImportFusionComp(path)
    names = item.GetFusionCompNameList() or []
    if len(names) > 1:
        item.LoadFusionCompByName(names[-1])
        for nm in names[:-1]:
            item.DeleteFusionCompByName(nm)


def plan(take):
    """beat list with absolute times: [(start, end, kind, payload)]"""
    T = TAKES[take]
    W_ = words(take)
    total = json.load(open(os.path.join(JOB, f"yap-{take}", "meta.json")))["dur"]
    starts = [cue(W_, b[0], b[1]) for b in T["beats"]]
    for i in range(1, len(starts)):
        if starts[i] <= starts[i - 1]:
            sys.exit(f"beats out of order at {T['beats'][i]}")
    out = [(0.0, starts[0], "title", T["title"])]
    ki = 0
    for i, b in enumerate(T["beats"]):
        rgb = None
        if b[3]:
            rgb = WHITE if ki % 2 == 0 else ORANGE
            ki += 1
        out.append((starts[i], starts[i + 1] if i + 1 < len(starts) else total, "beat", (b[2], b[3], b[4], rgb)))
    return out, W_, total


def build(take, p, mp, carrier):
    T = TAKES[take]
    beats, W_, total = plan(take)
    root = mp.GetRootFolder()
    sub = lambda nm: next((f for f in root.GetSubFolderList() or [] if f.GetName() == nm), None) or mp.AddSubFolder(root, nm)
    mp.SetCurrentFolder(sub("aroll"))
    path = os.path.expanduser(f"~/Downloads/{T['src']}.MP4")
    clip = find_clip(root, os.path.basename(path)) or mp.ImportMedia([path])[0]
    frames = int(float(clip.GetClipProperty("Frames")))
    mp.SetCurrentFolder(sub("timelines"))
    taken = {p.GetTimelineByIndex(i).GetName() for i in range(1, p.GetTimelineCount() + 1)}
    v = 1
    while (name := f"Yap {take} v{v} · {T['name']}") in taken or (v == 1 and f"Yap {take} · {T['name']}" in taken):
        v += 1  # never delete or overwrite a timeline from the script (deleting crashes Resolve): new version instead
    t = mp.CreateEmptyTimeline(name)
    if not t:
        sys.exit(f"could not create timeline {name}")
    p.SetCurrentTimeline(t)
    t0 = t.GetStartFrame()
    v = mp.AppendToTimeline([{"mediaPoolItem": clip, "startFrame": 0, "endFrame": frames, "trackIndex": 1, "recordFrame": t0, "mediaType": 1}])
    if v:
        v[0].SetProperty({"ZoomX": AROLL_ZOOM, "ZoomY": AROLL_ZOOM, "Tilt": AROLL_TILT})
    mp.AppendToTimeline([{"mediaPoolItem": clip, "startFrame": 0, "endFrame": frames, "trackIndex": 1, "recordFrame": t0, "mediaType": 2}])
    for _ in range(2):
        t.AddTrack("video")
    t.SetTrackName("video", 2, "images")
    t.SetTrackName("video", 3, "captions")
    jd = os.path.join(JOB, f"yap-{take}", "comps")
    rep = {"images": 0, "captions": 0, "fail": []}
    cursor = t0  # chain cards to the previous card's real end: no gap frames between beats
    for i, (a, b, kind, pl) in enumerate(beats):
        d = t0 + round(b * FPS) - cursor
        it = place(mp, t, carrier, cursor, d, 2)
        if not it:
            rep["fail"].append(f"beat {i}"); continue
        cursor = it.GetEnd()
        print(f"beat {i} {pl[0]} {d}f", flush=True)
        n = it.GetDuration()
        src = title_comp(n, *pl) if kind == "title" else beat_comp(n, *pl)
        attach(it, src, f"{jd}/beat_{i:02d}.comp")
        it.SetClipColor("Orange" if kind == "title" else "Teal")
        rep["images"] += 1
    for j, (a, b, ch, s) in enumerate(cap_plan(W_, total)):
        fa, d = round(a * FPS), round(b * FPS) - round(a * FPS)
        reveal, acc = [], 0
        for w in ch:
            acc += len(w["w"]) + 1
            reveal.append((max(0, round((w["s"] - a) * FPS)), min(1.0, acc / len(s))))
        it = place(mp, t, carrier, t0 + fa, d, 3)
        if not it:
            rep["fail"].append(f"cap {j}"); continue
        attach(it, caption_comp(it.GetDuration(), s, reveal), f"{jd}/cap_{j:03d}.comp")
        print(f"cap {j} {s}", flush=True)
        rep["captions"] += 1
    rep["timeline"] = name
    return rep


def main(takes):
    for tk in takes:
        pre_check(tk)
    r = connect(); pm = r.GetProjectManager(); p = pm.GetCurrentProject()
    if p.GetTimelineCount() == 0:
        p.SetSetting("timelineFrameRate", str(FPS))
        p.SetSetting("timelineResolutionWidth", str(W))
        p.SetSetting("timelineResolutionHeight", str(H))
    mp = p.GetMediaPool()
    carrier = find_clip(mp.GetRootFolder(), "Smooth Word Up")
    if not carrier:
        mp.ImportFolderFromFile(MTP_DRB)
        carrier = find_clip(mp.GetRootFolder(), "Smooth Word Up")
    for tk in takes:
        rep = build(tk, p, mp, carrier)
        rep["manifest"] = write_manifest(tk, rep["timeline"])
        print(json.dumps(rep))
    pm.SaveProject()


if __name__ == "__main__":
    if sys.argv[1:2] == ["plan"]:  # dry run: print the beat map, touch nothing
        for tk in sys.argv[2:] or ["a", "b"]:
            bs, _, _ = plan(tk)
            for a, b, kind, pl in bs:
                print(f"{tk} {a:6.2f}-{b:6.2f} {kind:5s} {pl[0] if kind == 'beat' else pl[0]!s:16s} {(pl[1] or '') if kind == 'beat' else pl[1]}".replace("\n", " / "))
        sys.exit()
    main(sys.argv[1:] or ["a", "b"])
