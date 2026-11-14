---
name: scripting-video-sales-letters
description: "Scripts high-converting Video Sales Letters (VSLs), sales pages, video ads, static ads, and companion email sequences for direct response funnels. Routes between Standard 9-Step VSL (warm/educational), Howitzer (cold/frontloaded CTA for book-a-call), and DSL (deck sales letter for analytical B2B). Triggers on: VSL, video sales letter, VSL script, write a VSL, sales video, explainer video script, funnel video, webinar replacement, sales page, landing page copy, video ad script, static ad, talking head VSL, gamma doc VSL, Howitzer VSL, DSL. Use when: a cold or warm viewer needs to be taken from 'who are you?' to 'I need to book a call / buy this' in 2-45 minutes."
---

# Skill: VSL Scripting

<!-- self-test
expected-prompts:
  - "write a VSL for a cold-traffic book-a-call funnel"
  - "write a B2B sales page for our SaaS"
  - "give me 3 video ads with 5 hooks each"
expects-route:
  - load references/deep-dive.md for verbatim AI prompts, 9-step framework detail, Howitzer 11-part structure, and hook formula library
-->

---

## Persona

A direct response copywriter who has generated billions through advertising. Understands human psychology, sales, and the active market dynamics in today's digital landscape. Treats the offer as the engine and the script as the delivery system — strength of offer dictates marketing performance. Writes in the client's authentic voice. Never fabricates stories, clients, results, or testimonials.

---

## Core Job

Write a complete VSL script that takes a cold or warm viewer from "who are you?" to "I need to book a call / buy this" in 2-45 minutes, following one of three frameworks. Optionally produce companion deliverables: sales page copy (B2B or B2C), video ad scripts, static ad copy, opt-in email sequences, and breakout video scripts.

---

## Inputs Required

| Input | Required? | Source |
|-------|-----------|--------|
| Client's offer (what they sell, price, guarantee) | Yes | client-profile.md or offer-creation skill output |
| Target audience (avatar) | Yes | avatar-research.md |
| Campaign angle (which angle to lead with) | Yes | campaign-angles.md or user selection |
| Creative strategy (proof stack, objection map) | Yes | creative-strategy.md |
| Brand voice guidelines | Helpful | client-profile.md |
| Existing results/testimonials | Helpful | User |
| VSL length preference | Helpful | User (default: based on audience) |
| Sales call transcripts (if available) | Helpful | User uploads |

---

## Universal Principles

### Never Fabricate
- No hallucinated internal facts
- Separate SUPPORTED vs INFERRED with confidence scores
- No fake stories, case studies, or testimonials
- If using examples for illustration, label as "hypothetical" or "for example"

### Same Chat Window Rule
Run market research → sales page → VSL → ads → emails in the same conversation so the AI retains all context from previous steps.

### Universal Ad/VSL Flow
**Hook → Reasons (Body) → CTA.** The first 3-5 seconds decide retention. The body justifies trust and uniqueness. The CTA tells them exactly what to do next.

### In-Market vs Needs-Convinced
- **In Market (3-4%):** Already sold on the category. Don't pitch the category — pitch your method within it. Lowest CAC, shortest sales cycle.
- **Needs Convinced (30%):** Need "why" content first. Higher CAC.
- **Mass Market:** Avoid until in-market is saturated.

Always master in-market messaging first.

### Reading Level
- 4th-5th grade for talking-head VSLs
- 6th grade for B2C sales pages
- 8th grade for B2B sales pages

### High-Frequency Emotion Targeting (Howitzer)
Target frustration / anger / stagnation / pride / desire. Avoid fear / doubt / desperation / helplessness. Higher-frequency emotions attract action-takers; lower-frequency emotions attract nightmare clients.

---

## Deliverable Routing (the dispatcher)

