"""QC preflight on finished exports, before anything goes into the scheduler (SOP 07).
Machine checks only: spec, loudness, peaks, black/flash at the start, swears. Prints every cut point so the
human watch-through can jump straight to each one. Dodgy cuts and taste are the human pass, never this script.
Usage: python3 preflight.py <folder|file.mp4> [...]   (folders are searched recursively)
Writes qc-report.md next to the first folder given. Exit 1 if any video FAILS."""
import json, os, re, subprocess, sys, tempfile

MODEL = os.path.expanduser("~/.cache/hyperframes/whisper/models/ggml-small.en.bin")
SWEARS = re.compile(r"\b(fuck\w*|shit\w*|bullshit|bitch\w*|cunt\w*|dick|prick|wank\w*|bollocks|arse\w*|asshole|bastard)\b", re.I)
LUFS_LO, LUFS_HI, PEAK_MAX = -14.0, -9.0, -1.0   # SOP 10: every reel lands about -11 LUFS, peaks limited to -1


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(f):
    j = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", f]).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    return v, a, float(j["format"]["duration"])


def loudness(f):
    err = run(["ffmpeg", "-nostats", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    tail = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", tail)
    return (float(i.group(1)) if i else None), (float(p.group(1)) if p and p.group(1) != "-inf" else None)


def start_black(f):
    err = run(["ffmpeg", "-t", "2", "-i", f, "-vf", "blackdetect=d=0.08:pic_th=0.95", "-an", "-f", "null", "-"]).stderr
    return [float(x) for x in re.findall(r"black_start:([\d.]+)", err)]


def cuts(f):
    err = run(["ffmpeg", "-i", f, "-vf", "scdet=threshold=12", "-an", "-f", "null", "-"]).stderr
    return [float(x) for x in re.findall(r"lavfi\.scd\.time:\s*([\d.]+)", err)]


def swears(f):
    if not os.path.exists(MODEL):
        return None
    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "a.wav")
        run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "16000", "-ac", "1", wav])
        run(["whisper-cli", "-m", MODEL, "-f", wav, "-oj", "-of", os.path.join(td, "w"), "-np"])
        try:
            segs = json.load(open(os.path.join(td, "w.json")))["transcription"]
        except Exception:
            return None
    hits = []
    for s in segs:
        for w in SWEARS.findall(s["text"]):
            hits.append(f"{w} @ {s['timestamps']['from'][3:8]}")
    return hits


def check(f):
    fails, warns = [], []
    v, a, dur = probe(f)
    if not v:
        return ["no video stream"], [], {}
    w, h = int(v["width"]), int(v["height"])
    if (w, h) != (1080, 1920):
        warns.append(f"{w}x{h}, not 1080x1920")
    if dur > 90:
        warns.append(f"{dur:.0f}s long, over 90s")
    if not a:
        fails.append("no audio")
    else:
        if int(a.get("channels", 0)) < 2:
            warns.append("mono audio")
        i, p = loudness(f)
        if i is None:
            warns.append("loudness unreadable")
        elif not LUFS_LO <= i <= LUFS_HI:
            fails.append(f"loudness {i} LUFS (want {LUFS_LO} to {LUFS_HI}, target -11)")
        if p is not None and p > PEAK_MAX:
            warns.append(f"peak {p} dBFS (limit to {PEAK_MAX})")
    b = start_black(f)
    if b:
        fails.append(f"black frame in the first 2s at {b[0]:.2f}s")
    sw = swears(f)
    if sw is None:
        warns.append("swear scan skipped (no whisper)")
    elif sw:
        fails.append("swears: " + ", ".join(sw))
    c = cuts(f)
    return fails, warns, {"dur": dur, "cuts": c}


def main(args):
    files = []
    for x in args:
        if os.path.isdir(x):
            for r, _, fs in os.walk(x):
                files += [os.path.join(r, n) for n in fs if n.lower().endswith((".mp4", ".mov")) and not n.startswith(".")]
        else:
            files.append(x)
    files.sort(key=lambda p: os.path.basename(p))
    out = ["# QC preflight", "", "Machine checks only. Every video still gets the human watch-through (SOP 07).", ""]
    bad = 0
    for f in files:
        fails, warns, info = check(f)
        bad += bool(fails)
        name = os.path.basename(f)
        status = "FAIL" if fails else ("WARN" if warns else "PASS")
        print(f"{status:4}  {name}" + "".join(f"\n      x {x}" for x in fails) + "".join(f"\n      ~ {x}" for x in warns))
        out.append(f"## {status} · {name}")
        out += [f"- FAIL: {x}" for x in fails] + [f"- warn: {x}" for x in warns]
        if info.get("cuts"):
            out.append(f"- cut points to check ({len(info['cuts'])}): " + ", ".join(f"{t:.1f}s" for t in info["cuts"]))
        out.append(f"- human pass: [ ] cuts  [ ] words whole  [ ] captions  [ ] music  [ ] hook + CTA  [ ] client rules")
        out.append("")
    root = args[0] if os.path.isdir(args[0]) else os.path.dirname(args[0])
    rep = os.path.join(root, os.environ.get("PREFLIGHT_REPORT", "qc-report.md"))
    open(rep, "w").write("\n".join(out))
    print(f"\n{len(files)} checked, {bad} failed. Report: {rep}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
