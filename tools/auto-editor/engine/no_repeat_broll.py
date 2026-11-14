"""HARD RULE (Eoin, 10 Nov 2026): the same b-roll clip never appears twice in one reel.
assert_unique(files) stops a build before anything is placed; check_timeline(t) audits a built timeline."""
from collections import Counter

def assert_unique(files):
    dup = [f for f, n in Counter(f for f in files if f).items() if n > 1]
    if dup:
        raise SystemExit(f"STOP: b-roll clip used more than once in this reel: {dup}")

def check_timeline(t, tracks=(2,)):
    names = []
    for tr in tracks:
        for it in t.GetItemListInTrack("video", tr) or []:
            mp = it.GetMediaPoolItem()
            if mp: names.append(mp.GetName())
    assert_unique(names)
