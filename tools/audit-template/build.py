#!/usr/bin/env python3
"""WellSetMedia content audit TEMPLATE (from the Kyle Ritchie build) -> report.html (+ report.pdf via headless Chrome).

Data masters (pulled live 2026-09-13) in data/: ig_reels.json (views/likes/comments/date),
ig_meta.jsonl (captions), ig_tags.json (hand tags), transcripts.json (hooks), yt_full.jsonl.
Covers in img/covers/. Shared look: ../../../tools/audit_kit.py
Run:  python3 build.py
"""
import json, os, sys, statistics as st, subprocess, html, tempfile
from collections import defaultdict
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', '..', 'tools')))
from audit_kit import CSS, LENS, TIP_JS, bar_path, hbar_path, TEAL, SLATE, GRID

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
e = html.escape
med = lambda xs: st.median(xs) if xs else 0
def k(v): return f'{v/1000:.1f}K'.replace('.0K', 'K') if v >= 1000 else f'{v:,}'
def ig(code): return f'https://www.instagram.com/reel/{code}/'
def yt(vid): return f'https://www.youtube.com/watch?v={vid}'

# ---------- data ----------
R = json.load(open('data/ig_reels.json'))                                   # newest first
CAP = {}
if os.path.exists('data/ig_meta.jsonl'):
    for l in open('data/ig_meta.jsonl'):
        d = json.loads(l); CAP[d['code']] = d['cap']
TAGS = json.load(open('data/ig_tags.json')) if os.path.exists('data/ig_tags.json') else {}
TR = json.load(open('data/transcripts.json'))
CFG = json.load(open('data/config.json'))                                    # client, key reels, copy
import datetime as _dt
CL = CFG['client']; AS_OF = CL['as_of']; FOLLOWERS, POSTS = CL['followers'], CL['posts']
Y = [json.loads(l) for l in open('data/yt_full.jsonl')] if os.path.exists('data/yt_full.jsonl') else []   # not every client has a channel
RC = {r['code']: r for r in R}

FMT_NAME = {'live': 'Live session / reaction', 'testimonial': 'Client testimonial', 'take': 'Contrarian take',
            'curiosity': 'Curiosity hook ("what do you do?")', 'lifestyle': 'Lifestyle / aspiration',
            'teach': 'Teaching to camera', 'ytcut': 'YouTube cut-down', 'podcast': 'Podcast-set clip',
            'event': 'Event / mastermind footage', 'promo': 'Promo (paid)', 'story': 'Personal story'}
TOF = {'live', 'take', 'curiosity', 'lifestyle', 'story'}
if CFG.get('formats'):                                                      # per-client format names + which ones reach strangers
    FMT_NAME.update(CFG['formats'].get('names', {}))
    TOF = set(CFG['formats'].get('tof', TOF))

def cover(code):
    return f'img/covers/{code}.jpg'

def letterboxed(code):
    """True if the cover has black bars top and bottom (a 16:9 clip inside the 9:16 frame)."""
    p = cover(code)
    if not os.path.exists(p): return None
    im = Image.open(p).convert('L'); w, h = im.size
    band = max(4, int(h * 0.10))
    top = im.crop((0, int(h * 0.02), w, int(h * 0.02) + band)); bot = im.crop((0, h - int(h * 0.02) - band, w, h - int(h * 0.02)))
    m = lambda x: sum(x.getdata()) / (x.size[0] * x.size[1])
    return m(top) < 14 and m(bot) < 14

for r in R:
    r['fmt'], r['label'] = TAGS.get(r['code'], ['teach', (CAP.get(r['code'], '') or '').split('\n')[0][:70]])
    r['lb'] = letterboxed(r['code'])
    if r['lb'] and r['fmt'] in ('teach', 'podcast'):                        # a letterboxed lesson = a YouTube cut-down
        r['fmt'] = 'ytcut'
    r['hidden_likes'] = r['likes'] <= 3 and r['views'] > 1500
