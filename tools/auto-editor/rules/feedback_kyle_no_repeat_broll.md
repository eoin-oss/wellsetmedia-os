---
name: feedback_kyle_no_repeat_broll
description: "HARD RULE: the same b-roll clip never appears twice in one reel; builders stop on a repeat"
metadata:
  type: feedback
---

A b-roll source clip is used at most once per reel, even at a different in-point.

**Why:** Eoin, 10 Nov 2026, on reel 04 (trader recap): the trader call clip C8229 sat twice back to back at 1.4-4.4s. "the same b roll clip is there twice that can never happen again." He pulled 04 off Frame/Notion to fix it.

**How to apply:** `engine/no_repeat_broll.py` (`assert_unique` on the shot list, `check_timeline` on a built timeline) is wired into `jobs/kyle-batch/broll.py` and `jobs/kyle-03-whoami/build.py`; wire it into every new builder. Run `check_timeline` before any render. Applies to all clients. See [[feedback_kyle_broll_relevance]].
