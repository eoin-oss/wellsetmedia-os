---
name: morelife-carousel
description: Build More Life (Kyle Ritchie) Instagram carousels and story sequences in the locked "My story" format. Each slide is one full-bleed real photo, with black highlight boxes of white bold text set in the photo's empty space. Negative words are red, there's one gold box at most per slide, every beat ends on "...", and it closes on a "Comment LIMITLESS" CTA. Use when asked to make a More Life carousel, story carousel, origin story, client story, lesson carousel or IG story sequence, or says "/morelife-carousel".
---

# More Life carousel

The format comes from the "My story" carousel (9 Nov 2026). Run `examples/my-story/` to see it rendered. Every carousel and story sequence uses this look. Only the words and photos change.

## The look (locked, don't redesign)
- **One real photo per slide, full bleed**, 1080x1350. Story sequences are 1080x1920. Use real photos of Kyle, his clients and his life. Never stock or AI images.
- **Black rounded boxes with white bold sans text**, centred. Each box holds one thought, and boxes stack with a small gap.
- **Red is for the negatives only.** Mark the painful words with red: the problem, the fear, the low point ("sick with anxiety", "I froze at a networking event", "still feel stuck"). Use one or two red phrases per slide, never whole slides.
- **Gold box** (black text on gold): the turning point or the line to remember. One per slide at most, and not on every slide.
- **Pencil underline** (red, hand drawn): one per carousel, on a name or the key phrase.
- **Every beat ends on "..."** so the reader swipes. The hook can stretch the dots ("......"). The last slide has no dots.
- **Gold swipe arrow** bottom right on every slide but the last. The builder adds it.
- **Cards for screenshots:** a podcast header, a DM or a post goes on the dark card with text above and below it.

## Using the empty space (the part that makes it work)
Before placing any text, look at every photo. Put the text where the photo is empty:
- **Headspace:** the sky, ceiling or wall above the head. Use `"at": "top"`.
- **Floor:** the ground or the dark bottom of the frame. Use `"at": "bottom"`.
- **Split:** two lines in the headspace and two over the floor, when one block would cover the subject.

Never cover a face, eyes or hands mid-gesture, and don't cover the thing the slide is about (the books, the board, the stage). If the subject fills the frame, move the crop with `focus` (0 to 1 across and down the photo) and `zoom`, or pick another photo. Wide shots beat close-ups because they leave room.

## Story shape (origin story / client story)
Hook on a real photo (one sentence, plus a lower-third follow-up that opens the loop) → the spiral → family / roots → the turn → the false fix → the low point → the discovery → the work → proof → mission + CTA. Use 8 to 12 slides and 1 to 5 boxes per slide. Short lessons follow the same look: hook → the problem (red) → the reframe (gold) → 3 to 5 steps → CTA.

## House rules (Kyle's)
- His words where possible. Mark anything you've guessed and check it with him.
- No swearing.
- No materialism: no cars, money flexes or prices. Show the transformation, not the stuff.
- No named third parties (people, brands, venues) without their OK.
- Zero em dashes or en dashes. Use commas and full stops.
- The last slide ends on **"Comment LIMITLESS and I'll show you where to start"** (or a close variant with LIMITLESS in caps).
- Sentence case, natural speech. No corporate words, no hype.

## Edit it live (default for anything the client or Eoin will tweak)
Run it through the `/story-sequence` live page with `"format": "carousel"` in the doc and the gold accent
(`theme: {accent: "#d4ad6e", accentInk: "#000"}`). They edit words, crop, zoom and position on the page (or tell
Claude), say go, and `story-sequence/scripts/render.py` exports the 1080x1350 slides exactly as approved. Use the
`spec.json` builder below when you need the pencil underline, screenshot cards or the gold swipe arrow.

## How to build one
1. **Get the story and the photos.** Ask for the beats and drop the photos into a folder (e.g. `my-carousel/photos/`).
2. **Write the beats** as a slide list. Show Kyle the words before rendering.
3. **Look at each photo** (open it). Decide top, bottom or split, and the crop.
4. **Write `spec.json`** next to the photos. Copy `examples/my-story/spec.json` and change it:
   - `photo` + `focus` [x, y] + optional `zoom` (or `card` for a screenshot)
   - `size` (42 default, 50 for a one-line hook)
   - `groups`: each has `at` ("top"/"bottom"), `y` (px from the top of the slide), and `lines`
   - each line: `text` with markup `[[red words]]`, `__pencil underline__`, `\n` for a break, and `"box": "g"` for gold
   - `"format": "story"` at the top makes a 9:16 story sequence (keep text below y 250 and above y 1580)
5. **Build:** `python3 scripts/build.py path/to/spec.json --sheet`. Slides go to `export/` (01.jpg, 02.jpg…) and a `contact-sheet.jpg` lands next to the spec. Any `CHECK:` lines are rule breaks, so fix them.
6. **Look at every slide.** Check that no text is on a face, nothing is clipped, the red is only on negatives, there's one gold box max, and the dots are there. Move `y`/`focus` and rebuild until it's clean.
7. **Caption:** a short story version in his voice that ends on the LIMITLESS CTA, with 8 to 10 hashtags on mindset, identity, self-improvement and entrepreneur themes. No em dashes.

Needs Python 3 with Pillow (`pip install pillow`). On a Mac it uses Helvetica Neue Bold. Elsewhere it falls back to Arial Bold or DejaVu Sans Bold.
