"""Motion cards behind the speaker: an image (IG header, screenshot, logo...) fades and lifts into place behind
their head on a trigger word and leaves after an end word. Built inside each A-roll piece's own Fusion comp, before
the face push-in, so it moves with the shot:
  MediaIn -> Merge(card, rounded mask) [-> next card] -> Merge(speaker cut out from DepthMap) -> Transform1 -> out
extras.json: "cards": [{"image": path, "from_word": "Andrew", "to_word": "mind", "y": 0.70, "width": 0.94,
                        "depth": [0.28, 0.30]}]
  from_word / to_word: first word whose text starts with it (case-insensitive); to_word searched after from_word.
  y: settled centre (Fusion, y-up). Put it so the card's bottom edge tucks just behind the hair, never the face.
  depth: DepthMap -> alpha ramp for the cutout. Check once per setup with a still of the depth pass.
Run after build (and after silences.py, it reads the cut words). Usage: python3 cards.py <job>"""
import json, os
from PIL import Image
from _common import job_dir, extras, FPS
from resolve import connect

job = job_dir(); X = extras(job); W_ = json.load(open(os.path.join(job, "words.json")))
CARDS = []
for k, cd in enumerate(X.get("cards", [])):
    ia = next(i for i, w in enumerate(W_) if w["w"].lower().startswith(cd["from_word"].lower()))
    ib = next(i for i in range(ia, len(W_)) if W_[i]["w"].lower().strip(",.?!").startswith(cd["to_word"].lower()))
    IN = W_[ia]["start"] - 0.12; OUT = W_[ib]["end"] + 0.1
    iw, ih = Image.open(cd["image"]).size
    CARDS.append(dict(cd, k=k, IN=IN, UP=IN + 0.38, OUT=OUT, DOWN=OUT - 0.3, iw=iw, ih=ih))


def apply(it, t0, cards):
    c = it.GetFusionCompByIndex(1) or it.AddFusionComp()
    p0 = it.GetStart() - t0
    g = c.GetAttrs()["COMPN_RenderStart"]  # clip comps render on 0..n-1 (NOT GlobalStart)
    fr = lambda sec: g + round(sec * FPS) - p0
    W = float(c.GetPrefs("Comp.FrameFormat.Width") or 2160); H = float(c.GetPrefs("Comp.FrameFormat.Height") or 3840)
    for tl in list(c.GetToolList().values()):
        if tl.Name.startswith("Card"):
            tl.Delete()
    mi, out = c.FindTool("MediaIn1"), (c.FindTool("Transform1") or c.FindTool("MediaOut1"))
    c.Lock()
    src = mi
    for cd in cards:
        n = f"Card{cd['k']}"
        ld = c.AddTool("Loader", -32768, -32768); ld.SetAttrs({"TOOLS_Name": n + "Img"}); ld.Clip = cd["image"]
        wd = cd.get("width", 0.94)
        mk = c.AddTool("RectangleMask", -32768, -32768); mk.SetAttrs({"TOOLS_Name": n + "Mask"})
        mk.Width = wd; mk.Height = wd * W / H * cd["ih"] / cd["iw"]; mk.CornerRadius = 0.12  # height is vs frame HEIGHT
        mg = c.AddTool("Merge", -32768, -32768); mg.SetAttrs({"TOOLS_Name": n + "Merge"})
        mg.Background = src.Output; mg.Foreground = ld.Output; mg.Size = wd * W / cd["iw"]; mg.EffectMask = mk.Mask
        y1 = cd.get("y", 0.70); y0 = y1 - 0.05
        fa, fb, fc, fd = fr(cd["IN"]), fr(cd["UP"]), fr(cd["DOWN"]), fr(cd["OUT"])
        # numbers in brackets: a negative frame would otherwise read 'time--18' and black out the comp
        ease = f"(1-(1-min(max((time-({fa}))/{fb - fa},0),1))^3)"
        y = f"({y0}+({y1}-{y0})*{ease}-0.02*min(max((time-({fc}))/{fd - fc},0),1))"
        mg.Center.SetExpression(f"Point(0.5, {y})"); mk.Center.SetExpression(f"Point(0.5, {y})")
        mg.Blend.SetExpression(f"min(max((time-({fa}))/{max(fb - fa, 1) * 0.6},0),1)*(1-min(max((time-({fc}))/{fd - fc},0),1))")
        src = mg
    lo, hi = cards[0].get("depth", [0.28, 0.30])
    dm = c.AddTool("DepthMap", -32768, -32768); dm.SetAttrs({"TOOLS_Name": "CardDepth"}); dm.Input = mi.Output
    try:
        dm.SetInput("Mode", "Faster")
    except Exception:
        pass
    cu = c.AddTool("Custom", -32768, -32768); cu.SetAttrs({"TOOLS_Name": "CardCut"})
    cu.Image1 = mi.Output; cu.Image2 = dm.Output
    cu.SetInput("NumberIn1", lo); cu.SetInput("NumberIn2", hi)
    cu.SetInput("Intermediate1", "min(max((r2-n1)/(n2-n1),0),1)")
    for ch in ("Red", "Green", "Blue"):
        cu.SetInput(ch + "Expression", f"{ch[0].lower()}1*i1")
    cu.SetInput("AlphaExpression", "i1")
    cm = c.AddTool("Merge", -32768, -32768); cm.SetAttrs({"TOOLS_Name": "CardCutMerge"})
    cm.Background = src.Output; cm.Foreground = cu.Output
    out.Input = cm.Output
    c.Unlock()
    print("cards", [cd["k"] for cd in cards], "in piece", round(p0 / FPS, 2), "->", round((it.GetEnd() - t0) / FPS, 2))


r = connect(); t = r.GetProjectManager().GetCurrentProject().GetCurrentTimeline(); t0 = t.GetStartFrame()
for it in t.GetItemListInTrack("video", 1) or []:
    a, b = (it.GetStart() - t0) / FPS, (it.GetEnd() - t0) / FPS
    hit = [cd for cd in CARDS if cd["IN"] < b and cd["OUT"] > a]
    if hit:
        apply(it, t0, hit)
r.GetProjectManager().SaveProject()
