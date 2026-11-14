# Mode: penguin style edit (`penguin`), LOCKED 11 Nov 2026

Eoin, 11 Nov 2026: *"that video is so nice and so perfect. so that style is officially locked in... the one I will be rolling with from now on."*
This is his own 16:9 talking-head edit style, modelled on @longevitypenguin. He'll keep improving it, especially for informational videos.
**It's a base, not a template (Eoin 12 Nov):** "i dont want the style to be the exact same every single time". Keep the
look (white text, word cards, payoffs, slow zooms, quiet sound) but vary the devices per video: the opener, which beats get
payoffs or cards, transitions. Propose the variations in Gate 1. He changes the rules, nobody else.
**Never render without his say-so** (12 Nov): show stills or let him scrub the timeline; renders only when he asks.

Reference build: `jobs/glasgow-bodies` ("the polymaths win", timeline "Eoin · polymaths win v2.9" in the Resolve project
"penguine dit", render `~/Desktop/polymaths win.mp4`). Ref reels and the frame breakdown: `REFERENCE-BREAKDOWN.md` and
`research/penguin-edit-refs/` (DeT0W1GRZSe is the main one).
Everything is built natively in Resolve (Fusion), per the auto-edit hard rules.

## The look (locked)
**Format:** 16:9, 1920x1080, 29.97, about 40s. One seated A-roll angle, his own footage.

**Cut**
- Every pause goes. Pauses are measured against his own speech level (anything 22 dB under the line's p90 for 0.16s
  or more), not as digital silence: room noise and breaths go too.
- Pads: 0.06s before, 0.10s after (soft word endings must not clip). No piece under 6 frames (no stray frames).
- Jump cuts alternate 1.00 / 1.08 zoom. Sentences can sit on a 1.12 punch.
- Verify by rebuilding the cut audio and transcribing it start to end before anyone sees it, then transcribe each
  piece on its own to catch clipped words.

**Opener (the hook)**
1. Video in a video: the first shot starts full frame, **blurred, and sharpens within 1s max**, while a ramped
   (ease-out) zoom-out settles it onto the off-white canvas (#f4f2ee) at **no smaller than 80%** of the frame (12 Nov:
   the old 46% was too small, too fast, not subtle). `inset_blur_zoom()` in the job build2.py.
2. Fast cuts of him doing things, **one beat per word** (12 Nov: "lost / all / momentum" a beat each, let them breathe; was 7 cuts), (working, shooting, lifting, editing, the terminal), 5-6 frames each, one white
   word at a time in the centre with a soft dark glow. **Opener captions are BIG** (11 Nov, after a 77% skip rate on
   the first post: the small centred words didn't land). The hook is what's said and what's seen. **No text hook** in
   this style; the spoken line has to carry a promise or a curiosity gap.
3. His face on the next phrase, with a slow zoom-out that never settles.
4. The payoff cutaway (sunset WIN) with a slow, constant push-in.
5. A 3-frame negative strobe (inverted, normal, inverted) into the body.

**Text**
- **White only, never black and white mixed in one shot.** On his blue wall the captions are white. Black text only on
  a white/off-white card, or a shot he names (IRRELEVANT on the pale beach was black, lead included).
- A-roll captions (12 Nov, Eoin: "more variety than the little white thing top left", bigger, never blocking him): a style
  per line, judged from the refs (`SEG_STYLE` in build2.py):
  `chest` one word centred on his chest (72px, 90 in the hook) · `wall` raised left in the wall space (64px) ·
  `stack` the line so far small on top, the current word big under it (92px) · accent words in **Didot Italic**
  lowercase in the stack slot (like the refs' "framing"). Hard cut on the word, glow only if the contrast check fails.
- Captions run on **every** shot where he's talking, plain cutaways included. Only payoff shots and word cards skip them.
- Payoff on a cutaway: a small lead typed on from the cut (1 char/frame, 40px), then the BIG word (300px or up to ~72%
  of the width; a hero word can go ~92%, like LAYERS) with each letter ghosting in (8f ramp, 2f stagger, gliding from the
  right) starting 4f before it's spoken, **behind him** (DepthMap cut-out, or a luma key for a silhouette against a
  window), then a small tail typed on as he says it. The lead and tail stay inside a 5% margin.
- The last line: the payoff goes behind his head on the A-roll (SCROLLING), white.

**Lists**: word cards OR the word big on its own b-roll (12 Nov: MESSAGES on him typing etc.), cut **on each word** (measured onsets, not Whisper times): black bg + white text,
then white bg + black text, alternating to the end of the list. 150px max, centred. No images, no tilted cards.

**Zooms**
- Every time the edit comes back to him from a cutaway or card: zoom-out 1.22 to 1.00 across the rest of the shot,
  60% ease-out + 40% linear, so it **never fully stops**.
- Cutaways: slow push 1.00 to 1.10 eased (the hook payoff: 1.00 to 1.12 linear).
- A white blow-out (2 white frames, 3 easing back) into the section after the list.

**Sound**
- Quiet little ticks on every caption, word card and payoff word: `assets/tick.wav` (Short foley 14, one 51ms transient,
  -30 dBFS peak). Never the Vintage "Click" (that's the shutter he hates), never whooshes, never impacts.
- A quiet riser audible from frame 1, building through the whole hook into the strobe (Riser 4, compressed, -30 dB peak),
  plus a short flash hit on the strobe (16. FLASH "4E_02 D", -24 dB peak). Nothing else.
- A song bed under the whole thing, pre-levelled about 11 dB under his voice (-37 LUFS when his raw voice is ~-26).
  He picks the song. **Never the Loki track "Purpose Is Glorious"** (trashed, he hates it).
- Resolve won't set clip volume by script: level every SFX/music file before import.

**Grade**: he grades the ungraded/4K plates himself in Resolve. After any rebuild, copy his grade onto every piece of the
same clip (`CopyGrades`), including filler frames.

## Run it
1. Transcribe the A-roll, then pick the ~40s body with him (Gate 1: `PROPOSAL.md` with the cut, words, shots, payoffs).
2. Frame strips at every b-roll's real in/out before building (single thumbnails lie about in-points).
3. New job: `jobs/<job>/`. Copy `modes/penguin/tools/lib.py` to `jobs/<job>/build.py` and `tools/build.py` to
   `jobs/<job>/build2.py`, then set the job constants: SRC, SEGS, OPEN_*, CUTS (payoffs), LIST_WORDS (measured onsets),
   END_PAYOFF, INK_SHOTS, LUMA_SHOTS, BIG. Word timing: per-island Whisper (`words_islands.json`).
4. `python3 build2.py` builds into the OPEN Resolve project as a new timeline version. It seals 1-3 frame holes at the
   end (Resolve rounds 24fps carriers and 25fps clips short).
5. Audit: no V1 gaps, no short A-roll flashes between covers, no caption gaps, no tiny pieces, audio tracks as expected.
6. Check frames mid-motion and settled (`ExportCurrentFrameAsStill`), then a 640x360 review render for Eoin.
7. On his OK: full render (H.264 1080p) and delete the old timeline versions.
