# Hostile Validation (adversarial copy/script QA)

> A red-team pass: before any ad script, page, or VSL ships, attack it from hostile angles and fix what
> breaks. Sourced from the AI Ads Mastery "hostile validation" concept, rebuilt as distinct *lenses*
> (diversity catches more than 25 identical skeptics) and tied to our `copy-rules` + `proof-discipline`.
> Run AFTER `copy-editing`'s Seven Sweeps + `humanizer`, as the last gate before delivery.

## How to run
Read the copy ONCE through each lens below, as that person, looking for the reason to bounce. Mark
PASS / FAIL per lens. Any FAIL → fix, then re-run that lens. Don't ship with an open FAIL on lenses 1–8.

## The lenses

**Critical (must pass):**
1. **The skeptical buyer** — "Why should I believe this?" Every claim has a named/specific source, or it's cut. (= proof-discipline)
2. **The 3-second scroller** — Hook stops the scroll in the first line/frame? If the first sentence is throat-clearing, cut to paragraph 2 (copy-rules #5).
3. **"So what?"** — Each feature/line resolves to an outcome the reader cares about. If a line survives three "so whats," it earns its place.
4. **The clarity test** — Can a smart 12-year-old say what's offered and what to do next, in one read? Confusion = bounce.
5. **The price/risk objection** — Is the cost anchored on cost-of-inaction (not a fabricated value stack), and is risk reversed? (= offer-structuring, value-stack rule)
6. **Compliance / legal** — Any income/health/earnings claim defensible? Platform rules (Meta income claims, Google trademark) respected? No guarantee we can't honor?
7. **The AI-tell sniff** — Em dashes, banned phrases, the 3-short-then-medium cadence, framework/rhetorical-question stacking? (= copy-rules; run verify_copy.py)
8. **The brand-voice check** — Sounds like THIS client (copy-foundation §9/§13), not generic? (= voice-check)

**Sharpening (should pass):**
9. **The competitor** — Could a rival run this exact copy with their logo? If yes, it's not differentiated — name the mechanism/enemy.
10. **The cynic** — Where does it sound hypey or too-good-to-be-true? Specificity and proof beat enthusiasm.
11. **The busy CFO/owner** — Does it respect their time and lead with the outcome, not your process?
12. **The "already tried that"** — Does it address why THIS is different from what burned them before? (objection handling)
13. **The proof auditor** — Are proof points stacked in threes, placed near the claims/objections they answer? (proof-pyramid)
14. **The mobile reader** — Scannable? Short paragraphs, subheads, one idea per sentence?

## Output
```
HOSTILE VALIDATION — {deliverable}
FAILS: [lens # — what broke — fix applied]
PASSES: [n/14]
Verdict: SHIP / FIX-FIRST
```

> For ad scripts specifically, `animation-ad-scripting` and `ad-copy` call this pass before output.
> For pages/VSLs, `sales-pages` / `vsl-scripting` call it as the final gate.
