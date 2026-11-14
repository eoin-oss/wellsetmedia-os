# Copy rules: WellSetMedia + personal brand

Adopted 7 Oct 2026. Applies to every piece of copy for WellSetMedia and Eoin's personal brand:
scripts, captions, site copy, proposals, DMs, emails, audits, Loom scripts, VSLs, ads.

The rulebook is `copy-rules-pack/` (installed from Eoin's download). This page says how it applies
here and what wins when it disagrees with something we already had.

## Always load

1. `copy-rules-pack/Context/Marketing/copy-rules.md`: the hard rules
2. `copy-rules-pack/Skills/Marketing/Copy/quality-bar.md`: the build standard
3. `copy-rules-pack/Skills/Marketing/OUTPUT-QUALITY-GATES.md`: pre-ship gates
4. Then route by task with `copy-rules-pack/CLAUDE.md` (VSL, ads, hooks, email, offers, pages)

Scripts still go through `../content/scripts/SCRIPT-RULES.md` and the 5-phase retention framework.
The pack sits on top of both.

## The hard rules, short

- **Zero em dashes.** Periods, commas, colons, line breaks.
- **The banned AI phrase list**, plus "quick 15" in any form (Eoin's own ban).
- **No foil framing.** No "not X, it's Y", no "most people do X", no strawman before the claim.
- **No 3-short-plus-1-medium cadence.** No stacked rhetorical questions.
- **The three-test on every line:** can you picture it, can it be proven false, could nobody else say it.
- **Never invent proof.** Missing number, name or result goes in as `[PLACEHOLDER]` / `[NEED: …]`.
- **Count repeated words** before shipping and swap the habits for plainer words.
- **3+ hook or headline options** on every deliverable that has one.

## Where this pack and our existing rules meet

- **Voice wins.** Eoin's voice (`~/.claude/CLAUDE.md`, Identity/Voice.md) and his outbound formula
  beat the pack's defaults. The pack's "pet words" note is from its original author: keep the rule
  (rotate habit words), not that person's word list.
- **"Name the enemy" vs "no foil framing."** Name the bleed directly, as a fact about the reader
  ("your best reel was the last thing you posted for 158 days"). Never as a contrast with a strawman.
- **Self-check block** (quality-bar section 9) goes on written deliverables: scripts, pages, VSLs,
  email sequences. Not on chat replies or DMs.
- **Paths the pack mentions that don't exist here** (`Clients/{slug}`, `MyBusiness`,
  `Scripts/validation/*`, `Skills/voice-check`): our equivalents are `clients/<slug>/`,
  `brand/POSITIONING.md`, and checking by hand. Run the repeat-word count with the shell snippet in
  copy-rules.md.
- **Never run `quality-check-output`.** It posts work to the pack author's API. Not installed.
