"""Emotion index: every usable b-roll clip grouped by emotion, then by shoot, strongest-energy first.
One file a human or the planner can scan in seconds ("I need a lonely Kyle shot" -> one section).
Usage: python3 emotion_index.py [folder substring ...]   -> index/EMOTION-INDEX.md"""
import json, os, sys, glob, subprocess, tempfile
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORDER = ["lonely", "reflective", "pressure", "grind", "power", "calm", "connection", "joy", "momentum", "awe", "neutral", "untagged"]
tmp = tempfile.mkdtemp()
subprocess.run([sys.executable, f"{HOME}/engine/catalog.py", tmp, *sys.argv[1:]], check=True, capture_output=True)
rows = [l.rstrip("\n").split(" | ") for l in open(f"{tmp}/catalog.txt") if l.strip()]
by = {}
for r in rows:
    cid, folder, dur, emo, who, lm, desc = r[:7]
    tags = r[8] if len(r) > 8 else ""
    e1, _, energy = emo.partition("/")
    for i, e in enumerate(e1.split("+")):
        by.setdefault(e, []).append((i, {"high": 0, "mid": 1, "low": 2}.get(energy, 3), folder, cid, dur, who, desc, e1, energy, tags))
out = ["# Emotion index", "", "Every usable b-roll clip by the feeling it gives. Primary emotion first, then clips where it's the",
       "second emotion (marked ²). Built by engine/emotion_index.py from the labels; regenerate after labelling.", ""]
out.append(" · ".join(f"[{e}](#{e}) {len(by.get(e, []))}" for e in ORDER if by.get(e)))
for e in ORDER:
    items = sorted(by.get(e, []), key=lambda x: (x[0], x[2], x[1]))
    if not items: continue
    out += ["", f"## {e}", ""]
    folder = None
    for sec, _, f, cid, dur, who, desc, both, energy, tags in items:
        if f != folder:
            out.append(f"**{f}**"); folder = f
        out.append(f"- `{cid}` {dur} · {energy} · {who}{' · ²' if sec else ''} · {desc}")
open(f"{HOME}/index/EMOTION-INDEX.md", "w").write("\n".join(out) + "\n")
print(len(rows), "clips ->", f"{HOME}/index/EMOTION-INDEX.md")
