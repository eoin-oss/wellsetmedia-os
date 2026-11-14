---
type: module-map
status: draft
created: 2026-05-27
tags: [copy, modules, migration, agent-to-skill]
---

# Copy Module Map

This map consolidates reusable copywriter agent knowledge into the Copy skill family.

Legacy source:

the copywriter agent package (archived - migration complete)

Current skill destination:

`Skills/Marketing/Copy/`

## Modules

| Need | Load |
|---|---|
| sales page structure | `modules/sales-pages.md` |
| VSL structure | `modules/vsl-scripting.md` |
| email flows | `modules/email-flows.md` |
| ad copy | `modules/ad-copy.md` |
| offer structuring for copy | `modules/offer-structuring.md` |
| website homepage | `modules/homepage.md` |

## References

| Need | Load |
|---|---|
| headline patterns | `references/headline-formulas.md` |
| proof strategy | `references/proof-pyramid.md` |
| named framework catalog (AIDA/PAS/BAB/4Ps…) | `references/framework-catalog.md` |
| positive power-words bank (filtered) | `references/power-words.md` |
| final adversarial QA (run before delivery) | `references/hostile-validation.md` |

## Templates

| Need | Load |
|---|---|
| client copy foundation | `templates/copy-foundation.md` |
| funnel brief | `templates/funnel-brief.md` |

## Examples

| Need | Load |
|---|---|
| sample VSL outline | `examples/sample-vsl-outline.md` |

## Loading Rule

Do not load every module by default.

Load the smallest relevant module after identifying the deliverable type.

Examples:

- Sales page request -> load `direct-response-copy/SKILL.md`, `modules/sales-pages.md`, copy rules.
- VSL request -> load `vsl-scripting/SKILL.md`, `modules/vsl-scripting.md`, copy rules.
- Email flow request -> route to `Skills/Marketing/Funnels/email-flows/` and optionally load `modules/email-flows.md`.
- Ad copy request -> route to Ads skill and optionally load `modules/ad-copy.md`.
- Homepage request -> load `direct-response-copy/SKILL.md`, `modules/homepage.md`, copy rules.
- Humanizer request -> load `humanizer/SKILL.md` and copy rules.
- Before delivering ANY page/ad/VSL -> run `references/hostile-validation.md` as the final adversarial gate.

## Migration Status

Copied from legacy agent:

- `modules/`
- `references/`
- `templates/`
- `examples/`

Not yet complete:

- parity test old agent vs new skill route
- split oversized `direct-response-copy/SKILL.md`
- [done] legacy copywriter agent archived
