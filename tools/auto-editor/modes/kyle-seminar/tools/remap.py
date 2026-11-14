import json,csv,glob,os,re,difflib,sys
S=os.path.dirname(os.path.abspath(__file__))
def load(p):
    W=[]
    for r in csv.DictReader(open(p)):
        t=re.sub(r"[^a-z0-9']","",r["text"].lower())
        if t: W.append((int(r["start"])/1000,int(r["end"])/1000,t))
    return W
cache={}
def get(src):
    if src not in cache:
        O=load(f"{S}/words/{src}.csv"); N=load(f"{S}/w2/{src}.csv")
        sm=difflib.SequenceMatcher(None,[w[2] for w in O],[w[2] for w in N],autojunk=False)
        mp={}
        for a,b,n in sm.get_matching_blocks():
            for k in range(n): mp[a+k]=b+k
        cache[src]=(O,N,mp)
    return cache[src]
def near(mp,i,step,lim):
    for d in range(0,8):
        j=i+d*step
        if j in mp and 0<=j<lim: return mp[j],d
    return None,None
log=[]
def fix_in(src,a):
    O,N,mp=get(src)
    i=next((k for k in range(len(O)) if O[k][0]>=a-0.01),len(O)-1)
    j,d=near(mp,i,1,len(O))
    if j is None: log.append(f"  UNMAPPED in {src} {a}"); return a
    if d: log.append(f"  in {src} {a}: '{O[i][2]}' unmatched, snapped {d} words later to '{N[j][2]}'")
    prev=N[j-1][1] if j>0 else 0
    gap=N[j][0]-prev
    return round(max(prev+min(gap/2,0.08) if gap>0 else N[j][0]-0.02, 0),3) if gap<0.16 else round(N[j][0]-0.08,3)
def fix_out(src,b):
    O,N,mp=get(src)
    i=max((k for k in range(len(O)) if O[k][1]<=b+0.01),default=0)
    j,d=near(mp,i,-1,len(O))
    if j is None: log.append(f"  UNMAPPED out {src} {b}"); return b
    if d: log.append(f"  out {src} {b}: '{O[i][2]}' unmatched, snapped {d} words earlier to '{N[j][2]}'")
    nxt=N[j+1][0] if j+1<len(N) else N[j][1]+1
    gap=nxt-N[j][1]
    return round(N[j][1]+min(0.15,gap/2) if gap>0 else N[j][1]+0.02,3)
for p in sorted(glob.glob(f"{S}/edl/*.json")):
    e=json.load(open(p)); log.append(e["id"])
    for pl in e["pulls"]:
        pl["segments"]=[[fix_in(pl["src"],a),fix_out(pl["src"],b)] for a,b in pl["segments"]]
    for s in e["short"]["segments"]:
        o=(s["in"],s["out"]); s["in"]=fix_in(s["src"],max(0,s["in"])); s["out"]=fix_out(s["src"],s["out"])
        if abs(o[0]-s["in"])>0.25 or abs(o[1]-s["out"])>0.25: log.append(f"  short {s['role']}: {o} -> {(s['in'],s['out'])}")
    json.dump(e,open(f"{S}/edl2/{e['id']}.json","w"),indent=1)
print("\n".join(log))
