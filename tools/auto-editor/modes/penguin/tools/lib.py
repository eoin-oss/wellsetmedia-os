"""Eoin "the polymaths win" in the penguin system (research/penguin-edit-refs/BREAKDOWN.md), 16:9, native Resolve.
STATIC build for Gate 2: every graphic sits at its settled end state, no keyframes. Animation comes after approval.
Builds into the OPEN project (Eoin's fresh "penguine dit").
  V1 A-roll pieces (C8580), alternating 1.00 / 1.12 punch-ins. Payoff behind the head on the last line.
  V2 full-frame cutaways (payoff word behind him inside the item's comp) + canvas carriers.
  V3 inset (opener video-in-video) and list cards.
  V4 text carriers (captions, leads, canvas words).
  A1 Eoin. A2 caption clicks. A3 whooshes + hits.
Usage: python3 build.py | python3 build.py stills"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
AE = os.path.abspath(os.path.join(HERE, "../.."))
sys.path.insert(0, os.path.join(AE, "engine"))
sys.path.insert(0, os.path.join(AE, "jobs/kyle-lagging"))
import fusion
from fusion import Comp, P
from resolve import connect, find_clip
from build16 import attach, place, comp_of, strobe, MTP_DRB

FPS = 30000 / 1001
TW, TH = 1920, 1080
TL_NAME = "Eoin · polymaths win v{}"
G = "/Volumes/Extreme SSD/glasgow november"
M, MB = f"{G}/mine", f"{G}/mine/b roll"
PB = "/Volumes/Extreme SSD/personal brand directory"
SFXD = "/Volumes/Extreme SSD/editiing assets"
SRC = {
    "A": f"{M}/C8580_00470079.mov",
    "C8628": f"{M}/C8628_00569011.mov", "DL1": f"{G}/day3/d3g/Timeline 1_00347394.mov",
    "DL2": f"{G}/day3/d3g/Timeline 1_00345429.mov", "SHOOT": f"{PB}/broll/working/shooting/A743194.MP4",
    "C8227": f"{MB}/C8227_02422182.mov", "LIFT": f"{MB}/Timeline 1_00281259.mov", "C8212": f"{M}/C8212_02284452.mov",
    "C8583": f"{MB}/C8583_00479499.mov", "C8581": f"{MB}/C8581_00476304.mov", "C8620": f"{MB}/C8620_00551579.mov",
    "C7076": f"{PB}/broll/seaside/C7076_00918477.mov", "C8627": f"{MB}/C8627_00567793.mov",
    "C4432": f"{PB}/trips/NYC/12/graded/C4432_02228361.mov", "C4176": f"{PB}/trips/NYC/8/graded/C4176_02122986.mov",
    "C4198": f"{PB}/trips/NYC/8/graded/C4198_02126631.mov", "STREET": f"{MB}/Timeline 1_00340089.mov",
    "C4431": f"{PB}/trips/NYC/12/graded/C4431_02228211.mov", "C8612": f"{M}/C8612_00526689.mov",
    "C4411": f"{PB}/trips/NYC/12/graded/C4411_02222076.mov",
    "C3480": f"{PB}/broll/clientfootage/highlight reel/C3480_01497519.mov",
}
SFX = {"click": f"{SFXD}/5. Sound FX/Vintage SFX/Click.wav", "whoosh": f"{SFXD}/Wooshes/Fast-woosh.wav",
       "hit": f"{SFXD}/5. Sound FX/Invention SFX/IMPACT/Impact 5.wav"}
SFX_DB = {"click": -12.0, "whoosh": -19.0, "hit": -14.0}

INK = (0.10, 0.10, 0.10)
WHITE = (1, 1, 1)
CANVAS = (0.957, 0.949, 0.933)   # off-white #f4f2ee
HN = "Helvetica Neue"

# A-roll pieces in order: (name, raw in, raw out, punch-in zoom)
SEGS = [("hook", 142.62, 147.15, 1.00), ("p2a", 8.20, 9.56, 1.00), ("p2b", 9.96, 13.30, 1.00),
        ("p3", 13.40, 16.75, 1.12), ("think", 23.45, 25.65, 1.00), ("l1", 27.05, 28.80, 1.00), ("l2", 29.30, 30.40, 1.00),
        ("l3", 34.40, 37.55, 1.00), ("l4", 43.80, 45.85, 1.00), ("p5", 70.45, 74.95, 1.12), ("p6", 76.12, 80.60, 1.00),
        ("p7a", 105.60, 107.40, 1.12), ("p7b", 114.80, 118.15, 1.12), ("p8a", 173.18, 176.40, 1.00),
        ("p8b", 178.80, 181.65, 1.00), ("p9", 201.50, 205.30, 1.15)]
WORDS = json.load(open(os.path.join(HERE, "words_islands.json")))
W_ALL = sorted([w for v in WORDS.values() for w in v], key=lambda w: w[1])

# opener over the hook (seconds into the hook piece): inset first, then the rapid "doing things" cuts, then WIN
OPEN_INSET = ("C8628", 30.0, 0.0, 0.90)                       # clip, clip in, from, to
OPEN_RAPID = [("DL1", 3.0), ("SHOOT", 5.0), ("C8227", 20.0), ("LIFT", 0.6), ("C8212", 8.0), ("C8583", 2.0),
              ("C8581", 30.0), ("DL2", 25.0)]
RAPID_FROM, RAPID_TO = 0.90, 3.30
# cutaways: (seg, raw from, raw to, clip, clip in, payoff or None)
# payoff = (WORD, lead, tail, subject x-range (frac) for the cutout | None = no cutout, colour)
CUTS = [("hook", 146.00, 147.15, "C8620", 4.0, ("WIN", "ARE GOING TO", None, (0.30, 0.62), WHITE)),
        ("p2b", 12.00, 13.30, "C7076", 6.0, ("IRRELEVANT", "SEEMINGLY", None, (0.38, 0.62), WHITE)),
        ("p3", 14.55, 16.75, "C8627", 0.4, ("CLICKS", "UNTIL ONE DAY IT ALL", None, (0.22, 0.52), WHITE)),
        ("p5", 73.05, 74.95, "LIFT", 0.4, None),
        ("p6", 77.80, 80.60, "C8612", 12.0, ("PERCEPTION", "IN CONTROL OF THE", None, (0.38, 0.62), WHITE)),
        ("p7b", 116.25, 118.15, "C8581", 20.0, None),
        ("p8a", 174.70, 176.40, "C4411", 10.0, ("LAYERS", "PEEL BACK THE", "OF THE ONION", (0.48, 0.85), WHITE)),
        ("p8b", 180.55, 181.65, "C3480", 40.0, ("CORE", "AT THEIR", None, None, WHITE))]
# canvas list: (seg, word raw start, card clip, clip in, word on canvas)
CARDS = [("l1", 27.05, "C8227", 25.0, "PSYCHOLOGY"), ("l1", 28.10, "C4432", 5.0, "PHYSICS"),
         ("l2", 29.30, "C8583", 3.0, "NEUROSCIENCE"), ("l3", 34.40, "C4176", 2.0, "HUMAN BEHAVIOUR"),
         ("l3", 36.65, "C4198", 1.0, "INFLUENCE"), ("l4", 43.80, "STREET", 2.0, "SOCIOLOGY"),
         ("l4", 44.85, "C4431", 1.0, "MATHEMATICS")]
CARD_ANGLES = [-4, 3, -2, 4, -3, 2, -4]
# last line: payoff behind the head on the A-roll
END_PAYOFF = ("p9", 202.65, "SCROLLING", "STOP FUCKING", "GO READ A BOOK", INK)
STROBE_INTO = "p2a"        # invert strobe on the hand-off into this piece
BLOWOUT_INTO = "p5"        # white blow-out into this piece
CAP_POS = (0.20, 0.24)     # A-roll one-word captions: empty wall, upper left
CAP_PX = 46


class _Sym(str):
    """a frame number Fusion resolves live: comp.RenderStart moves when Resolve re-bases a clip's comp (it did on a
    4K clip after a project reopen and froze every animation), so expressions must never bake it in (12 Nov)"""
    def __add__(self, o): return _Sym(f"({self}+{o})")
    __radd__ = __add__
    def __sub__(self, o): return _Sym(f"({self}-{o})")
    def __rsub__(self, o): return _Sym(f"({o}-{self})")


RS = _Sym("comp.RenderStart")


def fr(s):
    return int(round(s * FPS))


def plan():
    rec, out = 0, {}
    for nm, a, b, z in SEGS:
        n = fr(b) - fr(a)
        out[nm] = {"name": nm, "a": a, "b": b, "z": z, "rec": rec, "n": n}
        rec += n
    return out, rec


def t_of(pc, s):
    return pc["rec"] + fr(s) - fr(pc["a"])


def hn_width(s, px):
    from PIL import ImageFont
    idx = next(i for i in range(20) if ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 10, index=i).getname()[1] == "Bold")
    f = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 100, index=idx)
    return f.getlength(s) * px / 100


def setup():
    fusion.W, fusion.H, fusion.TEXT_DIV = TW, TH, 1450.0


def text_comp(n, items, halo=False, typeon=False):
    """static text overlay: items = [(text, x px, y px, px, rgb)]; halo = soft dark glow under white words"""
    from fusion import L
    setup()
    c = Comp(n)
    out = c.canvas()
    for i, (s, x, y, px, rgb) in enumerate(items):
        if halo:
            sh = c.text(f"T{i}H", s, x, y, px, rgb=(0, 0, 0), font=HN, style="Bold", spacing=0.97)
            bl = c.tool(f"T{i}HB", "Blur", {"Input": L(sh), "XBlurSize": max(6.0, px / 10)})
            out = c.merge(f"T{i}HM", out, bl, blend=0.8)
        end = None
        if typeon:
            from fusion import A
            end = A(lambda f, k=len(s): min(max((f + 1) / k, 0), 1))
        out = c.merge(f"T{i}M", out, c.text(f"T{i}", s, x, y, px, rgb=rgb, font=HN, style="Bold", spacing=0.97, end=end))
    return c.text_out(out)


def solid_comp(n, rgb):
    setup()
    c = Comp(n)
    return c.text_out(c.solid("Fill", rgb))


_FR = {}


def frame_at(key, sec):
    import subprocess, io
    from PIL import Image
    k = (key, round(sec, 2))
    if k not in _FR:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(sec), "-i", SRC[key], "-frames:v", "1", "-vf", f"scale={TW}:{TH}",
                              "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        _FR[k] = Image.open(io.BytesIO(raw)).convert("RGB")
    return _FR[k]


def lum(rgb):
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2])


REPORT = []


def pick(key, sec, box, label):
    """the white-to-black rule: measure the plate where the text lands, use whichever of white/ink reads better"""
    im = frame_at(key, sec).crop(tuple(int(v) for v in box)).resize((32, 8))
    px_ = list(im.getdata())
    L = sorted(lum(tuple(c / 255 for c in p)) for p in px_)
    lo, hi = L[len(L) // 10], L[9 * len(L) // 10]
    c = 1.05 / (hi + 0.05)                  # white vs the brightest 10% behind it (Eoin 11 Nov: white only, never mixed)
    REPORT.append([label, "white", round(c, 2), "halo" if c < 3.0 else ""])
    return WHITE


BIG = {}          # word -> fraction of frame width (Eoin: LAYERS nearly full width)


def payoff_geo(word, lead, xr):
    frac = BIG.get(word)
    px = (frac * TW / max(hn_width(word, 1), 1e-6)) if frac else min(300, 0.72 * TW / max(hn_width(word, 1), 1e-6))
    w = hn_width(word, px)
    cx = TW / 2 if (xr is None or frac) else min(max((xr[0] + xr[1]) / 2 * TW, 0.08 * TW + w / 2), 0.92 * TW - w / 2)
    cy = 0.42 * TH
    cap = px * 0.714
    return {"px": px, "w": w, "x": cx, "y": cy, "top": cy - cap / 2, "bot": cy + cap / 2}


def payoff_into(it, word, lead, tail, xr, rgb, depth=(0.28, 0.31), key=None, sec=0.0, word_f=0, tail_f=0, push=True,
                cut="depth", push_curve="ease"):
    """payoff inside an item's comp, animated INTO the approved still:
    plate slow push 1.00->1.04 over the clip; big word per-letter ghost reveal (8f ramp, 2f stagger, glide from the right)
    starting 4f before it's spoken; subject cut out on top (DepthMap gated to xr); lead typed on from the cut, tail typed
    on at its word. word_f / tail_f = frames from the item's start."""
    c = comp_of(it)
    mi0, mo = c.FindTool("MediaIn1"), c.FindTool("MediaOut1")
    g0 = RS
    dur = it.GetDuration()
    g = payoff_geo(word, lead, xr)
    lpx = 40
    lx = max(g["x"] - g["w"] / 2 + hn_width(lead, lpx) / 2, 0.05 * TW + hn_width(lead, lpx) / 2)
    ly = g["top"] - lpx * 0.9
    if key:
        rgb = pick(key, sec, (g["x"] - g["w"] / 2, g["top"], g["x"] + g["w"] / 2, g["bot"]), word)
        lrgb = pick(key, sec, (lx - hn_width(lead, lpx) / 2, ly - lpx * 0.4, lx + hn_width(lead, lpx) / 2, ly + lpx * 0.4), lead)
        trgb = pick(key, sec, (g["x"] + g["w"] / 2 - hn_width(tail, lpx), g["bot"] + lpx * 0.7, g["x"] + g["w"] / 2, g["bot"] + lpx * 1.5), tail) if tail else rgb
    else:
        lrgb = trgb = rgb
    c.Lock()
    res = (it.GetMediaPoolItem().GetClipProperty("Resolution") or "") if it.GetMediaPoolItem() else ""
    if res and res != f"{TW}x{TH}":            # 4K source: bring the comp to 1080 before text/cutout so sizes match
        rz = c.AddTool("BetterResize", -32768, -32768); rz.SetAttrs({"TOOLS_Name": "To1080"}); rz.Input = mi0.Output
        rz.SetInput("Width", TW); rz.SetInput("Height", TH)
        mi0 = rz
    if push:
        mi = c.AddTool("Transform", -32768, -32768); mi.SetAttrs({"TOOLS_Name": "Push"}); mi.Input = mi0.Output
        u = f"min(max((time-{g0})/{max(dur - 1, 1)},0),1)"
        mi.Size.SetExpression(f"1+0.12*{u}" if push_curve == "linear" else f"1+0.10*(1-(1-{u})^3)")
    else:
        mi = mi0

    def txt(nm, s, x, y, px, col):
        t = c.AddTool("TextPlus", -32768, -32768); t.SetAttrs({"TOOLS_Name": nm})
        t.SetInput("UseFrameFormatSettings", 0); t.SetInput("Width", TW); t.SetInput("Height", TH)
        t.SetInput("StyledText", s); t.SetInput("Font", HN); t.SetInput("Style", "Bold")
        t.SetInput("Size", px / 1450.0); t.SetInput("CharacterSpacing", 0.97)
        t.SetInput("Red1", col[0]); t.SetInput("Green1", col[1]); t.SetInput("Blue1", col[2])
        t.SetInput("Center", {1: x / TW, 2: 1 - y / TH})
        return t

    def weak(label):
        return any(r[0] == label and r[3] == "halo" for r in REPORT)

    def halo(nm, s, x, y, px, bg):
        """soft dark glow under white text on mixed plates (readable rule)"""
        sh = txt(nm + "H", s, x, y, px, (0, 0, 0))
        bl = c.AddTool("Blur", -32768, -32768); bl.SetAttrs({"TOOLS_Name": nm + "HB"}); bl.Input = sh.Output
        bl.SetInput("XBlurSize", max(6.0, px / 14))
        m = c.AddTool("Merge", -32768, -32768); m.SetAttrs({"TOOLS_Name": nm + "HM"})
        m.Background = bg.Output; m.Foreground = bl.Output; m.SetInput("Blend", 0.75)
        return m, sh

    def over(nm, bg, fg, mask=None):
        m = c.AddTool("Merge", -32768, -32768); m.SetAttrs({"TOOLS_Name": nm})
        m.Background = bg.Output; m.Foreground = fg.Output
        if mask is not None:
            m.EffectMask = mask.Mask
        return m

    a0 = g0 + max(0, word_f - 4)
    n = len(word)
    stag = 2
    done = a0 + (n - 1) * stag + 8
    src = mi
    if weak(word):
        src, _sh = halo("PO", word, g["x"], g["y"], g["px"], mi)
        src.Blend.SetExpression(f"0.75*min(max((time-{a0})/{done - a0},0),1)")
    for i in range(n):
        s0 = a0 + i * stag
        tl = txt(f"PO{i}", word, g["x"], g["y"], g["px"], rgb)
        tl.SetInput("Start", i / n); tl.SetInput("End", (i + 1) / n)
        e = f"(1-(1-min(max((time-({s0}))/10,0),1))^3)"
        x, y = g["x"] / TW, 1 - g["y"] / TH
        tl.Center.SetExpression(f"Point({x}+0.03*(1-{e}), {y})")
        m = over(f"PO{i}M", src, tl)
        m.Blend.SetExpression(f"iif(time<({s0}), 0, 0.08+0.92*min((time-({s0}))/8,1)^1.3)")
        src = m
    if xr is not None:
        dm = c.AddTool("DepthMap", -32768, -32768); dm.SetAttrs({"TOOLS_Name": "PODepth"}); dm.Input = mi.Output
        cu = c.AddTool("Custom", -32768, -32768); cu.SetAttrs({"TOOLS_Name": "POCut"})
        cu.Image1 = mi.Output; cu.Image2 = dm.Output
        cu.SetInput("NumberIn1", depth[0]); cu.SetInput("NumberIn2", depth[1])
        cu.SetInput("Intermediate1", "min(max((r2-n1)/(n2-n1),0),1)")
        if cut == "luma":                     # dark silhouette against a bright window: luminance key, no depth model
            cu.Image2 = mi.Output
            cu.SetInput("NumberIn1", 0.16); cu.SetInput("NumberIn2", 0.28)
            cu.SetInput("Intermediate1", "1-min(max(((0.3*r1+0.59*g1+0.11*b1)-n1)/(n2-n1),0),1)")
        for ch in ("Red", "Green", "Blue"):
            cu.SetInput(ch + "Expression", f"{ch[0].lower()}1*i1")
        cu.SetInput("AlphaExpression", "i1")
        rm = c.AddTool("RectangleMask", -32768, -32768); rm.SetAttrs({"TOOLS_Name": "POGate"})
        rm.SetInput("Center", {1: (xr[0] + xr[1]) / 2, 2: 0.5}); rm.SetInput("Width", xr[1] - xr[0])
        rm.SetInput("Height", 1.2); rm.SetInput("SoftEdge", 0.02)
        src = over("POCutM", src, cu, rm)
    def typeon(t_, f0, nch):
        t_.End.SetExpression(f"min(max((time-({f0})+1)/{nch},0),1)")

    if weak(lead):
        src, sh = halo("POLead", lead, lx, ly, lpx, src); typeon(sh, g0, len(lead))
    tl = txt("POLead", lead, lx, ly, lpx, lrgb); typeon(tl, g0, len(lead))
    src = over("POLeadM", src, tl)
    if tail:
        tx_ = min(g["x"] + g["w"] / 2 - hn_width(tail, lpx) / 2, 0.95 * TW - hn_width(tail, lpx) / 2)
        f1 = g0 + max(0, tail_f - 2)
        if weak(tail):
            src, sh = halo("POTail", tail, tx_, g["bot"] + lpx * 1.1, lpx, src); typeon(sh, f1, len(tail))
        tt = txt("POTail", tail, tx_, g["bot"] + lpx * 1.1, lpx, trgb); typeon(tt, f1, len(tail))
        src = over("POTailM", src, tt)
    mo.Input = src.Output
    c.Unlock()


