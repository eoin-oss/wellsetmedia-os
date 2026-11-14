# Copy Quality Rules — Quick Reference

> These rules apply to ALL client-facing copy produced by this system. No exceptions.
> Full details in CLAUDE.md Section 9.

---

## Banned: Em Dashes

Never use em dashes (---) in copy. They are an AI writing giveaway.

**Instead use:** periods, commas, colons, or line breaks.

| Wrong | Right |
|-------|-------|
| We built this system --- and it changed everything | We built this system. It changed everything. |
| Your ads are failing --- your costs are rising --- your leads are dying | Your ads are failing. Your costs are rising. Your leads are dying. |

---

## Banned: AI Phrases

These phrases immediately signal "AI wrote this." Never use any of them:

- "I'd be happy to"
- "It's important to note"
- "It's worth noting"
- "In today's fast-paced world"
- "In today's digital landscape"
- "Leverage" (use "use" instead)
- "Utilize" (use "use" instead)
- "Game-changer" (use specific result instead)
- "Dive deep" (use "explore" or "break down")
- "Cutting-edge"
- "Revolutionary"
- "Groundbreaking"
- "Seamless"
- "Robust"
- "Streamline"
- "Elevate"
- "Empower"
- "Transform your"
- "Unlock the power of"
- "Take your X to the next level"
- "Look no further"
- "No fluff" / "zero fluff"
- "At the end of the day"
- "Let's be real"
- "Here's the thing"
- "The reality is"
- "The truth is"
- "Whether you're a... or a..."
- "Without further ado"
- "That being said"
- "In conclusion"
- "Moving forward"
- "Rest assured"
- "Don't miss out"

---

## Banned: Your Own Pet Words (rotate the vocabulary)

Ellis, 2026-09-20: "dont use words like quiet, use slow. for any words you see yourself
instinctively use, or that you use a lot in other scripts, try to find another one that
makes sense and is simple."

Two rules, both enforced by reading the finished piece back:

1. **Prefer the plainer word.** `quiet` -> `slow`. `properly` -> `well` / `right`.
   `genuinely` -> `really`, or cut it. `completely` -> cut it. `quicker` -> `faster`.
   `nobody` -> `no one`. `utilise`, `leverage`, `sort of` -> cut.
2. **Count your repeats before shipping.** Any content word appearing more than 2 or 3
   times in one deliverable, or carried across from the last deliverable, is a tell.
   Swap most of them for a simpler word that means the same thing. The exception is the
   locked offer language and the angle's own spine word, which are supposed to repeat.

Check it, don't eyeball it:

```bash
sed -n '/^## Ad 1/,$p' FILE | tr 'A-Z' 'a-z' | tr -cs "a-z'" '\n' \
  | grep -E "^[a-z']{5,}$" | sort | uniq -c | sort -rn | head -40
```

Then diff that list against the previous set in the same folder. Words topping both lists
are habits, not choices.

---

## Banned: AI Cadence Patterns

**Pattern to avoid:** 3 short punchy sentences followed by a medium-length one.

Wrong:
> Your ads are failing. Your costs are rising. Your leads are drying up. But there is a proven system that fixes all three of these problems at once.

Right:
> Every month you spend $3,000 on ads that bring in 12 leads. Six months ago, the same budget brought 40. The Meta algorithm changed, and the playbook that worked in 2023 is bleeding you dry.

---

## Banned: Foil Framing (the "not X, but Y" tell)

The loudest AI-slop giveaway is defining yourself against a foil: describing what
others do, or what the thing isn't, so you look good by contrast. It is intellectually
lazy and instantly recognizable. Kill it on sight.

Every one of these is the same tell:

- **Negated category** — "Not a prompt pack. It's an operating system."
- **The strawman contrast** — "Most tools just ask a model to be careful. We run real gates."
- **The limit-negation** — "not just campaigns", "not only saved files"
- **The alternative-negation** — "instead of forcing an agency workflow on you"
- **The past-negation** — "no longer assumes", "the docs won't drift"
- **The fear-negation** — "marketing didn't get thinner", "nothing was removed"
- **Visual foils** — struck-through options, a "before" column that is really a strawman

State the strength directly. If the contrast is real, a strong enough positive claim
makes the reader feel it without you naming the foil.

| Foil (cut it) | Direct (ship it) |
|---------------|-------------------|
| Not a prompt pack. It's an operating system. | An operating system you install to run your back office. |
| Most tools just ask a model to be careful. We run gates. | The gate blocks bad work in code, before you read it. |
| Marketing didn't get thinner. | The marketing engine is the core, and 3.5 deepened it. |
| No cut-down editions. Nothing is removed. | Everyone gets the complete vault, tuned to their business. |
| It's not about features, it's about outcomes. | Requested Tuesday, paid Wednesday. Thirty-one hours. |

