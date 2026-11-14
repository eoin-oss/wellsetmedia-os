"""WellSetMedia audit kit: shared look + chart helpers for prospect content audits.
Extracted from clients/mark-meehan/audit/build.py (2026-09-13). Import from a client build.py:
    sys.path.insert(0, <wellset-media>/tools); from audit_kit import *
"""
TEAL, SLATE, GRID = '#3595B8', '#6E7B7E', '#24343A'
GRAIN = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)' opacity='.55'/></svg>")

CSS = """
:root{--ink:#0E1113;--ink2:#12171A;--slate:#182428;--line:#24343A;--line-soft:#1B272B;
--bone:#EDE9D6;--body:#C9C6B4;--muted:#7E8A8C;--teal:#2E7E96;--teal-hi:#48A0BC;--chart-teal:#3595B8;--chart-slate:#6E7B7E;color-scheme:dark}
*{box-sizing:border-box}
html{background:var(--ink)}
body{margin:0;background:var(--ink);color:var(--body);font-family:'Inter',-apple-system,BlinkMacSystemFont,'Helvetica Neue',sans-serif;
font-size:16px;line-height:1.6;font-weight:430;-webkit-font-smoothing:antialiased;padding-inline:clamp(16px,4vw,56px)}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background-image:url("GRAIN");opacity:.05;mix-blend-mode:overlay;z-index:50}
.wrap{max-width:1120px;margin:0 auto}
a{color:var(--teal-hi);text-decoration:none}
a:hover{color:var(--bone)}
a:focus-visible{outline:2px solid var(--teal-hi);outline-offset:3px;border-radius:3px}
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:28px 22px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.mark{display:flex;align-items:center;gap:10px;font-weight:900;letter-spacing:-.03em;color:var(--bone);font-size:17px}
.mark svg{width:22px;height:22px}
.top .meta{font-size:12px;font-weight:650;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
section{padding-block:56px 12px}
section+section{border-top:1px solid var(--line-soft)}
.eyebrow{font-size:12px;font-weight:650;letter-spacing:.2em;text-transform:uppercase;color:var(--teal-hi);margin:0 0 14px}
h1{font-weight:900;letter-spacing:-.035em;line-height:.98;color:var(--bone);font-size:clamp(44px,7vw,88px);margin:0 0 20px;text-wrap:balance}
h1 em{font-style:italic;font-weight:800;color:var(--body)}
h2{font-weight:900;letter-spacing:-.03em;line-height:1.05;color:var(--bone);font-size:clamp(28px,3.6vw,42px);margin:0 0 16px;max-width:22ch;text-wrap:balance}
h3{font-weight:800;color:var(--bone);font-size:18px;letter-spacing:-.01em;margin:0 0 8px}
p{margin:0 0 14px;max-width:68ch}
.lead{font-size:19px;line-height:1.55;color:var(--body);max-width:60ch}
strong{color:var(--bone);font-weight:700}
.hero{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:40px;align-items:start;margin-top:34px}
.shot{border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--ink2);margin:0}
.shot img{display:block;width:100%;height:auto}
.shot figcaption{font-size:12.5px;color:var(--muted);padding:10px 14px;border-top:1px solid var(--line-soft)}
.tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.tile{background:var(--ink2);padding:18px 18px 16px}
.tile .v{font-weight:900;font-size:34px;letter-spacing:-.03em;color:var(--bone);line-height:1;font-variant-numeric:tabular-nums}
.tile .v small{font-size:15px;font-weight:700;color:var(--muted);letter-spacing:0;margin-left:3px}
.tile .l{font-size:12px;font-weight:650;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-top:8px}
.tile.hl .v{color:var(--teal-hi)}
.verdict{margin-top:34px;padding:22px 26px;background:var(--slate);border-radius:10px;border:1px solid var(--line)}
.verdict p{margin:0;font-size:18px;color:var(--bone);max-width:none}
.chartbox{background:var(--ink2);border:1px solid var(--line);border-radius:10px;padding:18px 18px 8px;margin:22px 0 10px;overflow-x:auto}
.chart{display:block;width:100%;height:auto;min-width:560px}
.chart .ax{font-size:11.5px;fill:#7E8A8C;font-family:inherit;font-variant-numeric:tabular-nums}
.chart .lbl{font-size:14px;fill:#EDE9D6;font-weight:600;font-family:inherit}
.chart .val{font-size:14px;fill:#EDE9D6;font-weight:750;font-family:inherit;font-variant-numeric:tabular-nums}
.chart .val.sm{font-size:12.5px;fill:#C9C6B4;font-weight:650}
.chart .ann{font-size:12.5px;fill:#C9C6B4;font-family:inherit}
.chart .annv{font-weight:800;fill:#EDE9D6}
.chart path[data-tip]{transition:opacity .15s}
.chart path[data-tip]:hover{opacity:.78}
.chartbox.narrow .chart{max-width:820px}
h3.sub{margin:44px 0 10px;font-size:21px;max-width:40ch;text-wrap:balance}
.chart .lbl.sm{font-size:13px}
.chart .axv{font-size:12px;fill:#7E8A8C;font-weight:600}
.txs{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:16px 0}
.tx{display:flex;flex-direction:column;gap:7px;color:var(--body);font-size:12.5px;line-height:1.35}
.tx img{width:100%;height:170px;object-fit:cover;object-position:top;border-radius:8px;border:1px solid var(--line);display:block}
.tx span{color:var(--bone);font-weight:600}
.ytrow.six{grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
.ytrow.six .yv{font-size:15px}.ytrow.six .yt-t{font-size:12px}
@media (max-width:900px){.txs,.ytrow.six{grid-template-columns:repeat(2,minmax(0,1fr))}}
.cap{font-size:13.5px;color:var(--muted);max-width:80ch}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--body);margin:0 0 8px}
.legend i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:7px;vertical-align:-1px}
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px}
.two .chartbox{margin:0}
.callout{border-left:2px solid var(--teal-hi);padding:4px 0 4px 18px;margin:22px 0;max-width:72ch}
.callout p{margin:0;color:var(--bone);font-size:17.5px}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-top:22px}
.card{margin:0;background:var(--ink2);border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column}
.card img{display:block;width:100%;aspect-ratio:229/356;object-fit:cover;max-width:100%}
.card figcaption{padding:14px 14px 16px;display:flex;flex-direction:column;gap:6px;flex:1}
.card .num{font-weight:900;font-size:26px;letter-spacing:-.03em;color:var(--bone);line-height:1;font-variant-numeric:tabular-nums}
.card .num span{font-size:13px;font-weight:650;color:var(--muted);letter-spacing:0}
.card .meta{font-size:11.5px;color:var(--muted);letter-spacing:.02em}
.card .ttl{font-size:14px;font-weight:700;color:var(--bone);line-height:1.35}
.card p{font-size:13.5px;line-height:1.5;margin:0;color:var(--body)}
.card .lnk{font-size:12.5px;font-weight:650;margin-top:auto;padding-top:6px}
.minis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:20px 0}
.mini{position:relative;display:block;border-radius:8px;overflow:hidden;border:1px solid var(--line);background:var(--ink2)}
.mini img{display:block;width:100%;aspect-ratio:229/356;object-fit:cover}
.mini span{position:absolute;left:8px;bottom:8px;font-size:13px;font-weight:800;color:var(--bone);background:rgba(14,17,19,.78);padding:2px 8px;border-radius:99px;font-variant-numeric:tabular-nums}
.mini em{position:absolute;left:8px;right:8px;top:8px;font-style:normal;font-size:11px;font-weight:650;color:var(--bone);background:rgba(14,17,19,.78);padding:4px 7px;border-radius:5px;line-height:1.3}
ul.clean{list-style:none;padding:0;margin:0 0 14px;max-width:72ch}
ul.clean li{padding:9px 0 9px 22px;position:relative;border-bottom:1px solid var(--line-soft)}
ul.clean li:before{content:"";position:absolute;left:2px;top:19px;width:8px;height:2px;background:var(--teal-hi)}
.quote{background:var(--slate);border:1px solid var(--line);border-radius:10px;padding:24px 24px 20px;display:flex;flex-direction:column;gap:10px}
.quote .q{font-weight:900;font-size:24px;letter-spacing:-.02em;line-height:1.15;color:var(--bone)}
.quote .s{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--muted)}
.quote .s b{color:var(--teal-hi);font-size:20px;font-weight:900;margin-right:4px;font-variant-numeric:tabular-nums}
.takes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:14px}
.take{border:1px solid var(--line);border-radius:8px;padding:14px 16px;color:var(--bone);font-weight:650;font-size:15.5px;line-height:1.35;background:var(--ink2)}
.take small{display:block;color:var(--muted);font-weight:450;font-size:12.5px;margin-top:6px}
.ytrow{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:20px 0}
.yt{display:flex;flex-direction:column;gap:5px;color:var(--body)}
.yt img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:8px;border:1px solid var(--line);display:block}
.yv{font-weight:900;font-size:19px;color:var(--bone);letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.yv.hot{color:var(--teal-hi)}
.yt-t{font-size:13.5px;font-weight:650;color:var(--bone);line-height:1.35}
.yt-m{font-size:12px;color:var(--muted)}
.strip{margin:16px 0}
.strip img{display:block;width:100%;height:auto;border-radius:8px;border:1px solid var(--line)}
.strip figcaption{font-size:12.5px;color:var(--muted);margin-top:8px}
.funnel{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin-top:22px}
.stage{background:var(--ink2);padding:20px 20px 18px}
.stage .st{font-size:12px;font-weight:650;letter-spacing:.18em;text-transform:uppercase;color:var(--muted)}
.stage h3{margin-top:8px}
.chip{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:3px 10px;border-radius:99px;margin:4px 0 10px;border:1px solid}
.chip.fix{color:#EDE9D6;border-color:#EDE9D6}
.chip.part{color:var(--teal-hi);border-color:var(--teal-hi)}
.chip.ok{color:var(--muted);border-color:var(--line)}
.stage p{font-size:14px;margin:0}
ol.play{counter-reset:p;list-style:none;padding:0;margin:18px 0 0;display:grid;gap:12px}
ol.play li{counter-increment:p;display:grid;grid-template-columns:44px minmax(0,1fr);gap:14px;background:var(--ink2);border:1px solid var(--line);border-radius:10px;padding:18px 20px}
ol.play li:before{content:counter(p);font-weight:900;font-size:26px;color:var(--teal-hi);line-height:1}
ol.play h3{margin-bottom:4px}
ol.play p{margin:0;font-size:15px}
table{border-collapse:collapse;width:100%;font-size:13px}
th{text-align:left;font-size:11px;font-weight:650;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);padding:8px 10px 8px 0;border-bottom:1px solid var(--line)}
td{padding:7px 10px 7px 0;border-bottom:1px solid var(--line-soft);vertical-align:top;color:var(--body)}
td.n{text-align:right;font-variant-numeric:tabular-nums;color:var(--bone)}
th.n{text-align:right}
.tbl{overflow-x:auto;margin-top:14px}
.base td:first-child{color:var(--bone);font-weight:600}
details{margin-top:18px;border:1px solid var(--line);border-radius:10px;padding:0 18px;background:var(--ink2)}
details summary{cursor:pointer;padding:16px 0;font-weight:700;color:var(--bone)}
footer{padding-block:40px 60px;border-top:1px solid var(--line);margin-top:56px;font-size:13px;color:var(--muted)}
footer p{max-width:90ch}
#tip{position:fixed;pointer-events:none;z-index:60;background:#EDE9D6;color:#0E1113;font-size:12.5px;font-weight:600;line-height:1.35;padding:7px 10px;border-radius:6px;max-width:320px;opacity:0;transition:opacity .12s;box-shadow:0 6px 24px rgba(0,0,0,.4)}
@media (max-width:900px){.hero,.two{grid-template-columns:1fr}.cards{grid-template-columns:repeat(2,minmax(0,1fr))}.minis{grid-template-columns:repeat(3,minmax(0,1fr))}.funnel,.ytrow{grid-template-columns:1fr}.takes{grid-template-columns:1fr}}
@media (max-width:480px){.tiles{grid-template-columns:1fr 1fr}.tile .v{font-size:27px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media print{
  @page{size:A4;margin:12mm 11mm;background:#0E1113}
  html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  body{font-size:12.5px;padding-inline:0}
  body:before{display:none}
  section{padding-block:26px 6px;break-inside:auto}
  h1{font-size:54px}h2{font-size:28px}
  .lead{font-size:15px}
  .chartbox,.card,.quote,.funnel,ol.play li,.mini,.yt,.strip,.shot,.verdict,.callout,.takes{break-inside:avoid}
  h2,h3,.eyebrow{break-after:avoid}
  .chart{min-width:0}
  details{border:0;padding:0}
  details summary{padding:0 0 8px}
  #tip{display:none}
}
""".replace('GRAIN', GRAIN)

