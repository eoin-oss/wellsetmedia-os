"""Delete timelines by name from the open project (switches away first: deleting the open one crashed Resolve).
Usage: python3 rmtl.py <name prefix> [...]"""
import sys
from resolve import connect
p = connect().GetProjectManager().GetCurrentProject()
tls = [p.GetTimelineByIndex(k) for k in range(1, p.GetTimelineCount() + 1)]
kill = [t for t in tls if any(t.GetName().startswith(x) for x in sys.argv[1:])]
keep = [t for t in tls if t not in kill]
if keep and p.GetCurrentTimeline().GetName() in {t.GetName() for t in kill}:
    p.SetCurrentTimeline(keep[0])
print([t.GetName() for t in kill], p.GetMediaPool().DeleteTimelines(kill) if kill else None)
