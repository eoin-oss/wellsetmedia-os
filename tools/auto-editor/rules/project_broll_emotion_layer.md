---
name: broll-emotion-layer
description: "9 Nov: the auto-editor b-roll library has an emotion layer (fixed 11-emotion set), the emotion index and Kyle's materialism flag"
metadata:
  node_type: memory
  type: project
  originSessionId: 926b4361-1e59-48b2-819b-dfbd08d8a622
  modified: 2026-11-09T12:14:39.177Z
---

9 Nov 2026: Eoin asked for the AI editor to "super easily choose the right shots".

**What's built:**
- **Emotion fields:** every usable clip (844) carries `emotion`, `emotion2`, `energy` and `tags`. The fixed set is lonely, reflective, pressure, grind, power, calm, connection, joy, momentum, awe and neutral. The spec is in `tools/auto-editor/index/LABELING.md`.
- **Where the tags live:**
  - Clips labelled earlier got theirs in `index/emotions_*.jsonl`; catalog.py merges them in.
  - New clips carry the fields in their own labels.
- **Catalog line:** `id | folder | dur | emotion/energy | people | light/mood | desc | lines | tags`.
- **Planner:**
  - PLANNER.md rule 4d is the emotional match (a feeling line is matched to the clip's emotion and energy, the same person first).
  - The story arc moves emotion from before to after.
  - Rule 6b covers Kyle's no-materialism rule. The catalog auto-tags `materialism-borderline` (Porsche, Lambo, first class, penthouse, designer shops, money).
- **Index:** `engine/emotion_index.py` writes `index/EMOTION-INDEX.md`, with every clip grouped by emotion, then shoot.
- **Kyle's Glasgow b-roll:**
  - Indexed and labelled in `labels_glasgow_nov*.jsonl`.
  - The SSD `glasgow november/b roll/emotion` folder holds the 3 blue window shots.

**Why:** Eoin wants shot choice to land on the feeling, not just the literal noun.

**How to apply:** after any new shoot, run the following, then regenerate the index:
1. `index_broll.py <folder>`
2. `sheets.py`
3. Label against LABELING.md, including the emotion layer.

Related: [[project_auto_editor]], [[feedback_kyle_no_materialism]].
