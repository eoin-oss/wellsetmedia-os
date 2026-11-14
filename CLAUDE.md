# WellSetMedia OS: instructions for Claude

This repo is the WellSetMedia team's shared system. `$WSM_HOME` = this folder. Every path in the skills that starts
with `$WSM_HOME/` resolves here.

## Before writing anything (scripts, captions, hooks, DMs, audits, carousels, stories)
1. `brand/COPY-RULES.md`, then the pack it routes to (`brand/copy-rules-pack/`, team only).
2. `content/scripts/SCRIPT-RULES.md` and everything in `rules/scripts-and-copy/`.
3. The client's `clients/<slug>/CONTENT-RULES.md` if it's client work. Client rules beat house rules.

## Before editing or QC
`rules/edit-and-qc/`, `tools/auto-editor/rules/` and the client's CONTENT-RULES. Machine QC runs on every render;
fix every `CHECK:` line or say why it stays.

## How we work
- The SOPs in `sops/` are the process. Find the stage you're on and follow its page.
- Creative calls (ideas, scripts, final words) are the human's. Draft, present, they edit or say go.
- Nothing posts, sends or goes to a client without an explicit approval (SOP 08).
- Never invent proof, numbers or client facts. Use `[PLACEHOLDER]`.
- Never spend on a paid API without asking first, with a total spend cap.
- Client work lives in `clients/<slug>/` (gitignored). Footage stays in Frame / Drive, never in git.
