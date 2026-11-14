---
name: feedback-all-in-davinci
description: "HARD RULE: every edit, graphic, cutout and caption is built natively in DaVinci Resolve (Fusion/Color/Edit), never rendered locally (Remotion, ffmpeg, python matting)"
metadata:
  type: feedback
---

Everything in an edit is built INSIDE DaVinci Resolve Studio: cuts, punch-ins, captions, motion graphics (Fusion comps:
Text+, shapes, Custom Tool for maths patterns like waves/cymatics, Glow), cutouts (Magic Mask / Fusion), sound design.
Scripts may only DRIVE Resolve (scripting API, writing .comp/.setting files Resolve imports). Never render footage or
graphics outside it: no Remotion/HyperFrames ProRes overlays, no ffmpeg renders, no local python mattes.

**Why:** 18 Oct 2026, resonance lab reel. I started building motion graphics in Remotion and a person matte with
torch locally. He stopped it: "this is all meant to be done in davinci ffs not locally its so much more powerful thats
the whole point this is the 2nd time ... make sure it doesnt happen again." (1st time: Hempton clips, see
[[feedback-find-moments-dont-edit]].) Native = he can open and tweak every piece in Resolve.

**How to apply:** before any build step, ask "does this produce pixels outside Resolve?" If yes, find the Fusion /
Resolve-native way. Analysis outside Resolve (transcripts, word timings, face positions, planning) is fine.
Related: [[project-auto-editor]], [[project-ai-editor-modes]].
