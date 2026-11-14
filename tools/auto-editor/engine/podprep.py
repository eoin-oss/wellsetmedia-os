"""Podcast clip prep for a Resolve build (analysis only, nothing rendered). Per clip in clips.tsv:
word-accurate transcript (openai-whisper medium.en), cuts snapped to whole words from text anchors, caption phrases,
camera-shot changes and the speaker's face position per shot (for the 9:16 reframe).
Usage: python3 podprep.py <source> <clips.tsv> <job root> [ids]
clips.tsv: id, slug, segments "mm:ss-mm:ss{first words|last words}+...", speaker, why"""
import csv, json, os, re, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from phrases import split

HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STYLE = json.load(open(f"{HOME}/styles/eoin/style.json"))
FACE_MODEL = f"{HOME}/models/blaze_face_short_range.tflite"
FIX = [(r"\b(?:[Ee]ight|[Aa]|[Bb]ig)[ -][Pp]layers\b", "A Players"), (r"\bGall?[ai]g[ae]n\b", "Galligan"),
       (r"\bHampton\b", "Hempton"), (r"\bCollins?on\b", "Collison"), (r"\bDren's\b", "trends"),
       (r"\b(?:Kyle|Carl|Kel|Kal) Ritchie\b", "Kyle Ritchie"), (r"\bMarcel Kl[ae]ine?\b", "Marcel Klein"),
       (r"\b(?:M\.?E\.?O?\.?R\.?|EMUOR|Emmy or)\b", "MER"), (r"\bflight shock\b", "anaphylactic shock"),
       (r"\bKabb?al[iy][oa]n\b", "Kybalion"), (r"\bCaballion\b", "Kybalion"), (r"\bDarren Brown\b", "Derren Brown")]
LEAD = {"and", "so", "but", "like", "yeah", "right", "okay", "ok", "mm", "hmm", "um", "uh", "well"}
FILLER = {"yeah", "right", "okay", "ok", "mm", "hmm", "mmhmm", "yep", "exactly", "nice", "wow", "sure", "100"}
DROP = {"um", "uh", "erm"}
MODEL = None
SRC = None


def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + float(s)


def norm(t):
    return re.sub(r"[^a-z0-9']", "", t.lower())


def toks(t):
    return [x for x in (re.sub(r"[^a-z0-9]", "", w.lower()) for w in t.split()) if x]


def transcribe(src, a, b):
    global MODEL
    import whisper
    MODEL = MODEL or whisper.load_model("medium.en")
    wav = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", src, "-t", f"{b - a:.3f}", "-ac", "1", "-ar", "16000", wav], check=True)
    # no initial_prompt: with one, medium.en skipped the first ~30s of the window
    r = MODEL.transcribe(wav, word_timestamps=True, language="en", condition_on_previous_text=False)
    os.remove(wav)
    return [dict(w=w["word"].strip(), start=w["start"] + a, end=w["end"] + a)
            for seg in r["segments"] for w in seg["words"] if w["word"].strip()]


def find(W, words, lo, hi, target, last=False):
    n, keys = len(words), [(toks(w["w"]) or [""])[0] for w in W]
    for slack in (0, 1):
        hits = [i for i in range(len(W) - n + 1) if lo <= W[i]["start"] <= hi and sum(keys[i + k] != words[k] for k in range(n)) <= slack]
        if hits:
            i = min(hits, key=lambda i: abs(W[i]["start"] - target))
            return i + n - 1 if last else i
    return None


def snap(W, a, b, first, final, warn):
    i0 = find(W, toks(first), a - 10, min(b, a + 8), a) if first else None  # near where the start should be
    if i0 is None:
        warn.append(f"start anchor '{first}' not found near {a:.0f}s")
        i0 = next(i for i, w in enumerate(W) if w["start"] >= a - 0.35)
        while i0 + 1 < len(W) and norm(W[i0]["w"]) in LEAD:
            i0 += 1
    i1 = find(W, toks(final), max(W[i0]["start"], b - 8), b + 10, b, last=True) if final else None  # near the end, never early
    if i1 is None:
        warn.append(f"end anchor '{final}' not found near {b:.0f}s")
        i1 = max(i for i, w in enumerate(W) if w["start"] < b)
    s = voice_start(SRC, W[i0]["start"], W[i0 - 1]["end"] + 0.02 if i0 else 0.0)
    e = voice_end(SRC, W[i1]["end"], W[i1 + 1]["start"] - 0.04 if i1 + 1 < len(W) else W[i1]["end"] + 1.5)
    return s, e, W[i0:i1 + 1]


