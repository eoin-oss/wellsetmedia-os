# Email Flows Module

> Activates when `email-flows` is listed in knowledge.md `modules_active`.

## What This Module Adds

Deep email sequence architecture beyond the core SKILL.md protocol. SKILL.md covers the universal copywriting frameworks (awareness levels, market sophistication, headlines, proof pyramid, objection handling, CTAs). This module adds the format-specific methodology for email marketing: sequence types and their internal logic, trigger-based automation rules, subject line testing frameworks, cadence and timing rules per sequence type, segmentation strategy, deliverability hygiene, email copy structure, and personalization patterns. Built for email systems that nurture cold leads into buyers, retain existing customers, and recover lost revenue across 6 core sequence types.

## Sequence Types: Architecture and Purpose

Every email system is built from these 6 sequence types. Each has a distinct purpose, cadence, emotional arc, and copy approach. Mixing the rules across types is the fastest way to kill open rates and conversions.

### Sequence 1: Welcome Sequence (Post Opt-In)

**Purpose:** Convert a subscriber into an engaged reader within the first 72 hours. The welcome sequence sets expectations, delivers immediate value, and establishes the sender's voice and authority. This is the highest-engagement window you will ever have with this contact.

**Trigger:** New email subscriber via lead magnet, webinar registration, or list join.

**Cadence:**
- Email 1: Immediate (within 60 seconds of opt-in). Deliverability depends on this.
- Email 2: 24 hours after Email 1.
- Email 3: 48 hours after Email 1.
- Email 4: 72 hours after Email 1.
- Email 5 (optional): 96 hours. Only if the sequence bridges into a nurture or launch.

**Emotional arc across the sequence:**
```
Email 1: RELIEF + GRATITUDE  ████████░░ (8/10) -- they got what they asked for
Email 2: CURIOSITY            ███████░░░ (7/10) -- teach one thing, open a loop
Email 3: TRUST                ██████████ (10/10) -- deep value, proof stacking
Email 4: DESIRE               █████████░ (9/10) -- introduce the offer or next step
Email 5: URGENCY              ████████░░ (8/10) -- deadline or scarcity (if real)
```

**Email 1 structure (the delivery email):**
1. Subject line: Deliver on the promise. "[First Name], here's your [Lead Magnet Name]"
2. First line: Acknowledge the action they took. "You just signed up for [X]. Good move."
3. Deliver the asset: Direct download link. No hoops, no "but first" gates.
4. One-line value preview: Tell them the single most important thing inside the asset.
5. Set expectations: "Over the next few days, I'll send you [X]. These emails are short, specific, and built to help you [outcome]."
6. Sign-off: Name, one-line identity statement.

**Email 2 structure (the teaching email):**
1. Subject line: Curiosity or micro-result. "The one thing most [audience] get wrong about [topic]"
2. Open with a story or observation (2-3 sentences max).
3. Teach one actionable concept. Not three. One.
4. Connect the teaching to the lead magnet they downloaded.
5. Close with an open loop: "Tomorrow I'll show you [next concept], which is the piece most people miss."

**Email 3 structure (the proof email):**
1. Subject line: Result-driven. "[Client Name] did [result] in [timeframe]"
2. Tell a case study story. Name, situation, obstacle, mechanism used, result with numbers.
3. Connect the case study to the reader: "You have the same starting point [Client Name] did."
4. Soft CTA: Link to a resource, reply prompt, or content piece.

**Email 4 structure (the bridge email):**
1. Subject line: Transition signal. "The fastest way to [desired outcome]"
2. Recap the value delivered so far (1-2 sentences, not a summary essay).
3. Introduce the offer, program, or next step. Frame it as the logical next move.
4. CTA: Clear, specific, single action.

### Sequence 2: Nurture Sequence (Ongoing Relationship)

**Purpose:** Maintain engagement between purchase-ready moments. Nurture sequences keep the sender top-of-mind, build authority over time, and prime the subscriber for future offers. Most businesses skip this and only email when they want money. That pattern trains subscribers to ignore you.

**Trigger:** Subscriber completes welcome sequence without purchasing, or is added to the general list.

**Cadence:**
- 2-3 emails per week for engaged lists (open rate above 25%).
- 1-2 emails per week for colder lists (open rate 15-25%).
- 1 email per week minimum. Below this frequency, subscribers forget who you are.

