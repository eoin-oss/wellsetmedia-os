"""Learn from Eoin's finishing pass: diff his finished timeline against the auto draft and log the corrections.
Usage: python3 learn.py <job_dir>     (run after he's finished the edit in the job's Resolve project)
Writes <job>/finished/ (dump), appends styles/<style>/corrections.jsonl, rewrites styles/<style>/LEARNED.md"""
import json, os, subprocess, sys, collections
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
job = os.path.abspath(sys.argv[1])
plan = json.load(open(f"{job}/plan.json"))
style_dir = f"{HOME}/styles/{plan['style']}"
subprocess.run([sys.executable, f"{HOME}/engine/dump_timeline.py", plan["project"], f"{job}/finished"], check=True)
fin = json.load(open(f"{job}/finished/timeline.json"))
fps, s0 = float(fin["fps"]), fin["start"]
clips = {json.loads(l)["path"]: json.loads(l)["id"] for l in open(f"{HOME}/index/clips.jsonl") if '"id"' in l}
words = json.load(open(f"{job}/words.json"))

draft = {}
for k, s in enumerate(plan["segments"]):
    t = words[s["words"][0]]["start"]
    draft[k] = dict(t=t, caption=s["caption"], broll=(s.get("broll") or {}).get("id"), mode=s.get("mode"))

fb = [r for r in fin["items"] if r["kind"] == "video" and r["track"] == 2 and r["file"]]
fc = [r for r in fin["items"] if r.get("text") is not None]


def at(rows, t):
    f = s0 + t * fps + 2
    return next((r for r in rows if r["start"] <= f < r["end"]), None)


corr = []
for k, d in draft.items():
    b = at(fb, d["t"]); c = at(fc, d["t"])
    got_b = clips.get(b["file"]) if b else None
    if b and not got_b:
        got_b = "new:" + b["file"]
    if got_b != d["broll"]:
        kind = "removed_broll" if d["broll"] and not got_b else "added_broll" if got_b and not d["broll"] else "swapped_broll"
        corr.append(dict(job=os.path.basename(job), line=k, kind=kind, caption=d["caption"], draft=d["broll"], final=got_b))
    if c and c["text"].strip() != d["caption"].strip():
        corr.append(dict(job=os.path.basename(job), line=k, kind="caption_text", draft=d["caption"], final=c["text"]))
    if c and c.get("zoom") not in (None, False):
        want = {"over_broll": 1.0, "over_aroll": 0.73}.get(d["mode"])
        if want and abs(c["zoom"] - want) > 0.03:
            corr.append(dict(job=os.path.basename(job), line=k, kind="caption_size", mode=d["mode"], draft=want, final=round(c["zoom"], 2)))
with open(f"{style_dir}/corrections.jsonl", "a") as f:
    for c in corr:
        f.write(json.dumps(c) + "\n")

allc = [json.loads(l) for l in open(f"{style_dir}/corrections.jsonl")]
kinds = collections.Counter(c["kind"] for c in allc)
jobs = len({c["job"] for c in allc})
lines = [f"# What Eoin changed in auto drafts ({jobs} edits, {len(allc)} corrections)", "",
         "The planner reads this before planning. Patterns here override PLANNER.md defaults.", "",
         "## Counts", *[f"- {k}: {v}" for k, v in kinds.most_common()], "", "## Recent corrections (newest last)"]
for c in allc[-60:]:
    if c["kind"] == "caption_text":
        lines.append(f'- caption: "{c["draft"]}" -> "{c["final"]}"')
    elif c["kind"] == "caption_size":
        lines.append(f'- caption size on {c["mode"]}: {c["draft"]} -> {c["final"]}')
    else:
        lines.append(f'- {c["kind"]} on "{c.get("caption","")}": {c["draft"]} -> {c["final"]}')
open(f"{style_dir}/LEARNED.md", "w").write("\n".join(lines) + "\n")
print(f"{len(corr)} corrections from this edit; {len(allc)} total -> {style_dir}/LEARNED.md")
