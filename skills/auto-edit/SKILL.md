---
name: auto-edit
description: Auto-edit talking-head videos into DaVinci Resolve Studio in Eoin's (or a client's) style — final takes only, sound anomalies + other speakers cut, intentional b-roll matched line by line from the indexed library, Motion Text Pro captions, then learns from his finishing pass. Use when Eoin says "/auto-edit", "edit this reel", "edit the batch", "cut this footage", "put b-roll and captions on this", or drops A-roll to edit.
---

# Auto-edit

**HARD RULE: everything is built natively in Resolve.** Cuts, captions, motion graphics (Fusion: Text+, shapes, Custom
Tool maths, Glow), cutouts (Magic Mask) and sound design. Scripts only drive Resolve. Never render pixels outside it:
no Remotion, HyperFrames, ffmpeg or local python mattes. Analysis outside Resolve (transcripts, timings, planning) is fine.

**HARD RULE: impact SFX sit back.** Booms/hits, whooshes and flashes go 4 dB under the 19 Oct levels, in every style:
whooshes about -19 dB, booms/hits/stamps about -13 to -15 dB at the peak, flashes about -16 dB. Pops and clicks stay
where they are. They support the edit and never jump out over his voice.

**HARD RULE: show what he's pointing at.** Whenever he points at something ("here is…", "look at this", "this reel",
"this guy", or names a person, brand, post, tool, site, stat or study), the edit shows the real thing on the
word: a pulled image, a screenshot, the actual reel or post, the site, the chart. This applies in every style and
mode. In the proposal, list each one with its line, what will be shown and where it comes from. Fetch them after his
go (yt-dlp, a Chrome screenshot, the web) into `jobs/<job>/assets/`, then build them natively in Resolve, framed in
the style (a phone/UI frame, a card or a cutout). If the source is missing or unclear, ask. Never fake it with a
generic shape or a lookalike.

**HARD RULE: every piece of text is readable, and the editor proves it.** Every mode runs `engine/readable.py`:
(1) before building, any image that text sits on is measured where the text lands (`zone_ok`) and the build stops
naming the image if it's too bright; (2) after building, the builder writes a text manifest (time, box, colour of
every title/caption/label) and `python3 engine/readable.py <manifest.json>` pulls a Resolve still at each one and
measures the contrast between the letters and what's right around them (min 3.0, WCAG large text). Nothing is handed
over until it reports all readable. Fix with a darker image or a soft dark halo behind the text (`halo()` in
modes/eoin-yap/build_yap.py), never by hoping. Light walls and orange text are the usual failures.

**HARD RULE: Instagram safe zone.** All text and graphics inside top 250 / bottom 1440 / left 60 / right 1020
(940 below y 1000) on 1080x1920, asserted in the builder.

