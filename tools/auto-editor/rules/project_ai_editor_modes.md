---
name: project-ai-editor-modes
description: "Eoin's AI editor runs on MODES, one per format x person (e.g. hempton-podcast); each lives in auto-editor/modes/<name>/"
metadata:
  node_type: memory
  type: project
  originSessionId: 3f41a642-93f1-43f9-b91b-c6eb7d7d16e4
  modified: 2026-10-18T15:57:27.713Z
---

18 Oct 2026: Eoin said his AI editor system will have "different modes per format and per person". The first one he
locked was **`hempton-podcast`** (James Hempton podcast clips); the second, `kyle-seminar` (18 Oct), is the Kyle seminar shorts (`modes/kyle-seminar/`). Hempton is saved at
`$WSM_HOME/tools/auto-editor/modes/hempton-podcast/` (`mode.json` holds every parameter, which
`engine/podbuild.py` reads via `AE_MODE`; `MODE.md` has the look and the run steps). It's listed in the `/auto-edit`
skill under "Modes".

**Why:** he wants a reusable per-client, per-format profile instead of re-explaining a look every time.
**How to apply:** when he approves a look for a new person or format, save it as a new mode folder, never as edits to
an existing one. Before working in a mode, read its MODE.md. A mode's settled rules don't change without him.
Related: [[project-hempton-galligan-clips]], [[project-auto-editor]].

- **`negative-text-reel`** (19 Oct 2026, from Kyle's 'My story' reel): negative Difference captions in Inter Bold, 3 words max, key words big, motion cards behind the head, photo push-ins, silences cut. `modes/negative-text-reel/` (MODE.md + tools/), style `styles/negative-text`, reference job `jobs/kyle-story`. Eoin: 'somewhat standard', a profile to reuse.
- **kallaway-split** (19 Oct, approved "damn good, amazing"): vertical action-packed motion graphics; mode.json + MODE.md in modes/kallaway-split, reference build jobs/themvsus.

- **Podcast clips is a FAMILY of designs** (Eoin 21 Oct: "think of this as a version of the podcast clips, there will be more designs later"). Shared prep/cut engine `engine/podprep.py`; each design = its own mode + builder. `hempton-podcast` = 9:16 face-lock design. **`podcast-sidecap`** (21 Oct, Kyle x James Hempton episode, job `jobs/kyle-podcast-hempton`): 4:5 crop, speaker off-centre, captions stacked beside the head as native Motion Text Pro titles (font swapped only: Helvetica Oblique + Playfair Italic payoff, rows enter left/up/right), seminar/dinner/street b-roll cutaways, builder `engine/podbuild_sidecap.py`. Eoin's rule: captions always MTP pack titles inside Resolve, just change the font.

- **`evil-framework`** (21 Oct 2026, Kyle's Tristan-style framework reels): `modes/evil-framework/build_evil.py <take>` builds into the CURRENT project. V1 raw take in zoom pieces (1.0 hook/titles, 1.1 base, 1.3 cards-off punch-in), V2 held B&W card pairs at hand height (Fusion Loader->BrightnessContrast->masked Merge), V3 hook top card + blue (DO NOT USE FOR EVIL) tag + step titles, V4 grey-then-white word write-on captions, 2-4 words. All text Avenir Next with a thin black outline; tag RED (Eoin 21 Oct). Music = Tristan's two IG licensed tracks: Every Living Breathing Moment (Gabriel Piano, on SSD editiing assets/music) and L'Amour Toujours Organs Slowed (Charbo, Eoin to source); voice +4 dB, bed -23 dB. Deleting the current timeline via API crashes Resolve: switch timeline first, delete one at a time. Card timings in `clients/kyle-ritchie/content/evil-overlays/breakdown/data.py`, images in `cards.py` + `jobs/evil-assets/cards/`. Breakdown page: https://claude.ai/artifact/TLcjDU18baGmWkF2kcEsrT
