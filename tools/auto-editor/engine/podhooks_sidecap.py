"""Text hooks for podcast-sidecap clips: a 3-row stack (caps / script / BIG caps) in the lower third over the opening
hook, built from Motion Text Pro titles on their own tracks (Hook 1-3) so the caption tracks stay untouched.
Rows: Helvetica Neue Bold Italic caps, Playfair Display Italic middle word(s), big caps. Staggered entrances; held to
the cut back (hook_end), clamped 3.2-4.5s. Reruns clear the Hook tracks first.
Usage: python3 podhooks_sidecap.py <job root> <text-hooks.tsv> [ids]"""
import csv, glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from resolve import connect, find_clip
from PIL import ImageFont
os.environ.setdefault("AE_MODE", "podcast-sidecap")
from podbuild_sidecap import place_title, W, H, FPS, SIZE_PX, CAP

FONTS = {"caps": ("Helvetica Neue", "Bold Italic", ("/System/Library/Fonts/HelveticaNeue.ttc", 3)),
         "script": ("Playfair Display", "Italic",
                    (os.path.expanduser("~/Library/Fonts/PlayfairDisplay-Italic-VariableFont_wght.ttf"), 0))}
ROWS = [("top", "caps", 52, "Smooth Word Up", 0.00),
        ("mid", "script", 88, "Smooth Word Right", 0.24),
        ("big", "caps", 104, "Smooth Word Up", 0.48)]
MAXW, BOTTOM, GAP = 960, 1190, 2
SHADOW = {"Alpha3": 0.75, "SoftnessX3": 14, "SoftnessY3": 14}
TRACKS = ["Hook 1", "Hook 2", "Hook 3"]


def fit(text, kind, em):
    path, idx = FONTS[kind][2]
    while em > 24:
        w = ImageFont.truetype(path, em, index=idx).getlength(text)
        if w <= MAXW:
            return em
        em -= 2
    return em


def hook_tracks(t):
    have = {t.GetTrackName("video", k): k for k in range(1, t.GetTrackCount("video") + 1)}
    out = []
    for name in TRACKS:
        if name not in have:
            t.AddTrack("video")
            k = t.GetTrackCount("video")
            t.SetTrackName("video", k, name)
            have[name] = k
        k = have[name]
        old = t.GetItemListInTrack("video", k) or []
        if old:
            t.DeleteClips(old)
        out.append(k)
    return out


def set_text(it, text, kind, em):
    import time
    comp = None
    for _ in range(30):
        comp = it.GetFusionCompByIndex(1)
        if comp and comp.FindTool("Template"):
            break
        time.sleep(0.2)
    tool = comp.FindTool("Template")
    fol = next(v for v in comp.GetToolList(False).values() if v.GetAttrs()["TOOLS_RegID"] == "StyledTextFollower")
    fol.SetInput("Text", text)
    fam, sty, _ = FONTS[kind]
    tool.SetInput("Font", fam)
    tool.SetInput("Style", sty)
    tool.SetInput("Size", em / SIZE_PX)
    tool.SetInput("Enabled3", 1)
    for k, v in SHADOW.items():
        tool.SetInput(k, v)
    it.SetName(text)
    return fol.GetInput("Text") == text


def main(root, tsv, only=None):
    hooks = {r["id"]: r for r in csv.DictReader(open(tsv), delimiter="\t")}
    p = connect().GetProjectManager().GetCurrentProject()
    mp = p.GetMediaPool(); rootf = mp.GetRootFolder()
    tls = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)}
    for cid, h in hooks.items():
        if only and cid not in only:
            continue
        clipdir = glob.glob(f"{root}/{cid}-*")[0]
        clip = json.load(open(f"{clipdir}/clip.json"))
        name = next((n for n in tls if n.startswith(cid + " ") and n.endswith(" v2")), None)
        if not name:
            print(cid, "NO TIMELINE"); continue
        t = tls[name]
        p.SetCurrentTimeline(t)
        hold = min(max(clip["hook_end"], 3.2), 4.5)
        ks = hook_tracks(t)
        rows = [(h[key], kind, fit(h[key], kind, em), anim, lead) for key, kind, em, anim, lead in ROWS]
        heights = [em * (1.05 if kind == "script" else 0.9) for _, kind, em, _, _ in rows]
        y = BOTTOM - sum(heights) - GAP * 2
        ok = []
        for (text, kind, em, anim, lead), hgt, k in zip(rows, heights, ks):
            cy = y + hgt / 2; y += hgt + GAP
            a = round(lead * FPS); e = round(hold * FPS)
            it = place_title(mp, rootf, t, anim, k, a, e)
            good = bool(it) and set_text(it, text, kind, em)
            if it:
                it.SetProperty({"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 0, "Tilt": round(H / 2 - cy)})
            ok.append(good)
        print(cid, name, f"hold {hold:.2f}s", "OK" if all(ok) else f"FAIL {ok}")


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]), sys.argv[2], set(sys.argv[3:]) or None)
