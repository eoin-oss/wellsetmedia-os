<!-- Living doc: update in place. -->
# Weekly content research

Built 20 Oct 2026. **Every Monday.** For Eoin and every client: what the best accounts in each niche are doing *this week*,
which hooks broke out, which formats and topics are rising, and a hook bank that learns what actually works for each person.

Run it with `/weekly-research` (or "run the weekly research"). About 30 minutes of Eoin's time: reading the brief and writing hooks.

## The loop

| # | Step | How | Who |
|---|---|---|---|
| 1 | **Pull** | `pull.js` in his logged-in IG Chrome ("work" browser): one tab, a detached loop over every handle (3 pages ≈ the last 36 reels each, ~10s an account). Dump → `data/<week>/raw.txt` | Claude (browser) |
| 2 | **Qualify + find outliers** | `python3 research.py ingest` · account must be winning (median ≥ 20k over its last 30 settled reels, ≥ 4 posts a month). Outlier = ≥ 3x its own median, last 60 days | script |
| 3 | **Media** | `python3 research.py media` · caption, first 8s transcript, frames at 0 / 1.5 / 3s for the outliers only | script (background) |
| 4 | **Tag** | Opus agent per `TAGGING.md` → `data/<week>/tags.jsonl` (spoken, on-screen text, visual, fixed labels, the reusable pattern) | agent |
| 5 | **Bank** | `python3 research.py bank` → `bank/<person>.jsonl` | script |
| 6 | **Niche read** | `python3 research.py trends <person>` (tag shares now vs the 4 weeks before) **plus** a web pass per niche: platform changes, news, sounds, the conversation the niche is having this week | script + agent |
| 7 | **Brief** | `reports/<person>/<week>.md` per person (template below). Eoin writes the hooks; the brief only hands him the patterns | agent |
| 8 | **Close the loop** | A week after a client reel goes out using a bank pattern, `python3 research.py result <person> <code> won|dead` (won = beat that person's own median) | Claude |
| 9 | **Watchlist upkeep** | Accounts that fail qualification 2 weeks running get dropped. Once a month: search the niche on IG for new accounts, add candidates | Claude |

## The brief (reports/<person>/<week>.md)

1. **This week in the niche** (3–5 lines): what's rising, what's fading, anything platform-level. Numbers from `trends`.
2. **The outliers**: top 5, each with the link, the multiple, spoken + text + visual, and the one-line mechanic.
3. **Patterns to steal**: 3–5 hook shapes with the specifics stripped out. **No finished hooks.** Eoin writes those.
4. **CTA notes**: what the outliers asked for and how.
5. **Bank scoreboard**: tried / won / dead for this person.
6. **Watchlist changes**: dropped, added, candidates.

## Rules
- Creative output is Eoin's: the system supplies patterns and evidence, never finished scripts or hooks.
- Never name a watched account inside client-facing work. Never reuse a prospect's signature line word for word.
- Outlier maths stays in Python. No model decides what counts as a winner.
- One Instagram loop at a time, sequential, with sleeps. If IG starts redirecting to login, stop and resume later.
- Spend: €0. If the browser pull ever fails for good, Apify's reel scraper (~$2.30 per 1k reels) is the fallback. Ask first and cap total spend.
- `HOOK-PATTERNS.md` (content/) stays Eoin's personal log of hooks he flags. The bank is the machine version.

## Files
`watchlists.json` (people, niches, accounts, thresholds) · `pull.js` · `research.py` · `TAGGING.md` ·
`data/<week>/` (raw, accounts, outliers, media, frames, tags) · `bank/<person>.jsonl` · `reports/<person>/<week>.md`
