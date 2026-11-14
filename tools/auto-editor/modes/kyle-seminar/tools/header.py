# Header layer for 9:16 letterbox: white Helvetica Bold in the top bar, bottom-aligned just above the video.
import sys,subprocess,json
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920; VID_TOP=(H-round(W*9/16))//2  # 656
def make(text,png):
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for size in range(78,40,-2):
        f=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",size,index=1)
        lines=[]
        for sent in [s.strip() for s in text.replace(". ",".|").split("|") if s.strip()]:
            cur=""
            for w in sent.split():
                t=(cur+" "+w).strip()
                if d.textlength(t,font=f)<=940: cur=t
                else: lines.append(cur); cur=w
            lines.append(cur)
        # avoid a lone last word: pull one word down from the previous line
        if len(lines)>1 and len(lines[-1].split())==1 and not lines[-2].endswith('.'):
            a=lines[-2].split(); lines[-2]=" ".join(a[:-1]); lines[-1]=a[-1]+" "+lines[-1]
        if len(lines)<=4: break
    lh=int(size*1.18); y=VID_TOP-60-lh*len(lines)
    for l in lines:
        x=(W-d.textlength(l,font=f))/2; d.text((x,y),l,font=f,fill=(255,255,255,255)); y+=lh
    im.save(png)
def mov(png,out,dur):
    subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-loop","1","-framerate","25","-i",png,"-t",f"{dur:.3f}","-c:v","prores_ks","-profile:v","4444","-pix_fmt","yuva444p10le","-vendor","apl0",out],check=True)
if __name__=="__main__":
    text,png,out,dur=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]); make(text,png); mov(png,out,dur)