def voice_start(src, word_start, floor):
    """Whisper word starts land up to ~0.5s after the voice really starts, which clips the first word. Walk back from
    the whisper start to where the voice actually comes up, then lead it by 0.08s. Never before `floor`
    (the previous word's end)."""
    a = max(floor, word_start - 0.8)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", src, "-t", f"{word_start - a + 0.3:.3f}", "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float)
    if len(x) < 1600:
        return max(floor, word_start - 0.12)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(160) / 160, "same")[::160])
    thr = max(np.percentile(rms, 20) * 2.5, rms.max() * 0.08)
    i = int((word_start - a) * 100)
    i = min(i, len(rms) - 1)
    while i > 0 and rms[i - 1] > thr:  # walk back while the voice is still up
        i -= 1
    return max(floor, a + i / 100 - 0.08)


def voice_end(src, last_end, hard_stop):
    """Where the voice really stops after a word whisper says ends at last_end: first 150ms of quiet after it,
    + 0.3s hold. Never past the next voice (hard_stop) and never more than 1.5s on."""
    a = max(0.0, last_end - 0.3)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", src, "-t", "2.5", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float)
    if not len(x):
        return min(last_end + 0.3, hard_stop)
    hop = 160
    rms = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, "same")[::hop])
    thr = max(np.percentile(rms, 20) * 2.5, rms.max() * 0.06)
    start = int((last_end - a) * 100)
    for i in range(start, len(rms) - 15):
        if (rms[i:i + 15] < thr).all():
            end = a + i / 100 + 0.3
            # the next voice coming back in inside the hold: cut just before it
            back = next((j for j in range(i + 15, min(len(rms), i + 45)) if rms[j] > thr * 1.5), None)
            if back is not None:
                end = min(end, a + back / 100 - 0.04)
            return max(last_end + 0.08, min(end, hard_stop, last_end + 1.5))
    return min(last_end + 0.3, hard_stop)


def shots_and_faces(src, s, e, fps):
    """Decode [s, e] once at 640x360: hard cuts from frame differences, face centre every 3rd frame.
    Returns shots [(f0, f1, face_x_norm, face_y_norm)] in frames relative to s."""
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    det = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=FACE_MODEL), min_detection_confidence=0.45))
    w, h = 640, 360
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{s:.3f}", "-i", src, "-t", f"{e - s:.3f}", "-vf", f"scale={w}:{h}",
                          "-r", str(fps), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    cuts, faces, prev, i = [0], {}, None, 0
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        f = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        small = f[::10, ::10].mean(2)
        if prev is not None and np.abs(small - prev).mean() > 30 and i - cuts[-1] > 5:
            cuts.append(i)
        prev = small
        if True:  # every frame: the crop locks to the face
            r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)))
            if r.detections:
                b = max(r.detections, key=lambda d: d.bounding_box.width * d.categories[0].score).bounding_box
                faces[i] = ((b.origin_x + b.width / 2) / w, (b.origin_y + b.height / 2) / h)
        i += 1
    p.wait()
    out = []
    for f0, f1 in zip(cuts, cuts[1:] + [i]):
        pts = [v for k, v in faces.items() if f0 <= k < f1]
        fx = float(np.median([x for x, _ in pts])) if pts else None
        fy = float(np.median([y for _, y in pts])) if pts else None
        # per-frame face x for the lock: fill gaps, then a light gaussian (sigma 2 frames) so it's tight but not jittery
        ks = [k for k in range(f0, f1) if k in faces]
        if ks:
            xs = np.interp(np.arange(f0, f1), ks, [faces[k][0] for k in ks])
            g = np.exp(-0.5 * (np.arange(-6, 7) / 2.0) ** 2); g /= g.sum()
            xs = np.convolve(np.pad(xs, 6, mode="edge"), g, "valid")
            track = [round(float(x), 4) for x in xs]
        else:
            track = None
        out.append([f0, f1, fx, fy, track])
    for k, o in enumerate(out):  # a shot with no face found keeps its neighbour's framing
        if o[2] is None:
            nb = next((x for x in out[k - 1::-1] + out[k + 1:] if x[2] is not None), None) if len(out) > 1 else None
            o[2], o[3] = (nb[2], nb[3]) if nb else (0.5, 0.4)
        if o[4] is None:
            o[4] = [o[2]] * (o[1] - o[0])
    return out


