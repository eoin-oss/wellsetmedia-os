---
name: story-sequence
description: Build an Instagram story sequence (9:16 photo frames with black text boxes) for Eoin or any WellSetMedia client, on a live page the person edits with Claude (text, red words, accent box, crop, zoom, position, order), then export the final 1080x1920 JPGs exactly as approved. LOCKED 12 Nov 2026 as SOP for Eoin and clients. Use when Eoin says "/story-sequence", "make a story sequence", "story frames", "IG story for <client>", or drops phone snaps for a story.
---

# Story sequence (locked 12 Nov 2026)

Eoin, 12 Nov: "whatever you did with the editing thing i want that locked in. thats defo gonna be sop AND USED FOR CLIENTS and for me going forwards."
First run: his "weekend into a month of content" story, `$WSM_HOME/content/stories/weekend-story/`,
page https://claude.ai/artifact/3dzmRCvyZuoiyWxtGKVg89.

## The look (don't redesign)
The More Life "My story" format (`morelife-carousel` skill) at 9:16:
- One real photo per frame, full bleed, 1080x1920. Their own snaps, never stock or AI.
- Black rounded boxes, white Helvetica Neue Bold, centred. One thought per box, 1 to 5 boxes per frame.
- `[[red]]` words for the pain, `{{green}}` words for the win (darker green on the white box). A line starting `! ` is a
  red box with white text, for the hook line that has to pop. One **accent box** per frame max (line starts `* `).
  Accent per brand: **Eoin = white box, black text**. **Kyle / More Life = gold #d4ad6e, black text**.
  Other clients: their brand's one accent, set in `theme` at Gate 1.
- Every frame but the last ends on `...`. The last frame is the CTA with the person's keyword.
- Text in the photo's empty space (headspace or floor), never on a face. Inside the IG safe area (y 250 to 1580).
- Copy: zero em/en dashes, no price, their words, no invented numbers or proof. Other people's faces: flag consent.

## Carousels (added 13 Nov)
Same look, same page, same renderer: set `"format": "carousel"` in the doc for 1080x1350 (4:5) slides, safe area
y 80 to 1270, no "..." rule. Over-under = text group on top AND bottom of every slide. Jobs: `content/carousels/<slug>/`.
First: "I've never been ready" (`content/carousels/never-ready/`).

## The structure (locked 12 Nov, from Eoin's story research)
Every sequence is one TYPE and runs HOOK -> AMPLIFIER -> VALUE -> CTA (optional). Label all of it at Gate 1.
- **Types:** documentation (the week, loose, few boxes, no CTA) · wins (client results) · value (process, breakdown,
  case study, a free drop) · limiting belief (contrarian open, their objections, the reality, proof, CTA). Two may mix.
- **Hook, frame 1, pick one:** recency, relevancy (their fears/desires), celebrity jacking, proximity (same city or
  situation), conflict, weird.
- **Amplifier, frame 2 or 3, never later:** social proof, desire, roadblock, controversial, personal story, information
  gap, call out, negative assumption ("and no, it's not X, Y or Z"), risk reversal, celebrity jacking, reference,
  visual, scarcity, killing expectations. Lint: no amplifier by frame 3 = fix before the page goes live.
- **Value:** a tool, resource, insight, step-by-step, relatable story with a lesson, or entertainment. Must make them feel something.
- **Guardrails (their rules win):** scarcity only if real. Controversial = against an idea, never a creative.
  Celebrity jacking = well-known public figures only, never unknown names. Reference = real sources only.
  Proof comes from the person's proof bank, never invented.
- **Weekly rotation (3):** Mon documentation, no CTA · Wed value = the weekly FREE VALUE DROP (non-negotiable for
  Eoin, e.g. a skill/system he uses for clients; keyword CTA to get it) · Fri wins or limiting belief, offer keyword
  CTA (Eoin: WEEKEND). Never the same CTA every day.
- **Strategy link:** stories are part of `/content-engine`. Hooks pull from the person's dream follower
  (`content/strategy/dream-follower.md` for Eoin, `clients/<slug>/strategy/` for clients): their wants, fears, tension.
- **Proof bank:** Eoin `$WSM_HOME/content/proof-bank/`, clients `clients/<slug>/proof-bank/`. Numbers, client DMs,
  screenshots, BTS, each with date + where it came from + OK to show.
- **Log after posting:** `<job>/results.md`: type, hook, amplifier, CTA, replies, per-frame exits/forward taps (IG insights).

## Flow
1. **Photos.** They dump phone snaps in a folder. Run
   `python3 scripts/prep.py "<folder>" <job dir> [IMG_2520@1.35 ...]`: sorts into `images/` + `videos/`,
   full-res to `<job>/full/`, 1080px web copies to `<job>/pub/photos/`, optional video stills. Look at every photo.
2. **Words (Gate 1).** Draft the beats in chat, labelled per The structure (type, hook, amplifier by frame 3, value,
   CTA or none), each mapped to a photo, proof pulled from the proof bank.
   Creative is theirs: present, they edit or say go. Client stories: the client approves words before export.
3. **The page.** Copy `assets/page.html` to `<job>/pub/<slug>.html`, replace `{{TITLE}}` and `{{STORIES}}` (one story: `[["main","Story"]]`; a week: `[["mon","Mon 16 · Documentation"],["wed",...],["fri",...]]`, each its own doc `story/<key>`, tabs on the page), publish with the Artifact
   tool: `capabilities: {"db": {}, "user": {}}`, `files` = every `photos/<stem>.jpg`. Then seed the doc with
   ArtifactData `set` on collection `story`, doc `main`:
   `{title, theme: {accent, accentInk}, photos: [stems], frames: [{photo, fx, fy, zoom, size, top, topY, bottom, botY}]}`
   (`topY` = top of the top group, `botY` = bottom of the bottom group, in 1920px frame space; start 270 / 1560).
   **Carousel:** add `"format": "carousel"` to the doc. The page switches to 4:5 (1080x1350, safe area y 80 to 1270,
   start 100 / 1250) and the renderer exports carousel slides. Same edit-live-then-go flow.
   Verify with one ArtifactData `list`. Give them the link. For a client, Eoin shares it from the page's Share menu.
4. **Edit together.** They edit on the page (autosaves) or tell Claude; Claude edits the doc with
   ArtifactData `update`/`str_replace` pinned to the version it read. Read the doc before every change.
5. **Export (on their go).** ArtifactData `get` with `out_dir`, then
   `python3 scripts/render.py <doc.json> <job>/full ~/Desktop/"<slug>" --sheet`.
   The renderer mirrors the page's CSS, so the export matches what they approved. Fix or flag every `CHECK:`
   (a deliberate choice by them stays, but say so). Look at the contact sheet. Open the folder only if asked
   (Eoin AirDrops it to his phone). Keep `story.json` + contact sheet in the job dir.

## Photos
Eoin's phone library is organised by period on the SSD: `personal brand directory/phone content/` (01 childhood ... 15 glasgow nov 2026),
with `INDEX.md` / `INDEX.json` (his description, date, tags, flags per file). Pick frames from the index; respect flags
(blur names on comment screenshots, OK before showing clients/others, never the slur text in the plane video).
New dumps: describe them on the photo library page (claude.ai/artifact/Xo7oCovP5poj8A1Knp2pBy), then organise + index.

## Where jobs live
- Eoin: `$WSM_HOME/content/stories/<slug>/`
- Clients: `$WSM_HOME/clients/<slug>/stories/<slug>/`, with that client's `CONTENT-RULES.md` applied (Kyle: no
  swearing, no materialism, LIMITLESS CTA, gold accent).
