---
name: project-penguin-caption-system
description: 7 Nov 2026 - Kyle test reel in Jack Mason (@longevitypenguin) caption style, 16:9, built natively in Resolve; builder + spec + Resolve gotchas
metadata:
  type: project
---
Eoin wants the @longevitypenguin caption look "elite tier" for Kyle, and **16:9, not vertical** (his call, 7 Nov). Spec: `clients/kyle-ritchie/glasgow/PENGUIN-CAPTION-BREAKDOWN.md`. Builder: `tools/auto-editor/jobs/kyle-lagging/build_elite.py` (hand-directed beats in PAYOFFS / BARS / CAPS lists; `reattach` re-does the V3 text comps in place). Resolve project "test", timeline "Kyle · lagging indicator ELITE v2".

Look: payoff behind the head in Helvetica Neue Bold caps with a per-letter ghost reveal (8f ease-in, glide); Playfair Display Italic lead-ins typed on; chest captions in white Helvetica Neue Bold caps, face-tracked; b-roll gets white bars that wipe in with near-black words; 4-frame invert strobe between beats. Kyle's palette: gold #d4ad6e on dark plates, near-black on light walls.

**Why:** his first reaction to generic captions was "the captions are ass". The fonts and animations have to match the reference exactly.
**How to apply / gotchas:**
- Live Fusion API edits on Edit-page clips don't show until the MediaOut input is re-wired (`refresh()`). Stills grabbed before that lie.
- DepthMap mattes grab near walls. Gate the cutout with a face-tracked rectangle mask.
- Leads must dodge the tracked head.
- Clip Volume can't be set via the API, so set music by hand.
- Face tracking: mediapipe tasks + `tools/auto-editor/models/blaze_face_short_range.tflite` (`mp.solutions` is gone).
Related: [[project_morelife_kyle_cd]], [[feedback_all_in_davinci]].

**Eoin review 7 Nov (ELITE v2):** KEEP the word-per-clip montage (one new b-roll clip per word: assumptions/actions/behaviours/decisions) and the ending titles (RESULTS behind head). BIN the white box bars over b-roll text ("shite"). Most text animation reads as not properly animated, so it needs real motion and not just fades. He's shooting a lot more b-roll first, so a rebuild waits for that. Payoff words should come from Kyle's ICP problems: resistance, loneliness, taking action.
