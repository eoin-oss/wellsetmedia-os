"""Gold one-line text hook for 9:16 podcast-sidecap deliveries (James Hempton variant, 24 Oct 2026).
Same spot as the plain hook (black band above the picture, clear of the IG header) and the same font
(RODE Noto Sans CJK SC B, caps), but:
  - warm metallic GOLD (#E8B84A), solid, no gradient, no shadow
  - ONE line, always: the tsv's "line" column may never contain "|", the text is never wrapped, and the size only
    shrinks (84 -> MIN_EM 64) to fit 940px; under 64 it refuses to build that hook (shorten the copy instead)
  - a fast entrance: fades in and scales 0.92 -> 1.0 over IN_FRAMES (ease-out) on the Text+ itself, then holds
    (fade = Alpha1 AND Red1/Green1/Blue1 keyed together; Text+ colour is premultiplied, alpha alone shows on black)
Native Fusion in Resolve: the hook is a Motion Text Pro carrier with its word-follower disconnected, keyed on the Text+.
Usage: AE_PREFIX=j python3 podhook916_gold.py <job root> <text-hooks.tsv> [ids]   (works on "<id> <slug> 9x16"; reruns retext)"""
import csv, glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("AE_MODE", "podcast-sidecap")
from resolve import connect
from podbuild_sidecap import place_title, SIZE_PX
from PIL import ImageFont

FONT, STYLE, FILE = "RODE Noto Sans CJK SC B", "Bold", "/Library/Fonts/RODE Noto Sans CJK SC B.otf"
H, PIC_TOP = 1920, 478                  # picture top edge in the 9:16 (podwrap916: centred block, clear of the IG header)
EM, MIN_EM, MAXW, GAP = 84, 64, 940, 44  # Text+ em px (same as the plain hook), floor, one-line width cap, gap above picture
REND = 0.676                             # this font renders at 0.676x the PIL width for the same Text+ size (measured)
GOLD = (0.91, 0.722, 0.29)               # #E8B84A
IN_FRAMES, SCALE_FROM = 5, 0.92
PREFIX = os.environ.get("AE_PREFIX", "j")


def width(text, em):
    return ImageFont.truetype(FILE, max(8, round(em * REND))).getlength(text)


def fit_one_line(text):
    """largest em <= EM (step 1) whose single line fits MAXW; None if it needs to go under MIN_EM"""
    em = EM
    while em >= MIN_EM:
        if width(text, em) <= MAXW:
            return em
        em -= 1
    return None


def ease_out(u):
    return 1 - (1 - u) ** 3