**Content rotation (cycle through these types):**
1. Teaching email: One concept, one takeaway, one application.
2. Story email: Personal narrative that demonstrates a principle.
3. Case study email: Client result with specifics.
4. Belief-shifting email: Challenge an assumption the audience holds.
5. Behind-the-scenes email: Process, decision-making, real numbers.
6. Curated value email: Resources, tools, frameworks from other sources (with commentary).

**Nurture rules:**
- Every 4th or 5th email can include a soft CTA to an offer. Not every email.
- Value-to-pitch ratio: 4:1 minimum. Four value emails for every one pitch email.
- Never send two pitch emails back to back. Always place a value email between them.
- Personalize the "from" name. First name only or first + last. Never a company name alone.

### Sequence 3: Launch Sequence (Time-Bound Campaign)

**Purpose:** Drive conversions during a defined launch window. Launch sequences create compressed urgency through a structured series that builds belief, handles objections, and closes with real deadlines.

**Trigger:** Manual campaign start, tied to a specific open/close date for an offer.

**Cadence:**
- Pre-launch (3-5 days before): 1 email per day. Seed the idea, build anticipation.
- Launch day: 2 emails. Morning announcement, evening reminder.
- Mid-launch (days 2-4): 1 email per day. Proof, objection handling, bonuses.
- Final day: 3 emails. Morning urgency, afternoon social proof, final hours countdown.

**Launch email sequence (7-day example):**
```
Day -3: Seed email       "Something's coming that I've been working on for [X months]"
Day -1: Teaser email     "Tomorrow at [time], I'm opening [Offer Name]"
Day 0 AM: Launch email   "It's live. Here's everything inside [Offer Name]"
Day 0 PM: Reminder       "In case you missed this morning's email..."
Day 2: Case study        "[Client Name]'s story (and why I built [Offer Name])"
Day 4: Objection email   "The #1 question I'm getting about [Offer Name]"
Day 5: Bonus stack       "I just added [Bonus] for everyone who joins by [deadline]"
Day 6 AM: Urgency        "[Offer Name] closes tomorrow at midnight"
Day 6 PM: Social proof   "[X] people joined this week. Here's what they're saying."
Day 7 AM: Final day      "Last chance: [Offer Name] closes tonight at midnight"
Day 7 PM: Final hours    "Closing in [X] hours. This is your last email about this."
```

**Launch rules:**
- Every deadline must be real. If the cart doesn't actually close, don't say it does.
- Remove purchasers from the launch sequence immediately after purchase. Continuing to sell to someone who already bought is the fastest way to get unsubscribes.
- Segment non-openers and send a re-engagement variation with a different subject line 6-12 hours after the original send.

### Sequence 4: Abandon Sequence (Cart/Application Recovery)

**Purpose:** Recover revenue from people who started the buying process but didn't finish. These subscribers are the warmest leads in the system. They demonstrated intent. Something stopped them.

**Trigger:** Cart abandon event, incomplete application, or checkout page exit without purchase.

**Cadence:**
- Email 1: 1 hour after abandon. Not 24 hours. One hour.
- Email 2: 24 hours after abandon.
- Email 3: 48 hours after abandon.
- Email 4 (optional): 72 hours. Only for high-ticket offers ($1,000+).

**Email 1 structure (the reminder):**
1. Subject line: Direct. "You left something behind" or "Your [Offer Name] is waiting"
2. No story. No teaching. Straight to the point: "You started [action] but didn't finish."
3. Address the most likely reason: technical issue. "If something went wrong with the page, here's a direct link."
4. CTA: Direct link back to the checkout page.

**Email 2 structure (the objection handler):**
1. Subject line: Question-based. "Was it the price?" or "Quick question about [Offer Name]"
2. Acknowledge that they were interested (they started the process).
3. Address the top 2 objections for this offer (price and timing are almost always in the top 3).
4. Restate the guarantee.
5. CTA: Direct link back to checkout.

**Email 3 structure (the proof push):**
1. Subject line: Social proof. "[Client Name] was on the fence too"
2. Tell a short case study of someone who hesitated, then joined, then got results.
3. Restate the offer in one sentence.
4. If applicable, add a time-limited incentive (bonus, payment plan, discount).
5. CTA: Direct link back to checkout.

### Sequence 5: Post-Purchase Sequence

**Purpose:** Reduce refund rates, increase consumption of the product, build loyalty, and set up the next purchase. Most businesses go silent after the sale. That silence creates buyer's remorse.

**Trigger:** Successful purchase or enrollment.

**Cadence:**
- Email 1: Immediate. Confirmation and onboarding.
- Email 2: 24 hours. Quick win guidance.
- Email 3: Day 3. Check-in and community connection.
- Email 4: Day 7. Progress check and deeper resource.
- Email 5: Day 14. Testimonial request or next offer tease.
- Email 6: Day 30. Results check and referral/upsell.

