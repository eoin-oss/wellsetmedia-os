---
name: feedback-text-readable
description: HARD RULE in the auto-editor - every piece of on-screen text must be readable in every video, checked automatically by engine/readable.py
metadata:
  type: feedback
---

Eoin 23 Oct 2026 (after a white beach image sat under a white title): "always make sure to verify text is readable in all videos, this is a hard rule for the editor". He wants it baked in for when he productises the editor ("this stuff makes it a smart AI editor").

**Why:** he shouldn't be the one catching unreadable text; the editor has to check itself.
**How to apply:** every mode uses `auto-editor/engine/readable.py`: pre-build `zone_ok` on any image under text, post-build `readable.py <manifest>` measures contrast at every title/caption from Resolve stills (min 3.0). Report all-readable before handover. Fixes: darker image, or soft dark `halo()` behind text. On 23 Oct the gate found captions at ~2:1 on his light wall and orange brackets at ~1.1 that looked "fine" by eye. Related: [[feedback-ig-safe-zone]], [[project-eoin-yap-mode]].
