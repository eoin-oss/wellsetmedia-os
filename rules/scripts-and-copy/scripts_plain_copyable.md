---
name: feedback-scripts-plain-copyable
description: "Scripts inside any client doc/PDF go in plain copyable blocks — just text, nothing around it — so they can be copied from a screenshot"
---

**Every script in a client-facing doc (Kyle's VIRAL-FORMATS-GUIDE and anything like it) is a plain
text block.** Black text on white, one line per item, title as the first line, CTA as a plain
`CTA: …` line. No bold, italics, quote marks, tables or callouts inside the block. B-roll, notes and
warnings sit OUTSIDE the block as small text. Images and the format/framing sections stay as they are.

**Why:** Eoin (6 Oct 2026) — the scripts get copied out of screenshots (Live Text / OCR); styling and
tables around the words make that messy. "make sure future versions are like this."

**How to apply:** in the .md, wrap each script in `<div class="script">` with one `<p>` per line
(`<p class="gap"></p>` for a blank line). `tools/md2pdf.py` carries the `.script` style. Regenerate
over the same filename (feedback_update_docs_in_place). Related: project_morelife_kyle_cd.
