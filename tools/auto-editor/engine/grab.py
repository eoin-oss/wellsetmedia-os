"""Export stills of the current timeline at given seconds. Usage: python3 grab.py <out_dir> <sec> [<sec>...]"""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from resolve import connect

r = connect()
p = r.GetProjectManager().GetCurrentProject()
t = p.GetCurrentTimeline()
fps = float(t.GetSetting("timelineFrameRate"))
out = os.path.abspath(sys.argv[1]); os.makedirs(out, exist_ok=True)
r.OpenPage("edit")
for s in sys.argv[2:]:
    f = t.GetStartFrame() + int(float(s) * fps)
    hh, rem = divmod(f, int(round(fps)) * 3600); mm, rem = divmod(rem, int(round(fps)) * 60); ss, ff = divmod(rem, int(round(fps)))
    t.SetCurrentTimecode(f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}")
    time.sleep(1.5)
    path = f"{out}/t{float(s):06.2f}.jpg"
    print(s, p.ExportCurrentFrameAsStill(path), path)
