"""Plan QA before build. Usage: python3 qa.py <job_dir>. Exit 1 on hard failures."""
import json, os, sys, glob
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
job = sys.argv[1]
plan = json.load(open(f"{job}/plan.json", encoding="utf-8")); words = json.load(open(f"{job}/words.json", encoding="utf-8"))
style = json.load(open(f"{HOME}/styles/{plan['style']}/style.json", encoding="utf-8"))
clips = {json.loads(l)["id"]: json.loads(l) for l in open(f"{HOME}/index/clips.jsonl") if '"id"' in l}
labels = {}
for f in glob.glob(f"{HOME}/index/labels*.jsonl"):
    for l in open(f):
        try: d = json.loads(l); labels[d["id"]] = d
        except Exception: pass
hard, soft = [], []
segs = plan["segments"]
nxt = 0
for k, s in enumerate(segs):
    i0, i1 = s["words"]
    if i0 != nxt: hard.append(f"line {k}: words start at {i0}, expected {nxt} (gap/overlap)")
    nxt = i1 + 1
if nxt != len(words): hard.append(f"segments end at word {nxt}, transcript has {len(words)}")
seen, run, bsec = {}, 0, 0.0
total = words[-1]["end"] - words[0]["start"]
for k, s in enumerate(segs):
    b = s.get("broll"); i0, i1 = s["words"]; d = words[i1]["end"] - words[i0]["start"]
    if not b:
        run = 0; continue
    run += 1; bsec += d
    c = clips.get(b["id"])
    if not c: hard.append(f"line {k}: unknown clip {b['id']}"); continue
    if b["id"] in seen: hard.append(f"line {k}: clip {b['id']} already used on line {seen[b['id']]}")
    seen[b["id"]] = k
    if c["dur"] < d + 0.2: hard.append(f"line {k}: clip {c['dur']:.1f}s shorter than line {d:.1f}s")
    iss = " ".join(labels.get(b["id"], {}).get("issues", [])).lower()
    if any(x in iss for x in ("ungraded", "flat", "blurry", "talking to camera")): hard.append(f"line {k}: clip flagged '{iss}'")
    if not b.get("why"): hard.append(f"line {k}: no why")
    if run > 4: soft.append(f"line {k}: {run} b-roll lines in a row")
lo, hi = style["broll"]["share_range"]
share = bsec / total if total else 0
if not lo <= share <= hi: soft.append(f"b-roll share {share:.0%} outside {lo:.0%}-{hi:.0%}")
if segs and segs[0].get("broll"): soft.append("hook line is on b-roll (style keeps A-roll on the hook)")
if segs and segs[-1].get("broll"): soft.append("last line is on b-roll (style keeps A-roll on the close)")
print(f"b-roll {share:.0%} · {len(seen)} shots · {len(segs)} lines")
for h in hard: print("FAIL", h)
for s in soft: print("warn", s)
sys.exit(1 if hard else 0)
