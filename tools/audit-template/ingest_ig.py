#!/usr/bin/env python3
"""data/ig_raw.txt (code,views,likes,comments;...) -> data/ig_reels.json, newest first, with post dates
decoded from each shortcode (media id >> 23 = ms since Instagram's epoch). Prints monthly medians + top 14."""
import datetime, json, os, statistics as st
from collections import defaultdict
os.chdir(os.path.dirname(os.path.abspath(__file__)))
A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
rows, seen, skipped = [], set(), []
for ch in open('data/ig_raw.txt').read().replace('\n', ';').split(';'):
    if not ch.strip(): continue
    c, v, l, m = ch.strip().split(',')
    if c in seen: continue
    seen.add(c); n = 0
    for x in c: n = n * 64 + A.index(x)
    d = datetime.datetime.utcfromtimestamp(((n >> 23) + 1314220021721) / 1000)
    if not str(v).strip():                                                 # pre-2021 posts carry no view count
        skipped.append(c); continue
    rows.append(dict(code=c, date=d.strftime('%Y-%m-%d'), views=int(v), likes=int(l), comments=int(m)))
rows.sort(key=lambda r: r['date'], reverse=True)
json.dump(rows, open('data/ig_reels.json', 'w'), indent=1)
print('skipped (no view count):', skipped)
print(len(rows), 'reels', rows[-1]['date'], '->', rows[0]['date'])
mo = defaultdict(list)
for r in rows: mo[r['date'][:7]].append(r['views'])
for k in sorted(mo): print(k, 'n', len(mo[k]), 'median', st.median(mo[k]), 'max', max(mo[k]))
for r in sorted(rows, key=lambda r: -r['views'])[:14]: print(r)
