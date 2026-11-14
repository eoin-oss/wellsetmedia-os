# Planner brief: lines -> b-roll + caption mode

You turn a transcribed talking-head video into `plan.json`. This is the judgment step: every b-roll shot must be
INTENTIONAL. A random or loosely related shot loses retention. A missing shot never does.

## Inputs (in the job folder)
- `words.json`: every spoken word with start/end seconds (index = position in the list).
- `phrases.json`: a draft split into caption phrases (each has its words; you may re-split or merge).
- `catalog.txt`: the usable b-roll library, one clip per line:
  `id | folder | dur | emotion(+emotion2)/energy | people | light/mood | what's on screen | lines it could serve | tags`.
  Emotion is from a fixed set (index/LABELING.md): lonely, reflective, pressure, grind, power, calm, connection, joy,
  momentum, awe, neutral.
- `shotlist.md` (optional): the pre-production shot list. A shot listed against a line WINS over anything else.
- `../../styles/<style>/style.json`: the creator's measured style.

## Rules (from Eoin's own edits: First 100, Glasgow, Burn the boats, Perception)
1. **Phrase = caption = edit unit.** 2-6 words, 0.6-2.5s. Cuts land on phrase starts. Never split a name or a number.
2. **A-roll stays on screen for:** the hook (first line), "I" claims and opinions, rhetorical questions to camera,
   the direct ask / CTA, and the last line. Viewers need his face when he's claiming or asking.
3. **B-roll goes on lines that name or describe something:** a person, place, object, action, a story beat, an
   example. Target share = style.broll.target_share of runtime (Eoin ~36%, story pieces up to ~55%).
4. **Match order (strict):**
   a. the planned shot from shotlist.md;
   b. **literal**: the exact person/place/object/action in the line ("Kyle" -> Kyle; "seminar" -> the seminar room;
      "smoking cigarettes" -> someone smoking);
   c. **embodied**: a movement that acts the line out ("trying to take" -> walking away from camera; "turn back" ->
      looking back over the shoulder; "pay me back" -> golden-hour payoff; "putting in the work" -> hands editing);
   d. **emotional**: when the line is a feeling or a story beat rather than a thing ("I felt completely alone",
      "nobody knew what was going on in my head", "that's when it clicked", "I was done"), name the line's emotion from
      the fixed set FIRST, then pick a clip whose emotion (or emotion2) matches and whose energy matches the delivery
      (quiet confession = low, hype = high). Same person beats anyone: in a client's video use that client's footage
      (people field) before stock or other people's. Write the emotion in the `why` ("emotional: lonely, low").
   e. **nothing confident -> stay on A-roll** (mode over_aroll). Never fill with a vaguely nice shot.
   Story arc: a before -> after story should move the emotion with it (lonely/pressure in the before, grind in the
   process, power/calm/connection in the after). Don't put a power shot under a low point or a lonely shot under a win.
5. **Story coherence:** in a story section prefer clips from ONE trip/shoot folder so the world stays consistent.
   Don't jump Glasgow -> NYC -> beach inside one story unless the line does.
6. **Never:** the same clip twice; clips flagged ungraded/flat, blurry, test shot, talking-to-camera, text-on-screen;
   client footage unless the line is about client work; a clip shorter than its segment.
6b. **Kyle Ritchie (More Life) only:** no materialism. Never a shot whose point is the car, a brand or wealth (Porsche
   badge/headlight beauty shots, stepping out of the car as a flex, designer shop windows, anything tagged
   `materialism-borderline`). Driving POV / interior for `momentum` is fine. Old phone footage tagged `archival` is
   for "who I was" story beats only.
7. **Rhythm:** don't run more than 4 b-roll phrases in a row without returning to A-roll; don't leave more than
   ~8s of A-roll in a b-roll-heavy section without a cutaway or a stack caption beat.
8. **Caption modes:** `over_broll` (centred, full size) whenever there's b-roll; `over_aroll` (lower third) otherwise;
   `stack` for a short punchy beat of <=3 words (a rhetorical question and its answer, "nobody else", "right now").
   Caption text = what he said, cleaned: drop filler (um, like, you know), keep his words, light punctuation,
   no full stops except where a sentence lands hard. Lowercase except names/"I".
9. **Write a `why` for every shot** in plain words: which rule and what in the line it serves. If you can't write a
   specific why, there is no shot.

## Output: plan.json
{ "project": "<job> auto", "timeline": "<job> v1", "style": "eoin", "fps": 25, "w": 1920, "h": 1080,
  "aroll": "<path>",
  "segments": [ {"words": [i0, i1], "caption": "text", "mode": "over_broll|over_aroll|stack",
                 "broll": {"id": "<clip id>", "in": <optional source second>, "why": "...",
                           "alts": ["<id>", "<id>"]} | null } ] }
Segments must cover every word exactly once, in order. `alts` = the next 1-2 best clips (for the review sheet).