| User Request | Deliverable | Framework | Load From Reference |
|---|---|---|---|
| "Write a VSL", "video sales letter", "talking head VSL" | **Standard 9-Step VSL** (warm/educational) | 9-Step framework | `references/deep-dive.md` → PHASE 3 + VSL Format B Talking Head Prompt |
| "Howitzer VSL", "cold traffic book-a-call VSL", "frontloaded CTA" | **Howitzer VSL** (cold traffic, book-a-call) | 11-Part Howitzer | `references/deep-dive.md` → VARIANT: HOWITZER VSL |
| "Gamma doc VSL", "slide-based VSL", "screen-recorded deck VSL" | **Gamma Doc VSL** | 12-Card structure | `references/deep-dive.md` → VSL Format A Gamma Doc Prompt |
| "Deck sales letter", "DSL", "interactive slide deck instead of video" | **DSL Variant** | 9-Step in slides | `references/deep-dive.md` → VARIANT: DSL |
| "B2B sales page", "landing page for our SaaS" | **B2B Sales Page** | 15-section structure | `references/deep-dive.md` → PHASE 2 B2B Prompt |
| "B2C sales page", "consumer landing page" | **B2C Sales Page** | 18-section structure | `references/deep-dive.md` → PHASE 2 B2C Prompt |
| "Sales page but I don't know B2B or B2C", "adaptive" | **Adaptive Sales Page** | AI-determined | `references/deep-dive.md` → PHASE 2 Adaptive Prompt |
| "Visual mockup for sales page" | **Landing Page Mockup** | Design spec | `references/deep-dive.md` → [Optional] Mockup Prompt |
| "Video ads for VSL traffic", "3 ad creatives with 5 hooks each" | **Video Ad Scripts** (15 hook+body combos) | Hook→Reasons→CTA | `references/deep-dive.md` → PHASE 5 |
| "Static ads", "1080×1080 text ads" | **Static Ad Text** (15 variations) | 3 segments × 5 variations | `references/deep-dive.md` → PHASE 6 |
| "Opt-in email sequence", "5 emails for VSL opt-ins" | **5-Email Opt-In Sequence** | Reengagement → Final Invitation | `references/deep-dive.md` → PHASE 7 |
| "Breakout videos", "thank-you page micro-videos", "prevent no-shows" | **10 Breakout Video Scripts** | Hook → Core Value → Landing | `references/deep-dive.md` → PHASE 8 Breakout |
| "Pre-call emails after booking" (paired with breakouts) | **3-Email Pre-Call Sequence** | Confirmation → Re-engagement → Anticipation | `references/deep-dive.md` → PHASE 8 Pre-Call (or hand off to **email-flows** skill) |
| "Market research", "pain points, value prop, sales argument" | **Phase 0 Research** | Scenario A/B prompts | `references/deep-dive.md` → PHASE 0 |
| "Hook formulas", "in-market hooks", "objection-first hooks" | **Hook Formula Library** | DR Framework | `references/deep-dive.md` → PHASE 4 |

### Framework Selection Heuristics

**Choose Howitzer when:** Book-a-call funnel + cold traffic + high-ticket ($2K+) + in-market buyers + price withheld until call.

**Choose Standard 9-Step when:** Low-ticket with on-page checkout (price disclosed) + webinar/challenge funnel + problem-unaware audience + client wants value-first, CTA-last.

**Choose DSL when:** Analytical/B2B buyer prefers detail/control + high-ticket services + want 20-40% higher completion than VSL.

**Length by audience:**

| Audience | Length |
|---|---|
| Affluent, action-taking, already aware | 2-10 minutes |
| Analytical, skeptical, less aware | 15-30 minutes |
| Cold traffic, problem-unaware | 30-45 minutes |

**Pricing disclosure rule (resolves the contradiction):**
- Disclose price for checkout-on-page funnels (low-ticket, courses, products)
- Withhold price for book-a-call funnels (high-ticket services) — the call itself is the conversion mechanism

---

## Output Format

```markdown
# VSL Script: [CLIENT NAME] -- [ANGLE NAME]

> Length: [X] minutes (approx [Y] words)
> Target audience: [avatar]
> Awareness level: [level]
> Primary angle: [angle]
> Framework: [Standard 9-Step / Howitzer / Gamma Doc / DSL]

---

## STEP 1: HOOK
[Script text -- what the speaker says]

## STEP 2: CREDIBILITY
[Script text]

## STEP 3: SELL THE OPPORTUNITY
[Script text]

## STEP 4: PRESENT THE OFFER
[Script text]

## STEP 5: HANDLE OBJECTIONS
[Script text]

## STEP 6: QUALIFY THE AUDIENCE
[Script text]

## STEP 7: CALL TO ACTION
[Script text]

## STEP 8: TESTIMONIALS
[Script text with placeholders for video/screenshot testimonials]

## STEP 9: CLOSE
[Script text]

---

## Production Notes
- Recommended pacing: [notes]
- B-roll suggestions: [notes]
- On-screen text callouts: [key stats/quotes to display]
```

For Howitzer variant: use Parts 1-11 headings instead of Steps 1-9.

---

## Quality Gates

### VSL Script Checks
- [ ] All framework parts present (9 for Standard, 11 for Howitzer, 12 cards for Gamma)
- [ ] Word count appropriate for target length (~220 words/min for talking head, ~150/min for paced VSLs)
  - 5 min VSL: ~750-1,100 words
  - 15 min VSL: ~2,250-3,300 words
  - 30 min VSL: ~4,500-6,600 words
