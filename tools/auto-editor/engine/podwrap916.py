"""9:16 delivery for podcast-sidecap clips: the finished 4:5 cut (its ProRes master from render_tls.py, 1080x1350,
placed at its own size, no scaling; nesting the timeline doesn't work: Resolve renders a nested timeline as 16:9)
inside a 1080x1920 timeline, sitting low, with the text hook in the black band above it for the whole clip.
Hook rows (caps / script / BIG caps) come from the job's text-hooks.tsv, built as Motion Text Pro titles (Hook 1-3).
Usage: python3 podwrap916.py <job root> <text-hooks.tsv> <masters dir> [ids]   (masters named "<id> <slug>.mov")
Makes "<id> <slug> 9x16"; reruns replace it."""
import csv, glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("AE_MODE", "podcast-sidecap")
from resolve import connect, find_clip

from podhooks_sidecap import fit, set_text, place_title, ROWS, GAP
from podbuild_sidecap import put

W, H, IH = 1080, 1920, 1350
HOOK_BOTTOM = 372                      # last hook row ends here, just above the picture's top edge
# 23 Oct: hook + picture sit as one centred block, clear of the IG reels header (~230px) and the caption bar:
# picture top 478, bottom 1630 (4:5 cropped at the bottom to 1080x1152). Tilt moves ~0.70px per unit (measured).
PIC_TILT, PIC_CROP_BOTTOM = -275, 198
PREFIX = os.environ.get("AE_PREFIX", "k")   # clip-dir prefix: k = Kyle job, j = James job
TL_SUFFIX = os.environ.get("AE_TL_SUFFIX", "")  # e.g. " qc27": a fix pass gets its own timeline, the delivered one stays


def find_tl_item(folder, name):
    for c in folder.GetClipList() or []:
        if c.GetName() == name and c.GetClipProperty("Type") == "Timeline":
            return c
    for s in folder.GetSubFolderList() or []:
        hit = find_tl_item(s, name)
        if hit:
            return hit
    return None


def main(root, tsv, masters, only=None):
    hooks = {r["id"]: r for r in csv.DictReader(open(tsv), delimiter="\t")}
    p = connect().GetProjectManager().GetCurrentProject()
    mp = p.GetMediaPool(); rootf = mp.GetRootFolder()
    tls = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)}
    folder = next((f for f in rootf.GetSubFolderList() or [] if f.GetName() == "9x16"), None) or mp.AddSubFolder(rootf, "9x16")
    for path in sorted(glob.glob(f"{root}/{PREFIX}*/clip.json")):
        c = json.load(open(path)); cid = c["id"]
        if only and cid not in only:
            continue
        out_name = f"{cid} {c['slug']} 9x16{TL_SUFFIX}"
        mfile = os.path.join(masters, f"{cid} {c['slug']}.mov")
        if not os.path.exists(mfile):
            print(cid, "no master", mfile); continue
        if out_name in tls:  # rerun: switch away, then delete the old wrapper
            p.SetCurrentTimeline(next(x for nm, x in tls.items() if nm != out_name))
            mp.DeleteTimelines([tls[out_name]])
        mp.SetCurrentFolder(folder)
        item = next((x for x in folder.GetClipList() or [] if x.GetClipProperty("File Path") == mfile), None)
        if item:  # a re-rendered master: drop the stale media pool copy so the new file is read
            mp.DeleteClips([item])
        item = mp.ImportMedia([mfile])[0]
        t = mp.CreateEmptyTimeline(out_name)
        for k, v in (("useCustomSettings", "1"), ("timelineResolutionWidth", str(W)), ("timelineResolutionHeight", str(H)),
                     ("timelineFrameRate", "25"), ("timelineInputResMismatchBehavior", "scaleToFit"),
                     ("timelineOutputResMismatchBehavior", "scaleToFit")):
            t.SetSetting(k, v)
        p.SetCurrentTimeline(t)
        n = int(item.GetClipProperty("Frames"))
        p.SetCurrentTimeline(t)
        mp.AppendToTimeline([{"mediaPoolItem": item, "startFrame": 0, "endFrame": n - 1, "trackIndex": 1, "recordFrame": t.GetStartFrame()}])
        vids = [x for x in (t.GetItemListInTrack("video", 1) or [])]
        for v in vids:
            v.SetProperty({"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 0, "Tilt": PIC_TILT, "CropBottom": PIC_CROP_BOTTOM})
        h = hooks.get(cid)
        ok = []
        if h and h.get("top"):  # the 3-row stacked hook; tsvs with only a "line" column get their hook from podhook916_plain/gold
            for _ in range(3):
                t.AddTrack("video")
            for k in range(2, 5):
                t.SetTrackName("video", k, f"Hook {k - 1}")
            rows = [(h[key], kind, fit(h[key], kind, em), anim, lead) for key, kind, em, anim, lead in ROWS]
            heights = [em * (1.05 if kind == "script" else 0.9) for _, kind, em, _, _ in rows]
            y = HOOK_BOTTOM - sum(heights) - GAP * 2
            for (text, kind, em, anim, lead), hgt, k in zip(rows, heights, (2, 3, 4)):
                cy = y + hgt / 2; y += hgt + GAP
                it = place_title(mp, rootf, t, anim, k, round(lead * 25), n)
                good = bool(it) and set_text(it, text, kind, em)
                if it:
                    it.SetProperty({"ZoomX": 1.0, "ZoomY": 1.0, "Pan": 0, "Tilt": round(H / 2 - cy)})
                ok.append(good)
        print(cid, out_name, f"{n / 25:.1f}s", "pic" if vids else "NO PIC", "hook OK" if ok and all(ok) else f"hook {ok}")


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]), sys.argv[2], os.path.abspath(sys.argv[3]), set(sys.argv[4:]) or None)