**Email 1 structure (confirmation + onboarding):**
1. Subject line: Celebration. "Welcome to [Offer Name]. Here's your first step."
2. Confirm what they purchased and what they now have access to.
3. Give them ONE action to take right now. Not five. One.
4. Set expectations: what emails they'll receive, when, and why.
5. Provide support contact information.

**Post-purchase rules:**
- Never pitch a new offer in the first 7 days. Let them consume what they bought.
- Day 14 is the earliest for a testimonial ask. Frame it as: "How's it going? If you've seen results, I'd love to hear about it."
- Day 30 is the earliest for an upsell. Frame it as: "Now that you've [result from first purchase], here's the next level."

### Sequence 6: Re-Engagement Sequence (Win-Back)

**Purpose:** Reactivate subscribers who have stopped opening emails. If they don't re-engage, remove them from the active list to protect deliverability.

**Trigger:** Subscriber has not opened or clicked in 60-90 days (adjust based on send frequency).

**Cadence:**
- Email 1: Day 1 of re-engagement window.
- Email 2: Day 4.
- Email 3: Day 7 (final email before removal).

**Email 1 structure (the check-in):**
1. Subject line: Personal and direct. "Still interested in [topic]?" or "[First Name], should I stop emailing you?"
2. Acknowledge the silence. "I noticed you haven't opened my last few emails."
3. Offer value: link to the single best resource or content piece.
4. Ask directly: "If you still want to hear from me, just click here."

**Email 3 structure (the breakup):**
1. Subject line: Finality. "Removing you from my list (unless...)"
2. State clearly: "If I don't hear from you, I'll remove you from my list in 48 hours."
3. One-click re-subscribe link.
4. No guilt. No manipulation. Respect their inbox.

**Re-engagement rules:**
- If a subscriber doesn't engage with any of the 3 emails, remove them. Do not keep cold subscribers on the list. They hurt deliverability for everyone.
- After removal, add them to a suppression list. Do not re-add unless they explicitly opt in again.

## Trigger Logic and Automation Rules

Every sequence is triggered by a specific event, not a calendar date. Build automations around these events.

**Event-to-sequence mapping:**

| Event | Sequence Triggered | Entry Condition | Exit Condition |
|-------|-------------------|-----------------|----------------|
| New subscriber | Welcome | Confirmed opt-in | Sequence complete or purchase |
| Welcome sequence complete (no purchase) | Nurture | Welcome Email 4+ sent | Purchase or unsubscribe |
| Cart/checkout abandon | Abandon | Checkout started, no payment | Purchase or sequence complete |
| Purchase | Post-purchase | Payment confirmed | Sequence complete |
| 60-90 days no engagement | Re-engagement | No opens or clicks | Re-engaged or removed |
| Launch date | Launch | Manual campaign trigger | Cart close date |

**Automation rules:**
1. A subscriber should never be in two selling sequences simultaneously. If they enter a launch sequence, pause their nurture sequence.
2. Purchase events override everything. If a subscriber buys mid-sequence, immediately move them to post-purchase. Remove them from all other active sequences.
3. Unsubscribe events are instant and permanent. Never re-add an unsubscribed contact to any sequence.
4. Tag every subscriber with their entry source (which lead magnet, which page, which ad). This data drives segmentation decisions.

## Subject Line A/B Testing Framework

Subject lines determine whether the email gets opened. Test them systematically, not randomly.

**Testing hierarchy (test in this order):**

1. **Personalization vs. no personalization:** "[First Name], your strategy is ready" vs. "Your strategy is ready." Test this first because it affects all future tests.
2. **Curiosity vs. benefit:** "The thing nobody tells you about [topic]" vs. "How to [achieve result] in [timeframe]." These are the two dominant subject line categories.
3. **Length:** Short (3-5 words) vs. medium (6-10 words). Short wins on mobile. Medium wins for specificity.
4. **Emoji vs. no emoji:** Test once. Apply the result globally. Don't re-test every campaign.
5. **Question vs. statement:** "Are you making this mistake?" vs. "The mistake that costs most [audience] $X/month."

**Testing rules:**
- Test one variable at a time. Changing two things means you learn nothing.
- Minimum sample size: 1,000 subscribers per variant, or 500 per variant if the list is under 5,000. Below 500, the data is noise.
- Wait 24 hours before declaring a winner. Early openers skew toward certain demographics.
- Track click-through rate alongside open rate. A subject line that gets opens but no clicks is clickbait, not good copy.

