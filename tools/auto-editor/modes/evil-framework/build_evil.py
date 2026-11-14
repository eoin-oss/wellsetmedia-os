"""evil-framework mode: Tristan's (DO NOT USE FOR EVIL) framework reel, built natively in Resolve.
V1 the raw take in pieces (wide 1.0 on the hook open + step titles, medium 1.1 base, 1.3 punch-in when the cards go
off), V2 the held card pairs (Fusion: Loader -> B&W grade -> masked Merge at hand height), V3 the top layer (hook top
card + blue tag, step titles), V4 word-by-word captions (grey line, white write-on as each word is said).
Card timings: clients/kyle-ritchie/content/evil-overlays/breakdown/data.py; card images: cards.py.
Usage: python3 build_evil.py v4 [v1 v3]   (current project; one timeline per take)"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
AE = os.path.abspath(os.path.join(HERE, "../.."))
sys.path.insert(0, os.path.join(AE, "engine"))
BD = os.path.expanduser("$WSM_HOME/clients/kyle-ritchie/content/evil-overlays")
sys.path.insert(0, os.path.join(BD, "breakdown"))
sys.path.insert(0, HERE)
from PIL import Image
import fusion
from fusion import Comp, A, P, L, Fu, Raw, q
from resolve import connect, find_clip
from data import KYLE
from cards import CARDS

W, H, FPS = 1080, 1920, 24
fusion.W, fusion.H = W, H
fusion.TEXT_DIV = 1450.0 * 1080 / 1920
ASSETS = os.path.join(AE, "jobs/evil-assets/cards")
JOB = os.path.join(AE, "jobs/evil-framework")
MTP_DRB = "/Volumes/Extreme SSD/personal brand directory/asssets/Motiontext-pro-v1/davinci-resolve-version21+/MotionText Pro V1.drb"
SRC = {"v1": "0C84FE4C-C4D7-4ED0-B820-EEC75AE24B28", "v3": "A304F19A-0097-437D-BD53-D8FBBAE513A3", "v4": "E27165F1-B1D2-402B-BD7A-EC79E5690DCD"}
WORDS = {"v1": "w1", "v3": "w3", "v4": "w4"}
FIX = {"v1": [("Labet", "Libet"), ("pill", "pull")], "v3": [("Klons", "Klontz"), ("he calls don't", "like us don't")], "v4": []}
TITLES = {
    "v4": ["THE\nBASELINE", "THE\nSHIFT", "THE\nCLUSTER"],
    "v1": ["NAME\nIT", "USE THE\nGAP", "TRACE IT\nBACK"],
    "v3": ["FIND THE\nLINE", "FIND THE\nMOMENT", "CATCH THE\nFLINCH"],
}
ACCENT = {"flushed", "name_tag"}  # keep their colour (Tristan's red NO)
RED = (0.9, 0.12, 0.12)
FONT = "Avenir Next"                           # closest installed face to Tristan's Montserrat
FONT_FILE = "/System/Library/Fonts/Avenir Next.ttc"  # index 0 = Bold, for measuring
ZOOM = {"wide": 1.0, "med": 1.1, "punch": 1.3}
CAP_Y, CAP_PX = 0.605 * H, 50                  # captions between chin and cards
CARD_Y = 0.775 * H                             # card centre (hand height)
CARD_W = min(0.36 * W, (CARD_Y - (CAP_Y + CAP_PX)) * 2 * 3 / 4)  # shrink so a card never reaches the captions
PAIR_X = (W / 2 - CARD_W / 2 - 12, W / 2 + CARD_W / 2 + 12)
MUSIC = {"path": "/Volumes/Extreme SSD/editiing assets/music/Every Living Breathing Moment.mp3", "start": 0.83, "gain_db": -23.0}
VOICE_GAIN_DB = 4.0                            # Kyle's takes sit at -18.9 LUFS, Tristan's reels at -14.5


# ---- words + timing --------------------------------------------------------------------------------------------
def words(take):
    d = json.load(open(os.path.join(BD, "raw", WORDS[take] + ".json")))["transcription"]
    out = []
    for s in d:
        t = s["text"].strip()
        if not t or t.startswith("["):
            continue
        out.append({"w": t, "s": s["offsets"]["from"] / 1000, "e": s["offsets"]["to"] / 1000})
    # whisper mishears: fix on the word sequence
    for a, b in FIX[take]:
        aw, bw = a.split(), b.split()
        for i in range(len(out) - len(aw) + 1):
            if [re.sub(r"[^\w']", "", x["w"]) for x in out[i:i + len(aw)]] == aw:
                for j, nw in enumerate(bw):
                    tail = re.sub(r"[\w']", "", out[i + j]["w"])
                    out[i + j]["w"] = nw + tail
    return out


def snap(t, W_, tol=0.6):
    """a planned second -> the nearest word onset, led by one frame"""
    if t <= 0.05:
        return 0.0
    best = min(W_, key=lambda w: abs(w["s"] - t))
    return max(0.0, (best["s"] if abs(best["s"] - t) <= tol else t) - 1 / FPS)


def chunks(W_):
    """2 to 4 words: break on punctuation or a pause once there are 2, never past 4 words / 24 characters"""
    out, cur = [], []
    for i, w in enumerate(W_):
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        nxt = W_[i + 1] if i + 1 < len(W_) else None
        if not nxt or len(cur) >= 4 or len(txt + " " + nxt["w"]) > 24:
            out.append(cur); cur = []
        elif len(cur) >= 2 and (re.search(r"[.,?!]$", w["w"]) or nxt["s"] - w["e"] > 0.35):
            out.append(cur); cur = []
    # a lone word joins its neighbour (unless that would pass 4 words)
    fixed = []
    for ch in out:
        if len(ch) == 1 and fixed and len(fixed[-1]) < 4 and ch[0]["s"] - fixed[-1][-1]["e"] < 0.6:
            fixed[-1] = fixed[-1] + ch
        else:
            fixed.append(ch)
    for k in range(len(fixed) - 1):
        if len(fixed[k]) == 1 and len(fixed[k + 1]) < 4:
            fixed[k + 1] = fixed[k] + fixed[k + 1]; fixed[k] = []
    return [c for c in fixed if c]


def fit_px(lines, width, cap):
    """font px so the longest line spans `width` (measured on Avenir Next Bold)"""
    from PIL import ImageFont
    f = ImageFont.truetype(FONT_FILE, 100, index=0)
    longest = max(f.getlength(l) for l in lines)
    return min(cap, 100 * width / longest)


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


def put_image(c, bg, key, cx, cy, cw, ch, blend=None, dim=1.0, path=None):
    """one card: image fills a cw x ch rect at (cx, cy), B&W unless accent"""
    path = path or os.path.join(ASSETS, key.replace("K:", "K_") + ".jpg")
    pw, ph = Image.open(path).size
    n = re.sub(r"\W", "", key) + str(len(c.tools))
    ld = loader(c, "L" + n, path)
    sat = 1.0 if key in ACCENT else 0.0
    g = c.tool("G" + n, "BrightnessContrast", {"Input": L(ld), "Saturation": sat, "Contrast": 0.18, "Gain": dim})
    m = c.rect("M" + n, cx, cy, cw, ch)
    mg = c.merge("C" + n, bg, g, center=P(cx, cy), size=max(cw / pw, ch / ph), blend=blend)
    masked(c, mg, m)
    return mg


def outlined_text(c, bg, name, s, x, y, size, rgb=(1, 1, 1), style="Bold", end=None, alpha=1.0, spacing=1.0, line=0.06):
    """Text+ with a thin black outline (shading element 2)"""
    tx = c.text(name, s, x, y, size, rgb=rgb, a=alpha, style=style, font=FONT, end=end, spacing=spacing)
    extra = (f"Enabled2 = Input {{ Value = 1, }},\n\t\t\t\tThickness2 = Input {{ Value = {line}, }},\n\t\t\t\t"
             f"Red2 = Input {{ Value = 0, }},\n\t\t\t\tGreen2 = Input {{ Value = 0, }},\n\t\t\t\tBlue2 = Input {{ Value = 0, }},\n\t\t\t\t"
             f"Alpha2 = Input {{ Value = {alpha}, }},\n\t\t\t\t")
    for k, (n, t) in enumerate(c.tools):
        if n == tx:
            c.tools[k] = (n, t.replace("Inputs = {\n\t\t\t\t", "Inputs = {\n\t\t\t\t" + extra, 1))
    return c.merge(name + "M", bg, tx)


def card_comp(spec, n, a_sec, title=None, end_word=None):
    """spec: list of card keys ((key, join_sec) for a late second card) or a dict for hook/end"""
    c = Comp(n)
    bg = c.canvas()
    ch = CARD_W * 4 / 3
    if isinstance(spec, dict) and "end" in spec:  # same size and place as a card, so it never covers the captions
        top = put_image(c, bg, "eye", W / 2, CARD_Y, CARD_W * 1.2, ch, dim=0.35)
        out = outlined_text(c, top, "End", spec["end"], W / 2, CARD_Y, fit_px([spec["end"]], CARD_W * 1.05, 80), style="Bold", spacing=1.08)
        return c.text_out(out)
    keys = spec["cards"] if isinstance(spec, dict) else spec
    out = bg
    if isinstance(spec, dict) and "top" in spec:  # hook open: top card (landscape), handled on V3
        pass
    if title:  # step title shot: one card, centred
        keys = keys[:1]
    if len(keys) == 1:
        k = keys[0] if isinstance(keys[0], str) else keys[0][0]
        out = put_image(c, out, k, W / 2, CARD_Y, CARD_W, ch)
    elif len(keys) == 2:
        for i, k in enumerate(keys):
            join = None
            if isinstance(k, tuple):
                k, js = k
                jf = max(0, round((js - a_sec) * FPS))
                join = A(lambda f, jf=jf: 1.0 if f >= jf else 0.0)
            out = put_image(c, out, k, PAIR_X[i], CARD_Y, CARD_W, ch, blend=join)
    return c.text_out(out)


def top_comp(n, kind, payload):
    c = Comp(n)
    bg = c.canvas()
    if kind == "hook":
        cw, ch = 0.5 * W, 0.5 * W * 3 / 4
        im = put_image(c, bg, payload, W / 2, 0.2 * H, cw, ch)
        tag = "(DO NOT USE FOR EVIL)"
        out = outlined_text(c, im, "Tag", tag, W / 2, 0.2 * H + ch / 2 + 70, fit_px([tag], 0.74 * W, 70), rgb=RED, style="Bold")
    else:  # Tristan's step title: big bold caps across the top, about 0.8 of the frame wide
        out = outlined_text(c, bg, "Title", payload, W / 2, 0.13 * H, fit_px(payload.split("\n"), 0.8 * W, 150), style="Bold", spacing=1.0)
    return c.text_out(out)


def caption_comp(n, text, reveal):
    """grey line + white write-on: reveal = [(frame, end_fraction), ...]"""
    c = Comp(n)
    bg = c.canvas()
    g = outlined_text(c, bg, "Grey", text, W / 2, CAP_Y, CAP_PX, style="Demi Bold", alpha=0.55)
    def endf(f):
        v = 0.0
        for fr, e in reveal:
            if f >= fr:
                v = e
        return v
    out = outlined_text(c, g, "White", text, W / 2, CAP_Y, CAP_PX, style="Demi Bold", end=A(endf))
    return c.text_out(out)


# ---- Resolve ---------------------------------------------------------------------------------------------------
def place(mp, t, carrier, rec, d, track):
    span, item = d, None
    for _ in range(8):
        res = mp.AppendToTimeline([{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": span, "trackIndex": track, "recordFrame": rec}])
        item = res[0] if res else None
        if not item:
            return None
        got = item.GetDuration()
        if d - 1 <= got <= d:
            return item
        t.DeleteClips([item]); item = None
        span += 1 if got < d - 1 else -1
    return None


def attach(item, src, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(src)
    item.ImportFusionComp(path)
    names = item.GetFusionCompNameList() or []
    if len(names) > 1:
        item.LoadFusionCompByName(names[-1])
        for nm in names[:-1]:
            item.DeleteFusionCompByName(nm)


def build(take, p, mp, carrier):
    r = KYLE[take]
    segs, spec = r["segs"], CARDS[take]
    W_ = words(take)
    starts = [snap(s[0], W_) for s in segs]
    for i in range(1, len(starts)):  # keep order
        starts[i] = max(starts[i], starts[i - 1] + 0.3)
    root = mp.GetRootFolder()
    sub = lambda nm: next((f for f in root.GetSubFolderList() or [] if f.GetName() == nm), None) or mp.AddSubFolder(root, nm)
    mp.SetCurrentFolder(sub("aroll"))
    path = os.path.expanduser(f"~/Downloads/{SRC[take]}.mp4")
    clip = find_clip(root, os.path.basename(path)) or mp.ImportMedia([path])[0]
    total = int(float(clip.GetClipProperty("Frames")))
    mp.SetCurrentFolder(sub("timelines"))
    name = f"Kyle {take} · {r['name'].split(' · ')[0]}"
    t = mp.CreateEmptyTimeline(name)
    p.SetCurrentTimeline(t)
    t0 = t.GetStartFrame()
    ends = starts[1:] + [total / FPS]
    # V1 zoom pieces
    zones = []
    for i, s in enumerate(segs):
        k = s[2]
        if i == 0:
            zones += [(0.0, min(2.0, ends[0]), "wide"), (min(2.0, ends[0]), ends[0], "med")]
            continue
        zones.append((starts[i], ends[i], "wide" if k == "title" else "punch" if k == "off" else "med"))
    merged = []
    for a, b, z in zones:
        if merged and merged[-1][2] == z:
            merged[-1] = (merged[-1][0], b, z)
        elif b > a:
            merged.append((a, b, z))
    rec = t0
    for a, b, z in merged:
        fa, fb = round(a * FPS), round(b * FPS)
        res = mp.AppendToTimeline([{"mediaPoolItem": clip, "startFrame": fa, "endFrame": fb, "trackIndex": 1, "recordFrame": t0 + fa, "mediaType": 1}])
        if res and ZOOM[z] != 1.0:
            res[0].SetProperty({"ZoomX": ZOOM[z], "ZoomY": ZOOM[z]})
    va = mp.AppendToTimeline([{"mediaPoolItem": clip, "startFrame": 0, "endFrame": total, "trackIndex": 1, "recordFrame": t0, "mediaType": 2}])
    if va:
        va[0].SetProperty({"AudioVolumeEnabled": True, "AudioVolume": VOICE_GAIN_DB})
    # music bed (Tristan's licensed track), from its kick-in, under the voice
    if os.path.exists(MUSIC["path"]):
        mp.SetCurrentFolder(sub("music"))
        mc = find_clip(root, os.path.basename(MUSIC["path"])) or mp.ImportMedia([MUSIC["path"]])[0]
        mfps = float(mc.GetClipProperty("FPS") or FPS) or FPS
        t.AddTrack("audio", "stereo")
        mres = mp.AppendToTimeline([{"mediaPoolItem": mc, "startFrame": int(MUSIC["start"] * mfps), "endFrame": int((MUSIC["start"] + total / FPS) * mfps),
                                     "trackIndex": t.GetTrackCount("audio"), "recordFrame": t0, "mediaType": 2}])
        if mres:
            mres[0].SetProperty({"AudioVolumeEnabled": True, "AudioVolume": MUSIC["gain_db"]})
            mres[0].SetFades({"FadeIn": 0, "FadeOut": int(FPS * 0.8)})
        mp.SetCurrentFolder(sub("timelines"))
    for _ in range(3):
        t.AddTrack("video")
    for i, nm in enumerate(["cards", "titles", "captions"], 2):
        t.SetTrackName("video", i, nm)
    jd = os.path.join(JOB, take, "comps")
    rep = {"cards": 0, "titles": 0, "captions": 0, "fail": []}
    ti = 0
    for i, s in enumerate(segs):
        a, b, k = starts[i], ends[i], s[2]
        fa, d = round(a * FPS), round((b - a) * FPS)
        sp = spec[i]
        if k == "off" or not sp:
            continue
        title = TITLES[take][ti] if k == "title" else None
        it = place(mp, t, carrier, t0 + fa, d, 2)
        if not it:
            rep["fail"].append(f"card {i}"); continue
        sp2 = [(x[0], snap(x[1], W_)) if isinstance(x, tuple) else x for x in sp] if isinstance(sp, list) else sp
        attach(it, card_comp(sp2, d, a, title=title), f"{jd}/card_{i:02d}.comp")
        it.SetClipColor("Teal"); rep["cards"] += 1
        if k == "hook":
            d2 = round(min(2.0, b) * FPS)
            it2 = place(mp, t, carrier, t0, d2, 3)
            if it2:
                attach(it2, top_comp(d2, "hook", sp["top"]), f"{jd}/top_hook.comp"); it2.SetClipColor("Blue"); rep["titles"] += 1
        if title:
            d3 = min(d, round(3.0 * FPS))
            it3 = place(mp, t, carrier, t0 + fa, d3, 3)
            if it3:
                attach(it3, top_comp(d3, "title", title), f"{jd}/title_{ti}.comp"); it3.SetClipColor("Orange"); rep["titles"] += 1
            ti += 1
    # captions
    C = chunks(W_)
    for j, ch in enumerate(C):
        a = max(0.0, ch[0]["s"] - 1 / FPS)
        nxt = C[j + 1][0]["s"] - 1 / FPS if j + 1 < len(C) else ch[-1]["e"] + 0.4
        b = nxt if nxt - ch[-1]["e"] < 0.6 else ch[-1]["e"] + 0.2
        fa, d = round(a * FPS), round((b - a) * FPS)
        if d < 3:
            continue
        text = " ".join(x["w"] for x in ch)
        reveal, acc = [], 0
        for w in ch:
            acc += len(w["w"]) + 1
            reveal.append((max(0, round((w["s"] - a) * FPS)), min(1.0, acc / len(text))))
        it = place(mp, t, carrier, t0 + fa, d, 4)
        if not it:
            rep["fail"].append(f"cap {j}"); continue
        attach(it, caption_comp(d, text, reveal), f"{jd}/cap_{j:03d}.comp")
        rep["captions"] += 1
    rep["timeline"] = name
    return rep


def main(takes):
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
        print(json.dumps(build(tk, p, mp, carrier)))
    pm.SaveProject()


if __name__ == "__main__":
    main(sys.argv[1:] or ["v4"])
