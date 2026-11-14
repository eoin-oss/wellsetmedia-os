"""Dump a finished edit (every item, timing, source, caption text) + export its caption comps.
Usage: python3 dump_timeline.py "<project>" <out_dir>"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from resolve import open_project

proj, out = sys.argv[1], os.path.abspath(sys.argv[2])
os.makedirs(f"{out}/comps", exist_ok=True)
p = open_project(proj)
t = p.GetTimelineByIndex(1)
rows = []
for kind in ("video", "audio"):
    for tr in range(1, t.GetTrackCount(kind) + 1):
        for i, it in enumerate(t.GetItemListInTrack(kind, tr) or []):
            mpi = it.GetMediaPoolItem()
            row = dict(kind=kind, track=tr, name=it.GetName(), start=it.GetStart(), end=it.GetEnd(),
                       src_in=it.GetLeftOffset(), file=mpi.GetClipProperty("File Path") if mpi else None,
                       zoom=it.GetProperty("ZoomX"), pan=it.GetProperty("Pan"), tilt=it.GetProperty("Tilt"))
            if kind == "video" and it.GetFusionCompCount():
                comp = it.GetFusionCompByIndex(1)
                for tool in (comp.GetToolList(False) or {}).values():
                    if tool.GetAttrs().get("TOOLS_RegID") == "TextPlus":
                        row["text"] = tool.GetInput("StyledText")
                        row["size"] = tool.GetInput("Size")
                        row["font"] = f'{tool.GetInput("Font")} {tool.GetInput("Style")}'
                path = f"{out}/comps/V{tr}_{i:03d}.comp"
                it.ExportFusionComp(path, 1)
                row["comp"] = os.path.basename(path)
            rows.append(row)
json.dump(dict(project=proj, fps=t.GetSetting("timelineFrameRate"), start=t.GetStartFrame(),
               w=t.GetSetting("timelineResolutionWidth"), h=t.GetSetting("timelineResolutionHeight"), items=rows),
          open(f"{out}/timeline.json", "w"), indent=1)
print(len(rows), "items ->", out)
