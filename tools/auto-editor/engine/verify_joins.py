"""Frame-exact jump-cut check on a built timeline: a join shows when the frames either side of it are both A-roll
(no b-roll on V2 over either). Usage: python3 verify_joins.py <job_dir>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from resolve import open_project

job = os.path.abspath(sys.argv[1])
plan = json.load(open(f"{job}/plan.json", encoding="utf-8"))
joins = json.load(open(f"{job}/joins.json", encoding="utf-8")) if os.path.exists(f"{job}/joins.json") else []
p = open_project(plan["project"])
t = next(p.GetTimelineByIndex(k) for k in range(1, p.GetTimelineCount() + 1) if p.GetTimelineByIndex(k).GetName() == plan["timeline"])
fps, t0 = plan["fps"], t.GetStartFrame()
b = [(i.GetStart(), i.GetEnd()) for i in t.GetItemListInTrack("video", 2) or []]
v1 = [(i.GetStart(), i.GetEnd(), i.GetProperty("ZoomX")) for i in t.GetItemListInTrack("video", 1) or []]
cov = lambda f: any(s <= f < e for s, e in b)
bad = []
for j in joins:
    J = t0 + int(round(j * fps))
    if not (cov(J - 1) or cov(J)):
        bad.append(j)
v1items = t.GetItemListInTrack("video", 1) or []
seams = [i.GetStart() for i in v1items[1:]]
intro_end = v1items[0].GetEnd() if v1items else None
open_seams = [round((f - t0) / fps, 2) for f in seams if f != intro_end and not (cov(f - 1) or cov(f))]
if open_seams:
    print("V1 SEAMS ON SCREEN:", open_seams)
print(os.path.basename(job), f"joins {len(joins) - len(bad)}/{len(joins)} hidden", "SHOWING:" if bad else "", bad,
      f"| V1 pieces {len(v1)} punched {sum(1 for x in v1 if x[2] and abs(x[2] - 1) > 0.01)}")
