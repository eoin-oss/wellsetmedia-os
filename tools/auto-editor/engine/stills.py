"""Render stills of the CURRENT timeline through Deliver (no Fusion popups): one job per timestamp, JPEG.
Usage: python3 stills.py <out dir> <sec> [<sec> ...]   (timeline seconds)"""
import os, sys, time, glob
from resolve import connect


def stills(out, secs, fps=25, width=1920, height=1080):
    r = connect(); p = r.GetProjectManager().GetCurrentProject(); t = p.GetCurrentTimeline()
    os.makedirs(out, exist_ok=True)
    codec = list(p.GetRenderCodecs("jpg").values())[0]
    p.SetCurrentRenderFormatAndCodec("jpg", codec)
    t0, jobs = t.GetStartFrame(), []
    for s in secs:
        f = t0 + round(s * fps)
        p.SetRenderSettings({"SelectAllFrames": 0, "MarkIn": f, "MarkOut": f, "TargetDir": out,
                             "CustomName": f"t{s:06.2f}_", "FormatWidth": width, "FormatHeight": height, "ExportAlpha": False})
        jobs.append(p.AddRenderJob())
    p.StartRendering(jobs, False)
    while p.IsRenderingInProgress():
        time.sleep(1)
    for j in jobs:
        p.DeleteRenderJob(j)
    r.OpenPage("edit")
    return sorted(glob.glob(os.path.join(out, "t*.jpg")))


if __name__ == "__main__":
    print("\n".join(stills(sys.argv[1], [float(x) for x in sys.argv[2:]])))
