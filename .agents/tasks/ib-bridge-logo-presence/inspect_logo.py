#!/usr/bin/env python3
"""Inspect logo.png ground truth: size, mode, alpha bbox, navy/teal pixel accounting."""
from PIL import Image
from collections import Counter

im = Image.open("/projects/sandbox/ib-bridge/logo.png")
print("mode", im.mode, "size", im.size)
im = im.convert("RGBA")
px = im.load()
W, H = im.size

alpha = im.getchannel("A")
print("alpha extrema", alpha.getextrema())
print("alpha bbox", im.getbbox())

navy = teal = other = transp = 0
navy_bright = Counter()
for y in range(H):
    for x in range(W):
        r, g, b, a = px[x, y]
        if a < 40:
            transp += 1
            continue
        mx = max(r, g, b); mn = min(r, g, b)
        gr = g - r
        bright = (r + g + b) / 3
        # teal test
        if g >= r and b >= r and g > 80 and b > 80 and gr >= 25:
            teal += 1
        elif b >= g and b >= r and gr < 40:
            navy += 1
            navy_bright[bright // 40 * 40] += 1
        else:
            other += 1

print("navy", navy, "teal", teal, "other", other, "transp", transp)
print("navy brightness buckets (bucket:count):", dict(sorted(navy_bright.items())))
