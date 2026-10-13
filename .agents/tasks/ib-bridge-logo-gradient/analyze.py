#!/usr/bin/env python3
"""Analyze the original logo pixel color families to tune the navy classifier."""
from PIL import Image

im = Image.open("/projects/sandbox/ib-bridge/logo.png").convert("RGBA")
px = im.load()
W, H = im.size

navy = 0
teal = 0
other = 0
# Sample histogram of hue-ish buckets
for y in range(H):
    for x in range(W):
        r, g, b, a = px[x, y]
        if a < 60:
            continue
        gr = g - r
        bright = (r + g + b) / 3
        if b >= g and b >= r and bright < 150:
            navy += 1
        elif g >= r and b >= r and g > 70 and b > 70 and gr >= 22:
            teal += 1
        else:
            other += 1

print("navy", navy, "teal", teal, "other", other)

# Print some representative colors in regions by scanning columns.
# IB is on the left of the wordmark; Bridge is to the right.
print("bbox", im.getbbox())
