"""Penguin mode job: "my content got boring" (C8577, Glasgow). Built from modes/penguin/tools (locked 11 Nov),
with the 11 Nov change: no text hook, BIG captions in the opener.
Usage: python3 build2.py"""
import json, os, sys, wave, array, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = sys.argv[:1] + ["lib"]
import build as B
from build import fr, FPS, TW, TH, WHITE, INK, SRC, HN

TL_NAME = "Eoin · content got boring v{}"
N = "/Volumes/Extreme SSD/personal brand directory/trips/NYC"
PB = "/Volumes/Extreme SSD/personal brand directory"
MB = "/Volumes/Extreme SSD/glasgow november/mine/b roll"
SRC.clear()
SRC.update({
    "A": "/Volumes/Extreme SSD/glasgow november/mine/C8577_00453759.mov",
    "C4389": f"{N}/12/graded/C4389_02214471.mov", "C4394": f"{N}/12/graded/C4394_02217696.mov",
    "C4442": f"{N}/12/graded/C4442_02231991.mov", "C4109": f"{N}/5/graded/C4109_02064396.mov",
    "C4092": f"{N}/4/graded/C4092_02039376.mov", "C4438": f"{N}/12/graded/C4438_02230686.mov",
    "C4458": f"{N}/12/nycd12g/C4458_02236911.mov", "C4456": f"{N}/12/nycd12g/C4456_02236431.mov",
    "C4418": f"{N}/12/graded/C4418_02226171.mov", "C7045": f"{PB}/broll/ambient/C7045_00880110.mov",
    "C4286": f"{N}/9/graded/C4286_02153421.mov", "C4430": f"{N}/12/graded/C4430_02228046.mov",
    "C6997": f"{PB}/broll/working/laptop:desk/C6997_00692355.mov",
    "C2354": f"{PB}/broll/emotion/C2354.MP4",
    "C8582": f"{MB}/C8582_00478749.mov", "C8584": f"{MB}/C8584_00479724.mov", "C8227": f"{MB}/C8227_02422182.mov",
    "C8620": f"{MB}/C8620_00551579.mov", "C8320": f"{MB}/C8320_00101201.mov",
    "C3918": f"{PB}/trips/NYC/day 1 and 2/C3918_01991361.mov",
    "C8317": f"{MB}/C8317_00098952.mov", "C8319": f"{MB}/C8319_00100355.mov",
    "C6998": f"{PB}/broll/working/laptop:desk/C6998_00693540.mov",
})
# A-roll pieces: (name, raw in, raw out, punch). Pauses inside each are cut by plan().
B.SEGS = [("hook", 13.95, 19.25, 1.00), ("p2", 19.40, 21.95, 1.00), ("p3a", 27.80, 29.62, 1.00), ("p3c", 30.70, 34.15, 1.00),
          ("p3b", 38.12, 39.72, 1.12), ("p4", 47.26, 50.08, 1.00), ("p5a", 56.54, 57.60, 1.12),
          ("p5b", 66.15, 68.13, 1.12), ("p5c", 77.05, 78.95, 1.00), ("p6", 82.10, 83.56, 1.00),
          ("p7a", 83.57, 88.55, 1.00), ("p7b", 88.72, 89.82, 1.00), ("p7c", 90.33, 91.45, 1.08),
          ("p7d", 99.55, 103.15, 1.12), ("p8", 157.80, 159.53, 1.00), ("l1", 159.50, 163.80, 1.00),
          ("l2", 165.50, 168.15, 1.00), ("p9a", 170.02, 171.80, 1.12), ("p9b", 173.57, 174.90, 1.15)]
