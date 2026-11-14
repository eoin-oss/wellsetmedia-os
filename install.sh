#!/usr/bin/env bash
# Link the WellSetMedia OS skills into Claude Code and set WSM_HOME. Safe to re-run.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$HOME/.claude/skills"
PRIV="${WSM_PRIVATE:-$(dirname "$HERE")/wellsetmedia-os-private}"
mkdir -p "$SKILLS"

echo "Skills -> $SKILLS"
for s in "$HERE"/skills/*/; do
  name="$(basename "$s")"; dst="$SKILLS/$name"
  if [ -L "$dst" ] || [ ! -e "$dst" ]; then
    ln -sfn "${s%/}" "$dst"; echo "  linked  /$name"
  else
    echo "  SKIPPED /$name (a real folder already exists at $dst; move it away and re-run)"
  fi
done

if ! grep -q "WSM_HOME=" "$HOME/.zshrc" 2>/dev/null; then
  echo "export WSM_HOME=\"$HERE\"" >> "$HOME/.zshrc"; echo "WSM_HOME set in ~/.zshrc"
fi

if [ -d "$PRIV" ]; then
  ln -sfn "$PRIV/copy-rules-pack" "$HERE/brand/copy-rules-pack"
  for c in "$PRIV"/clients/*/; do
    slug="$(basename "$c")"; mkdir -p "$HERE/clients/$slug"
    for f in "$c"*; do ln -sfn "$f" "$HERE/clients/$slug/$(basename "$f")"; done
  done
  mkdir -p "$HERE/rules/clients"
  for f in "$PRIV"/rules/*.md; do ln -sfn "$f" "$HERE/rules/clients/$(basename "$f")"; done
  echo "Private pack linked from $PRIV"
else
  echo "No private pack at $PRIV (team members: clone wellsetmedia-os-private next to this repo, then re-run)"
fi

command -v python3 >/dev/null && python3 -c "import PIL" 2>/dev/null || echo "Next: pip3 install pillow"
command -v ffmpeg >/dev/null || echo "Next: brew install ffmpeg whisper-cpp (for the editor)"
echo "Done. Open a new terminal, cd \"$HERE\", run claude."
