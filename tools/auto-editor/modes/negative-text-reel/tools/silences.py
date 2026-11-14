"""Cut the silences: find pauses >= MIN in the A-roll, keep PAD either side, and move the whole job onto the cut
timeline (words.json, audio.wav for the onset snap, joins.json, plan['keep']). build.py then lays only the kept
pieces (V1 + A1) and every caption / b-roll lands in the right place. Idempotent: originals kept as *_src.
Usage: python3 silences.py <job> [min_gap=0.28] [pad=0.10]"""
import json, os, shutil, subprocess, sys, wave
import numpy as np
from _common import job_dir, FPS

job = job_dir(); os.chdir(job)
MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.28
PAD = float(sys.argv[3]) if len(sys.argv) > 3 else 0.10
if not os.path.exists("words_src.json"):
    shutil.copy("words.json", "words_src.json"); shutil.copy("audio.wav", "audio_src.wav")
W = json.load(open("words_src.json"))
wf = wave.open("audio_src.wav"); sr = wf.getframerate()
x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(float) / 32768
n = sr // 100; db = 20 * np.log10(np.sqrt((x[:len(x) // n * n].reshape(-1, n) ** 2).mean(1)) + 1e-9)
quiet = db < np.percentile(db, 10) + 12; L = len(quiet)
gaps, i, end = [], int(W[0]["start"] * 100), min(int(W[-1]["end"] * 100), L)
while i < end:
    if quiet[i]:
        j = i
        while j < end and quiet[j]: j += 1
        if (j - i) >= MIN * 100: gaps.append((i / 100, j / 100))
        i = j
    else:
        i += 1
fr = lambda v: round(v * FPS) / FPS
drops = [(fr(a + PAD), fr(b - PAD)) for a, b in gaps if (b - a) - 2 * PAD >= 0.12]
aroll = json.load(open("job.json"))["aroll"]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", aroll], capture_output=True, text=True).stdout)
keep, cur = [], 0.0
for a, b in drops: keep.append([cur, a]); cur = b
keep.append([cur, fr(dur) - 1 / FPS])
def tm(t):
    off = 0
    for a, b in drops:
        if t >= b: off += b - a
        elif t > a: return round(a - off, 4)
    return round(t - off, 4)
json.dump([dict(w, start=tm(w["start"]), end=tm(w["end"])) for w in W], open("words.json", "w"), indent=0)
acc, joins = 0, []
for a, b in keep[:-1]: acc += b - a; joins.append(round(acc, 3))
json.dump(joins, open("joins.json", "w"))
filt = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];" for i, (a, b) in enumerate(keep)) + "".join(f"[a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1[o]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "audio_src.wav", "-filter_complex", filt, "-map", "[o]", "audio.wav"], check=True)
p = json.load(open("plan.json")); p["keep"] = keep; json.dump(p, open("plan.json", "w"), indent=1)
print(f"{len(drops)} silences cut, {sum(b - a for a, b in drops):.2f}s removed, new length {sum(b - a for a, b in keep):.2f}s")
