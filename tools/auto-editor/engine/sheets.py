"""Contact sheets for labeling: 8 clips per sheet, one row each (3 frames), id burned in.
Usage: python3 sheets.py   (only clips not yet labeled and not yet on a sheet)"""
import json, os, subprocess
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IDX = f"{HOME}/index"
SH = f"{IDX}/sheets"; os.makedirs(SH, exist_ok=True)
rows = [json.loads(l) for l in open(f"{IDX}/clips.jsonl")]
labeled = set()
if os.path.exists(f"{IDX}/labels.jsonl"):
    labeled = {json.loads(l)["id"] for l in open(f"{IDX}/labels.jsonl") if l.strip()}
onsheet = set()
for f in os.listdir(SH):
    if f.endswith(".json"):
        onsheet |= set(json.load(open(f"{SH}/{f}")))
todo = [r for r in rows if "id" in r and len(r.get("thumbs", [])) == 3 and r["id"] not in labeled and r["id"] not in onsheet]
n0 = len([f for f in os.listdir(SH) if f.endswith(".jpg")])
for k in range(0, len(todo), 8):
    batch = todo[k:k + 8]
    name = f"{SH}/s{n0 + k // 8:04d}"
    inputs, filt = [], []
    for j, r in enumerate(batch):
        for t in r["thumbs"]:
            inputs += ["-i", f"{IDX}/thumbs/{t}"]
    for j in range(len(batch) * 3):
        filt.append(f"[{j}:v]scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2[f{j}]")
    for j, r in enumerate(batch):
        filt.append(f"[f{3*j}][f{3*j+1}][f{3*j+2}]hstack=3,pad=1040:180:80:0,drawtext=text='{r['id']}':x=4:y=80:fontsize=11:fontcolor=yellow[r{j}]")
    filt.append("".join(f"[r{j}]" for j in range(len(batch))) + f"vstack={len(batch)}[out]" if len(batch) > 1 else "[r0]null[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", "-q:v", "4", name + ".jpg"])
    json.dump([r["id"] for r in batch], open(name + ".json", "w"))
print(len(todo), "clips ->", (len(todo) + 7) // 8, "sheets")