def filler_cuts(src, pieces, words, fps):
    """Clip-time ranges to remove: voice between two words that whisper didn't transcribe (um / ah / uh) and dead
    pauses over 0.6s. Keeps a natural 0.06s after the word and 0.08s before the next."""
    spans, t = [], 0.0
    for p in pieces:
        n = (p["src_out"] - p["src_in"]) / fps
        spans.append((t, t + n, p["src_in"] / fps))
        t += n
    def src_t(x):
        return next((s + (x - a) for a, b, s in spans if a <= x < b), None)
    # min/max, not first/last: a hook lifted from LATER in the episode opens the clip, so the first piece can sit after the last
    lo, hi = min(p["src_in"] for p in pieces) / fps, max(p["src_out"] for p in pieces) / fps
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{lo:.3f}", "-i", src, "-t", f"{hi - lo + 1:.3f}", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(160) / 160, "same")[::160])
    thr = np.percentile(rms, 60) * 0.5
    cuts = []
    for a, b in zip(words, words[1:]):
        gap = b["start"] - a["end"]
        if gap <= 0.3:
            continue
        s0, s1 = src_t(a["end"]), src_t(b["start"])
        if s0 is None or s1 is None or s1 <= s0 or s1 - s0 > gap + 0.05:
            continue  # the gap spans a segment join: already cut
        voiced = (rms[int((s0 - lo) * 100):int((s1 - lo) * 100)] > thr).sum() / 100
        if voiced >= 0.12 or gap > 0.5:
            c0, c1 = a["end"] + 0.06, b["start"] - 0.08
            if c1 - c0 > 0.15:
                cuts.append((c0, c1))
    return cuts


def apply_cuts(pieces, words, cuts, fps):
    """Remove clip-time ranges: split pieces, drop the removed frames, retime words. A cut inside one camera shot
    is a jump, so the piece after it toggles a punch-in."""
    if not cuts:
        for q in pieces:
            q["punch"] = False
        return pieces, words
    out, t = [], 0.0
    for p in pieces:
        n = p["src_out"] - p["src_in"]
        keep = [(0, n)]
        for c0, c1 in cuts:
            f0, f1 = int(round((c0 - t) * fps)), int(round((c1 - t) * fps))
            if f1 <= 0 or f0 >= n:
                continue
            nk = []
            for k0, k1 in keep:
                if f1 <= k0 or f0 >= k1:
                    nk.append((k0, k1))
                    continue
                if f0 > k0:
                    nk.append((k0, f0))
                if f1 < k1:
                    nk.append((f1, k1))
            keep = nk
        for j, (k0, k1) in enumerate(keep):
            if k1 - k0 < 2:
                continue
            out.append(dict(p, src_in=p["src_in"] + k0, src_out=p["src_in"] + k1, track=p["track"][k0:k1], jump=j > 0))
        t += n / fps
    on = False
    for q in out:  # alternate the punch-in at every jump; a camera change resets it
        on = (not on) if q["jump"] else False
        q["punch"] = on
    def shift(x):
        return x - sum(min(c1, x) - c0 for c0, c1 in cuts if c0 < x)
    W = [dict(w, start=shift(w["start"]), end=shift(w["end"])) for w in words
         if not any(c0 <= (w["start"] + w["end"]) / 2 < c1 for c0, c1 in cuts)]
    return out, W


def caption_text(t):
    for p, r in FIX:
        t = re.sub(p, r, t)
    return t


