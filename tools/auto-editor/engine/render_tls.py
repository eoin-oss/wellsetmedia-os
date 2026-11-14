"""Queue + render whole timelines of the open project through Deliver, one file per timeline named after it.
Machine QC runs on every render (SOP 06/07): a timeline with banned music is not rendered, and preflight.py writes
qc-report-render-<time>.md into <out dir> for the files just rendered. AE_NO_QC=1 skips both (intermediate renders only).
Usage: python3 render_tls.py <out dir> <mov|mp4> <codec key e.g. ProRes422HQ|H264> <name suffix to match> [ids]"""
import os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from resolve import connect
import music_guard


def main(out, fmt, codec, suffix, only=None):
    r = connect(); p = r.GetProjectManager().GetCurrentProject()
    out = os.path.abspath(out)
    os.makedirs(out, exist_ok=True)
    tls = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
    tls = [t for t in tls if t.GetName().endswith(suffix) and (not only or t.GetName().split()[0] in only)]
    qc = not os.environ.get("AE_NO_QC")
    ban = music_guard.banned() if qc else []
    jobs, blocked, made = [], [], []
    for t in tls:
        hits = music_guard.check_timeline(t, ban) if qc else []
        if hits:
            blocked.append(t.GetName())
            print(f"FAIL  {t.GetName()}: banned music " + ", ".join(f"A{tr} {n}" for tr, n in hits) + " (not rendered)", flush=True)
            continue
        p.SetCurrentTimeline(t)
        p.SetCurrentRenderFormatAndCodec(fmt, codec)
        name = t.GetName()[: -len(suffix)].strip() if suffix else t.GetName()
        p.SetRenderSettings({"SelectAllFrames": 1, "TargetDir": out, "CustomName": name, "ExportVideo": True, "ExportAudio": True,
                             "FormatWidth": int(t.GetSetting("timelineResolutionWidth")),
                             "FormatHeight": int(t.GetSetting("timelineResolutionHeight"))})
        jobs.append(p.AddRenderJob())
        made.append(os.path.join(out, f"{name}.{fmt}"))
    print(f"queued {len(jobs)}", flush=True)
    p.StartRendering(jobs, False)
    while p.IsRenderingInProgress():
        time.sleep(3)
    for j in jobs:
        st = p.GetRenderJobStatus(j) or {}
        if st.get("JobStatus") != "Complete":
            print("!", j, st)
        p.DeleteRenderJob(j)
    r.OpenPage("edit")
    print("done", len(jobs))
    if qc and jobs and fmt == "mp4":
        rc = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "preflight.py")] + [f for f in made if os.path.exists(f)],
                            env=dict(os.environ, PREFLIGHT_REPORT=time.strftime("qc-report-render-%Y%m%d-%H%M.md"))).returncode
        print("QC preflight:", "FAIL, fix before QC (SOP 07)" if rc else "clean. Human QC after a 1h break (SOP 07)")
    if blocked:
        print(f"{len(blocked)} timeline(s) blocked for banned music:", ", ".join(blocked))
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], set(sys.argv[5:]) or None)
