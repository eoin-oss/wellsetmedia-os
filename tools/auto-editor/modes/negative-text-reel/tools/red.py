"""Lines that can't be read in negative (bright, busy shots) go solid red, normal composite.
extras.json: "red": ["caption line", ...]   Run after build, or any time in place. Usage: python3 red.py <job>"""
from _common import job_dir, extras
from resolve import connect
want = set(extras(job_dir()).get("red", []))
r = connect(); t = r.GetProjectManager().GetCurrentProject().GetCurrentTimeline(); n = 0
for tr in (3, 4, 5):
    for it in t.GetItemListInTrack("video", tr) or []:
        c = it.GetFusionCompByIndex(1)
        tp = list((c.GetToolList(False, "TextPlus") or {}).values()) if c else []
        if tp and tp[0].GetInput("StyledText") in want:
            for x in tp:
                x.SetInput("Red1", 1.0); x.SetInput("Green1", 0.12); x.SetInput("Blue1", 0.12)
            it.SetProperty("CompositeMode", 0); n += 1
r.GetProjectManager().SaveProject(); print("red lines", n)