B.BIG.clear()
B.BIG["BORING"] = 1.15     # Eoin 12 Nov: nearly the full width, behind him (~92% rendered)
RISER = os.path.join(HERE, "assets/riser.wav"); FLASH = os.path.join(HERE, "assets/flash.wav")
TICK = os.path.join(HERE, "assets/tick.wav"); MUSIC = os.path.join(HERE, "assets/music_win_again.wav")
GAP_MIN, PAD, PAD_END, MIN_N = 0.16, 0.06, 0.10, 6
BLACK = (0.02, 0.02, 0.02)
# opener (raw s): inset on "my content", 7 fast cuts on "lost all momentum", BORING payoff on "and became boring",
# then his face on "when I stopped doing this one thing", strobe into p2
OPEN_INSET = ("C4389", 11.4)
OPEN_A, RAPID_END, FACE_A = 14.96, 16.17, 17.45
# Eoin 12 Nov: "lost", "all", "momentum" a beat each, let the shots breathe
OPEN_BEATS = [("C4394", 9.0, 14.96), ("C4092", 6.0, 15.25), ("C4438", 9.5, 15.53)]
OPENER_PX, HOOK_FACE_PX = 140, 90           # Eoin 11 Nov: bigger captions in the beginning
# cutaways: (seg, raw from, raw to, clip, clip in, payoff (WORD, lead, tail, subject x-range, rgb) | None)
CUTS = [("hook", 16.17, 17.45, "C2354", 2.0, ("BORING", "AND BECAME", None, (0.12, 0.62), WHITE)),   # hands over face, slow zoom-out
        ("p3a", 27.80, 29.70, "C4418", 0.3, ("NEW YORK", "WHEN I WAS IN", None, None, WHITE)),
        ("p3c", 30.70, 32.16, "C4389", 22.0, None),          # Ibiza removed (Eoin 12 Nov)
        ("p3c", 32.16, 34.15, "C4286", 15.0, None),
        ("p4", 47.26, 49.00, "C4430", 3.3, None),
        ("p7a", 86.70, 87.88, "C6997", 143 / FPS, None),    # Eoin's v6 in-point
        ("p7d", 101.73, ("p8", 158.10), "C7045", 1.6, ("FORGETTABLE", "PRETTY", None, None, WHITE))]
INK_SHOTS, LUMA_SHOTS = set(), {"BORING"}   # silhouette at the window: luma key puts the word behind him
SLOW_OUT = {"BORING"}
# emphasis montage (Eoin 12 Nov: "emphasize the all day part"): time passing at the desk under one big word
MONTAGE = [("p7a", 87.88, 88.55, "ALL DAY", [("C8317", 2.0), ("C8319", 8.0), ("C6998", 20.0)])]            # payoff shots that zoom OUT slowly instead of pushing in
# word cards cut on measured onsets; each group alternates black/white starting black
LISTS = [[("p6", 82.10, "DOCUMENT"), ("p6", 82.79, "DON'T CREATE")]]
# list words on b-roll (Eoin 12 Nov): big white word centred on the shot, cut on the measured onset
LIST_BROLL = [("l1", 159.65, "MESSAGES", "C8582", 4.0), ("l1", 161.43, "LOOMS", "C8584", 2.0),
              ("l1", 162.68, "MEETINGS", "C8227", 0.5), ("l2", 165.78, "WHAT WORKED", "C8620", 6.0),
              ("l2", 166.22, "WHAT DIDN'T", "C8320", 1.5), ("l2", 166.93, "WHAT WENT WRONG", "C3918", 7.0)]
# caption style per line, judged from the refs (Eoin 12 Nov: mix it up, bigger, never blocking him)
SEG_STYLE = {"hook": "chest_big", "p2": "stack", "p3a": "chest", "p3c": "chest", "p3b": "chest", "p4": "wall", "p5a": "chest",
             "p5b": "chest", "p5c": "chest", "p7a": "wall", "p7b": "stack", "p7c": "stack", "p7d": "chest",
             "p8": "stack", "p9a": "wall"}
ACCENT = {"UNFOLDING", "WISDOM"}   # serif italic accent words, like the refs' "framing" / "Image"
END_PAYOFF = ("p9b", 174.19, "HAPPENING", "SHOW IT", None)
STROBE_INTO, BLOWOUT_INTO = "p2", "p9a"
END_OUT = 5241 / FPS            # his v6 out-point on the last clip
WAV = os.path.join(HERE, "tx/C8577_00453759.wav")


def env():
    w = wave.open(WAV); sr = w.getframerate()
    a = array.array("h", w.readframes(w.getnframes())); hop = sr // 50          # 20 ms
    return [20 * math.log10(math.sqrt(sum(x * x for x in a[i:i + hop]) / hop) / 32768 + 1e-9) for i in range(0, len(a) - hop, hop)]


_E = None
def onset(t):
    """measured onset near a Whisper time: the biggest 20ms energy rise within -0.2..+0.2s"""
    global _E
    _E = _E or env()
    i0, i1 = int((t - 0.2) * 50), int((t + 0.2) * 50)
    best = max(range(max(i0, 1), i1), key=lambda i: _E[i] - _E[i - 1])
    return best / 50


