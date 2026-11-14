# Mode: James Hempton podcast clips (`hempton-podcast`)

9:16 shorts cut from a multicam episode of The James Hempton Show. Only cuts and captions, with no b-roll.
Eoin approved it on 18 Oct 2026 (clip 01 of the James Galligan episode). Every parameter is in `mode.json`, and
`engine/podbuild.py` reads it (`AE_MODE=hempton-podcast`, the default).

## What a finished clip looks like
- **Picture:** a 1080x1920 crop with a face lock that holds whoever is speaking dead centre, keyed every 3 frames.
  It opens with Eoin's Smooth Zoom out (1.278 to 1 over 23 frames, motion blur).
- **Cuts:** whole words only, starting on the voice and ending on the payoff. Ums, ahs and dead pauses over 0.5s
  come out, and each cut inside one shot is hidden with a 112% punch-in toggle.
- **Ending:** the picture holds 15 frames past the last word. The voice stops before the other mic comes in, and the
  music carries the end.
- **Hook:** the clip opens on the question (James's, or the guest's when James leads). It's built as a stack:
  - The yellow text hook (black SF Pro Display Bold, rounded box) sits directly under the speaker's chin.
  - The question sits under it in Motion Text Pro rows: Smooth Word Down, Line Left, then Blur Up slide (big).
  - The rows land at frames 3, 8 and 13.
  - All of it clears exactly on the cut to the answer.
  - Clips with no question get the text hook alone for 3s.
- **Captions:** max 3 words, fast blur-in-and-up (`fast.comp`), lower third, inside a 760px safe width, never
  before the cut.
- **Music:** one bed per clip from the Kyle pool (never notdavid, never the same track back to back). Each bed starts
  where it kicks in and is level-matched to -31.8 LUFS, with a 0.8s fade.

## Running a new episode
1. Transcribe it and pick the moments: about 30, skip the intro, mostly the guest plus about 6 James-led ones, and
   no ad reads. Write `clients/<client>/<episode>/clips.tsv` with text anchors. A clip that opens on a question gets
   a why starting `James asks first` or `Galligan asks first (n)`, where n is the number of segments the question
   spans. Use the FULL question, never trimmed.
2. Write `hooks.tsv` (one curiosity line per clip) and `music.tsv` (track, measured kick-in, gain to -31.8 LUFS).
3. Bring the moments to Eoin before building.
4. Prep (analysis only, safe any time): `python3 engine/podprep.py <source> <clips.tsv> jobs/<job> [ids]`
5. Build into the open Resolve project: `python3 engine/podbuild.py jobs/<job> [ids]`. Nothing else may touch
   Resolve while this runs.

## Hard rules Eoin set
- **Never cut the hook question short.** Use the full question with enough context to stand on its own. Long
  questions wrap onto more lines; they're never trimmed.
- No flash of another camera after the hook: hold the question shot under the answer's first words.
- The first answer caption must exist: captions never span the hook cut.
- Never change the hook when he asks to change the body captions.
- Nothing from the hook may overlap the cut to the answer.
- The ending can never cut short.
- These clips get no b-roll ("that's not how these are done, this is for James Hempton").
- Never pick notdavid tracks.

The episode paths in `podbuild.py` (`MUSIC_TSV`, `HOOKS_TSV`) point at the Galligan episode. A new episode
changes those two lines.

**Gates (HARD RULE, 8 Nov):** two approval gates before anything is animated: (1) PROPOSAL.md after the transcript, (2) final-frame stills contact sheet before animation. See the auto-edit SKILL.md.
