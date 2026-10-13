#!/usr/bin/env python3
"""Verify logo-ondark.png uniformity: composite over navy + teal swatches and
sample interior pixels of IB, Bridge, and tagline to prove each is one flat color."""
from PIL import Image

OUT = "/projects/sandbox/ib-bridge/logo-ondark.png"
TASK = "/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-logo-clean"
NAVY_BG = (18, 41, 63)       # #12293f
TEAL_BG = (31, 139, 144)     # #1f8b90

out = Image.open(OUT).convert("RGBA")
W, H = out.size
print("size", out.size, "mode", out.mode)

for name, bg in (("navy", NAVY_BG), ("teal", TEAL_BG)):
    swatch = Image.new("RGBA", (W, H), bg + (255,))
    comp = Image.alpha_composite(swatch, out)
    comp.convert("RGB").save(f"{TASK}/composite_on_{name}.png")

# Sample interior regions (approx glyph centers in the 1536x1024 canvas).
# IB letters band: x ~ 240-500, y ~ 500-650 (navy region -> should read ~WHITE)
# Bridge letters: x ~ 560-1250, y ~ 500-650 (teal region -> uniform teal)
# Tagline: x ~ 360-1150, y ~ 760-800 (navy region -> white)
opx = out.load()


def samples(x0, y0, x1, y1, step=7, amin=200):
    out_rgb = []
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            r, g, b, a = opx[x, y]
            if a >= amin:
                out_rgb.append((r, g, b))
    return out_rgb


def summarize(label, pts):
    if not pts:
        print(f"{label}: NO opaque pixels sampled")
        return
    rs = [p[0] for p in pts]
    gs = [p[1] for p in pts]
    bs = [p[2] for p in pts]
    uniq = set(pts)
    print(f"{label}: n={len(pts)} unique_colors={len(uniq)} "
          f"R[{min(rs)}-{max(rs)}] G[{min(gs)}-{max(gs)}] B[{min(bs)}-{max(bs)}] "
          f"example={pts[0]}")


summarize("IB letters (navy->white)", samples(250, 500, 500, 660))
summarize("Bridge letters (teal)", samples(600, 500, 1240, 660))
summarize("Tagline (navy->white)", samples(380, 760, 1140, 800))
summarize("Arcs (teal)", samples(300, 180, 1250, 360))
