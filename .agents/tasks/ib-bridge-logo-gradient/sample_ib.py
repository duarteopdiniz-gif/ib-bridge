#!/usr/bin/env python3
"""Sample actual interior pixels of the white IB letters and tagline."""
from PIL import Image

OUT = "/projects/sandbox/ib-bridge/logo-ondark.png"
out = Image.open(OUT).convert("RGBA")
up = out.load()
WHITE = (243, 247, 248)

# IB glyphs: absolute approx x 258-468, y 464-664 (from crop view).
# Probe a grid, collect opaque samples, classify white vs other.
def probe(name, x0, x1, y0, y1, step=8):
    opaque = 0
    white = 0
    nonwhite = []
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            r, g, b, a = up[x, y]
            if a > 200:
                opaque += 1
                if abs(r - WHITE[0]) <= 6 and abs(g - WHITE[1]) <= 6 and abs(b - WHITE[2]) <= 6:
                    white += 1
                else:
                    nonwhite.append((x, y, r, g, b, a))
    print(f"{name}: opaque={opaque} white={white} nonwhite={len(nonwhite)}")
    for s in nonwhite[:8]:
        print("   nonwhite", s)

# IB letters region
probe("IB-letters", 258, 470, 460, 670)
# tagline region (thin band near bottom of bbox ~ y 760-805)
probe("tagline", 300, 1200, 760, 810, step=4)
