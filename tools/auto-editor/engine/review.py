"""B-roll approval sheet: every line, its caption mode, the chosen shot (+alts) with why.
Usage: python3 review.py <job_dir>   -> <job_dir>/review.html"""
import json, os, sys, html
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
job = os.path.abspath(sys.argv[1])
plan = json.load(open(f"{job}/plan.json"))
words = json.load(open(f"{job}/words.json"))
clips = {json.loads(l)["id"]: json.loads(l) for l in open(f"{HOME}/index/clips.jsonl") if '"id"' in l}
thumbs = os.path.relpath(f"{HOME}/index/thumbs", job)


def strip(cid, big=True):
    c = clips.get(cid)
    if not c:
        return f"<div class=miss>{cid}?</div>"
    imgs = "".join(f'<img src="{thumbs}/{t}">' for t in c["thumbs"])
    return f'<div class="clip {"big" if big else "alt"}"><div class=imgs>{imgs}</div><div class=meta>{html.escape(c["folder"].replace("personal brand directory/",""))}/{html.escape(os.path.basename(c["path"]))} · {cid}</div></div>'


rows = []
total = words[-1]["end"]
bsec = 0
for k, s in enumerate(plan["segments"]):
    i0, i1 = s["words"]
    t0, t1 = words[i0]["start"], words[i1]["end"]
    b = s.get("broll")
    if b:
        bsec += t1 - t0
    said = " ".join(w["w"] for w in words[i0:i1 + 1])
    right = (strip(b["id"]) + f'<div class=why>{html.escape(b.get("why",""))}</div>'
             + ('<div class=alts>' + "".join(strip(a, False) for a in b.get("alts", [])) + "</div>" if b.get("alts") else "")
             ) if b else '<div class=aroll>A-roll</div>'
    rows.append(f'<tr class="{"b" if b else "a"}"><td class=n>{k}</td><td class=t>{t0:.1f}s</td>'
                f'<td><div class=cap>{html.escape(s["caption"])}</div><div class=said>{html.escape(said)}</div>'
                f'<div class=mode>{s.get("mode") or ("over_broll" if b else "over_aroll")}</div></td><td>{right}</td></tr>')
doc = f"""<!doctype html><meta charset=utf-8><title>{html.escape(plan['timeline'])} review</title>
<style>body{{font:14px -apple-system,Helvetica;background:#0d0d0d;color:#eee;margin:24px}}table{{border-collapse:collapse;width:100%}}
td{{border-bottom:1px solid #222;padding:10px;vertical-align:top}}.n,.t{{color:#777;width:40px}}.cap{{font-weight:700;font-size:16px}}
.said{{color:#888;margin-top:4px}}.mode{{color:#5aa0ff;font-size:12px;margin-top:6px}}.imgs img{{width:180px;margin-right:3px}}
.alt .imgs img{{width:90px}}.meta{{color:#777;font-size:11px}}.why{{color:#ffd166;margin:4px 0}}.alts{{display:flex;gap:12px;opacity:.7}}
.aroll{{color:#555}}tr.b .cap{{color:#fff}}</style>
<h2>{html.escape(plan['timeline'])}</h2><p>{len(plan['segments'])} lines · b-roll {bsec:.1f}s of {total:.1f}s ({bsec/total:.0%}).
{"".join(f"<p style='color:#ff6b6b'>check: {html.escape(f)}</p>" for f in plan.get("flags", []))}Swap a shot: tell Claude "line N use alt 1 / use &lt;clip id&gt; / A-roll".</p><table>{''.join(rows)}</table>"""
open(f"{job}/review.html", "w").write(doc)
print(f"{job}/review.html")
