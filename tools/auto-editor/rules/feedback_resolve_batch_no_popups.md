---
name: feedback-resolve-batch-no-popups
description: "Resolve builds: batch-load the whole timeline in one script run; never preview via Fusion comp.Render (it pops a 'render completed' dialog he has to click, and blocks the API)"
metadata:
  type: feedback
---

Build the whole timeline (all graphics, captions, audio) in ONE batch script run, then verify with a single Deliver
render (background, no modal) and fix in another batch. Never render preview frames with Fusion `comp.Render` +
Saver: each one pops a "Render completed" OK dialog in Resolve, and while it's up every API call returns None
(CreateEmptyTimeline, DeleteClips, GetCurrentPage all fail).

**Why:** 18 Oct 2026, resonance lab: "its because i have to press ok on this render completed popup. stop that
happening. also this is taking really long why cant u batch load the timeline? I want the most efficient method."

**How to apply:** write every comp first, place them all in one pass, one Deliver proxy render to check, iterate in
batches. If API calls start returning None, a modal is up: tell him, don't retry blindly.
Related: [[feedback-all-in-davinci]], [[project-auto-editor]].
