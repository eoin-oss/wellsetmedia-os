"""Words + speakers from Resolve Studio's own transcription (TranscribeAudio with speaker detection).
Usage: python3 resolve_words.py <project> <media file> <out words.json>"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from resolve import open_project, find_clip


def tc_to_frames(tc, fps):
    hh, mm, ss, ff = [int(x) for x in re.split(r"[:;.]", tc)]
    nominal = int(round(fps))
    frames = ((hh * 60 + mm) * 60 + ss) * nominal + ff
    if ";" in tc or abs(fps - nominal) > 0.001 and fps % 1:  # drop-frame
        drop = int(round(nominal / 15))  # 2 at 29.97, 4 at 59.94
        total_min = hh * 60 + mm
        frames -= drop * (total_min - total_min // 10)
    return frames


def get(project, path, out):
    p = open_project(project, create=True)
    mp = p.GetMediaPool()
    c = find_clip(mp.GetRootFolder(), os.path.basename(path)) or mp.ImportMedia([path])[0]
    tr = c.GetTranscription()
    if not tr:
        c.TranscribeAudio(True)
        for _ in range(240):
            time.sleep(5)
            tr = c.GetTranscription()
            if tr:
                break
    if not tr:
        sys.exit("transcription did not finish")
    fps = float(c.GetClipProperty("FPS"))
    start = tc_to_frames(c.GetClipProperty("Start TC"), fps)
    words = []
    for seg in tr["segments"]:
        spk = seg.get("speaker")
        for w in seg.get("words", []):
            txt = w["text"].strip()
            if not txt or txt.startswith("("):
                continue
            words.append(dict(w=txt, start=(tc_to_frames(w["start"], fps) - start) / fps,
                              end=(tc_to_frames(w["end"], fps) - start) / fps, speaker=spk,
                              norm=re.sub(r"[^a-z0-9']", "", txt.lower())))
    json.dump(words, open(out, "w"), indent=0)
    return words


if __name__ == "__main__":
    W = get(*sys.argv[1:4])
    from collections import Counter
    sec = Counter()
    for w in W:
        sec[w["speaker"]] += w["end"] - w["start"]
    print(len(W), "words; speaking time:", {k: round(v, 1) for k, v in sec.items()})
    print("first:", W[0], "\nlast:", W[-1])
