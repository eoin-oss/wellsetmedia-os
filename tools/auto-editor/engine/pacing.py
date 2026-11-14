"""Pacing check for a plan (Kyle v4 rules, from RESEARCH-PACING.md + Eoin's notes).
Usage: python3 pacing.py <job_dir>  -> PASS/FAIL lines"""
import json, os, sys

job = sys.argv[1].rstrip("/")
w = json.load(open(f"{job}/words.json", encoding="utf-8"))
S = json.load(open(f"{job}/plan.json", encoding="utf-8"))["segments"]
dur = w[-1]["end"]
shots = []
for k, s in enumerate(S):
    b = s.get("broll")
    if not b:
        continue
    sw = b.get("start_word")
    a = w[sw if sw is not None and s["words"][0] < sw <= s["words"][1] else s["words"][0]]["start"]
    e = w[S[k + 1]["words"][0]]["start"] if k + 1 < len(S) else w[s["words"][1]]["end"]
    shots.append((a, e, k))
fail, info = [], []
first = shots[0][0] if shots else dur
if not 1.2 <= first <= 2.2:
    fail.append(f"first b-roll at {first:.2f}s (want ~1.5s, 1.2-2.2)")
ch8 = sum(1 for a, e, k in shots if a < 8) * 2  # each shot = cut in + cut out
if sum(1 for a, e, k in shots if a < 8) < 2:
    fail.append(f"only {sum(1 for a, e, k in shots if a < 8)} b-roll shots start in the first 8s (want 2-3)")
for a, e, k in shots:
    if e - a < 0.8:
        fail.append(f"s{k} shot {e - a:.2f}s < 0.8s")
    if e - a > 3.5:
        info.append(f"s{k} shot {e - a:.2f}s (long; fine if it covers two short phrases)")
# longest stretch on the face after the open
edges = [0.0] + [x for a, e, k in shots for x in (a, e)] + [dur]
gaps = [(edges[i + 1] - edges[i], edges[i]) for i in range(0, len(edges) - 1, 2)]
for g, at in gaps[1:-1]:
    if g > 6.0:
        info.append(f"{g:.1f}s on the face from {at:.1f}s (ok only for a claim/story/payoff)")
run, mx = 1, 1
for (a1, e1, k1), (a2, e2, k2) in zip(shots, shots[1:]):
    run = run + 1 if a2 - e1 < 0.3 else 1
    mx = max(mx, run)
if mx > 2:
    fail.append(f"{mx} b-roll shots in a row")
share = sum(e - a for a, e, k in shots) / dur
if not 0.28 <= share <= 0.45:
    fail.append(f"b-roll share {share:.0%} (want 30-45%)")
print(os.path.basename(job), f"share {share:.0%} · {len(shots)} shots · first {first:.2f}s · max run {mx}")
for f in fail: print("FAIL", f)
for i in info: print("note", i)
