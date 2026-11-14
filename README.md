# WellSetMedia OS

The systems WellSetMedia runs its content offer on: the Claude Code skills, the AI editor, the house rules, the SOPs and the frameworks. One repo, so everyone on the team works off exactly the same machine.

Footage, client folders and finished work are not in here. They live in Frame / Drive.

## Install (Mac, 5 minutes)

```bash
git clone https://github.com/eoin-oss/wellsetmedia-os ~/wellsetmedia-os
# team only: the private pack (copy rules + client rules) sits next to it
git clone https://github.com/eoin-oss/wellsetmedia-os-private ~/wellsetmedia-os-private
cd ~/wellsetmedia-os && ./install.sh
```

`install.sh` links every skill into `~/.claude/skills/`, sets `WSM_HOME` to this folder, and links the private copy rules pack and client rules in if you have them. Run it again after every `git pull` (it's safe to re-run).

The editor also needs **DaVinci Resolve Studio**, `brew install ffmpeg whisper-cpp` and `pip3 install pillow`. See `tools/auto-editor/README.md`.

## The skills

| Say | What it does | SOP |
|---|---|---|
| `/content-audit <name>` | Full IG + YouTube audit of a prospect, the report plus a Loom script | 01 |
| `/weekly-research` | Monday pull of every niche watchlist, the outliers and why they worked | 03b |
| `/content-engine` | Content day in order: research, ideation multiplier, scripts, shot list, film, edit, stories | 04 |
| `/viral-hooks` | Hook batches and hook critique against the patterns that work | 04 |
| `/auto-edit` | The AI editor. Talking head to a finished edit in DaVinci: takes, cuts, b-roll, captions, hook text, QC | 06 / 07 |
| `/overlay-system` | The 10/10 habits overlays and motion graphics on top of edits | 06 |
| `/story-sequence` | IG story sequences **and carousels** on a live page you edit with Claude, then exported exactly as approved | 04 / 06 |
| `/morelife-carousel` | More Life (Kyle) carousels in the locked "My story" look | 06 |

### The live edit flow (stories + carousels)

1. Claude drafts the words with you and maps each beat to a photo.
2. It publishes a private page on claude.ai where every frame is editable: words, red/green emphasis, accent box, crop, zoom, position, order. Add `"format": "carousel"` and it's 4:5 slides instead of 9:16 stories.
3. You (or the client, from the page's Share menu) edit live on the page, or tell Claude what to change. It autosaves.
4. Tell Claude **"good to go"**. It reads the page and renders 1080px JPGs that match the page exactly, then flags anything that breaks a rule.

## The rules (Claude loads these automatically from `CLAUDE.md`)

- `brand/COPY-RULES.md`: every word of copy. Zero em dashes, no foil framing, the three-test, never invent proof.
- `content/scripts/SCRIPT-RULES.md` + `rules/scripts-and-copy/`: the 5-phase retention framework, hook stacking, anti-generic law.
- `rules/edit-and-qc/` + `tools/auto-editor/rules/`: safe zone, readable text, text hook on every video, whole-word cuts, no repeat b-roll, QC with cold eyes.
- `rules/process/`: front-load the client (one call, one list), batch shoots by setup, the creative is the human's call.
- `clients/<slug>/CONTENT-RULES.md`: per-client rules. Copy `clients/_template/` for a new client.

## The client cycle

```
01 leads + audit → 02 sales call → 03 onboarding → 03b research → 04 pre-production → 05 shoot
      → 06 edit → 07 QC → 08 approval → 09 scheduling → 10 month end → back to 03b
```

One page per stage in `sops/`. Every stage has one owner and a "done when".

## Updating

Eoin's live systems are the source. He re-exports and pushes. You `git pull && ./install.sh`. If you improve a skill, open a PR or tell him. Don't fork the rules.
