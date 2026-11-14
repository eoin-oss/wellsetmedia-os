#!/usr/bin/env python3
"""Generate a whole 10/10 habits video's overlays in one go.

  python3 generate.py 01          # make more money
  python3 generate.py --list      # what's defined
  python3 generate.py --set eoin E1   # Eoin's own set (videos_eoin.py, b-roll/eoin/, output/eoin/)

Reads the locked scripts from videos.py, pulls b-roll from b-roll/<slug>/,
writes transparent PNGs to output/<slug>/.

Images are assigned darkest-first for the cover grid (so it reads as one
image) and spread across the items (so the video keeps moving).
"""
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "tools"))
sys.path.insert(0, str(HERE))

from overlay import build, build_item          # noqa: E402
from videos import VIDEOS                      # noqa: E402
import videos_eoin                              # noqa: E402

SETS = {"morelife": (VIDEOS, ""), "eoin": (videos_eoin.VIDEOS, "eoin")}
SUB = ""
from PIL import Image, ImageStat               # noqa: E402


def ranked(folder):
    """Images sorted by brightness — mid-range first, extremes last."""
    out = []
    for f in sorted(folder.glob("*.jpg")):
        try:
            out.append((abs(ImageStat.Stat(Image.open(f).convert("L")).mean[0] - 45), f))
        except Exception:
            pass
    return [f for _, f in sorted(out)]


def run(key):
    v = VIDEOS[key]
    src = HERE / "b-roll" / SUB / v["slug"]
    dst = HERE / "output" / SUB / v["slug"]
    dst.mkdir(parents=True, exist_ok=True)
    for old in dst.glob("*.png"):
        old.unlink()

    imgs = ranked(src)
    if len(imgs) < 7:
        print(f"!  only {len(imgs)} images in {src.name} — need 14 for a full set")

    cover = [src / c for c in v["cover"]] if v.get("cover") else imgs[:6]  # hand-picked cover grid
    build(v["title"], v.get("sub", ""), [str(i) for i in cover], str(dst / "00 cover.png"))
    print(f"00 cover")

    pool = imgs[6:] or imgs
    picks = v.get("images")  # hand-picked, one per item: the image must show what the line says
    for n, line in enumerate(v["items"], 1):
        img = src / picks[n - 1] if picks else pool[(n - 1) % len(pool)]
        build_item(n, line, str(img), str(dst / f"{n:02d}.png"))
        print(f"{n:02d}  {line[:52]}")

    print(f"\n-> {dst}")


if __name__ == "__main__":
    if "--set" in sys.argv:
        i = sys.argv.index("--set")
        VIDEOS, SUB = SETS[sys.argv[i + 1]]
        del sys.argv[i:i + 2]
    if len(sys.argv) < 2 or sys.argv[1] == "--list":
        for k, v in VIDEOS.items():
            state = "ready" if v["items"] else "NO ITEMS YET"
            print(f"  {k}  {v['title'][:56]:58} {state}")
        sys.exit(0)
    run(sys.argv[1])
