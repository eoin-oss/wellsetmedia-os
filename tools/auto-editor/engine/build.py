"""Build an approved plan into a fresh Resolve project: A-roll on V1, b-roll on V2, captions V3-V5.
Usage: python3 build.py <job_dir>"""
import re
import json, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from resolve import connect, find_clip

HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MTP_DRB = "/Volumes/Extreme SSD/personal brand directory/asssets/Motiontext-pro-v1/davinci-resolve-version21+/MotionText Pro V1.drb"


# Helvetica Bold advance widths in em (approx) -> caption width estimate, so no caption leaves the frame
_NARROW, _WIDE = set("iljtf.,'!:;|"), set("mwMW@")
EM_PX = 116.0  # px per em at caption zoom 1.0 on a 1920-wide timeline (measured off a render)


def text_width(s):
    lines = s.split("\n")
    def w(line):
        return sum(0.28 if c in _NARROW or c == " " else 0.86 if c in _WIDE else 0.68 if c.isupper() else 0.56 for c in line)
    return max(w(l) for l in lines) * EM_PX


def speech_onsets(wav, words, idxs):
    """Whisper word starts land ~0.13s (up to 0.6s) after the voice actually starts, so cuts placed on them feel late.
    For each word index, find the real onset in the audio between the previous word's end and the whisper start."""
    import wave, numpy as np
    if not os.path.exists(wav):
        return {}
    wf = wave.open(wav)
    sr, ch = wf.getframerate(), wf.getnchannels()
    a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).reshape(-1, ch).astype(float).mean(1)
    hop = sr // 100
    rms = np.sqrt(np.convolve(a ** 2, np.ones(hop) / hop, "same")[::hop])
    thr = np.percentile(rms, 30) * 3
    out = {}
    for i in idxs:
        ws = words[i]["start"]
        lo = int(((words[i - 1]["end"] + 0.03) if i > 0 else max(0.0, ws - 0.6)) * 100)
        hi = int(ws * 100) + 1
        on = next((f for f in range(lo, min(hi, len(rms))) if rms[f] > thr), None)
        if on is not None:
            out[i] = min(ws, on / 100)
    return out


def hook_look(src, m, last):
    """Hook lines: white with a soft drop shadow so they read on any background; the last hook line, the punch,
    takes the accent colour."""
    if not m.get("shadow") and not m.get("accent"):
        return src  # the template as is
    rgb = m.get("accent", [1, 1, 1]) if last else [1, 1, 1]
    fill = "".join(f"\n\t\t\t\t{c}1 = Input {{ Value = {v}, }}," for c, v in zip(("Red", "Green", "Blue"), rgb))
    sh = m.get("shadow") or {"softness": 0, "opacity": 0, "offset": [0, 0]}
    return src.replace('Style = Input { Value = "Bold", },',
                       'Style = Input { Value = "Bold", },' + fill + '\n\t\t\t\tEnabled3 = Input { Value = 1, },'
                       f'\n\t\t\t\tSoftness3 = Input {{ Value = {sh["softness"]}, }},'
                       f'\n\t\t\t\tAlpha3 = Input {{ Value = {sh["opacity"]}, }},'
                       f'\n\t\t\t\tOffset3 = Input {{ Value = {{ {sh["offset"][0]}, {sh["offset"][1]} }}, }},', 1)


def render_intro(src, fps, frames, z_from, out):
    """Smooth per-frame zoom-out of the first frames. Encoded with the SOURCE's pixel format and colour tags (range,
    matrix, transfer) so Resolve reads it exactly like the clip it joins: a mismatch shows as a brightness jump."""
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(src):
        return out
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                               "stream=width,height,pix_fmt,color_range,color_space,color_transfer,color_primaries",
                                               "-of", "json", src], text=True))["streams"][0]
    zp = (f"zoompan=z='1+{z_from - 1}*pow(1-in/{frames}\\,3)':d=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
          f":s={info['width']}x{info['height']}:fps={fps},format={info['pix_fmt']}")
    tags = []
    for k, flag in (("color_range", "-color_range"), ("color_space", "-colorspace"), ("color_transfer", "-color_trc"),
                    ("color_primaries", "-color_primaries")):
        if info.get(k) and info[k] != "unknown":
            tags += [flag, info[k]]
    # libx264 drops some transfer tags (e.g. iec61966-2-4 on clip 16): write the VUI straight into the stream
    codes = {"bt709": 1, "unknown": 2, "smpte170m": 6, "bt470bg": 5, "iec61966-2-4": 11, "iec61966-2-1": 13, "bt2020nc": 9,
             "bt2020": 9, "arib-std-b67": 18, "smpte2084": 16}
    vui = [f"{n}={codes[info[k]]}" for k, n in (("color_primaries", "colour_primaries"), ("color_transfer", "transfer_characteristics"),
                                                ("color_space", "matrix_coefficients")) if info.get(k) in codes and info[k] != "unknown"]
    if vui:
        tags += ["-bsf:v", "h264_metadata=" + ":".join(vui)]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-frames:v", str(frames), "-an", "-vf", zp, "-c:v", "libx264",
                    "-crf", "8", "-preset", "slow", "-pix_fmt", info["pix_fmt"], *tags, out], check=True)
    return out


