"""Render every '<id> <slug> v2' timeline of the open project to H.264 mp4 at timeline res. Usage: python3 render_v2.py <out dir>"""
import sys, time
from resolve import connect
out = sys.argv[1]
r = connect(); p = r.GetProjectManager().GetCurrentProject()
r.OpenPage("deliver")
p.SetCurrentRenderFormatAndCodec("mp4", "H264")
jobs = []
for k in range(1, p.GetTimelineCount() + 1):
    t = p.GetTimelineByIndex(k)
    n = t.GetName()
    if not n.endswith(" v2"):
        continue
    p.SetCurrentTimeline(t)
    p.SetRenderSettings({"SelectAllFrames": 1, "TargetDir": out, "CustomName": n[:-3], "FormatWidth": 1080, "FormatHeight": 1350,
                         "ExportVideo": True, "ExportAudio": True, "AudioCodec": "aac", "AudioBitDepth": 16, "AudioSampleRate": 48000})
    jobs.append(p.AddRenderJob())
print(len(jobs), "jobs", flush=True)
p.StartRendering(jobs, False)
while p.IsRenderingInProgress():
    time.sleep(5)
for j in jobs:
    st = p.GetRenderJobStatus(j)
    print(st.get("JobStatus"), st.get("CompletionPercentage"), flush=True)
    p.DeleteRenderJob(j)
r.OpenPage("edit")
