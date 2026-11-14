# 06 · Edit

**Trigger:** selects are marked (05 step 7).

## Steps
1. **Rules in before the build:** read the client's `CONTENT-RULES.md`, the hook format, the safe zone and the
   banned music. Set them in the mode before the first render.
2. Auto-editor first pass (`/auto-edit`, the client's mode).
3. **Pilot 3.** Build 3 clips, finish them, Eoin watches. Fix the style, not the clip.
4. Once the pilot passes, run the rest of the batch on the fixed style.
5. Eoin's finish pass in Resolve. All edits native in DaVinci.
6. Render. The machine checks run automatically on every render (preflight, readability, safe zone, banned music).
   A FAIL gets fixed before anything else.
7. Export to the batch folder and **stop. Next task.** QC is not done now (07).

**Done when:** the batch is rendered with no machine FAILs and handed to QC.

## Rules
- **No style experiments in client time.** New looks get tested on Eoin's own content.
- A new rule found mid-batch goes into the rules file and the mode, then only affected clips re-render.
- The machine checks never replace a person watching every reel.