def push_into(it):
    c = comp_of(it); mi, mo = c.FindTool("MediaIn1"), c.FindTool("MediaOut1")
    g0 = RS; d = it.GetDuration()
    c.Lock()
    x = c.AddTool("Transform", -32768, -32768); x.SetAttrs({"TOOLS_Name": "Push"}); x.Input = mi.Output
    x.Size.SetExpression(f"1+0.10*(1-(1-min(max((time-{g0})/{max(d - 1, 1)},0),1))^3)")
    mo.Input = x.Output
    c.Unlock()


def inset_zoom(it, end_size=0.46, frames=None):
    """video-in-a-video: full frame -> end_size across the WHOLE inset, slow, never fully stops (Eoin 11 Nov):
    65% ease-out + 35% linear, so it is still drifting on the last frame"""
    c = comp_of(it); mi, mo = c.FindTool("MediaIn1"), c.FindTool("MediaOut1")
    g0 = RS
    c.Lock()
    x = c.AddTool("Transform", -32768, -32768); x.SetAttrs({"TOOLS_Name": "ZoomOut"}); x.Input = mi.Output
    frames = frames or max(it.GetDuration() - 1, 1)
    u = f"min(max((time-{g0})/{frames},0),1)"
    x.Size.SetExpression(f"1-{1 - end_size}*(0.65*(1-(1-{u})^3)+0.35*{u})")
    mo.Input = x.Output
    c.Unlock()


