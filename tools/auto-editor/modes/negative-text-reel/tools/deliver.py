"""Render the CURRENT state of the job's timeline (touches nothing in the edit), finish (-1 dBTP, no tmcd), trim the
black tail the caption overhang leaves, name it <out>.mp4 and delete any older renders in the folder.
Usage: python3 deliver.py <job> <out_name>"""
import glob, json, os, subprocess, sys
from _common import job_dir, HOME
job = job_dir(); name = sys.argv[2] if len(sys.argv) > 2 else "final"
plan = json.load(open(os.path.join(job, "plan.json")))
out = os.path.join(job, "render"); os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, "*.mp4")):
    os.remove(f)
subprocess.run([sys.executable, os.path.join(HOME, "engine/compile.py"), "--each", plan["project"], out, plan["timeline"]], check=True)
raw = os.path.join(out, plan["timeline"] + ".mp4")
subprocess.run([sys.executable, os.path.join(HOME, "engine/finish.py"), raw], check=True)
log = subprocess.run(["ffmpeg", "-v", "info", "-i", raw, "-vf", "blackdetect=d=0.05:pix_th=0.05", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
starts = [float(l.split("black_start:")[1].split()[0]) for l in log.splitlines() if "black_start:" in l]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", raw], capture_output=True, text=True).stdout)
final = os.path.join(out, name + ".mp4")
if starts and dur - starts[-1] < 0.6:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-t", str(starts[-1]), "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", final], check=True)
    os.remove(raw)
else:
    os.replace(raw, final)
print(final)
