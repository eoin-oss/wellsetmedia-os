---
name: content-audit
description: Full Instagram + YouTube content-funnel audit for a WellSetMedia prospect or warm lead. Every reel's views/likes/comments pulled live, formats tagged from captions, transcripts and covers, spikes explained, TOF/MOF/BOF mapped, a month-one play, shipped as the branded Night report (HTML + PDF + private artifact link) plus a Loom beat script. The locked format from the Mark Meehan and Kyle Ritchie audits. Use when Eoin says "audit <name>", "content audit", "go through his IG and YouTube", "new lead to audit", or drops a prospect's IG/YT links for a Loom.
---

# Content audit: the locked format

Eoin, 2026-09-13: *"that audit template is so damn good keep that shit locked in."*
This is the standard for every prospect audit. **Don't redesign it per client.** Only the
config, the tags and the copy change.

Reference builds (read one before starting):
- `$WSM_HOME/clients/kyle-ritchie/audit/`: the config-driven one. Its
  scripts became the template.
- `$WSM_HOME/clients/mark-meehan/audit/`: the production-heavy one (cuts
  per minute, loudness, thumbnails, text styles).

Template: `$WSM_HOME/tools/audit-template/`, shared look
`tools/audit_kit.py`. For a cold-outreach receipts doc (no full audit), use `prospect-proof`.

## What it produces (per client, in `clients/<slug>/audit/`)
- `report.html` + `report.pdf`: 10 sections plus an appendix where every reel and video is linked.
- A private artifact link (publish with a `files` map, then `pbcopy` the URL).
- `loom-script.md` + `.pdf`: a beats table, the lines in Eoin's voice, an **INTERNAL** block and locks.
- `data/`: the raw pulls (the masters), `img/`: covers and screenshots.

## Order of work
1. **Get the links from Eoin.** Never guess the account.
2. **Set up:** `mkdir -p clients/<slug>/audit/{data,img}` and copy the template in:
   `cp tools/audit-template/*.{py,js,sh} clients/<slug>/audit/` and
   `cp tools/audit-template/data/config.example.json clients/<slug>/audit/data/config.json`.
3. **Pull** (the recipes are below): YouTube → Instagram numbers → dates → captions + covers in
   the background.
4. **Look:** a profile screenshot (crop the header to `img/ig-header.jpg`), 3–4 grid screens,
   the bio, and the funnel page (curl it, since the browser may lack permission). Read the
   captions and transcripts of the biggest reels.
5. **Review with Eoin before building** when he asks ("review it before making anything"): give
   the key numbers, early reads and questions (ads? who edits? warm paths?). His read plus the
   data sets the thesis.
6. **Verify every claim.** Transcribe the hooks, frame-strip the spikes, check what the car or the
   number actually is. **Correct Eoin plainly** when the data disagrees. The report has to be
   unarguable. (Past misses: the fat-loss format *was* repeated once; the reel said $37K, not
   $30K; the car was a Lamborghini, not the Porsche; text-over-b-roll *did* exist.)
7. **Tag:** `python3 tag.py` (caption rules plus verified overrides), then
   `python3 sheet.py <scratch>` contact sheets, then a visual pass and more overrides. Letterboxed
   lessons auto-become "YouTube cut-down" in the build.
8. **Build:** fill `data/config.json` (client block, key reels, spikes, take, script, MOF tiles,
   b-roll tiles, labels, baseline, play), then `python3 build.py`. Labels accept `{placeholders}`
   from the computed stats (see `S` in build.py).
9. **One look, one fix pass:** a headless screenshot at 1300 wide, sliced into 2400px strips.
   Look once, fix once, no test loop.
10. **Publish** the artifact (favicon required, `files` map of every `img/` path the HTML uses),
    then `pbcopy` the link.
11. **Loom script:** `python3 ../../../tools/md2pdf.py loom-script.md`.
12. **Hygiene:** add a line to `context/STATE.md` → In flight, and a memory file plus the
    MEMORY.md index.

## Iron rules
- **Live numbers, stamped.** Capture date in the header and footer. Newest ~2 days are excluded
  from medians (still accruing).
