import math
W,H,N=60,26,36
chars=".,-~:;=!*#$@"
frames=[]
K1=W*0.38; K2=5
for f in range(N):
    A=f*2*math.pi/N; B=f*2*math.pi/N*0.5
    out=[[" "]*W for _ in range(H)]; z=[[0]*W for _ in range(H)]
    cA,sA,cB,sB=math.cos(A),math.sin(A),math.cos(B),math.sin(B)
    th=0
    while th<2*math.pi:
        ct,st=math.cos(th),math.sin(th)
        ph=0
        while ph<2*math.pi:
            cp,sp=math.cos(ph),math.sin(ph)
            cx=ct+2; D=1/(sp*cx*sA+st*cA+K2)
            t=sp*cx*cA-st*sA
            x=int(W/2+K1*D*(cp*cx*cB-t*sB)*2*0.5*1.0)
            y=int(H/2+K1*0.5*D*(cp*cx*sB+t*cB))
            L=int(8*((st*sA-sp*ct*cA)*cB-sp*ct*sA-st*cA-cp*ct*sB))
            if 0<=y<H and 0<=x<W and D>z[y][x]:
                z[y][x]=D; out[y][x]=chars[L] if L>0 else "."
            ph+=0.02
        th+=0.05
    frames.append(["".join(r).rstrip() for r in out])
lh=14; cw=7.2
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W*cw)}" height="{H*lh+10}" viewBox="0 0 {int(W*cw)} {H*lh+10}">',
'<style>text{font:12px ui-monospace,Menlo,Consolas,monospace;fill:#24292f;white-space:pre}@media(prefers-color-scheme:dark){text{fill:#e6edf3}}</style>']
for i,fr in enumerate(frames):
    kt=f"0;{i/N:.4f};{(i+1)/N:.4f};1"
    svg.append(f'<g visibility="hidden"><animate attributeName="visibility" dur="3.6s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="hidden;visible;hidden;hidden"/>')
    for r,line in enumerate(fr):
        if line.strip():
            svg.append(f'<text x="0" y="{(r+1)*lh}" xml:space="preserve">{line.replace("&","&amp;").replace("<","&lt;")}</text>')
    svg.append('</g>')
svg.append('</svg>')
open("assets/donut.svg","w").write("\n".join(svg))
print(frames[5][0:H] and "\n".join(frames[5]))
