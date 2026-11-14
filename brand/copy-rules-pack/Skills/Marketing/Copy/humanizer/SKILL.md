---
name: humanizer
description: "Use when copy sounds generic, over-polished, AI-written, corporate, stiff, or unlike the founder/client voice. Triggers include: humanize this copy, make this sound less AI, make this sound like me, remove AI smell, make this more natural, add voice, rewrite in human voice, make it less generic. Preserves the original claim set while improving specificity, rhythm, proof, and voice."
metadata:
  version: 1.0.0
  status: draft
---

# Copy Humanizer

Humanizing copy is not sprinkling slang on top. It is making the piece sound like a specific person speaking to a specific reader about a specific problem with specific proof.

## Load First

Resolve the `{workspace}` (the named client, or `MyBusiness` for the member's own copy — see `Skills/conventions/workspace.md`), then:

1. Load `{workspace}/knowledge.md`.
2. Load `{workspace}/copy-foundation.md` if it exists.
3. Load `{workspace}/offer-foundation.md` if the copy sells an offer.
4. Load any voice samples the user provides.

Always load `Context/Marketing/copy-rules.md` before editing final copy.

If no client or voice sample exists, use a plain-spoken direct response voice and flag that voice accuracy will improve with 2-3 source samples.

## Non-Negotiables

- Do not invent proof, metrics, testimonials, mechanisms, guarantees, or personal stories.
- Do not change the offer, promise, or compliance posture without calling it out.
- Do not preserve generic language just because it was in the draft.
- Do not use em dashes in final marketing copy.
- Do not add fake casualness, forced slang, or performative personality.

## Diagnosis

Before rewriting, identify the main AI fingerprints:

- generic abstractions instead of concrete details
- banned AI phrases from `copy-rules.md`
- symmetrical phrasing like "not just X, but Y"
- repeated sentence lengths
- over-explaining obvious points
- polished-but-empty claims
- claims without proof
- corporate nouns where a human would use plain verbs
- rhetorical question stacking
- paragraph rhythm that feels manufactured

## Rewrite Passes

Run these passes in order.

### 1. Claim Preservation Pass

List the claims, promises, CTAs, and compliance-sensitive statements in the source copy. Preserve them unless the user asked for strategic rewriting.

### 2. Specificity Pass

Replace vague claims with concrete language from client context, proof, examples, avatar pains, product mechanics, and observed customer language.

If proof is missing, add a `[proof needed: ...]` marker instead of fabricating.

### 3. Voice Pass

Match the available voice source:

- sentence length and cadence
- level of directness
- favorite words and phrases
- how the person opens and closes ideas
- how they use humor, tension, skepticism, or warmth
- how they make claims without sounding inflated

If no voice source exists, default to clear, direct, lightly conversational copy.

### 4. Rhythm Pass

Make the copy feel spoken without making it sloppy:

- vary sentence length
- break dense paragraphs
- use fragments only when they improve emphasis
- remove redundant setup
- keep one idea per sentence when stakes are high

### 5. Proof And Friction Pass

For every major claim, ask:

- Why should the reader believe this?
- What objection appears right here?
- What evidence can we safely use?
- What specificity would make this less generic?

### 6. Compression Pass

Cut filler, repeated ideas, softeners, and "marketing throat clearing." Keep the parts that create belief, desire, clarity, or action.

### 7. Compliance And Copy Rules Pass

Check final copy against `Context/Marketing/copy-rules.md`:

- no em dashes
- no banned AI phrases
- no unsupported proof
- no fake urgency
- no cross-client details

## Output Format

Return:

1. `Diagnosis` - 3-7 bullets on what made the draft feel AI, generic, or off-voice.
2. `Humanized Copy` - the revised copy.
3. `Change Log` - what changed and why.
4. `Proof Gaps` - any claims that still need evidence or client confirmation.
5. `Voice Confidence` - High, Medium, or Low based on available samples.

## Save Location

Save final approved outputs in:

`{workspace}/copy/` — `{workspace}` = `Clients/{slug}`, `MyBusiness`, or `Projects/{slug}` (see `Skills/conventions/workspace.md`).

Ask before writing if the user has not already requested a saved artifact.
