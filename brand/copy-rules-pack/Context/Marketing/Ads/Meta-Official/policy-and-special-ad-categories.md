# Ad Policy & Special Ad Categories — Meta Official Reference

> **Source layer:** Meta's own published policies (Transparency Center + Business Help Center).
> **Last pulled:** 2026-06-25
> **Maintained by:** meta-official-docs skill (Skills/Marketing/Ads/meta-official-docs/)

## What this covers

The Special Ad Category system (which categories exist and the audience/targeting restrictions Meta forces on them) and the prohibited/restricted content rules most likely to get coaching, trading, and finance ads rejected — Personal Attributes, Unrealistic Outcomes, and Financial & Insurance Products and Services. Every rule below was retrieved from a live Meta source on 2026-06-25 and cited inline; items we could not pull verbatim are flagged in *Verify-at-source*. This is an internal compliance summary, not legal advice — Meta's pages are the source of truth.

## Special Ad Categories

Meta requires advertisers to self-declare a **Special Ad Category** when an ad relates to credit/finance, housing, employment, or social issues/elections/politics. Declaring the category triggers automatic audience restrictions as "a preventative measure to protect people from discriminatory practices." If you qualify and don't declare, **the ad may be rejected**. (Help Center 399587795372584)

**The categories (finance/housing/employment branch):**

- **Financial products & services** — *replaced the former "Credit" category.* Required since **January 21, 2025** for advertisers based in the US or showing financial ads to US audiences. (Help Center 567423788405762)
  - *In scope (US):* banking/checking/savings accounts, credit cards, loans (auto, mortgage, personal, business), prepaid cards, investment services, pension/retirement funds, insurance products, consumer payment services, BNPL / 0% APR installments, plus brand ads for any of these "regardless of offer."
  - *Credit subset* (US, Canada, and parts of Europe): credit cards, loans, long-term financing, debt recovery, debt consolidation/relief.
  - *Out of scope:* gift cards, store rewards, B2B-only financial products, tax & accounting services.
- **Housing** — sale/rental/temporary listings, mortgage/home/renters/mortgage insurance, financing/mortgage loans, home equity/appraisal, real estate & house-hunting/aggregator services. *Excludes* hotels, resorts, retreats, and general homeownership education.
- **Employment** — full/part-time jobs, internships, apprenticeships, certification programs, job fairs/boards, guaranteed interviews or career placement, company perks alongside a listing. *Excludes* generic career advice with no specific listing.
- **Social Issues, Elections or Politics (SIEP)** — separate category with its own authorization/"Paid for by" disclaimer regime (see *Verify-at-source*).

**Targeting restrictions applied when a finance/housing/employment category is declared** (for advertisers in or targeting the US/US territories, Canada, and listed European countries) — (Help Center 2220749868045706):

- **Geography:** target by country/region/state/province/city only — **no ZIP/postal code**, and **you cannot exclude locations**. City/address/pin-drop audiences get an **expanded radius** (e.g., Seattle → +15-mile radius from city center).
- **Age:** generally fixed to **18 through 65+** for housing, employment, and credit ads. (Exception: credit ads in Europe may select a different age range to meet local/industry requirements.)
- **Gender:** audiences **must include all genders** — this option cannot be edited.
- **Detailed targeting:** "some demographic, behavior and interest options are unavailable," and **excluding any detailed-targeting selections is unavailable**.
- **Lookalikes:** **Advantage+ Lookalike is unavailable.** Audience exclusions, lookalike audiences, and some saved audiences are limited or unavailable.
- **Special Ad Audience (the old lookalike replacement):** as of **August 25, 2022, you can no longer create new Special Ad Audiences.** (Help Center 364084711158390)

> Net effect for finance/trading/coaching clients: once declared, you scale almost entirely through **creative volume + Broad targeting + Advantage Audience**, not through demographic/interest narrowing or lookalikes.

## Prohibited / restricted content (high-risk for our verticals)

**Privacy Violations and Personal Attributes** (Objectionable Content):
> "Ads must not contain content that shares or asks for private information about users. In addition, ads must not contain content that asserts or implies personal attributes."

Prohibited assertions/implications include: *"race, ethnicity, religion, beliefs, age, sexual orientation or practices, gender identity, disability, physical or mental health (including medical conditions), vulnerable financial status, voting status, membership in a trade union, criminal record, or name."* **Allowed:** describing the product/service, "you/your" language that doesn't reference a restricted attribute, broad references like "American"/"New Yorker," passing references to gender/age groups, and health PSAs that don't assert someone *has* a condition.
*High-risk pattern for us:* trading/finance copy that implies the reader's financial situation — e.g., "Struggling with debt?", "Tired of being broke?", "Your trading account is bleeding" — can be read as implying **vulnerable financial status**. Avoid second-person copy that asserts the reader's financial or emotional state.

