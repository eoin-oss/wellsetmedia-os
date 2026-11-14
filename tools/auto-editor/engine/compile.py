"""Review reel: nest every built timeline in one timeline with black gaps, render it.
Usage: python3 compile.py "<project>" "<review timeline name>" <out_dir> <gap_sec> <timeline name> [<timeline name> ...]
       python3 compile.py --each "<project>" <out_dir> <timeline name> [...]   (render each timeline as its own file)"""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from resolve import open_project


def find_tl(p, name):
    for k in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(k)
        if t.GetName() == name:
            return t
    return None


def tl_item(folder, name):
    for c in folder.GetClipList() or []:
        if c.GetName() == name and c.GetClipProperty("Type") == "Timeline":
            return c
    for s in folder.GetSubFolderList() or []:
        hit = tl_item(s, name)
        if hit:
            return hit
    return None


def render(p, t, out, name):
    p.SetCurrentTimeline(t)
    p.SetCurrentRenderFormatAndCodec("mp4", "H264")
    p.SetRenderSettings({"SelectAllFrames": True, "TargetDir": out, "CustomName": name, "FormatWidth": int(p.GetSetting("timelineResolutionWidth")),
                         "FormatHeight": int(p.GetSetting("timelineResolutionHeight")), "ExportVideo": True, "ExportAudio": True})
    j = p.AddRenderJob()
    p.StartRendering([j])
    while p.IsRenderingInProgress():
        time.sleep(3)
    st = p.GetRenderJobStatus(j)
    p.DeleteRenderJob(j)
    return st


if sys.argv[1] == "--each":
    proj, out, names = sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4:]
    os.makedirs(out, exist_ok=True)
    p = open_project(proj)
    for n in names:
        t = find_tl(p, n)
        print(n, render(p, t, out, n) if t else "MISSING")
    sys.exit()

proj, review, out, gap, names = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), float(sys.argv[4]), sys.argv[5:]
os.makedirs(out, exist_ok=True)
p = open_project(proj)
mp = p.GetMediaPool()
root = mp.GetRootFolder()
old = find_tl(p, review)
if old:
    mp.DeleteTimelines([old])
mp.SetCurrentFolder(root)
rt = mp.CreateEmptyTimeline(review)
p.SetCurrentTimeline(rt)
fps = float(rt.GetSetting("timelineFrameRate"))
rec = rt.GetStartFrame()
for n in names:
    item = tl_item(root, n)
    if not item:
        print("MISSING", n); continue
    res = mp.AppendToTimeline([{"mediaPoolItem": item, "trackIndex": 1, "recordFrame": rec}])
    if not res:
        print("APPEND FAIL", n); continue
    rec = res[0].GetEnd() + int(round(gap * fps))  # empty track = black between videos
    print("+", n, res[0].GetDuration())
print(render(p, rt, out, review))
