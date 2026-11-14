"""Prep a phone dump for a story sequence.

    python3 prep.py "<phone folder>" <job dir> [video stem@seconds ...]

1. Sorts loose files in the phone folder into images/ and videos/ (moves only top-level files, never deletes).
2. Writes full-res JPGs (HEIC converted with sips, EXIF rotation applied) to <job>/full/  -> render.py input
3. Writes 1080px web copies to <job>/pub/photos/<stem lowercase>.jpg                     -> published with the page
4. Optional stills from videos: IMG_2520@1.35 grabs that frame as v2520.
Prints the photo stems for the doc's "photos" list.
"""
import os, shutil, subprocess, sys
from PIL import Image, ImageOps

IMG = {".heic", ".jpg", ".jpeg", ".png"}
VID = {".mov", ".mp4", ".m4v"}
src, job = sys.argv[1], os.path.expanduser(sys.argv[2])
full, pub = os.path.join(job, "full"), os.path.join(job, "pub", "photos")
for d in (os.path.join(src, "images"), os.path.join(src, "videos"), full, pub):
    os.makedirs(d, exist_ok=True)
for f in os.listdir(src):
    p, ext = os.path.join(src, f), os.path.splitext(f)[1].lower()
    if os.path.isfile(p) and not f.startswith("."):
        if ext in IMG: shutil.move(p, os.path.join(src, "images", f))
        elif ext in VID: shutil.move(p, os.path.join(src, "videos", f))
stems = []
for f in sorted(os.listdir(os.path.join(src, "images"))):
    if f.startswith("."): continue
    stem = os.path.splitext(f)[0]; out = os.path.join(full, stem + ".jpg")
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "92", os.path.join(src, "images", f), "--out", out],
                   capture_output=True)
    stems.append(stem)
for arg in sys.argv[3:]:
    v, t = arg.split("@"); vf = [x for x in os.listdir(os.path.join(src, "videos")) if x.startswith(v)][0]
    stem = "v" + v.split("_")[-1]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", os.path.join(src, "videos", vf), "-frames:v", "1",
                    "-q:v", "2", os.path.join(full, stem + ".jpg")])
    stems.append(stem)
for stem in stems:
    im = ImageOps.exif_transpose(Image.open(os.path.join(full, stem + ".jpg"))).convert("RGB")
    im.save(os.path.join(full, stem + ".jpg"), quality=95)          # bake the rotation into the full-res copy
    im.thumbnail((1080, 1920)); im.save(os.path.join(pub, stem.lower() + ".jpg"), quality=82, optimize=True)
print("photos:", [s.lower() for s in stems])
