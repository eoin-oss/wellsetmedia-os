#!/usr/bin/env bash
# Captions + covers for several audits, STRICTLY one account at a time.
# Instagram rate-limits hard, so never run two of these loops (or one of these plus a
# logged-in Chrome pull) at the same time.
#
# Usage:  bash run_meta_all.sh <clients-dir> <slug> [slug...]
#   e.g.  bash run_meta_all.sh $WSM_HOME/clients adam-power ted-jago
set -u
ROOT="$1"; shift
for slug in "$@"; do
  d="$ROOT/$slug/audit"
  [ -f "$d/data/ig_reels.json" ] || { echo "SKIP $slug (no ig_reels.json)"; continue; }
  cd "$d" || continue
  mkdir -p img/covers
  python3 -c "
import json; R=json.load(open('data/ig_reels.json'))
print('\n'.join('https://www.instagram.com/reel/'+r['code']+'/' for r in sorted(R,key=lambda r:-r['views'])))" > data/reel_urls.txt
  : > data/ig_meta.jsonl
  total=$(wc -l < data/reel_urls.txt | tr -d ' ')
  echo "== $slug: $total reels"
  while read -r u; do
    yt-dlp --no-simulate --skip-download --write-thumbnail --convert-thumbnails jpg \
           -o "img/covers/%(id)s.%(ext)s" -j --no-warnings "$u" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(json.dumps({'code': d.get('id'), 'ts': d.get('timestamp'), 'cap': d.get('description') or ''}))
except Exception:
    pass
" >> data/ig_meta.jsonl
    sleep 3
  done < data/reel_urls.txt
  echo "== $slug done: $(wc -l < data/ig_meta.jsonl | tr -d ' ') captions, $(ls img/covers | wc -l | tr -d ' ') covers"
done
echo "ALL DONE"