**Unrealistic Outcomes** (Deceptive Content): Meta prohibits "deceptive or exaggerated claims about the success of a product or service to mislead people," and (per Unacceptable Business Practices) ads that "**promise financial benefits by misrepresenting an entity, industry association or news outlet**" or "use the image of a famous person and misleading tactics in order to bait people." For health/wellness, depictions "must reflect realistic outcomes over time and should not include side-by-side comparisons."
*High-risk pattern for us:* income/ROI claims ("$10k/month in 30 days," "turn $500 into $50k"), get-rich-quick framing, fabricated trading P&L screenshots, and before/after equity-curve side-by-sides.

**Financial and Insurance Products and Services** (Restricted Goods & Services):
> "Ads promoting credit cards, loans or insurance services must be targeted to people 18 years or older."

- **No data harvesting in-ad:** ads must not "directly request the input of any personally identifiable information or certain types of financial information."
- **Verification/authorization:** advertisers "may be required to verify their business and/or individual identity and demonstrate they are authorized by the relevant regulatory authorities," and must comply with legal disclosure requirements.
- **Prohibited financial products** (associated with misleading/deceptive promotion): payday loans, paycheck/cash advances, bail bonds, **short-term loans of 90 days or less**, penny auctions, **binary options**, **initial coin offerings (ICOs)**, and **contract-for-difference (CFD) trading**. (See also the separate Cryptocurrency policy.)

## How AID applies this

- **Declare the category up front.** Any client whose offer touches credit/finance/investing/insurance (or housing/employment) runs under the matching Special Ad Category — e.g. a prop-trading or funding client is locked to `FINANCIAL_PRODUCTS_SERVICES`. Declaring is mandatory for US-based or US-targeted finance ads since 2025-01-21; skipping it is a rejection.
- **Scale through creative, not targeting.** Because SAC blocks lookalikes, ZIP/postal, location exclusions, gender/age narrowing, and detailed-targeting exclusions, the only levers are **creative volume + Broad + Advantage Audience**. Bake this into media-buying playbooks for every finance/trading client.
- **No vulnerable-financial-status implications in copy.** Route trading/coaching/finance copy through `Context/Marketing/copy-rules.md` and the Personal Attributes test: strip any second-person line that *asserts or implies* the reader's debt, brokenness, or financial distress.
- **No invented outcomes — ever.** The Unrealistic Outcomes + "never invent proof/metrics/testimonials/guarantees" rule (CLAUDE.md Quality Rules) is the same rule. No income claims, fabricated P&L, before/after equity curves, or fake-news/endorsement framing.
- **Hard-gate it deterministically.** Encode per-client prohibitions (income claims, guarantee language, CFD/binary-options terms) as Golden Rules and run `python3 Scripts/validation/golden_rules_check.py --client {slug} <deliverable>` — a HARD-FAIL blocks the deliverable, wired into `Skills/voice-check/` Check 0 and the PostToolUse hook.
- **Know the prohibited list cold.** CFDs, binary options, ICOs, payday/sub-90-day loans, bail bonds, penny auctions are flat-out banned — never accept a client offer built on these, and treat crypto as its own restricted regime.

## Canonical sources

- Advertising Standards (index): https://transparency.meta.com/policies/ad-standards/
- Privacy Violations and Personal Attributes: https://transparency.meta.com/policies/ad-standards/objectionable-content/privacy-violations-personal-attributes/
- Unrealistic Outcomes: https://transparency.meta.com/policies/ad-standards/deceptive-content/unrealistic-outcomes
- Unacceptable Business Practices: https://transparency.meta.com/policies/ad-standards/fraud-scams/unacceptable-business-practices/
- Financial and Insurance Products and Services: https://transparency.meta.com/policies/ad-standards/restricted-goods-services/financial-services/
- Prohibited Financial Products and Services: https://transparency.meta.com/policies/ad-standards/deceptive-content/prohibited-financial-products-and-services/
- About ads for housing, employment or financial products & services: https://www.facebook.com/business/help/399587795372584
- About ads for financial products & services (credit detail): https://www.facebook.com/business/help/567423788405762
- Audiences for housing/employment/financial campaigns (targeting restrictions): https://www.facebook.com/business/help/2220749868045706
- Create a Special Ad Audience (deprecation notice): https://www.facebook.com/business/help/364084711158390

## Verify-at-source / open questions

- **Unrealistic Outcomes — exact policy sentence not captured verbatim.** The `/deceptive-content/unrealistic-outcomes/` page returned 404 on direct WebFetch; content above is drawn from WebSearch extraction plus the adjacent Unacceptable Business Practices page. Pull the literal "Policy" statement directly before quoting it externally.
- **Prohibited Financial Products list** is corroborated across pages, but confirm the *current* full enumeration on the live page — Meta revises this list.
- **SIEP (Social Issues, Elections or Politics)** carries its own authorization + "Paid for by" disclaimer requirements; not detailed here. Pull the SIEP policy if a client runs issue/political ads.
- **Cryptocurrency** is governed by a separate restricted policy (written authorization/licensing often required); verify per-client before running any crypto/token offer.
- **European age exception** for credit ads and evolving EU privacy-driven targeting changes should be re-checked for any EU-targeted campaign.
- **Policy drift:** Meta updates these pages frequently (the Credit→Financial Products migration is a recent example). Re-pull before each new finance/trading client launch; treat anything older than ~30 days as stale.