def main(root, tsv, only=None):
    hooks = {r["id"]: r for r in csv.DictReader(open(tsv), delimiter="\t")}
    for cid, h in hooks.items():  # hard rules, checked before touching Resolve
        line = h["line"].strip()
        assert "|" not in line and "\n" not in line, f"{cid}: hook must be one line, got {line!r}"
        assert line == line.upper(), f"{cid}: hook must be caps"
        assert not any(ch in line for ch in ".,!?;:—–-"), f"{cid}: hook punctuation (only ( ) \" \" and apostrophes): {line!r}"
    p = connect().GetProjectManager().GetCurrentProject()
    mp = p.GetMediaPool(); rootf = mp.GetRootFolder()
    tls = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)}
    report = []
    for path in sorted(glob.glob(f"{root}/{PREFIX}*/clip.json")):
        c = json.load(open(path)); cid = c["id"]
        if only and cid not in only or cid not in hooks:
            continue
        t = tls.get(f"{cid} {c['slug']} 9x16")
        if not t:
            print(cid, "no 9x16 timeline"); continue
        text = hooks[cid]["line"].strip()
        em = fit_one_line(text)
        if em and (hooks[cid].get("em") or "").strip():  # measured-render cap when the PIL estimate runs narrow
            em = min(em, int(hooks[cid]["em"]))
            assert em >= MIN_EM
        if em is None:
            print(f"{cid} REFUSED: '{text}' needs < {MIN_EM}px to fit one line, shorten it"); continue
        lines = [text]
        assert len(lines) == 1
        p.SetCurrentTimeline(t)
        n = t.GetEndFrame() - t.GetStartFrame()
        have = t.GetItemListInTrack("video", 2) if t.GetTrackCount("video") >= 2 else []
        if not have and t.GetTrackCount("video") < 2:
            t.AddTrack("video")
        it = have[0] if have else place_title(mp, rootf, t, "Smooth Word Up", 2, 0, n)
        t.SetTrackName("video", 2, "Hook")
        comp = None
        for _ in range(30):
            comp = it.GetFusionCompByIndex(1)
            if comp and comp.FindTool("Template"):
                break
            time.sleep(0.2)
        tool = comp.FindTool("Template")
        if tool.StyledText.GetConnectedOutput():
            tool.StyledText.ConnectTo(None)          # drop the word-follower: our own entrance, then static
        tool.SetInput("StyledText", text)
        tool.SetInput("Font", FONT); tool.SetInput("Style", STYLE)
        tool.SetInput("Red1", GOLD[0]); tool.SetInput("Green1", GOLD[1]); tool.SetInput("Blue1", GOLD[2])
        tool.SetInput("Enabled3", 0)                  # no shadow on the black band
        tool.SetInput("LineSpacing", 1.0)
        # entrance: Size + element-1 alpha keyed on the comp's own frames (keys at COMPN_RenderStart + f)
        g0 = int(comp.GetAttrs()["COMPN_RenderStart"])
        size = em / SIZE_PX
        # Text+ colour is premultiplied: alpha alone doesn't fade it over black, so RGB ramps with the alpha
        for inp in ("Size", "Alpha1", "Red1", "Green1", "Blue1"):
            if getattr(tool, inp).GetConnectedOutput():
                getattr(tool, inp).ConnectTo(None)
            setattr(tool, inp, comp.BezierSpline())
        for f in range(IN_FRAMES + 1):
            u = ease_out(f / IN_FRAMES)
            a = min(1.0, u * 1.15)
            tool.Size[g0 + f] = size * (SCALE_FROM + (1 - SCALE_FROM) * u)
            tool.Alpha1[g0 + f] = a
            tool.Red1[g0 + f], tool.Green1[g0 + f], tool.Blue1[g0 + f] = (GOLD[0] * a, GOLD[1] * a, GOLD[2] * a)
        # a retexted title can keep stale keys past the entrance (seen: a Size key at frame 40 from the carrier):
        # clear them, then assert the hook really holds at its final size and colour to the end
        for inp in ("Size", "Alpha1", "Red1", "Green1", "Blue1"):
            sp = getattr(tool, inp).GetConnectedOutput().GetTool()
            sp.DeleteKeyFrames(g0 + IN_FRAMES + 1, g0 + 100000)
        for f in (g0 + IN_FRAMES, g0 + n // 2, g0 + n - 1):
            assert abs(tool.GetInput("Size", f) - size) < 1e-6, f"{cid}: hook size drifts at frame {f}"
            assert abs(tool.GetInput("Red1", f) - GOLD[0]) < 1e-6, f"{cid}: hook colour drifts at frame {f}"
        cap = em * REND * 0.72                     # cap height
        cy = PIC_TOP - GAP - cap / 2
        it.SetName(text)
        it.SetProperty({"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 0, "Tilt": round(H / 2 - cy)})
        got = tool.GetInput("StyledText")
        ok = got == text and "\n" not in got
        w = width(text, em)
        report.append((cid, text, em, round(w)))
        print(cid, text, f"em {em}", f"{w:.0f}px", "OK" if ok else f"TEXT NOT SET ({got!r})", flush=True)
    connect().GetProjectManager().SaveProject()
    return report


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]), sys.argv[2], set(sys.argv[3:]) or None)