def prep(src, row, root, fps):
    global SRC
    SRC = src
    cid, slug = row["id"], row["slug"]
    job = f"{root}/{cid}-{slug}"
    os.makedirs(job, exist_ok=True)
    segs = [re.fullmatch(r"\s*([\d:.]+)-([\d:.]+)(?:\{(.*?)\|(.*?)\})?\s*", x).groups() for x in row["segments"].split("+")]
    segs = [(secs(a), secs(b), f, l) for a, b, f, l in segs]
    W = transcribe(src, min(x[0] for x in segs) - 10, max(x[1] for x in segs) + 10)
    warn, pieces, words, t0, seg_ends = [], [], [], 0.0, []
    for a, b, first, final in segs:
        s, e, ws = snap(W, a, b, first, final, warn)
        f_in, f_out = int(round(s * fps)), int(round(e * fps))
        for f0, f1, fx, fy, tr in shots_and_faces(src, f_in / fps, f_out / fps, fps):
            pieces.append(dict(src_in=f_in + f0, src_out=f_in + f1, face_x=fx, face_y=fy, track=tr))
        for w in ws:
            words.append(dict(w=caption_text(w["w"]), start=w["start"] - f_in / fps + t0, end=min(w["end"], f_out / fps) - f_in / fps + t0))
        t0 += (f_out - f_in) / fps
        seg_ends.append(t0)
    cuts = filler_cuts(src, pieces, words, fps)
    pieces, words = apply_cuts(pieces, words, cuts, fps)
    seg_ends = [e - sum(min(c1, e) - c0 for c0, c1 in cuts if c0 < e) for e in seg_ends]
    t0 = sum((p["src_out"] - p["src_in"]) / fps for p in pieces)
    if cuts:
        warn.append(f"cut {len(cuts)} ums/pauses ({sum(b - a for a, b in cuts):.1f}s)")
    # "(2)": the question spans 2 segments. "hook first" = a line lifted from later in the clip opens it, then cuts back
    m = re.match(r"(?:James|Galligan|hook) (?:asks )?first(?: \((\d)\))?", row["why"])
    hook_end = seg_ends[int(m.group(1) or 1) - 1] if m else 0.0
    if hook_end:
        t_ = 0.0
        for k, pc in enumerate(pieces):
            n_ = (pc["src_out"] - pc["src_in"]) / fps
            if t_ >= hook_end - 0.02 and k > 0:
                if pc["src_out"] - pc["src_in"] < 30:  # a flash of another angle as the answer starts
                    q = pieces[k - 1]
                    pc["video_in"] = q["src_out"]       # continue the question shot under the answer's first words
                    pc["track"] = [q["track"][-1]] * (pc["src_out"] - pc["src_in"])
                    pc["punch"] = q.get("punch", False)
                break
            t_ += n_
    for w in words:
        w["norm"] = norm(w["w"])
    cap, k = [], 0
    while k < len(words):  # a sentence that's only "Yeah." / "Right." is the other mic reacting: no caption
        j = k
        while j < len(words) - 1 and words[j]["w"][-1:] not in ".?!":
            j += 1
        sent = words[k:j + 1]
        if not (len(sent) <= 3 and all(norm(w["w"]) in FILLER for w in sent)):
            cap += [w for w in sent if w["norm"] not in DROP]
        k = j + 1
    he = hook_end if 'hook_end' in dir() else 0.0
    pre = [w for w in cap if w["norm"] and w["start"] < he - 0.02]
    post = [w for w in cap if w["norm"] and w["start"] >= he - 0.02]
    phrases = (split(pre, STYLE["phrases"]) if pre else []) + (split(post, STYLE["phrases"]) if post else [])
    for ph in phrases:  # light punctuation: keep ? and !, drop full stops and commas
        ph["text"] = re.sub(r"[.,;:]+(\s|$)", r"\1", ph["text"]).strip()
    json.dump(dict(id=cid, slug=slug, speaker=row["speaker"], why=row["why"], fps=fps, source=src, dur=t0,
                   pieces=pieces, words=words, phrases=phrases, hook_end=hook_end,
                   hook_words=[w for w in words if w["end"] <= hook_end + 0.05], warnings=warn), open(f"{job}/clip.json", "w"), indent=1)
    print(f"{cid} {slug}: {t0:.1f}s, {len(pieces)} shots, {len(phrases)} captions" + (f"  ! {'; '.join(warn)}" if warn else ""), flush=True)


if __name__ == "__main__":
    src, tsv, root = sys.argv[1:4]
    only = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
    fps = 25
    rows = list(csv.DictReader(open(tsv), delimiter="\t", fieldnames=["id", "slug", "segments", "speaker", "why"]))[1:]
    for row in rows:
        if not only or row["id"] in only:
            try:
                prep(src, row, root, fps)
            except Exception as ex:
                print(f"{row['id']} FAILED: {ex}", flush=True)
