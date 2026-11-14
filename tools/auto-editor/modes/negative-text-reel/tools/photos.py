"""Photo b-roll as native Fusion comps on V2: Loader -> Merge onto a black 1080x1920 plate, sized to fill, slow 7%
push-in, timed exactly to its caption lines. (Stills appended by script ignore their out point and run long, so
photos never go in plan.json broll.)
extras.json: "photos": [["first caption line", "last caption line", "/path/photo.jpg"], ...]
Run after build (and silences.py). Usage: python3 photos.py <job>"""
import json, os
from PIL import Image
from _common import job_dir, extras, FPS
import fusion
from fusion import Comp, A
from resolve import connect, find_clip

fusion.W, fusion.H = 1080, 1920
job = job_dir(); X = extras(job)


def comp_for(path, n):
    pw, ph = Image.open(path).size
    c = Comp(n)
    bg = c.tool("Plate", "Background", {"Width": 1080, "Height": 1920, "UseFrameFormatSettings": 0, "TopLeftAlpha": 1})
    c.tool("Photo", "Loader", {})
    c.tools[-1] = ("Photo", c.tools[-1][1].replace("Inputs = {", "Clips = {\n\t\t\t\tClip {\n\t\t\t\t\tFilename = " + fusion.q(path) +
                                                     ",\n\t\t\t\t\tFormatID = \"JpegFormat\",\n\t\t\t\t\tLength = 1,\n\t\t\t\t\tLoop = 1,\n\t\t\t\t}\n\t\t\t},\n\t\t\tInputs = {", 1))
    fit = max(1920 / ph, 1080 / pw)
    c.merge("Fill", bg, "Photo", size=A(lambda f: fit * (1 + 0.07 * f / max(n, 1))))
    return c.text_out("Fill")


plan = json.load(open(os.path.join(job, "plan.json"))); W = json.load(open(os.path.join(job, "words.json")))
segs = plan["segments"]; caps = [s["caption"] for s in segs]; lead = 2 / FPS
r = connect(); p = r.GetProjectManager().GetCurrentProject(); t = p.GetCurrentTimeline(); mp = p.GetMediaPool(); t0 = t.GetStartFrame()
carrier = find_clip(mp.GetRootFolder(), "Smooth Word Up")
os.makedirs(os.path.join(job, "comps"), exist_ok=True)
for a, b, photo in X.get("photos", []):
    i, j = caps.index(a), caps.index(b)
    start = W[segs[i]["words"][0]]["start"] - lead
    end = (W[segs[j + 1]["words"][0]]["start"] - lead) if j + 1 < len(segs) else W[segs[j]["words"][1]]["end"] + 0.3
    rec, d = t0 + round(start * FPS), round((end - start) * FPS)
    span, item = d, None
    for _ in range(6):
        res = mp.AppendToTimeline([{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": span, "trackIndex": 2, "recordFrame": rec}])
        item = res[0] if res else None
        if not item:
            break
        got = item.GetDuration()
        if d - 2 <= got <= d:
            break
        t.DeleteClips([item]); item = None
        span += 1 if got < d - 2 else -1
    if not item:
        print("FAILED", photo); continue
    cp = os.path.join(job, "comps", "photo_" + os.path.splitext(os.path.basename(photo))[0] + ".comp")
    open(cp, "w", encoding="utf-8").write(comp_for(photo, d))
    item.ImportFusionComp(cp)
    names = item.GetFusionCompNameList() or []
    if len(names) > 1:
        item.LoadFusionCompByName(names[-1])
        for nm in names[:-1]:
            item.DeleteFusionCompByName(nm)
    item.SetClipColor("Teal")
    print("photo", os.path.basename(photo), round(start, 2), "->", round(end, 2))
r.GetProjectManager().SaveProject()