def card_in(it, size=0.48, cx=0.31, cy=0.50, frames=7):
    """straight card (no tilt) slides up into place over 7f, ease-out"""
    c = comp_of(it); mi, mo = c.FindTool("MediaIn1"), c.FindTool("MediaOut1")
    g0 = RS
    c.Lock()
    x = c.AddTool("Transform", -32768, -32768); x.SetAttrs({"TOOLS_Name": "Card"}); x.Input = mi.Output
    x.SetInput("Size", size)
    e = f"(1-(1-min(max((time-{g0})/{frames},0),1))^3)"
    x.Center.SetExpression(f"Point({cx}, {cy}-0.06*(1-{e}))")
    mo.Input = x.Output
    c.Unlock()


def append(mp, item, src_s, n, track, rec, media=None):
    fps = float(item.GetClipProperty("FPS") or FPS) or FPS
    a = int(round(src_s * fps))
    b = a + max(1, int(round(n * fps / FPS)))
    d = {"mediaPoolItem": item, "startFrame": a, "endFrame": b, "trackIndex": track, "recordFrame": rec}
    if media:
        d["mediaType"] = media
    res = mp.AppendToTimeline([d]) or []
    if media == 2:
        return res[0] if res else None
    v = [x for x in res if (x.GetTrackTypeAndIndex() or ["?"])[0] == "video"]
    return v[0] if v else None


