---
name: brand-positioning
description: "Build a complete brand positioning document that combines voice, angles, mechanism, and competitive differentiation into a single strategic output. Use when starting a new client engagement, repositioning an existing brand, entering a new market, or when campaigns feel undifferentiated. Triggers on: position my brand, competitive positioning, brand strategy, how do I differentiate, what makes us different, positioning document, brand positioning. Outputs a positioning document that feeds into direct-response-copy, meta-ad-strategy, landing-page, email-flows, and positioning-angles skills."
---

# Brand Positioning Skill

> Build a complete brand positioning document that combines voice, angles, mechanism, and competitive differentiation into a single strategic output.

Undifferentiated brands compete on price. Differentiated brands compete on value. The difference between a $500 offer and a $5,000 offer is rarely the product. It is the positioning around the product.

This skill produces a positioning document that tells you exactly where the brand sits in its market, why it is different, and how to communicate that difference across every channel.

---

## Before you start

**Required inputs:**
- `knowledge.md` (business context: offer, avatar, competitors, voice)
- Market research deliverables: competitor matrix, avatar profile, objection map (from the market-research skill)

**Optional but recommended:**
- Brand voice profile (from the brand-voice skill). If it exists, load it. If not, extract what you can from knowledge.md and available content.
- Positioning angles output (from the positioning-angles skill). If it exists, reference it. The positioning document will feed back INTO angles with sharper framing.

**If required inputs are missing:**
Say: "I need market research before building a positioning document. Without competitor data and avatar language, the positioning will be generic. Want me to run market research first?"

---

## Positioning Framework (6 Steps)

Follow every step in order. Do not skip. Do not compress. Each step builds on the one before it.

### Step 1: Load Context

Read these files and extract the relevant data before writing anything:

1. **knowledge.md** -- Pull: business name, niche, offer, price point, delivery model, avatar (WHO, PAIN, DESIRE, OBJECTION, FAILED SOLUTIONS), competitive landscape, unique mechanism, brand voice.
2. **Market research deliverables** -- Pull: competitor matrix (names, positioning, pricing, strengths, weaknesses), avatar profile (psychographics, day-in-the-life, buying triggers), objection map (ranked objections with frequency), voice-of-customer (direct quotes organized by pain, desire, objection).
3. **Brand voice profile** (if it exists) -- Pull: personality traits, tone spectrum, vocabulary patterns, do's and don'ts.
4. **Positioning angles** (if they exist) -- Pull: angle names, frameworks used, market sophistication assessment.

If the brand voice profile does not exist, extract what you can from knowledge.md's Brand Voice section and any content samples provided. Note in the output: "Voice summary based on knowledge.md inputs. A full voice extraction (brand-voice skill) would strengthen this section."

---

### Step 2: Market Position Analysis (Schwartz Sophistication)

**Reference:** `References/Positioning/schwartz-sophistication.md`

Determine which of the 5 stages of market sophistication the client's market is at. This is the single most important strategic decision in the positioning document. It dictates the entire messaging approach.

**How to determine the stage:**

Analyze the competitor matrix and market research for these signals:

**Stage 1 (Pioneer) signals:**
- Few or no direct competitors making similar claims
- Customers say "I didn't know that was possible"
- Sales conversations are mostly educational
- You are explaining what the category IS

**Stage 2 (Enlarger) signals:**
- Multiple competitors with similar promises
- Customers compare options and ask "why you vs. them?"
- Claims are escalating across the market (bigger numbers, faster timelines)
- Differentiation is mostly about magnitude, not approach

**Stage 3 (Mechanism) signals:**
- Customer skepticism is high
- "I've tried things like this before" is a common objection
- Competitors all sound the same to the buyer
- You need to explain WHY your approach works, not just WHAT it does

**Stage 4 (Mechanism Enlarger) signals:**
- Multiple competing mechanisms exist
- Proof, credibility, and data are the primary differentiators
- Customers research heavily before buying
- Reviews, testimonials, and third-party validation drive decisions

**Stage 5 (Identity) signals:**
- Brand loyalty matters more than features or mechanisms
- Customers identify with certain brands in the space
- Emotional and aspirational messaging dominates
- Features are commoditized. Differentiation comes through personality.

**Output for this step:**
- The stage number (1-5)
- The stage name
- 3-5 specific evidence points from the market research supporting this determination
- What this means for messaging: the specific approach this stage requires (simple claim, enlarged claim, mechanism introduction, mechanism proof, or identity/belonging)

**Example:**

