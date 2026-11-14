"""Podcast clips, design 'sidecap' (mode podcast-sidecap): a 4:5 crop of the 16:9 episode with the speaker off-centre,
captions stacked beside the head in the room the crop leaves (Kyle on the left of frame -> captions to his right,
James on the right -> captions to his left), short b-roll cutaways from the shoot, a music bed.
Everything lands natively in the OPEN Resolve project: cuts + Fusion transforms on V1, b-roll on V2, Motion Text Pro
titles (font swapped, nothing else) for every caption row on V3-V5, music on A2.
Usage: python3 podbuild_sidecap.py <job root> <broll.tsv> <music.tsv> [ids]
Revision builds: AE_SNAPSHOT=<snapshot.json> takes the b-roll (placement, trims, Pan/Zoom) from Eoin's edited timelines
instead of picking it, AE_OLDCLIPS=<dir> maps it onto re-cut clips by source time, AE_SUFFIX names the new timelines."""
import csv, glob, json, math, os, re, subprocess, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from resolve import connect, find_clip
_mode = os.environ.get("AE_MODE")
os.environ["AE_MODE"] = "hempton-podcast"  # podbuild reads its own mode at import; the shared helpers don't depend on it
from podbuild import zoom_out, put, MTP_DRB
os.environ["AE_MODE"] = _mode or "podcast-sidecap"

HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODE = json.load(open(f"{HOME}/modes/{os.environ.get('AE_MODE', 'podcast-sidecap')}/mode.json"))
W, H, FPS = MODE["canvas"]["w"], MODE["canvas"]["h"], MODE["canvas"]["fps"]
WV = W / (1920 * H / 1080)            # share of the source width the crop shows (0.45 for 4:5)
FR, CAP, BR = MODE["framing"], MODE["captions"], MODE["broll"]
SIZE_PX = CAP["size_px_per_unit"]     # Text+ Size -> rendered em px on this canvas (measured)
TAIL = MODE["cut"]["tail_frames"]
PUNCH = MODE["cut"]["jump_punch"]


def font(name):
    from PIL import ImageFont
    f = CAP["fonts"][name]
    return ImageFont.truetype(os.path.expanduser(f["file"]), 100, index=f.get("index", 0))


FONTS = {}


def width_px(text, style, em):
    """rendered width of a row at em px (MTP Text+ keeps its 0.96 character spacing)"""
    if style not in FONTS:
        FONTS[style] = font(CAP["rows"][style]["font"])
    return FONTS[style].getlength(text) / 100 * em * CAP["spacing_factor"]