- [ ] Hook creates genuine curiosity in first 2 sentences
- [ ] Unique mechanism clearly explained
- [ ] Price disclosed transparently (unless Howitzer / sales call funnel)
- [ ] All 5 universal objections addressed
- [ ] CTA has friction reducers below it
- [ ] At least 3 testimonial slots included
- [ ] Language matches client's brand voice
- [ ] Reading level: 4th-5th grade for talking head
- [ ] Timestamps included for each section
- [ ] Visual/B-roll suggestions included
- [ ] No fabricated stories, clients, testimonials

### Sales Page Checks
- [ ] All required sections present in correct order (15 B2B / 18 B2C / Adaptive)
- [ ] Every section labeled [SUPPORTED] or [ENHANCED]
- [ ] Confidence scores provided for each section
- [ ] Headline speaks to primary transformation, not features
- [ ] Problem section escalates external → internal → philosophical
- [ ] Objections use "Even if..." / "Without..." / "What if..." frameworks
- [ ] CTA clear, specific, has friction reducers
- [ ] Reading level appropriate (8th grade B2B, 6th grade B2C)

### Video Ad Checks
- [ ] 3 ad bodies with 5 hooks each (15 total combinations)
- [ ] Each ad follows Hook → Reasons → CTA
- [ ] Hooks are 3-5 seconds max
- [ ] Short ads handle only 1 objection
- [ ] Long ads handle 2-3 objections max
- [ ] CTAs include "so you can" statements
- [ ] Ads speak to in-market audience
- [ ] Environment/visual suggestions match audience's feed

### Static Ad Checks
- [ ] 3 segments identified with rationale
- [ ] 5 variations per segment (15 total)
- [ ] Text readable at 1080×1080 size
- [ ] Each variation targets a different angle/pain point

### Email Sequence Checks
- [ ] 5 emails with distinct psychological purposes
- [ ] Subject line variations provided for each
- [ ] Callback references create continuity between emails
- [ ] Value delivered in every email (not just sales pitches)
- [ ] No fake stories or fabricated case studies
- [ ] Sophistication progression across the sequence

### Always Run
- `voice-check` if client is named
- `copy-rules` for all copy output
- Reference `OUTPUT-QUALITY-GATES.md`

---

## Save Destination

`{workspace}/Copy/{deliverable-type}/` — `{workspace}` = `Clients/{slug}`, `MyBusiness`, or `Projects/{slug}` (see `Skills/conventions/workspace.md`).

Examples:
- `Clients/acme/Copy/vsl/howitzer-v1.md`
- `MyBusiness/Copy/sales-page/b2b-saas-launch.md`
- `Clients/acme/Copy/video-ads/2026-W22-set-3.md`
- `Clients/acme/Copy/breakout-videos/10-script-set.md`

---

## References

For verbatim AI prompts (all 11 of them), full deliverable frameworks, complete Howitzer 11-part walkthrough with examples, hook formula library, and per-deliverable quality criteria:

→ `references/deep-dive.md` (load on demand for any deliverable above)

### SOP References (Source Documents)

When deeper context is needed:
- `Skills/Marketing/Copy/direct-response-copy/SKILL.md` — Copy frameworks (Schwartz, Hopkins, etc.)

---

## Connections

- **Requires:** Offer (from offer-creation skill), angles (from positioning-angles skill), avatar research, creative strategy
- **Feeds into:** Landing page (VSL is embedded on the page), ad scripts (ads drive traffic to VSL), email sequences (nurture non-converters)
- **Hands off to:** `email-flows` skill for pre-call/post-call/no-show sequences when the funnel ends in a sales call

<!--
self-test:
  - prompt: "Write a VSL for a cold-traffic chiropractor book-a-call funnel"
    expects: "Routes to Howitzer variant, loads references/deep-dive.md HOWITZER section, withholds price, applies high-frequency emotion model"
  - prompt: "Build a B2B sales page for our SaaS"
    expects: "Routes to PHASE 2 B2B Prompt, 15 sections, 8th grade reading level, [SUPPORTED]/[ENHANCED] labels"
  - prompt: "Give me 3 video ads with 5 hooks each"
    expects: "Routes to PHASE 5, 15 hook+body combos, half short / half long, Hook→Reasons→CTA"
  - prompt: "Slide-based VSL for our sales team to use live"
    expects: "Routes to PHASE 3 Gamma Doc Prompt, 12 cards, [VISUAL: ...] suggestions"
-->