**The one exception: honest limitation disclosure about your OWN product.** "The
deterministic floor only catches known patterns" tells the truth about your own limits.
That is credibility, and it is welcome. Knocking a strawman to inflate yourself is the
slop. The difference is whether the thing you name is your own real limit or someone
else's caricatured weakness.

---

## The Three-Beat Structure (why we're good · what happened · the improvements)

Every announcement, release note, launch, or positioning block runs this order, and
every beat is affirmative:

1. **Why we're good** — the strength, stated as one concrete, ownable, falsifiable fact.
   Open here. Never open on the competitor, the old way, or what the thing is not.
2. **What happened** — the specific event or change, told straight (the changelog beat):
   what shipped, what moved, the real number.
3. **The improvements, laid out** — the member-facing wins, each one concrete and named.

If a draft opens by describing what other things do, rewrite the opening. The reader
came for you. Lead with you.

---

## Banned: Rhetorical Question Stacking

One rhetorical question to open a section is fine. Three in a row is AI writing.

---

## Do Instead

1. **Specificity beats generality.** "Increased revenue by 340% in 90 days" > "significantly improved results"
2. **Proof beats claims.** Back assertions with data, case studies, or third-party validation.
3. **One idea per sentence.** Two ideas in one sentence? Split it.
4. **Lead with the outcome.** Reader cares about what they GET, not what you DO.
5. **Cut the first paragraph.** In 80% of cases, the real copy starts at paragraph 2.
6. **Name the enemy.** Great copy has a villain (the old way, the competitor, the broken system).
7. **Stack proof in threes.** One proof point = anecdote. Two = coincidence. Three = pattern.

---

## The Three-Test (run on every line: visualize · falsify · own)

Before any line, headline, or claim ships, it must pass all three. Fail one, and you cut it or sharpen it. This is the Ogilvy/Schwartz standard turned into a checklist (the Rolls-Royce "at 60 mph the loudest noise is the electric clock" line passes all three).

1. **Can the reader visualize it?** They can see it in their mind. Concrete and sensory, not abstract.
   - "win a prize" → "strap on a Rolex you didn't pay a dollar for"
   - "fast payouts" → "requested Tuesday, paid Wednesday, 31 hours"
2. **Can it be falsified?** A specific, checkable claim, not vague puffery. A claim that *could* be proven false is believable; one that can't be tested gets ignored.
   - "the best platform" → "a full depth-of-market ladder on live CME data"
   - "great support" → "answered in the Discord in under an hour"
3. **Can nobody else say it?** It's ownable. If a competitor could paste their logo on the line, it is a category cliché. Kill it.
   - "200+ indicators" (every charting tool) → "the chart is your choice, not ours"
   - "get funded fast" → "one trader in this community owns a Rolex by August"

Lines that pass all three are vivid, credible, and unmistakably yours. That is the whole game. It is a judgment filter, not a regex, so it lives here in doctrine, run by the writer on every pass.

---

## Specificity Score + Proof-Source Gate (enforced, Wave 4)

The three-test is judgment; these are its deterministic backstops in
`Scripts/validation/deliverable_gate.py`. They never fabricate — they ENFORCE that
real proof is attached and flag copy that reads generic.

- **Specificity is scored, not just spot-checked.** The gate scores concrete-noun
  density against vagueness (dates, numbers, names, timestamps, real artifacts push
  the score up; puffery pushes it down). Low-specificity copy is surfaced as a review
  finding — it reads generic and fails the three-test 'falsify' leg. Vague/unfalsifiable
  lines ("unlock your potential", "take it to the next level", "world-class",
  "supercharge your growth") are named individually to sharpen.
- **The poster-on-a-gradient default is flagged** even when a creative is described in
  copy — it is the creative-execution-bar HARD FAIL, so the same bar applies to text.
- **Proof-source is required for every factual/number/outcome claim.** This is the
  SEMANTIC layer over the syntactic citation check: a real number/result needs real
  backing (a `Source:` line, a dataset, a screenshot, a footnote), not just a bracket
  nearby. A claim with no concrete proof source is surfaced by name so you attach the
  source or cut the claim. **Never invent a source to clear it.**

Model-based adversarial critique is the real answer to "is this claim actually true?"
that regex cannot reach — see `Skills/conventions/adversarial-critique.md`.

## Validation Script

```bash
python3 Scripts/validation/verify_copy.py [file_path]
# universal quality layer (specificity score + proof-source + no-fabrication):
python3 Scripts/validation/deliverable_gate.py --type <type> [file_path]
```

Run these on every deliverable before presenting to the user.