M = [r for r in R if r['date'] < CL['fresh_before']]                          # newest days still accruing
ORG = [r for r in M if r['fmt'] != 'promo']                                  # organic only
NOW = [r for r in ORG if r['date'] >= CL['now_from']]                         # the analysis window
_f = _dt.date.fromisoformat(CL['fresh_before'])
L90 = [r for r in ORG if r['date'] >= str(_f - _dt.timedelta(days=90))]
per_month = len([r for r in R if CL['now_from'] <= r['date'] < CL['fresh_before']]) / max(1, (_f - _dt.date.fromisoformat(CL['now_from'])).days / 30.44)

by = defaultdict(list)
for r in NOW: by[r['fmt']].append(r)
TOT = sum(r['views'] for r in NOW)
FMT = sorted([dict(k=kk, name=FMT_NAME[kk], n=len(v), med=med([r['views'] for r in v]),
                   vshare=sum(r['views'] for r in v) / TOT * 100, pshare=len(v) / len(NOW) * 100)
              for kk, v in by.items()], key=lambda f: -f['med'])
F = {f['k']: f for f in FMT}
LB = [r['views'] for r in NOW if r['lb']]; NAT = [r['views'] for r in NOW if r['lb'] is False]
if not CFG.get('lb_tiles'):                                                  # auto-pick recent letterboxed examples
    CFG['lb_tiles'] = [r['code'] for r in NOW if r['lb'] and r['fmt'] == 'ytcut'][:6]
TOF_SHARE = sum(F[x]['pshare'] for x in TOF if x in F)
TOF_VSHARE = sum(F[x]['vshare'] for x in TOF if x in F)

YL = sorted([y for y in Y if not (y['duration'] <= 180 and (y.get('height') or 0) > (y.get('width') or 1))], key=lambda y: y['upload_date'])
YT_MED = med([y['view_count'] for y in YL])
_ys = CL.get('yt_split', '00000000')
YT_PRE = med([y['view_count'] for y in YL if y['upload_date'] < _ys])
YT_POST = med([y['view_count'] for y in YL if y['upload_date'] >= _ys])
YT_SUBS = CL.get('yt_subs') or max(((y.get('channel_follower_count') or 0) for y in Y), default=0)

