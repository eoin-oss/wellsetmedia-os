# Mode: Kyle Ritchie seminar shorts (`kyle-seminar`)

These are 30-45s storytelling shorts cut from Kyle's Glasgow stage seminar and delivered as 9:16 with a text hook
header. Eoin approved them across his 17 Oct review, the 9:16 header pass and the 07 music swap on 18 Oct. Every
parameter is in `mode.json`. The tools are in `tools/`, and the final cut lists (EDLs) are in `edl/`.

## What a finished reel looks like
- **Story:** it opens on the hook line and runs hook, context, conflict, turn, payoff, then echo. It always ends on
  the finished point. If he hasn't finished the point, it isn't a reel.
- **Cuts:** only at a full stop or a pause of 0.35s or more, so there are no joins mid-sentence. The last word is
  never clipped: the tail is padded by measured voice energy, not by transcript times.
- **Picture:** the 16:9 stage shot is centred in a 1080x1920 frame with black bars, and the original edits stay
  untouched.
- **Header:** the hook text sits in the top bar in white Helvetica Bold, wrapped one sentence per line, with no lone
  last word. It sits 60px above the picture and stays up for the whole reel.
- **Text:** it never covers Kyle's face. On some shots the lighting means captions go at the bottom only (12).
- **Music:** never notdavid. The bed is trimmed to its kick-in so it hits on frame one, then level-matched by LUFS.
- **Audio:** the voice runs at about -14 dB RMS on both channels.
- **Caption CTA:** every IG caption opens with: Comment "IDENTITY" and I'll send you a free resource breaking it
  down.

## Run steps
1. Mine the moments with `clients/kyle-ritchie/frame/SEMINAR-MOMENTS.md`, then pull ranges using `tools/pull.sh`.
   It reconnects on a dropped connection and checks the duration afterwards.
2. Get word timings with `tools/align.py` (openai-whisper).
3. Cut with `tools/cut.py <IDs>`, using the spec in `edl/<ID>.spec.json`. Fix every warning until it reports
   zero.
4. Render with `tools/render3.py` (ProRes HQ, constant frame rate), then check with `tools/verify3.py` and a
   re-transcribe.
5. Finish (captions and b-roll) in Resolve, project "Kyle Seminar Clips".
6. Build the vertical versions in Resolve, project "Kyle Seminar 9x16 Hooks": V1 holds the reel and V2 holds
   `tools/header.py "<hook>" hdr.png hook.mov <dur>`.
7. Upload to Frame (`edited` folder), delete the old version there, then paste the link into the Notion card's
   "Edited video" field.

## Where things are
- **Final 16:9:** `auto-editor/jobs/kyle-final/`
- **Final 9:16:** `auto-editor/jobs/kyle-final-9x16/` (12 reels; 07 stays 16:9 with no header)
- **Raw, pulls and ProRes cuts:** SSD `wellsetmedia/kyle-seminar-pulls/`
- **Edit sheet:** `clients/kyle-ritchie/frame/SEMINAR-SHORTS.md`, with a copy in `EDIT-SHEET-v2.md`
- **Hooks:** `tools/hooks.tsv`

**Gates (HARD RULE, 8 Nov):** two approval gates before anything is animated: (1) PROPOSAL.md after the transcript, (2) final-frame stills contact sheet before animation. See the auto-edit SKILL.md.
