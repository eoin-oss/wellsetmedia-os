import json,glob,os,subprocess,math,wave,sys
import numpy as np
S=os.path.dirname(os.path.abspath(__file__)); D="/Volumes/Extreme SSD/wellsetmedia/kyle-seminar-pulls/shorts-v2"
for f in sorted(glob.glob(f"{D}/[0-9]*.mov")):
    i=os.path.basename(f)[:2]; e=json.load(open(f"{S}/edl3/{i}.json"))
    w=f"{S}/v4/{i}.wav"; subprocess.run(["ffmpeg","-nostdin","-v","error","-i",f,"-ac","1","-ar","16000","-y",w])
    x=np.frombuffer(wave.open(w).readframes(10**9),dtype=np.int16).astype(np.float32)/32768
    r=np.sqrt((x[:len(x)//160*160].reshape(-1,160)**2).mean(1)+1e-12)
    speech=np.percentile(r,70)
    o=json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=avg_frame_rate,r_frame_rate:format=duration","-of","json",f],capture_output=True,text=True).stdout)
    fr=o["streams"][0]; dur=float(o["format"]["duration"])
    # boundaries: recompute frame-aligned segment lengths
    srcfps=eval(fr["r_frame_rate"]); t=0; bounds=[0]
    for s in e["short"]:
        t+= (math.ceil(s["out"]*srcfps)-math.floor(s["in"]*srcfps))/srcfps; bounds.append(t)
    bad=[]
    for k,b in enumerate(bounds):
        lo=int(max(0,b-0.03)*100); hi=int(min(dur,b+0.03)*100)
        if k==0: lo=0; hi=4
        if k==len(bounds)-1: lo=max(0,len(r)-4); hi=len(r)
        lvl=r[lo:hi].max()/speech if hi>lo else 0
        if lvl>0.45: bad.append(f"{'start' if k==0 else 'end' if k==len(bounds)-1 else 'join'+str(k)}@{b:.2f}s level {lvl:.2f}")
    print(f"{i} {dur:5.1f}s fps {fr['avg_frame_rate']} | " + ("CLEAN" if not bad else "LOUD CUTS: "+"; ".join(bad)))