def plan():
    """pauses = anything 22 dB under the line's own speech level (p90) for >= 0.16s: room noise and breaths go too"""
    E = env()
    pieces, rec = [], 0
    for nm, a, b, z in B.SEGS:
        d = E[int(a * 50):int(b * 50)]
        pk = sorted(d)[int(len(d) * 0.9)]
        q = [v < pk - 22 for v in d] + [True]
        runs, st = [], None
        for i, x in enumerate(q):
            if not x and st is None:
                st = i
            if x and st is not None:
                runs.append((a + st / 50, a + i / 50)); st = None
        # merge speech runs separated by < GAP_MIN, pad each kept run
        keep = []
        for r0, r1 in runs:
            if keep and r0 - keep[-1][1] < GAP_MIN:
                keep[-1][1] = r1
            else:
                keep.append([r0, r1])
        for i_, (r0, r1) in enumerate(keep):
            nxt0 = keep[i_ + 1][0] - PAD if i_ + 1 < len(keep) else b
            r0, r1 = max(a, r0 - PAD), min(b, r1 + PAD_END, nxt0)
            if fr(r1) - fr(r0) >= MIN_N:                # no stray frames
                pieces.append({"g": nm, "a": r0, "b": r1, "z": z})
    pieces[-1]["b"] = max(pieces[-1]["b"], END_OUT)       # Eoin's longer last clip (v6): never trim the ending early
    for p in pieces:
        p["n"] = fr(p["b"]) - fr(p["a"]); p["rec"] = rec; rec += p["n"]
        p["k"] = [q for q in pieces if q["g"] == p["g"]].index(p)
    return pieces, rec


def t_of(P, g, s):
    ps = [p for p in P if p["g"] == g]
    for p in ps:
        if p["a"] <= s < p["b"]:
            return p["rec"] + fr(s) - fr(p["a"])
        if s < p["a"]:
            return p["rec"]
    return ps[-1]["rec"] + ps[-1]["n"]


def g_span(P, g):
    ps = [p for p in P if p["g"] == g]
    return ps[0]["rec"], ps[-1]["rec"] + ps[-1]["n"]


def zoom_out_at(it, f_local, z_from=1.22, frames=10):
    """dynamic zoom-out on the return to Eoin, slow and never fully stops (Eoin 11 Nov):
    z_from -> 1 across `frames` (the rest of the shot), 60% ease-out + 40% linear"""
    c = B.comp_of(it); mi, mo = c.FindTool("MediaIn1"), c.FindTool("MediaOut1")
    g0 = B.RS
    feed = mo.Input.GetConnectedOutput().GetTool()
    c.Lock()
    nm = f"ZoomBack{len([x for x in c.GetToolList().values() if x.Name.startswith('ZoomBack')])}"
    x = c.AddTool("Transform", -32768, -32768); x.SetAttrs({"TOOLS_Name": nm})
    # sits right after MediaIn so text added later (end payoff) is unaffected
    x.Input = mi.Output
    for t in c.GetToolList().values():
        if t.Name != nm and t.Name != "MediaIn1":
            for inp in t.GetInputList().values():
                try:
                    if inp.GetConnectedOutput() and inp.GetConnectedOutput().GetTool().Name == "MediaIn1":
                        inp.ConnectTo(x.Output)
                except Exception:
                    pass
    if feed.Name == "MediaIn1":
        mo.Input = x.Output
    s0 = g0 + f_local
    u = f"min(max((time-{s0})/{frames},0),1)"
    x.Size.SetExpression(f"iif(time<{s0}, 1, 1+{z_from - 1}*(1-(0.6*(1-(1-{u})^3)+0.4*{u})))")
    c.Unlock()


