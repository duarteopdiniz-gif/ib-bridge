#!/usr/bin/env python3
"""Generate the on-dark logo by PRESERVING the original teal gradient.

Approach (differs from the prior flat-fill generator):
  1. Open the ORIGINAL colored logo.png (RGBA 1536x1024).
  2. Build a NAVY-only mask: opaque pixels that are dark, blue-dominant and
     low-luminance (the "IB" letters + the thin tagline). Everything else that
     is opaque (teal/blue gradient arcs + the word "Bridge") is NON-navy and
     is left ALONE.
  3. Clean the navy mask morphologically (close then open) so it is a solid,
     speckle-free shape with no pinholes and no stray specks bleeding into the
     teal "Bridge"/arcs.
  4. Start from a byte-for-byte COPY of the original. ONLY where the cleaned
     navy mask is set, recolor the pixel to soft white #F3F7F8 while PRESERVING
     the pixel's ORIGINAL ALPHA (so antialiased edges stay crisp, just white).
     Every non-navy pixel (teal gradient on "Bridge" + arcs) is untouched, so
     the original gradient is preserved exactly.

Antialiased navy edge handling: the morphological close dilates the navy mask
slightly so the navy glyphs' antialiased edge pixels (navy-ish, partial alpha)
are also whitened -> no dark navy fringe. The dilation is bounded so it does
not reach the teal "Bridge"/arcs (there is clear transparent spacing between
the navy "IB" glyphs and the teal word, and the tagline sits well below).
"""
from PIL import Image, ImageFilter

SRC = "/projects/sandbox/ib-bridge/logo.png"
OUT = "/projects/sandbox/ib-bridge/logo-ondark.png"

WHITE = (243, 247, 248)  # #F3F7F8 soft brand white

# Navy classification of ORIGINAL colored pixels: dark, blue-dominant,
# low luminance. Teal/blue gradient pixels are brighter and greener and must
# NOT match this.
NAVY_MAXBRIGHT = 150  # navy region is dark
GR_TEAL = 22          # teal family has green noticeably above red; navy does not


def build_navy_mask(im):
    px = im.load()
    W, H = im.size
    navy = Image.new("L", (W, H), 0)
    npx = navy.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a < 60:
                continue
            gr = g - r
            bright = (r + g + b) / 3
            # Teal family: green & blue elevated and green well above red.
            is_teal = (g >= r and b >= r and g > 70 and b > 70 and gr >= GR_TEAL)
            if is_teal:
                continue
            # Navy: blue dominant and dark.
            if b >= g and b >= r and bright < NAVY_MAXBRIGHT:
                npx[x, y] = 255
    return navy


def clean(mask, close=5, open_=3):
    """Morphological close (fill pinholes) then open (drop specks)."""
    m = mask
    m = m.filter(ImageFilter.MaxFilter(close))  # dilate
    m = m.filter(ImageFilter.MinFilter(close))  # erode back -> close
    m = m.filter(ImageFilter.MinFilter(open_))  # erode
    m = m.filter(ImageFilter.MaxFilter(open_))  # dilate back -> open
    return m


def main():
    im = Image.open(SRC).convert("RGBA")
    assert im.size == (1536, 1024), f"unexpected size {im.size}"
    W, H = im.size

    navy_raw = build_navy_mask(im)
    navy = clean(navy_raw)
    # Grow the cleaned navy mask by a small, bounded amount so the glyphs'
    # antialiased edge pixels (navy-ish, partial alpha) are whitened too, to
    # kill any dark fringe. 3px keeps it local to the glyphs.
    navy_edge = navy.filter(ImageFilter.MaxFilter(3))

    # Start from an EXACT copy of the original; recolor ONLY navy-mask pixels
    # to white, preserving each pixel's original alpha. Non-navy pixels keep
    # their original RGBA byte-for-byte.
    out = im.copy()
    opx = out.load()
    spx = im.load()
    mpx = navy_edge.load()
    recolored = 0
    for y in range(H):
        for x in range(W):
            if not mpx[x, y]:
                continue
            r, g, b, a = spx[x, y]
            if a == 0:
                continue  # nothing to show; keep transparent
            opx[x, y] = (WHITE[0], WHITE[1], WHITE[2], a)
            recolored += 1

    out.save(OUT)
    print("size", out.size, "mode", out.mode)
    print("navy mask px:", sum(navy.histogram()[255:]))
    print("recolored px:", recolored)
    print("saved", OUT)


if __name__ == "__main__":
    main()
