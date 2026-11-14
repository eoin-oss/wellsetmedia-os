# eoin-yap — Eoin's personal yap reels (template, 23 Oct 2026)

Talking head shot on his phone, music already on the take. Reference: coachkyle "Big Boy Maxxing" (instagram.com/p/Detc9GNqITZ), breakdown frames in `reference/yap-ref/`.

## Look (locked by Eoin 23 Oct)
- **Image card above his head** (x 70-1010, y 252-604), one image per beat, hard cut on the beat's first word. Some sentences are 1 beat, some 2.
- **No text on the images.** Eoin: the keyword-on-image idea was cut. The images carry the visual, the captions carry the words.
- **Captions just under the image** (y 646): Helvetica Bold, white, thin black outline, 2-4 words, no box, never over the face.
- **Title card on the open**: 3-image strip + the viral soft Helvetica: Bold, tracking 0.9 (letters nearly touch), slight blur (0.3) + Soft Glow (gain 0.18, size 3) + faint blurred shadow (`soft_text`). Bracket subtitle gets the same soft treatment in a slightly red orange (0.95, 0.45, 0.13), tracking 0.98 so the small words keep their spaces. Fusion Blur units are big: 1.6 turned it to mush. `retitle.py <take>` swaps the title on an existing timeline in place.
- Palette: white + orange (teal/olive kept as hints only, keep it basic).
- Take pushed 1.04 and shifted down so the card clears his cap. Audio untouched.
- **IG safe zone is a hard rule**: top 250, bottom 1440, left 60, right 1020 (940 below y 1000). Asserted in code.
- Images: compelling, current, literal to what he's saying (e.g. "something different" = Nathaniel POV sax crowd, "our generation" = Dublin rent queue).

## Run
1. Transcribe: whisper-cli (see build notes) into `jobs/yap-<take>/words.json` + `meta.json` (`{"dur": seconds}`).
2. Beat map in `beats.py` (cue word + occurrence -> image key). `python3 build_yap.py plan <take>` prints it, touches nothing.
3. Images: `python3 fetch.py key="search query"` pulls Bing candidates into `jobs/yap-assets/cand/` + numbered sheets; copy the pick to `jobs/yap-assets/cards/<key>.jpg`.
4. Open the Resolve project, then `python3 build_yap.py <take> [take...]`. New timeline every run (`Yap a v3 · ...`), never deletes.
5. Check stills with `engine/grab.py`. **Don't render until Eoin has reviewed.**

## Never again (crashed Resolve twice on 23 Oct)
- Two Fusion nodes with the same name -> a merge feeds itself -> Resolve hangs at 100% CPU on import. `check_comp()` now refuses any comp with duplicate names or bad links before Resolve sees it.
- The MTP carrier is 24fps: on a 30fps timeline spans scale x1.25. `place()` converts; the image track chains each card to the last card's real end so there are no gap frames.
- The script never deletes timelines (deleting crashes Resolve).

## Readability gate (HARD RULE, 23 Oct)
- `build_yap.py` runs `pre_check()` before touching Resolve: title strip images must be dark enough where the title sits.
- After a build it writes `jobs/yap-<take>/text_manifest.json`; run `python3 ../../engine/readable.py ../../jobs/yap-a/text_manifest.json` and get all-readable before handover.
- Captions and the bracket subtitle carry a soft dark `halo()` (fat blurred black copy). Without it his light wall gave captions ~2:1 and the orange brackets ~1.1.
- `retitle.py` / `recap.py` re-apply title / caption comps onto an existing timeline in place.

**Gates (HARD RULE, 8 Nov):** two approval gates before anything is animated: (1) PROPOSAL.md after the transcript, (2) final-frame stills contact sheet before animation. See the auto-edit SKILL.md.
