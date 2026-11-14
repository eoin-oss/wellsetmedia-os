"""Index b-roll: per clip metadata + 3 thumbnails + flat-log check. Resumable.
Usage: python3 index_broll.py <root> [<root> ...]"""
import json, os, subprocess, sys, hashlib
from concurrent.futures import ThreadPoolExecutor

HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = f"{HOME}/index"
THUMBS = f"{OUT}/thumbs"
SKIP_DIRS = {"asssets", "moodboard", "finished reels", "testimonials", "photos"}
EXT = (".mp4", ".mov", ".mxf")
os.makedirs(THUMBS, exist_ok=True)
DB = f"{OUT}/clips.jsonl"
done = set()
if os.path.exists(DB):
    done = {json.loads(l)["path"] for l in open(DB)}


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate,codec_name,color_transfer:format=duration",
                          "-of", "json", path], capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    s = (d.get("streams") or [{}])[0]
    num, den = (s.get("r_frame_rate") or "0/1").split("/")
    return dict(w=s.get("width"), h=s.get("height"), fps=round(int(num) / max(int(den), 1), 3),
                codec=s.get("codec_name"), transfer=s.get("color_transfer"),
                dur=float((d.get("format") or {}).get("duration") or 0))


def stats(jpg):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", jpg, "-vf", "signalstats,metadata=print", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    vals = {}
    for line in out.splitlines():
        if "lavfi.signalstats." in line:
            k, v = line.split("lavfi.signalstats.")[1].split("=")
            vals[k] = float(v)
    return vals


def work(path):
    try:
        m = probe(path)
        cid = hashlib.md5(path.encode()).hexdigest()[:12]
        thumbs = []
        for k, frac in enumerate((0.15, 0.5, 0.85)):
            j = f"{THUMBS}/{cid}_{k}.jpg"
            if not os.path.exists(j):
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(m["dur"] * frac), "-i", path,
                                "-frames:v", "1", "-vf", "scale=320:-2", "-q:v", "4", j])
            if os.path.exists(j):
                thumbs.append(os.path.basename(j))
        st = stats(f"{THUMBS}/{thumbs[1]}") if len(thumbs) > 1 else {}
        sat, ymin, ymax = st.get("SATAVG", st.get("SATAVG ", 0)), st.get("YMIN", 0), st.get("YMAX", 0)
        # S-Log3 that hasn't been graded: low saturation and squashed range
        flat = sat < 22 and (ymax - ymin) < 170
        return dict(id=cid, path=path, folder=os.path.relpath(os.path.dirname(path), ROOTS_BASE), **m,
                    thumbs=thumbs, sat=round(sat, 1), yrange=round(ymax - ymin), looks_ungraded=flat)
    except Exception as e:
        return dict(path=path, error=str(e))


ROOTS_BASE = "/Volumes/Extreme SSD"
files = []
for root in sys.argv[1:]:
    for d, subdirs, fs in os.walk(root):
        subdirs[:] = [s for s in subdirs if s not in SKIP_DIRS and not s.startswith(".")]
        files += [os.path.join(d, f) for f in fs if f.lower().endswith(EXT) and not f.startswith("._")]
todo = [f for f in files if f not in done]
print(f"{len(files)} clips, {len(todo)} to index", flush=True)
with open(DB, "a") as db, ThreadPoolExecutor(6) as ex:
    for i, row in enumerate(ex.map(work, todo), 1):
        db.write(json.dumps(row) + "\n"); db.flush()
        if i % 100 == 0:
            print(i, flush=True)
print("done", flush=True)
