---
name: project-auto-editor
description: "The Resolve Studio auto-editor (built 2026-10-16): cut engine, b-roll library index, Motion Text Pro captions, learning loop — /auto-edit skill"
metadata:
  type: project
---

Built 2026-10-16 via /mission after Eoin bought Resolve Studio 21.1.1. Home `$WSM_HOME/tools/auto-editor/`
(engine/, styles/eoin/, index/, jobs/), skill `/auto-edit`. 
Builds INTO Resolve so he finishes there.

**Scope he set:** final takes only, any sound anomaly cut, other speakers dropped, intentional b-roll ("a random
filler shot loses retention" — paramount), his Motion Text Pro captions. Motion graphics (diagrams popping up behind
him, from a reference VSL) = phase 2. Grade = his PowerGrade already contains the CST; auto WB/exposure goes in a node
BEFORE it — needs his PowerGrade .drx with an empty first node (not built yet). Shoots on A6700 S-Log3.

**His style, measured from his edits (First 100 = `post the first videp`, `perception`):** captions are a Text+ with
StyledTextFollower word-rise (Helvetica Bold 0.08, blur+glow), 2-6 word phrases; over b-roll centred zoom 1.0; over
A-roll zoom 0.73 tilt -290; short punch beats stacked left (pan ~-515) on V3-V5. B-roll on V2 cut exactly on caption
phrase boundaries, ~36% of runtime, literal or "embodied" matches, A-roll on hook/claims/CTA.

**What works (verified):** captions placed by script = append MTP "Smooth Word Up" carrier (24fps, duration converts)
+ ImportFusionComp his exported comp; whisper.cpp `-dtw small.en` word times land within ~0.1-0.2s of his hand
placements; Resolve `TranscribeAudio(True)`/`GetTranscription()` gives words + speakers (async: poll); cutter turned a
5-min messy Alex Nolan session into a clean 41s Alex-only monologue. LoadProject on the already-open project returns None.

**Library reality:** 1,259 clips indexed + Opus-labelled, but curated broll/ folders are tiny (~60 clips); 984 are NYC
trip clips, ~half flat/duplicates. He said he "might need a better b-roll system" — that's the next build.
Related: [[project_resolve_auto_edit]], [[reference_resolve_scripting_assets_bin]].

**Kyle seminar run (16 Oct): 20 clips, project "Kyle Seminar Clips".** He flagged captions going off the edge.
Root cause: a Text+ title draws on its own W-wide canvas BEFORE the timeline zoom, so long lines clip at the canvas
edge and shrinking the clip can't fix it. Fit by FONT size in the comp (`Size` input, calibrated ~116px/em at 0.08 on
1920) to 86% width, side stacks to their half. Also: scripted Fusion comps on plain clips don't render (intro zoom =
2-frame slices with stepped ZoomX/Y); whisper `--prompt` glossary can collapse DTW timings (auto-check + rerun without);
render MarkIn/MarkOut leaves marks on the timeline that nesting honours; Kyle's mics are one-sided (SetAudioMapping
[ch,ch]); he said no vertical phone b-roll, SSD footage only.

**17 Oct Kyle v2 lessons:**
- Flashing bug = 2-frame intro slices on 29.97 sources in a 25fps timeline (Resolve rounded each to 1 frame, leaving black gaps). Now same-fps sources use exact 1-frame slices; other fps use a pre-rendered ffmpeg zoom. A re-encoded intro can be read with a different Input Color Space (Project vs Rec.709 Scene), which shows as a brightness jump, so avoid re-encoding when the fps matches.
- Eoin's caption rule for Kyle: hooks small and under his face, all captions in the lower third (side stacks and centred captions over b-roll retired in styles/kyle). Comps are written as UTF-8 (a £ crashed the build).
- Final set: 14 reels in jobs/kyle-final; 05 11 13 16 17 20 are binned.

**18 Oct:**
- Kyle seminar delivered as v5. 12 reels in 9:16 with the headline in the top bar (`engine/vertical.py`, headlines in `jobs/kyle-v5-9x16/headlines.tsv`), plus 07 in 16:9. Old Frame files were deleted and the Notion card links swapped.
- Kyle's Notion is a separate workspace that the Notion MCP can't see. It's driven through Chrome with the internal `/api/v3/saveTransactionsFanout` endpoint, sending the `x-notion-active-user-header` and `x-notion-space-id` headers. Block text edits work. Database URL-property edits failed with ValidationError, so those were typed in the UI instead.
- Storage: `engine/cleanup.py` works from `jobs/RETENTION.json`, which sorts each batch into drafts, until_posted and keep. Every deletion is logged to `jobs/CLEANUP-LOG.md`. When the Kyle batch is all posted, run `cleanup.py posted kyle-seminar-oct` (36GB).
- `styles/eoin` now carries every Kyle-round rule. The lab log is `styles/eoin/LAB.md`.