**HARD RULE: two approval gates, every job, every mode (Eoin, 8 Nov).** Nothing goes into the edit unapproved.
- **Gate 1, proposed edit (right after the transcript).** Before any plan or build, write `jobs/<job>/PROPOSAL.md`:
  per video, the cut (in/out per line, what's dropped and why: swears, stumbles, names, promises), the text hook,
  the hook line, every caption beat, every b-roll pick and every graphic/"show what he points at" item with its line,
  plus flags (rules, consent). Short and scannable. Give him the path and stop. He edits or says go.
- **Gate 2, final stills before animation.** Every graphic, title, card and caption style is built first at its
  END state only (settled frame, no keyframes), then `engine/stills.py` renders those frames (via Deliver, no Fusion
  popups) into one contact sheet at `jobs/<job>/stills/`. Run the readable + text-box checks on them. Give him the
  path and stop. Animation is built only after he approves, and it must land exactly on the approved still: re-render
  the settle frame and compare; any difference is a fail.

**Never crash Resolve.** Validate every Fusion comp before import (no repeated node names, no self-links:
`check_comp` in modes/eoin-yap/build_yap.py). Never delete timelines from a script: new version or edit in place.

Home: `$WSM_HOME/tools/auto-editor/` (engine/, styles/, index/, jobs/).
Needs Resolve Studio open with Preferences > System > General > External scripting = **Local**.
Never touch his own Resolve projects: every build is a NEW project named `<job> auto`. Restore his open project after any
script that switches projects (`New Project 1` or whatever was open).

## The flow (one job per video)

1. **Set up the job**
   - Already-cut A-roll (studio reels): `python3 engine/transcribe.py "<aroll>" <job>` (whisper.cpp + DTW, glossary from style).
   - Raw footage: create `jobs/<job>/job.json` {aroll, style, fps, w, h}, then
     `python3 engine/resolve_words.py "zz autoedit lab" "<raw>" jobs/<job>/words_raw.json` (Resolve's transcription,
     speaker detection), then the cut engine:
     - with a script: `python3 engine/cutter.py jobs/<job> --script jobs/<job>/script.txt`
     - no script: `python3 engine/cutter.py jobs/<job>` -> read `takes.json`, pick takes per `TAKES.md` into
       `takes_keep.json`, then `python3 engine/cutter.py jobs/<job> --keep jobs/<job>/takes_keep.json`
     - Eoin's own footage: add `--motion` (tic-safe cut points). Read `cut_report.md` and sanity-check the final script.
2. **Plan** (the judgment step): `python3 engine/plan_default.py jobs/<job>` then `python3 engine/catalog.py jobs/<job>`.
   Spawn an **Opus** subagent with `PLANNER.md`, the job folder, the style's `style.json` + `LEARNED.md`, and any shot
   list. It writes `plan.json`. Then `python3 engine/qa.py jobs/<job>` must pass (fix FAILs, judge warns).
3. **GATE 1, proposed edit (STOP)**: write `PROPOSAL.md` from the cut + plan (see the hard rule), and run
   `python3 engine/review.py jobs/<job>` for the line-by-line `review.html`. Give Eoin both paths (don't open them).
   He swaps lines ("line 7 alt 1", "line 9 A-roll") or edits the proposal. Apply, re-run qa + review. Go on only on his go.
4. **Build static**: `python3 engine/build.py jobs/<job>` -> Resolve project `<job> auto` with cuts, b-roll and every
   graphic/caption at its final settled frame, no animation.
5. **GATE 2, final stills (STOP)**: `engine/stills.py` -> contact sheet in `jobs/<job>/stills/`, readable + text-box
   checks pass. Give Eoin the path. He approves or lists fixes; fix and re-render the stills until he says go.
6. **Animate**: build the motion into each approved still (last keyframe = approved values). Re-render the settle
   frames and compare to the approved stills. Verify with `python3 engine/grab.py jobs/<job>/grabs <sec...>`.
   Report what's left for him.
7. **Learn**: after he finishes the edit in Resolve, `python3 engine/learn.py jobs/<job>` -> corrections.jsonl + LEARNED.md.

## Modes (per format, per person)
Each format/person combo is a mode in `modes/<name>/` (`mode.json` = every parameter, `MODE.md` = the look + how to
run it). Read the mode's MODE.md before working in it, and never change its settled rules without Eoin.
- `penguin` (**LOCKED 11 Nov, Eoin's own default style**): 16:9 @longevitypenguin-style talking head. Relative-level silence cut, video-in-video opener + rapid cuts, white one-word captions, payoff words behind him (DepthMap/luma), black/white word cards for lists, never-stopping zoom-outs on every return, quiet ticks + frame-1 riser + flash only. Reference: `jobs/glasgow-bodies`. Read `modes/penguin/MODE.md` first.
- `negative-text-reel`: 9:16 talking-head story/teaching reels. Negative captions (white Inter Bold, Difference), 3 words max, key words big, b-roll between lines, motion cards behind the head (cards.py), photo push-ins (photos.py), silences cut (silences.py), red for unreadable lines. Reference: `jobs/kyle-story`. Read `modes/negative-text-reel/MODE.md` first.
- `kallaway-split`: vertical action-packed motion-graphics reels (Kallaway look), approved 19 Oct; reference build `jobs/themvsus`.
- `hempton-podcast`: James Hempton podcast clips. 9:16, face-locked, no b-roll, question hook + yellow text hook,
  fast captions, per-clip music. Flow: clips.tsv -> `engine/podprep.py` -> `engine/podbuild.py` (builds into the
  OPEN project, one timeline per clip).

## Library
`index/clips.jsonl` (metadata + thumbs) and `index/labels*.jsonl` (vision labels). New footage:
`python3 engine/index_broll.py "<folder>"` -> `python3 engine/sheets.py` -> label new sheets with Opus subagents per
`index/LABELING.md` (one labels_<x>.jsonl per agent).

## Styles
`styles/<name>/style.json` (phrases, caption modes, b-roll rules), `captions/base.comp` (his Motion Text Pro Text+),
`reference/` (dumps of his finished edits), `LEARNED.md`. A client = copy `styles/eoin`, then override.

## Known limits
- Title carriers are 24fps; durations land within 2 frames short (never overlapping).
- B-roll share and choices are only as good as the library labels: a line with no confident match stays on A-roll.
- Grade is not applied by the builder yet (studio reels are pre-graded).
