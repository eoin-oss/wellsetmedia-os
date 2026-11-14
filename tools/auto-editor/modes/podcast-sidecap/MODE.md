# Mode: podcast clips, design "sidecap" (`podcast-sidecap`)

One **design** of the podcast-clips family. It shares the prep and cut engine (`engine/podprep.py`) with
`hempton-podcast` (the 9:16 face-locked design); only the look differs. More designs will follow, each in its own mode
folder. First use: Kyle Ritchie clips from his episode of The James Hempton Show (21 Oct 2026, job
`jobs/kyle-podcast-hempton`). Look reference: the two interview reels Eoin sent (frames pulled into
the session scratchpad, not kept).

## What a finished clip looks like
- **Picture:** 4:5 (1080x1350) crop of the 16:9 episode. The person on screen sits off-centre, so the captions get
  the open side: Kyle (frame-left, black top) at 30%, James (frame-right, white polo) at 70%. Framing is static per
  shot (no per-frame face lock). It opens on Eoin's Smooth Zoom out, and a 1.12 punch hides jump cuts.
  The person on screen is decided **per frame** from torso brightness, because the shot detector misses some of
  the multicam cuts.
- **Hook:** a strong line lifted from later in the clip opens it, then it cuts back to where the thought starts
  (`why = hook first` in clips.tsv). The hook's caption rows are 1.3x bigger.
- **Delivery is 9:16 (21 Oct):** the 4:5 cut sits at its own size (1080x1350) low in a 1080x1920 frame, black above
  and below. The text hook goes in the 400px band above it for the whole clip: caps (Helvetica Neue Bold Italic) /
  script link words (Playfair Display Italic) / BIG caps, Motion Text Pro titles on Hook 1-3, staggered 0.24s. Copy
  lives in the job's `text-hooks.tsv` (id, top, mid, big). Nesting the 4:5 timeline does NOT work (Resolve renders a
  nested timeline as 16:9), so the 4:5 timeline is rendered to a ProRes master first.
  **Hook look changed 21 Oct:** plain static caption, solid white, all caps, RODE Noto Sans CJK SC B, centred, last
  line 44px above the picture; breaks hand-set in `text-hooks.tsv` `line` (| = break). Build: `engine/podhook916_plain.py
  jobs/<job> jobs/<job>/text-hooks.tsv` after podwrap916. Delete MTP titles one at a time (bulk delete crashed Resolve).
- **Kyle: no swearing.** `engine/deswear.py <job>` cuts swears out of clip.json (picture + audio + caption) before the
  build; per-clip phrase cuts and keeps go in the job's `deswear.json`.
- **Captions:** every row is a native **Motion Text Pro** title. Only the font is changed (Helvetica Oblique, payoff row
  in Playfair Display Italic) and the template's own Black Shadow element is switched on. Text goes on the
  StyledTextFollower, and Font/Style/Size go on the Template Text+.
  - **Blocks:** a block is up to 7 words, broken on sentence ends, pauses over 0.4s, the hook cut, and any change of
    who's on screen.
  - **Rows:** each block is 1-3 rows, built top-down: medium / small / BIG.
  - **Entrances:** rows come in left -> up -> right (mirrored right -> up -> left beside James). The last row is the
    payoff, in big script when it's 2 words / 14 chars or less, else big oblique sans.
  - **Placement:** the column sits beside the head, starting about eye level. It's left-aligned right of Kyle and
    right-aligned left of James.
- **B-roll:** 2-3 cutaways per clip (picture only, the voice carries on). Each one sits exactly on a caption block
  (1.4-3.4s), after the hook, at least 6s apart, and never in the last 3s. Captions over b-roll sit in a left column
  at 42% height. The library is in `broll-library.tsv`: the walk-outs, the street group, Kyle with the Porsche, the
  dark-wood dinner and the seminar room. The per-clip picks are in the episode's `broll-kyle.tsv`.
- **Music:** one bed per clip on A2, from the measured kick-in, faded over 0.8s. Interstellar (Hans Zimmer, added
  21 Oct) goes on the deep or aspirational clips and enters at 20s where it starts to build. Never notdavid.

## Tracks
V1 picture, V2 b-roll, V3-V5 caption rows 1-3, A1 dialogue, A2 music.

## Run
1. `python3 engine/podprep.py <episode> clients/<client>/<ep>/clips-<who>.tsv jobs/<job>`
2. Write `broll-<who>.tsv` (id, keys from the library) and `music-<who>.tsv` (id, file, start, gain_db).
3. `AE_MODE=podcast-sidecap python3 engine/podbuild_sidecap.py jobs/<job> <broll.tsv> <music.tsv> [ids]`, which builds
   into the OPEN project. If the project has no timeline yet, it sets 25fps 1080x1350 first.
4. `python3 engine/deswear.py jobs/<job>` (Kyle), then build. 9:16: `engine/render_tls.py jobs/<job>/master-4x5 mov ProRes422HQ " v3"`,
   then `engine/podwrap916.py jobs/<job> jobs/<job>/text-hooks.tsv jobs/<job>/master-4x5` (makes `<id> <slug> 9x16`).
