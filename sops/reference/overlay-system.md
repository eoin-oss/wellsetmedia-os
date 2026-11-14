# Overlay system

**Transparent PNG overlays for the viral formats. Locked 5 Oct 2026.**

Lives at `$WSM_HOME/content/overlay-system/`.

---

## Why it exists

Not speed — **consistency.** The trial variants get outsourced, and a generator means an editor
physically cannot put the text in the wrong place or the wrong size. The format enforces itself.

That's what makes the outsourcing condition on the Middle and Creative Direction tiers actually
hold.

---

## Generate a video

```
cd $WSM_HOME/content/overlay-system
python3 generate.py 01          # make more money
python3 generate.py --list      # what's defined, and what's missing items
```

Writes 9 transparent PNGs to `output/<slug>/` — `00 cover.png` plus `01`–`08`.
1080×1920, alpha everywhere except the image and the text.

---

## The structure

```
overlay-system/
  generate.py        one video, one command
  videos.py          the locked scripts — edit here, re-run
  b-roll/            reference images, one folder per video
  output/            generated PNGs, one folder per video
```

The generator lives in `tools/overlay.py`.

---

## The format, measured off real references

| | |
|---|---|
| Canvas | 1080 × 1920, transparent |
| Cover grid | 3×2, 9%–88% wide, 1.8%–33.8% tall, 5px gaps |
| Item image | one, centred, same band, 60% of grid width |
| Title | 52px, auto-shrinks to fit |
| Item text | 42px, `"N. the line"` |
| Stroke | 11% of font size, black |
| Text block | starts 36.5%, never past 52% — **the face lives below** |
| Font | Inter Black |

**Type size was wrong twice before it was measured.** Don't eyeball it — if a new format comes in,
take a screenshot of a real one and measure the text width against the frame width.

---

## Adding a new video

1. **Items into `videos.py`** — the locked script, verbatim from the formats guide
2. **Images into `b-roll/<slug>/`** — 14 minimum, 25+ comfortable
3. `python3 generate.py <key>`

Image selection is automatic: sorted by brightness, mid-range first so the cover grid reads as one
picture, the rest spread across the items so the video keeps moving.

---

## Picking b-roll

**Each video gets its own register.** They are not interchangeable, and a wrong-register image is
more obvious than a missing one.

| | Register |
|---|---|
| **Make more money** | Night, restraint. City windows, watches, desks, cars on wet streets |
| **Dangerously present** | Stillness. Hands, steam, light through windows, quiet rooms |
| **Ridiculous flow** | Steam, early light, work in progress, water, empty gyms |
| **Obscenely abundant** | Warm, full, golden hour. Tables, evenings, generosity |
| **Delusionally confident** | Posture, stages, spotlights, walking in, before the fight |
| **Disgustingly motivated** | Effort. Dark mornings, rain, training, grind |

**No flex imagery, in any of them.** Restraint reads as wealth; supercars and cash read as hustle,
and that fights the brand.

The pull is a Pinterest search, two or three queries per video, grabbing roughly 30 and binning the
bright ones — ads and stock come back pale, and every register here is dark.

---

## The rule that isn't technical

**These are reference images. Someone else made them.**

Fine for deciding a look and for a moodboard. If one goes into a published reel for a paying client,
that's a different question and it's worth a thought before it ships — not after.