**Subject line formulas that consistently perform:**

| Formula | Example | Best For |
|---------|---------|----------|
| [Number] + [unexpected detail] | "3 emails that generated $47K last month" | Nurture, launch |
| [First Name] + direct question | "[Name], still thinking about this?" | Abandon, re-engagement |
| [Specific result] + [timeframe] | "$12K in 14 days (case study inside)" | Launch, proof emails |
| [Contrarian statement] | "Stop writing more content" | Nurture, belief-shifting |
| [Curiosity + specificity] | "The 11:47 PM email that changed everything" | Any sequence type |
| [Social proof lead] | "[Client Name] just hit $50K/month" | Launch, proof emails |

## Cadence Rules by Sequence Type

**Frequency guidelines:**

| Sequence | Min Frequency | Max Frequency | Danger Zone |
|----------|--------------|---------------|-------------|
| Welcome | 1x/day | 1x/day | More than 1x/day feels aggressive |
| Nurture | 1x/week | 3x/week | Less than 1x/week: forgotten. More than 4x/week: fatigue |
| Launch | 1x/day | 3x/day (final day only) | More than 2x/day outside final 48 hours |
| Abandon | 1 hour, 24h, 48h | 4 emails max | More than 4 emails feels desperate |
| Post-purchase | Day 0, 1, 3, 7, 14, 30 | 6 emails in 30 days | Pitching before Day 14 |
| Re-engagement | Every 3 days | 3 emails total | More than 3 emails to unengaged contacts |

**Send time guidelines:**
- B2B: Tuesday-Thursday, 8-10 AM recipient's timezone.
- B2C: Tuesday-Thursday, 10 AM-2 PM or 7-9 PM recipient's timezone.
- Launch emails: Send the first email of each day between 8-10 AM. Evening follow-ups at 7-8 PM.
- Abandon emails: Email 1 at 1 hour post-abandon (time of day irrelevant). Subsequent emails follow the B2C/B2B timing.

## Segmentation Strategy

Segmentation is the difference between "blasting your list" and "sending the right message to the right person." Start with these 4 segments and add complexity only when you have the data to support it.

**Tier 1 segments (implement immediately):**

| Segment | Definition | How to Treat Differently |
|---------|-----------|-------------------------|
| Buyers | Has purchased any offer | Exclude from cold selling sequences. Send post-purchase and upsell content. |
| Engaged non-buyers | Opens/clicks in last 30 days, no purchase | Primary target for launches and soft CTAs in nurture. |
| Cold subscribers | No opens/clicks in 60+ days | Re-engagement sequence only. Do not send launches. |
| New subscribers | Joined in last 14 days | Welcome sequence only. Do not add to launches until welcome is complete. |

**Tier 2 segments (implement when list exceeds 2,000):**

| Segment | Definition | How to Treat Differently |
|---------|-----------|-------------------------|
| Lead magnet source | Which opt-in they used | Customize nurture content to match the topic they opted in for. |
| Offer tier | Which product level they purchased | Upsell to next tier. Don't pitch what they already own. |
| Engagement level | High (opens 80%+), medium (30-80%), low (<30%) | Adjust send frequency: high gets 3x/week, medium 2x, low 1x. |

## Deliverability Best Practices

Copy quality is irrelevant if the email lands in spam. Follow these rules to protect sender reputation.

**Technical requirements:**
- SPF, DKIM, and DMARC records configured and passing. Non-negotiable.
- Custom sending domain (not @gmail.com or @outlook.com for marketing emails).
- Dedicated IP or reputable shared IP pool (platform-dependent).

**List hygiene rules:**
- Remove hard bounces immediately. Never retry a hard bounce.
- Remove soft bounces after 3 consecutive failures.
- Remove unengaged subscribers after the re-engagement sequence fails (see Sequence 6).
- Never purchase, rent, or scrape email lists. Every subscriber must have explicitly opted in.

**Content rules for deliverability:**
- Avoid spam trigger words in subject lines: "free," "guaranteed," "act now," "limited time." Use them sparingly in body copy.
- Maintain a text-to-image ratio of at least 60% text, 40% images. Text-only emails have the highest deliverability.
- Include a plain-text version of every HTML email.
- Always include a visible unsubscribe link. Making it hard to unsubscribe increases spam complaints.
- Keep the "from" name consistent. Changing it frequently confuses both subscribers and spam filters.

## Email Copy Structure