> **Stage 3: Mechanism Introduction.** The online coaching market for B2B founders is saturated with "grow your business" promises. Competitors X, Y, and Z all claim "6-figure months" and "scale to $100K." Customer forum language shows high skepticism: "I've bought three courses and none of them worked" (Reddit r/Entrepreneur, 47 upvotes). The avatar profile confirms "failed solutions" include two coaching programs and a mastermind. This market needs a mechanism. Leading with a promise alone will be dismissed. Leading with WHY this approach works differently is the path.

---

### Step 3: Unique Mechanism Identification

**Reference:** `References/Positioning/unique-mechanism.md`

The mechanism is what makes the promise believable. In a Stage 3+ market, no mechanism means no differentiation.

**Step 3A: Check if a mechanism already exists**

Look in knowledge.md under "YOUR UNIQUE MECHANISM" and "POSITIONING." If the client already has a named mechanism, evaluate it against four criteria:

1. **Nameable** -- Does it have a proprietary name? ("The Profit Acceleration Method" passes. "Our proven process" fails.)
2. **Explainable in one sentence** -- Can you describe what it does and why it is different in a single sentence? If it takes a paragraph, it is too complex.
3. **Defensible** -- Could a competitor claim the exact same thing? If yes, it is not unique enough.
4. **Believable** -- Does it make the promise MORE believable? Does the prospect think "that makes sense" or "I have not tried that approach"?

If the existing mechanism passes all four criteria, use it and move on.

**Step 3B: If no mechanism exists (or the existing one is weak)**

Identify the mechanism using Todd Brown's three types:

**Type 1 -- Existing Mechanism (Named):**
Look at what the client actually does differently. Even small differences become mechanisms when named and positioned.
- What steps do they take that competitors skip?
- What sequence do they follow that is counterintuitive?
- What do they invest extra effort in?
- What is their process that produces the result?

Give it a proprietary name. Good names sound specific and benefit-oriented: "The StoryBrand Framework," "The Profit First Method," "The SPIN Selling System." Weak names sound generic: "Our approach," "The comprehensive method."

**Type 2 -- Unspoken Mechanism (Revealed):**
Look at what everyone in the industry does but nobody talks about. The first one to explain it owns it.
- What "behind the scenes" process is invisible to customers?
- What industry standard practice sounds impressive when explained?

**Type 3 -- Transubstantiated Mechanism (Innovated):**
The client has genuinely built something new. A proprietary process, framework, technology, or methodology that competitors cannot claim.
- Document it
- Name it
- Make it central to the positioning

**Output for this step:**
- Mechanism type (1, 2, or 3)
- Mechanism name (proprietary, specific, memorable)
- One-sentence explanation of what it does and why it is different
- Why it is believable (the "because" statement -- the reason it works)
- How it passes the four criteria (nameable, explainable, defensible, believable)

**Example:**

> **Name:** The Revenue Architecture Method
> **Type:** 1 (Existing, Named)
> **One-Sentence Explanation:** A 4-phase build sequence that installs your complete sales system (ads, funnel, emails, sales process) in dependency order so each piece amplifies the next, instead of building disconnected marketing pieces that compete with each other.
> **Why It Is Believable:** Most agencies build ads OR funnels OR emails in isolation. The dependency-order approach explains why those isolated pieces fail and gives the prospect a reason to believe this approach will produce a different result.
> **Criteria Check:** Nameable (yes), Explainable in one sentence (yes), Defensible (competitors cannot claim the same 4-phase dependency sequence without copying), Believable (addresses the "I've hired agencies before" objection directly).

---

### Step 4: Competitive Positioning (Dunford 5-Component Model)

**Reference:** `References/Positioning/dunford-positioning.md`

April Dunford's model forces specificity. Each component connects to the others. Fill in all five with data from the client's business and the competitor matrix. No generic answers.

**Component 1: Competitive Alternatives**

What would customers use if this solution did not exist? This is broader than "competitors." Include:
- Do nothing (live with the problem)
- DIY / manual workaround (spreadsheet, free tools, figure it out themselves)
- Hire someone different (agency, freelancer, consultant in a different category)
- Use a completely different type of solution
- Use a direct competitor

Rank by how often customers actually consider each alternative. Pull this from the avatar profile's "FAILED SOLUTIONS" and the objection map.

**Component 2: Unique Attributes**

What does this offer have that alternatives do not? Pull from knowledge.md and the mechanism work in Step 3. List everything genuinely different:
- Features or capabilities
- Methodology or approach (the mechanism)
- Business model (pricing, delivery, guarantee)
- Team expertise or background
- Speed, depth, or format of delivery
- Partnerships, technology, or proprietary tools

