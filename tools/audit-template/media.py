#!/usr/bin/env python3
"""Reel media tools for an audit (run from the client audit folder).

  python3 media.py transcribe CODE [CODE ...]   whisper (base) -> data/transcripts.json  (hooks to quote)
  python3 media.py strips CODE [CODE ...]       8-frame strip per reel -> <cache>/strips.jpg  (eyeball format/text)
  python3 media.py measure CODE [CODE ...]      cuts/min (scene>0.3), LUFS, resolution -> data/reel_metrics.json

Reels download (logged out, yt-dlp) into $AUDIT_CACHE (default: $TMPDIR/audit-cache). Whisper mishears
numbers and names: cross-check against the on-screen text before quoting.
"""
import json, os, re, subprocess, sys, tempfile
os.chdir(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get('AUDIT_CACHE', os.path.join(tempfile.gettempdir(), 'audit-cache'))
os.makedirs(CACHE, exist_ok=True)

def fetch(code):
    p = os.path.join(CACHE, code + '.mp4')
    if not os.path.exists(p):
        subprocess.run(['yt-dlp', '-q', '--no-warnings', '-o', os.path.join(CACHE, '%(id)s.%(ext)s'),
                        f'https://www.instagram.com/reel/{code}/'], capture_output=True)
    return p if os.path.exists(p) else None

def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                capture_output=True, text=True).stdout)

def transcribe(codes):
    import whisper
    m = whisper.load_model('base'); path = 'data/transcripts.json'
    T = json.load(open(path)) if os.path.exists(path) else {}
    for c in codes:
        p = fetch(c)
        if not p: print(c, 'download failed'); continue
        r = m.transcribe(p, language='en', fp16=False)
        T[c] = {'dur': round(dur(p), 1), 'segments': [[round(s['start'], 1), s['text'].strip()] for s in r['segments']]}
        print('\n==', c); [print(f'  {s[0]:5.1f} {s[1]}') for s in T[c]['segments'][:6]]
    json.dump(T, open(path, 'w'), indent=1)

def strips(codes):
    from PIL import Image, ImageDraw
    ims = []
    for c in codes:
        p = fetch(c)
        if not p: continue
        o = os.path.join(CACHE, f's8_{c}.jpg')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vf', f'fps=8/{dur(p)},scale=150:-1,tile=8x1', '-frames:v', '1', o])
        ims.append((c, Image.open(o)))
    W = max(i.width for _, i in ims); H = sum(i.height + 16 for _, i in ims)
    sheet = Image.new('RGB', (W, H), (14, 17, 19)); dr = ImageDraw.Draw(sheet); y = 0
    for c, i in ims: dr.text((4, y + 2), c, fill=(237, 233, 214)); sheet.paste(i, (0, y + 16)); y += i.height + 16
    out = os.path.join(CACHE, 'strips.jpg'); sheet.save(out, quality=82); print(out)

def measure(codes):
    path = 'data/reel_metrics.json'
    M = json.load(open(path)) if os.path.exists(path) else {}
    for c in codes:
        p = fetch(c)
        if not p: continue
        pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', p], capture_output=True, text=True).stdout)
        v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]; d = dur(p)
        sc = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-vf', "select='gt(scene,0.3)',metadata=print", '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
        cuts = len(re.findall(r'lavfi.scene_score', sc))
        lr = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
        lufs = re.findall(r'I:\s+(-?[\d.]+) LUFS', lr)
        M[c] = dict(dur=round(d, 1), w=v['width'], h=v['height'], cuts30=cuts, cpm=round(cuts / d * 60, 1), lufs=float(lufs[-1]) if lufs else None)
        print(c, M[c])
    json.dump(M, open(path, 'w'), indent=1)

if __name__ == '__main__':
    cmd, codes = sys.argv[1], sys.argv[2:]
    {'transcribe': transcribe, 'strips': strips, 'measure': measure}[cmd](codes)
