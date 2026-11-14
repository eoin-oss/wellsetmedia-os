"""Cut engine for raw talking-head footage.
- keeps one speaker (Resolve speaker detection) and drops everyone else
- keeps the FINAL take when a line is restarted or said again; drops stutters ("I I", "we went to- we went to")
- removes everything that isn't a kept word: silences, coughs, knocks, breaths, mumbles
- trims pads off sound spikes; optional motion-aware cut points (Eoin's tics)
Usage: python3 cutter.py <job_dir> [--speaker "Speaker 2"] [--gap 0.25] [--motion]
Reads job.json (aroll) + words_raw.json; writes cuts.json, words.json (edited timeline time), cut_report.md"""
import argparse, difflib, json, os, subprocess, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("job"); ap.add_argument("--speaker"); ap.add_argument("--gap", type=float, default=0.25)
ap.add_argument("--motion", action="store_true")
ap.add_argument("--script", help="script text file: keep the last complete take of each script line, in script order")
ap.add_argument("--keep", help="takes_keep.json: list of take ids chosen by the take-picker (no-script shoots)")
a = ap.parse_args()
job = os.path.abspath(a.job)
meta = json.load(open(f"{job}/job.json"))
W = json.load(open(f"{job}/words_raw.json"))
fps = meta["fps"]

# 1. speaker
from collections import Counter
talk = Counter()
for w in W:
    talk[w.get("speaker")] += w["end"] - w["start"]
spk = a.speaker or (talk.most_common(1)[0][0] if talk else None)
dropped_other = [w for w in W if w.get("speaker") != spk]
W = [w for w in W if w.get("speaker") == spk]

# 2. sentences
sents, cur = [], []
for i, w in enumerate(W):
    if cur and (w["start"] - cur[-1]["end"] > 0.7):
        sents.append(cur); cur = []
    cur.append(w)
    if w["w"][-1:] in ".?!":
        sents.append(cur); cur = []
if cur:
    sents.append(cur)


def toks(s):
    return [w["norm"] for w in s if w["norm"]]


report = []
# 3a. stutters + in-sentence restarts: drop the first attempt of a repeated opening
clean = []
for s in sents:
    t = toks(s)
    changed = True
    while changed and len(s) > 1:
        changed = False
        for m in (4, 3, 2):
            for k in range(1, min(len(t) - m + 1, 12)):
                if t[k:k + m] == t[0:m] and k >= 1:
                    report.append(f'restart dropped: "{" ".join(x["w"] for x in s[:k])}"')
                    s, t = s[k:], t[k:]
                    changed = True
                    break
            if changed:
                break
    out = [s[0]]
    for w in s[1:]:
        if w["norm"] == out[-1]["norm"] and w["start"] - out[-1]["end"] < 0.6:
            report.append(f'stutter dropped: "{out[-1]["w"]}"')
            out[-1] = w
        else:
            out.append(w)
    clean.append(out)
sents = clean

# 3b. retakes across sentences: keep the LAST attempt
keep = [True] * len(sents)
for i, s in enumerate(sents):
    ti = toks(s)
    if not ti:
        keep[i] = False; continue
    for j in range(i + 1, min(i + 6, len(sents))):
        tj = toks(sents[j])
        if sents[j][0]["start"] - s[-1]["end"] > 40 or not tj:
            break
        head = min(3, len(ti), len(tj))
        same_open = ti[:head] == tj[:head] and head >= 2
        sim = difflib.SequenceMatcher(None, ti, tj[:len(ti) + 2]).ratio()
        if (same_open and sim >= 0.5) or sim >= 0.8:
            keep[i] = False
            report.append(f'retake: kept later take "{" ".join(w["w"] for w in sents[j])[:70]}", dropped "{" ".join(w["w"] for w in s)[:70]}"')
            break
json.dump([dict(id=k, start=round(s[0]["start"], 2), end=round(s[-1]["end"], 2), text=" ".join(w["w"] for w in s), rule_keep=keep[k])
           for k, s in enumerate(sents)], open(f"{job}/takes.json", "w"), indent=1)
