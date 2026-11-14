# Mode: negative-text reel with motion cards (`negative-text-reel`)

A 9:16 talking-head reel cut with b-roll between lines. The captions are negative: white Inter Bold set to
Difference, so the letters show the video inverted. Key words go big, motion cards rise behind the speaker's head,
and photos get a slow push-in. Approved on Kyle Ritchie's "My story" reel, 19 Oct 2026. The reference job is
`jobs/kyle-story` (`plan.json` + `extras.json`). Every parameter is in `mode.json`. Style: `styles/negative-text`.

## The look
- **Hook:** zoom out on the first words, with the first 2-3 words in big captions (`mode: hook_big`). Cut straight
  into the strongest visual inside the first second.
- **Captions:**
  - 3 words max per line.
  - Key words (`kw` in a segment) go big, with the rest of the line smaller and stacked in reading order: whichever
    part is said first sits on top. Use them every so often, most heavily on the hook.
  - They come in on the original smooth ease-in, just quicker, and are sharp once settled.
  - A line that can't be read in negative (a bright or busy shot) goes solid red via `extras.red`.
- **B-roll:**
  - Never use the same clip twice.
  - The past = the client's old footage. The present = cinematic angles (low angles, profiles, close-ups), never the
    head-on stage shot. Status or purpose lines = photos.
  - Claims and payoff lines stay on the face.
- **Motion cards:** a screenshot (an IG header for a name drop) fades and lifts into place behind the speaker's head
  on the trigger word, with the speaker cut out in front. It never crosses the face. It leaves after the end word.
- **Silences:** pauses of 0.28s or more are cut to a 0.2s breath. Bare joins get the punch-in toggle.
- **Music:** trimmed to its kick-in so it hits on frame one. Never notdavid.

## Run it (one job)
1. `python3 engine/transcribe.py "<aroll>" <job>`, then in `job.json` set style `negative-text`, w 1080, h 1920.
2. `python3 engine/plan_default.py jobs/<job>`. Rechunk to 3 words max, then pick key words and b-roll into
   `plan.json` (index new footage first: `engine/index_broll.py`; conform any 600fps Snapchat/VFR clips to 30fps first).
   `shared_project: true` once the project exists.
3. `python3 modes/negative-text-reel/tools/silences.py <job>` (after the plan, before the build).
4. `python3 engine/build.py jobs/<job>` (or `rebuild.py` after the first build).
5. Post steps, in place, from `extras.json`:
   - `tools/cards.py <job>`
   - `tools/photos.py <job>`
   - `tools/red.py <job>`
6. Check stills (`ExportCurrentFrameAsStill`, wait for DepthMap pieces). **No render until Eoin says it's done.**
7. `tools/deliver.py <job> <name>`, then upload to the client's Frame `edited` folder (delete the old version) and
   put the link in the Notion card's Edited video field. Stage: client review.

## Rules learned building it
- **Once Eoin edits by hand, never rebuild.** Change things in place (caption comps, colours) or snapshot his
  deletions first (`timeline_snapshot.json`), carry them into the plan, and only then rebuild.
- **Comp frames:**
  - Clip comps render on frames 0..n-1 (`COMPN_RenderStart`), not GlobalStart.
  - Wrap frame numbers in brackets in expressions: `time--18` breaks and blacks out the comp.
- **Stills:** stills appended by script ignore their out point and run long, so photos go in as Fusion Loader comps
  on title carriers.
- **Media files:** never overwrite a media file Resolve has imported. It goes offline, and a render on it freezes
  Resolve.
- **Depth cutout:** the ramp is per setup. Kyle's desk set: 0.28-0.30. Check a still of the depth pass once.

**Gates (HARD RULE, 8 Nov):** two approval gates before anything is animated: (1) PROPOSAL.md after the transcript, (2) final-frame stills contact sheet before animation. See the auto-edit SKILL.md.
