---
type: quality-gates
status: draft
created: 2026-05-27
tags: [marketing, quality, validation, outputs]
---

# Marketing Output Quality Gates

Use this before final delivery of any marketing output.

The goal is not to make outputs longer. The goal is to make them more specific, more useful, safer, and more likely to survive real client review.

## Universal Gate

Every marketing output must pass these checks:

0. **Golden rules (HARD BLOCK):** resolve the workspace first (`Skills/conventions/workspace.md`) — a named client is `Clients/{slug}`, no client on a generative task is `MyBusiness` — then run `python3 Scripts/validation/golden_rules_check.py --workspace {workspace} <deliverable>` (or `--client {slug}` for a client, `--mybusiness` for the member's own business). Exit 1 blocks the deliverable until every violation is fixed. This is enforced by code, not model judgment, it runs first, and it fires for MyBusiness/own-business deliverables too — "no client named" is not a bypass. (Also wired into `Skills/voice-check/` Check 0.)
1. Client context loaded if client work.
2. Output matches the requested deliverable.
3. Brief-before-build completed for major deliverables.
4. Strategy is named before output begins.
5. No unsupported proof, metrics, guarantees, screenshots, testimonials, or claims.
6. No cross-client details.
7. Clear next action or save location.
8. No obvious AI filler or generic abstractions.
9. Any missing input is flagged as a gap, not invented.
10. **Voice check:** if client is named, run `Skills/voice-check/` against the output. Output must pass voice match before save.

**Universal gate behavior — iterate until pass (`Skills/conventions/iterate-until-pass.md`):** any FAIL or STYLE finding from any gate in this file auto-revises and re-runs the SAME gate, up to 3 passes; only what still fails after pass 3 is surfaced, with why. Members see one line — "N lines revised to pass [gate name]" — never raw failure lists. Hard blocks (golden rules) are never iterated away: they must actually pass or the member explicitly overrides.

## Autonomous Output Gate

Use this when the user wants the operator or vault to keep moving without repeated back-and-forth.

Load:

- `Skills/conventions/autonomous-output-contract.md`

Rule:

```text
Ask only when the answer materially changes the output or approval boundary.
If the answer is not blocking, infer, state assumptions, produce the deliverable, and mark gaps.
```

This is the default for autonomous operator tasks and high-speed client work.

## Brief Gate

Use before:

- VSLs
- ads
- offers
- landing pages
- email flows
- webinar/challenge funnels
- SEO/AEO strategy
- client reports

Ask questions only when the answer changes the output.

For VSLs, classify:

- direct response, educational, webinar-style, Howitzer/book-a-call, or explainer
- book-a-call, checkout, opt-in, application, DM, or other CTA
- cold, warm, retargeting, or existing-list traffic
- audience awareness level
- high-ticket or low-ticket
- price disclosed or withheld
- proof available
- objections to handle
- voice samples to match

## Copy Gate

Use for:

- sales pages
- headlines
- ads
- emails
- VSL scripts
- landing pages
- social content

Load:

- `Context/Marketing/copy-rules.md`

Check:

- no em dashes in final marketing copy
- no banned AI phrases
- no "not just X, but Y" pattern unless intentionally needed
- no generic promise without mechanism
- one clear reader
- one clear offer or CTA
- concrete pain, desire, or belief shift
- proof appears near important claims
- voice matches client or source samples

## Voice Gate

Use for ANY client deliverable (copy, email, VSL, ad, page, sales script).

Auto-runs via `Skills/voice-check/`. Member can also invoke explicitly.

Checks:
- Banned phrases (universal + client-specific)
- Required terms (client-specified must-include language)
- Sentence-length distribution vs client samples
- Voice rules from `{workspace}/voice/voice-rules.md` (`{workspace}` = the named client, else `MyBusiness` — see `Skills/conventions/workspace.md`)

Failure = revise-first per `Skills/conventions/iterate-until-pass.md`: stylistic findings are auto-fixed and re-checked (max 3 passes); only survivors are surfaced with why, and the member decides on those. Golden-rule hits stay hard blocks — fixed to pass or explicitly overridden by the member, never bypassed. Report: "N lines revised to pass your brand rules."

## Offer Gate

Use for:

- offer creation
- offer audits
- pricing
- guarantee/risk reversal
- offer stack

Check:

- clear target buyer
- clear painful problem
- clear desired outcome
- mechanism or delivery model
- offer components are named and useful
- bonuses are not filler
- price logic is explained
- risk reversal is believable
- fulfillment constraints are realistic

## Ads Gate

Use for:

- Meta ads
- creative strategy
- static ads
- video ad scripts
- campaign diagnosis

Check:

- objective is clear
- audience sophistication is stated
- creative angle is distinct
- hook matches the awareness level
- offer and CTA are explicit
- claims are compliant and provable
- diagnosis separates creative, targeting, offer, and funnel issues
- no budget or account changes without approval
- (creative strategy) tests iso-vary ONE variable (hook/visual/angle/format); win metric + min-data set before reading results
- (creative strategy) live creative audited against the documented strategy — drift flagged (e.g. off-strategy discount creative)
- (creative strategy) modular components are distinct (Andromeda-safe) and on-strategy; ad data used read-only

## Design Gate

Use for ANY visual design executed in Figma (or design output generally):

- static/motion ad design
- brand kits / design systems
- multi-placement resize
- Slides decks (pitch/SOP/sales/webinar)
- shader/texture work, design-to-code, Weave outputs

Load:

- `Context/Marketing/Creative/creative-execution-bar.md` — the **$1M/mo execution bar** (decent = FAIL); the standard the critique enforces
- `Context/Marketing/Creative/creative-director-system.md` — the idea/judgment layer (the CD bar); `brand-identity-system.md` for brand work
- `Context/Marketing/Creative/design-craft-system.md` — the taste/craft doctrine + Skill-Level Adaptation Protocol
- `Context/Marketing/Creative/design-quality-gate.md` — the enforced craft checklist (run on plan AND output)
- `Context/Marketing/Creative/anti-generic-gate.md` — AI-generation tells (runs alongside; different failure mode)

**Deterministic block (not optional):** a render/design step must pass `python3 Scripts/validation/creative_gate.py --job <job-folder>` — it BLOCKS unless `concepts.md` (≥10 distinct, swipe-anchored) + a `VERDICT: PASS` `critique.md` exist. Enforced every turn by the `aid-creative-enforcer` hook. "Decent" cannot ship.

First — the **idea bar** (creative-director check): is there a real idea, not just a layout? on strategy/insight? distinctive (survives the logo being covered)? does it feel something? would it earn attention? A weak idea fails here *regardless of craft* — route back to `creative-concepting`.

Then — the **craft bar** (same for every operator level, junior to senior):

- clear 1-2-3 visual hierarchy; one dominant focal point
- type on a scale, ≤2 fonts, disciplined weights, readable measure + line-height
- elements on a grid; consistent margins; spacing on the 8pt system
- one dominant + one accent color; text contrast passes (~AA); accent only on what matters
- consistent radii / icons / strokes / shadow style (no drop-shadow soup)
- on the client's `creative-foundation.md` style code
- no amateur-design tells (see `design-quality-gate.md` GATE B); passes the anti-generic gate too
- correct spec for placement (ratio, safe zones, resolution); on-design copy passed copy-rules/voice-check

The one-line test: *"Would a senior designer sign their name to this?"* If no, name the specific craft failure (usually hierarchy, type, or spacing), fix, re-check.

## Funnel And Landing Page Gate

Use for:

- landing pages
- opt-in pages
- confirmation pages
- webinar/challenge funnels

Check:

- page has one primary conversion goal
- hero answers who, what, why now
- sections follow a belief-building sequence
- proof appears before or near friction points
- CTA is repeated at natural decision points
- objections are handled before final CTA
- page copy does not rely on design to explain the offer

## Research Gate

Use for:

- market research
- competitor analysis
- avatar research
- keyword research
- content intelligence

Check:

- sources are listed or clearly described
- findings are separated from assumptions
- insights are actionable
- competitor claims are not overgeneralized
- customer language is preserved when useful
- recommendations connect back to evidence

## SEO / AEO Gate

Use for:

- SEO audits
- AI SEO/AEO
- content briefs
- schema
- site architecture

Check:

- target search intent is explicit
- entity/topic coverage is clear
- recommendations are prioritized by impact
- technical issues are separated from content issues
- claims about rankings or citations are not guaranteed
- source/citation strategy is included when relevant

## Sales Gate

Use for:

- sales scripts
- objection handling
- sales enablement
- pre-call emails
- retention/churn workflows

Check:

- buyer stage is clear
- objection is named accurately
- script does not sound manipulative
- claims are supportable
- next step is clear
- tone matches relationship stage

## Final Output Stamp

At the end of substantial deliverables, include a short validation note:

```text
Quality check:
- Strategy: [chosen strategy]
- Client context: loaded / not provided
- Proof gaps: none / listed
- Approval needed: no / yes, because [reason]
- Copy rules: passed / needs review
- Save location: [path]
```

For member-facing outputs, keep this short and practical.
