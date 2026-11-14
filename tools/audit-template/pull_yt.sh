#!/bin/bash
# usage (from the client audit folder): bash pull_yt.sh @handle
# -> data/yt_full.jsonl: one JSON line per upload (long-form + Shorts): views, likes, comments, duration, date, title.
set -u
H="$1"; mkdir -p data
for t in videos shorts streams; do
  yt-dlp --flat-playlist -J "https://www.youtube.com/$H/$t" > "data/.yt_$t.json" 2>/dev/null || true
done
python3 - <<'PY'
import json
ids = []
for t in ['videos', 'shorts', 'streams']:
    try: d = json.load(open(f'data/.yt_{t}.json'))
    except Exception: continue
    if not d: continue
    en = d.get('entries') or []
    print(t, d.get('channel'), 'subs', d.get('channel_follower_count'), 'n', len(en))
    ids += [('https://www.youtube.com/shorts/' if t == 'shorts' else 'https://www.youtube.com/watch?v=') + e['id'] for e in en]
open('data/.yt_ids.txt', 'w').write('\n'.join(ids)); print('total', len(ids))
PY
yt-dlp --skip-download -j --no-warnings -a data/.yt_ids.txt > data/yt_full.jsonl 2>/dev/null
rm -f data/.yt_*.json
echo "uploads: $(wc -l < data/yt_full.jsonl)"