Do not list "good customer service" or "high quality." Those are table stakes, not unique attributes.

**Component 3: Value**

What capability do those unique attributes enable for the customer? Translate every attribute into customer value using the "So What?" chain:

Attribute -> Functional Benefit -> Business Impact -> Emotional Payoff

Keep asking "so what?" until you hit something the customer feels.

Example: "4-phase dependency build" -> "Each marketing piece amplifies the next" -> "Higher ROAS because the system compounds instead of competing with itself" -> "You stop wondering if your marketing is working and start seeing predictable monthly revenue growth."

**Component 4: Target Customer**

Who cares MOST about the value identified in Component 3? This is not "everyone." This is the specific segment that would pay a premium for this specific differentiation.

Define them by:
- Role or title
- Company size or revenue range
- Specific situation (what is happening in their business right now)
- What they have already tried and why it failed
- Why they value YOUR specific differentiation over the alternatives

The narrower this is, the stronger the positioning. "Business owners" is weak. "B2B service founders doing $300K-$1M who have tried at least one agency and were disappointed by the results" is strong.

**Component 5: Market Category**

What context makes the value obvious? The category you claim sets expectations. Calling yourself a "marketing agency" triggers different assumptions than calling yourself a "Revenue Architecture firm."

Three options:
- Existing category (compete within an established space)
- Adjacent category (borrow from a related space)
- New category (create your own frame)

Choose the category that makes your unique value self-evident. If your differentiation disappears in the category you pick, pick a different category.

**Output for this step:**
Fill in all 5 components with specifics. No placeholders. No generic language. Every answer must reference actual data from the client's business and research.

---

### Step 5: Brand Position Synthesis

Combine Steps 2-4 into a unified positioning output.

**5A: One-Line Positioning Statement**

Write a single sentence that captures the positioning. Use this structure:

"We help [target customer from Component 4] achieve [specific outcome from Component 3] through [unique mechanism from Step 3], unlike [top competitive alternative from Component 1] which [their specific limitation]."

Rules:
- Under 30 words
- Must include the mechanism name
- Must name a specific outcome (with numbers if possible)
- Must name what the alternative gets wrong

Test: Read it to someone unfamiliar with the business. If they can explain what makes this different after hearing it once, it works.

**5B: Brand Personality Traits**

Pull from the brand voice profile (if loaded) or knowledge.md's Brand Voice section. List 3-5 personality traits with what each means in practice.

Format:
- **[Trait]:** [What this looks like in actual content. One sentence.]

Example:
- **Direct:** States the point in the first sentence. No warm-up paragraphs. No hedging.
- **Data-grounded:** Every claim includes a number. Revenue figures, timelines, percentages. Never vague.

**5C: Positioning Angles (3-5)**

Identify 3-5 distinct angles that can be used across different channels. Each angle is a different way to communicate the same core positioning.

For each angle, specify:
- Angle name
- Where it works best (ads, sales pages, emails, social, sales calls)
- Why it works (which psychological trigger or market condition it activates)
- Example headline or hook using this angle

Pull from the positioning-angles output if it exists. If not, build angles from the Schwartz stage determination (Step 2) and the mechanism (Step 3).

**5D: Brand Archetype Identification**


Using [CREATOR_NAME]'s brand measurement framework (reach, influence, direction), identify where the client currently sits and where they should aim. Determine which of the eight brand positions they currently occupy and which position they should target.

Then identify the brand archetype that fits their positioning:
- Are they the Expert (authority, credentials, data)?
- Are they the Peer (been there, sharing what worked)?
- Are they the Rebel (against the establishment, contrarian)?
- Are they the Guide (Sherpa model, walking alongside the customer)?
- Are they the Insider (access, exclusivity, behind-the-scenes)?
- Are they the Builder (showing the work, transparent process)?
- Are they the Educator (simplifying complexity, making knowledge accessible)?
- Are they the Provocateur (challenging assumptions, strong opinions)?

Select the archetype that aligns with the brand voice AND the target customer's preferences. The archetype must feel authentic to the founder's personality AND appealing to the avatar.

---

### Step 6: Competitive Positioning Map

Create a text-based positioning map that shows where the client sits relative to competitors.

**How to build it:**

1. Choose two axes:
   - X-axis: Price (low to high). This is almost always one axis.
   - Y-axis: The client's primary differentiator. This should be the dimension where the client wins. Examples: "Done-for-you vs. DIY," "Speed of results (slow to fast)," "Customization (template to bespoke)," "Depth of service (surface to comprehensive)."

