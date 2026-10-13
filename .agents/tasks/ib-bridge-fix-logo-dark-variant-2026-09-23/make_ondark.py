#!/usr/bin/env python3
"""Regenerate logo-ondark.png: recolor NAVY wordmark/tagline -> near-white (#F3F7F8),
keep TEAL bridge arcs original, feather anti-alias edges toward their nearest class.
Alpha channel is preserved EXACTLY."""
from PIL import Image

SRC = "/projects/sandbox/ib-bridge/logo.png"
DST = "/projects/sandbox/ib-bridge/logo-ondark.png"
WHITE = (243, 247, 248)  # #F3F7F8

im = Image.open(SRC).convert("RGBA")
assert im.size == (1536, 1024), im.size
px = im.load()
W, H = im.size

def classify(r, g, b):
    brightness = (r + g + b) / 3.0
    sat = 0.0
    mx, mn = max(r, g, b), min(r, g, b)
    if mx > 0:
        sat = (mx - mn) / mx
    is_navy = brightness < 120 and b >= r
    is_teal = g > r and b > r and brightness >= 120 and sat > 0.12
    return brightness, is_navy, is_teal

navy_before = teal_before = 0
navy_after = teal_after = 0
opaque = 0
alpha_hist_src = [0] * 256

out = Image.new("RGBA", im.size)
op = out.load()

for y in range(H):
    for x in range(W):
        r, g, b, a = px[x, y]
        alpha_hist_src[a] += 1
        if a < 20:
            op[x, y] = (r, g, b, a)
            continue
        opaque += 1
        brightness, is_navy, is_teal = classify(r, g, b)
        if is_navy:
            navy_before += 1
        if is_teal:
            teal_before += 1
        # navy-ness weight: 1 at pure dark, 0 at/above brightness 120; only where blue-dominant
        if b >= r and not is_teal:
            w = (120 - brightness) / 120.0
            w = max(0.0, min(1.0, w))
        else:
            w = 0.0
        nr = int(round(r + (WHITE[0] - r) * w))
        ng = int(round(g + (WHITE[1] - g) * w))
        nb = int(round(b + (WHITE[2] - b) * w))
        op[x, y] = (nr, ng, nb, a)
        # reclassify after
        _, na, ta = classify(nr, ng, nb)
        if na:
            navy_after += 1
        if ta:
            teal_after += 1

out.save(DST)

# verify alpha identical
chk = Image.open(DST).convert("RGBA")
alpha_hist_dst = [0] * 256
cp = chk.load()
for y in range(H):
    for x in range(W):
        alpha_hist_dst[cp[x, y][3]] += 1

print("size", chk.size, "mode", chk.mode)
print("opaque pixels:", opaque)
print("NAVY before:", navy_before, " after:", navy_after)
print("TEAL before:", teal_before, " after:", teal_after)
print("alpha histogram identical:", alpha_hist_src == alpha_hist_dst)
