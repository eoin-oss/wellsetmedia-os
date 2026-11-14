# Tagging an outlier (agent instructions)

Input per reel: `outliers.json` (views, account median, multiple), `media.json` (caption, first 8s transcript, music),
and the frames `frames/<code>_0.jpg`, `_1.5.jpg`, `_3.jpg`. **Look at the frames.** The on-screen text and the opening
visual are half of the hook and the transcript can't show them.

Write one JSON line per reel to `data/<week>/tags.jsonl`. **Use only the labels below** so weeks compare. If nothing fits,
use `other` and say why in `note`. Never invent numbers.

```json
{"code": "...", "spoken": "first spoken line, verbatim (fix obvious whisper mishears from the on-screen text)",
 "text_on_screen": "the text hook in frame, verbatim, or null",
 "visual": "what we see in the first 1.5s, one plain line",
 "hook_type": "...", "text_hook": "...", "visual_open": "...", "format": "...", "topic": "...", "cta": "...", "length": "...",
 "triple_match": true,
 "why_it_worked": "one line: the mechanic, not a compliment",
 "pattern": "the reusable shape with the specifics stripped out, e.g. 'The only [N] [things] you need to [identity payoff]'",
 "note": ""}
```

## Labels

- **hook_type:** `contrarian` · `withheld-method` (how to X, method lands late) · `named-person` (someone famous / a client named) ·
  `number-stakes` (money, time, a hard number) · `question` · `story-cold-open` (mid-scene, no setup) · `warning` (danger, don't do this) ·
  `exclusive-claim` (only, ever, nobody) · `pov-skit` · `list` · `reaction` (stitch / responding to someone) · `confession` · `other`
- **text_hook** (what the on-screen text does next to the spoken line): `none` · `same-as-spoken` · `adds-charge` (warning, admission, removal) ·
  `label` (topic title) · `curiosity` (withholds) · `other`
- **visual_open:** `motion` (moving camera or subject from frame 1) · `still-talking-head` · `prop-in-hand` · `contrast` (before/after, odd object) ·
  `pov-hands` · `b-roll-cinematic` · `screen-or-graphic` · `crowd-stage` · `other`
- **format:** `talking-head` · `podcast-clip` · `skit` · `voiceover-broll` · `tutorial-demo` · `listicle` · `story` · `reaction-stitch` ·
  `carousel-video` · `interview-street` · `other`
- **topic:** free text, 1–3 words, lower case (`identity`, `sleep`, `back pain`, `pricing`, `editing`). Reuse last week's topic words where they fit.
- **cta** (caption or on screen): `none` · `follow` · `comment-keyword` · `dm-keyword` · `link-in-bio` · `save-share` · `question-for-comments`
- **length:** `<15s` · `15-30s` · `30-60s` · `60s+`
- **triple_match:** do the spoken line, the text and the opening visual all point at the same promise? (Kallaway's triple hook)

## Rules
- Tag the **mechanic**, not the topic. The bank exists so a hook shape can be moved into another niche.
- Never copy a live prospect's or competitor's signature line word for word into client work. The `pattern` field is the reusable part.
- No client names in here. This is niche research, not client data.