**19 Oct, resonance lab (native Fusion motion graphics):** `engine/fusion.py` writes .comp files (Text+, masks, Custom Tool,
SoftGlow, keyed splines) placed on Motion Text Pro title carriers; job in `jobs/resonance/` (`gfx.py` scenes, `build_fx.py`
steps, `timemap.py` silence cuts). Cutout of him = Fusion **DepthMap** (Faster) + Custom Tool alpha ramp 0.13-0.17 (mic and desk
stay in front; no strokes needed, unlike Magic Mask). Checks = `engine/stills.py` (Deliver JPEG stills, no popups).
- Custom Tool: trig in DEGREES, `exp()` broken, no `pow()` (use `^`), and `-(a)^2` parses as `(-a)^2`: write `1/2.71828^(..)`.
  It's per-pixel CPU: run each one only on its own box at reduced res (`region()`), or playback/render takes hours.
- RectangleMask Height is relative to frame HEIGHT (width to width); EllipseMask both to width. Background colours must
  be premultiplied (rgb*a). Text+ CharacterSpacing 1.5 is huge; ~1.05-1.1 is subtle tracking. Helvetica has no arrow glyph.
- Crashes (Fusion DiskCacheManager segfault): deleting/replacing Fusion clips and background auto render cache racing
  comp imports. Build = fresh timeline, append-only, on the Media page, `perfAutoRenderCacheEnable/FuEffect` off during it;
  `ensure_resolve()` relaunches + reopens the project if it dies. Audio import once hit a Resolve heap-corruption crash.
- **v5 verdict (19 Oct): "way better... really great".** Open notes for the next pass: riser before "frequencies" a bit loud;
  hook feels slow (his own slow delivery), so add a brain hologram rising + rotating on his left that morphs into the planet on
  "the most fundamental part", zoom into the globe, then reveal the frequency, to keep it flowing.
- **The workflow he wants kept:** I propose a full list of edits/graphics, he approves/trims, then I go all in on the build.
- **Later (not now):** same system in other styles, e.g. less crazy, more techy + minimal, still super clean. Style presets per mode.
- **GOAL (19 Oct): lock a consistent personal-brand mode (`modes/eoin-pb/`) so his own content runs on autopilot.** Resonance v5
  is the starting look. Needs: reusable parameterised graphic templates (not bespoke gfx.py per reel), cutout cached once not
  live, one-pass render without chunking, flow = drop footage > proposal > his approve > build > render. Not started.

**19 Oct, Kyle story reel draft:** job `jobs/kyle-story` (style `styles/kyle-story` = eoin + `hook_big` caption mode, zoom 2.4), project "kyle-story auto", render `jobs/kyle-story/render/kyle-story v1.mp4`. Source + Snapchat b-roll on SSD `wellsetmedia/kyle-story-reel/`. Snapchat 600fps VFR clips must be conformed to 30fps (`broll/cfr`) before indexing. `compile.py` now renders at the project's timeline resolution (was hard-coded 1920x1080). Never overwrite a media file Resolve already has imported: it goes offline and a render on it freezes Resolve (happened on the 19 recut; force-quit needed).
- 19 Oct story-reel lessons: clip Fusion comps render on frames 0..n-1 (`COMPN_RenderStart`), NOT `COMPN_GlobalStart` (that was silently breaking the face push-in in build.py, now fixed). Stills appended by script ignore their out point and run long: place photos as Loader comps on title carriers (`jobs/kyle-story/photos.py`). Card-behind-head = Loader+Merge+DepthMap cutout inside the A-roll piece comp (`jobs/kyle-story/huberman.py`, depth ramp 0.27-0.32 for Kyle's desk set). Negative captions = white Text+ (value 1.35) + item CompositeMode 3 (Difference); `kw` in plan = key words big, rest small, stacked in reading order; max 3 words a line.
- **19 Oct: Kallaway format v1** (`styles/kallaway/BREAKDOWN.md`, job `jobs/themvsus/`): vertical 1080x1920 split layout
  (graphics top, rounded A-roll window bottom, DepthMap cutout head breaking out above it), drifting grid bg, one-word
  captions, cues snapped to the music's beats (`beats.py`, 180db from 8s, 129 BPM). Timeline "them vs us kallaway v2".
  Vertical gotchas: Text+ size = px / (1450*1080/1920); clip Fusion comps can output a 1080x1920 canvas fine; connect
  masks with `tool.EffectMask = mask.Mask` (not .Output).
- **Kallaway format APPROVED 19 Oct ("fucking amazing")**: keep `jobs/themvsus` as the template for this style. Music
  = background only: sit it ~15 LU under the voice (voice -23.7 LUFS -> bed ~-39). Bug to fix in build.py: A-roll audio
  lands on A2 so the music append to A2 silently failed (Eoin added it by hand on A6); put the voice on A1.

**21 Oct speed lesson (Kyle sidecap v2):** a long Resolve session with thousands of MTP titles bogged it down to ~10 min per clip (CPU idle, waiting on Resolve). After a Resolve restart the same builds took 7-19s per clip. Each fresh title still costs ~1s the first time its Fusion comp is touched. Caption rows are now appended once per track (one AppendToTimeline list). If builds crawl, ask him to restart Resolve before blaming the code.