def seal(t, mp, carrier, pool, jd):
    """close every 1-3 frame hole Resolve's rounding leaves: on V2/V3 (a flash of A-roll between covers) and on V4
    (a blank frame between captions), by extending the cover/caption before the hole"""
    t0 = t.GetStartFrame()
    import shutil
    def lst(tr):
        return sorted(t.GetItemListInTrack("video", tr) or [], key=lambda x: x.GetStart())
    n = 0
    for trs in ((2, 3), (4,)):
        its = sorted([x for tr in trs for x in lst(tr)], key=lambda x: x.GetStart())
        for a, b in zip(its, its[1:]):
            g = b.GetStart() - a.GetEnd()
            if not 0 < g <= 3:
                continue
            tr = a.GetTrackTypeAndIndex()[1]
            mpi = a.GetMediaPoolItem()
            if mpi and mpi.GetName() != carrier.GetName():                        # media clip: continue its frames
                fps = float(mpi.GetClipProperty("FPS") or FPS) or FPS
                src_end = a.GetRightOffset() if False else None
                start_src = a.GetSourceStartFrame() + int(round(a.GetDuration() * fps / FPS))
                res = mp.AppendToTimeline([{"mediaPoolItem": mpi, "startFrame": start_src, "endFrame": start_src + max(1, int(round(g * fps / FPS))),
                                            "trackIndex": tr, "recordFrame": a.GetEnd(), "mediaType": 1}])
                n += bool(res)
            else:                                                                   # carrier: duplicate its comp
                comp = os.path.join(jd, f"seal_{a.GetStart()}.comp")
                try:
                    a.ExportFusionComp(comp, 1)
                except Exception:
                    continue
                fil = B.place(mp, t, carrier, a.GetEnd(), g, tr)
                if fil and os.path.exists(comp):
                    fil.ImportFusionComp(comp)
                    nm = fil.GetFusionCompNameList() or []
                    if len(nm) > 1:
                        fil.LoadFusionCompByName(nm[-1])
                        for x in nm[:-1]:
                            fil.DeleteFusionCompByName(x)
                    n += 1
    print("sealed holes:", n)



def inset_blur_zoom(it, end_size=0.80, blur_s=0.8):
    """opener inset (Eoin 12 Nov): quick blur-in (<= 1s) + a ramped zoom-out that never goes under 80%"""
    c = B.comp_of(it); mi, mo = c.FindTool("MediaIn1"), c.FindTool("MediaOut1")
    g0 = B.RS; n = max(it.GetDuration() - 1, 1)
    c.Lock()
    bl = c.AddTool("Blur", -32768, -32768); bl.SetAttrs({"TOOLS_Name": "BlurIn"}); bl.Input = mi.Output
    bf = min(int(round(blur_s * FPS)), n)
    bl.XBlurSize.SetExpression(f"24*(1-min(max((time-{g0})/{bf},0),1))^2")
    x = c.AddTool("Transform", -32768, -32768); x.SetAttrs({"TOOLS_Name": "ZoomOut"}); x.Input = bl.Output
    u = f"min(max((time-{g0})/{n},0),1)"
    x.Size.SetExpression(f"1-{1 - end_size}*(1-(1-{u})^3)")
    mo.Input = x.Output
    c.Unlock()


def push_cont(it, amt=0.10):
    """cutaway push that starts on the first frame and never stops (Eoin 12 Nov: more continuous)"""
    c = B.comp_of(it); mi, mo = c.FindTool("MediaIn1"), c.FindTool("MediaOut1")
    g0 = B.RS; d = max(it.GetDuration() - 1, 1)
    c.Lock()
    x = c.AddTool("Transform", -32768, -32768); x.SetAttrs({"TOOLS_Name": "Push"}); x.Input = mi.Output
    u = f"min(max((time-{g0})/{d},0),1)"
    x.Size.SetExpression(f"1+{amt}*(0.25*(1-(1-{u})^2)+0.75*{u})")
    mo.Input = x.Output
    c.Unlock()


def didot_w(s, px):
    from PIL import ImageFont
    f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Didot.ttc", 100, index=1)
    return f.getlength(s) * px / 100


def cap_comp(n, items, halo):
    """caption overlay: items = [(text, x, y, px, rgb, font, style)]"""
    from fusion import L
    B.setup(); c = B.Comp(n); out = c.canvas()
    for i, (s_, x, y, px, rgb, font, style) in enumerate(items):
        sp = 0.97 if font == HN else 1.0
        if halo:
            sh = c.text(f"T{i}H", s_, x, y, px, rgb=(0, 0, 0), font=font, style=style, spacing=sp)
            bl = c.tool(f"T{i}HB", "Blur", {"Input": L(sh), "XBlurSize": max(6.0, px / 10)})
            out = c.merge(f"T{i}HM", out, bl, blend=0.8)
        out = c.merge(f"T{i}M", out, c.text(f"T{i}", s_, x, y, px, rgb=rgb, font=font, style=style, spacing=sp))
    return c.text_out(out)


