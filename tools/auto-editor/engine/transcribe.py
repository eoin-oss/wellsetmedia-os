"""Set up a job from a cut A-roll: transcribe (whisper.cpp + DTW word timing), words.json, phrases.json.
Usage: python3 transcribe.py <aroll file> <job name> [style]"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from words import load_words
from phrases import split

HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL = os.path.expanduser("~/.cache/hyperframes/whisper/models/ggml-small.en.bin")
aroll, name = os.path.abspath(sys.argv[1]), sys.argv[2]
style_name = sys.argv[3] if len(sys.argv) > 3 else "eoin"
style = json.load(open(f"{HOME}/styles/{style_name}/style.json"))
job = f"{HOME}/jobs/{name}"
os.makedirs(job, exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", aroll, "-ar", "16000", "-ac", "1", f"{job}/audio.wav"], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", aroll],
                          capture_output=True, text=True).stdout)


def run(prompt):
    cmd = ["whisper-cli", "-m", MODEL, "-f", f"{job}/audio.wav", "-ojf", "-of", f"{job}/whisper", "-dtw", "small.en", "-np"]
    subprocess.run(cmd + (["--prompt", prompt] if prompt else []), check=True, capture_output=True)
    return load_words(f"{job}/whisper.json")


def broken(W):
    # DTW sometimes collapses: many words share one timestamp, or words run past the end of the clip
    from collections import Counter
    same = Counter(round(w["start"], 1) for w in W).most_common(1)[0][1] if W else 0
    return not W or same > 3 or W[-1]["end"] > dur + 0.3


W = run(style.get("glossary", ""))
if broken(W):
    print("timing broke with the glossary prompt: re-running without it")
    W = run("")
if broken(W):
    sys.exit("word timing still broken: check this clip by hand")
json.dump(W, open(f"{job}/words.json", "w"), indent=0)
P = split(W, style["phrases"])
json.dump(P, open(f"{job}/phrases.json", "w"), indent=1)
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate", "-of", "json", aroll], capture_output=True, text=True).stdout)["streams"][0]
n, d = probe["r_frame_rate"].split("/")
json.dump(dict(aroll=aroll, style=style_name, fps=round(int(n) / int(d), 3), w=probe["width"], h=probe["height"]),
          open(f"{job}/job.json", "w"), indent=1)
print(f"{len(W)} words, {len(P)} phrases -> {job}")
print(" | ".join(p["text"] for p in P))
