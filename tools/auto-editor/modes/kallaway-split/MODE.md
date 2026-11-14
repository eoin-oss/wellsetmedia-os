# Mode: Kallaway split (`kallaway-split`)

Vertical talking-head reels with action-packed motion graphics, after Kallaway. Approved by Eoin on 19 Oct 2026 on
"them vs us" ("damn good, I can't believe it, amazing"). Every parameter is in `mode.json`. The reference build is
`jobs/themvsus/` (`gfx.py` scenes, `build.py` steps, `beats.py` music grid), and the style breakdown is in
`styles/kallaway/BREAKDOWN.md`.

## What a finished reel looks like
- **Split layout:** graphics fill the top 1000px. His wide shot sits in a rounded window across the bottom, cropped so
  the window's top edge cuts his forehead. A DepthMap cutout of him (head, chair, mic arm) breaks out above the window.
- **Close-ups:** go full-screen for 2-4s every 8-12s on asides and emphatic lines. These have no stage graphics, just
  one big slam word if the line earns it (CULT-LIKE / *Following*).
- **Ground:** near-black, a 120px grid drifting slowly down-right, and a dim red bloom behind the stage.
- **Titles:** line 1 in Helvetica Bold, line 2 in big Didot Italic in red. Words rise in on the word he says, and the
  block flicks up and out when the idea changes.
- **One cast for the whole reel:** the same objects (crowds, cards, a phone) persist and regroup into each new idea.
  Moves are speed ramps (quintic, 6-8 frames, motion blur), builds pop on a spring, and something changes every
  0.5-1.5s.
- **Show what he's pointing at:** any "here is…", "look at this" or named post, person or tool puts the real thing
  on the stage on that word, in a phone/UI frame or card that fits the cast (see the HARD RULE in the auto-edit skill).
- **On the music:** every cue snaps to the nearest beat or hit of the bed (within 0.2s).
- **Captions:** one word at a time, uppercase Helvetica Bold with a dark halo, sitting just above the head break-out.
  Key words are set in Didot Italic.
- **Audio:** the bed sits 15 LU under his voice, SFX go on every move, and nothing rings past the last frame.

## Run steps (new reel)
1. Copy `jobs/themvsus/` to `jobs/<reel>/`. Set `SRC`, `END`, `CU` and the face/crop numbers in `build.py` (grab a
   gridded frame to read face x and head top), then run `engine/transcribe.py`.
2. Set `SONG` and the offset in `beats.py`, then run it to get `beats.json`.
3. Propose the graphic chain line by line (one cast that evolves) and get Eoin's go.
4. Write the scenes in `gfx.py`: `section(S, E)`, `put()` for moves, `people()`, `card()`, `pill()`, `bar()` and
   `title()`, with cues through `snap()` + `cue()`.
5. Run `TVU_TL="<name>" python3 build.py all`, then `build.py stills`. Check every box and every word in the stills.
6. Run `python3 render_review.py` (720p) for his review, then `python3 render_review.py full` for the final. Delete
   the review file afterwards.

## Gotchas
- Text+ size is `px / (1450*1080/1920)` at this frame size.
- Connect masks with `tool.EffectMask = mask.Mask`.
- The voice goes on A1 as its own audio-only append. A linked append puts it on A2 and blocks the music.
- Build into a fresh timeline every time (append-only), on the Media page, with background render cache off.

**Gates (HARD RULE, 8 Nov):** two approval gates before anything is animated: (1) PROPOSAL.md after the transcript, (2) final-frame stills contact sheet before animation. See the auto-edit SKILL.md.
