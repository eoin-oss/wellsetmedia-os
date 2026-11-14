"""Cut swear words out of prepped podcast clips (clip.json): picture + audio pieces split around the word, words
retimed, hook_end/dur shifted. Kyle rule (21 Oct 2026): no swearing, the odd punchline at most.
Phrase rules: "what the fuck?" goes whole, "the fuck" goes with its "the", per-clip extra spans and keeps in the
job's deswear.json ({"cut": {id: ["word sequence", ...]}, "keep": {id: ["word sequence", ...]}}).
Usage: python3 deswear.py <job root> [ids]"""
import glob, json, os, re, sys

SW = re.compile(r"^(fuck\w*|motherfuck\w*|shit\w*|bullshit|cunt\w*|bastard\w*|twat|wank\w*|bollocks|piss\w*|dick|dickhead|bitch\w*|asshole|arsehole)$")


def n(w):
    return re.sub(r"[^a-z']", "", w.lower())


def seq(W, phrase):
    f = [n(x) for x in phrase.split()]
    return [i for i in range(len(W) - len(f) + 1) if [n(w["w"]) for w in W[i:i + len(f)]] == f], len(f)


def spans_for(W, extra, keep):
    kept = set()
    for ph in keep:
        hits, L = seq(W, ph)
        for i in hits:
            kept |= set(range(i, i + L))
    out = []
    for ph in extra:
        hits, L = seq(W, ph)
        if not hits:
            print(f"  ! cut phrase not found: {ph!r}")
        out += [(i, i + L - 1) for i in hits]
    covered = {k for a, b in out for k in range(a, b + 1)}
    for i, w in enumerate(W):
        if i in covered or i in kept or not SW.match(n(w["w"])):
            continue
        a = b = i
        if i > 0 and n(W[i - 1]["w"]) == "the" and n(w["w"]) == "fuck":
            a = i - 1
            if i > 1 and n(W[i - 2]["w"]) == "what" and w["w"].endswith("?"):
                a = i - 2
        out.append((a, b))
    return sorted(out)


def cut_ranges(W, spans):
    cuts = []
    for a, b in spans:
        c0 = W[a]["start"] - 0.02
        c1 = W[b]["end"] + 0.02
        if a > 0:
            c0 = max(c0, W[a - 1]["end"] + 0.02)
        if b + 1 < len(W):
            c1 = min(c1, W[b + 1]["start"] - 0.02)
        if c1 > c0:
            cuts.append((c0, c1))
    return cuts


def apply(c, cuts, fps):
    out, t = [], 0.0
    for p in c["pieces"]:
        nfr = p["src_out"] - p["src_in"]
        keep = [(0, nfr)]
        for c0, c1 in cuts:
            f0, f1 = int(round((c0 - t) * fps)), int(round((c1 - t) * fps))
            if f1 <= 0 or f0 >= nfr:
                continue
            nk = []
            for k0, k1 in keep:
                if f1 <= k0 or f0 >= k1:
                    nk.append((k0, k1)); continue
                if f0 > k0:
                    nk.append((k0, f0))
                if f1 < k1:
                    nk.append((f1, k1))
            keep = nk
        for j, (k0, k1) in enumerate(keep):
            if k1 - k0 < 2:
                continue
            q = dict(p, src_in=p["src_in"] + k0, src_out=p["src_in"] + k1, track=p["track"][k0:k1])
            if j > 0:
                q["jump"] = True
                q.pop("video_in", None)
            if "video_in" in p and k0 > 0:
                q["video_in"] = p["video_in"] + k0
            q["_new"] = j > 0
            out.append(q)
        t += nfr / fps
    for k, q in enumerate(out):  # every jump flips the punch-in so the cut never shows; camera changes keep theirs
        if k and q.get("jump") and "video_in" not in q:
            q["punch"] = not out[k - 1].get("punch", False)
        q.pop("_new", None)

    def shift(x):
        return x - sum(min(c1, x) - c0 for c0, c1 in cuts if c0 < x)
    W = c["words"]
    keepw = []
    for w in W:
        mid = (w["start"] + w["end"]) / 2
        if any(c0 <= mid < c1 for c0, c1 in cuts):
            p_ = re.search(r"[.?!,]+$", w["w"])
            if p_ and keepw and not re.search(r"[.?!]$", keepw[-1]["w"]):
                keepw[-1]["w"] = keepw[-1]["w"].rstrip(",") + p_.group(0)  # the sentence end survives the word
            continue
        keepw.append(dict(w, start=shift(w["start"]), end=shift(w["end"])))
    c["pieces"], c["words"] = out, keepw
    c["hook_end"] = shift(c["hook_end"]) if c["hook_end"] else 0.0
    c["hook_words"] = [w for w in keepw if w["end"] <= c["hook_end"] + 0.05]
    c["dur"] = sum((p["src_out"] - p["src_in"]) / fps for p in out)
    c["phrases"] = [ph for ph in c.get("phrases", []) if not SW.search(n(ph.get("text", "")))]
    return c


def main(root, only=None):
    cfg = json.load(open(f"{root}/deswear.json")) if os.path.exists(f"{root}/deswear.json") else {}
    for path in sorted(glob.glob(f"{root}/{os.environ.get('AE_PREFIX', 'k')}*/clip.json")):
        c = json.load(open(path))
        if only and c["id"] not in only:
            continue
        W = c["words"]
        sp = spans_for(W, cfg.get("cut", {}).get(c["id"], []), cfg.get("keep", {}).get(c["id"], []))
        if not sp:
            print(f"{c['id']}: clean"); continue
        cuts = cut_ranges(W, sp)
        gone = [" ".join(W[k]["w"] for k in range(a, b + 1)) for a, b in sp]
        d0 = c["dur"]
        apply(c, cuts, c.get("fps", 25))
        c.setdefault("warnings", []).append(f"deswear: cut {len(gone)} ({', '.join(gone)})")
        json.dump(c, open(path, "w"), indent=1)
        print(f"{c['id']}: cut {len(gone)} [{' | '.join(gone)}]  {d0:.2f}s -> {c['dur']:.2f}s, hook_end {c['hook_end']:.2f}")


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]), set(sys.argv[2:]) or None)
