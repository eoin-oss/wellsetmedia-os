#!/bin/bash
# usage (from the client audit folder, in the BACKGROUND): bash fetch_meta.sh
# For every reel in data/ig_reels.json: caption (+ likes/comments/size) -> data/ig_meta.jsonl and cover -> img/covers/<code>.jpg.
# Sequential on purpose (Instagram rate limits): ~3s a reel. Never run two Instagram loops at once.
mkdir -p img/covers
python3 -c "import json;print('\n'.join('https://www.instagram.com/reel/'+r['code']+'/' for r in json.load(open('data/ig_reels.json'))))" > data/reel_urls.txt
: > data/ig_meta.jsonl
while read -r u; do
  yt-dlp --no-simulate --skip-download --write-thumbnail --convert-thumbnails jpg -o "img/covers/%(id)s.%(ext)s" -j --no-warnings "$u" 2>/dev/null \
  | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(json.dumps({'code': d.get('id'), 'ts': d.get('timestamp'), 'cap': d.get('description') or '', 'w': d.get('width'), 'h': d.get('height'),
                      'likes': d.get('like_count'), 'com': d.get('comment_count')}))
except Exception:
    pass" >> data/ig_meta.jsonl
  sleep 1.5
done < data/reel_urls.txt
# second pass: any cover the first pass missed
while read -r u; do
  c=$(basename "$u"); [ -f "img/covers/$c.jpg" ] && continue
  yt-dlp -q --no-warnings --skip-download --write-thumbnail --convert-thumbnails jpg -o "img/covers/%(id)s.%(ext)s" "$u" 2>/dev/null; sleep 1.2
done < data/reel_urls.txt
echo "captions $(wc -l < data/ig_meta.jsonl) covers $(ls img/covers | wc -l)"
