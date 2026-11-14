#!/usr/bin/env python3
"""Weekly content research: watchlist -> outliers -> hook breakdowns -> hook bank + niche trends.

  python3 research.py ingest [WEEK]        data/<week>/raw.txt -> accounts.json (qualified or not) + outliers.json
  python3 research.py media  [WEEK]        per outlier: caption, first 8s transcript, frames at 0 / 1.5 / 3s -> media.json
  python3 research.py bank   [WEEK]        data/<week>/tags.jsonl (written by the tagging agent) -> bank/<person>.jsonl
  python3 research.py trends PERSON [WEEK] tag shares this week vs the 4 before -> markdown for the report
  python3 research.py result PERSON CODE won|dead|tried   mark a hook bank entry after the client's reel lands

WEEK defaults to this ISO week (2026-W43). Outlier maths stays in plain Python on purpose: no model decides it.
"""
import datetime as dt, json, os, statistics as st, subprocess, sys, tempfile
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
WL = json.load(open(os.path.join(HERE, 'watchlists.json')))
RULES = WL['rules']


def week(arg=None):
    if arg: return arg
    y, w, _ = dt.date.today().isocalendar(); return f'{y}-W{w:02d}'


def wdir(w):
    d = os.path.join(HERE, 'data', w); os.makedirs(d, exist_ok=True); return d


def posted(code):
    n = 0
    for x in code: n = n * 64 + A.index(x)
    return dt.datetime.utcfromtimestamp(((n >> 23) + 1314220021721) / 1000).date()


def owners(handle):
    return [p for p, v in WL['people'].items() if handle in v['accounts']]


def ingest(w):
    d = wdir(w); today = dt.date.today()
    accounts, outliers = {}, []
    if os.path.exists(os.path.join(d, 'summary.txt')):          # the normal path: pull.js STEP 3 summary
        return ingest_summary(d, today)
    raw = open(os.path.join(d, 'raw.txt')).read()
    for line in raw.splitlines():
        if '|' not in line: continue
        h, rows = line.split('|', 1)
        reels, fol = [], ''
        toks = rows.replace(';', ' ').split()
        if toks and toks[0].startswith(('F:', 'F=')):
            fol = toks.pop(0)[2:]
            if toks and ',' not in toks[0]: fol = toks.pop(0)   # 'F: 1.6M' split by the space swap
        for r in toks:
            f = r.split(',')
            if len(f) != 4 or not f[1].strip(): continue
            c = f[0]; reels.append(dict(code=c, date=posted(c), views=int(f[1]), likes=int(f[2] or 0), com=int(f[3] or 0)))
        reels.sort(key=lambda r: r['date'], reverse=True)
        settled = [r for r in reels if (today - r['date']).days >= RULES['settle_days']][:RULES['median_window']]
        if len(settled) < 6:
            accounts[h] = dict(reels=len(reels), followers=fol, qualified=False, why='not found / too few reels'); continue
        med = st.median(r['views'] for r in settled)
        recent = [r for r in reels if (today - r['date']).days <= 30]
        q = med >= RULES['min_median_views'] and len(recent) >= RULES['min_posts_30d']
        why = '' if q else ('median under %d' % RULES['min_median_views'] if med < RULES['min_median_views'] else 'posts under %d in 30d' % RULES['min_posts_30d'])
        accounts[h] = dict(reels=len(reels), followers=fol, median=int(med), posts_30d=len(recent), qualified=q, why=why, owners=owners(h))
        if not q: continue
        for r in settled:
            x = r['views'] / med if med else 0
            if x >= RULES['outlier_x'] and (today - r['date']).days <= RULES['outlier_max_age_days']:
                outliers.append(dict(handle=h, code=r['code'], date=str(r['date']), views=r['views'], likes=r['likes'],
                                     com=r['com'], median=int(med), x=round(x, 1), owners=owners(h)))
    # drop anything already in a bank
    known = set()
    for p in WL['people']:
        bp = os.path.join(HERE, 'bank', p + '.jsonl')
        if os.path.exists(bp): known |= {json.loads(l)['code'] for l in open(bp) if l.strip()}
    fresh = [o for o in outliers if o['code'] not in known]
    fresh.sort(key=lambda o: -o['x'])
    json.dump(accounts, open(os.path.join(d, 'accounts.json'), 'w'), indent=1, default=str)
    json.dump(fresh, open(os.path.join(d, 'outliers.json'), 'w'), indent=1)
    print(f'{len(accounts)} accounts, {sum(a["qualified"] for a in accounts.values())} qualified, '
          f'{len(outliers)} outliers ({len(fresh)} new)')
    for h, a in sorted(accounts.items(), key=lambda kv: -kv[1].get('median', 0)):
        print(f'  {"OK  " if a["qualified"] else "FAIL"} {h:28} {a.get("followers", ""):>7} fol  median {a.get("median", "-"):>9}  30d {a.get("posts_30d", "-"):>3}  {a["why"]}')
    for o in fresh[:40]:
        print(f'  {o["x"]:>5}x  {o["views"]:>10,}  {o["handle"]:24} {o["code"]}  {o["date"]}')