- **Ads:** ask. Promos/ads are tagged `promo` and excluded from every organic figure.
  **Hidden likes show as ~3 likes.** They're not ads, so mark them "hidden".
- **Posts ≠ reels.** Reels not shared to the grid don't count as posts. Pull the reels tab.
- **Measure before claiming quality.** Loudness (ebur128), cuts per minute (scene > 0.3),
  frames, thumbnails (check all of them). Say what a meter can't prove (echo, room sound).
- **No inference dressed as data.** You can't see follower vs non-follower reach, so state
  medians, not "only reaches followers".
- **Client-facing copy:** WellSetMedia voice, no slop, no negative parallelism, never knock
  another creative's work (Kyle's YouTube creative director). Show the result, not the mechanics.
- **Internal notes never go in the report.** Warm paths, corrections, don't-say items and
  unverified hunches go in the Loom script's INTERNAL block.
- **Loom lines:** Eoin's casual register, one take, about 5 min, sign "All the best, Eoin."
  **Never "quick 15".**

## Data recipes
- **YouTube:** `bash pull_yt.sh @handle` writes `data/yt_full.jsonl` (every upload: views, likes,
  comments, duration, date). Thumbnails: `i.ytimg.com/vi/<id>/maxresdefault.jpg`, falling back to
  `hqdefault` if under 5KB.
- **Instagram numbers** (claude-in-chrome, his logged-in Chrome):
  1. Navigate to `instagram.com/<handle>/reels/`, then run `ig_pull.js` STEP 1 (hook) via
     `javascript_tool`.
  2. Do **one real scroll** (the `computer` scroll action) so IG fires its own pagination query.
  3. Run STEP 2 (replay) repeatedly until `more:false`. Each call loops about 38s (the tool
     times out at 45s).
  4. Run STEP 3 (dump) in chunks of 35 (output truncates at about 1.3K chars) and paste into
     `data/ig_raw.txt`.
  5. Run `python3 ingest_ig.py`. It decodes post dates from shortcodes and writes
     `data/ig_reels.json`.
  6. Never return request bodies or CDN URLs from JS. They carry tokens and the output gets
     blocked. `web_profile_info` returns 429, so don't bother.
- **Captions + covers:** `bash fetch_meta.sh` in the **background**. It uses yt-dlp logged out,
  sequential, about 3s per reel. Never run two Instagram loops at once.
- **Hooks + frames:** `python3 media.py transcribe CODE…` (openai-whisper, base model), and
  `python3 media.py strips CODE…` to eyeball. Whisper mishears numbers and names, so
  cross-check the on-screen text.
- **Quality:** `python3 media.py measure CODE…` gives cuts per minute, LUFS and resolution in
  `data/reel_metrics.json`. For YouTube loudness, pull `-f bestaudio --download-sections
  "*90-150"` and run ebur128 on it.
- **Gotchas:**
  - Reel pages render the video black, so use covers or the grid for visuals.
  - zsh doesn't word-split `$L`, so use arrays.
  - `pgrep -f "x.txt"` matches its own waiting shell, so use `pgrep -f "x[.]txt"`.
  - A click on a page that's still loading can land on the wrong video. Wait before clicking.
  - Headless Chrome hangs when it shares the live Chrome profile. `build.py` now passes its own
    `--user-data-dir`; do the same for any screenshot pass, and give the PDF step a few minutes.

## Report structure (build.py; the copy lives in config.json)
Hero (header shot, 6 tiles, verdict) → 01 timeline of every reel (formats that travel = teal,
promos = dashed) → 02 median by format plus share posted vs share of views → 03 spike cards →
04 the take → 05 the script (annotated transcript vs the hook that holds) → 06 MOF tiles →
07 gaps (letterboxed, b-roll, teaching) → 08 YouTube vs Instagram → 09 funnel (TOF/MOF/BOF
chips) → 10 month-one play plus baseline table → appendix (every reel and video linked).
For a production-first audit (Mark), swap 07 for Mark's production blocks: the cuts chart, the
engagement tiles, the camera montage, text crops, loudness and thumbnails.