def build():
    pcs, total = plan()
    r = connect(); pm = r.GetProjectManager(); p = pm.GetCurrentProject()
    print("project:", p.GetName())
    if p.GetTimelineCount() == 0:
        p.SetSetting("timelineDropFrameTimecode", "0")
    mp = p.GetMediaPool(); root = mp.GetRootFolder()
    sub = lambda nm: next((f for f in root.GetSubFolderList() or [] if f.GetName() == nm), None) or mp.AddSubFolder(root, nm)
    pool = {}
    for k, path in SRC.items():
        mp.SetCurrentFolder(sub("aroll" if k == "A" else "broll"))
        pool[k] = find_clip(root, os.path.basename(path)) or (mp.ImportMedia([path]) or [None])[0]
        if not pool[k]:
            sys.exit(f"import failed: {path}")
    mp.SetCurrentFolder(sub("sfx"))
    sfx = {k: find_clip(root, os.path.basename(v)) or mp.ImportMedia([v])[0] for k, v in SFX.items()}
    carrier = find_clip(root, "Smooth Word Up")
    if not carrier:
        mp.SetCurrentFolder(root); mp.ImportFolderFromFile(MTP_DRB); carrier = find_clip(root, "Smooth Word Up")
    if not carrier:
        sys.exit("MTP carrier not found")
    mp.SetCurrentFolder(sub("timelines"))
    taken = {p.GetTimelineByIndex(i).GetName() for i in range(1, p.GetTimelineCount() + 1)}
    v = 1
    while TL_NAME.format(v) in taken:
        v += 1
    t = mp.CreateEmptyTimeline(TL_NAME.format(v))
    p.SetCurrentTimeline(t)
    t.SetSetting("useCustomSettings", "1")
    t.SetSetting("timelineResolutionWidth", str(TW)); t.SetSetting("timelineResolutionHeight", str(TH))
    t.SetSetting("timelineInputResMismatchBehavior", "scaleToFill")
    t0 = t.GetStartFrame()
    for _ in range(3):
        t.AddTrack("video")
    for _ in range(2):
        t.AddTrack("audio", "stereo")
    for i, nm in enumerate(["aroll", "cutaways", "inset+cards", "text"], 1):
        t.SetTrackName("video", i, nm)
    jd = os.path.join(HERE, "comps")
    # V1 A-roll
    v1 = {}
    for nm, a, b, z in SEGS:
        pc = pcs[nm]
        it = append(mp, pool["A"], a, pc["n"], 1, t0 + pc["rec"])
        if not it:
            sys.exit(f"A-roll piece {nm} failed")
        if z != 1.0:
            it.SetProperty({"ZoomX": z, "ZoomY": z})
        v1[nm] = it
    hook = pcs["hook"]
    # opener: canvas on V2 under the inset, inset on V3 at its settled zoomed-out size
    ia, ib = fr(OPEN_INSET[2]), fr(OPEN_INSET[3])
    cv = place(mp, t, carrier, t0 + hook["rec"] + ia, ib - ia, 2)
    attach(cv, solid_comp(cv.GetDuration(), CANVAS), f"{jd}/canvas_open.comp"); cv.SetClipColor("Beige")
    ins = append(mp, pool[OPEN_INSET[0]], OPEN_INSET[1], ib - ia, 3, t0 + hook["rec"] + ia, 1)
    inset_zoom(ins)
    # rapid cuts
    n_r = len(OPEN_RAPID)
    step = (fr(RAPID_TO) - fr(RAPID_FROM)) / n_r
    for i, (k, cin) in enumerate(OPEN_RAPID):
        a = fr(RAPID_FROM) + int(round(i * step)); b = fr(RAPID_FROM) + int(round((i + 1) * step))
        it = append(mp, pool[k], cin, b - a, 2, t0 + hook["rec"] + a, 1)
        it.SetClipColor("Orange")
    # cutaways + payoffs
    v2 = []
    for seg, a_s, b_s, k, cin, po in CUTS:
        pc = pcs[seg]
        a, b = t_of(pc, a_s), min(t_of(pc, b_s), pc["rec"] + pc["n"])
        it = append(mp, pool[k], cin, b - a, 2, t0 + a, 1)
        if not it:
            print("cutaway failed", seg, k); continue
        if po:
            wt = next((w[1] for w in W_ALL if w[0].strip(".,?!").upper() == po[0] and a_s - 1 <= w[1] <= b_s + 0.5), a_s)
            tt = next((w[1] for w in W_ALL if po[2] and w[0].strip(".,?!").upper() == po[2].split()[0] and wt <= w[1] <= b_s + 1), b_s)
            payoff_into(it, po[0], po[1], po[2], po[3], po[4], key=k, sec=cin + (b - a) / FPS * 0.7,
                        word_f=max(0, t_of(pc, wt) - a), tail_f=max(0, t_of(pc, tt) - a))
        else:
            push_into(it)
        it.SetClipColor("Teal"); v2.append((seg, a, b, it))
    # canvas list: white canvas over all list pieces, one tilted card per word, its word in ink on the canvas
    la, lb = pcs["l1"]["rec"], pcs["l4"]["rec"] + pcs["l4"]["n"]
    cv = place(mp, t, carrier, t0 + la, lb - la, 2)
    attach(cv, solid_comp(cv.GetDuration(), CANVAS), f"{jd}/canvas_list.comp"); cv.SetClipColor("Beige")
    starts = [t_of(pcs[s], ws) for s, ws, *_ in CARDS] + [lb]
    n_ok = 0
    for i, (s, ws, k, cin, word) in enumerate(CARDS):
        a, b = max(starts[i], la), starts[i + 1]
        it = append(mp, pool[k], cin, b - a, 3, t0 + a, 1)
        card_in(it)
        it.SetClipColor("Pink")
        px = min(92, 0.34 * TW / max(hn_width(word, 1), 1e-6))
        tx = place(mp, t, carrier, t0 + a, b - a, 4)
        attach(tx, text_comp(tx.GetDuration(), [(word, 0.77 * TW, 0.50 * TH, px, INK)], typeon=True), f"{jd}/card_{i}.comp")
        n_ok += 1
    # end payoff behind the head
    seg, at, word, lead, tail, rgb = END_PAYOFF
    pc9 = pcs[seg]
    wf = t_of(pc9, next(w[1] for w in W_ALL if w[0].strip(".,?!").upper() == word)) - pc9["rec"]
    tf = t_of(pc9, next(w[1] for w in W_ALL if w[0].upper() == "GO" and w[1] > 203)) - pc9["rec"]
    payoff_into(v1[seg], word, lead, tail, (0.25, 0.62), rgb, key="A", sec=204.6, word_f=wf, tail_f=tf, push=False)
    # invert strobe into p2a (inverted, normal, inverted), white blow-out into p5
    T = pcs[STROBE_INTO]["rec"]
    strobe(v1[STROBE_INTO], [T, T + 2], T)
    blowout(v1[BLOWOUT_INTO])
    # captions: one word at a time where the A-roll is on screen; white centre words over the opener
    cover = [(pcs["hook"]["rec"], pcs["hook"]["rec"] + pcs["hook"]["n"])] + [(a, b) for _, a, b, _ in v2] + [(la, lb)]
    cover.append((t_of(pcs[seg], at) - 10, pcs[seg]["rec"] + pcs[seg]["n"]))
    clicks = []
    for nm, a, b, z in SEGS:
        pc = pcs[nm]
        ws = [w for w in W_ALL if a <= w[1] < b - 0.05]
        for j, (w, ws_, we) in enumerate(ws):
            f0 = t_of(pc, ws_)
            f1 = t_of(pc, ws[j + 1][1]) if j + 1 < len(ws) else pc["rec"] + pc["n"]
            f0 = max(f0, pc["rec"])
            if f1 - f0 < 2:
                continue
            word = w.strip(".,?!").upper().replace("POLYMOTS", "POLYMATHS")
            opener = nm == "hook" and f0 < hook["rec"] + fr(3.30)
            if not opener and any(c0 <= f0 < c1 for c0, c1 in cover):
                continue
            it = place(mp, t, carrier, t0 + f0, f1 - f0, 4)
            if not it:
                continue
            if opener:
                items = [(word, 0.5 * TW, 0.50 * TH, 64, WHITE)]
            else:
                cw = hn_width(word, CAP_PX)
                col = pick("A", ws_, (CAP_POS[0] * TW - cw / 2, CAP_POS[1] * TH - 20, CAP_POS[0] * TW + cw / 2, CAP_POS[1] * TH + 20), word)
                items = [(word, CAP_POS[0] * TW, CAP_POS[1] * TH, CAP_PX, col)]
            weak_cap = (not opener) and REPORT and REPORT[-1][0] == word and REPORT[-1][3] == "halo"
            attach(it, text_comp(it.GetDuration(), items, halo=opener or weak_cap), f"{jd}/cap_{nm}_{j}.comp")
            n_ok += 1
    # SFX: a click on every caption, whoosh on every card, hits on the strobe + WIN
    def sfx_at(k, f, track):
        it = append(mp, sfx[k], 0, fr(0.8), track, t0 + f, 2)
        if it:
            it.SetProperty("Volume", SFX_DB[k])
    sfx_at("whoosh", max(la - 4, 0), 3)
    sfx_at("hit", T, 3)
    refresh(t)
    pm.SaveProject()
    json.dump(REPORT, open(os.path.join(HERE, "readable.json"), "w"), indent=0)
    weak_ = [r for r in REPORT if r[2] < 3.0]
    print("readable checks:", len(REPORT), "below 3.0 (haloed):", weak_)
    print(json.dumps({"timeline": t.GetName(), "seconds": round(total / FPS, 2), "text_items": n_ok, "cutaways": len(v2)}))