def cap_items(style, word, prefix):
    """returns (items, check box) for one caption beat in the line's style"""
    if style == "chest_big" or style == "chest":
        px = 90 if style == "chest_big" else 72
        px = min(px, 0.60 * TW / max(B.hn_width(word, 1), 1e-6))
        x, y = 0.46 * TW, 0.80 * TH
        w = B.hn_width(word, px)
        return [(word, x, y, px, WHITE, HN, "Bold")], (x - w / 2, y - px / 2, x + w / 2, y + px / 2)
    if style == "wall":
        px = 64; w = B.hn_width(word, px); x = max(0.20 * TW, 0.05 * TW + w / 2); y = 0.24 * TH
        return [(word, x, y, px, WHITE, HN, "Bold")], (x - w / 2, y - px / 2, x + w / 2, y + px / 2)
    # stack: the line so far small on top, the current word big under it, in the wall space left of his head
    x, y = 0.205 * TW, 0.30 * TH
    if word in ACCENT:
        txt = word.lower(); px = min(150, 0.30 * TW / max(didot_w(txt, 1), 1e-6)); font, st = "Didot", "Italic"
        w = didot_w(txt, px)
    else:
        txt = word; px = min(92, 0.30 * TW / max(B.hn_width(word, 1), 1e-6)); font, st = HN, "Bold"
        w = B.hn_width(word, px)
    its = [(txt, x, y, px, WHITE, font, st)]
    if prefix:
        ppx = min(34, 0.30 * TW / max(B.hn_width(prefix, 1), 1e-6))
        its.append((prefix, x, y - px * 0.62 - ppx * 0.5, ppx, WHITE, HN, "Bold"))
    return its, (x - w / 2, y - px / 2 - 40, x + w / 2, y + px / 2)


def first(W, word, lo, hi):
    w0 = word.split()[0]
    return next((w[1] for w in W if w[0].strip(".,?!").upper() == w0 and lo <= w[1] <= hi), None)


