"""Build prepped podcast clips (podprep.py) into the OPEN Resolve project, one 9:16 timeline per clip:
V1 = the cut pieces of the source, each camera shot panned so the speaker's face is centred (face tracking),
a fast zoom-out with motion blur on the opening, V2 = Eoin-style captions (Motion Text Pro "Smooth Word Up" carrier
+ his comp), lower third under the face. No b-roll, no music.
Usage: python3 podbuild.py <job root> [ids]"""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from resolve import connect, find_clip
from build import text_width, fusion_str

HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# every look/feel parameter comes from the mode (modes/<name>/mode.json); AE_MODE picks it, default = the approved one
MODE = json.load(open(f"{HOME}/modes/{os.environ.get('AE_MODE', 'hempton-podcast')}/mode.json"))
MTP_DRB = os.path.expanduser("~/Library/CloudStorage/Dropbox/personal brand directory/asssets/Motiontext-pro-v1/"
                             "davinci-resolve-version21+/MotionText Pro V1.drb")
W, H, FPS = MODE["canvas"]["w"], MODE["canvas"]["h"], MODE["canvas"]["fps"]
SRC_W, SRC_H = 1920, 1080
SCALED_W = SRC_W * H / SRC_H          # source scaled to fill the 9:16 height (scale-to-crop)
LOCK = (SRC_W - SRC_W * W / SCALED_W) / 2 / SRC_W  # how far the source can slide before an edge shows (0.342)


def zoom_out(f):
    """Eoin's Smooth Zoom out: Fusion bezier P0(0,1.278) P1(2,1.114) P2(17.6,1) P3(35,1), cut at 23 frames."""
    if f >= 23:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(40):  # solve x(u) = f
        u = (lo + hi) / 2
        x = 3 * (1 - u) ** 2 * u * 2 + 3 * (1 - u) * u ** 2 * 17.6 + u ** 3 * 35
        lo, hi = (u, hi) if x < f else (lo, u)
    u = (lo + hi) / 2
    return round((1 - u) ** 3 * 1.278 + 3 * (1 - u) ** 2 * u * 1.114 + 3 * (1 - u) * u ** 2 * 1 + u ** 3 * 1, 4)


SAFE_W = MODE["captions"]["safe_width_px"]  # IG/TikTok reels: text stays clear of the right-hand buttons (x ~160-920 when centred)


def split3(phrases):
    """Max 3 words on screen: longer phrases split into balanced chunks (4 -> 2+2, 5 -> 3+2, 6 -> 3+3)."""
    import math
    out = []
    for p in phrases:
        ws = p["words"]
        n = len(ws)
        if n <= 3:
            out.append(p)
            continue
        k = math.ceil(n / 3)
        size = math.ceil(n / k)
        for i in range(0, n, size):
            ch = ws[i:i + size]
            text = " ".join(w["w"] for w in ch)
            out.append(dict(start=ch[0]["start"], end=ch[-1]["end"], words=ch, text=text))
    import re
    for p in out:
        p["text"] = re.sub(r"[.,;:]+(\s|$)", r"\1", p["text"]).strip()
    return out


CAP = dict(size=MODE["captions"]["size"], tilt=MODE["captions"]["tilt"], maxw=0.86, lead_frames=MODE["captions"]["lead_frames"])  # caption size vs template, lower third, safe width


STYLE_PUNCH = MODE["cut"]["jump_punch"]  # Eoin's jump punch-in (style.json aroll.jump_punch)
TAIL = MODE["cut"]["tail_frames"]  # frames the picture holds after the last word
MUSIC_DIR = MODE["music"]["dir"]
MUSIC_TSV = os.path.expanduser("$WSM_HOME/clients/james-hempton/podcast-clips-galligan/music.tsv")


