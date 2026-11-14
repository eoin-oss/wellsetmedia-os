---
name: feedback-overlay-images-semantic
description: "10/10 habits overlay images must show what the line says, in a moody film / soft halation look; never sharp product shots"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 69f73d9c-3970-4946-8649-6b55fb03bb9d
  modified: 2026-10-07T10:23:11.420Z
---

Every item image in the 10/10 habits overlays has to **match the line being said** (semantic): feet
for "feel your feet", a seated still figure for "meditate", one cup for "focus on one object".
Look: **moody film, old halation-style images** (warm glow, grain, soft light). **Never sharp
product shots** ("not sharp images of a watch. thats bad"). Eoin, 7 Oct 2026: "some of the images
you have been using are super irrelevant to the words being said."

**Why:** the brightness-sorted auto-assignment in generate.py put images next to lines they had
nothing to do with.

**How to apply:** pick one image per item by eye and set `"images": [...]` on the video in
videos.py / videos_eoin.py (generate.py uses it when present). Pull only what the bank lacks. He
said there's no need to search for "halation" as a keyword. Just know the look. Related:
[[project_overlay_system]].
