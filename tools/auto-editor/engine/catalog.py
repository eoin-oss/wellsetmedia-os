"""Write the usable-clip catalog the planner reads. Usage: python3 catalog.py <job_dir>"""
import json, os, sys, glob
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
clips = {json.loads(l)["id"]: json.loads(l) for l in open(f"{HOME}/index/clips.jsonl") if '"id"' in l}
labels = {}
for f in glob.glob(f"{HOME}/index/labels*.jsonl"):
    for l in open(f):
        l = l.strip()
        if l:
            try:
                d = json.loads(l); labels[d["id"]] = d
            except Exception:
                pass
EMO = {}  # emotion layer for clips labelled before it existed (index/emotions_*.jsonl); a label's own fields win
for f in glob.glob(f"{HOME}/index/emotions*.jsonl"):
    for l in open(f):
        l = l.strip()
        if l:
            try:
                d = json.loads(l); EMO[d["id"]] = d
            except Exception:
                pass
for cid, e in EMO.items():
    if cid in labels:
        lab = labels[cid]
        for k in ("emotion", "emotion2", "energy", "tags"):
            lab.setdefault(k, e.get(k))
        lab["lines_it_could_serve"] = list(lab.get("lines_it_could_serve", [])) + [x for x in e.get("emotional_lines", []) if x not in lab.get("lines_it_could_serve", [])]
BAD = ("ungraded", "flat log", "blurry", "test shot", "talking to camera", "mostly black", "lens cap",
       "attendee in trance", "attendee speaking", "attendee close-up")
ONLY = [a for a in sys.argv[2:]]  # optional folder substrings: only clips whose folder contains one of these
out, skipped = [], 0
for cid, lab in labels.items():
    c = clips.get(cid)
    if not c or (ONLY and not any(o in c["folder"] for o in ONLY)):
        continue
    if (c.get("h") or 0) > (c.get("w") or 0):  # no vertical phone footage in landscape edits
        skipped += 1
        continue
    issues = " ".join(lab.get("issues", [])).lower()
    if lab.get("quality") == "bad" or any(b in issues for b in BAD) or c.get("dur", 0) < 1.0:
        skipped += 1
        continue
    folder = c["folder"].replace("personal brand directory/", "")
    lux = ("lamborghini", "porsche", "rolex", "first-class", "first class", "penthouse", "supercar", "designer", "boss shop",
           "boss store", "hugo boss", "luxury", "urus", "cash", "money", "stock exchange")
    tl = list(lab.get("tags") or [])
    if any(k in (lab.get("desc", "") + " " + " ".join(tl)).lower() for k in lux) or "materialism" in issues:
        tl.append("materialism-borderline")
    lab = dict(lab, tags=tl)
    emo = "+".join(x for x in (lab.get("emotion"), lab.get("emotion2")) if x) or "untagged"
    who = ",".join(p.split(":")[0] if p.startswith("other") else p for p in lab.get("people", [])) or "-"
    out.append(f'{cid} | {folder} | {c["dur"]:.1f}s | {emo}/{lab.get("energy") or "-"} | {who} | {lab.get("light","")}/{lab.get("mood","")} '
               f'| {lab.get("desc","")} | {"; ".join(lab.get("lines_it_could_serve", []))} | {",".join(lab.get("tags") or [])}')
job = sys.argv[1]
open(f"{job}/catalog.txt", "w").write("\n".join(sorted(out, key=lambda s: s.split(" | ")[1])) + "\n")
print(len(out), "usable,", skipped, "skipped ->", f"{job}/catalog.txt")
