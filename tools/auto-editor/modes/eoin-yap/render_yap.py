"""Render the newest `Yap <take> v*` timeline of each take through Deliver at master quality.
H.264 MP4, 1080x1920, 30fps, ~40 Mbps (source is ~9.3 Mbps HEVC, so nothing is lost), AAC 320k.
Usage: python3 render_yap.py <out dir> a b"""
import os, re, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "engine"))
from resolve import connect
from beats import TAKES


def newest(p, take):
    best, bv = None, -1
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        m = re.match(rf"Yap {take}(?: v(\d+))? ·", t.GetName())
        if m and int(m.group(1) or 1) > bv:
            best, bv = t, int(m.group(1) or 1)
    return best


def main(out, takes):
    r = connect(); p = r.GetProjectManager().GetCurrentProject()
    assert p.GetName().lower() == "my yap", p.GetName()
    out = os.path.abspath(os.path.expanduser(out))
    jobs = []
    for k in takes:
        t = newest(p, k)
        p.SetCurrentTimeline(t)
        p.SetCurrentRenderFormatAndCodec("mp4", "H264")
        p.SetRenderSettings({"SelectAllFrames": 1, "TargetDir": out, "CustomName": TAKES[k]["name"],
                             "ExportVideo": True, "ExportAudio": True, "FormatWidth": 1080, "FormatHeight": 1920,
                             "FrameRate": 30, "VideoQuality": 40000, "AudioCodec": "aac", "AudioBitDepth": 16,
                             "AudioSampleRate": 48000, "ColorSpaceTag": "Same as Project", "GammaTag": "Same as Project"})
        jobs.append(p.AddRenderJob())
        print("queued", t.GetName(), flush=True)
    p.StartRendering(jobs, False)
    while p.IsRenderingInProgress():
        time.sleep(3)
    for j in jobs:
        st = p.GetRenderJobStatus(j) or {}
        print(st.get("JobStatus"), st.get("TimeTakenToRenderInMs"))
        p.DeleteRenderJob(j)
    r.OpenPage("edit")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or ["a", "b"])
