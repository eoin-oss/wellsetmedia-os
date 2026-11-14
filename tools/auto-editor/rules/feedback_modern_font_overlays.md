---
name: feedback-modern-font-overlays
description: "\"The modern font\" = CapCut's Modern.ttf (Oswald Regular), the IG-edits caption face; all text overlays use it with a thin black outline, no gradients"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d734f811-80f4-428d-8043-4de75ac1ae67
  modified: 2026-10-14T16:59:04.984Z
---

When Eoin says "the modern font" he means one specific font: CapCut's **Modern** (`~/Movies/CapCut/User Data/Cache/effect/7517487651092434192/.../Modern.ttf`, which is Oswald Regular inside). It's the font his 10/10 habits captions use (draft `1005 (1)`). A copy lives at `$WSM_HOME/content/overlay-system/edit/books/fonts/Modern.ttf`.

**Why:** on 14 Oct 2026 I tried Garamond, then Tactic Sans, then Inter Black, and each one annoyed him more ("not a modern font. the modern font").

**How to apply:** every text overlay is in Modern, white, with a thin black outline (about 4.5% of font size). No gradient or shade plate, no drop shadow, and no "Part 1 / Part 2" unless he asks for it. Oswald's lines are tall, so space stacked lines by their measured bounding box, never by font size. Related: [[project_overlay_system]].

**Update 18 Oct 2026:** for his own reels' motion graphics and cards, he said "my font is helvetica". Use Helvetica
(Bold for headings) in all Fusion graphics, matching his captions. Saved as `graphics_font` in `styles/eoin/style.json`.