Every email, regardless of sequence type, follows this structure. Adapt the length and tone per sequence, but the bones remain the same.

**The Hook (first 1-2 lines):**
- Job: Get the reader past the preview text and into the body. This is the subject line's partner.
- Rule: First sentence under 10 words. Declarative, provocative, or story-opening.
- Pattern: "I almost deleted this email before sending it." / "Three numbers changed how I think about [topic]." / "$47,329. Thirty-seven days."

**The Body (3-8 paragraphs depending on sequence type):**
- One idea per email. Not two ideas. Not a comprehensive guide. One idea.
- Paragraphs: 1-3 sentences each. White space is your friend.
- Vary sentence length: short declarative, then a longer explanatory sentence, then another short one.
- Use bucket brigades between paragraphs: "Here's why that matters..." / "The result?" / "But it gets better."
- If teaching, give the complete framework or the actionable takeaway. Don't tease and gate.

**The CTA (final 2-3 lines):**
- One CTA per email. Multiple CTAs create decision paralysis and reduce click-through rate.
- State the CTA as a command verb + specific next step: "Click here to download the framework." Not "If you're interested, you might want to check this out."
- Place the CTA on its own line. Do not bury it in a paragraph.
- Repeat the CTA if the email is long (once mid-email, once at the end). Same link, can be different words.

**The Sign-Off:**
- First name only, or first name + one-line identity.
- No long signature blocks with social links, disclaimers, and phone numbers in marketing emails. Save that for transactional correspondence.

## Personalization Patterns

Personalization goes beyond [First Name]. These patterns use subscriber data to make emails feel individually written.

**Level 1: Merge tag personalization**
- First name in subject line and opening line.
- Company name in B2B emails.
- Lead magnet name in welcome sequence ("Since you downloaded [Lead Magnet Name]...")

**Level 2: Behavioral personalization**
- Reference their last action: "I noticed you checked out [Page Name] yesterday."
- Reference their engagement: "You've been opening every email this week, so I want to share something I don't usually send."
- Reference their inaction: "You haven't logged in to [Product] since [date]. Here's a quick win to get you back on track." (Post-purchase only.)

**Level 3: Segment-based personalization**
- Different email body for different segments viewing the same campaign.
- B2B vs. B2C language variants within the same launch sequence.
- Price-point variants: subscribers who have purchased $97 products get different framing than those who have purchased $2,000+ products.

**Personalization rules:**
- Never personalize with data you shouldn't have. If they didn't give you their company name, don't use it (even if you scraped it).
- If a merge field is empty, use a fallback. "[First Name]" with no data becomes "Hey there" or "Hi friend," never "[First Name]."
- Test personalized vs. non-personalized versions. Personalization usually wins, but not always. Some audiences find it invasive.

## Vault Resources

Load these files for deeper framework detail when writing email sequences:

- `Context/Marketing/Email/neo-email-matrix.md` -- Full email matrix methodology, sequence architecture, modal operator deployment
- `Skills/Marketing/Funnels/email-flows` -- Condensed email flow skill with step-by-step workflow
- `Skills/Marketing/Funnels/email-sequences` -- Sequence-specific templates and cadence rules

## Module-Specific Quality Standards

- [ ] Every email has a subject line AND preview text written
- [ ] Subject lines are under 50 characters (or intentionally long for contrast testing)
- [ ] Each email has exactly one CTA (not two, not zero)
- [ ] CTA is on its own line, not buried in a paragraph
- [ ] Welcome Email 1 delivers the asset immediately with no gates
- [ ] Welcome sequence sets expectations for future emails
- [ ] Nurture sequence maintains 4:1 value-to-pitch ratio minimum
- [ ] Launch sequence has real deadlines (not fabricated urgency)
- [ ] Abandon sequence Email 1 sends within 1 hour of the abandon event
- [ ] Post-purchase sequence does not pitch a new offer before Day 14
- [ ] Re-engagement sequence removes non-responders after 3 emails
- [ ] Purchasers are excluded from all selling sequences
- [ ] No subscriber is in two selling sequences simultaneously
- [ ] Send times match audience type (B2B vs. B2C guidelines)
- [ ] Personalization merge fields have fallback values for empty data
- [ ] Emotional arc is mapped for each sequence (not flat energy throughout)

---

> **[COMPANY_NAME] Copywriter Agent v2.0 -- Email Flows Module**
> Created by [AUTHOR_NAME], [COMPANY_NAME] ([company_domain])
> All rights reserved. Unauthorized reproduction or distribution prohibited.
