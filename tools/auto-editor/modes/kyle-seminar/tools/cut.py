# Snap segments to real word boundaries, pad by measured voice energy, audit joins.
import json,csv,os,sys,wave,math,re,glob
import numpy as np
S=os.path.dirname(os.path.abspath(__file__))
FPS={}
def words(src):
    W=[]
    for r in csv.DictReader(open(f"{S}/w2/{src}.csv")):
        t=r["text"].strip()
        if re.sub(r"[^\w']","",t): W.append([int(r["start"])/1000,int(r["end"])/1000,t])
    return W
_A={}
def audio(src):
    if src not in _A:
        w=wave.open(f"{S}/w2/{src}.wav"); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
        n=160; f=len(x)//n; _A[src]=np.sqrt((x[:f*n].reshape(f,n)**2).mean(1)+1e-12)  # 10ms RMS
    return _A[src]
def rms_at(r,t): i=int(t*100); return r[min(max(i,0),len(r)-1)]
def resolve(src,frm,to):
    W=words(src); r=audio(src)
    i=min(range(len(W)),key=lambda k:abs(W[k][0]-frm)); j=min(range(len(W)),key=lambda k:abs(W[k][1]-to))
    s,e=W[i][0],W[j][1]; pe=W[i-1][1] if i>0 else 0.0; ns=W[j+1][0] if j+1<len(W) else e+2
    seg=r[max(0,int((s-4)*100)):int((e+4)*100)]; thr=float(np.percentile(seg,10))*2.5
    t=s
    while t>max(pe+0.02,s-0.25) and rms_at(r,t-0.01)>thr: t-=0.01
    a=max(pe+0.01,t-0.04)
    t=e
    while t<min(ns-0.03,e+0.6) and rms_at(r,t)>thr: t+=0.01
    b=min(ns-0.02,max(t+0.08,e+0.12))
    warn=[]
    gp=s-pe; gn=ns-e
    if i>0 and not re.search(r"[.?!]$",W[i-1][2]) and gp<0.35: warn.append(f"IN mid-sentence after '{W[i-1][2]}' gap {gp:.2f}")
    if not re.search(r"[.?!]$",W[j][2]) and gn<0.35: warn.append(f"OUT mid-sentence before '{W[j+1][2] if j+1<len(W) else ''}' gap {gn:.2f}")
    if gn<0.15: warn.append(f"OUT tail tight: next word {gn:.2f}s after")
    txt=" ".join(w[2] for w in W[i:j+1])
    return round(a,3),round(b,3),txt,warn
if __name__=="__main__":
    ids=sys.argv[1:]
    for p in sorted(glob.glob(f"{S}/edl3/*.spec.json")):
        if ids and os.path.basename(p).split(".")[0] not in ids: continue
        e=json.load(open(p)); out={"id":e["id"],"title":e["title"],"short":[],"pulls":e.get("pulls",[])}
        print(f"== {e['id']} {e['title']}")
        tot=0
        for sg in e["short"]:
            a,b,txt,w=resolve(sg["src"],sg["from"],sg["to"]); tot+=b-a
            out["short"].append({"src":sg["src"],"in":a,"out":b,"role":sg.get("role",""),"text":txt})
            print(f"  {sg.get('role',''):8} {a:7.2f}-{b:7.2f} | {txt}")
            for x in w: print(f"      !! {x}")
        print(f"  total {tot:.1f}s")
        json.dump(out,open(p.replace(".spec.json",".json"),"w"),indent=1)