2. Plot 3-5 competitors and the client on both axes. Use the competitor matrix data.

3. Identify the "open space." Where is the map empty? Is there a quadrant with no competitors? That is a potential positioning opportunity.

4. State the strategic implication: Given where the competitors cluster and where the open space is, where should the client position? Is the current position defensible? Should they move?

**Output format:**

```
COMPETITIVE POSITIONING MAP

Y-axis: [Differentiator] (Low -> High)
X-axis: Price (Low -> High)

High [Differentiator]
  |
  |  [Client Name] *
  |                        [Competitor C]
  |
  |     [Competitor A]
  |
  |                  [Competitor B]
  |        [Competitor D]
  |
Low [Differentiator]
  +------------------------------------
  Low Price                    High Price

OPEN SPACE: [Description of the unoccupied quadrant or area]
STRATEGIC IMPLICATION: [What this means for the client's positioning]
```

---

## Output Format

The deliverable is a single structured document. Every section must be filled with client-specific data. No placeholders. No "insert here" notes.

```
# [Brand Name] Positioning Document

## Positioning Statement
[One sentence, under 30 words. Includes mechanism name, target customer, specific outcome, and competitive contrast.]

## Market Sophistication Stage
**Stage [X]: [Stage Name]**
[2-3 sentences explaining the determination.]

**Evidence:**
- [Evidence point 1 from market research]
- [Evidence point 2 from competitor analysis]
- [Evidence point 3 from voice-of-customer data]

**Messaging implication:** [What this stage requires: simple claim, enlarged claim, mechanism, mechanism proof, or identity.]

## Unique Mechanism
**Name:** [Proprietary mechanism name]
**Type:** [1: Named, 2: Revealed, or 3: Innovated]
**One-Sentence Explanation:** [What it does differently and why]
**Why It Is Believable:** [The "because" -- the logical reason this approach produces different results]

## Dunford 5-Component Positioning

| Component | Details |
|-----------|---------|
| Competitive Alternatives | [What they would use instead -- ranked by frequency] |
| Unique Attributes | [What this offer has that alternatives do not -- specific, not generic] |
| Value | [The capability those attributes enable -- translated to customer impact] |
| Target Customer | [Who cares most -- specific segment with situation, not demographics alone] |
| Market Category | [The context that makes the value obvious -- existing, adjacent, or new] |

## Brand Voice Summary
[3-5 personality traits with explanations. Tone spectrum position. Key vocabulary patterns. Reference the full voice profile if one exists.]

## Brand Archetype
**Primary:** [Archetype name]
**Why this fits:** [1-2 sentences connecting the archetype to the founder's personality AND the avatar's preferences.]

## Positioning Angles

1. **[Angle name]** -- Best for: [channel/format] -- Why it works: [psychological trigger or market condition] -- Example: "[Sample headline or hook]"
2. **[Angle name]** -- Best for: [channel/format] -- Why it works: [psychological trigger or market condition] -- Example: "[Sample headline or hook]"
3. **[Angle name]** -- Best for: [channel/format] -- Why it works: [psychological trigger or market condition] -- Example: "[Sample headline or hook]"
4. **[Angle name]** -- Best for: [channel/format] -- Why it works: [psychological trigger or market condition] -- Example: "[Sample headline or hook]"
5. **[Angle name]** -- Best for: [channel/format] -- Why it works: [psychological trigger or market condition] -- Example: "[Sample headline or hook]"

## Competitive Map
[Text-based positioning map with axes, competitor plots, open space identification, and strategic implication.]

## Implementation Guide

**Headlines that reflect this positioning:**
- [Headline 1 -- uses the mechanism name and targets the specific avatar]
- [Headline 2 -- uses the competitive contrast angle]
- [Headline 3 -- uses the identity/aspiration angle]

**Ad hooks that use the mechanism:**
- [Hook 1 -- opens with the mechanism as the differentiator]
- [Hook 2 -- opens with the problem the mechanism solves]
- [Hook 3 -- opens with proof that the mechanism works]

**Email subject lines that reinforce the position:**
- [Subject line 1 -- curiosity-driven, references the mechanism]
- [Subject line 2 -- contrarian, challenges the alternative approach]
- [Subject line 3 -- proof-driven, leads with a result]
```

---

## Quality Gates

Run these checks before delivering the positioning document. If any check fails, fix it before delivery.