def put(mp, t, items):
    """Append to THIS timeline: Resolve appends to whatever timeline is open, and Eoin may be clicking through the
    others while a batch runs. Re-select ours right before every append, and check it stuck."""
    proj = connect().GetProjectManager().GetCurrentProject()
    for _ in range(5):
        proj.SetCurrentTimeline(t)
        if proj.GetCurrentTimeline().GetUniqueId() == t.GetUniqueId():
            break
        time.sleep(0.3)
    return mp.AppendToTimeline(items)


def music_for(cid):
    """Per-clip bed from music.tsv: file on the SSD, where it kicks in (measured), gain level-matched to 01."""
    import csv
    for r in csv.DictReader(open(MUSIC_TSV), delimiter="\t"):
        if r["id"] == cid:
            return dict(path=os.path.join(MUSIC_DIR, r["file"]), start=float(r["start"]), gain_db=float(r["gain_db"]))
    return None


# hook rows, top to bottom: Motion Text Pro animation, size vs template, the punch row biggest
HOOK_ROWS = [tuple(r) for r in MODE["hook"]["rows"]]
CHIN = MODE["text_hook"]["chin_offset"]  # face centre -> chin, as a fraction of frame height (this studio framing)
HOOK_FIRST = MODE["hook"]["first_frame"]  # first row lands 3 frames in, so frame one is clean
HOOK_STAGGER = MODE["hook"]["stagger_frames"]  # frames between rows


