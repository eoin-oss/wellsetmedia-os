"""Delete a job's timeline from its shared project and build it again.  Usage: python3 rebuild.py <job_dir>..."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from resolve import connect

for job in sys.argv[1:]:
    plan = json.load(open(f"{job}/plan.json"))
    p = connect().GetProjectManager().GetCurrentProject()
    assert p.GetName() == plan["project"], p.GetName()
    old = [p.GetTimelineByIndex(k) for k in range(1, p.GetTimelineCount() + 1)]
    old = [t for t in old if t.GetName() == plan["timeline"]]
    if old:
        p.GetMediaPool().DeleteTimelines(old)
    subprocess.run([sys.executable, f"{os.path.dirname(__file__)}/build.py", job], check=True)
