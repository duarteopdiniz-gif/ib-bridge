#!/usr/bin/env python3
"""Generate a clean on-dark two-tone logo variant.

Recolor ONLY the NAVY region (the "IB" wordmark + the thin tagline) toward
near-white, and KEEP the TEAL region (bridge arcs + the word "Bridge") exactly.
Alpha channel is preserved byte-for-byte.

Classification keys on HUE (channel dominance), not brightness alone, so the
bright blue-tinted anti-aliased edge pixels of the navy glyphs (brightness
200-255 but still blue-dominant) are whitened too -> clean edges, no navy fringe.
"""
import sys
from PIL import Image

SRC = "/projects/sandbox/ib-bridge/logo.png"
OUT = "/projects/sandbox/ib-bridge/logo-ondark.png"
TARGET = (243, 247, 248)  # #F3F7F8 soft brand white

# navy-ness ramp on the green-minus-red gap (gr):
#   gr <= GR_LO  -> fully navy  (w = 1)   recolor toward white
#   gr >= GR_HI  -> fully teal  (w = 0)   keep as-is
# The teal family is defined as gr >= 25 (see verify/inspect). To keep teal
# EXACTLY, the navy ramp must finish (reach w=0) before gr hits 25, so no teal
# pixel is ever touched. We ramp over gr 15 -> 25 and hard-guard the teal test.
GR_LO = 15
GR_HI = 25


def navy_weight(r, g, b):
    """Return navy-ness weight in [0,1]. 0 means keep (teal/other), 1 means fully whiten."""
    gr = g - r
    # Must be blue-dominant (blue the max-ish channel) to be navy family.
    if not (b >= g and b >= r):
        return 0.0
    # Explicit teal guard: anything in the teal family is kept EXACTLY.
    if g >= r and b >= r and g > 80 and b > 80 and gr >= 25:
        return 0.0
    if gr <= GR_LO:
        return 1.0
    if gr >= GR_HI:
        return 0.0
    # transition zone: ramp 1 -> 0 as gr goes GR_LO -> GR_HI
    return (GR_HI - gr) / (GR_HI - GR_LO)


def main():
    im = Image.open(SRC).convert("RGBA")
    assert im.size == (1536, 1024), f"unexpected size {im.size}"
    src_alpha_hist = im.getchannel("A").histogram()

    px = im.load()
    W, H = im.size
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    opx = out.load()

    tr, tg, tb = TARGET
    changed = 0
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a == 0:
                # fully transparent: copy as-is (keeps alpha 0, color irrelevant)
                opx[x, y] = (r, g, b, a)
                continue
            w = navy_weight(r, g, b)
            if w <= 0.0:
                opx[x, y] = (r, g, b, a)
            else:
                nr = round(r + (tr - r) * w)
                ng = round(g + (tg - g) * w)
                nb = round(b + (tb - b) * w)
                opx[x, y] = (nr, ng, nb, a)
                changed += 1

    out.save(OUT)

    # Verify alpha preserved EXACTLY.
    out_check = Image.open(OUT).convert("RGBA")
    out_alpha_hist = out_check.getchannel("A").histogram()
    alpha_identical = (src_alpha_hist == out_alpha_hist)
    print("size", out_check.size, "mode", out_check.mode)
    print("pixels recolored:", changed)
    print("alpha histogram identical:", alpha_identical)
    if not alpha_identical:
        print("ERROR: alpha channel changed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
