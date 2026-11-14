"""Plain text hook for the 9:16 podcast-sidecap deliveries: one static white caption in the black band above the
picture, all caps, RODE Noto Sans CJK SC B, wrapped like a caption (no stacking, no animation), sitting a natural
gap above the picture's top edge, on for the whole clip. Built from a Motion Text Pro carrier with its word-follower
disconnected (the project has no plain Text+ carrier). Text = the tsv's line column (| = line break), else top + mid + big joined and balanced.
Usage: python3 podhook916_plain.py <job root> <text-hooks.tsv> [ids]   (works on "<id> <slug> 9x16"; reruns replace)"""
import csv, glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("AE_MODE", "podcast-sidecap")
from resolve import connect
from podbuild_sidecap import place_title, SIZE_PX
from PIL import ImageFont
import safezone

FONT, STYLE, FILE = "RODE Noto Sans CJK SC B", "Bold", "/Library/Fonts/RODE Noto Sans CJK SC B.otf"
H, PIC_TOP = 1920, 478                  # picture top edge as rendered: centred block, picture cropped at the bottom (23 Oct; 365 put the hook under the IG header)
EM, MAXW, GAP, LINE = 84, 940, 44, 1.13   # Text+ em px, wrap width, space above the picture, line pitch (x EM)
REND = 0.676                             # this font renders at 0.676x the PIL width for the same Text+ size (measured)


def wrap(text, em):
    """Fewest lines that fit MAXW, then the split with the most even line widths (no lonely last word)."""
    f = ImageFont.truetype(FILE, max(8, round(em * REND)))
    words = text.split()
    W = lambda a, b: f.getlength(" ".join(words[a:b]))
    n = len(words)
    for L in range(1, n + 1):
        best = {}
        def go(a, left):
            if (a, left) in best:
                return best[(a, left)]
            if left == 1:
                r = (W(a, n), [(a, n)]) if W(a, n) <= MAXW else None
            else:
                r = None
                for b in range(a + 1, n - left + 2):
                    if W(a, b) > MAXW:
                        break
                    sub = go(b, left - 1)
                    if sub:
                        cand = (max(W(a, b), sub[0]), [(a, b)] + sub[1])
                        if not r or cand[0] < r[0]:
                            r = cand
            best[(a, left)] = r
            return r
        r = go(0, L)
        if r:
            return [" ".join(words[a:b]) for a, b in r[1]]
    return [text]


def main(root, tsv, only=None):
    unsafe = []
    hooks = {r["id"]: r for r in csv.DictReader(open(tsv), delimiter="\t")}
    p = connect().GetProjectManager().GetCurrentProject()
    mp = p.GetMediaPool(); rootf = mp.GetRootFolder()
    tls = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)}
    for path in sorted(glob.glob(f"{root}/{os.environ.get('AE_PREFIX', 'k')}*/clip.json")):
        c = json.load(open(path)); cid = c["id"]
        if only and cid not in only or cid not in hooks:
            continue
        t = tls.get(f"{cid} {c['slug']} 9x16{os.environ.get('AE_TL_SUFFIX', '')}")
        if not t:
            print(cid, "no 9x16 timeline"); continue
        p.SetCurrentTimeline(t)
        n = t.GetEndFrame() - t.GetStartFrame()
        h = hooks[cid]
        text = " ".join(x for x in (h["top"], h["mid"], h["big"]) if x).upper()
        lines = wrap(text, EM)
        if h.get("line"):  # hand-set breaks ("|"), kept unless a line is too wide
            hand = [x.strip() for x in h["line"].split("|")]
            f = ImageFont.truetype(FILE, round(EM * REND))
            if all(f.getlength(x) <= MAXW for x in hand):
                lines = hand
            else:
                print(f"  {cid}: hand line too wide, auto-wrapped")
            text = " ".join(hand)
        # reuse the hook title already on V2 and just retext it: deleting these titles crashes Resolve
        if t.GetTrackCount("video") < 2:
            t.AddTrack("video")             # a wrap built from a line-only tsv has no hook track yet
        have = t.GetItemListInTrack("video", 2) or []
        it = have[0] if have else place_title(mp, rootf, t, "Smooth Word Up", 2, 0, n)
        comp = None
        for _ in range(30):
            comp = it.GetFusionCompByIndex(1)
            if comp and comp.FindTool("Template"):
                break
            time.sleep(0.2)
        tool = comp.FindTool("Template")
        if tool.StyledText.GetConnectedOutput():
            tool.StyledText.ConnectTo(None)          # drop the word-follower: static text, no entrance
        tool.SetInput("StyledText", "\n".join(lines))
        tool.SetInput("Font", FONT); tool.SetInput("Style", STYLE)
        tool.SetInput("Size", EM / SIZE_PX)
        tool.SetInput("Red1", 1.0); tool.SetInput("Green1", 1.0); tool.SetInput("Blue1", 1.0); tool.SetInput("Alpha1", 1.0)
        tool.SetInput("Enabled3", 0)              # no shadow on the black band
        tool.SetInput("LineSpacing", 1.0)
        pitch = EM * LINE
        cap = EM * REND * 0.72                 # cap height of the last line
        last_c = PIC_TOP - GAP - cap / 2        # centre of the last line
        cy = last_c - (len(lines) - 1) * pitch / 2
        fw = ImageFont.truetype(FILE, round(EM * REND))
        wmax = max(fw.getlength(x) for x in lines)
        why = safezone.check(f"{cid} hook", (1080 - wmax) / 2, last_c - (len(lines) - 1) * pitch - cap / 2,
                             (1080 + wmax) / 2, last_c + cap / 2)
        if why:
            unsafe.append(why); print("  FAIL", why, f"({len(lines)} lines: shorten the hook)")
        it.SetName(text)
        it.SetProperty({"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 0, "Tilt": round(H / 2 - cy)})
        print(cid, " / ".join(lines), "OK" if tool.GetInput("StyledText") == "\n".join(lines) else "TEXT NOT SET")
    if unsafe:
        sys.exit(f"{len(unsafe)} hook(s) outside the IG safe zone (SOP 07). Shorten them and rerun.")


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]), sys.argv[2], set(sys.argv[3:]) or None)
