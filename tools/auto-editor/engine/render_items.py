"""Render every V1 item of one timeline as its own file (mark in/out per item), so a batch can share one timeline,
e.g. one Fairlight limiter on the main bus for a whole loudness pass (QC, SOP 12).
Output is named after the item ("k13 just-feel-confident.mov" -> "k13 just-feel-confident.mp4"), or, with a names dir,
after the file in it that carries the same clip id ("16 Tue 27 1700 k13 just-feel-confident.mp4").
Usage: python3 render_items.py "<timeline name>" <out dir> [names dir]"""
import os, re, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from resolve import connect


def main(name, out, names=None):
    r = connect(); p = r.GetProjectManager().GetCurrentProject()
    t = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == name), None)
    if not t:
        sys.exit(f"no timeline {name!r}")
    p.SetCurrentTimeline(t)
    out = os.path.abspath(out); os.makedirs(out, exist_ok=True)
    pool = [f for f in os.listdir(names) if f.lower().endswith((".mp4", ".mov"))] if names else []
    jobs = []
    for it in t.GetItemListInTrack("video", 1) or []:
        stem = os.path.splitext(it.GetName())[0]
        cid = re.match(r"([a-z]\d+)", stem)
        hit = next((f for f in pool if cid and re.search(rf"\b{cid.group(1)}\b", f)), None)
        nm = os.path.splitext(hit)[0] if hit else stem
        p.SetCurrentRenderFormatAndCodec("mp4", "H264")
        p.SetRenderSettings({"SelectAllFrames": 0, "MarkIn": it.GetStart(), "MarkOut": it.GetEnd() - 1, "TargetDir": out,
                             "CustomName": nm, "ExportVideo": True, "ExportAudio": True,
                             "FormatWidth": int(t.GetSetting("timelineResolutionWidth")),
                             "FormatHeight": int(t.GetSetting("timelineResolutionHeight"))})
        jobs.append(p.AddRenderJob())
        print("queued", nm, flush=True)
    p.StartRendering(jobs, False)
    while p.IsRenderingInProgress():
        time.sleep(3)
    for j in jobs:
        st = p.GetRenderJobStatus(j) or {}
        if st.get("JobStatus") != "Complete":
            print("!", j, st)
        p.DeleteRenderJob(j)
    print("done", len(jobs))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
