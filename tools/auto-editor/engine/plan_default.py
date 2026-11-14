"""Starter plan.json from phrases (captions only, every line A-roll). The planner then adds b-roll + modes.
Usage: python3 plan_default.py <job_dir>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from phrases import split
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
job = os.path.abspath(sys.argv[1]); name = os.path.basename(job)
meta = json.load(open(f"{job}/job.json")); W = json.load(open(f"{job}/words.json"))
style = json.load(open(f"{HOME}/styles/{meta['style']}/style.json"))
for w in W:
    w.setdefault("norm", w["w"].lower())
P = split(W, style["phrases"]); json.dump(P, open(f"{job}/phrases.json", "w"), indent=1)
segs, k = [], 0
for p in P:
    n = len(p["words"]); segs.append({"words": [k, k + n - 1], "caption": p["text"], "mode": "over_aroll", "broll": None}); k += n
json.dump(dict(project=f"{name} auto", timeline=f"{name} v1", style=meta["style"], fps=meta["fps"], w=meta["w"], h=meta["h"],
               aroll=meta["aroll"], segments=segs), open(f"{job}/plan.json", "w"), indent=1)
print(len(segs), "segments")
