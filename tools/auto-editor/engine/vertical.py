"""9:16 deliverable from a finished 16:9 reel: the reel letterboxed in the middle of a 1080x1920 frame, with the
reel's headline in white Helvetica Bold in the top bar, bottom-aligned just above the picture. Audio is copied as is
(run finish.py on the 16:9 first). Same layout as the first Kyle 9:16 batch in his Frame.
Usage: python3 vertical.py <in.mp4> "<headline>" <out.mp4>"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safezone

W, H = 1080, 1920
VID_TOP = (H - round(W * 9 / 16)) // 2  # 656


def header(text, png):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for size in range(78, 40, -2):
        f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size, index=1)
        lines = []
        for sent in [s.strip() for s in text.replace(". ", ".|").split("|") if s.strip()]:
            cur = ""
            for w in sent.split():
                t = (cur + " " + w).strip()
                if d.textlength(t, font=f) <= 940:
                    cur = t
                else:
                    lines.append(cur)
                    cur = w
            lines.append(cur)
        # avoid a lone last word: pull one word down from the previous line
        if len(lines) > 1 and len(lines[-1].split()) == 1 and not lines[-2].endswith('.'):
            a = lines[-2].split()
            lines[-2] = " ".join(a[:-1])
            lines[-1] = a[-1] + " " + lines[-1]
        if len(lines) <= 4:
            break
    lh = int(size * 1.18)
    y = VID_TOP - 60 - lh * len(lines)
    wmax = max(d.textlength(l, font=f) for l in lines)
    why = safezone.check("headline", (W - wmax) / 2, y, (W + wmax) / 2, VID_TOP - 60)
    if why:
        sys.exit(why + " (SOP 07): shorten the headline")
    for l in lines:
        d.text(((W - d.textlength(l, font=f)) / 2, y), l, font=f, fill=(255, 255, 255, 255))
        y += lh
    im.save(png)


def vertical(src, text, out):
    png = os.path.join(tempfile.mkdtemp(), "header.png")
    header(text, png)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-loop", "1", "-i", png, "-filter_complex",
                    f"[0:v]scale={W}:-2:flags=lanczos,pad={W}:{H}:0:{VID_TOP}:black[v];[v][1:v]overlay=0:0:shortest=1,format=yuv420p",
                    "-map", "0:a:0", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                    "-c:a", "copy", "-map_metadata", "-1", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    vertical(sys.argv[1], sys.argv[2], sys.argv[3])
    print("vertical", os.path.basename(sys.argv[3]))
