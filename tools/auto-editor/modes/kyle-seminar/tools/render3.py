# ProRes HQ, constant frame rate, frame-aligned cuts, 8ms audio fades at joins.
import json,sys,subprocess,os,glob,math
S=os.path.dirname(os.path.abspath(__file__))
B="/Volumes/Extreme SSD/wellsetmedia/kyle-seminar-pulls"; RAW=f"{B}/raw"; OUT=f"{B}/shorts-v2"; os.makedirs(OUT,exist_ok=True)
def rawpath(src): return next(p for p in glob.glob(f"{RAW}/{src}.*") if not os.path.basename(p).startswith("._"))
def info(p):
    o=json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=height,r_frame_rate,pix_fmt","-of","json",p],capture_output=True,text=True).stdout)["streams"][0]
    n,d=map(int,o["r_frame_rate"].split("/")); return o["height"],n,d,o["pix_fmt"]
def mainch(p):
    # pick the louder channel: stage cams record speech on one side only
    r=subprocess.run(["ffmpeg","-nostdin","-v","info","-t","120","-i",p,"-map","0:a:0","-af","astats=measure_overall=none:measure_perchannel=RMS_level","-f","null","-"],capture_output=True,text=True).stderr
    lv=[float(l.split(":")[-1]) if "inf" not in l else -999 for l in r.splitlines() if "RMS level dB" in l]
    return 1 if len(lv)>1 and lv[1]>lv[0]+6 else 0 if len(lv)>1 and lv[0]>lv[1]+6 else None
def render(segs,out):
    srcs=[]
    for s,_,_ in segs:
        if s not in srcs: srcs.append(s)
    I={s:info(rawpath(s)) for s in srcs}
    CH={s:mainch(rawpath(s)) for s in srcs}
    h=max(v[0] for v in I.values()); n,d=I[srcs[0]][1],I[srcs[0]][2]; fps=n/d
    fc=[]
    for i,(s,a,b) in enumerate(segs):
        k=srcs.index(s); fa=math.floor(a*fps); fb=math.ceil(b*fps); ta=fa/fps; tb=fb/fps; dur=tb-ta
        sc=f",scale=-2:{h}" if I[s][0]!=h else ""
        c=CH[s]; pan=f"pan=stereo|c0=c{c}|c1=c{c}," if c is not None else ""
        fc.append(f"[{k}:v:0]fps={n}/{d},trim=start_frame={fa}:end_frame={fb},setpts=PTS-STARTPTS{sc},format=yuv422p10le[v{i}]")
        fc.append(f"[{k}:a:0]aresample=48000,atrim=start={ta:.6f}:end={tb:.6f},asetpts=PTS-STARTPTS,{pan}aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:d=0.008,afade=t=out:st={max(dur-0.008,0):.6f}:d=0.008[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(len(segs)))+f"concat=n={len(segs)}:v=1:a=1[v][a]")
    cmd=["ffmpeg","-nostdin","-v","error","-y"]
    for s in srcs: cmd+=["-i",rawpath(s)]
    cmd+=["-filter_complex",";".join(fc),"-map","[v]","-map","[a]","-r",f"{n}/{d}","-fps_mode","cfr","-c:v","prores_videotoolbox","-profile:v","hq","-c:a","pcm_s24le",out]
    r=subprocess.run(cmd,capture_output=True,text=True)
    print(("OK " if r.returncode==0 else "FAIL ")+os.path.basename(out)+(" "+r.stderr[-400:] if r.returncode else ""),flush=True)
for i in sys.argv[1:]:
    e=json.load(open(f"{S}/edl3/{i}.json"))
    slug=e["title"].lower().replace(" ","-").replace("/","-").replace("'","").replace(",","")
    render([(s["src"],s["in"],s["out"]) for s in e["short"]],f"{OUT}/{e['id']}_{slug}.mov")