def refresh(t):
    """re-wire MediaOut so live comp edits reach the Edit page (skips carriers with no MediaIn)"""
    for tr in (1, 2, 3):
        for it in t.GetItemListInTrack("video", tr) or []:
            if (it.GetFusionCompCount() or 0) < 1:
                continue
            c = it.GetFusionCompByIndex(1); mo = c.FindTool("MediaOut1"); mi = c.FindTool("MediaIn1")
            if not (mo and mi):
                continue
            src = mo.Input.GetConnectedOutput()
            if src:
                mo.Input = mi.Output; mo.Input = src


def blowout(it):
    """white blow-out into a piece: 2 frames full white, then 3 frames easing back"""
    c = comp_of(it)
    g = RS
    mo = c.FindTool("MediaOut1")
    feed = mo.Input.GetConnectedOutput().GetTool()
    c.Lock()
    bg = c.AddTool("Background", -32768, -32768); bg.SetAttrs({"TOOLS_Name": "BlowWhite"})
    bg.SetInput("UseFrameFormatSettings", 0); bg.SetInput("Width", TW); bg.SetInput("Height", TH)
    for ch in ("TopLeftRed", "TopLeftGreen", "TopLeftBlue", "TopLeftAlpha"):
        bg.SetInput(ch, 1.0)
    m = c.AddTool("Merge", -32768, -32768); m.SetAttrs({"TOOLS_Name": "Blow"})
    m.Background = feed.Output; m.Foreground = bg.Output
    m.Blend.SetExpression(f"iif(time<{g}+2, 1, max(0, 1-(time-({g}+1))/4))")
    mo.Input = m.Output
    c.Unlock()