# ---------- charts ----------
def chart_timeline():
    W, H, l, rt, t, b = 1040, 330, 58, 14, 34, 44
    rows = list(reversed(M)); n = len(rows); band = (W - l - rt) / n; bw = max(1.6, band * 0.72)
    ymax = max(10000, -(-max(r['views'] for r in M) // 10000) * 10000)
    Y_ = lambda v: t + (H - t - b) * (1 - v / ymax)
    out = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Views on every reel in the window">']
    for tv in range(0, ymax + 1, 10000 if ymax <= 80000 else 20000):
        yy = Y_(tv)
        out.append(f'<line x1="{l}" x2="{W-rt}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{l-10}" y="{yy+4:.1f}" text-anchor="end" class="ax">{k(tv) if tv else 0}</text>')
    lastmo = None
    span_long = len({r['date'][:4] for r in rows}) > 2                      # >2 calendar years: label years, not quarters
    for j, r in enumerate(rows):
        x = l + j * band + (band - bw) / 2; y0 = Y_(r['views']); h = Y_(0) - y0
        tip = f"{r['date'][8:]}/{r['date'][5:7]}/{r['date'][2:4]} · {r['views']:,} views — {FMT_NAME[r['fmt']]}: {r['label']}"
        if r['fmt'] == 'promo':
            mark = f'<path d="{bar_path(x, y0, bw, h, 1)}" fill="none" stroke="#EDE9D6" stroke-width="1" stroke-dasharray="2 2" data-tip="{e(tip)}"/>'
        else:
            mark = f'<path d="{bar_path(x, y0, bw, h, 1)}" fill="{TEAL if r["fmt"] in TOF else SLATE}" data-tip="{e(tip)}"/>'
        out.append(f'<a href="{ig(r["code"])}" target="_blank" rel="noopener">{mark}</a>')
        mo = r['date'][:7]
        if mo != lastmo and ((span_long and mo[5:] == '01') or (not span_long and mo[5:] in ('01', '04', '07', '10'))):
            lab = mo[:4] if span_long else f'{["","Jan","","","Apr","","","Jul","","","Oct"][int(mo[5:])]} {mo[2:4]}'
            out.append(f'<text x="{x:.1f}" y="{H-14}" class="ax">{lab}</text>')
        lastmo = mo
        if r['code'] in CFG['timeline_labels']:
            anchor = 'end' if j > n * 0.55 else 'start'; dx = -6 if anchor == 'end' else bw + 6
            out.append(f'<text x="{x+dx:.1f}" y="{y0+11:.1f}" text-anchor="{anchor}" class="ann"><tspan class="annv">{k(r["views"])}</tspan> {e(CFG["timeline_labels"][r["code"]])}</text>')
    out.append('</svg>')
    return '\n'.join(out)

def chart_formats():
    W, row, l, vw = 780, 40, 300, 400
    H = row * len(FMT) + 20; xmax = max(f['med'] for f in FMT) * 1.12
    out = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Median views by format since February 2026">']
    for j, f in enumerate(FMT):
        y = 10 + j * row; w = max(3, vw * f['med'] / xmax)
        c = TEAL if f['k'] in TOF else SLATE
        out.append(f'<text x="{l-14}" y="{y+17}" text-anchor="end" class="lbl">{e(f["name"])}</text>')
        out.append(f'<text x="{l-14}" y="{y+31}" text-anchor="end" class="ax">{f["n"]} reel{"s" if f["n"]>1 else ""}{" · small sample" if f["n"]<4 else ""}</text>')
        out.append(f'<path d="{hbar_path(l, y+6, w, 20)}" fill="{c}" data-tip="{e(f["name"])}: {f["n"]} reels, median {f["med"]:,.0f}, {f["pshare"]:.0f}% of reels, {f["vshare"]:.0f}% of views"/>')
        out.append(f'<text x="{l+w+10:.1f}" y="{y+21}" class="val">{f["med"]:,.0f}</text>')
    out.append('</svg>')
    return '\n'.join(out)

def chart_share():
    keys = [f['k'] for f in sorted(FMT, key=lambda f: -f['pshare'])][:6]
    W, row, l, vw = 780, 58, 300, 400
    H = row * len(keys) + 40; xmax = max(max(F[x]['pshare'], F[x]['vshare']) for x in keys) * 1.15
    out = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Share of reels posted versus share of views by format">']
    out.append(f'<rect x="{l}" y="4" width="12" height="12" rx="2" fill="{SLATE}"/><text x="{l+18}" y="14" class="ax">share of reels posted</text>')
    out.append(f'<rect x="{l+190}" y="4" width="12" height="12" rx="2" fill="{TEAL}"/><text x="{l+208}" y="14" class="ax">share of all views</text>')
    for j, kk in enumerate(keys):
        f = F[kk]; y = 34 + j * row
        out.append(f'<text x="{l-14}" y="{y+22}" text-anchor="end" class="lbl">{e(f["name"])}</text>')
        for m, (val, c, nm) in enumerate([(f['pshare'], SLATE, 'of reels posted'), (f['vshare'], TEAL, 'of all views')]):
            yy = y + 4 + m * 20; w = max(2, vw * val / xmax)
            out.append(f'<path d="{hbar_path(l, yy, w, 15)}" fill="{c}" data-tip="{e(f["name"])}: {val:.0f}% {nm}"/>')
            out.append(f'<text x="{l+w+8:.1f}" y="{yy+12}" class="val sm">{val:.0f}%</text>')
    out.append('</svg>')
    return '\n'.join(out)

def chart_yt_vs_ig():
    W, row, l, vw = 780, 44, 300, 400
    rows = [('Instagram reel, median', med([r['views'] for r in NOW]), TEAL),
            ('YouTube long-form, median', YT_POST, SLATE)]
    xmax = rows[0][1] * 1.12
    out = [f'<svg viewBox="0 0 {W} {row*2+16}" class="chart" role="img" aria-label="Instagram median views against YouTube median views">']
    for j, (name, v, c) in enumerate(rows):
        y = 8 + j * row; w = max(3, vw * v / xmax)
        out.append(f'<text x="{l-14}" y="{y+20}" text-anchor="end" class="lbl">{e(name)}</text>')
        out.append(f'<path d="{hbar_path(l, y+6, w, 22)}" fill="{c}" data-tip="{e(name)}: {v:,.0f}"/>')
        out.append(f'<text x="{l+w+10:.1f}" y="{y+22}" class="val">{v:,.0f}</text>')
    out.append('</svg>')
    return '\n'.join(out)

# ---------- components ----------
def card(code, why, title=None):
    r = RC[code]
    likes = 'likes hidden' if r['hidden_likes'] else f"{r['likes']:,} likes"
    return f'''<figure class="card"><a href="{ig(code)}" target="_blank" rel="noopener"><img src="{cover(code)}" alt="{e(title or r['label'])}" loading="lazy"></a>
  <figcaption><div class="num">{r['views']:,}<span> views</span></div>
  <div class="meta">{likes} · {r['comments']} comments · {e(FMT_NAME[r['fmt']])}</div>
  <div class="ttl">{e(title or r['label'])}</div><p>{why}</p>
  <a class="lnk" href="{ig(code)}" target="_blank" rel="noopener">Open reel ↗</a></figcaption></figure>'''

def mini(code, cap=None):
    r = RC[code]
    return (f'<a class="mini" href="{ig(code)}" target="_blank" rel="noopener"><img src="{cover(code)}" alt="{e(r["label"])}" loading="lazy">'
            f'<span>{r["views"]:,}</span>{f"<em>{e(cap)}</em>" if cap else ""}</a>')

def transcript(code, upto, notes):
    segs = [s for s in TR[code]['segments'] if s[0] <= upto]
    rows = []
    for t, txt in segs:
        note = notes.get(f'{t}', '')
        rows.append(f'<div class="tl{" flag" if note else ""}"><span class="ts">0:{int(t):02d}</span><span class="tx2">{e(txt)}</span>'
                    f'{f"<span class=nt>{e(note)}</span>" if note else ""}</div>')
    return '<div class="script">' + ''.join(rows) + '</div>'

# ---------- page ----------
EXTRA_CSS = """
.script{background:var(--ink2);border:1px solid var(--line);border-radius:10px;padding:10px 0;margin:16px 0}
.tl{display:grid;grid-template-columns:56px minmax(0,1fr);gap:4px 12px;padding:7px 18px;border-left:3px solid transparent}
.tl .ts{font-variant-numeric:tabular-nums;color:var(--muted);font-size:13px;padding-top:2px}
.tl .tx2{color:var(--bone);font-size:15.5px}
.tl .nt{grid-column:2;font-size:13px;font-weight:650;color:var(--teal-hi)}
.tl.flag{border-left-color:var(--teal-hi);background:rgba(72,160,188,.07)}
h3.sub{margin:40px 0 10px;font-size:21px;max-width:40ch;text-wrap:balance}
.chartbox.narrow .chart{max-width:820px}
.chart .lbl.sm{font-size:13px}
.card img{aspect-ratio:9/16}
.scard .card{max-width:340px}
.mini img{aspect-ratio:9/16}
"""

S = dict(teach_p=F.get('teach', {}).get('pshare', 0), teach_med=F.get('teach', {}).get('med', 0),
         live_p=F.get('live', {}).get('pshare', 0), live_med=F.get('live', {}).get('med', 0),
         test_p=F.get('testimonial', {}).get('pshare', 0), test_med=F.get('testimonial', {}).get('med', 0),
         ytcut_p=F.get('ytcut', {}).get('pshare', 0), ytcut_med=F.get('ytcut', {}).get('med', 0),
         tof_p=TOF_SHARE, tof_v=TOF_VSHARE, lb_n=len(LB), lb_med=med(LB), nat_med=med(NAT),
         ig_med=med([r['views'] for r in NOW]), yt_pre=YT_PRE, yt_post=YT_POST, yt_subs=YT_SUBS,
         ratio=med([r['views'] for r in NOW]) / max(YT_POST, 1))
PM = f'{per_month:.1f}' if per_month < 10 else f'{per_month:.0f}'
L90_TXT = f'{med([r["views"] for r in L90]):,.0f}' if L90 else '\u2014'   # a page that has not posted in 90 days must not read as 0   # a page posting under one a month must not read as 0
L90_CAP = ('The median over the last 90 days is ' + format(med([r['views'] for r in L90]), ',.0f') + '.') if L90 else 'Nothing has been posted in the last 90 days.'
S.update(l90_med=med([r['views'] for r in L90]), l90_n=len(L90), followers=FOLLOWERS, as_of=AS_OF, per_month=per_month,
         now_n=len(NOW), now_med=med([r['views'] for r in NOW]))
for f in FMT:                                                                # every format gets {<fmt>_p} {<fmt>_med} {<fmt>_n}
    S[f"{f['k']}_p"] = f['pshare']; S[f"{f['k']}_med"] = f['med']; S[f"{f['k']}_n"] = f['n']; S[f"{f['k']}_v"] = f['vshare']
class _Safe(dict):
    def __missing__(self, key): return 0
LBL = {kk: vv.format_map(_Safe(S)) for kk, vv in CFG['labels'].items()}
_gt = CFG.get('gap_tiles') or [['{lb_n}', 'Letterboxed reels, in the window'], ['{lb_med:,.0f}', 'Their median views'], ['{nat_med:,.0f}', 'Full-screen vertical median']]
GAP_TILES = ('<div class="tiles" style="grid-template-columns:repeat(%d,minmax(0,1fr));margin:14px 0">' % len(_gt)
             + ''.join('<div class="tile%s"><div class="v">%s</div><div class="l">%s</div></div>' % (' hl' if i == len(_gt) - 1 else '', v.format_map(_Safe(S)), e(l)) for i, (v, l) in enumerate(_gt))
             + '</div>')
BASE_HTML = ''.join('<tr><td>' + e(m) + '</td><td class="n">' + v.format_map(_Safe(S)) + '</td><td>' + e(src.format_map(_Safe(S))) + '</td></tr>' for m, v, src in CFG['baseline'])
CH = CFG['chips']
YT_APPENDIX = ('<details open><summary>YouTube \u00b7 all ' + str(len(Y)) + ' uploads, newest first</summary>'
               '<div class="tbl"><table><tr><th>Date</th><th class="n">Views</th><th class="n">Likes</th><th>Title</th><th>Link</th></tr>'
               + ''.join(f'<tr><td>{y["upload_date"][6:]}/{y["upload_date"][4:6]}/{y["upload_date"][2:4]}</td><td class="n">{y["view_count"]:,}</td><td class="n">{y.get("like_count") or 0}</td><td>{e(y["title"])}</td><td><a href="{yt(y["id"])}" target="_blank" rel="noopener">{y["id"]}</a></td></tr>' for y in sorted(Y, key=lambda y: y['upload_date'], reverse=True)) + '</table></div></details>') if Y else ''

page = f'''<title>{CL['name']} Content Audit</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap">
<style>{CSS}{EXTRA_CSS}</style>
<div class="wrap">
<header class="top"><div class="mark">{LENS}WellSetMedia</div><div class="meta">Content audit · pulled live {AS_OF}</div></header>

<section style="padding-top:44px">
  <p class="eyebrow">Instagram + YouTube · {e(CL["brand"])}</p>
  <h1>{e(CL["name"])}</h1>
  <p class="lead">{LBL["lead"]}</p>
  <div class="hero">
    <figure class="shot"><a href="https://www.instagram.com/{CL["ig_handle"]}/" target="_blank" rel="noopener"><img src="img/ig-header.jpg" alt="Instagram profile header for {CL["ig_handle"]}"></a>
      <figcaption>instagram.com/{CL["ig_handle"]} · {AS_OF}</figcaption></figure>
    <div class="tiles">
      <div class="tile"><div class="v">{FOLLOWERS:,}</div><div class="l">Instagram followers</div></div>
      <div class="tile"><div class="v">{PM}<small>/ month</small></div><div class="l">Reels posted, in the window</div></div>
      <div class="tile"><div class="v">{L90_TXT}</div><div class="l">{"Median views, last 90 days" if L90 else "No reels in the last 90 days"}</div></div>
      <div class="tile hl"><div class="v">{k(RC[CFG["best"]]["views"])}</div><div class="l">Best organic reel</div></div>
      <div class="tile"><div class="v">{YT_SUBS:,}</div><div class="l">YouTube subscribers</div></div>
      <div class="tile"><div class="v">{YT_POST:,.0f}</div><div class="l">{LBL["yt_tile"]}</div></div>
    </div>
  </div>
  <div class="verdict"><p>{LBL["verdict"]}</p></div>
</section>

<section id="grid">
  <p class="eyebrow">01 · Instagram · every reel, {M[-1]["date"][:7]} to {M[0]["date"][:7]}</p>
  <h2>{LBL["h_grid"]}</h2>
  <p>{LBL["grid_intro"]}</p>
  <div class="chartbox"><div class="legend"><span><i style="background:var(--chart-teal)"></i>Formats that travel</span><span><i style="background:var(--chart-slate)"></i>Everything else</span><span><i style="background:transparent;border:1px dashed #EDE9D6"></i>Promo (paid)</span></div>{chart_timeline()}</div>
  <p class="cap">{len(M)} reels, {M[-1]["date"]} to {M[0]["date"]}. The newest reels are still collecting views and are left out. You've posted about {PM} a month since {CL["now_from"]}. {L90_CAP}</p>
</section>

<section id="formats">
  <p class="eyebrow">02 · What each kind of reel earns · since {CL["now_from"]}</p>
  <h2>{LBL["formats_h2"]}</h2>
  <div class="chartbox narrow"><h3 style="margin:2px 0 10px">Median views, by format</h3>{chart_formats()}</div>
  <div class="chartbox narrow"><h3 style="margin:2px 0 10px">What you post vs what gets watched</h3>{chart_share()}</div>
  <div class="callout"><p>{LBL["formats_callout"]}</p></div>
  <p class="cap">Formats were tagged by hand from each reel's cover and caption. Promos are excluded. Formats with under four reels are signals, not averages.</p>
</section>

<section id="spikes">
  <p class="eyebrow">03 · What already reaches strangers</p>
  <h2>{LBL["h_spikes"]}</h2>
  <p>{LBL["spikes_intro"]}</p>
  <div class="cards">{''.join(card(c, w, t) for c, t, w in CFG["spikes"])}</div>
</section>

<section id="takes">
  <p class="eyebrow">{LBL.get("eb_take", "04 · The take")}</p>
  <h2>{LBL["h_take"]}</h2>
  <div class="two">
    <div class="quote"><div class="q">"{e(CFG["take_quote"])}"</div>
      <div class="s"><span><b>{RC[CFG["take"]]["comments"]}</b>comments</span><span><b>{RC[CFG["take"]]["views"]:,}</b>views</span>{'<span><b>hidden</b>likes</span>' if RC[CFG["take"]]["hidden_likes"] else '<span><b>' + f'{RC[CFG["take"]]["likes"]}' + '</b>likes</span>'}</div>
      <p style="margin:0;font-size:14px">{LBL["take_note"]} <a href="{ig(CFG["take"])}" target="_blank" rel="noopener">Open reel ↗</a></p></div>
    <div><p>{LBL["take_why"]}</p><p>The same move, pointed at your topics:</p></div>
  </div>
  <div class="takes">{''.join(f'<div class="take">"{e(q)}"<small>{e(s)}</small></div>' for q, s in CFG["take_examples"])}</div>
</section>

<section id="script">
  <p class="eyebrow">05 · The script</p>
  <h2>{LBL["h_script"]}</h2>
  <p>{LBL["script_intro"]}</p>
  {transcript(CFG["hook30k"], CFG["hook30k_upto"], CFG["hook30k_notes"]) if CFG.get("hook30k") else ''}
  <div class="callout"><p>{LBL["script_callout"]}</p></div>
  {'<h3 class="sub">' + LBL.get('h_hold', 'The hook that holds') + '</h3>' if CFG.get('paycheck') else ''}
  <div class="two">
    <div class="scard">{card(CFG["paycheck"], LBL["paycheck_why"], CFG["paycheck_title"]) if CFG.get("paycheck") else ''}</div>
    <div>{transcript(CFG["paycheck"], CFG["paycheck_upto"], CFG["paycheck_notes"]) if CFG.get("paycheck") else ''}</div>
  </div>
</section>

<section id="mof">
  <p class="eyebrow">06 · The middle of the funnel</p>
  <h2>{LBL["h_mof"]}</h2>
  <p>{LBL["mof_intro"]}</p>
  <div class="minis">{''.join(mini(c, cap) for c, cap in CFG["mof_tiles"])}</div>
  <p>{LBL["mof_outro"]}</p>
</section>

<section id="gaps">
  <p class="eyebrow">07 · Where the top of the funnel is thin</p>
  <h2>{LBL["h_gaps"]}</h2>
  <h3 class="sub">{LBL["h_lb"]}</h3>
  {GAP_TILES}
  <div class="minis">{''.join(mini(c) for c in CFG["lb_tiles"])}</div>
  <p>{LBL["lb_text"]}</p>
  <h3 class="sub">{LBL["h_broll"]}</h3>
  <p>{LBL["broll_text"]}</p>
  <div class="minis">{''.join(mini(c, cap) for c, cap in CFG["broll_tiles"])}</div>
  <h3 class="sub">{LBL["h_teach"]}</h3>
  <p>{LBL["teach_text"]}</p>
</section>

<section id="youtube">
  <p class="eyebrow">08 · YouTube</p>
  <h2>{LBL["h_yt"]}</h2>
  {f'<div class="chartbox narrow">{chart_yt_vs_ig()}</div>' if Y else ''}
  <p>{LBL["yt_text"]}</p>
</section>

<section id="funnel">
  <p class="eyebrow">09 · The whole funnel</p>
  <h2>{LBL["h_funnel"]}</h2>
  <div class="funnel">
    <div class="stage"><div class="st">Top · reach</div><h3>Strangers finding you</h3><span class="chip {CH[0][0]}">{CH[0][1]}</span><p>{LBL["tof"]}</p></div>
    <div class="stage"><div class="st">Middle · trust</div><h3>Strangers believing you</h3><span class="chip {CH[1][0]}">{CH[1][1]}</span><p>{LBL["mof"]}</p></div>
    <div class="stage"><div class="st">Bottom · convert</div><h3>Followers buying</h3><span class="chip {CH[2][0]}">{CH[2][1]}</span><p>{LBL["bof"]}</p></div>
  </div>
</section>

<section id="play">
  <p class="eyebrow">10 · The play</p>
  <h2>{LBL["h_play"]}</h2>
  <ol class="play">{''.join(f'<li><div><h3>{e(h.format_map(_Safe(S)))}</h3><p>{p.format_map(_Safe(S))}</p></div></li>' for h, p in CFG["play"])}</ol>
  <h3 style="margin-top:34px">The baseline we'd measure against</h3>
  <div class="tbl"><table class="base">
    <tr><th>Measure</th><th class="n">Today</th><th>Source</th></tr>
    {BASE_HTML}
  </table></div>
</section>

<section id="appendix">
  <p class="eyebrow">Appendix · every data point, linked</p>
  <h2>The raw numbers</h2>
  <details open><summary>Instagram · all {len(R)} reels, newest first</summary><div class="tbl"><table>
    <tr><th>Date</th><th class="n">Views</th><th class="n">Likes</th><th class="n">Comm.</th><th>Format</th><th>Reel</th><th>Link</th></tr>
    {''.join(f'<tr><td>{r["date"][8:]}/{r["date"][5:7]}/{r["date"][2:4]}</td><td class="n">{r["views"]:,}</td><td class="n">{"hidden" if r["hidden_likes"] else r["likes"]}</td><td class="n">{r["comments"]}</td><td>{e(FMT_NAME[r["fmt"]])}</td><td>{e(r["label"])}</td><td><a href="{ig(r["code"])}" target="_blank" rel="noopener">{r["code"]}</a></td></tr>' for r in R)}
  </table></div></details>
  {YT_APPENDIX}
</section>

<footer>
  <p><strong>Prepared by WellSetMedia</strong> · <a href="https://wellsetmedia.com" target="_blank" rel="noopener">wellsetmedia.com</a></p>
  <p>Views, likes and comments were read from Instagram and YouTube on {AS_OF}. Post dates come from each reel's ID. Formats were tagged by hand from each reel's cover and caption. Letterboxing was detected from black bars at the top and bottom of each cover. Hooks were transcribed from the reels themselves and lightly cleaned for readability. Reels with hidden like counts are marked "hidden". Promos are excluded from organic figures.</p>
</footer>
</div>
<div id="tip" role="tooltip"></div>
{TIP_JS}
'''

page = page.replace('\ufffd', '')                                     # IG captions carry broken emoji halves
open('report.html', 'w').write(page)
head = page.split('<style>')[0]; css = page.split('<style>')[1].split('</style>')[0]; body = page.split('</style>', 1)[1]
open('report-local.html', 'w').write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                                     + head + '<style>' + css + '</style></head><body>' + body + '</body></html>')
subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=8000',
                '--user-data-dir=' + tempfile.mkdtemp(prefix='audit-chrome-'),   # never share the live Chrome profile: it hangs

                '--print-to-pdf=' + os.path.join(HERE, 'report.pdf'), 'file://' + os.path.join(HERE, 'report-local.html')], capture_output=True)
print('pdf', 'ok' if os.path.exists('report.pdf') else 'FAILED')
print(f'NOW n={len(NOW)} med={med([r["views"] for r in NOW])} L90 n={len(L90)} med={med([r["views"] for r in L90])} per_month={per_month:.1f}')
for f in FMT: print(f"  {f['k']:11} n={f['n']:3} med={f['med']:7.0f} posts={f['pshare']:4.1f}% views={f['vshare']:4.1f}%")
print(f'letterboxed n={len(LB)} med={med(LB)} | native n={len(NAT)} med={med(NAT)} | unknown={sum(1 for r in NOW if r["lb"] is None)}')
print(f'TOF share posts={TOF_SHARE:.1f}% views={TOF_VSHARE:.1f}% | YT pre={YT_PRE} post={YT_POST}')