def hook_titles(mp, rootf, t, c, hook_end):
    """James's opening question as stacked MTP rows: top row drops in, middle slides in from the left, the last
    words rise up big. Each row lands as he says it; all hold until the question ends."""
    import re
    ws = [dict(w) for w in c["hook_words"] if w["norm"] not in ("um", "uh")]
    for w in ws:
        w["w"] = re.sub(r"[.,;:]+$", "", w["w"])
    # the approved 01 split: 1 row (<=3 words), 2 rows (<=5), 3 rows (<=9: first up to 3, middle, last 2 big).
    # Only longer questions go to 4 rows of at most 4 words (adds a row coming in from the right).
    import math
    n = len(ws)
    if n <= 3:
        rows, styles = [ws], HOOK_ROWS[2:]
    elif n <= 5:
        rows, styles = [ws[:-2], ws[-2:]], HOOK_ROWS[1:]
    elif n <= 9:
        k = min(3, (n - 2 + 1) // 2)
        rows, styles = [ws[:k], ws[k:-2], ws[-2:]], HOOK_ROWS
    else:  # long question: still the approved three rows, the font shrinks to fit the safe width
        k = math.ceil((n - 2) / 2)
        rows, styles = [ws[:k], ws[k:-2], ws[-2:]], HOOK_ROWS
    t0, end = t.GetStartFrame(), int(round(hook_end * FPS))
    sizes, nl = [], []
    for row, (_, sz) in zip(rows, styles):
        text = " ".join(w["w"] for w in row)
        f = min(sz, SAFE_W / (text_width(text) * W / 1920))
        if f < 0.85 * sz and len(row) > 3:  # too long for one line: break it in two, balanced
            k = min(range(1, len(row)), key=lambda j: abs(text_width(" ".join(w["w"] for w in row[:j])) -
                                                           text_width(" ".join(w["w"] for w in row[j:]))))
            l1, l2 = " ".join(w["w"] for w in row[:k]), " ".join(w["w"] for w in row[k:])
            text = l1 + "\n" + l2
            f = min(sz, SAFE_W / (max(text_width(l1), text_width(l2)) * W / 1920))
        sizes.append((text, f))
        nl.append(text.count("\n") + 1)
    em = [65 * f * k for (_, f), k in zip(sizes, nl)]   # block height per row (em px x lines)
    gaps = [(a + b) / 2 * 1.05 for a, b in zip(em, em[1:])]
    lay = box_layout(c)
    top = box_top(c) + (lay[3] + 30 if lay else 10) + em[0] / 2  # first row centre: under the text hook (or the chin)
    tilts = [H / 2 - (top + sum(gaps[:i])) for i in range(len(rows))]
    for i, (row, (title, _), (text, f)) in enumerate(zip(rows, styles, sizes)):
        carrier = find_clip(rootf, title)
        a = HOOK_FIRST + i * HOOK_STAGGER  # the stack builds in at the top of the clip, a row every few frames
        cf = float(carrier.GetClipProperty("FPS"))
        res = put(mp, t, [{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": max(1, int((end - a) * cf / FPS)),
                                    "trackIndex": 3 + i, "recordFrame": t0 + a}])
        if not res:
            print(f"  hook row {i} failed")
            continue
        it = res[0]
        comp = None
        for _ in range(20):  # a freshly placed title can take a moment before its comp is reachable
            comp = it.GetFusionCompByIndex(1)
            if comp and comp.FindTool("Template"):
                break
            time.sleep(0.25)
        tool = comp.FindTool("Template")
        # text on the StyledTextFollower (drives the word animation), size on the Text+
        fol = next(v for v in comp.GetToolList(False).values() if v.GetAttrs()["TOOLS_RegID"] == "StyledTextFollower")
        fol.SetInput("Text", text)
        tool.SetInput("Size", 0.08 * f)
        it.SetName(title)  # shows as the pack's title on the timeline, not "Text+"
        it.SetProperty({"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 0, "Tilt": tilts[i]})


HOOKBOX_MIN = MODE["text_hook"]["min_sec"]  # the text hook stays at least this long (sec), even on clips with no question
BOX_SIZE = MODE["text_hook"]["size"]  # Text+ size of the text hook (em ~65px), shrinks to fit the safe width
HOOKS_TSV = os.path.expanduser("$WSM_HOME/clients/james-hempton/podcast-clips-galligan/hooks.tsv")


def hook_line(cid):
    import csv
    return next((r["hook"] for r in csv.DictReader(open(HOOKS_TSV), delimiter="\t") if r["id"] == cid), None)


def box_layout(c):
    """Text hook geometry: up to two balanced lines, sized to the safe width. Returns lines, Text+ size, em px and
    the height the box takes up (incl. padding), or None when the clip has no text hook."""
    from PIL import ImageFont
    text = hook_line(c["id"])
    if not text:
        return None
    font_px = lambda size: size * 1450 * W / 1920
    pil = ImageFont.truetype(os.path.expanduser("~/Library/Fonts/SFPRODISPLAYBOLD.OTF"), 100)
    width = lambda s_, size: pil.getlength(s_) / 100 * font_px(size)
    size = BOX_SIZE
    lines = [text]
    if width(text, size) > SAFE_W - 60:
        ws = text.split()
        best = min(range(1, len(ws)), key=lambda k: abs(pil.getlength(" ".join(ws[:k])) - pil.getlength(" ".join(ws[k:]))))
        lines = [" ".join(ws[:best]), " ".join(ws[best:])]
    size = min(size, size * (SAFE_W - 60) / max(width(l, size) for l in lines))
    em = font_px(size)
    return lines, size, em, len(lines) * em * 1.0 + em * 0.9


def box_top(c):
    """The hook block starts just under the speaker's chin (his head fills the top of this framing)."""
    return (c["pieces"][0]["face_y"] + CHIN) * H + 30


def hook_box(mp, rootf, t, c, end):
    """The text hook: black SF Pro Display Bold in a rounded yellow box at the top, pops in at the start and stays
    for the hook. Long lines break onto two balanced lines; size fits the safe width."""
    lay = box_layout(c)
    if not lay:
        return
    lines, size, em, block = lay
    cy = 1 - (box_top(c) + block / 2) / H  # Fusion y runs up
    carrier = find_clip(rootf, "Smooth Word Up")
    cf = float(carrier.GetClipProperty("FPS"))
    n = int(round(end * FPS))
    res = put(mp, t, [{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": max(1, int(n * cf / FPS)), "trackIndex": 6,
                       "recordFrame": t.GetStartFrame()}])
    if not res:
        print("  ! hook box failed")
        return
    it = res[0]
    src_ = open(f"{HOME}/styles/eoin/captions/hookbox.comp", encoding="utf-8").read()
    src_ = src_.replace("__TEXT__", fusion_str("\n".join(lines))).replace("__SIZE__", f"{size:.4f}").replace("__CY__", f"{cy:.4f}")
    cp = f"{c['_dir']}/comps/hookbox.comp"
    os.makedirs(os.path.dirname(cp), exist_ok=True)
    open(cp, "w", encoding="utf-8").write(src_)
    it.ImportFusionComp(cp)
    names = it.GetFusionCompNameList() or []
    if len(names) > 1:
        it.LoadFusionCompByName(names[-1])
        for nm in names[:-1]:
            it.DeleteFusionCompByName(nm)
    it.SetName("Text Hook")


def music_bed(mp, folder, t, dur, MUSIC):
    mp.SetCurrentFolder(folder)
    mi = find_clip(folder, os.path.basename(MUSIC["path"])) or mp.ImportMedia([MUSIC["path"]])[0]
    if t.GetTrackCount("audio") < 2:
        t.AddTrack("audio", "stereo")
    n = int(round(dur * FPS))
    r = put(mp, t, [{"mediaPoolItem": mi, "startFrame": int(MUSIC["start"] * FPS), "endFrame": int(MUSIC["start"] * FPS) + n,
                              "trackIndex": 2, "recordFrame": t.GetStartFrame(), "mediaType": 2}])
    if r:
        r[0].SetProperty({"AudioVolumeEnabled": True, "AudioVolume": MUSIC["gain_db"]})
        r[0].SetFades({"FadeIn": 0, "FadeOut": int(FPS * 0.8)})


def main(root, only=None):
    root = os.path.abspath(root)  # Resolve only imports comps from absolute paths
    style = json.load(open(f"{HOME}/styles/eoin/style.json"))
    # running captions: fast blur-in-and-up (sharp within ~4 frames); the hook keeps the stock MTP animations
    template = open(f"{HOME}/{MODE['captions']['comp']}", encoding="utf-8").read()
    z = style["intro_zoom"]
    p = connect().GetProjectManager().GetCurrentProject()
    if not p.GetTimelineCount():
        for k, v in (("timelineFrameRate", str(FPS)), ("timelineResolutionWidth", str(W)), ("timelineResolutionHeight", str(H)),
                     ("timelineInputResMismatchBehavior", "scaleToCrop"), ("timelineOutputResMismatchBehavior", "scaleToCrop")):
            if not p.SetSetting(k, v):
                print(f"warning: could not set {k}={v}")
    mp = p.GetMediaPool()
    rootf = mp.GetRootFolder()

    def sub(n):
        return next((f for f in rootf.GetSubFolderList() or [] if f.GetName() == n), None) or mp.AddSubFolder(rootf, n)
    if not find_clip(rootf, style["captions"]["carrier_title"]):
        mp.SetCurrentFolder(rootf)
        mp.ImportFolderFromFile(MTP_DRB)
    carrier = find_clip(rootf, style["captions"]["carrier_title"])
    if not carrier:
        sys.exit("Motion Text Pro carrier not found after import")
    carrier_fps = float(carrier.GetClipProperty("FPS"))
    existing = {p.GetTimelineByIndex(k).GetName() for k in range(1, (p.GetTimelineCount() or 0) + 1)}

    for path in sorted(glob.glob(f"{root}/*/clip.json")):
        c = json.load(open(path))
        c["_dir"] = os.path.dirname(path)
        if only and c["id"] not in only:
            continue
        name = f"{c['id']} {c['slug']}"
        if name in existing:
            print(f"skip {name}: timeline exists")
            continue
        mp.SetCurrentFolder(sub("source"))
        src = find_clip(rootf, os.path.basename(c["source"])) or mp.ImportMedia([c["source"]])[0]
        mp.SetCurrentFolder(sub("timelines"))
        t = mp.CreateEmptyTimeline(name)
        p.SetCurrentTimeline(t)
        t0 = t.GetStartFrame()

        # V1: pieces back to back. Each piece gets a Fusion transform keyed every frame: Center X holds the face on the
        # vertical centre line (the face lock), and over the first 23 timeline frames Size runs Eoin's "Smooth Zoom out"
        # curve (1.278 -> 1, hard ease-out, lifted from his Perception edit).
        rec, g = t0, 0
        for k, pc in enumerate(c["pieces"]):
            last = k == len(c["pieces"]) - 1
            if last:
                # payoff: the picture holds a beat past the last word (music carries it); the voice stops just
                # before the other mic comes back in, with a 3-frame fade so nothing clicks
                r = put(mp, t, [{"mediaPoolItem": src, "startFrame": pc["src_in"], "endFrame": pc["src_out"] + TAIL,
                                          "trackIndex": 1, "recordFrame": rec, "mediaType": 1}])
                ra = put(mp, t, [{"mediaPoolItem": src, "startFrame": pc["src_in"], "endFrame": pc["src_out"] + 3,
                                           "trackIndex": 1, "recordFrame": rec, "mediaType": 2}])
                if ra:
                    ra[0].SetFades({"FadeIn": 0, "FadeOut": 3})
            elif pc.get("video_in") is not None:
                # picture from elsewhere (the question shot held under the answer's first words), audio from here
                n0 = pc["src_out"] - pc["src_in"]
                r = put(mp, t, [{"mediaPoolItem": src, "startFrame": pc["video_in"], "endFrame": pc["video_in"] + n0,
                                 "trackIndex": 1, "recordFrame": rec, "mediaType": 1}])
                put(mp, t, [{"mediaPoolItem": src, "startFrame": pc["src_in"], "endFrame": pc["src_out"],
                             "trackIndex": 1, "recordFrame": rec, "mediaType": 2}])
            else:
                r = put(mp, t, [{"mediaPoolItem": src, "startFrame": pc["src_in"], "endFrame": pc["src_out"],
                                          "trackIndex": 1, "recordFrame": rec}])
            if not r:
                sys.exit(f"{name}: could not lay {pc}")
            it = next((x for x in r if (x.GetTrackTypeAndIndex() or [None])[0] == "video"), r[0])
            rec = it.GetEnd()
            n = it.GetDuration()
            comp = it.AddFusionComp()
            mi, mo = comp.FindTool("MediaIn1"), comp.FindTool("MediaOut1")
            tr = comp.AddTool("Transform", -32768, -32768)
            tr.Input = mi.Output
            mo.Input = tr.Output
            g0 = int(comp.GetAttrs()["COMPN_RenderStart"])  # the clip's first frame in comp time (GlobalStart is source frame 0)
            punch = STYLE_PUNCH if pc.get("punch") else 1.0  # hides the jump where an um was cut inside one shot
            intro = [zoom_out(g + f) for f in range(n)]
            zoom = [z_ * punch for z_ in intro]
            if punch != 1.0 and all(z_ == 1.0 for z_ in intro):
                tr.Size = punch
            elif any(zv != 1.0 for zv in zoom):
                tr.Size = comp.BezierSpline()
                for f in range(n):
                    if f == 0 or zoom[f] != 1.0 or zoom[f - 1] != 1.0:
                        tr.Size[g0 + f] = zoom[f]
                tr.MotionBlur = 1
                tr.Quality = 8
                tr.ShutterAngle = 180
            tr.Center = comp.XYPath()
            xy = tr.Center.GetConnectedOutput().GetTool()
            xy.X = comp.BezierSpline()
            xy.Y = comp.BezierSpline()
            trk = pc["track"]
            for f in sorted(set(range(0, n, 3)) | {n - 1} | {f for f in range(n) if intro[f] != 1.0}):
                fx = trk[min(f, len(trk) - 1)]
                cx = 0.5 - (fx - 0.5) * zoom[f]
                xy.X[g0 + f] = max(0.5 - LOCK, min(0.5 + LOCK, cx))  # XYPath X/Y are absolute positions
                xy.Y[g0 + f] = 0.5
            g += n

        # V2: captions, one carrier per phrase, phrase start -> next phrase start (continuous) unless there's a pause
        for _ in range(5):
            t.AddTrack("video")
        t.SetTrackName("video", 2, "captions")
        t.SetTrackName("video", 3, "hook")
        hook_end = c.get("hook_end", 0.0)
        hold = 0.0
        ph = split3([x for x in c["phrases"] if x["start"] >= hook_end - 0.05])
        lead = CAP["lead_frames"]
        fails = 0
        for k, s in enumerate(ph):
            a = max(0, int(round(s["start"] * FPS)) - lead, int(round(hook_end * FPS)))  # nothing before the cut
            nxt = ph[k + 1]["start"] if k + 1 < len(ph) else c["dur"]
            e = int(round(nxt * FPS)) - lead if nxt - s["end"] < 0.6 else int(round((s["end"] + 0.15) * FPS))
            e = min(e, int(round(c["dur"] * FPS)))
            d = e - a
            if d < 3:
                continue
            span, item, tried = max(1, int(d * carrier_fps / FPS)), None, set()
            for _ in range(6):
                if span in tried:
                    break
                tried.add(span)
                res = put(mp, t, [{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": span, "trackIndex": 2,
                                            "recordFrame": t0 + a}])
                item = res[0] if res else None
                if not item:
                    break
                got = item.GetDuration()
                if d - 2 <= got <= d:
                    break
                t.DeleteClips([item])
                item = None
                span += 1 if got < d - 2 else -1
            if not item:
                fails += 1
                continue
            tw = text_width(s["text"]) * W / 1920  # px at template size on this canvas
            f = min(CAP["size"], SAFE_W / tw)
            src_ = template.replace('Value = "you have to give"', f'Value = "{fusion_str(s["text"])}"')
            src_ = src_.replace('Font = Input { Value = "Helvetica", },',
                                f'Font = Input {{ Value = "Helvetica", }},\n\t\t\t\tSize = Input {{ Value = {0.08 * f:.4f}, }},', 1)
            cp = f"{os.path.dirname(path)}/comps/{k:03d}.comp"
            os.makedirs(os.path.dirname(cp), exist_ok=True)
            open(cp, "w", encoding="utf-8").write(src_)
            # the first import onto a fresh title sometimes doesn't take: verify the text, retry
            for _ in range(4):
                item.ImportFusionComp(cp)
                names = item.GetFusionCompNameList() or []
                if len(names) > 1:
                    item.LoadFusionCompByName(names[-1])
                    for nm in names[:-1]:
                        item.DeleteFusionCompByName(nm)
                tool = item.GetFusionCompByIndex(1).FindTool("Template")
                if tool and tool.GetInput("StyledText") == s["text"]:
                    break
                time.sleep(0.3)
            else:
                fails += 1
            tilt = CAP["tilt"]
            if not hook_end and a < HOOKBOX_MIN * FPS and box_layout(c):
                # the text hook sits at caption height for the first seconds: early captions go under the box
                tilt = round(H / 2 - (box_top(c) + box_layout(c)[3] + 30 + 47))
            item.SetProperty({"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 0, "Tilt": tilt})
        if hook_end:
            hook_titles(mp, rootf, t, c, hook_end)  # clears exactly on the cut to the answer
        hook_box(mp, rootf, t, c, hook_end or HOOKBOX_MIN)  # with a question: ends on the cut, like the rows
        mus = music_for(c["id"])
        if mus and os.path.exists(mus["path"]):
            music_bed(mp, sub("music"), t, c["dur"] + TAIL / FPS, mus)
        else:
            print(f"  ! no music for {c['id']} (SSD mounted?)")
        connect().GetProjectManager().SaveProject()
        print(f"built {name}: {len(c['pieces'])} shots, {len(ph) - fails} captions" + (f", {fails} caption fails" if fails else ""), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None)
