---
name: project-overlay-system
description: "The 10/10 habits overlay generator — Kyle/Morelife set + Eoin's own separate set (--set eoin); transparent PNGs, b-roll banks, /overlay-system skill"
metadata:
  node_type: memory
  type: project
  originSessionId: 69f73d9c-3970-4946-8649-6b55fb03bb9d
  modified: 2026-10-06T10:36:12.086Z
---

**Built 5–6 Oct 2026 for Kyle Ritchie / Morelife.** Since 6 Oct it also runs **Eoin's own set** — `videos_eoin.py`, `b-roll/eoin/`, `output/eoin/`, run `python3 generate.py --set eoin E1`. Never mix the brands' folders.

Generates transparent 1080×1920 PNG overlays for the 10/10 habits viral format — a 3×2 cover grid
plus eight numbered item slides. Invoke with **`/overlay-system`**.

**Home:** `$WSM_HOME/content/overlay-system/` · generator `tools/overlay.py` ·
SOP `sops/reference/overlay-system.md` · Desktop shortcut "Overlay system".

**One command per video:** `python3 generate.py 01`. Scripts live in `videos.py`, b-roll in
`b-roll/<slug>/`, output in `output/<slug>/`.

**Why it exists: consistency, not speed.** The trial variants get outsourced, and a generator means
an editor physically cannot put the text wrong. That's what makes the outsourcing condition on the
Middle and Creative Direction pricing tiers hold.

**Type size was wrong twice before it was measured off a real screenshot.** 52px title, 42px items,
stroke 11% of font size, text block 36.5%–52% so the face stays clear. **Never eyeball it** — if a
new format appears, screenshot a real one and measure text width against frame width.

**Six b-roll registers, not interchangeable**, 165 images pulled from Pinterest. **No flex imagery
in any of them** — restraint reads as wealth, supercars read as hustle, and the brand is framed as
God's work. Bin anything brighter than mean 165; Pinterest injects sponsored picture-frame mockups.

**Eoin's set (6 Oct):** 7 videos locked item-by-item with him and generated — E1 on camera, E2 camera confidence, E3 forbidden level of creativity, E4 aligned, E5 opportunities, E6 impossible to ignore, E7 work feel expensive. He rejected: ruthlessly consistent, storytelling, quietly dangerous at 20. He rewrites most of my items — pitch, then let him swap in his own lines.

**Morelife status:** 01 money · 02 present · 03 flow · 05 confident all generated. 04 abundant and
06 motivated have b-roll but no items written yet.

**Next, discussed not built:** auto-editing via Resolve's own Python API (v20.2.1 installed, no MCP
needed) — whisper transcribe → silence cut → overlays placed on word timings → music ducked.

Related: [[project_morelife_kyle_cd]], [[feedback_creative_output_is_his]].
