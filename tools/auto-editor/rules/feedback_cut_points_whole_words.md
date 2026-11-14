---
name: feedback-cut-points-whole-words
description: "Talking-head cuts: never clip last words, never cut inside a sentence, always end on the payoff, keep intentional to-camera reels whole, on-screen text never over the face"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ff10e9cb-0203-440a-96b4-ad9df06cb0fd
  modified: 2026-10-17T13:20:19.473Z
---

Eoin's review of the Kyle seminar shorts (2026-10-17):
- Ending words were clipped "a tiny tiny bit too early" (e.g. "control", "wants", "want"). This happens when a cut lands where the next word starts with no gap. Transcript word end-times also run early.
- No cuts between words inside a single sentence unless there's a genuine long pause.
- Every short must end on a finished point. Twice he said "he didn't finish the point".
- A to-camera piece Kyle recorded on purpose (IMG_9313) must be used in full. Strip only the plugs and dead air, never half the reel.
- On-screen text: no huge stacked titles in the middle. Keep it off the face, below it on the opener. Some shots need captions at the bottom only (lighting).
- Flashing frames at the start of some reels were reported. Render CFR, frame-aligned, ProRes for Resolve.

**Why:** clipped words and mid-sentence joins read as amateur, and an unfinished point kills the reel.

**How to apply:** cut only at sentence ends or pauses of 0.35s or more. Pad the tail by measured voice energy, not transcript times; the tool is `kyle-seminar-pulls/edl/cut.py`. Re-transcribe the outputs to verify. Check that the final line is the payoff. Related: [[project-kyle-frame-library]].