5. Check with `engine/stills.py` at 1080x1350. A frame caught mid-slide shows words bunched together; that's the
   animation, not a spacing bug.

`engine/rmtl.py "<name prefix>"` deletes timelines safely (it switches away from the open one first).

## Calibration
Text+ Size x 757 = rendered em px on a 1080-wide canvas (measured with Helvetica Oblique "really the" at
0.0932 -> 287px). Item Pan/Tilt move the row centre in timeline px (Tilt up is positive).

## James Hempton variant (24 Oct 2026, job `jobs/james-podcast-hempton`, Resolve project "james podcast clips")
Same episode, clips for James's account. Same 4:5 build + 9:16 wrap as Kyle's delivered (safe) batch, with these changes:
- **Hook: gold, one line, fast in.** `engine/podhook916_gold.py` (run after podwrap916, `AE_PREFIX=j`): RODE Noto Sans CJK
  SC B caps in #E8B84A, no gradient or shadow, same spot as the plain hook (last line 44px above the picture, band 250-478).
  ONE line, always: the tsv `line` column may never hold "|", nothing wraps, em 84 shrinks to fit 940px and refuses
  under 64 (shorten the copy). Entrance: fade + scale 0.92 -> 1 over 5 frames keyed on the Text+ (Size, Alpha1 AND
  Red1/Green1/Blue1; Text+ colour is premultiplied, so alpha alone still shows on black), then holds. Copy: 3-6 words,
  from what James says. `text-hooks.tsv` = id, line.
- **No b-roll** (James's clips aren't done with it): pass a header-only b-roll tsv.
- **Who's talking is decided by voice**: `engine/podspeakers.py <job> <voices.json>` trains a 2-speaker voice model
  from single-speaker windows (in the job's `voices.json`) and writes `spk` per word into clip.json. The builder keeps it,
  so captions only show over whoever is actually talking, whichever camera is up. Needed because James's clips are
  back-and-forth; the Kyle job used hand-listed `james-lines.json` instead.
- **Job overrides** in `jobs/<job>/job.json` (the Kyle job has none, so it builds as before): `caption_drop_px` 190
  (= Kyle's 22 Oct caplower pass, which Resolve reads back as Tilt -270) and narrower columns (Kyle 410, James 490) so
  rows stay inside the IG safe zone.
- Globs: `podwrap916.py` / `podhook916_plain.py` take `AE_PREFIX` (default k). `podprep.py` fix: the filler/pause scan
  now covers min..max source time (it crashed when a hook lifted from LATER in the episode ended after the last segment).
- QC after render: a few blocks touched a beard when he leaned into the column (j01, j10, j13): those blocks were
  lowered under the chin in the 4:5 timeline and the clips re-rendered.
Run: podprep -> podspeakers -> `podbuild_sidecap <job> broll-none.tsv music-james.tsv` -> render_tls masters ->
`AE_PREFIX=j podwrap916` -> `AE_PREFIX=j podhook916_gold` -> `render_tls <job>/render-9x16 mp4 H264 " 9x16"`.
- Revision 25 Oct: `podhook916_gold.py` now clears every hook key after the 5-frame entrance and asserts that the
  size and colour hold to the end. A retexted title had kept a stale Size key at frame 40, so the hook drifted in size
  mid-clip. An optional `em` column in text-hooks.tsv caps the size where the PIL estimate runs narrow (j02: the
  estimate said 935px, the render measured 972px). Apostrophes are allowed in hooks.
- deswear caveat: it cuts on whisper's word edges, and those can leave a syllable behind. On j08 the cut left the
  "-cking" of "fucking" in, which a re-transcribe of the render heard as "off". Re-transcribe every deswear'd render
  and widen the cut to the real silence on either side if anything is left.
- QC pass 27 Oct (SOP 12): deswear's whisper word edges were off by 1-5 frames on Kyle's clips, so 5 delivered clips
  (k17 k18 k22 k23 k24) still had a "fu-"/"sh-" fragment either side of the cut. Fix by source frame, not word time:
  rebuild the clip's voice from the episode audio (no music), test candidate frame cuts with whisper medium.en at
  temperature 0, with AND without an "uncensored" prompt (whisper medium writes "f***ing", so a plain regex misses it),
  then apply the frames to clip.json (`qc27-src-cuts.json`). small.en also hallucinates swears into silence: confirm
  any hit with medium before cutting. Fix builds get `AE_SUFFIX=" v3 qc27"` / `AE_TL_SUFFIX=" qc27"` so the delivered
  timelines stay. Loudness: the API has clip gain but no limiter, so a batch goes onto ONE timeline with per-clip gain,
  one Limiter on its Fairlight main bus (by hand), then `engine/render_items.py` renders each item to its own file.

**Gates (HARD RULE, 8 Nov):** two approval gates before anything is animated: (1) PROPOSAL.md after the transcript, (2) final-frame stills contact sheet before animation. See the auto-edit SKILL.md.
