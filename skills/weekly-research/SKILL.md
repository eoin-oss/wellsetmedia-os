---
name: weekly-research
description: Monday content research for Eoin and every WellSetMedia client — pulls each niche watchlist from Instagram, keeps only accounts that are genuinely winning, finds each account's outlier reels (3x its own median), breaks down the hooks (spoken + on-screen text + opening visual), banks the reusable patterns, reads niche-wide trends and writes a one-page brief per person. Use when Eoin says "/weekly-research", "run the weekly research", "what's working in the niche", "hook research", "update the hook bank" or "watchlist".
---

# Weekly research

Home: `$WSM_HOME/tools/research/`. **Read `README.md` there first**: the loop, the brief template, the rules.

## Run order
1. **Browser:** the Chrome named **"work"** (his 2nd monitor, logged into IG). Never the DCU profile `6d4491f2…`, which bounces IG to login. If "work" isn't connected, `switch_browser` and have him click Connect.
2. **Pull:** follow `pull.js`: one tab on any watched account's /reels/, STEP 1, a real scroll, STEP 1b, then STEP 2 with every handle from `watchlists.json` (deduped). It runs detached in-page; poll STEP 2b. "RATE LIMITED" = stop, report how far it got, rerun later (it skips done accounts). Then STEP 3 chunks, appended with no separator, into `data/<week>/raw.txt`. Then STEP 4 to clear.
3. `python3 research.py ingest` → read the qualified/failed table and the outliers.
4. `python3 research.py media` in the **background**.
5. **Tag:** one Opus subagent per ~15 outliers, pinned `model: opus`, with `TAGGING.md`, `outliers.json`, `media.json` and the frames folder. Each writes its own `tags_<n>.jsonl`; concatenate into `tags.jsonl`.
6. `python3 research.py bank`, then `python3 research.py trends <person>` per person.
7. **Niche web pass** per niche (WebSearch, standard mode): platform changes, news and the conversation the niche is having this week. Two or three searches, no more.
8. **Briefs:** `reports/<person>/<week>.md` per the README template. Patterns only, **never finished hooks or scripts** (creative output is Eoin's).
9. **Close the loop:** for client reels that used a bank pattern and are a week old, mark won/dead with `research.py result`.
10. Report in chat: per person, the top 3 outliers + the one trend that matters, plus the paths. Don't open files.

## Rules
- One Instagram loop at a time. Never `pkill` Chrome.
- €0 spend. Apify is the fallback only with his OK and a total spend cap.
- Never name a watched account in client-facing work. Never reuse a live prospect's signature line word for word.
- Watchlist upkeep: drop accounts failing 2 weeks running; monthly, search the niche on IG for new candidates and add them to `watchlists.json`.
