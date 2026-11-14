"""Word list with timings from a whisper.cpp -ojf -dtw json. Merges sub-word tokens into words."""
import json, re


def load_words(path):
    d = json.load(open(path))
    words = []
    for seg in d["transcription"]:
        for tok in seg.get("tokens", []):
            txt = tok["text"]
            if txt.strip().startswith("[") or not txt.strip():
                continue
            t = tok.get("t_dtw", -1)
            t = t / 100 if t is not None and t >= 0 else tok["offsets"]["from"] / 1000
            end = tok["offsets"]["to"] / 1000
            if txt.startswith(" ") or not words:
                words.append(dict(w=txt.strip(), start=t, end=end))
            else:
                words[-1]["w"] += txt
                words[-1]["end"] = end
    for w in words:
        w["w"] = re.sub(r"<\|.*?\|>|\[?BLANK_AUDIO\]?|\[[^\]]*\]", "", w["w"]).strip()
    words = [w for w in words if w["w"] and not re.search(r"[\[\]<>]", w["w"])]
    for i, w in enumerate(words):
        w["norm"] = re.sub(r"[^a-z0-9']", "", w["w"].lower())
        if i + 1 < len(words):
            w["end"] = min(max(w["end"], w["start"] + 0.08), words[i + 1]["start"])
    return [w for w in words if w["norm"]]
