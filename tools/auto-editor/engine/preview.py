"""Render frames of one timeline item's Fusion comp (inside Resolve) to PNGs for a quick visual check.
Usage: python3 preview.py <track> <timeline sec> [<sec> ...] -> out dir from $PREVIEW_DIR"""
import os, sys
from resolve import connect

def render(track, secs, out, fps=25, timeline="resonance lab"):
    r = connect(); p = r.GetProjectManager().GetCurrentProject()
    t = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(i).GetName() == timeline)
    t0, paths = t.GetStartFrame(), []
    for s in secs:
        f = t0 + round(s * fps)
        it = next((i for i in t.GetItemListInTrack("video", track) or [] if i.GetStart() <= f < i.GetEnd()), None)
        if not it:
            paths.append(None); continue
        comp = it.GetFusionCompByIndex(1)
        a = comp.GetAttrs()
        cf = int(a["COMPN_GlobalStart"]) + (f - it.GetStart())
        sv = comp.AddTool("Saver", -32768, -32768)
        sv.Input = comp.FindTool("MediaOut1").Input.GetConnectedOutput()
        name = f"{out}/v{track}_{s:06.2f}_.png"
        sv.Clip = name
        comp.Render({"Start": cf, "End": cf, "Wait": True})
        sv.Delete()
        got = name.replace("_.png", f"_{cf:04d}.png")
        paths.append(got if os.path.exists(got) else None)
    return paths

if __name__ == "__main__":
    print(render(int(sys.argv[1]), [float(x) for x in sys.argv[2:]], os.environ.get("PREVIEW_DIR", "/tmp")))