def build():
    P, total = plan()
    r = B.connect(); pm = r.GetProjectManager(); p = pm.GetCurrentProject()
    print("project:", p.GetName(), "| pieces:", len(P), "| seconds:", round(total / FPS, 2))
    assert p.GetName() == "content got boring", "open the 'content got boring' project first"
    mp = p.GetMediaPool(); root = mp.GetRootFolder()
    sub = lambda nm: next((f for f in root.GetSubFolderList() or [] if f.GetName() == nm), None) or mp.AddSubFolder(root, nm)
    pool = {}
    for k, path in SRC.items():
        pool[k] = B.find_clip(root, os.path.basename(path))
        if not pool[k]:
            mp.SetCurrentFolder(sub("04 B-roll")); pool[k] = mp.ImportMedia([path])[0]
    tick = B.find_clip(root, "tick.wav"); music = B.find_clip(root, os.path.basename(MUSIC))
    flash = B.find_clip(root, "flash.wav")
    carrier = B.find_clip(root, "Smooth Word Up")
    if not carrier:
        mp.SetCurrentFolder(root); mp.ImportFolderFromFile(B.MTP_DRB); carrier = B.find_clip(root, "Smooth Word Up")
    assert carrier, "MTP carrier missing"
    mp.SetCurrentFolder(sub("timelines"))
    taken = {p.GetTimelineByIndex(i).GetName() for i in range(1, p.GetTimelineCount() + 1)}
    v = 1
    while TL_NAME.format(v) in taken:
        v += 1
    t = mp.CreateEmptyTimeline(TL_NAME.format(v)); p.SetCurrentTimeline(t)
    t.SetSetting("useCustomSettings", "1")
    t.SetSetting("timelineResolutionWidth", str(TW)); t.SetSetting("timelineResolutionHeight", str(TH))
    t.SetSetting("timelineInputResMismatchBehavior", "scaleToFill")
    t0 = t.GetStartFrame()
    for _ in range(3):
        t.AddTrack("video")
    for _ in range(4):
        t.AddTrack("audio", "stereo")
    for i, nm in enumerate(["aroll", "cutaways+cards", "inset", "text"], 1):
        t.SetTrackName("video", i, nm)
    jd = os.path.join(HERE, "comps"); os.makedirs(jd, exist_ok=True)
    W = B.W_ALL
    v1 = []
    for pc in P:
        it = B.append(mp, pool["A"], pc["a"], pc["n"], 1, t0 + pc["rec"])
        z = pc["z"] * (1.08 if pc["k"] % 2 else 1.0)
        if z != 1.0:
            it.SetProperty({"ZoomX": z, "ZoomY": z})
        v1.append(it)
    hs, he = g_span(P, "hook")
    # opener: canvas + inset, then the fast cuts
    ib = t_of(P, "hook", OPEN_A) - hs
    cv = B.place(mp, t, carrier, t0 + hs, ib, 2)
    B.attach(cv, B.solid_comp(cv.GetDuration(), B.CANVAS), f"{jd}/canvas_open.comp")
    ins = B.append(mp, pool[OPEN_INSET[0]], OPEN_INSET[1], ib, 3, t0 + hs, 1)
    inset_blur_zoom(ins)
    edges = [ib] + [t_of(P, "hook", s_) - hs for _k, _c, s_ in OPEN_BEATS[1:]] + [t_of(P, "hook", RAPID_END) - hs]
    for i, (k, cin, _s) in enumerate(OPEN_BEATS):
        it_ = B.append(mp, pool[k], cin, edges[i + 1] - edges[i], 2, t0 + hs + edges[i], 1)
        it_.SetClipColor("Orange"); push_cont(it_, 0.06)
    rapid_f = t_of(P, "hook", RAPID_END)
    face_f = t_of(P, "hook", FACE_A)
    # cutaways + payoffs
    covers, plain = [], []
    ticks, n_txt = [], 0
    for seg, a_s, b_s, k, cin, po in CUTS:
        if isinstance(b_s, tuple):                      # payoff held into the next line so the word fully lands
            b = t_of(P, *b_s); b_s = max(p_["b"] for p_ in P if p_["g"] == seg)
        else:
            b = min(t_of(P, seg, b_s), g_span(P, seg)[1])
        a = t_of(P, seg, a_s)
        if b - a < 3:
            print("skip tiny cutaway", seg, k); continue
        it = B.append(mp, pool[k], cin, b - a, 2, t0 + a, 1)
        if po:
            wt = first(W, po[0], a_s - 0.3, b_s + 0.5) or a_s
            B.payoff_into(it, po[0], po[1], po[2], po[3], INK if po[0] in INK_SHOTS else po[4], key=None if po[0] in INK_SHOTS else k,
                          sec=cin + (b - a) / FPS * 0.7, word_f=max(0, t_of(P, seg, wt) - a), tail_f=0,
                          cut="luma" if po[0] in LUMA_SHOTS else "depth",
                          push_curve="linear" if seg == "hook" else "ease", push=po[0] not in SLOW_OUT)
            if po[0] in SLOW_OUT:
                zoom_out_at(it, 0, z_from=1.16, frames=max(b - a - 1, 20))
            ticks.append(t_of(P, seg, wt) - 4)
        else:
            push_cont(it); plain.append((a, b))
        it.SetClipColor("Teal"); covers.append((a, b))
    # word cards
    for grp in LISTS:
        segs = [g for g, _o, _w in grp]
        la, lb = g_span(P, segs[0])[0], g_span(P, segs[-1])[1]
        starts = [t_of(P, g, onset(on)) for g, on, _w in grp]
        starts[0] = la; starts.append(lb)
        for i, (g, _on, word) in enumerate(grp):
            a, b = starts[i], starts[i + 1]
            if b - a < 2:
                print("skip card", word); continue
            bg, fg = (BLACK, WHITE) if i % 2 == 0 else (WHITE, BLACK)
            px = min(150, 0.80 * TW / max(B.hn_width(word, 1), 1e-6))
            B.setup()
            c = B.Comp(b - a)
            out = c.merge("WM", c.solid("BG", bg), c.text("W", word, TW / 2, TH / 2, px, rgb=fg, font=HN, style="Bold", spacing=0.97))
            it = B.place(mp, t, carrier, t0 + a, b - a, 2)
            B.attach(it, c.text_out(out), f"{jd}/card_{segs[0]}_{i}.comp"); it.SetClipColor("Pink")
            ticks.append(a); n_txt += 1
        covers.append((la, lb))
    # emphasis montages: quick beats under one big centred word
    for seg, a_s, b_s, word, shots in MONTAGE:
        a, b = t_of(P, seg, onset(a_s)), min(t_of(P, seg, b_s), g_span(P, seg)[1])
        edges = [a + round(i * (b - a) / len(shots)) for i in range(len(shots))] + [b]
        for i, (k, cin) in enumerate(shots):
            it = B.append(mp, pool[k], cin, edges[i + 1] - edges[i], 2, t0 + edges[i], 1)
            push_cont(it, 0.06); it.SetClipColor("Orange")
        px = min(170, 0.70 * TW / max(B.hn_width(word, 1), 1e-6))
        cw = B.place(mp, t, carrier, t0 + a, b - a, 4)
        if cw:
            B.attach(cw, cap_comp(cw.GetDuration(), [(word, TW / 2, TH / 2, px, WHITE, HN, "Bold")], True), f"{jd}/mont_{seg}.comp")
        ticks.append(a); n_txt += 1
        covers.append((a, b))
    # list words on b-roll
    lsegs = sorted({g for g, *_ in LIST_BROLL}, key=lambda g: g_span(P, g)[0])
    la, lb = g_span(P, lsegs[0])[0], g_span(P, lsegs[-1])[1]
    starts = [t_of(P, g, onset(on)) for g, on, *_ in LIST_BROLL]
    starts[0] = la; starts.append(lb)
    for i, (g, _on, word, k, cin) in enumerate(LIST_BROLL):
        a, b = starts[i], starts[i + 1]
        if b - a < 2:
            print("skip list word", word); continue
        it = B.append(mp, pool[k], cin, b - a, 2, t0 + a, 1); push_cont(it, 0.08); it.SetClipColor("Pink")
        px = min(150, 0.80 * TW / max(B.hn_width(word, 1), 1e-6))
        B.pick(k, cin + 0.3, (TW / 2 - B.hn_width(word, px) / 2, TH / 2 - px / 2, TW / 2 + B.hn_width(word, px) / 2, TH / 2 + px / 2), word)
        cw = B.place(mp, t, carrier, t0 + a, b - a, 4)
        if cw:
            B.attach(cw, cap_comp(cw.GetDuration(), [(word, TW / 2, TH / 2, px, WHITE, HN, "Bold")], True), f"{jd}/lw_{i}.comp")
        ticks.append(a); n_txt += 1
    covers.append((la, lb))
    # end payoff behind his head on the last piece
    seg, at, word, lead, tail = END_PAYOFF
    pe = [i for i, pc in enumerate(P) if pc["g"] == seg]
    ite, pce = v1[pe[-1]], P[pe[-1]]
    wt = first(W, word, at - 0.5, at + 0.8) or at
    wf = max(0, t_of(P, seg, wt) - pce["rec"])
    B.payoff_into(ite, word, lead, tail, (0.25, 0.62), WHITE, key="A", sec=wt + 0.5, word_f=wf, tail_f=0, push=False)
    ticks.append(t_of(P, seg, wt) - 4)
    end_cover = (pce["rec"], pce["rec"] + pce["n"])
    # strobe + blow-out
    i2 = next(i for i, pc in enumerate(P) if pc["g"] == STROBE_INTO)
    T = P[i2]["rec"]
    B.strobe(v1[i2], [T, T + 2], T)
    B.blowout(v1[next(i for i, pc in enumerate(P) if pc["g"] == BLOWOUT_INTO)])
    # zoom-out every time it comes back to him
    backs = sorted({b for a, b in covers} | {he, face_f})
    n_back = 0
    for f in backs:
        j = next((i for i, pc in enumerate(P) if pc["rec"] <= f < pc["rec"] + pc["n"]), None)
        if j is None or any(a <= f < b for a, b in covers):
            continue
        nxt = min([a for a, b in covers if a > f] + [P[j]["rec"] + P[j]["n"]])
        zoom_out_at(v1[j], f - P[j]["rec"], frames=max(20, nxt - f)); n_back += 1
    # captions: big centred words over the opener, bigger wall captions on the hook face, locked 46px after
    cover_all = [c_ for c_ in covers if c_ not in plain] + [end_cover]
    for nm, a_, b_, z in B.SEGS:
        ws = [w for w in W if a_ <= w[1] < b_ - 0.05 and any(p_["g"] == nm and p_["a"] - 0.08 <= w[1] < p_["b"] for p_ in P)]
        carry, c0f = "", None
        for j, (w, ws_, we) in enumerate(ws):
            f0 = max(t_of(P, nm, ws_), g_span(P, nm)[0])
            f1 = t_of(P, nm, ws[j + 1][1]) if j + 1 < len(ws) else g_span(P, nm)[1]
            word_ = (carry + w.strip(".,?!").upper()).strip()
            if c0f is not None:
                f0 = c0f
            if j == 0:                        # first word: caption from the cut, not from Whisper's late onset
                f0 = g_span(P, nm)[0]
            opener = nm == "hook" and f0 < rapid_f
            if opener:
                f1 = min(f1, rapid_f)
            if f1 - f0 < 4 and j + 1 < len(ws) and len(word_) < 12:   # DTW stacked words: show them together
                carry, c0f = word_ + " ", f0
                continue
            carry, c0f = "", None
            nxt_c = [c0 for c0, c1 in cover_all if f0 < c0 < f1]
            if nxt_c and not opener:
                f1 = min(nxt_c)                   # never run a caption into a cover/montage that has its own text
            if f1 - f0 < 2:
                continue
            if not opener:
                hit = next((c1 for c0, c1 in cover_all if c0 <= f0 < c1), None)
                if hit is not None:
                    if f1 - hit < 3:          # word is under a cover: skip
                        continue
                    f0 = hit                  # word runs past the cover: caption from the return
            it = B.place(mp, t, carrier, t0 + f0, f1 - f0, 4)
            if not it:
                continue
            on_plain = any(a <= f0 < b for a, b in plain)
            if opener:
                items, halo = [(word_, 0.5 * TW, 0.50 * TH, OPENER_PX, WHITE, HN, "Bold")], True
            else:
                st_ = SEG_STYLE.get(nm, "wall")
                j0 = j - (len(word_.split()) - 1)            # first word of a merged caption
                prev = [x_[0].strip(".,?!").upper() for x_ in ws[max(0, j0 - 4):j0]] if st_ == "stack" else []
                prefix = " ".join(prev)
                items, box = cap_items(st_, word_, prefix)
                B.pick("A", ws_, box, word_)
                halo = B.REPORT[-1][3] == "halo" or on_plain
            B.attach(it, cap_comp(it.GetDuration(), items, halo), f"{jd}/cap_{nm}_{j}.comp")
            short = (f1 - f0) - it.GetDuration()
            if short > 0:
                fil = B.place(mp, t, carrier, t0 + f0 + it.GetDuration(), short, 4)
                if fil:
                    B.attach(fil, cap_comp(fil.GetDuration(), items, halo), f"{jd}/cap_{nm}_{j}_fill.comp")
            ticks.append(f0); n_txt += 1
    n_t = 0
    for f in sorted(set(ticks)):
        if B.append(mp, tick, 0, fr(0.15), 2, t0 + max(f, 0), 2):
            n_t += 1
    B.append(mp, music, 0, total, 3, t0, 2)
    # riser from frame 1 into the strobe, flash on it
    L = T / FPS
    srcr = "/Volumes/Extreme SSD/editiing assets/5. Sound FX/Cinematic Sound Library/6. RISERS/_ Riser 4.wav"
    peak_at = 4.6
    tempo = max(0.5, min(2.0, (peak_at - 0.2) / L)) if L > peak_at - 0.2 else 1.0
    st = max(0.0, peak_at - L * tempo)
    import subprocess
    rf = os.path.join(HERE, "assets/riser_long.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(st), "-t", str(L * tempo + 0.05), "-i", srcr, "-af",
                    f"atempo={tempo},acompressor=threshold=-38dB:ratio=5:attack=20:release=200:makeup=6,afade=t=in:d=0.12",
                    "-ar", "48000", rf + ".tmp.wav"], check=True)
    pk = float(subprocess.run(["ffmpeg", "-nostats", "-i", rf + ".tmp.wav", "-af", "volumedetect", "-f", "null", "-"],
                              capture_output=True, text=True).stderr.split("max_volume:")[1].split("dB")[0])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", rf + ".tmp.wav", "-af", f"volume={-30 - pk}dB", rf], check=True)
    os.remove(rf + ".tmp.wav")
    mp.SetCurrentFolder(sub("05 Audio"))
    riser = B.find_clip(root, "riser_long.wav") or mp.ImportMedia([rf])[0]
    B.append(mp, riser, 0, T, 4, t0, 2)
    B.append(mp, flash, 0, fr(0.66), 5, t0 + T - fr(0.30), 2)
    seal(t, mp, carrier, pool, jd)
    B.refresh(t)
    pm.SaveProject()
    print(json.dumps({"timeline": t.GetName(), "seconds": round(total / FPS, 2), "pieces": len(P), "text": n_txt,
                      "ticks": n_t, "zoom_backs": n_back, "readable": B.REPORT}))
    json.dump({"pieces": P}, open(os.path.join(HERE, "plan2.json"), "w"), indent=0)


if __name__ == "__main__":
    if sys.argv[1:2] == ["plan"] or "--plan" in sys.argv:
        pass
    build()
