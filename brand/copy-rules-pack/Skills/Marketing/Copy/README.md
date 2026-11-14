---
type: skill-category
status: draft
created: 2026-05-27
tags: [skills, copy, routing]
---

# Copy Skills

Copy work routes here first.

Use `Agents/specialist-wrappers/copywriter.md` only as compatibility language for users who ask for the copywriter agent.

Use `MODULE-MAP.md` before loading large copy modules.

## Routes

| Task | Skill |
|---|---|
| Direct response copy, headlines, sales pages | `direct-response-copy/` |
| VSL | `vsl-scripting/` |
| Positioning, hooks, angles | `positioning-angles/` |
| Brand voice | `brand-voice/` |
| Brand positioning | `brand-positioning/` |
| Copy editing | `copy-editing/` |
| Humanize copy, remove AI feel, match voice | `humanizer/` |

## Context Rules

For workspace work (`{workspace}` = the named client, or `MyBusiness` for the member's own business — see `Skills/conventions/workspace.md`):

1. Load `{workspace}/knowledge.md`.
2. Load `{workspace}/copy-foundation.md` if present.
3. Load `{workspace}/offer-foundation.md` if relevant.
4. Load `Context/Marketing/copy-rules.md`.
5. Load only the skill needed for the deliverable.

## Migration Note

The legacy copywriter agent package has been archived. This skill family replaces it.

Do not load the full copywriter agent package unless the user explicitly needs standalone deployment or parity testing.

For most "make this sound better" requests, decide between:

- `copy-editing/` when the structure, offer, and voice are mostly right but the draft needs improvement.
- `humanizer/` when the draft feels AI-written, generic, stiff, corporate, or unlike the client/founder voice.

## Consolidated Agent Assets

Reusable assets from the archived copywriter agent were copied here:

- `modules/`
- `references/`
- `templates/`
- `examples/`

The legacy agent package remains in place until parity testing passes.
