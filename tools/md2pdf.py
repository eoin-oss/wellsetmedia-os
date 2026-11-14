#!/usr/bin/env python3
"""Any .md -> branded A4 PDF, written beside its .md master.

Usage:  python3 md2pdf.py <file.md> [more.md ...]
The MDs stay the machine masters; the PDFs are Eoin's reading copies.
"""
import sys, os, subprocess, tempfile, re
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Type system locked 2026-09-19 (brand/BRAND.md s4): Tactic Sans Medium display, Helvetica body.
# Rendered by local Chrome, so the locally-installed desktop fonts are used by family name.
# NOTE: the installed OTFs report one family per weight - the family is 'TacticSans-Med',
# not 'Tactic Sans'. Asking for 'Tactic Sans' silently falls back to Helvetica.
# Headless Chrome does not resolve user-installed OTFs by family name, so the display face is
# embedded from the converted TTF (made by tools/otf2ttf.py from ~/Library/Fonts/TacticSans-Med.otf).
FONT_DISPLAY = os.path.join(ROOT, 'client-docs', 'fonts', 'TacticSans-Med.ttf')
DISPLAY = "'TacticMed','Helvetica Neue',Helvetica,sans-serif"
BODY    = "'Helvetica Neue',Helvetica,Arial,sans-serif"
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

CSS = f"""
@font-face{{font-family:'TacticMed';src:url('file://{FONT_DISPLAY}') format('truetype');font-weight:400;font-style:normal}}
@page{{size:A4;margin:16mm 15mm 18mm}}
*{{box-sizing:border-box}}
body{{font-family:{BODY};font-weight:400;font-size:9.6pt;line-height:1.55;
  color:#14181A;background:#F4F1E8;margin:0;padding:2mm 0}}
.mark{{display:flex;align-items:center;gap:6pt;font-family:{DISPLAY};font-weight:400;font-size:10pt;letter-spacing:.02em;
  padding-bottom:6pt;border-bottom:.6pt solid #C9C4B4;margin-bottom:12pt}}
h1{{font-family:{DISPLAY};font-weight:400;font-size:17pt;letter-spacing:-.01em;line-height:1.1;margin:0 0 8pt}}
h2{{font-family:{DISPLAY};font-weight:400;font-size:12pt;letter-spacing:-.005em;margin:14pt 0 5pt;color:#14181A}}
h3{{font-family:{BODY};font-weight:700;font-size:10.3pt;margin:10pt 0 3pt}}
p{{margin:0 0 6pt}}
a{{color:#1D5D70;text-decoration:none}}
strong{{font-weight:700}}
ul,ol{{margin:0 0 7pt;padding-left:14pt}}
li{{margin-bottom:2.5pt}}
li input[type=checkbox]{{margin-right:4pt}}
code{{font-family:Menlo,monospace;font-size:8.4pt;background:#EAE6D9;padding:.5pt 3pt;border-radius:2pt}}
pre{{background:#EAE6D9;padding:6pt 8pt;border-radius:4pt;overflow:hidden}}
table{{border-collapse:collapse;width:100%;margin:0 0 8pt;font-size:8.8pt}}
th{{text-align:left;font-weight:700;color:#1D5D70;border-bottom:1pt solid #C9C4B4;padding:3pt 6pt 3pt 0}}
td{{border-bottom:.5pt solid #DDD8C8;padding:3pt 6pt 3pt 0;vertical-align:top}}
hr{{border:0;border-top:.6pt solid #C9C4B4;margin:11pt 0}}
img{{display:block;max-width:78%;height:auto;margin:8pt auto 3pt;border:.5pt solid #C9C4B4;page-break-inside:avoid}}
img + em, p > img:first-child + em{{display:block;text-align:center;font-size:8.2pt;color:#6B7578}}
blockquote{{margin:0 0 7pt;padding:4pt 10pt;border-left:2pt solid #1D5D70;color:#4A5356}}
em{{font-style:italic}}
h2,h3{{page-break-after:avoid}}
.script{{background:#FFFFFF;color:#000;font-family:{BODY};font-size:11pt;line-height:1.6;padding:10pt 13pt;margin:4pt 0 8pt;page-break-inside:avoid}}
.script p{{margin:0}} .script p.gap{{height:8pt}}
table,blockquote,pre{{page-break-inside:avoid}}
"""

LENS = ('<svg style="width:12pt;height:12pt" viewBox="0 0 100 100">'
        '<circle cx="50" cy="50" r="34" fill="none" stroke="#14181A" stroke-width="7"/>'
        '<path d="M 50 16 A 34 34 0 0 1 79.4 33" fill="none" stroke="#1D5D70" '
        'stroke-width="7" stroke-linecap="round"/></svg>')

def _inline_images(html, md_path):
    """The HTML renders from a temp file, so relative src paths would break.
    Resolve them against the markdown's own directory and embed as data URIs."""
    import base64, mimetypes, re as _re
    base = os.path.dirname(os.path.abspath(md_path))

    def repl(m):
        src = m.group(1)
        if src.startswith(('data:', 'http://', 'https://')):
            return m.group(0)
        path = src if os.path.isabs(src) else os.path.join(base, src)
        if not os.path.exists(path):
            print(f'     ! image not found: {src}')
            return m.group(0)
        mime = mimetypes.guess_type(path)[0] or 'image/png'
        data = base64.b64encode(open(path, 'rb').read()).decode()
        return f'src="data:{mime};base64,{data}"'

    return _re.sub(r'src="([^"]+)"', repl, html)


def convert(md_path):
    src = open(md_path).read()
    # checkbox lists render as real boxes
    src = src.replace('- [ ]', '- ☐').replace('- [x]', '- ☑')
    body = markdown.markdown(src, extensions=['tables', 'fenced_code', 'sane_lists'])
    body = _inline_images(body, md_path)
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div class="mark">{LENS}WellSetMedia</div>{body}</body></html>')
    # pdf sits beside its md master
    out_pdf = os.path.splitext(os.path.abspath(md_path))[0] + '.pdf'
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
        f.write(html); tmp = f.name
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={out_pdf}', tmp],
                   capture_output=True, timeout=60)
    os.unlink(tmp)
    ok = os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 1000
    print(('ok   ' if ok else 'FAIL ') + out_pdf)
    return ok

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    sys.exit(0 if all([convert(p) for p in sys.argv[1:]]) else 1)
