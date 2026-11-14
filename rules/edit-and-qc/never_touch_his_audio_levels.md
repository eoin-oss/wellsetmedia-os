---
name: feedback-never-touch-his-audio-levels
description: once Eoin sets music/voice levels on a timeline, never rebuild it or re-level audio; patch graphics only
---
Once Eoin has set the audio levels on a Resolve timeline (usually the music turned down), never touch them: no full rebuilds that recreate the audio tracks, no re-levelling, no new music bed. Change graphics through single-beat patches only (e.g. `patch_beats.py`). If a fix truly needs a rebuild (a cut), say up front that it resets his levels and ask before doing it.

**Why:** 13 Nov, Kyle case-study reels. Two full Jay rebuilds reset his music level. His words: "i changed the audio levels do not touch them. for the music its lower dont fucking touch it."

**How to apply:** before any Resolve rebuild, check whether he has touched that timeline. Related: feedback-resolve-batch-no-popups, project-auto-editor.
