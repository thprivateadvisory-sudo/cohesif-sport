import sys,json,numpy as np,soundfile as sf
from scipy.signal import butter,sosfilt
sr=44100; tl=json.load(open('timeline.json')); S=tl['segs']; D=tl['duration']
N=int((D+0.3)*sr); t=np.arange(N)/sr
rng=np.random.default_rng(7)
def lp(x,f,o=4):return sosfilt(butter(o,f,'low',fs=sr,output='sos'),x)
def hp(x,f,o=4):return sosfilt(butter(o,f,'high',fs=sr,output='sos'),x)
def bp(x,a,b):return sosfilt(butter(2,[a,b],'band',fs=sr,output='sos'),x)
mus=np.zeros(N)
bpm=100; beat=60/bpm
# chords (Am F C G), 2 bars each
hz=lambda m:440*2**((m-69)/12)
prog=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]
bass=[45,41,48,43]
bar=4*beat
for k in range(int(D/ (2*bar))+2):
    ch=prog[k%4]; st=k*2*bar; en=st+2*bar
    i0,i1=int(st*sr),min(int(en*sr),N)
    if i0>=N:break
    tt=t[i0:i1]-st; env=np.minimum(1,tt/0.6)*np.minimum(1,(2*bar-tt)/0.5)
    pad=sum(np.sin(2*np.pi*hz(m)*tt*d+rng.random()*6) for m in ch for d in (0.997,1.003))
    mus[i0:i1]+=0.035*env*pad
    # bass pulse on 8ths
    b=hz(bass[k%4]-12)
    for j in range(16):
        s=st+j*beat/2; a=int(s*sr)
        if a>=N:break
        L=min(int(0.22*sr),N-a); x=np.arange(L)/sr
        mus[a:a+L]+=0.09*np.sin(2*np.pi*b*x)*np.exp(-x*9)
# drums: kick on beats, hat on offbeats, clap on 2&4 — start after hook
start_drums=S[2]['start']-0.2
nb=int(D/beat)+1
for j in range(nb):
    s=j*beat
    if s<start_drums or s>D-1.2:continue
    a=int(s*sr);L=min(int(.35*sr),N-a);x=np.arange(L)/sr
    f=45+90*np.exp(-x*30); mus[a:a+L]+=0.30*np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-x*9)
    h=int((s+beat/2)*sr)
    if h<N-3000:
        L=min(int(.06*sr),N-h);mus[h:h+L]+=0.05*hp(rng.standard_normal(L),7000)*np.exp(-np.arange(L)/sr*60)
    if j%2==1:
        L=min(int(.18*sr),N-a);mus[a:a+L]+=0.07*bp(rng.standard_normal(L),900,3500)*np.exp(-np.arange(L)/sr*22)
# master music filter-in during hook
mus*=np.clip(0.35+0.65*(t-start_drums)/0.5,0.35,1)
fx=np.zeros(N)
def whoosh(at,dur=0.5,g=0.10):
    a=int((at-dur*0.7)*sr);L=int(dur*sr)
    if a<0:return
    n=rng.standard_normal(L);x=np.linspace(0,1,L)
    y=np.zeros(L)
    for q in range(8):
        seg=slice(q*L//8,(q+1)*L//8); y[seg]=bp(n,300+q*500,900+q*900)[seg]
    fx[a:a+L]+=g*y*np.sin(np.pi*x)**2
def boom(at,g=0.5):
    a=int(at*sr);L=int(0.9*sr);x=np.arange(L)/sr
    f=38+70*np.exp(-x*12)
    fx[a:a+L]+=g*np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-x*4)+0.12*lp(rng.standard_normal(L),1200)*np.exp(-x*14)
boom(S[1]['start']-0.03)
seen=set()
for s in S:
    if s['scene'] not in seen and s['scene']!='hook':
        seen.add(s['scene']); whoosh(s['start']-0.05)
# VO + ducking
vo,vsr=sf.read('vo.wav');
from scipy.signal import resample_poly
vo=resample_poly(vo,147,80)[:N]; vo=np.pad(vo,(0,N-len(vo)))
envv=lp(np.abs(vo),8,2); duck=1-0.55*np.clip(envv/0.05,0,1)
novoice='--sans-voix' in sys.argv
mix=mus*0.9+fx if novoice else vo*1.0+mus*duck*0.9+fx
# fade out tail
mix[-int(1.0*sr):]*=np.linspace(1,0,int(1.0*sr))**1.5
mix/=np.max(np.abs(mix))/0.95
sf.write('mix-sans-voix.wav' if novoice else 'mix.wav',np.stack([mix,mix],1),sr)
print('ok',N/sr)