# ---- who is on screen: Kyle wears black, James a white polo ------------------------------------------------------
def sides_per_frame(src, f0, f1):
    """'kyle' / 'james' for every source frame in [f0, f1): torso brightness in the lower middle of the 16:9 frame
    (James's white polo ~100-120, Kyle's black top ~30-65). Per frame, because the shot detector misses some of the
    multicam cuts between them."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{f0 / FPS:.3f}", "-i", src, "-frames:v", str(f1 - f0), "-vf", "scale=64:36",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8)[: (len(raw) // (64 * 36)) * 64 * 36].reshape(-1, 36, 64).astype(float)
    lum = a[:, 22:34, 20:44].mean(axis=(1, 2))
    out = ["james" if v > FR["white_shirt_luma"] else "kyle" for v in lum]
    out += [out[-1] if out else "kyle"] * (f1 - f0 - len(out))
    for i in range(1, len(out) - 1):  # a single odd frame is noise
        if out[i - 1] == out[i + 1] != out[i]:
            out[i] = out[i - 1]
    return out


def refine(c):
    """Split pieces wherever the person on screen changes; each part keeps its own face position."""
    out = []
    for pc in c["pieces"]:
        vin = pc.get("video_in", pc["src_in"])
        sd = sides_per_frame(c["source"], vin, vin + pc["src_out"] - pc["src_in"])
        k0 = 0
        for k in range(1, len(sd) + 1):
            if k == len(sd) or (sd[k] != sd[k0] and k - k0 >= 3 and (len(sd) - k >= 3)):
                part = dict(pc, src_in=pc["src_in"] + k0, src_out=pc["src_in"] + k, side=sd[k0],
                            track=pc["track"][k0:k] or pc["track"][-1:])
                if "video_in" in pc:
                    part["video_in"] = pc["video_in"] + k0
                if k0 > 0:
                    part["jump"], part["punch"] = False, False
                part["face_x"] = float(np.median(part["track"])) if part["track"] else pc["face_x"]
                out.append(part)
                k0 = k
    c["pieces"] = out
    return c


def hold_flashes(c):
    """A shot shorter than flash_frames (a stray frame of the other camera) never shows: its picture is the tail of the
    shot before it repeated (the first shot borrows the next one's head); the audio stays its own."""
    P, n_min = c["pieces"], MODE["cut"]["flash_frames"]
    for k, pc in enumerate(P):
        n = pc["src_out"] - pc["src_in"]
        if n >= n_min or len(P) == 1:
            continue
        nb = P[k - 1] if k > 0 else P[k + 1]
        vin = (nb.get("video_in", nb["src_in"]) + (nb["src_out"] - nb["src_in"]) - n) if k > 0 else nb.get("video_in", nb["src_in"])
        pc.update(video_in=vin, side=nb["side"], face_x=nb["face_x"], face_y=nb["face_y"], punch=nb.get("punch", False),
                  track=[nb["face_x"]] * n, held=True)
    return c


def norm_w(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def apply_fixes(c, fixes):
    """Caption text corrections: replace a word sequence, keeping its timing (re-spread when the count changes)."""
    W = c["words"]
    for fx in fixes:
        find = [norm_w(x) for x in fx["find"].split()]
        i = 0
        while i <= len(W) - len(find):
            if [norm_w(w["w"]) for w in W[i:i + len(find)]] == find:
                a, b = W[i]["start"], W[i + len(find) - 1]["end"]
                new = fx["replace"].split()
                step = (b - a) / len(new)
                W[i:i + len(find)] = [dict(W[i], w=x, norm=norm_w(x), start=a + j * step, end=a + (j + 1) * step) for j, x in enumerate(new)]
                i += len(new)
            else:
                i += 1
    return c


def mark_speakers(c, james):
    """Kyle unless the words sit inside one of James's lines (first words .. last words). Words already tagged by
    podspeakers.py (voice model) keep their tag; the james-lines overrides still apply on top."""
    W = c["words"]
    for w in W:
        w.setdefault("spk", "kyle")
    for line in james:
        f, l = [[norm_w(x) for x in part.split()] for part in line.split("|")]
        for i in range(len(W)):
            if [norm_w(w["w"]) for w in W[i:i + len(f)]] == f:
                j = next((j for j in range(i, len(W) - len(l) + 1) if [norm_w(w["w"]) for w in W[j:j + len(l)]] == l), None)
                if j is not None:
                    for w in W[i:j + len(l)]:
                        w["spk"] = "james"
                break
    return c


def src_map(pieces):
    """timeline frame <-> source frame for a clip's pieces (audio timing, which is what the cut follows)"""
    out, t = [], 0
    for pc in pieces:
        n = pc["src_out"] - pc["src_in"]
        out.append((t, t + n, pc["src_in"]))
        t += n
    return out


def remap(f, old, new):
    """old timeline frame -> new timeline frame through the source; None if that moment was cut"""
    s = next((s0 + f - a for a, b, s0 in old if a <= f < b), None)
    if s is None:
        a, b, s0 = old[-1]
        s = s0 + f - a  # the held tail
    hits = [a + s - s0 for a, b, s0 in new if s0 <= s < s0 + (b - a)]  # a hook repeats source: take the nearest
    return min(hits, key=lambda x: abs(x - f)) if hits else None


def frame_cx(fx, side, z):
    """Fusion Transform centre that puts the face at the side's target position in the 4:5 crop, never showing an edge"""
    u = FR["face_u"][side]
    cx = 0.5 + (u - 0.5) * WV - (fx - 0.5) * z
    lo, hi = 0.5 + WV / 2 - 0.5 * z, 0.5 - WV / 2 + 0.5 * z
    return max(lo, min(hi, cx))


# ---- caption blocks -> rows ----------------------------------------------------------------------------------------
def blocks(words, hook_end, dur, ctx=lambda t, w=None: "kyle", ctx_end=lambda t: 1e9):
    """Group words into on-screen blocks: break on sentence ends, commas, pauses, the hook cut, a change of what's on
    screen, or when the block is full. A word only gets a caption when its speaker is the one on camera (or b-roll covers
    it): Kyle's voice over a cut to James nodding along shows nothing, and the captions pick up on the cut back."""
    out, cur = [], []
    ws = [w for w in words if w["norm"] and w["norm"] not in ("um", "uh", "erm", "mm", "mmm", "mmmm", "hmm", "mhm", "mmhmm") and ctx(w["start"], w)]
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        end_sent = w["w"][-1:] in ".?!"
        pause = nxt is not None and nxt["start"] - w["end"] > CAP["block_pause"]
        hook_cut = hook_end and nxt is not None and w["start"] < hook_end - 0.02 <= nxt["start"]
        hook_cut = hook_cut or (nxt is not None and ctx(nxt["start"], nxt) != ctx(cur[0]["start"], cur[0]))  # new picture, new block
        hook_cut = hook_cut or (nxt is not None and ctx_end(cur[0]["start"]) <= nxt["start"])  # the picture changed in between
        comma = w["w"][-1:] == "," and len(cur) >= 3
        full = len(cur) >= CAP["block_words"] or (len(cur) >= 4 and nxt is not None and nxt["start"] - cur[0]["start"] > CAP["block_sec"])
        if nxt is None or hook_cut or comma or (end_sent and len(cur) >= 2) or pause or full or (end_sent and nxt is not None and nxt["start"] - w["end"] > 0.25):
            out.append(cur)
            cur = []
    res = []
    for k, b in enumerate(out):
        a = b[0]["start"]
        nxt = out[k + 1][0]["start"] if k + 1 < len(out) else dur
        e = nxt - 0.04 if nxt - b[-1]["end"] < CAP["hold_gap"] else b[-1]["end"] + CAP["hold_after"]
        e = min(e, ctx_end(a))  # gone on the frame the picture changes
        res.append(dict(words=b, start=a, end=min(e, dur), hook=bool(hook_end) and a < hook_end - 0.02))
    if not hook_end and res:
        res[0]["hook"] = True  # no lifted hook: the opening line plays big
    return res


def clean(w):
    return re.sub(r"[.,;:!?\"]+", "", w).strip()


def rows_of(block, colw, scale):
    """Split a block into 1-3 rows read top to bottom: [medium], [small], [big]; the last row is the payoff, big.
    Animations descend left -> up -> right (mirrored for a left-hand column)."""
    ws = [dict(w, w=clean(w["w"])) for w in block["words"] if clean(w["w"])]
    n = len(ws)
    if n == 0:
        return []
    if n <= 2:
        parts = [ws]
    elif n <= 4:
        parts = [ws[:n - 2], ws[n - 2:]]
    else:
        k = max(1, min(3, (n - 2) // 2))
        parts = [ws[:k], ws[k:n - 2], ws[n - 2:]]
    kinds = {1: ["big"], 2: ["medium", "big"], 3: ["medium", "small", "big"]}[len(parts)]
    rows = []
    for part, kind in zip(parts, kinds):
        text = " ".join(w["w"] for w in part)
        style = kind
        if kind == "big":
            style = "script" if len(text) <= CAP["script_max_chars"] and len(part) <= 2 else "bigsans"
        em = CAP["rows"][style]["em"] * scale
        wpx = width_px(text, style, em)
        if wpx > colw:  # never past the column: shrink this row to fit
            em *= colw / wpx
            wpx = colw
        rows.append(dict(text=text, style=style, em=em, w=wpx, start=part[0]["start"]))
    return rows


def lay_rows(rows, side, on_broll):
    """Pixel centres for a block's rows in a FIXED column (same spot every block, so they're readable): left-aligned
    right of Kyle, right-aligned left of James, a left column over b-roll."""
    gap = CAP["line_gap"]
    hs = [r["em"] * CAP["rows"][r["style"]]["line_h"] for r in rows]
    col = CAP["columns"]["broll" if on_broll else side]
    y = col["top"] * H
    out = []
    for r, h in zip(rows, hs):
        cy = y + h / 2
        if col["align"] == "left":
            cx = col["x"] + r["w"] / 2
        else:
            cx = col["x"] - r["w"] / 2
        out.append((cx, cy))
        y += h + gap
    return out


# ---- Resolve helpers -----------------------------------------------------------------------------------------------
def place_title(mp, rootf, t, title, track, a, e):
    carrier = find_clip(rootf, title)
    cf = float(carrier.GetClipProperty("FPS"))
    d = e - a
    res = put(mp, t, [{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": max(1, int(round(d * cf / FPS))),
                       "trackIndex": track, "recordFrame": t.GetStartFrame() + a}])
    return res[0] if res else None


def set_row(it, row, cx, cy):
    comp = None
    for _ in range(30):
        comp = it.GetFusionCompByIndex(1)
        if comp and comp.FindTool("Template"):
            break
        time.sleep(0.2)
    tool = comp.FindTool("Template")
    fol = next(v for v in comp.GetToolList(False).values() if v.GetAttrs()["TOOLS_RegID"] == "StyledTextFollower")
    fol.SetInput("Text", row["text"])
    f = CAP["fonts"][CAP["rows"][row["style"]]["font"]]
    tool.SetInput("Font", f["family"])
    tool.SetInput("Style", f["style"])
    tool.SetInput("Size", row["em"] / SIZE_PX)
    sh = CAP["shadow"]  # the template's own "Black Shadow" element, switched on so white text holds over the lamps
    tool.SetInput("Enabled3", 1)
    for k, v in sh.items():
        tool.SetInput(k, v)
    it.SetName(row["text"])
    it.SetProperty({"ZoomX": 1.0, "ZoomY": 1.0, "Pan": round(cx - W / 2), "Tilt": round(H / 2 - cy) - JOB.get("caption_drop_px", 0)})
    return fol.GetInput("Text") == row["text"]


def load_tsv(path):
    return list(csv.DictReader(open(path), delimiter="\t"))


# per-job overrides from <job>/job.json (absent for the Kyle job, so it builds exactly as before):
#   caption_drop_px: every caption row sits this many px lower (the Kyle "caplower" pass of 22 Oct was 190px (Resolve reads it back as Tilt -270))
#   columns: {"kyle": {"w": 410}, ...} merged into the mode's caption columns (IG safe zone: right rail 140px, left 60px)
JOB = {}


def main(root, broll_tsv, music_tsv, only=None):
    root = os.path.abspath(root)
    if os.path.exists(f"{root}/job.json"):
        JOB.update(json.load(open(f"{root}/job.json")))
        for side, ov in JOB.get("columns", {}).items():
            CAP["columns"][side].update(ov)
        print("job overrides:", JOB, flush=True)
    lib = {r["key"]: r for r in load_tsv(f"{HOME}/modes/{MODE['name']}/broll-library.tsv")}
    plan = {r["id"]: r["keys"].split(",") for r in load_tsv(broll_tsv)}
    music = {r["id"]: r for r in load_tsv(music_tsv)}
    snap = json.load(open(os.environ["AE_SNAPSHOT"])) if os.environ.get("AE_SNAPSHOT") else None
    olddir = os.environ.get("AE_OLDCLIPS")
    suffix = os.environ.get("AE_SUFFIX", "")
    fixes = json.load(open(f"{root}/caption-fixes.json")) if os.path.exists(f"{root}/caption-fixes.json") else {}
    james = json.load(open(f"{root}/james-lines.json")) if os.path.exists(f"{root}/james-lines.json") else {}
    p = connect().GetProjectManager().GetCurrentProject()
    if not p.GetTimelineCount():
        for k, v in (("timelineFrameRate", str(FPS)), ("timelineResolutionWidth", str(W)), ("timelineResolutionHeight", str(H)),
                     ("timelineInputResMismatchBehavior", "scaleToCrop"), ("timelineOutputResMismatchBehavior", "scaleToCrop")):
            p.SetSetting(k, v)
    mp = p.GetMediaPool()
    rootf = mp.GetRootFolder()

    def sub(n):
        return next((f for f in rootf.GetSubFolderList() or [] if f.GetName() == n), None) or mp.AddSubFolder(rootf, n)
    if not find_clip(rootf, "Smooth Word Up"):
        mp.SetCurrentFolder(rootf)
        mp.ImportFolderFromFile(MTP_DRB)
    existing = {p.GetTimelineByIndex(k).GetName() for k in range(1, (p.GetTimelineCount() or 0) + 1)}
    anim = CAP["animations"]

    for path in sorted(glob.glob(f"{root}/*/clip.json")):
        c = json.load(open(path))
        if only and c["id"] not in only:
            continue
        name = f"{c['id']} {c['slug']}{suffix}"
        if name in existing:
            print(f"skip {name}: timeline exists")
            continue
        apply_fixes(c, fixes.get(c["id"], []))
        mark_speakers(c, james.get(c["id"], []))
        mp.SetCurrentFolder(sub("source"))
        src = find_clip(rootf, os.path.basename(c["source"])) or mp.ImportMedia([c["source"]])[0]
        mp.SetCurrentFolder(sub("timelines"))
        t = mp.CreateEmptyTimeline(name)
        p.SetCurrentTimeline(t)
        t0 = t.GetStartFrame()
        for _ in range(4):
            t.AddTrack("video")
        t.SetTrackName("video", 2, "b-roll")
        for i, nm in enumerate(("row 1", "row 2", "row 3")):
            t.SetTrackName("video", 3 + i, nm)

        refine(c)  # who is on screen, per frame
        hold_flashes(c)  # no stray frames of the other camera

        # V1: pieces, static framing per shot (face at the side's mark), Eoin's zoom-out on the open, punch on jumps
        rec, g, spans = t0, 0, []
        for k, pc in enumerate(c["pieces"]):
            last = k == len(c["pieces"]) - 1
            n0 = pc["src_out"] - pc["src_in"]
            vin = pc.get("video_in", pc["src_in"])
            vext = TAIL if last else 0
            r = put(mp, t, [{"mediaPoolItem": src, "startFrame": vin, "endFrame": vin + n0 + vext,
                             "trackIndex": 1, "recordFrame": rec, "mediaType": 1}])
            ra = put(mp, t, [{"mediaPoolItem": src, "startFrame": pc["src_in"], "endFrame": pc["src_out"] + (3 if last else 0),
                              "trackIndex": 1, "recordFrame": rec, "mediaType": 2}])
            if last and ra:
                ra[0].SetFades({"FadeIn": 0, "FadeOut": 3})
            if not r:
                sys.exit(f"{name}: could not lay {pc}")
            it = r[0]
            n = it.GetDuration()
            spans.append((rec - t0, rec - t0 + n, pc))
            rec = it.GetEnd()
            comp = it.AddFusionComp()
            mi, mo = comp.FindTool("MediaIn1"), comp.FindTool("MediaOut1")
            tr = comp.AddTool("Transform", -32768, -32768)
            tr.Input = mi.Output
            mo.Input = tr.Output
            g0 = int(comp.GetAttrs()["COMPN_RenderStart"])
            punch = PUNCH if pc.get("punch") else 1.0
            zoom = [zoom_out(g + f) * punch for f in range(n)]
            moving = any(zoom_out(g + f) != 1.0 for f in range(n))
            if moving:
                tr.Size = comp.BezierSpline()
                tr.Center = comp.XYPath()
                xy = tr.Center.GetConnectedOutput().GetTool()
                xy.X = comp.BezierSpline()
                xy.Y = comp.BezierSpline()
                for f in range(n):
                    if f == 0 or zoom[f] != zoom[f - 1] or f == n - 1:
                        tr.Size[g0 + f] = zoom[f]
                        xy.X[g0 + f] = frame_cx(pc["face_x"], pc["side"], zoom[f])
                        xy.Y[g0 + f] = 0.5
                tr.MotionBlur = 1
                tr.Quality = 8
                tr.ShutterAngle = 180
            else:
                tr.Size = punch
                tr.Center = {1: frame_cx(pc["face_x"], pc["side"], punch), 2: 0.5}
            g += n
        dur_f = rec - t0
        cuts = sorted({sp[0] for sp in spans[1:]} | {sp[1] for sp in spans[:-1]})
        hook_end = c.get("hook_end", 0.0)

        # V2: b-roll. Revision builds take Eoin's own placement (mapped through any re-cut); edges snap to a nearby cut
        # so a new shot never flashes for a few frames either side of a cutaway
        mp.SetCurrentFolder(sub("b-roll"))
        items = []
        old_name = next((n for n in snap if n.startswith(c["id"] + " ")), None) if snap is not None else None
        if old_name and not snap[old_name]["tracks"].get("V1"):
            old_name = None  # that build never finished: pick fresh
        if old_name:
            old_pcs = json.load(open(f"{olddir}/{os.path.basename(os.path.dirname(path))}.json"))["pieces"] if olddir and os.path.exists(f"{olddir}/{os.path.basename(os.path.dirname(path))}.json") else None
            for b in (snap[old_name]["tracks"].get("V2", []) if old_name else []):
                a, e = b["start"], b["end"]
                if old_pcs is not None:
                    om, nm = src_map(old_pcs), src_map(c["pieces"])
                    a2, e2 = remap(a, om, nm), remap(e - 1, om, nm)
                    if a2 is None or e2 is None:
                        print(f"  b-roll {b['name']} at {a / FPS:.1f}s falls in a cut part: dropped")
                        continue
                    a, e = a2, e2 + 1
                items.append(dict(key=b["name"], path=b["path"], a=a, e=e, src_in=b["src_in"], props=b.get("props", {})))
        else:
            bl0 = blocks(c["words"], hook_end, c["dur"])
            keys = plan.get(c["id"], [])
            cand = [b for b in bl0 if not b["hook"] and b["start"] > max(hook_end, BR["min_start"])
                    and b["end"] < c["dur"] - BR["clear_end"] and BR["min_len"] <= b["end"] - b["start"] <= BR["max_len"]]
            picks = []
            for frac in BR["targets"][:len(keys)]:
                best = min((b for b in cand if all(abs(b["start"] - q["start"]) > BR["spacing"] for q in picks)),
                           key=lambda b: abs(b["start"] - c["dur"] * frac), default=None)
                if best:
                    picks.append(best)
            for b, key in zip(sorted(picks, key=lambda b: b["start"]), keys):
                L = lib[key]
                items.append(dict(key=key, path=L["path"], a=int(round(b["start"] * FPS)), e=int(round(b["end"] * FPS)),
                                  src_in=None, src_sec=float(L["in"]), props={}))
        snapw = MODE["broll"]["snap_frames"]
        cut = []
        for b in items:
            mi = find_clip(sub("b-roll"), os.path.basename(b["path"])) or (mp.ImportMedia([b["path"]]) or [None])[0]
            if not mi:
                print(f"  ! b-roll missing: {b['path']}")
                continue
            sf = float(mi.GetClipProperty("FPS") or 25)
            a, e = b["a"], b["e"]
            s0 = b["src_in"] if b["src_in"] is not None else int(round(b["src_sec"] * sf))
            back = max((a - x for x in cuts if 0 < a - x <= snapw), default=0)  # a new shot showing just before: start on the cut
            a -= back
            s0 = max(0, s0 - int(round(back * sf / FPS)))
            fwd = max((x - e for x in cuts if 0 < x - e <= snapw), default=0)  # the old shot showing just after: end on the cut
            e = min(e + fwd, dur_f)
            r = put(mp, t, [{"mediaPoolItem": mi, "startFrame": s0, "endFrame": s0 + int(round((e - a) * sf / FPS)),
                             "trackIndex": 2, "recordFrame": t0 + a, "mediaType": 1}])
            if not r or not r[0]:
                print(f"  ! b-roll {b['key']} failed: src {s0}-{s0 + int(round((e - a) * sf / FPS))} @ {a}-{e} (clip frames {mi.GetClipProperty('Frames')})")
                continue
            if r:
                r[0].SetName(b["key"])
                pr = {k: v for k, v in b["props"].items() if v is not None}
                if pr:
                    r[0].SetProperty(pr)
                cut.append((a, r[0].GetEnd() - t0))

        # V3-V5: every caption row is a Motion Text Pro title, font swapped; rows build top-down (left, up, right).
        # What's on screen at a moment: 'broll', or whoever the camera is on. A word is captioned only when its speaker
        # is the one on camera, or b-roll covers it.
        def screen(x):
            f = int(round(x * FPS))
            if any(a <= f < e for a, e in cut):
                return "broll"
            return next((sp[2]["side"] for sp in spans if sp[0] <= f < sp[1]), spans[-1][2]["side"])

        def ctx(x, w=None):
            sc = screen(x)
            if sc == "broll":
                return "broll"
            return sc if (w is None or w.get("spk", "kyle") == sc) else None

        bounds = sorted(set(cuts) | {a for a, _ in cut} | {e for _, e in cut} | {dur_f})

        def ctx_end(x):
            f = int(round(x * FPS))
            sc = screen(x)
            return next((b / FPS for b in bounds if b > f and screen(b / FPS) != sc), dur_f / FPS)

        bl = blocks(c["words"], hook_end, c["dur"], ctx, ctx_end)
        fails = rows_n = 0
        jobs = {3: [], 4: [], 5: []}  # every row first, then ONE append per track (Resolve takes a list)
        carriers = {}
        for b in bl:
            a = int(round(b["start"] * FPS)) - CAP["lead_frames"]
            a = max(a, int(round(hook_end * FPS)) if (hook_end and not b["hook"]) else a, 0)
            sc = screen(b["start"])
            lo = max((x for x in bounds if x <= int(round(b["start"] * FPS))), default=0)
            a = max(a, lo)  # never before the picture it belongs to
            e = min(int(round(b["end"] * FPS)), dur_f)
            on_broll = sc == "broll"
            side = "kyle" if on_broll else sc
            colw = CAP["columns"]["broll" if on_broll else side]["w"]
            rows = rows_of(b, colw, CAP["hook_scale"] if b["hook"] else 1.0)
            pos = lay_rows(rows, side, on_broll)
            seq = (anim["right_column"] if (on_broll or side == "kyle") else anim["left_column"])[str(len(rows))]
            for i, (row, (cx, cy), title) in enumerate(zip(rows, pos, seq)):
                ra = max(a, int(round(row["start"] * FPS)) - CAP["lead_frames"])
                if e - ra < 4:
                    continue
                jobs[3 + i].append((ra, e, title, row, cx, cy))
        for track, js in jobs.items():
            js.sort(key=lambda j: j[0])
            infos = []
            for ra, e, title, *_ in js:
                if title not in carriers:
                    carriers[title] = find_clip(rootf, title)
                cf = float(carriers[title].GetClipProperty("FPS"))
                infos.append({"mediaPoolItem": carriers[title], "startFrame": 0, "endFrame": max(1, int(round((e - ra) * cf / FPS))),
                              "trackIndex": track, "recordFrame": t0 + ra})
            res = put(mp, t, infos) if infos else []
            for j, it in zip(js, res or []):
                rows_n += 1
                if not it or not set_row(it, j[3], j[4], j[5]):
                    fails += 1
            fails += max(0, len(js) - len(res or []))

        # A2: music bed, sat well under the voice
        m = music.get(c["id"])
        if m:
            mp.SetCurrentFolder(sub("music"))
            mpath = os.path.join(MODE["music"]["dir"], m["file"])
            mi = find_clip(sub("music"), m["file"]) or mp.ImportMedia([mpath])[0]
            if t.GetTrackCount("audio") < 2:
                t.AddTrack("audio", "stereo")
            st = int(float(m["start"]) * FPS)
            r = put(mp, t, [{"mediaPoolItem": mi, "startFrame": st, "endFrame": st + dur_f, "trackIndex": 2,
                             "recordFrame": t0, "mediaType": 2}])
            if r:
                r[0].SetProperty({"AudioVolumeEnabled": True, "AudioVolume": float(m["gain_db"])})
                r[0].SetFades({"FadeIn": 0, "FadeOut": int(FPS * MODE["music"]["fade_out_sec"])})
        connect().GetProjectManager().SaveProject()
        held = sum(1 for pc in c["pieces"] if pc.get("held"))
        print(f"built {name}: {len(c['pieces'])} shots ({held} flashes held), {len(cut)} b-roll, {rows_n} caption rows"
              + (f", {fails} row fails" if fails else ""), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], a[2], set(a[3].split(",")) if len(a) > 3 else None)