order = [k for k in range(len(sents)) if keep[k]]
if a.script:
    import re
    lines = [l.strip() for l in re.split(r"(?<=[.?!])\s+|\n+", open(a.script).read()) if l.strip()]
    order, used = [], set()
    for line in lines:
        lt = [re.sub(r"[^a-z0-9']", "", x.lower()) for x in line.split()]
        lt = [x for x in lt if x]
        best = None
        for k, s in enumerate(sents):
            if k in used:
                continue
            sim = difflib.SequenceMatcher(None, lt, toks(s)).ratio()
            if sim >= 0.6 and (best is None or sim >= best[1] - 0.05):
                best = (k, sim)  # later takes win ties: the final take is the one that worked
        if best:
            order.append(best[0]); used.add(best[0])
        else:
            report.append(f'script line not found on camera: "{line[:70]}"')
    report.append(f"script mode: {len(order)}/{len(lines)} lines matched")
elif a.keep:
    order = json.load(open(a.keep))
    report.append(f"take-picker kept {len(order)} of {len(sents)} takes")
words = [w for k in order for w in sents[k]]

# 4. audio envelope for spike-aware pads
wav = f"{job}/audio.wav"
if not os.path.exists(wav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", meta["aroll"], "-ar", "16000", "-ac", "1", wav], check=True)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
hop = 160
env = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, "same"))[::hop]  # 10 ms
speech_lvl = np.median([env[int(w["start"] * 100):int(w["end"] * 100) + 1].max() for w in words if int(w["end"] * 100) < len(env)] or [0.1])


def pad_ok(t0, t1):
    seg = env[int(t0 * 100):int(t1 * 100) + 1]
    return not len(seg) or seg.max() < speech_lvl * 0.5


# ranges of kept words
ranges = []
for w in words:
    if ranges and 0 <= w["start"] - ranges[-1][1] <= a.gap:
        ranges[-1][1] = w["end"]
    else:
        ranges.append([w["start"], w["end"]])
LEAD, TAIL = 0.05, 0.08
cuts = []
for s0, s1 in ranges:
    lead = LEAD if pad_ok(s0 - LEAD, s0 - 0.01) else 0.01
    tail = TAIL if pad_ok(s1 + 0.01, s1 + TAIL) else 0.02
    cuts.append([max(0, s0 - lead), s1 + tail])

# 5. motion-aware cut points (tics): shift each boundary up to 3 frames to the stillest frame, never into a word
if a.motion:
    def motion_at(t):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, t - 0.15):.3f}", "-i", meta["aroll"], "-t", "0.3",
                            "-vf", "crop=iw/3:ih/2:iw/3:ih/6,scale=64:48,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
        fr = np.frombuffer(r, np.uint8).reshape(-1, 48, 64).astype(np.float32)
        return np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2)) if len(fr) > 1 else np.zeros(1)
    word_spans = [(w["start"], w["end"]) for w in words]
    for c in cuts:
        for k in (0, 1):
            m = motion_at(c[k])
            best = c[k] - 0.15 + (int(np.argmin(m)) + 0.5) / fps
            if not any(ws <= best <= we for ws, we in word_spans):
                c[k] = best

# merge overlaps, frame-snap (keep take order: script order may differ from shooting order)
merged = []
for c in cuts:
    c = [round(c[0] * fps) / fps, round(c[1] * fps) / fps]
    if merged and c[0] <= merged[-1][1]:
        merged[-1][1] = max(merged[-1][1], c[1])
    else:
        merged.append(c)

# 6. edited-time words
out, t = [], 0.0
for c0, c1 in merged:
    for w in words:
        if c0 <= w["start"] < c1:
            out.append(dict(w=w["w"], norm=w["norm"], start=t + w["start"] - c0, end=t + min(w["end"], c1) - c0))
    t += c1 - c0
src_len = W[-1]["end"] if W else 0
json.dump([{"in": c0, "out": c1} for c0, c1 in merged], open(f"{job}/cuts.json", "w"), indent=0)
json.dump(out, open(f"{job}/words.json", "w"), indent=0)
with open(f"{job}/cut_report.md", "w") as f:
    f.write(f"# Cut report\n\nspeaker kept: {spk} (talk time {dict((k, round(v,1)) for k, v in talk.items())})\n")
    f.write(f"other-speaker words dropped: {len(dropped_other)}\n\nsource {src_len:.1f}s -> edit {t:.1f}s, {len(merged)} pieces\n\n")
    f.write("\n".join(f"- {r}" for r in report) + "\n\n## Final script\n\n" + " ".join(w["w"] for w in out) + "\n")
print(f"{spk}: {src_len:.1f}s -> {t:.1f}s in {len(merged)} pieces; {len(report)} fixes; report {job}/cut_report.md")