- [ ] Positioning statement is one sentence, under 30 words
- [ ] Positioning statement includes: target customer, specific outcome, mechanism name, and competitive contrast
- [ ] Schwartz stage determination includes 3+ specific evidence points from research (not assumptions)
- [ ] Unique mechanism is named with a proprietary name (not "our approach" or "our method")
- [ ] Unique mechanism is explainable in one sentence
- [ ] Unique mechanism passes all four criteria: nameable, explainable, defensible, believable
- [ ] All 5 Dunford components filled with client-specific details (not generic placeholders)
- [ ] Target customer segment is specific enough that you could find them on one platform
- [ ] At least 3 positioning angles with specific use cases and example headlines
- [ ] Each angle specifies WHERE to use it (ads, email, sales page, social, calls)
- [ ] Competitive map includes 3+ competitors with clear axis labels
- [ ] Open space on the competitive map is identified with a strategic implication
- [ ] Implementation examples use language from knowledge.md and the voice profile (not generic marketing speak)
- [ ] Zero em dashes in the entire document
- [ ] Zero banned AI phrases ("leverage," "dive deep," "game-changer," "seamless," "cutting-edge," etc.)
- [ ] All claims reference specific data from market research, not assumptions

---

## Supporting References

| Reference | What It Adds | When to Load |
|-----------|-------------|-------------|
| `References/Positioning/dunford-positioning.md` | 5-component positioning model: competitive alternatives, unique attributes, value, target customer, market category | Always. This is the core competitive positioning framework. |
| `References/Positioning/unique-mechanism.md` | Todd Brown's mechanism methodology: 3 types, naming criteria, believability testing, language patterns | Always. The mechanism is central to the positioning document. |
| `References/Positioning/schwartz-sophistication.md` | 5 stages of market sophistication: what messaging approach works at each stage, signal detection for each stage | Always. The stage determines the entire messaging strategy. |
| `references/creator-branding.md` | 8 brand positions (reach/influence/direction matrix), 4-step brand building process, 5 expansion directions, brand-to-sales bridge | Always. Used for archetype identification and strategic brand direction. |

---

## Cross-Skill Integration

**This skill feeds INTO:**
- `direct-response-copy.md` -- The positioning statement and mechanism become the headline framework. The competitive contrast becomes the "unlike" section in sales copy.
- `meta-ad-strategy.md` -- Positioning angles become ad hooks. The mechanism becomes the ad's "why this is different" section. The Schwartz stage determines the ad's structure (claim vs. mechanism vs. identity).
- `landing-page.md` -- The positioning drives the above-the-fold messaging, the hero section, and the competitive comparison section.
- `email-flows.md` -- The brand voice carries through every email. The mechanism becomes the nurture sequence's educational backbone.
- `positioning-angles.md` -- The positioning document sharpens angle creation by providing the strategic foundation (stage, mechanism, competitive frame) that angles build on.
- `vsl-scripting.md` -- The mechanism becomes VSL Step 3 (Solution Introduction). The competitive positioning informs Step 4 (Credibility).
- `offer-creation.md` -- The Dunford value component translates directly into how the offer stack is presented.

**This skill feeds FROM:**
- `market-research.md` -- Competitor matrix, avatar profile, voice-of-customer data, and objection map are required inputs.
- `brand-voice.md` -- Voice profile provides personality traits, tone spectrum, and vocabulary patterns for the Brand Voice Summary section.
- `positioning-angles.md` -- If angles already exist, they inform the Positioning Angles section and provide a cross-check on the Schwartz stage.

---

## When to revisit

The positioning document is not permanent. Revisit it when:
- The competitive landscape shifts (new competitor enters, existing competitor pivots)
- The offer changes significantly (new price point, new delivery model, new features)
- Campaign performance data shows the current positioning is not resonating (low CTR on mechanism-based hooks, high objection rates on sales calls)
- The target customer segment changes (moving upmarket, downmarket, or adjacent)
- The market sophistication stage advances (competitors start using mechanisms, requiring you to move to Stage 4 or 5)
- A new competitor claims a similar mechanism (requiring differentiation refinement)

---

## The test

A strong positioning document passes these five checks:

1. **Differentiated:** If you swap in a competitor's name, does the document stop making sense? If yes, the positioning is specific enough.
2. **Actionable:** Could a copywriter (human or AI) read this document and produce on-brand, differentiated copy without asking additional questions?
3. **Consistent:** Does every section point in the same direction? The mechanism, the angles, the voice, and the competitive map should all reinforce one unified position.
4. **Evidence-based:** Is every claim backed by market research data, competitor analysis, or customer language? If any section relies on assumptions, flag it.
5. **Memorable:** Can someone read the positioning statement once and repeat the core idea back to you? If it takes two readings, simplify.

If any answer is no, the document needs more specificity or a tighter strategic focus.
