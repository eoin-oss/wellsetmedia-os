---
name: overlay-system
description: Generate transparent PNG overlays for Morelife's 10/10 habits viral reels — cover grid plus numbered item slides, sized and positioned from measured references. Also pulls and organises the b-roll reference banks from Pinterest. Use when Eoin says "generate the overlays", "run the overlay system", "do 10/10 habits for <topic>", "pull b-roll for <video>", or when a locked habits script needs its PNGs made.
---

# Overlay system — 10/10 habits

Built 5 Oct 2026 for Kyle Ritchie / Morelife. Since 6 Oct it also runs **Eoin's own set** —
kept fully separate: `videos_eoin.py`, `b-roll/eoin/`, `output/eoin/`, run with `--set eoin`.
Never mix the two brands' folders.

Home: `$WSM_HOME/content/overlay-system/`
SOP: `$WSM_HOME/sops/reference/overlay-system.md`
Generator: `$WSM_HOME/tools/overlay.py`

## Why it exists

Not speed — **consistency**. The trial variants get outsourced, and a generator means an editor
cannot put the text in the wrong place or at the wrong size. The format enforces itself, which is
what makes the outsourcing condition on the Middle and Creative Direction pricing tiers hold.

## Generate

```
cd $WSM_HOME/content/overlay-system
python3 generate.py 01          # by key
python3 generate.py --list      # what's ready, what's missing items
```

Writes 9 transparent PNGs to `output/<slug>/` — `00 cover.png` plus `01`–`08`.
1080×1920, alpha everywhere except the image and the text.

## The structure

```
overlay-system/
  generate.py        one video, one command
  videos.py          the locked scripts — edit here, re-run
  b-roll/<slug>/     reference images, one folder per video
  output/<slug>/     generated PNGs
```

## The format — measured, never eyeballed

| | |
|---|---|
| Canvas | 1080 × 1920, transparent |
| Cover grid | 3×2, 9%–88% wide, 1.8%–33.8% tall, 5px gaps |
| Item image | one, centred in the same band, 60% of grid width |
| Title | 52px, auto-shrinks to fit |
| Item text | 42px, rendered as `"N. the line"` |
| Stroke | 11% of font size, black |
| Text block | starts 36.5%, never past 52% — **the face lives below** |
| Font | Inter Black (`client-docs/fonts/Inter-Black.ttf`) |

**Type size was wrong twice before it was measured off a real frame.** If a new format appears,
screenshot a real one and measure the text width against the frame width. Do not estimate.

## Adding a video

1. Items into `videos.py`, verbatim from `clients/kyle-ritchie/content/VIRAL-FORMATS-GUIDE.md`
2. Images into `b-roll/<slug>/` — 14 minimum, 25+ comfortable
3. `python3 generate.py <key>`

**Images must be semantic (7 Oct rule):** set `"images": [one file per item]` on the video so each image shows what its line says, in a moody film / soft halation look, never sharp product shots. The automatic fallback below is only for when no picks are set:

Image assignment is automatic: sorted by distance from mid-brightness, so the cover grid reads as
one picture and the rest spread across the items.

## B-roll registers — not interchangeable

| Video | Register |
|---|---|
| make more money | Night, restraint. City windows, watches, desks, cars on wet streets |
| dangerously present | Stillness. Hands, steam, light through windows, quiet rooms |
| ridiculous flow | Steam, early light, work in progress, water, empty gyms |
| obscenely abundant | Warm, full, golden hour. Tables, evenings |
| delusionally confident | Posture, stages, spotlights, walking in, before the fight |
| disgustingly motivated | Effort. Dark mornings, rain, training, grind |

**No flex imagery in any of them.** Restraint reads as wealth; supercars and cash read as hustle,
and that fights the brand — which is framed as God's work, not a hustle.

## Pulling new b-roll

**Pinterest renders blank in the Claude-in-Chrome tab (hidden tab) — use the search API instead.**
Define `window.__pin(q, pages)` in the page: fetch `/resource/BaseSearchResource/get/` with
`source_url` + `data={options:{query,scope:"pins",rs:"typed",redux_normalize_feed:true,source_url,bookmarks}}`
and headers `X-Requested-With: XMLHttpRequest`, `X-Pinterest-PWS-Handler: www/search/[scope].js`,
`X-Pinterest-Source-Url`. Take `images.orig.url`, skip `is_promoted`. Return bare 32-char hashes,
one folder per call (output truncates ~1.1k chars); path = `h[0:2]/h[2:4]/h[4:6]/h.jpg`.
Then dedupe with a 12×12 average hash (Hamming ≤14) and eyeball a contact sheet — bin
identifiable people/models, text quotes, jets, cash.

Legacy notes (visible-tab method):

Claude-in-Chrome on Pinterest, two or three searches per video:

1. `window.__grab(4)` — scroll and collect, upgrading thumbs to `/originals/`
2. Return paths only (strip the `https://i.pinimg.com/<size>/` prefix) or the output truncates
3. `curl` each, falling back `originals` → `736x`
4. **Bin anything brighter than mean 165** — every register here is dark, so bright means a
   sponsored ad or stock crept in. Pinterest injects picture-frame mockups constantly
5. Delete files under 8k — failed fetches

## Status, 6 Oct 2026

**Eoin's set — all 7 generated** (`output/eoin/`): E1 on camera · E2 camera confidence · E3 forbidden creativity ·
E4 aligned · E5 opportunities · E6 impossible to ignore · E7 work feel expensive. 27–40 images each.

Morelife:

Ready and generated: **01 money · 02 present · 03 flow · 05 confident**
B-roll pulled but **no items written**: 04 obscenely abundant · 06 disgustingly motivated

165 reference images across six folders.

## The rule that isn't technical

**These are reference images someone else made.** Fine for deciding a look. If one goes into a
published reel for a paying client, that's a different question and it gets raised before it ships,
not after.