def ingest_summary(d, today):
    """summary.txt lines: handle|F:<followers>|N:<settled reels>|M:<median>|P:<posts 30d>|code,views,likes,com ... (reels >= 2x median, <= 60d).
    The browser only pre-filters at 2x so the dump fits the tool output; the real rules are applied here."""
    accounts, outliers = {}, []
    for line in open(os.path.join(d, 'summary.txt')).read().splitlines():
        if '|' not in line: continue
        h, F, N, M, P, cand = (line.split('|') + [''] * 6)[:6]
        fol, n, med, posts = F[2:], int(N[2:] or 0), int(M[2:] or 0), int(P[2:] or 0)
        if n < 6:
            accounts[h] = dict(followers=fol, qualified=False, why='WRONG HANDLE or not found (%s followers)' % (fol or '?'), owners=owners(h)); continue
        q = med >= RULES['min_median_views'] and posts >= RULES['min_posts_30d']
        why = '' if q else ('median under %d' % RULES['min_median_views'] if med < RULES['min_median_views'] else 'posts under %d in 30d' % RULES['min_posts_30d'])
        accounts[h] = dict(followers=fol, reels=n, median=med, posts_30d=posts, qualified=q, why=why, owners=owners(h))
        if not q: continue
        for r in cand.split():
            c, v, l, m = r.split(','); v = int(v); x = v / med
            if x >= RULES['outlier_x'] and (today - posted(c)).days <= RULES['outlier_max_age_days']:
                outliers.append(dict(handle=h, code=c, date=str(posted(c)), views=v, likes=int(l), com=int(m), median=med,
                                     x=round(x, 1), owners=owners(h), hidden_likes=int(l) <= 3))
    return finish_ingest(d, accounts, outliers)


def finish_ingest(d, accounts, outliers):
    known = set()
    for p in WL['people']:
        bp = os.path.join(HERE, 'bank', p + '.jsonl')
        if os.path.exists(bp): known |= {json.loads(l)['code'] for l in open(bp) if l.strip()}
    fresh = sorted([o for o in outliers if o['code'] not in known], key=lambda o: -o['x'])
    json.dump(accounts, open(os.path.join(d, 'accounts.json'), 'w'), indent=1, default=str)
    json.dump(fresh, open(os.path.join(d, 'outliers.json'), 'w'), indent=1)
    print(f'{len(accounts)} accounts, {sum(a["qualified"] for a in accounts.values())} qualified, {len(fresh)} new outliers')
    for h, a in sorted(accounts.items(), key=lambda kv: -kv[1].get('median', 0)):
        print(f'  {"OK  " if a["qualified"] else "FAIL"} {h:28} {a.get("followers", ""):>6}  median {a.get("median", "-"):>9}  30d {a.get("posts_30d", "-"):>3}  {a["why"]}')
    for o in fresh:
        print(f'  {o["x"]:>6}x  {o["views"]:>11,}  {o["handle"]:24} {o["code"]}  {o["date"]}  {"/".join(o["owners"])}')


