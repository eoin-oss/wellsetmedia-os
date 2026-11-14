"""Fallback transcription: openai-whisper medium.en with native word timestamps (slower, robust).
Usage: python3 words_whisper_py.py <job_dir>"""
import json, re, sys, subprocess, warnings
warnings.filterwarnings("ignore")
import whisper
job = sys.argv[1]
meta = json.load(open(f"{job}/job.json"))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", meta["aroll"]],
                           capture_output=True, text=True).stdout)
r = whisper.load_model("medium.en").transcribe(f"{job}/audio.wav", word_timestamps=True, condition_on_previous_text=False)
W = []
for seg in r["segments"]:
    for w in seg.get("words", []):
        t = w["word"].strip()
        if t and w["start"] < dur:
            W.append(dict(w=t, start=round(w["start"], 3), end=round(min(w["end"], dur), 3), norm=re.sub(r"[^a-z0-9']", "", t.lower())))
json.dump(W, open(f"{job}/words.json", "w"), indent=0)
print(len(W), "words, last", W[-1]["end"], "dur", round(dur, 2), "|", " ".join(x["w"] for x in W[-8:]))
