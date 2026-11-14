"""Who is talking, per word, by VOICE (not by what's on camera): the multicam cuts away to the listener nodding, so the
picture can't say who's speaking. Trains a 2-speaker linear voice model (LDA on smoothed log-mel frames) from windows
where only one person talks, scores every word of every clip.json in a job, smooths with a 2-state Viterbi (a switch
costs a little, so one odd word doesn't flip), and writes w["spk"] into clip.json. podbuild_sidecap keeps it.
Analysis only, nothing rendered.
Usage: python3 podspeakers.py <job root> <voices.json> [ids]
voices.json: {"source": "<episode>", "a": "kyle", "b": "james", "kyle": [[s0, s1], ...], "james": [[s0, s1], ...]}
Writes <job>/speakers.txt (every clip's words tagged, for review)."""
import glob, json, os, subprocess, sys
import numpy as np

FPS_MEL = 100


def audio(src, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", src, "-t", f"{b - a:.3f}", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def feats(src, a, b):
    import torch, whisper
    m = whisper.audio.log_mel_spectrogram(torch.from_numpy(audio(src, a, b))).numpy().T  # frames x 80
    k = 3
    pad = np.pad(m, ((k, k), (0, 0)), mode="edge")
    sm = np.stack([pad[i:i + len(m)] for i in range(2 * k + 1)]).mean(0)
    return np.hstack([sm, np.gradient(sm, axis=0)]), m.mean(1)


def train(src, A, B):
    def data(wins):
        out = []
        for a, b in wins:
            f, e = feats(src, a, b)
            out.append(f[e > np.percentile(e, 35)])
        return np.vstack(out)
    X0, X1 = data(A), data(B)
    allx = np.vstack([X0, X1])
    mu, sd = allx.mean(0), allx.std(0) + 1e-6
    X0, X1 = (X0 - mu) / sd, (X1 - mu) / sd
    Sw = np.cov(X0.T) + np.cov(X1.T) + np.eye(X0.shape[1]) * 0.05
    w = np.linalg.solve(Sw, X1.mean(0) - X0.mean(0))
    b = -(X0.mean(0) + X1.mean(0)) @ w / 2
    return mu, sd, w, b


def viterbi(scores, switch=2.5):
    """scores > 0 = speaker b. Two states, emission = +-score (clipped), a switch costs `switch`."""
    s = np.clip(np.asarray(scores, float), -4, 4)
    n = len(s)
    if not n:
        return []
    cost = np.zeros((n, 2)); back = np.zeros((n, 2), int)
    cost[0] = [max(0, s[0]), max(0, -s[0])]
    for i in range(1, n):
        for st in (0, 1):
            e = max(0, s[i]) if st == 0 else max(0, -s[i])
            stay, sw = cost[i - 1, st], cost[i - 1, 1 - st] + switch
            back[i, st] = st if stay <= sw else 1 - st
            cost[i, st] = min(stay, sw) + e
    st = int(np.argmin(cost[-1])); out = [st]
    for i in range(n - 1, 0, -1):
        st = back[i, st]; out.append(st)
    return out[::-1]


def label(c, model, A, B, fps):
    mu, sd, w, b = model
    src = c["source"]
    spans, t = [], 0.0
    for p in c["pieces"]:  # audio follows src_in..src_out, back to back in clip time
        n = (p["src_out"] - p["src_in"]) / fps
        spans.append((t, t + n, p["src_in"] / fps))
        t += n
    # one feature pass per contiguous source run
    runs = []
    for a, e, s0 in spans:
        if runs and abs(runs[-1][3] - s0) < 1e-3:
            runs[-1][1] = e; runs[-1][3] = s0 + (e - a)
        else:
            runs.append([a, e, s0, s0 + (e - a)])
    S, E = [], []
    for a, e, s0, s1 in runs:
        f, en = feats(src, s0, s1)
        S.append(((f - mu) / sd) @ w + b); E.append(en)
    scores = []
    for wd in c["words"]:
        mid = (wd["start"] + wd["end"]) / 2
        k = next((i for i, r in enumerate(runs) if r[0] <= mid < r[1]), len(runs) - 1)
        a = runs[k][0]
        i0 = max(0, int((wd["start"] - a) * FPS_MEL)); i1 = max(i0 + 2, int((wd["end"] - a) * FPS_MEL))
        sc, en = S[k][i0:i1], E[k][i0:i1]
        if len(sc) == 0:
            scores.append(0.0); continue
        thr = np.percentile(E[k], 30)
        v = sc[en > thr] if (en > thr).any() else sc
        scores.append(float(np.mean(v)))
    path = viterbi(scores)
    for wd, st, sc in zip(c["words"], path, scores):
        wd["spk"] = B if st else A
        wd["spk_score"] = round(sc, 2)
    return c


def main(root, spec, only=None):
    v = json.load(open(spec))
    A, B = v["a"], v["b"]
    model = None
    lines = []
    for path in sorted(glob.glob(f"{root}/*/clip.json")):
        c = json.load(open(path))
        if only and c["id"] not in only:
            continue
        model = model or train(v["source"], v[A], v[B])
        label(c, model, A, B, c.get("fps", 25))
        json.dump(c, open(path, "w"), indent=1)
        txt, cur = [], None
        for wd in c["words"]:
            if wd["spk"] != cur:
                cur = wd["spk"]; txt.append(f"\n  [{cur.upper()} {wd['start']:.1f}s]")
            txt.append(wd["w"])
        n = {s: sum(1 for wd in c["words"] if wd["spk"] == s) for s in (A, B)}
        lines.append(f"{c['id']} {c['slug']}  {n}" + " ".join(txt))
        print(c["id"], n, flush=True)
    open(f"{root}/speakers.txt", "w").write("\n\n".join(lines) + "\n")


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]), sys.argv[2], set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None)
