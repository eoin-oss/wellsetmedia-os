"""Render the newest 'VSL v*' timeline of the open project through Deliver, then measure the file's loudness.
H.264 MP4, 1920x1080, 25fps, ~25 Mbps, AAC. Target -14 LUFS integrated, true peak <= -1 dBTP.
Usage: python3 render_vsl.py <out dir> [name]"""
import os, re, subprocess, sys, time
import rv


def newest(p):
    best, bv = None, -1
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        m = re.match(r"VSL v(\d+)$", t.GetName())
        if m and int(m.group(1)) > bv:
            best, bv = t, int(m.group(1))
    return best


def loudness(path):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
    pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)[-1])
    return i, pk


def render(out, name="VSL"):
    r = rv.connect(); p = r.GetProjectManager().GetCurrentProject()
    t = newest(p)
    p.SetCurrentTimeline(t)
    p.LoadRenderPreset("H.264 Master")     # resets any stale Deliver state (an audio-only setting once stuck and dropped the video)
    p.SetCurrentRenderFormatAndCodec("mp4", "H264")
    p.SetRenderSettings({"SelectAllFrames": 1, "MarkIn": t.GetStartFrame(), "MarkOut": t.GetEndFrame() - 1, "TargetDir": out, "CustomName": name, "ExportVideo": True, "ExportAudio": True,
                         "FormatWidth": 1920, "FormatHeight": 1080, "FrameRate": 25, "VideoQuality": 25000,
                         "AudioCodec": "aac", "AudioBitDepth": 16, "AudioSampleRate": 48000})
    j = p.AddRenderJob()
    p.StartRendering([j], False)
    while p.IsRenderingInProgress():
        time.sleep(3)
    st = p.GetRenderJobStatus(j) or {}
    p.DeleteRenderJob(j)
    r.OpenPage("edit")
    path = os.path.join(out, name + ".mp4")
    print(t.GetName(), st.get("JobStatus"), st.get("TimeTakenToRenderInMs"), path)
    v = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name,width,height,r_frame_rate",
                        "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    if not v.startswith("h264,1920,1080,25/1"):
        sys.exit(f"render has no proper video stream: {v!r}")
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True).stdout)
    tl = (t.GetEndFrame() - t.GetStartFrame()) / 25
    if abs(d - tl) > 0.5:
        sys.exit(f"render is {d:.1f}s, timeline is {tl:.1f}s")
    print("video", v, f"{d:.1f}s")
    return path


if __name__ == "__main__":
    out = os.path.abspath(os.path.expanduser(sys.argv[1]))
    path = render(out, sys.argv[2] if len(sys.argv) > 2 else "VSL")
    i, pk = loudness(path)
    print(f"loudness {i:.1f} LUFS, true peak {pk:.1f} dBTP")