def media(w):
    import whisper
    d = wdir(w); fr = os.path.join(d, 'frames'); os.makedirs(fr, exist_ok=True)
    cache = os.path.join(tempfile.gettempdir(), 'research-cache'); os.makedirs(cache, exist_ok=True)
    out_p = os.path.join(d, 'media.json')
    M = json.load(open(out_p)) if os.path.exists(out_p) else {}
    model = whisper.load_model('base')
    for o in json.load(open(os.path.join(d, 'outliers.json'))):
        c = o['code']
        if c in M and M[c].get('hook'): continue
        url = f'https://www.instagram.com/reel/{c}/'
        meta = subprocess.run(['yt-dlp', '-j', '--no-warnings', url], capture_output=True, text=True).stdout
        try: j = json.loads(meta)
        except Exception: print(c, 'meta failed'); continue
        p = os.path.join(cache, c + '.mp4')
        if not os.path.exists(p):
            subprocess.run(['yt-dlp', '-q', '--no-warnings', '-o', p, url], capture_output=True)
        rec = dict(caption=(j.get('description') or '')[:600], duration=j.get('duration'),
                   track=' - '.join(x for x in [j.get('artist'), j.get('track')] if x) or None)
        if os.path.exists(p):
            for t in (0, 1.5, 3):
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', p, '-frames:v', '1', '-vf', 'scale=540:-1',
                                os.path.join(fr, f'{c}_{t}.jpg')])
            r = model.transcribe(p, language='en', fp16=False, clip_timestamps=[0, 8])
            rec['hook'] = ' '.join(s['text'].strip() for s in r['segments'] if s['start'] < 8)
        M[c] = rec; print(c, '|', (rec.get('hook') or '')[:90])
        json.dump(M, open(out_p, 'w'), indent=1)
        subprocess.run(['sleep', '1.5'])
    print('media for', len(M), 'outliers ->', out_p)


def bank(w):
    d = wdir(w); O = {o['code']: o for o in json.load(open(os.path.join(d, 'outliers.json')))}
    n = Counter()
    for l in open(os.path.join(d, 'tags.jsonl')):
        if not l.strip(): continue
        t = json.loads(l); o = O.get(t['code'], {})
        rec = {**o, **t, 'week': w, 'status': 'seen'}
        for p in o.get('owners') or t.get('owners') or []:
            bp = os.path.join(HERE, 'bank', p + '.jsonl')
            have = {json.loads(x)['code'] for x in open(bp)} if os.path.exists(bp) else set()
            if rec['code'] in have: continue
            open(bp, 'a').write(json.dumps(rec) + '\n'); n[p] += 1
    print('banked:', dict(n))


def load_bank(person):
    bp = os.path.join(HERE, 'bank', person + '.jsonl')
    return [json.loads(l) for l in open(bp) if l.strip()] if os.path.exists(bp) else []


def trends(person, w):
    B = load_bank(person)
    y, n = int(w[:4]), int(w[6:])
    prev = set()
    for k in range(1, 5):
        dd = dt.date.fromisocalendar(y, n, 1) - dt.timedelta(weeks=k); yy, ww, _ = dd.isocalendar(); prev.add(f'{yy}-W{ww:02d}')
    now = [b for b in B if b['week'] == w]; before = [b for b in B if b['week'] in prev]
    print(f'## Niche trends · {person} · {w}\n\n{len(now)} outliers this week, {len(before)} in the 4 weeks before.\n')
    for field in ('hook_type', 'format', 'topic', 'visual_open', 'text_hook', 'cta', 'length'):
        cn = Counter(b.get(field) for b in now if b.get(field)); cb = Counter(b.get(field) for b in before if b.get(field))
        if not cn: continue
        print(f'**{field}**\n\n| tag | this week | share | 4 weeks before | share | avg multiple |\n|---|---|---|---|---|---|')
        for tag, c in cn.most_common(8):
            xs = [b['x'] for b in now if b.get(field) == tag and b.get('x')]
            sb = cb.get(tag, 0)
            avg = f'{st.mean(xs):.1f}x' if xs else '-'
            print(f'| {tag} | {c} | {c / len(now):.0%} | {sb} | {(sb / len(before)) if before else 0:.0%} | {avg} |')
        print()
    res = Counter(b['status'] for b in B)
    print(f'**Hook bank:** {len(B)} entries · tried {res["tried"]} · won {res["won"]} · dead {res["dead"]}')


def result(person, code, status):
    bp = os.path.join(HERE, 'bank', person + '.jsonl'); B = load_bank(person)
    for b in B:
        if b['code'] == code: b['status'] = status
    open(bp, 'w').write(''.join(json.dumps(b) + '\n' for b in B)); print(code, '->', status)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    cmd = a[0]
    if cmd == 'ingest': ingest(week(a[1] if len(a) > 1 else None))
    elif cmd == 'media': media(week(a[1] if len(a) > 1 else None))
    elif cmd == 'bank': bank(week(a[1] if len(a) > 1 else None))
    elif cmd == 'trends': trends(a[1], week(a[2] if len(a) > 2 else None))
    elif cmd == 'result': result(a[1], a[2], a[3])
    else: print(__doc__)
