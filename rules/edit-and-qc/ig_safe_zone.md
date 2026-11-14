---
name: feedback-ig-safe-zone
description: "HARD RULE in the auto-editor - every caption, image, title and graphic sits inside the Instagram Reels safe zone"
---

Eoin 23 Oct 2026: "instagram safe zone is a hard rule in the editor". Every mode and builder must keep all text,
images and graphics inside the IG Reels safe zone on 1080x1920: clear of the top 250px (header UI), the bottom 480px
(caption, username, audio row) and the right 140px (like/comment/share rail); left margin 60px.

**Why:** anything under the IG UI is lost on the post; he does not want to catch it by eye on every reel.
**How to apply:** bake the box into each builder as constants and assert placements against it before building
(not a manual check). Applies to every mode in project-ai-editor-modes, incl. the personal yap mode.
