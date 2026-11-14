"""Swap the title card comp on existing yap timelines in place (no new timelines, nothing deleted).
Usage: python3 retitle.py a b"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_yap as B
from resolve import connect
p = connect().GetProjectManager().GetCurrentProject()
tls = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
for take in sys.argv[1:]:
    T = B.TAKES[take]
    mine = sorted((t for t in tls if t.GetName().startswith(f"Yap {take} v") and t.GetName().endswith(T["name"])), key=lambda t: t.GetName())
    t = mine[-1]  # newest version
    it = t.GetItemListInTrack("video", 2)[0]
    src = B.title_comp(it.GetDuration(), *T["title"])
    B.attach(it, src, os.path.join(B.JOB, f"yap-{take}", "comps", "beat_00.comp"))
    print(take, t.GetName(), "title swapped")
