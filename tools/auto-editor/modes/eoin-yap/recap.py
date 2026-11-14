"""Re-apply the caption comps on the newest yap timeline in place (same clips, new look), no rebuild, nothing deleted.
Usage: python3 recap.py a b"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_yap as B
from resolve import connect
p = connect().GetProjectManager().GetCurrentProject()
tls = [p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)]
for take in sys.argv[1:]:
    T = B.TAKES[take]
    t = sorted((x for x in tls if x.GetName().startswith(f"Yap {take} v") and x.GetName().endswith(T["name"])), key=lambda x: x.GetName())[-1]
    _, W_, total = B.plan(take)
    caps, items = B.cap_plan(W_, total), t.GetItemListInTrack("video", 3)
    if len(caps) != len(items):
        sys.exit(f"{t.GetName()}: {len(items)} caption clips vs {len(caps)} planned, rebuild instead")
    for j, ((a, b, ch, s), it) in enumerate(zip(caps, items)):
        B.attach(it, B.caption_comp(it.GetDuration(), s, []), os.path.join(B.JOB, f"yap-{take}", "comps", f"cap_{j:03d}.comp"))
    print(take, t.GetName(), len(items), "captions re-applied")
