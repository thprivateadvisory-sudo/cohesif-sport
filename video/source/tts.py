import os,sys,json,numpy as np,soundfile as sf
sys.path.insert(0,'.'); from script import SEGS
from kokoro_onnx import Kokoro
T=os.environ.get('KOKORO_DIR','.')+'/'
k=Kokoro(T+"kokoro-v1.0.onnx",T+"voices-v1.0.bin")
sr=24000; lead=0.4
out=[np.zeros(int(lead*sr),dtype=np.float32)]; t=lead; tl=[]
for scene,txt,caps,pause in SEGS:
    s,sr=k.create(txt,voice="ff_siwis",speed=1.08,lang="fr-fr")
    s=s.astype(np.float32); idx=np.where(np.abs(s)>0.01)[0]; s=s[max(idx[0]-240,0):idx[-1]+480]
    d=len(s)/sr; w=[len(c.replace('*','')) for c in caps]; tot=sum(w); c0=t; ch=[]
    for c,wi in zip(caps,w):
        dd=d*wi/tot; ch.append({"text":c,"start":round(c0,3),"end":round(c0+dd,3)}); c0+=dd
    tl.append({"scene":scene,"start":round(t,3),"end":round(t+d,3),"caps":ch})
    out+=[s,np.zeros(int(pause*sr),dtype=np.float32)]; t+=d+pause
a=np.concatenate(out); a=a/np.max(np.abs(a))*0.89
sf.write("vo.wav",a,sr)
json.dump({"duration":round(t,3),"segs":tl},open("timeline.json","w"),indent=1,ensure_ascii=False)
# SRT (phrase-level, readable)
def ts(x):h=int(x//3600);m=int(x%3600//60);s=x%60;return f"{h:02}:{m:02}:{int(s):02},{int(round((s%1)*1000)):03}"
caps=[c for s in tl for c in s["caps"]]
with open("sous-titres.srt","w") as f:
    for i,c in enumerate(caps):
        e=min(caps[i+1]["start"],c["end"]+0.6) if i+1<len(caps) else c["end"]+1.2
        f.write(f"{i+1}\n{ts(c['start'])} --> {ts(e)}\n{c['text'].replace('*','')}\n\n")
print("total",t)