def stills():
    pcs, total = plan()
    r = connect(); p = r.GetProjectManager().GetCurrentProject(); t = p.GetCurrentTimeline()
    r.OpenPage("edit"); refresh(t)
    out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
    marks = {"01_inset": fr(0.6), "02_rapid": fr(1.5), "03_win": t_of(pcs["hook"], 146.9),
             "04_caption": t_of(pcs["p2a"], 8.9), "05_irrelevant": t_of(pcs["p2b"], 13.0),
             "06_clicks": t_of(pcs["p3"], 16.2), "07_card_psych": t_of(pcs["l1"], 27.6),
             "08_card_human": t_of(pcs["l3"], 35.6), "09_card_maths": t_of(pcs["l4"], 45.4),
             "10_videographer": t_of(pcs["p5"], 74.4), "11_perception": t_of(pcs["p6"], 80.0),
             "12_punch": t_of(pcs["p7a"], 106.8), "13_layers": t_of(pcs["p8a"], 176.0),
             "14_core": t_of(pcs["p8b"], 181.3), "15_scrolling": t_of(pcs["p9"], 204.6)}
    if len(sys.argv) > 2:
        marks = {k: v for k, v in marks.items() if k in sys.argv[2:]}
    t0 = t.GetStartFrame()
    fps_i = 30
    for name, f in marks.items():
        F = t0 + f
        t.SetCurrentTimecode(f"{F // (fps_i * 3600):02d}:{F // (fps_i * 60) % 60:02d}:{F // fps_i % 60:02d}:{F % fps_i:02d}")
        time.sleep(3)
        print(name, p.ExportCurrentFrameAsStill(os.path.join(out, name + ".png")))


if __name__ == "__main__":
    {"stills": stills}.get((sys.argv[1:2] or ["build"])[0], build)()
