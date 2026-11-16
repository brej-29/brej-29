import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = sys.argv[1]
BG = (13, 17, 23)
CY, VI, AM, GR = (34, 211, 238), (167, 139, 250), (245, 177, 61), (95, 211, 154)
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def grad(t):
    return lerp(CY, VI, t * 2) if t < .5 else lerp(VI, AM, (t - .5) * 2)

# ---------- token globe
S, SS, N, F = 340, 2, 760, 60
R = S * SS * 0.31
i = np.arange(N) + 0.5
phi = np.arccos(1 - 2 * i / N); th = math.pi * (1 + 5 ** 0.5) * i
P = np.stack([np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)], 1)
tilt = 0.38
frames = []
for f in range(F):
    a = 2 * math.pi * f / F
    ca, sa = math.cos(a), math.sin(a)
    x = P[:, 0] * ca + P[:, 2] * sa; z = -P[:, 0] * sa + P[:, 2] * ca; y = P[:, 1]
    y2 = y * math.cos(tilt) - z * math.sin(tilt); z2 = y * math.sin(tilt) + z * math.cos(tilt)
    im = Image.new("RGB", (S * SS, S * SS), BG)
    glow = Image.new("RGB", (S * SS, S * SS), (0, 0, 0))
    d, g = ImageDraw.Draw(im), ImageDraw.Draw(glow)
    c = S * SS / 2
    order = np.argsort(z2)
    for k in order:
        depth = (z2[k] + 1) / 2
        col = grad((y[k] + 1) / 2)
        col = lerp(BG, col, 0.18 + 0.82 * depth ** 1.4)
        r = (1.2 + 3.4 * depth ** 2) * SS
        px, py = c + x[k] * R, c - y2[k] * R
        d.ellipse([px - r, py - r, px + r, py + r], fill=col)
        if depth > 0.8: g.ellipse([px - r * 2.2, py - r * 2.2, px + r * 2.2, py + r * 2.2], fill=lerp((0, 0, 0), col, 0.5))
    # orbiting packets on a tilted ring
    for j, (cl, sp, rr, ph) in enumerate([(AM, 1, 1.32, 0), (GR, -2, 1.18, 2.1), (CY, 1, 1.45, 4.0)]):
        steps = 140
        pts = []
        for s in range(steps + 1):
            t = 2 * math.pi * s / steps
            ox, oz, oy = math.cos(t) * rr, math.sin(t) * rr, 0
            ty = 0.55 + j * 0.5
            oy2 = oy * math.cos(ty) - oz * math.sin(ty); oz2 = oy * math.sin(ty) + oz * math.cos(ty)
            pts.append((c + ox * R, c - oy2 * R, oz2))
        d.line([(p[0], p[1]) for p in pts], fill=lerp(BG, cl, 0.22), width=SS)
        t = sp * a + ph
        idx = int((t % (2 * math.pi)) / (2 * math.pi) * steps)
        px, py, pz = pts[idx]
        r = 5 * SS
        for tail in range(1, 10):
            q = pts[(idx - sp * tail) % steps]
            rt = r * (1 - tail / 11)
            d.ellipse([q[0] - rt, q[1] - rt, q[0] + rt, q[1] + rt], fill=lerp(BG, cl, 1 - tail / 10))
        d.ellipse([px - r, py - r, px + r, py + r], fill=cl)
        g.ellipse([px - r * 3, py - r * 3, px + r * 3, py + r * 3], fill=cl)
    glow = glow.filter(ImageFilter.GaussianBlur(10 * SS))
    im = Image.fromarray(np.clip(np.asarray(im, dtype=np.int32) + (np.asarray(glow, dtype=np.int32) * 0.55).astype(np.int32), 0, 255).astype(np.uint8))
    frames.append(im.resize((S, S), Image.LANCZOS))
pal = frames[F // 3].quantize(colors=72, method=Image.Quantize.MEDIANCUT)
q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
q[0].save(f"{OUT}/globe.gif", save_all=True, append_images=q[1:], duration=50, loop=0, optimize=True, disposal=1)

# ---------- divider
W, H, F2 = 1200, 14, 36
x = np.linspace(0, 1, W)
fr2 = []
for f in range(F2):
    t = (x * 2 + f / F2) % 1.0
    cols = np.array([grad(abs(v * 2 - 1)) for v in t], dtype=np.float32)
    prof = np.exp(-((np.arange(H) - (H - 1) / 2) ** 2) / 6.0)[:, None, None]
    img = np.asarray(BG, np.float32) * (1 - prof) + cols[None] * prof
    fr2.append(Image.fromarray(img.astype(np.uint8)))
p2 = fr2[0].quantize(colors=96)
q2 = [fr.quantize(palette=p2, dither=Image.Dither.NONE) for fr in fr2]
q2[0].save(f"{OUT}/divider.gif", save_all=True, append_images=q2[1:], duration=50, loop=0, optimize=True)
