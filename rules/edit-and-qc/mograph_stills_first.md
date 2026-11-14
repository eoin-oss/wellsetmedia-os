---
name: feedback-mograph-stills-first
description: AI editor has two approval gates on every job - a proposed edit after the transcript, then final-frame stills before anything is animated
---

Every AI-editor job, every mode, has two STOP gates (stills-first from 31 Oct, made a hard rule with gate 1 on 8 Nov 2026):
1. **Gate 1, proposed edit right after the transcript:** `jobs/<job>/PROPOSAL.md` (cut in/outs and what's dropped, text hook, captions, b-roll, graphics, flags) + review.html. Eoin edits or says go.
2. Build every graphic at its END state only (settled frame, no animation).
3. **Gate 2, final stills:** `engine/stills.py` contact sheet (via Deliver, no Fusion popups), readable + text-box checks. Eoin approves or fixes. Nothing animated before that.
4. Animate INTO each approved still (last keyframe = approved values); re-render the settle frame and compare, any difference is a fail.

**Why:** "i want propsoed edits after the transcripts and i want the final stills generated before they get animated always so i can review and approve them before they go into the edit." Design gets judged on cheap stills and a text proposal, which kills the re-render loops (podcast batch 5-6 renders, seminar shorts 6+).

**How to apply:** written into `~/.claude/skills/auto-edit/SKILL.md` (hard rule + flow steps 3-6) and every `modes/*/MODE.md`. Still all native in Resolve/Fusion (feedback-all-in-davinci); text-box check (feedback-check-text-boxes) runs at gate 2. Separate from feedback-find-moments-dont-edit.
