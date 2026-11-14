"""Resolve-side helpers for the VSL mode (same carrier/attach rules as modes/eoin-yap/build_yap.py, without its
9:16 module globals)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "../../engine"))
from resolve import connect, find_clip

MTP_DRB = "/Volumes/Extreme SSD/personal brand directory/asssets/Motiontext-pro-v1/davinci-resolve-version21+/MotionText Pro V1.drb"


def carrier(mp):
    c = find_clip(mp.GetRootFolder(), "Smooth Word Up")
    if not c:
        mp.ImportFolderFromFile(MTP_DRB)
        c = find_clip(mp.GetRootFolder(), "Smooth Word Up")
    if not c:
        sys.exit("MotionText Pro carrier not found")
    return c


def place(mp, t, carrier, rec, d, track, fps):
    """a title of exactly d timeline frames at rec (the carrier is 24fps, so try nearby spans)"""
    cfps = float(carrier.GetClipProperty("FPS") or fps) or fps
    est = d * cfps / fps
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
    if best:
        res = mp.AppendToTimeline([{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": best[0], "trackIndex": track, "recordFrame": rec}])
        return res[0] if res else None
    return None


def check_comp(src, path):
    """refuse any comp that could hang Fusion on import: repeated node names, dangling or self links"""
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


def still(p, t, sec, path, fps):
    import time
    f = t.GetStartFrame() + int(round(sec * fps))
    fr = int(round(fps))
    hh, rem = divmod(f, fr * 3600); mm, rem = divmod(rem, fr * 60); ss, ff = divmod(rem, fr)
    t.SetCurrentTimecode(f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}")
    time.sleep(1.0)
    ok = p.ExportCurrentFrameAsStill(path)
    if not ok:
        time.sleep(1.5); ok = p.ExportCurrentFrameAsStill(path)
    return ok