LENS = ('<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="34" fill="none" stroke="#EDE9D6" stroke-width="7"/>'
        '<path d="M 50 16 A 34 34 0 0 1 79.4 33" fill="none" stroke="#48A0BC" stroke-width="7" stroke-linecap="round"/></svg>')

TIP_JS = """<script>
(function(){
  var tip=document.getElementById('tip');
  document.addEventListener('mousemove',function(ev){
    var t=ev.target.closest&&ev.target.closest('[data-tip]');
    if(!t){tip.style.opacity=0;return;}
    tip.textContent=t.getAttribute('data-tip');
    var x=ev.clientX+14,y=ev.clientY+14,w=tip.offsetWidth,h=tip.offsetHeight;
    if(x+w>innerWidth-8)x=ev.clientX-w-14; if(y+h>innerHeight-8)y=ev.clientY-h-14;
    tip.style.left=x+'px';tip.style.top=y+'px';tip.style.opacity=1;
  });
})();
</script>"""

def bar_path(x, y, w, h, rad=2.0):
    """Bar with rounded data-end (top), square baseline."""
    rad = min(rad, w / 2, h)
    return (f'M{x:.1f},{y+h:.1f}V{y+rad:.1f}Q{x:.1f},{y:.1f} {x+rad:.1f},{y:.1f}'
            f'H{x+w-rad:.1f}Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+rad:.1f}V{y+h:.1f}Z')

def hbar_path(x, y, w, h, rad=3.0):
    """Horizontal bar, rounded at the right (data) end."""
    rad = min(rad, h / 2, w)
    return (f'M{x:.1f},{y:.1f}H{x+w-rad:.1f}Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+rad:.1f}'
            f'V{y+h-rad:.1f}Q{x+w:.1f},{y+h:.1f} {x+w-rad:.1f},{y+h:.1f}H{x:.1f}Z')

