"""Snapshot what's on each timeline of the open project (Eoin's manual edits survive rebuilds): per track, every item's
name, media path, record start/end (timeline frames from 0), source in/out and transform properties.
Usage: python3 snapshot_tl.py <out.json> [name prefix ...]"""
import json, sys
from resolve import connect
PROPS = ("Pan", "Tilt", "ZoomX", "ZoomY", "RotationAngle", "AnchorPointX", "AnchorPointY", "FlipX", "FlipY", "CropLeft", "CropRight",
         "CropTop", "CropBottom", "Opacity")
p = connect().GetProjectManager().GetCurrentProject()
out = {}
for k in range(1, p.GetTimelineCount() + 1):
    t = p.GetTimelineByIndex(k)
    if len(sys.argv) > 2 and not any(t.GetName().startswith(x) for x in sys.argv[2:]):
        continue
    t0, tl = t.GetStartFrame(), {"tracks": {}}
    for kind in ("video", "audio"):
        for i in range(1, t.GetTrackCount(kind) + 1):
            items = []
            for it in t.GetItemListInTrack(kind, i) or []:
                mpi = it.GetMediaPoolItem()
                d = dict(name=it.GetName(), start=it.GetStart() - t0, end=it.GetEnd() - t0,
                         path=mpi.GetClipProperty("File Path") if mpi else "",
                         src_in=it.GetSourceStartFrame(), src_out=it.GetSourceEndFrame())
                if kind == "video":
                    d["props"] = {pr: it.GetProperty(pr) for pr in PROPS}
                items.append(d)
            tl["tracks"][f"{kind[0].upper()}{i}"] = items
    out[t.GetName()] = tl
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(len(out), "timelines")
