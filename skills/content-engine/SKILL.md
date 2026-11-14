---
name: content-engine
description: Eoin's weekly content engine (locked 12 Nov 2026), for his own brand first and later every WellSetMedia client via the portal. Runs the Saturday content day in order (research -> ideation multiplier -> scripts -> shot list -> film -> edit -> stories) and forces every framework at its step so none get skipped. Use when Eoin says "/content-engine", "content day", "plan this week's content", "run the multiplier", "ideas for this week", "proof content", or starts scripting his own reels.
---

# Content engine (locked 12 Nov 2026)

One chain, one gate per step. Every framework lives at the step where it's used, so "using it properly" = running
the step, not remembering. Never skip a step's checks. Creative is Eoin's: Claude brings research, structure, angles
and drafts when asked; he picks and approves. Ideas Claude generates stay in chat until he picks
(never written into a pipeline unapproved).

**Source of truth** (read before every run): `$WSM_HOME/content/strategy/`
- `LOCKED.md` (cadence, rotation, pillars, rules) · `dream-follower.md` (dream follower, ICP pain, questions bank,
  pillars, story beats) · `research-inputs.md` (the research Eoin fed in).
- Client version: same files under `clients/<slug>/strategy/`, built from the 4 onboarding questions.

## The week
**Saturday = content day** (all of it in one day). Always a week ahead: what's filmed Saturday posts the next week.
30 reels a month (1 a day): ~18 TOF (dream follower) / 12 MOF (ICP), every pillar ~3x a month. Spares = trial reels.
Stories: 3 a week (Mon documentation, Wed FREE VALUE DROP, Fri wins/belief + WEEKEND). Proof content: 1 a week.
Value drop: 1 a week, non-negotiable. Sunday: log numbers only, no changes till day 30.

## Steps (Saturday)
1. **Research (30 min).** `/weekly-research` report for the week (outliers = 3x the account median) +
   new entries in the questions bank (DMs, calls, audits, client answers) + the proof bank.
2. **Ideation: the multiplier (45 min).** Pick ~5 seeds: outliers (steal like an artist: the idea, never the
   wording) and questions-bank pains. Each seed: tag pillar + TOF/MOF, then 4 rephrases, 3 reframes, and formats
   from the editor modes (penguin, eoin-yap, negative-text, kallaway-split, how-to retention, POV text, shoot BTS).
   Output an idea board in chat. Eoin picks 8-10. Check the mix against the month: TOF/MOF ratio, pillar spread,
   1 proof, 1 value drop.
   - TOF must hit a dream-follower want/fear/tension. MOF must name an ICP pain from the bank in their words.
3. **Scripts (one at a time, in conversation).** Every script runs ALL of these, in this order:
   - Shape: retention framework (hook, context in one working line, conflict, turn+payoff, echo) —
     memory `project_retention_script_framework`. Story layer under it: want->need midpoint, lingering emotion,
     one-sentence test — `SCRIPT-RULES.md` §6.
   - Journey reels (a personal arc, not a pure story): hook -> backstory -> epiphany/shift moment -> come up/journey
     -> outcome -> valuable lesson (`research-inputs.md`, added 13 Nov). Shift = the turn, lesson = the payoff.
   - How-to videos: the withheld-method format (method held to ~30s, "Here's how to... And no, this isn't
     another..." opening) — memory `project_how_to_retention_format`.
   - Hook: 2-4 stacked reversals (memory `feedback_hook_stacking`) + the 2-line text hook. Penguin style = no text hook.
   - Hooks SOP (Josh Agbisit, 14 Nov): `content/strategy/hooks-sop/killer-hooks.html` (artifact
     https://claude.ai/artifact/RjbNSVqGKaYo4EwaL8uKnL). Check every hook against it: first-frame snap judgment, point of
     interest + belief tied to identity, the feeling, one of the 6 verbal types + a visual hook, amplifier by line 2-3,
     the $5 value test.
   - Language: `SCRIPT-RULES.md` (anti-generic law, banned patterns, concrete anchors, `[NEED: ...]` for any
     missing fact, silent self-audit). No price, no em dashes, no "quick 15", never knock other creatives,
     no unknown names. Proof only from the proof bank.
   - Comment test: what should people type under it. CTA in caption only (keyword).
   - Output per script: the script with `[VISUAL]` cues, `[NEED:]` gaps, two alt hooks, pillar + TOF/MOF + format.
4. **Shot list.** Setup-first across all the day's scripts (memory `feedback_batch_shooting_by_setup`),
   A-roll block then b-roll block. Flag anyone else on camera (Kyle: his OK before his face/name in Eoin's content).
5. **Film.** Then footage onto the SSD same day.
6. **Edit.** `/auto-edit` in the chosen mode, both gates (proposal, stills). QC cold, 1h+ later.
7. **Stories.** `/story-sequence` for the 3 slots, beats built on the structure (type, hook, amplifier by frame 3,
   value, CTA only in its slot). Hooks pull from the dream follower's wants/fears; amplifiers from the proof bank.
8. **Log + learn.** Each post: pillar, TOF/MOF, format, hook, views, skip rate, saves, follows, keyword replies.
   Month end: re-multiply the winning seed/angle/format (SOP 03b month 2: repeat winners + test new).

## Free value drop rules
Real things Eoin built and uses (e.g. the story-sequence kit). Strip client names, client data, private paths and
internal mechanics before it ships. Make sure the recipient can actually use it (a Claude skill only helps Claude users:
pair it with a plain one-page version).
