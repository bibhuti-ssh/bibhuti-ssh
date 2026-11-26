"""Calm self-building ASCII wave mesh -> assets/wave.svg (looping SMIL animation)."""
import math
W, H, N, DUR = 72, 24, 64, 9.0
RAMP = " .,:;-=+*#"
STEP = 0.0125                      # sample spacing in the (u,v) plane
M = int(2 / STEP) + 1
LINE_EVERY = 16                    # wireframe line spacing in samples
TAU = 2 * math.pi

def smooth(x):
    x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

def height(u, v, ph):
    r = math.hypot(u, v)
    return (0.16 * math.sin(5.0 * r - ph) / (1 + 1.6 * r)
            + 0.07 * math.sin(2.6 * u + ph)
            + 0.05 * math.sin(3.4 * v - ph + 1.3 * u))

def reveal(t):                      # 0 = bare wireframe, 1 = fully shaded
    if t < 0.12: return 0.0
    if t < 0.48: return smooth((t - 0.12) / 0.36)
    if t < 0.72: return 1.0
    if t < 0.95: return 1 - smooth((t - 0.72) / 0.23)
    return 0.0

frames = []
for f in range(N):
    t = f / N
    ph = TAU * t
    yaw = 0.22 * math.sin(TAU * t)
    cy, sy = math.cos(yaw), math.sin(yaw)
    tilt = 0.55
    ct, st = math.cos(tilt), math.sin(tilt)
    rv = reveal(t) * 1.5 - 0.25      # sweep position along the diagonal
    buf = [[" "] * W for _ in range(H)]
    zb = [[1e9] * W for _ in range(H)]
    for i in range(M):
        u = -1 + i * STEP
        for j in range(M):
            v = -1 + j * STEP
            wire = (i % LINE_EVERY == 0) or (j % LINE_EVERY == 0)
            s = ((u + v) / 2 + 1) / 2 * 1.0   # 0..1 along diagonal
            shaded = s < rv
            if not (wire or shaded):
                continue
            h = height(u, v, ph)
            x1 = u * cy - v * sy; y1 = u * sy + v * cy
            depth = y1 * ct - h * st
            ys = h * ct + y1 * st
            persp = 1 / (1 + 0.22 * depth)
            sx = int(W / 2 + x1 * persp * W * 0.27)
            sc = int(H * 0.52 - ys * persp * H * 0.52)
            if not (0 <= sx < W and 0 <= sc < H): continue
            if depth > zb[sc][sx]: continue
            if shaded:
                e = 0.01
                dhx = (height(u + e, v, ph) - height(u - e, v, ph)) / (2 * e)
                dhy = (height(u, v + e, ph) - height(u, v - e, ph)) / (2 * e)
                n = (-dhx, -dhy, 1); nl = math.sqrt(sum(c * c for c in n))
                L = (-0.4 * n[0] + 0.3 * n[1] + 0.85 * n[2]) / nl
                k = int(max(0, min(0.999, (L - 0.55) / 0.45)) * (len(RAMP) - 1)) + 1
                ch = RAMP[min(k, len(RAMP) - 1)]
                if wire and ch == " ": ch = "."
            else:
                ch = "+" if (i % LINE_EVERY == 0 and j % LINE_EVERY == 0) else "."
            zb[sc][sx] = depth; buf[sc][sx] = ch
    frames.append(["".join(r).rstrip() for r in buf])

lh, cw = 14, 7.2
w, h_ = int(W * cw), H * lh + 10
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h_}" viewBox="0 0 {w} {h_}">',
       '<style>text{font:12px ui-monospace,Menlo,Consolas,monospace;fill:#57606a;white-space:pre}'
       '@media(prefers-color-scheme:dark){text{fill:#9da7b3}}</style>']
for i, fr in enumerate(frames):
    kt = f"0;{i/N:.4f};{(i+1)/N:.4f};1"
    svg.append(f'<g visibility="hidden"><animate attributeName="visibility" dur="{DUR}s" repeatCount="indefinite" '
               f'calcMode="discrete" keyTimes="{kt}" values="hidden;visible;hidden;hidden"/>')
    for r, line in enumerate(fr):
        if line.strip():
            svg.append(f'<text x="0" y="{(r+1)*lh}" xml:space="preserve">{line.replace("&","&amp;").replace("<","&lt;")}</text>')
    svg.append('</g>')
svg.append('</svg>')
open("assets/wave.svg", "w").write("\n".join(svg))
for k in (4, 28, 40):
    print(f"--- frame {k}"); print("\n".join(frames[k]))
