"""A-roll joins (jump cuts) and whether b-roll hides them. A join is hidden when a b-roll shot is on screen across
it, or cuts in or out on it (the two A-roll frames either side of the join are never seen back to back).
Usage: python3 joins.py <job_dir> [edl.json]   -> prints per-join status; writes <job>/joins.json"""
import json, os, sys

EDL = "/Volumes/Extreme SSD/wellsetmedia/kyle-seminar-pulls/edl/v2"


def joins_for(job):
    if os.path.exists(f"{job}/joins.json"):
        return json.load(open(f"{job}/joins.json", encoding="utf-8"))
    return []


def edl_joins(edl):
    t, out = 0.0, []
    for c in json.load(open(edl))["short"]:
        t += c["out"] - c["in"]
        out.append(round(t, 2))
    return out[:-1]


def spans(job):
    w = json.load(open(f"{job}/words.json", encoding="utf-8"))
    S = json.load(open(f"{job}/plan.json", encoding="utf-8"))["segments"]
    out = []
    for k, s in enumerate(S):
        last = s.get("through", k)
        sw = (s.get("broll") or {}).get("start_word")
        a = w[sw if sw is not None and s["words"][0] < sw <= s["words"][1] else s["words"][0]]["start"]
        b = w[S[last + 1]["words"][0]]["start"] if last + 1 < len(S) else w[S[last]["words"][1]]["end"]
        out.append((k, a, b, bool(s.get("broll"))))
    return out, w


def check(job, joins):
    sp, w = spans(job)
    res = []
    for j in joins:
        hid = any(x and (a - 0.2 <= j <= b + 0.2) for k, a, b, x in sp)
        seg = next((k for k, a, b, x in sp if a - 0.05 <= j < b), None)
        res.append({"t": j, "hidden": hid, "segment_after": seg})
    return res


if __name__ == "__main__":
    job = sys.argv[1].rstrip("/")
    if len(sys.argv) > 2:
        json.dump(edl_joins(sys.argv[2]), open(f"{job}/joins.json", "w"))
    r = check(job, joins_for(job))
    print(os.path.basename(job), " ".join(f'{x["t"]}{"✓" if x["hidden"] else "✗"}(s{x["segment_after"]})' for x in r),
          f'{sum(x["hidden"] for x in r)}/{len(r)}')
