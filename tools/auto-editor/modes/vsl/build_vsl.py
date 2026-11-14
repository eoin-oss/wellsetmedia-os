"""VSL mode: Eoin's 16:9 VSL (vsl cut + intro.mov), built natively in Resolve. Plan agreed 26 Oct:
camera overlays in the dark side of frame, white scenes with a rounded facecam for 'what you've tried' and the
audit, full white cover cards for the two testimonials (photo boxed left, their sentence forming as he reads it),
the Signal Loop drawn on in teal, soft Helvetica throughout, captions from 0:07. No CTA graphics (the button lives
on the lander), no RTÉ tag.
Tracks: V1 A-roll (+A1, levelled), V2 facecam copies (crop/zoom), V3 scenes (white frames + cards),
V4 overlays on camera, V5 captions.
Usage: python3 build_vsl.py [plan]          (plan = print the map, touch nothing)
       python3 build_vsl.py build [project]  (default project 'vsl auto'; new timeline version each run)"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "../../engine"))
import rv
from vslfx import *

JD = os.path.abspath(os.path.join(HERE, "../../jobs/vsl"))
AS = os.path.join(JD, "assets")
SRC = "/Volumes/Extreme SSD/vsl cut + intro.mov"
DUR = 317.24

# ---- words (caption fixes: whisper heard Eoin as Owen, RTÉ as RTE, Hempton as Hampton) ------------------------
FIX = {"owen": "Eoin", "rte": "RTÉ", "hampton": "Hempton"}


def load_words():
    out = []
    for w in json.load(open(os.path.join(JD, "words.json"))):
        s = w["w"].strip()
        if not s:
            continue
        core = re.sub(r"[^\w]", "", s.lower())
        if core in FIX:
            s = re.sub(r"[A-Za-z]+", FIX[core], s, count=1)
        if core == "entered" and 62 < w["start"] < 63:
            s = "interned"
        out.append({"w": s, "s": w["start"], "e": w["end"]})
    return out


WORDS = load_words()


def at(word, near):
    """start of the spoken `word` closest to `near` seconds"""
    hits = [w for w in WORDS if re.sub(r"[^\w']", "", w["w"].lower()) == word.lower() and abs(w["s"] - near) < 4]
    if not hits:
        sys.exit(f"word not found: {word} near {near}")
    return min(hits, key=lambda w: abs(w["s"] - near))["s"]


def align(txt, a, b):
    """time each displayed word to its spoken match in [a, b); unmatched words land with the previous one"""
    spoken = span(a, b)
    out, j, last = [], 0, spoken[0][1]
    for d in txt.split():
        key = re.sub(r"[^\w']", "", d.lower())
        for k in range(j, len(spoken)):
            if re.sub(r"[^\w']", "", spoken[k][0].lower()) == key:
                last, j = spoken[k][1], k + 1
                break
        out.append((d, last))
    return out


def span(a, b):
    """[(word, t)] spoken between a and b"""
    return [(w["w"], w["s"]) for w in WORDS if a <= w["s"] < b]


# ---- layout --------------------------------------------------------------------------------------------------
FC = (110, 140, 725, 960)                          # facecam window (rounded, white around it)
FCX, FCY, FCW, FCH = (FC[0] + FC[2]) / 2, (FC[1] + FC[3]) / 2, FC[2] - FC[0], FC[3] - FC[1]
WIN_W, WIN_H, WIN_Y0 = 780, 1040, 20               # source window cut around his face (3:4)
FACECAM = {  # (from, to, face centre x in the source) per camera angle, cut points from jobs/vsl/cuts.txt
    "tried": [(98.84, 101.76, 990), (101.76, 112.28, 880), (112.28, 121.08, 1040), (121.08, 131.04, 900)],
    "audit": [(227.96, 230.64, 880), (230.64, 234.12, 980), (234.12, 240.28, 890)],
}
WHITE_SPANS = [(98.84, 131.04), (204.32, 221.44), (227.96, 246.44)]
NO_CAPS = [(0, 7.16), (54.88, 58.08), (196.2, 203.86), (205.8, 208.3), (213.2, 221.44), (240.28, 246.44)]
CAP_Y, CAP_PX, CAP_INK_PX = 1004, 44, 40
L_X = 110                                          # left margin for overlays on camera


def on_white(t):
    return any(a <= t < b for a, b in WHITE_SPANS)


MANIFEST = []   # readability items: (t, box, rgb, label)


def note(t, s, x, y, px, rgb, left=True):
    w = measure(s, px)
    x0 = x if left else x - w / 2
    MANIFEST.append({"t": round(t, 2), "box": [x0 - 10, y - px * 0.62, x0 + w + 10, y + px * 0.62], "rgb": list(rgb), "label": s})


# ---- small composites ----------------------------------------------------------------------------------------
def group(s, *layers):
    g = s.canvas()
    for l in layers:
        g = s.c.merge(s.nm("G"), g, l)
    return g


def cam_text(s, top, txt, x, y, px, t_in, t_out=None, rgb=WHITE, words=None, left=True, rise=True):
    """white soft Helvetica on camera with its dark halo; words = [(w, t)] makes it form word by word"""
    end = s.end_words(words) if words else None
    hl = s.halo(txt, x, y, px, end=end, left=left)
    tx = s.text(txt, x, y, px, rgb=rgb, end=end, left=left)
    fade = s.fade(t_in, t_out)
    dy = s.rise(t_in, 18) if rise else None
    top = s.put(top, hl, blend=fade, dy=dy)
    top = s.put(top, tx, blend=fade, dy=dy)
    t_note = words[-1][1] + 0.1 if words else t_in + 1.2
    note(min(t_note, (t_out or s.b) - 0.15), txt, x, y, px, rgb, left)
    return top


def ink_text(s, top, txt, x, y, px, t_in, t_out=None, rgb=INK, words=None, left=True, style="Bold", dy=None):
    end = s.end_words(words) if words else None
    tx = s.text(txt, x, y, px, rgb=rgb, end=end, left=left, style=style)
    top = s.put(top, tx, blend=s.fade(t_in, t_out), dy=dy or s.rise(t_in, 14))
    note(min(t_in + 1.0 if not words else words[-1][1] + 0.05, (t_out or s.b) - 0.15), txt, x, y, px, rgb, left)
    return top


def side_panel(s, top, t_in, t_out, width=980):
    """ink fade on the left of frame so overlay text reads on both camera angles"""
    p = s.box(INK, 0.78, width / 2 - 240, H / 2, width + 480, H * 1.3, soft=0.16)
    return s.put(top, p, blend=s.fade(t_in, t_out, 0.5, 0.5))


def grow_bar(s, rgb, a, x0, y, w, h, t_in, dur=0.4):
    """a bar that grows from its left edge"""
    c = s.c
    n = s.nm("Bar")
    lf0 = s.lf(t_in)
    g = lambda f: max(0.001, ease_out(ramp(f, lf0, lf0 + dur * FPS)))
    m = c.tool(n + "M", "RectangleMask", {"Center": AP(lambda f: (x0 + w * g(f) / 2, y)), "Width": A(lambda f: w * g(f) / W),
                                          "Height": h / H, "OutputSize": 0})
    return s.masked_solid(rgb, a, m)


# ---- scenes (V3) ---------------------------------------------------------------------------------------------
def scene_tried():
    a, b = 98.84, 131.04
    s = Scene(a, b)
    top = s.window_frame(FCX, FCY, FCW, FCH)
    top = ink_text(s, top, "WHAT YOU'VE PROBABLY TRIED", 820, 150, 26, 99.0, rgb=TEAL)
    panels = [
        ("01", "Cheap videographer", "Art without strategy", at("cheap", 102.5), at("art", 110.2), at("and", 112.4)),
        ("02", "Agency", "Strategy with no soul", at("agency", 112.9), at("strategy", 121.8), at("and", 123.4)),
        ("03", "Doing it yourself", "Waiting on the algorithm", at("yourself", 125.0), at("algorithm", 128.4), at("never", 130.3)),
    ]
    for i, (num, title, sub, t_in, t_sub, t_dim) in enumerate(panels):
        cy = 305 + i * 240
        x0, x1 = 820, 1810
        card = s.box(WHITE, 1.0, (x0 + x1) / 2, cy, x1 - x0, 210, radius=0.07)
        line = s.box(INK, 0.10, (x0 + x1) / 2, cy, x1 - x0, 210, radius=0.07, border=2)
        g = group(s, s.shadow((x0 + x1) / 2, cy, x1 - x0, 210, radius=0.07, a=0.10, blur=22, off=8), card, line)
        g = s.c.merge(s.nm("G"), g, s.text(num, 870, cy - 38, 30, rgb=TEAL, left=True, soft=False))
        g = s.c.merge(s.nm("G"), g, s.text(title, 940, cy - 38, 56, rgb=INK, left=True))
        sub_l = s.text(sub, 940, cy + 42, 36, rgb=GREY_INK, left=True, style="Regular")
        g = s.c.merge(s.nm("G"), g, s.put(s.canvas(), sub_l, blend=s.fade(t_sub)))
        strike = grow_bar(s, INK, 0.85, 930, cy - 36, measure(title, 56) + 20, 5, t_dim, 0.35)
        g = s.c.merge(s.nm("G"), g, strike)
        dim = s.fade(t_in, t_dim, 0.35, 0.35, lo=0.32)
        top = s.put(top, g, blend=dim, dy=s.rise(t_in, 40, 0.5))
        note(t_in + 0.8, title, 940, cy - 38, 56, INK)
        note(t_sub + 0.5, sub, 940, cy + 42, 36, GREY_INK)
    s.top = top
    return s


def testimonial(a, b, who, photo, handle, quote_words, intro=None):
    """white cover card: photo boxed left, name + handle, their sentence forming on the right as he reads it"""
    s = Scene(a, b)
    top = s.paper(s.canvas())
    t_main = intro["t_main"] if intro else a
    if intro:  # both clients first, then Kyle takes the frame
        tj, tk = intro["t_people"], intro["t_main"]
        top = s.put(top, s.shadow(760, 470, 330, 440, a=0.16, blur=22, off=10), blend=s.fade(a + 0.1, tk, 0.4, 0.3))
        top = s.put(top, s.shadow(1160, 470, 330, 440, a=0.16, blur=22, off=10), blend=s.fade(a + 0.3, tk, 0.4, 0.3))
        top = s.put(top, s.image(f"{AS}/james.jpg", 1160, 470, 330, 440, radius=0.05), blend=s.fade(a + 0.3, tk, 0.4, 0.3),
                    dy=s.rise(a + 0.3, 30))
        words = intro["words"]
        top = ink_text(s, top, " ".join(w for w, _ in words), 960, 780, 46, words[0][1] - 0.04, tk, words=words, left=False)
        k0 = s.lf(tk)
        mv = lambda f: ease_in_out(ramp(f, k0, k0 + 0.6 * FPS))
        sc = lambda f: 0.55 + 0.45 * mv(f) if f >= k0 else 0.55 * (0.94 + 0.06 * ease_out(ramp(f, s.lf(a + 0.1), s.lf(a + 0.6))))
        dx = lambda f: 310 * (1 - mv(f))
        dy = lambda f: -70 * (1 - mv(f)) + (0 if f >= k0 else 20 * (1 - ease_out(ramp(f, s.lf(a + 0.1), s.lf(a + 0.6)))))
        top = s.put(top, s.shadow(450, 540, 600, 800, a=0.18, blur=28, off=14), blend=s.fade(tk + 0.4))
        top = s.put(top, s.image(photo, 450, 540, 600, 800, radius=0.035, sc=sc, dx=dx, dy=dy), blend=s.fade(a + 0.1, None, 0.4))
    else:
        top = s.put(top, s.shadow(450, 540, 600, 800, a=0.18, blur=28, off=14), blend=s.fade(a + 0.1))
        top = s.put(top, s.image(photo, 450, 540, 600, 800, radius=0.035, dx=lambda f: -60 * (1 - ease_out(ramp(f, 0, 0.5 * FPS)))),
                    blend=s.fade(a, None, 0.35))
    tn = t_main + 0.25
    top = ink_text(s, top, who, 860, 205, 44, tn)
    top = ink_text(s, top, handle, 860, 255, 28, tn + 0.15, rgb=GREY_INK, style="Regular")
    top = s.put(top, s.text("“", 860, 370, 150, rgb=TEAL, left=True, soft=False), blend=s.fade(quote_words[0][1] - 0.3))
    for i, ln in enumerate(wrap(quote_words, 58, 920)):
        y = 440 + i * 80
        txt = " ".join(w for w, _ in ln)
        top = s.put(top, s.text(txt, 860, y, 58, rgb=INK, left=True, end=s.end_words(ln)))
        note(ln[-1][1] + 0.3, txt, 860, y, 58, INK)
    s.top = top
    return s


def scene_kyle():
    a, b = 204.32, 221.44
    q = span(213.2, 221.3)
    return testimonial(a, b, "Kyle Ritchie", f"{AS}/kyle.jpg", "@kyleritchie_morelife", q,
                       intro={"t_people": 205.88, "t_main": at("before", 208.45), "words": span(205.8, 208.3)})


def scene_james():
    a, b = 240.28, 246.44
    return testimonial(a, b, "James Hempton", f"{AS}/james.jpg", "@jameshempton_", span(241.5, 246.4))


def scene_audit():
    a, b = 227.96, 240.28
    s = Scene(a, b)
    top = s.window_frame(FCX, FCY, FCW, FCH)
    top = ink_text(s, top, "SIGNATURE CONTENT AUDIT", 820, 110, 26, at("signature", 229.0), rgb=TEAL)
    t1, t_fan, t_zoom, t_plan = at("signature", 229.0), at("no", 230.7), at("clarity", 236.9) - 0.6, at("moving", 239.0)
    PH = 720
    PW = PH * 1240 / 1754
    cx, cy = 1310, 560
    fan = s.lf(t_fan)
    m = lambda f: ease_in_out(ramp(f, fan, fan + 0.6 * FPS))
    out_fan = s.fade(t1, t_zoom, 0.45, 0.35)
    for pg, side in (("page2", -1), ("page3", 1)):
        lay = s.image(f"{AS}/{pg}.jpg", cx, cy, PW, PH, radius=0.012, dx=lambda f, sd=side: sd * 235 * m(f),
                      dy=lambda f: 26 * m(f), angle=A(lambda f, sd=side: -sd * 6 * m(f)))
        top = s.put(top, lay, blend=lambda f, o=out_fan: o(f) * min(1, m(f) * 3))
    rise1 = s.rise(t1, 60, 0.55)
    top = s.put(top, s.shadow(cx, cy, PW, PH, radius=0.012, a=0.22, blur=26, off=14), blend=out_fan, dy=rise1)
    top = s.put(top, s.image(f"{AS}/page1.jpg", cx, cy, PW, PH, radius=0.012), blend=out_fan, dy=rise1)
    # the chart that answers 'clarity': page 3, median views by format
    zw, zh = 1000, 700
    crop = (66, 300, 1176, 1077)       # same 10:7 as the window, so nothing is cut
    z0 = s.lf(t_zoom)
    zsc = lambda f: 0.9 + 0.1 * ease_out(ramp(f, z0, z0 + 0.5 * FPS))
    zfade = s.fade(t_zoom, t_plan, 0.35, 0.35)
    top = s.put(top, s.shadow(cx, cy, zw, zh, radius=0.02, a=0.22), blend=zfade)
    top = s.put(top, s.image(f"{AS}/page3.jpg", cx, cy, zw, zh, radius=0.02, crop=crop, sc=zsc), blend=zfade)
    k = max(zw / (crop[2] - crop[0]), zh / (crop[3] - crop[1]))
    ccx, ccy = (crop[0] + crop[2]) / 2, (crop[1] + crop[3]) / 2
    sx = lambda px_: cx + (px_ - ccx) * k
    sy = lambda py_: cy + (py_ - ccy) * k
    hl = s.box(TEAL_HI, 1.0, (sx(140) + sx(1100)) / 2, (sy(440) + sy(650)) / 2, sx(1100) - sx(140), sy(650) - sy(440), radius=0.04, border=5)
    top = s.put(top, hl, blend=s.fade(t_zoom + 1.1, t_plan, 0.3, 0.3))
    # 'moving forward': the month-one play (cropped below the seminar pricing on that page)
    pw_, ph_ = 1020, 358
    pcrop = (100, 2280, 2380, 3080)      # 'Month one' + the first move; the seminar price sits above y 2000
    ps = s.lf(t_plan)
    pdx = lambda f: 500 * (1 - ease_out(ramp(f, ps, ps + 0.5 * FPS)))
    top = s.put(top, s.shadow(cx, cy, pw_, ph_, radius=0.02, a=0.22), blend=s.fade(t_plan), dx=pdx)
    top = s.put(top, s.image(f"{AS}/page17hi.jpg", cx, cy, pw_, ph_, radius=0.02, crop=pcrop), blend=s.fade(t_plan), dx=pdx)
    s.top = top
    return s


# ---- overlays on camera (V4) ---------------------------------------------------------------------------------
def ov_wants():
    a, b = 7.16, 14.88
    s = Scene(a, b)
    top = s.canvas()
    top = cam_text(s, top, "THEY WANT", L_X, 370, 28, at("they", 7.24), b, rgb=TEAL_HI)
    for i, (txt, word, near) in enumerate((("More leads", "leads", 8.0), ("Trust before they meet you", "trust", 9.75),
                                           ("A brand people remember", "brand", 11.94))):
        top = cam_text(s, top, txt, L_X, 445 + i * 72, 50, at(word, near) - 0.1, b)
    s.top = top
    return s


def ov_chapter(a, b, num, label, t_in):
    s = Scene(a, b)
    top = s.canvas()
    top = cam_text(s, top, num, L_X, 110, 30, t_in, b, rgb=TEAL_HI)
    top = cam_text(s, top, label, L_X + 58, 110, 34, t_in + 0.1, b)
    s.top = top
    return s


def ov_punch():
    a, b = 54.88, 58.08
    s = Scene(a, b)
    top = s.c.solid("Ink", INK)
    top = s.put(s.canvas(), top)
    top = cam_text(s, top, "The problem is that", 960, 410, 40, at("the", 54.92), rgb=GREY, left=False)
    w1 = [(w, t) for w, t in span(56.0, 57.1)]
    top = cam_text(s, top, "nobody built it", 960, 530, 112, w1[0][1] - 0.04, words=w1, left=False, rise=False)
    w2 = [("to", at("to", 57.2)), ("sell.", at("sell", 57.43))]
    top = cam_text(s, top, "to sell.", 960, 665, 112, w2[0][1] - 0.04, rgb=TEAL_HI, words=w2, left=False, rise=False)
    s.top = top
    return s


def ov_lower_third():
    a, b = 61.3, 67.0
    s = Scene(a, b)
    top = s.put(s.canvas(), grow_bar(s, TEAL_HI, 1.0, L_X, 880, 4, 96, a + 0.05, 0.3), blend=s.fade(a, b))
    top = cam_text(s, top, "Eoin Wells", L_X + 24, 858, 48, a + 0.1, b)
    top = cam_text(s, top, "Founder, WellSetMedia", L_X + 24, 910, 30, a + 0.3, b)
    s.top = top
    return s


def ov_names():
    a, b = 70.3, 76.3
    s = Scene(a, b)
    top = side_panel(s, s.canvas(), a, b, 900)
    top = cam_text(s, top, "FOUNDERS I'VE MADE CONTENT FOR", L_X, 360, 26, at("people", 70.36), b, rgb=TEAL_HI)
    for i, (nm_, word, near) in enumerate((("Ryan Kelly", "ryan", 70.95), ("James Hempton", "james", 71.76),
                                           ("Kyle Ritchie", "kyle", 72.96), ("Josh Talks Biz", "josh", 74.16))):
        top = cam_text(s, top, nm_, L_X, 435 + i * 70, 48, at(word, near) - 0.1, b)
    s.top = top
    return s


def ov_loop():
    a, b = 136.3, 193.25
    s = Scene(a, b)
    top = side_panel(s, s.canvas(), a, b, 1000)
    cx, cy, r = 365, 330, 150
    nodes = [(0, "1"), (120, "2"), (240, "3")]
    t1, t2, t3, tc = at("step", 136.36), at("two", 153.4), at("three", 176.0), at("goes", 185.02)
    tname = at("signal", 187.48)
    fade_all = s.fade(a, b, 0.4, 0.4)
    top = s.put(top, s.arc(cx, cy, r, 0, 360, 3, WHITE, 0.22), blend=fade_all)
    for a0, a1, t in ((0, 120, t2), (120, 240, t3), (240, 360, tc)):
        f0 = s.lf(t)
        top = s.put(top, s.arc(cx, cy, r, a0, a1, 6, TEAL_HI, write=lambda f, f0=f0: ease_in_out(ramp(f, f0, f0 + 0.9 * FPS))), blend=fade_all)
    for (ang, num), t in zip(nodes, (t1, t2 + 0.8, t3 + 0.8)):
        x, y = cx + r * math.sin(math.radians(ang)), cy - r * math.cos(math.radians(ang))
        top = s.put(top, s.dot(x, y, 54, INK), blend=fade_all)
        top = s.put(top, s.dot(x, y, 54, WHITE, 0.35, border=3), blend=fade_all)
        top = s.put(top, s.dot(x, y, 54, TEAL), blend=lambda f, t=t, fa=fade_all: s.fade(t)(f) * fa(f))
        top = s.put(top, s.text(num, x, y + 1, 26, rgb=WHITE, soft=False), blend=fade_all)
    top = cam_text(s, top, "The Signal", cx, cy - 22, 40, tname - 0.05, b, left=False)
    top = cam_text(s, top, "Loop", cx, cy + 26, 40, tname + 0.2, b, rgb=TEAL_HI, left=False)
    steps = [
        (t1, t2, "01", "Find the signal", [("What already works", "what's", 141.3), ("What people stop for", "people", 145.6),
                                           ("Research, not output", "research", 148.2), ("The audience tells us first", "audience", 151.5)]),
        (t2, t3, "02", "Build to it", [("Scripts, shot lists, planning", "scripts", 158.6), ("One to two shoot days", "one", 162.4),
                                       ("Directed and graded", "camera", 165.4), ("Edited, scheduled, posted", "edited", 173.9)]),
        (t3, tc, "03", "Review", [("What reached, what didn't", "numbers", 177.4), ("Decides next month", "decides", 180.1),
                                  ("Nothing guessed twice", "guessed", 183.6)]),
        (tc, b, "", "Around again", [("Sharper every month", "sharper", 188.75), ("Moves with the market", "adjusts", 191.3)]),
    ]
    for t_in, t_out, num, title, keys in steps:
        if num:
            top = cam_text(s, top, num, L_X, 600, 28, t_in, t_out, rgb=TEAL_HI)
        top = cam_text(s, top, title, L_X + (54 if num else 0), 600, 46, t_in + 0.05, t_out)
        for i, (k, word, near) in enumerate(keys):
            top = cam_text(s, top, k, L_X, 680 + i * 56, 32, at(word, near) - 0.1, t_out, rgb=(0.86, 0.88, 0.88))
    s.top = top
    return s


def ov_position():
    a, b = 194.7, 203.86
    s = Scene(a, b)
    top = side_panel(s, s.canvas(), a, b, 1000)
    rows = [("I create personal brand", 196.2, 197.3, WHITE), ("content for founders", 197.4, 198.7, WHITE),
            ("using the Signal Loop", 198.7, 199.8, TEAL_HI), ("More leads", 200.5, 201.2, WHITE),
            ("A brand people buy into", 201.8, 203.6, WHITE)]
    for i, (txt, w0, w1, rgb) in enumerate(rows):
        y = 330 + i * 76 + (24 if i >= 3 else 0)
        ws = align(txt, w0, w1)
        if i >= 3:
            top = s.put(top, grow_bar(s, TEAL_HI, 1.0, L_X, y, 4, 52, ws[0][1] - 0.05, 0.25), blend=s.fade(a, b))
        top = cam_text(s, top, txt, L_X + (22 if i >= 3 else 0), y, 50, ws[0][1] - 0.05, b, rgb=rgb, words=ws)
    s.top = top
    return s


def ov_result(a, b, who, photo, lines):
    s = Scene(a, b)
    fade = s.fade(a, b, 0.35, 0.35)
    top = s.put(s.canvas(), s.box(INK, 0.72, 430, 815, 680, 210, radius=0.08), blend=fade, dy=s.rise(a, 20))
    top = s.put(top, s.image(photo, 185, 815, 120, 160, radius=0.08), blend=fade, dy=s.rise(a, 20))
    top = cam_text(s, top, who, 270, 755, 34, a + 0.1, b, rgb=TEAL_HI)
    for i, (txt, t) in enumerate(lines):
        top = cam_text(s, top, txt, 270, 812 + i * 52, 36 if i == 0 else 30, t, b, rgb=WHITE if i == 0 else (0.82, 0.84, 0.84))
    s.top = top
    return s


def overlays():
    return [
        ("wants", ov_wants()),
        ("ch01", ov_chapter(22.5, 39.0, "01", "Paid for nice videos", at("first", 22.9))),
        ("ch02", ov_chapter(39.05, 52.05, "02", "Doing it yourself", at("second", 39.4))),
        ("punch", ov_punch()),
        ("lower3", ov_lower_third()),
        ("names", ov_names()),
        ("loop", ov_loop()),
        ("position", ov_position()),
        ("kyle_res", ov_result(256.05, 267.5, "Kyle Ritchie", f"{AS}/kyle.jpg",
                               [("Time to grow the business", at("time", 257.25)), ("No longer babysitting", at("babysitting", 263.84))])),
        ("james_res", ov_result(267.5, 274.75, "James Hempton", f"{AS}/james.jpg",
                                [("His time back", at("time", 268.1)), ("Podcast out at volume", at("podcasts", 273.27))])),
    ]


def scenes():
    return [("tried", scene_tried()), ("kyle", scene_kyle()), ("audit", scene_audit()), ("james", scene_james())]


# ---- captions (V5) -------------------------------------------------------------------------------------------
def chunks():
    W_ = [w for w in WORDS if w["s"] >= 7.16 and not any(a <= w["s"] < b for a, b in NO_CAPS)]
    out, cur = [], []
    for i, w in enumerate(W_):
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        nxt = W_[i + 1] if i + 1 < len(W_) else None
        edges = [x for ab in NO_CAPS + WHITE_SPANS for x in ab]
        if (not nxt or len(cur) >= 6 or len(txt + " " + nxt["w"]) > 38 or nxt["s"] - w["e"] > 0.7
                or any(w["s"] < x <= nxt["s"] for x in edges)
                or (len(cur) >= 2 and re.search(r"[.,?!]$", w["w"]))):
            out.append(cur); cur = []
    caps = []
    for j, ch in enumerate(out):
        a = ch[0]["s"] - 0.04
        nxt = out[j + 1][0]["s"] - 0.04 if j + 1 < len(out) else DUR
        b = min(nxt, ch[-1]["e"] + 0.35) if nxt - ch[-1]["e"] > 0.6 else nxt
        for x0, x1 in NO_CAPS + WHITE_SPANS:     # never straddle a scene edge
            if a < x0 < b:
                b = x0
        if round(b * FPS) - round(a * FPS) >= 3:
            caps.append((a, b, " ".join(x["w"] for x in ch).rstrip(".")))
    return caps


def caption_comp(a, b, txt):
    s = Scene(a, b)
    if on_white(a):
        top = s.put(s.canvas(), s.text(txt, 960, CAP_Y + 6, CAP_INK_PX, rgb=INK, left=False))
        note((a + b) / 2, txt, 960, CAP_Y + 6, CAP_INK_PX, INK, left=False)
    else:
        top = s.put(s.canvas(), s.halo(txt, 960, CAP_Y, CAP_PX))
        top = s.put(top, s.text(txt, 960, CAP_Y, CAP_PX, rgb=WHITE, left=False))
        note((a + b) / 2, txt, 960, CAP_Y, CAP_PX, WHITE, left=False)
    s.top = top
    return s


# ---- Resolve -------------------------------------------------------------------------------------------------
def facecam_props(cx):
    x0, y0 = min(max(cx - WIN_W / 2, 0), 1920 - WIN_W), WIN_Y0
    z = FCH / WIN_H
    wcx, wcy = x0 + WIN_W / 2, y0 + WIN_H / 2
    return {"CropLeft": float(x0), "CropRight": float(1920 - x0 - WIN_W), "CropTop": float(y0), "CropBottom": float(1080 - y0 - WIN_H),
            "ZoomX": z, "ZoomY": z, "Pan": FCX - 960 - (wcx - 960) * z, "Tilt": -(FCY - 540 - (wcy - 540) * z)}


def prep_assets():
    hi = f"{AS}/page17hi.jpg"
    if not os.path.exists(hi):
        os.system(f"pdftoppm -r 300 -jpeg -jpegopt quality=92 -f 17 -l 17 -singlefile '{os.path.expanduser('$WSM_HOME/clients/kyle-ritchie/audit/report.pdf')}' '{hi[:-4]}'")
    for f in ("kyle.jpg", "james.jpg", "page1.jpg", "page2.jpg", "page3.jpg", "page17hi.jpg"):
        if not os.path.exists(f"{AS}/{f}"):
            sys.exit(f"missing asset {f}")


def all_comps():
    MANIFEST.clear()
    sc, ov = scenes(), overlays()
    caps = [(f"cap_{i:03d}", caption_comp(a, b, t)) for i, (a, b, t) in enumerate(chunks())]
    return sc, ov, caps


def build(project):
    prep_assets()
    sc, ov, caps = all_comps()
    for nm, s in sc + ov + caps:     # validate every comp before Resolve is touched
        rv.check_comp(s.out(s.top), nm)
    r = rv.connect(); pm = r.GetProjectManager()
    pm.GotoRootFolder()
    p = pm.LoadProject(project)
    if not p:
        p = pm.CreateProject(project)
        p.SetSetting("timelineFrameRate", "25")
        p.SetSetting("timelineResolutionWidth", "1920")
        p.SetSetting("timelineResolutionHeight", "1080")
    mp = p.GetMediaPool()
    car = rv.carrier(mp)
    clip = rv.find_clip(mp.GetRootFolder(), os.path.basename(SRC)) or mp.ImportMedia([SRC])[0]
    names = {p.GetTimelineByIndex(i).GetName() for i in range(1, p.GetTimelineCount() + 1)}
    v = 1
    while f"VSL v{v}" in names:
        v += 1          # never delete or overwrite a timeline from a script
    t = mp.CreateEmptyTimeline(f"VSL v{v}")
    t.SetSetting("useCustomSettings", "1")
    t.SetSetting("timelineFrameRate", "25"); t.SetSetting("timelineResolutionWidth", "1920"); t.SetSetting("timelineResolutionHeight", "1080")
    p.SetCurrentTimeline(t)
    t0 = t.GetStartFrame()
    frames = int(float(clip.GetClipProperty("Frames")))
    mp.AppendToTimeline([{"mediaPoolItem": clip, "startFrame": 0, "endFrame": frames, "trackIndex": 1, "recordFrame": t0, "mediaType": 1}])
    au = mp.AppendToTimeline([{"mediaPoolItem": clip, "startFrame": 0, "endFrame": frames, "trackIndex": 1, "recordFrame": t0, "mediaType": 2}])
    if au:
        au[0].SetProperty("AudioVolume", AUDIO_GAIN)
    for nm in ("facecam", "scenes", "overlays", "captions"):
        t.AddTrack("video")
    for i, nm in enumerate(("aroll", "facecam", "scenes", "overlays", "captions"), 1):
        t.SetTrackName("video", i, nm)
    rep = {"timeline": f"VSL v{v}", "facecam": 0, "comps": 0, "fail": []}
    for segs in FACECAM.values():
        for a, b, cx in segs:
            it = mp.AppendToTimeline([{"mediaPoolItem": clip, "startFrame": round(a * FPS), "endFrame": round(b * FPS), "trackIndex": 2,
                                       "recordFrame": t0 + round(a * FPS), "mediaType": 1}])
            if it and it[0].SetProperty(facecam_props(cx)):
                rep["facecam"] += 1
            else:
                rep["fail"].append(f"facecam {a}")
    cd = os.path.join(JD, "comps")
    for track, items, colour in ((3, sc, "Teal"), (4, ov, "Orange"), (5, caps, "Blue")):
        for nm, s in items:
            it = rv.place(mp, t, car, t0 + round(s.a * FPS), s.n, track, FPS)
            if not it:
                rep["fail"].append(nm); continue
            s.c.n = it.GetDuration()
            rv.attach(it, s.out(s.top), f"{cd}/{nm}.comp")
            it.SetClipColor(colour)
            rep["comps"] += 1
            print(nm, flush=True)
    path = os.path.join(JD, "text_manifest.json")
    json.dump({"timeline": rep["timeline"], "items": MANIFEST}, open(path, "w"), indent=0)
    rep["manifest"] = path
    pm.SaveProject()
    return rep


# dB on A1. Source is -26.1 LUFS / -7.5 dBTP; +6.4 puts the peak at -1.1 (about -19.7 LUFS). Going louder needs a
# limiter, which the API can't add (no Fairlight preset); the Dialogue Leveler raised peaks (+10 dB rendered +4.8 dBTP).
AUDIO_GAIN = 6.4

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        prep_assets()
        sc, ov, caps = all_comps()
        for nm, s in sc + ov + caps:
            rv.check_comp(s.out(s.top), nm)
        for nm, s in sc + ov:
            print(f"{s.a:7.2f}-{s.b:7.2f}  {nm:9s} {len(s.c.tools)} nodes")
        print(f"{len(caps)} captions, {len(MANIFEST)} text items")
    elif cmd == "build":
        print(json.dumps(build(sys.argv[2] if len(sys.argv) > 2 else "vsl auto"), indent=1))
