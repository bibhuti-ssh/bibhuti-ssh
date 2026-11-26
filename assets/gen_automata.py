"""Excitable-medium (Barkley) cellular automaton -> assets/automata.svg
Spiral waves rendered as ASCII; loop point chosen where the field nearly repeats."""
import numpy as np, sys
W, H = 80, 26
a, b, eps = 0.75, 0.06, 0.02
dt, hx, hy = 0.02, 0.5, 1.0          # chars are ~2x taller than wide
RAMP = " .,:;-=+*#%@"
REC_EVERY = 10                        # sim steps per frame

def lap(f):
    return ((np.roll(f, 1, 1) + np.roll(f, -1, 1) - 2 * f) / hx**2 +
            (np.roll(f, 1, 0) + np.roll(f, -1, 0) - 2 * f) / hy**2)

def step(u, v):
    du = u * (1 - u) * (u - (v + b) / a) / eps + lap(u)
    return np.clip(u + dt * du, 0, 1), v + dt * (u - v)

# seed: classic cross-field start, one spiral pair
u = np.zeros((H, W)); v = np.zeros((H, W))
cy = H // 2
for cx, sgn in ((W * 0.28, 1), (W * 0.72, -1)):
    cx = int(cx)
    for y in range(H):
        for x in range(W):
            if y < cy and 0 <= sgn * (x - cx) < 5: u[y, x] = 1.0          # excited strip
            if y < cy and -9 < sgn * (x - cx) < 0: v[y, x] = 0.7          # refractory tail breaks the front
for _ in range(3000): u, v = step(u, v)           # settle into rotating spirals

frames_u = []
for i in range(420):
    for _ in range(REC_EVERY): u, v = step(u, v)
    frames_u.append(u.copy())
F = np.array(frames_u)
if len(sys.argv) > 1 and sys.argv[1] == "scan":
    print("mean u", F.mean(), "min/max", F.min(), F.max())

# find loop: pick (s, P) minimising difference between frame s and s+P, P in [90, 300]
best = (1e9, 0, 0)
for s in range(0, 100):
    for P in range(90, 300):
        d = np.abs(F[s] - F[s + P]).mean()
        if d < best[0]: best = (d, s, P)
print("loop diff, start, period:", best, file=sys.stderr)
_, s0, P = best
frames = []
for k in range(P):
    f = F[s0 + k]
    idx = np.clip((f * (len(RAMP) - 1) + 0.5).astype(int), 0, len(RAMP) - 1)
    frames.append(["".join(RAMP[c] for c in r).rstrip() for r in idx])
if len(sys.argv) > 1 and sys.argv[1] == "preview":
    for k in (0, P // 3, 2 * P // 3):
        print("--- frame", k); print("\n".join(frames[k]))
    sys.exit()

STEP_T = 0.1
N = len(frames); lh, cw = 14, 7.2
w, h = int(W * cw), H * lh + 10
dur = N * STEP_T
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
       '<style>text{font:12px ui-monospace,Menlo,Consolas,monospace;fill:#57606a;white-space:pre}'
       '@media(prefers-color-scheme:dark){text{fill:#9da7b3}}</style>']
for i, fr in enumerate(frames):
    kt = f"0;{i/N:.5f};{(i+1)/N:.5f};1"
    svg.append(f'<g visibility="hidden"><animate attributeName="visibility" dur="{dur:.2f}s" repeatCount="indefinite" '
               f'calcMode="discrete" keyTimes="{kt}" values="hidden;visible;hidden;hidden"/>')
    for r, line in enumerate(fr):
        if line.strip():
            svg.append(f'<text x="0" y="{(r+1)*lh}" xml:space="preserve">{line.replace("&","&amp;").replace("<","&lt;")}</text>')
    svg.append('</g>')
svg.append('</svg>')
open("assets/automata.svg", "w").write("\n".join(svg))
print("frames", N, "bytes", sum(len(x) for x in svg), file=sys.stderr)
