#!/usr/bin/env python3
"""Verify the on-dark logo: teal gradient preserved, IB+tagline white."""
from PIL import Image

ORIG = "/projects/sandbox/ib-bridge/logo.png"
OUT = "/projects/sandbox/ib-bridge/logo-ondark.png"
TASK = "/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-logo-gradient"

orig = Image.open(ORIG).convert("RGBA")
out = Image.open(OUT).convert("RGBA")
W, H = orig.size
op = orig.load()
up = out.load()

WHITE = (243, 247, 248)


def is_teal(r, g, b, a):
    if a < 60:
        return False
    return g >= r and b >= r and g > 70 and b > 70 and (g - r) >= 22


# 1. Count distinct colors in the teal region of OUT and ORIG, and compare
#    pixel-for-pixel on teal pixels.
teal_colors_out = set()
teal_colors_orig = set()
teal_diff = 0
teal_count = 0
for y in range(H):
    for x in range(W):
        r, g, b, a = op[x, y]
        if is_teal(r, g, b, a):
            teal_count += 1
            teal_colors_orig.add((r, g, b))
            ur, ug, ub, ua = up[x, y]
            teal_colors_out.add((ur, ug, ub))
            if (ur, ug, ub, ua) != (r, g, b, a):
                teal_diff += 1

print("== TEAL REGION (Bridge + arcs) ==")
print("teal pixels:", teal_count)
print("distinct teal colors in ORIGINAL:", len(teal_colors_orig))
print("distinct teal colors in OUT     :", len(teal_colors_out))
print("teal pixels differing OUT vs ORIG:", teal_diff)

# 2. Sample interior pixels of the IB wordmark. The IB glyphs sit on the left
#    of the wordmark. Scan a band and report white coverage. Also sample fixed
#    interior points.
# Find navy-recolored (white) pixel stats across the whole image.
white_px = 0
for y in range(H):
    for x in range(W):
        r, g, b, a = up[x, y]
        if a > 200 and abs(r - WHITE[0]) <= 3 and abs(g - WHITE[1]) <= 3 and abs(b - WHITE[2]) <= 3:
            white_px += 1
print()
print("== WHITE (IB + tagline) ==")
print("opaque white pixels in OUT:", white_px)

# Sample several interior points of the IB letters. Based on bbox (228,144)-(1307,814),
# the IB wordmark glyphs are roughly in the upper-left. Probe a grid and print
# the first few opaque samples that are white vs not.
samples = [(360, 430), (420, 430), (300, 480), (470, 500), (330, 540)]
print("interior IB samples (x,y)->rgba:")
for (x, y) in samples:
    print(f"  ({x},{y}) orig={op[x,y]} out={up[x,y]}")
