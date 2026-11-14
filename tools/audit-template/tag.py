#!/usr/bin/env python3
"""TEMPLATE. Tag every reel by format: caption rules + verified overrides -> data/ig_tags.json. Rerun after captions/covers land."""
import json, re
R = json.load(open('data/ig_reels.json'))
CAP = {}
for l in open('data/ig_meta.jsonl'):
    d = json.loads(l); CAP[d['code']] = d['cap']
OVR = {  # verified by transcript / frames / cover-sheet pass: 'CODE': ['fmt', 'short label']
 # 'DXcj-GkjCLM': ['live', 'Live reaction: "it's gone"'],   <- example from the Kyle build
}
RULES = [
 ('promo',       r'seminar|ticket|book now|secure your|limited spots|early bird'),  # add the client's event words
 ('curiosity',   r'what do you do for a living'),
 ('lifestyle',   r'\bpov\b|la baby|lock in|vision > reality|dream car|#travel|marbella 🔥|villa'),
 ('testimonial', r'testimonial|\bclient\b|clients|shifted his|results don|called me|k/month|£\d|\$\d'),
 ('live',        r'live session|hypnosis session|session with|removing|removed|watch me|hypnoti[sz]e[sd]? (my|this|him|her)'),
 ('event',       r'mastermind|\bevent\b|\btalk\b|workshop|on stage'),
 ('podcast',     r'episode|podcast|🎙'),
 ('ytcut',       r'youtube|full video|full talk'),
]
tags = {}
for r in R:
    c = r['code']
    if c in OVR: tags[c] = OVR[c]; continue
    cap = CAP.get(c)
    if cap is None: continue
    low = cap.lower(); first = re.sub(r'\s+', ' ', cap.split('\n')[0]).strip()[:80] or '(no caption)'
    fmt = next((f for f, rx in RULES if re.search(rx, low)), 'teach')
    tags[c] = [fmt, first]
json.dump(tags, open('data/ig_tags.json', 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print('tagged', len(tags), 'of', len(R), Counter(v[0] for v in tags.values()))
pov = [(c, v[1]) for c, v in tags.items() if re.search(r'\bpov\b', (CAP.get(c) or '').lower()) or 'POV' in v[1]]
print('POV reels:', pov)
