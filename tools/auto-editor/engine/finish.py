"""Deliverable pass on rendered mp4s: drop Resolve's timecode data track (some phone players choke on it), true-peak
limit to -1 dBTP so loud words never clip, keep the picture untouched.
Usage: python3 finish.py <in.mp4> [...] -> writes next to each as <name>_final.mp4 ... then replaces the original"""
import os, subprocess, sys

for src in sys.argv[1:]:
    tmp = src[:-4] + ".finish.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
                    "-af", "alimiter=limit=0.84:level=false:attack=3:release=50", "-c:a", "aac", "-b:a", "256k",
                    "-write_tmcd", "0", "-map_metadata", "-1", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, src)
    print("finished", os.path.basename(src))