def fusion_str(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def main(job):
    job = os.path.abspath(job)
    plan = json.load(open(f"{job}/plan.json", encoding="utf-8"))
    words = json.load(open(f"{job}/words.json", encoding="utf-8"))
    style = json.load(open(f"{HOME}/styles/{plan['style']}/style.json", encoding="utf-8"))
    template = open(f"{HOME}/styles/{plan['style']}/{style['captions']['template']}", encoding="utf-8").read()
    clips = {json.loads(l)["id"]: json.loads(l) for l in open(f"{HOME}/index/clips.jsonl") if '"id"' in l}
    fps, W, H = plan["fps"], plan["w"], plan["h"]

    pm = connect().GetProjectManager()
    pm.GotoRootFolder()
    name = plan["project"]
    shared = plan.get("shared_project", False)
    cur = pm.GetCurrentProject()
    if shared and cur and cur.GetName() == name:
        p = cur
    elif shared and name in (pm.GetProjectListInCurrentFolder() or []):
        p = pm.LoadProject(name)
    elif name in (pm.GetProjectListInCurrentFolder() or []):
        sys.exit(f"project '{name}' already exists: rename or delete it first")
    else:
        p = pm.CreateProject(name)
        p.SetSetting("timelineFrameRate", str(fps))
        p.SetSetting("timelineResolutionWidth", str(W))
        p.SetSetting("timelineResolutionHeight", str(H))
    mp = p.GetMediaPool()
    root = mp.GetRootFolder()
    if not find_clip(root, style["captions"]["carrier_title"]):
        mp.ImportFolderFromFile(MTP_DRB)
    carrier = find_clip(root, style["captions"]["carrier_title"])
    for k in range(1, (p.GetTimelineCount() or 0) + 1):
        if p.GetTimelineByIndex(k).GetName() == plan["timeline"]:
            sys.exit(f"timeline '{plan['timeline']}' already exists in '{name}'")
    carrier_fps = float(carrier.GetClipProperty("FPS"))
    def sub(name_):
        return next((f for f in root.GetSubFolderList() or [] if f.GetName() == name_), None) or mp.AddSubFolder(root, name_)
    mp.SetCurrentFolder(sub("aroll"))
    aroll = find_clip(root, os.path.basename(plan["aroll"])) or mp.ImportMedia([plan["aroll"]])[0]
    ch = plan.get("audio_channel", 0)
    if ch in (1, 2):  # mono mic recorded on one side: play it on both
        aroll.SetAudioMapping(json.dumps({"track_mapping": {"1": {"channel_idx": [ch, ch], "mute": False, "type": "Stereo"}}}))
    broll_bin = sub("broll")
    mp.SetCurrentFolder(broll_bin)
    used = {s["broll"]["id"] for s in plan["segments"] if s.get("broll")}
    pool = {}
    for cid in used:
        items = [find_clip(broll_bin, os.path.basename(clips[cid]["path"]))] if find_clip(broll_bin, os.path.basename(clips[cid]["path"])) else mp.ImportMedia([clips[cid]["path"]])
        if items:
            pool[cid] = items[0]
    mp.SetCurrentFolder(sub("timelines"))
    t = mp.CreateEmptyTimeline(plan["timeline"])
    p.SetCurrentTimeline(t)
    t0 = t.GetStartFrame()
    a_frames = int(round(float(aroll.GetClipProperty("Frames"))))
    a_fps = float(aroll.GetClipProperty("FPS"))
    keep = plan.get("keep")  # [[src_in, src_out], ...] sec: silences cut out, everything else in TIMELINE time
    keep_f = [(int(round(a * a_fps)), int(round(b * a_fps))) for a, b in keep] if keep else None
    def src_f(f):  # timeline frame -> source frame
        if not keep_f:
            return f
        acc = 0
        for a, b in keep_f:
            if f < acc + (b - a):
                return a + (f - acc)
            acc += b - a
        return keep_f[-1][1]
    if keep_f:
        bounds, acc = [], 0
        for a, b in keep_f:
            acc += b - a; bounds.append(acc)
        a_frames = acc
    else:
        bounds = []
    if os.path.exists(f"{job}/cuts.json"):
        # raw footage: lay the kept pieces back to back (cut engine output)
        rec = t0
        for c in json.load(open(f"{job}/cuts.json", encoding="utf-8")):
            a_in, a_out = int(round(c["in"] * a_fps)), int(round(c["out"] * a_fps))
            mp.AppendToTimeline([{"mediaPoolItem": aroll, "startFrame": a_in, "endFrame": a_out, "trackIndex": 1, "recordFrame": rec}])
            rec += int(round((a_out - a_in) * fps / a_fps))
        # hide jump cuts: alternate punch-in on every other piece
        punch = style.get("aroll", {}).get("jump_punch", 1.0)
        for n, it in enumerate(t.GetItemListInTrack("video", 1) or []):
            if n % 2 == 1 and punch != 1.0:
                it.SetProperty({"ZoomX": punch, "ZoomY": punch})
    else:
        z = plan.get("intro_zoom")
        if z:
            z = {**z, **style.get("intro_zoom", {})}
        # V1 is laid as pieces of the one source: the intro, then a new piece at every A-roll join that no b-roll hides.
        # Each such piece toggles a punch-in, the standard way to hide a jump cut that can't take a cutaway.
        from joins import joins_for, check
        bare = [int(round(x["t"] * fps)) for x in check(job, joins_for(job)) if not x["hidden"]]
        zf = int(round(z["sec"] * fps)) if z else 0
        # face stretches get a slow push-in (VSL: the face never sits still). V1 is split under the middle of each
        # b-roll shot, where the split can't be seen, and each face piece eases in from 100% to push["to"].
        push = style.get("aroll", {}).get("face_push")
        hidden = []
        if push:
            from joins import spans
            hidden = [int(round((a + b) / 2 * fps)) for k, a, b, x in spans(job)[0] if x]
        cuts = sorted({c for c in [zf] + bare + hidden + bounds if 0 < c < a_frames})
        if cuts:
            punch = style.get("aroll", {}).get("jump_punch", 1.0)
            edges = [0] + cuts + [a_frames]
            on, rec = False, t0
            for f0, f1 in zip(edges, edges[1:]):
                r_ = mp.AppendToTimeline([{"mediaPoolItem": aroll, "startFrame": src_f(f0), "endFrame": src_f(f0) + (f1 - f0), "trackIndex": 1,
                                           "recordFrame": rec, "mediaType": 1}])
                if not r_:
                    sys.exit(f"could not lay A-roll piece {f0}-{f1}")
                rec = r_[0].GetEnd()
                if f0 in bare:
                    on = not on
                if on and punch != 1.0:
                    r_[0].SetProperty({"ZoomX": punch, "ZoomY": punch})
                if push and f0 >= zf and f1 - f0 >= push.get("min_sec", 3) * fps:
                    pc = r_[0].AddFusionComp()
                    pmi, pmo = pc.FindTool("MediaIn1"), pc.FindTool("MediaOut1")
                    ptr = pc.AddTool("Transform", -32768, -32768)
                    ptr.Input = pmi.Output
                    pmo.Input = ptr.Output
                    ptr.Size = pc.BezierSpline()
                    g = pc.GetAttrs()["COMPN_RenderStart"]  # clip comps render on 0..n-1; GlobalStart is the source offset
                    n_ = f1 - f0
                    base = punch if on and punch != 1.0 else 1.0
                    if on and punch != 1.0:
                        r_[0].SetProperty({"ZoomX": 1.0, "ZoomY": 1.0})  # the punch moves into the comp
                    for f in range(0, n_ + 1, 5):
                        x = f / n_
                        ptr.Size[g + f] = base * (1 + (push["to"] - 1) * (x * x * (3 - 2 * x)))
                if f0 == 0 and zf:
                    # fast zoom-out with motion blur, keyframed in Fusion on the source itself (no slices, no
                    # re-encode: both caused flashes or a brightness jump before)
                    comp = r_[0].AddFusionComp()
                    mi, mo = comp.FindTool("MediaIn1"), comp.FindTool("MediaOut1")
                    tr = comp.AddTool("Transform", -32768, -32768)
                    tr.Input = mi.Output
                    mo.Input = tr.Output
                    tr.Size = comp.BezierSpline()
                    g0 = comp.GetAttrs()["COMPN_RenderStart"]
                    for f in range(zf + 1):
                        tr.Size[g0 + f] = 1 + (z["from"] - 1) * (1 - f / zf) ** 3
                    if z.get("motion_blur", True):
                        tr.MotionBlur = 1
                        tr.Quality = 8
                        tr.ShutterAngle = z.get("shutter", 180)
            if keep_f:
                rec_a = t0
                for a, b in keep_f:
                    mp.AppendToTimeline([{"mediaPoolItem": aroll, "startFrame": a, "endFrame": b, "trackIndex": 1,
                                          "recordFrame": rec_a, "mediaType": 2}])
                    rec_a += b - a
            else:
                mp.AppendToTimeline([{"mediaPoolItem": aroll, "startFrame": 0, "endFrame": a_frames, "trackIndex": 1,
                                      "recordFrame": t0, "mediaType": 2}])
        else:
            mp.AppendToTimeline([{"mediaPoolItem": aroll, "startFrame": 0, "endFrame": a_frames, "trackIndex": 1, "recordFrame": t0}])
    # A-roll audio: level match quiet recordings, background-noise reduction on the dialogue track
    gain = plan.get("aroll_gain_db", 0)
    for it in t.GetItemListInTrack("audio", 1) or []:
        if gain:
            it.SetProperty({"AudioVolumeEnabled": True, "AudioVolume": float(gain)})
    vi = plan.get("voice_isolation")
    if vi:
        t.SetVoiceIsolationState(1, {"isEnabled": True, "amount": int(vi)})
    # music bed: original file from its first frame, trimmed to length, kept low
    mus = plan.get("music")
    if mus:
        mbin = sub("music")
        mp.SetCurrentFolder(mbin)
        mi_ = find_clip(mbin, os.path.basename(mus["path"])) or mp.ImportMedia([mus["path"]])[0]
        t.AddTrack("audio", "stereo")
        tl_len = t.GetEndFrame() - t0
        m_fps = float(mi_.GetClipProperty("FPS") or fps) or fps
        res = mp.AppendToTimeline([{"mediaPoolItem": mi_, "startFrame": int(mus.get("start", 0) * m_fps),
                                    "endFrame": int(mus.get("start", 0) * m_fps + tl_len * m_fps / fps),
                                    "trackIndex": t.GetTrackCount("audio"), "recordFrame": t0, "mediaType": 2}])
        if res:
            res[0].SetProperty({"AudioVolumeEnabled": True, "AudioVolume": float(mus["gain_db"])})
            res[0].SetFades({"FadeIn": 0, "FadeOut": int(fps * 0.8)})
    sfx = style.get("intro_zoom", {}).get("sfx") if plan.get("intro_zoom") else None
    if sfx and os.path.exists(sfx["path"]):
        # a whoosh under the opening zoom-out
        mp.SetCurrentFolder(root)
        si = find_clip(root, os.path.basename(sfx["path"])) or mp.ImportMedia([sfx["path"]])[0]
        t.AddTrack("audio", "stereo")
        r_ = mp.AppendToTimeline([{"mediaPoolItem": si, "startFrame": 0, "endFrame": int(float(si.GetClipProperty("Frames") or 10)),
                                   "trackIndex": t.GetTrackCount("audio"), "recordFrame": t0, "mediaType": 2}])
        if r_:
            r_[0].SetProperty({"AudioVolumeEnabled": True, "AudioVolume": float(sfx.get("gain_db", -10))})
    for _ in range(4):
        t.AddTrack("video")
    t.SetTrackName("video", 2, "broll")
    t.SetTrackName("video", 3, "captions")

    segs = plan["segments"]
    # cuts land on the real voice onset, then lead it by a couple of frames so the picture arrives with the word
    on = speech_onsets(f"{job}/audio.wav", words, [s["words"][0] for s in segs])
    lead = style.get("cut_lead_frames", 2) / fps
    def seg_start(k):
        i = segs[k]["words"][0]
        st = on.get(i, words[i]["start"])
        return max(words[i - 1]["start"] + 0.1 if i > 0 else 0.0, st - lead) if k else 0.0
    # segment timing: first word start -> next segment start (captions run continuously), clipped on long pauses
    for k, s in enumerate(segs):
        i0, i1 = s["words"]
        start = seg_start(k)
        end_word = words[i1]["end"]
        nxt = seg_start(k + 1) if k + 1 < len(segs) else end_word + 0.3
        s["_start"] = int(round(start * fps))
        s["_end"] = int(round((nxt if nxt - end_word < 0.6 else end_word + 0.15) * fps))

    # b-roll owns the A-roll joins: a shot meant to cut in or out on a join can miss it by a frame or two after the
    # onset snap, which shows the jump. Pull that edge exactly onto the join (b-roll timing only, captions untouched).
    for s in segs:
        s["_bs"], s["_be"] = s["_start"], s["_end"]
        sw = (s.get("broll") or {}).get("start_word")
        if sw is not None and s["words"][0] < sw <= s["words"][1]:
            # the shot comes in mid-phrase, on a chosen word (e.g. the 1.5s face open), not on the phrase start
            st = speech_onsets(f"{job}/audio.wav", words, [sw]).get(sw, words[sw]["start"])
            s["_bs"] = int(round(max(words[sw - 1]["start"] + 0.1, st - lead) * fps))
    from joins import joins_for as _jf
    for j in _jf(job):
        J = int(round(j * fps))
        shots = [s for s in segs if s.get("broll")]
        if any(s["_bs"] <= f < s["_be"] for s in shots for f in (J - 1, J)):
            continue
        near = min(shots, key=lambda s: min(abs(s["_be"] - J), abs(s["_bs"] - J)), default=None)
        if near and abs(near["_be"] - J) <= 8 and near["_be"] <= J:
            near["_be"] = J + 1
        elif near and abs(near["_bs"] - J) <= 8 and near["_bs"] > J:
            near["_bs"] = J

    report = dict(broll=0, broll_fail=[], captions=0, caption_fail=[])
    # b-roll, video only
    for k, s in enumerate(segs):
        b = s.get("broll")
        if not b or b["id"] not in pool:
            if b:
                report["broll_fail"].append(k)
            continue
        c = clips[b["id"]]
        sf = c["fps"] or fps
        n = s["_be"] - s["_bs"]
        src_in = b.get("in")
        if src_in is None:
            src_in = max(0.0, c["dur"] / 2 - n / fps / 2)
        a = int(src_in * sf)
        e = a + int(math.ceil(n / fps * sf))
        res = mp.AppendToTimeline([{"mediaPoolItem": pool[b["id"]], "startFrame": a, "endFrame": e,
                                    "trackIndex": 2, "recordFrame": t0 + s["_bs"], "mediaType": 1}])
        if res:
            ar, r_ = (c.get("w") or 16) / (c.get("h") or 9), W / H
            fill = max(ar / r_, r_ / ar)  # Resolve fits the whole frame in; zoom so it fills, cropping the excess
            if fill > 1.001:
                res[0].SetProperty({"ZoomX": fill, "ZoomY": fill})
            if b.get("x") is not None and ar > r_:  # subject's horizontal position in the source (0..1) -> keep it in frame
                res[0].SetProperty({"Pan": float(-(b["x"] - 0.5) * W * fill)})
            report["broll"] += 1
            t.AddMarker(s["_bs"], "Blue", f"B{k}", f'{s["caption"]} -> {os.path.basename(c["path"])}: {b.get("why", "")}', 1)
        else:
            report["broll_fail"].append(k)

    # captions
    modes = style["captions"]["modes"]
    scale = W / style["captions"]["ref_width"]
    stack_n = 0
    # key-word lines (plan 'kw'): the key words big on top, the rest of the line smaller underneath
    csegs = []
    for s in segs:
        kw = (s.get("kw") or "").strip()
        if kw and s.get("mode") != "hook" and kw.lower() in s["caption"].lower():
            i = s["caption"].lower().index(kw.lower())
            rest = re.sub(r"\s+([,.?!])", r"\1", (s["caption"][:i] + " " + s["caption"][i + len(kw):]).strip())
            rest = re.sub(r"\s{2,}", " ", rest).strip(" ,.")
            first = i == 0  # reading order: whichever part is said first sits on top
            csegs.append(dict(s, caption=kw, _kw="big", _top=first or not rest))
            if rest:
                csegs.append(dict(s, caption=rest, _kw="small", _top=not first))
        else:
            csegs.append(s)
    for k, s in enumerate(csegs):
        if not s["caption"].strip():  # words kept in the audio but deliberately not captioned
            continue
        mode = plan.get("caption_force") or s.get("mode") or ("over_broll" if s.get("broll") else "over_aroll")
        if mode == "stack" and len(s["caption"].split()) > modes["stack"].get("max_words", 3):
            mode = "over_broll" if s.get("broll") else "over_aroll"
        if mode == "stack" and modes["stack"].get("as"):  # a style can retire side stacks (Kyle: they hit his face)
            mode = modes["stack"]["as"]
        m = modes[mode]
        track = 3
        tilt = m["tilt"]
        if mode == "hook":
            hk = [j for j, x in enumerate(csegs) if x.get("mode") == "hook"]
            pos = hk.index(k)
            track = m["tracks"][min(pos, len(m["tracks"]) - 1)]
            # bottom-anchored: the last hook line always sits on the lowest slot, so short hooks stay low (off the face)
            tilt = m["tilt"][max(0, len(m["tilt"]) - len(hk)) + min(pos, len(m["tilt"]) - 1)] if len(hk) <= len(m["tilt"]) else m["tilt"][min(pos, len(m["tilt"]) - 1)]
            s["_end"] = csegs[hk[-1]]["_end"]
        elif mode == "stack":
            track = m["tracks"][min(stack_n, len(m["tracks"]) - 1)]
            tilt = m["tilt"][min(stack_n, len(m["tilt"]) - 1)]
            stack_n += 1
        if mode != "stack":
            stack_n = 0
        # fit inside the safe area: centred captions get 86% of the width, side stacks their half of the frame
        # The title draws on its own W-wide canvas BEFORE the timeline zoom, so fitting must shrink the font
        # (else long lines are clipped at the canvas edge). f = font scale vs the template's 0.08.
        zoom = m["zoom"]
        kwc = style["captions"].get("keyword", {"scale": 1.7, "up": 70, "down": 95})
        if s.get("_kw"):
            base = tilt if not isinstance(tilt, list) else tilt[0]
            if s["_kw"] == "big":
                zoom *= kwc["scale"]
            else:
                track = 4
            tilt = base + (kwc["up"] if s["_top"] else -kwc["down"])
        pan = m["pan"] * scale
        safe = W * 0.86 if not pan else 2 * (W / 2 - abs(pan)) - 0.06 * W
        tw = text_width(s["caption"]) * scale
        f = min(1.0, safe / (tw * zoom), 0.92 * W / tw)
        d = s["_end"] - s["_start"]
        if d < 2:
            continue
        span = max(1, int(d * carrier_fps / fps))
        item, tried = None, set()
        for attempt in range(6):
            if span in tried:
                break
            tried.add(span)
            res = mp.AppendToTimeline([{"mediaPoolItem": carrier, "startFrame": 0, "endFrame": span,
                                        "trackIndex": track, "recordFrame": t0 + s["_start"]}])
            item = res[0] if res else None
            if not item:
                break
            got = item.GetDuration()
            if d - 2 <= got <= d:  # never overlap the next caption; 1-2 frames short is invisible
                break
            t.DeleteClips([item])
            item = None
            span += 1 if got < d - 2 else -1
        if not item:
            report["caption_fail"].append(k)
            continue
        src = template.replace('Value = "you have to give"', f'Value = "{fusion_str(s["caption"])}"')
        src = re.sub(r'(\t*Font = Input \{ Value = "[^"]+", \},)', lambda mo: mo.group(1) + f'\n\t\t\t\tSize = Input {{ Value = {0.08 * f:.4f}, }},', src, count=1)
        if mode == "hook":
            src = hook_look(src, style["captions"]["modes"]["hook"], k == hk[-1])
        cp = f"{job}/comps/{k:03d}.comp"
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        open(cp, "w", encoding="utf-8").write(src)
        item.ImportFusionComp(cp)
        names = item.GetFusionCompNameList() or []
        if len(names) > 1:
            item.LoadFusionCompByName(names[-1])
            for nm in names[:-1]:
                item.DeleteFusionCompByName(nm)
        item.SetProperty({"ZoomX": zoom, "ZoomY": zoom, "Pan": pan, "Tilt": tilt * scale})
        if style["captions"].get("composite_mode") is not None:  # e.g. Difference: white letters show the video in negative
            item.SetProperty("CompositeMode", style["captions"]["composite_mode"])
        report["captions"] += 1

    p.SetCurrentTimeline(t)
    pm.SaveProject()
    report["timeline"] = plan["timeline"]
    report["project"] = name
    json.dump(report, open(f"{job}/build_report.json", "w"), indent=1)
    print(json.dumps(report))


if __name__ == "__main__":
    main(sys.argv[1])
