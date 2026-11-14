# AI Editor

A Claude-driven video editor that builds edits **natively inside DaVinci Resolve Studio**. Final takes only, silences and stumbles cut on whole words, b-roll matched line by line from an indexed library, captions and motion text built in Resolve, then it learns from the finishing pass.

Each look is a **mode** (how the edit is assembled) plus a **style** (captions, fonts, pacing, grade). The rules in `rules/` are the taste layer: every hard rule learned from real client and personal edits.

## What's in here

| Folder | What it is |
|---|---|
| `skills/auto-edit/SKILL.md` | The Claude Code skill that runs the whole editor. Start here. |
| `skills/overlay-system/SKILL.md` | The overlay / motion-graphic system that sits on top of edits. |
| `PLANNER.md` | How the edit gets planned: takes, cuts, b-roll rules, pacing. |
| `TAKES.md` | How final takes are picked and false starts thrown out. |
| `engine/` | The Python engine: transcribe, cut, b-roll catalog + matching, Resolve timeline build, captions, QA (safe zone, readability, joins, no repeat b-roll). |
| `modes/` | Every edit style. `penguin/` is the longevity-penguin style (locked default), plus `eoin-yap`, `kallaway-split`, `negative-text-reel`, `podcast-sidecap`, `hempton-podcast`, `kyle-seminar`, `evil-framework`, `vsl`. Each has a `MODE.md` explaining the look and the rules. |
| `styles/` | Caption comps (Fusion `.comp`), style JSON, pacing research, `style-packs.html` (visual overview of the packs). |
| `rules/` | The hard rules and the reasoning behind each one: safe zone, readable text, whole-word cut points, quieter impact SFX, all-in-DaVinci, no repeat b-roll, literal b-roll, text hook on every video, penguin edit rules, and more. |
| `reference/` | Written breakdowns of reference edits. |
| `models/` | MediaPipe BlazeFace model used for face-aware framing (Apache 2.0). |

## Setup

- macOS, **DaVinci Resolve Studio** (scripting API needs Studio), Python 3.9+
- `ffmpeg` and `whisper.cpp` (`brew install ffmpeg whisper-cpp`) plus a whisper model
- Claude Code: copy `skills/*` into `~/.claude/skills/`, then say `/auto-edit` with your footage
- Some scripts have absolute paths from the original machine (`/Users/...`, footage drives). Repoint them to your own folders.

## Not included

Footage, renders, client jobs, the labelled b-roll library and reference videos. Those are private or someone else's. Index your own b-roll with `engine/index_broll.py` + `engine/emotion_index.py`.
