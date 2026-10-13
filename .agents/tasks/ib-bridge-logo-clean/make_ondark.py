#!/usr/bin/env python3
"""Generate a CLEAN on-dark two-tone logo via REGION-MASK FLAT-FILL.

Problem with prior attempts: per-pixel brightness recolor on antialiased
gradient glyphs classified pixels inconsistently, leaving blotchy white
patches inside letters and a mottled tagline.

New approach (no mottling possible, because each region is ONE flat color):
  1. Classify original opaque pixels into NAVY vs TEAL using hue/brightness.
  2. Clean each binary mask with morphological close+open (MaxFilter/MinFilter)
     so each glyph/region is a single solid blob, no pinholes, no specks.
  3. Start from a fully transparent canvas. Flat-fill WHITE where the NAVY
     mask is set, flat-fill brand TEAL where the TEAL mask is set.
  4. Copy the ORIGINAL alpha channel onto the result so the silhouette and
     crisp antialiased edges exactly match the original.

Net result: white "IB" + white tagline, teal "Bridge" + teal arcs, each a
single uniform flat color, with original crisp edges. Light-on-dark, clean.
"""
import sys
from PIL import Image, ImageFilter

SRC = "/projects/sandbox/ib-bridge/logo.png"
OUT = "/projects/sandbox/ib-bridge/logo-ondark.png"

WHITE = (243, 247, 248)      # #F3F7F8 soft brand white for the navy-region glyphs
TEAL = (43, 167, 173)        # #2ba7ad site --teal, flat for Bridge + arcs

# Hue/brightness classification of ORIGINAL colored pixels.
#   TEAL  = brighter cyan/teal: green & blue both elevated, green >= red by margin.
#   NAVY  = dark blue-dominant: low luminance, blue the dominant channel.
GR_TEAL = 22      # green-minus-red threshold for teal family
TEAL_MINGB = 70   # teal needs green & blue reasonably elevated
NAVY_MAXBRIGHT = 150  # navy region is dark


def classify_masks(im):
    """Return (navy_mask, teal_mask) as mode-L images (255 = member)."""
    px = im.load()
    W, H = im.size
    navy = Image.new("L", (W, H), 0)
    teal = Image.new("L", (W, H), 0)
    npx = navy.load()
    tpx = teal.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a < 60:
                continue
            gr = g - r
            bright = (r + g + b) / 3
            is_teal = (g >= r and b >= r and g > TEAL_MINGB and b > TEAL_MINGB
                       and gr >= GR_TEAL)
            if is_teal:
                tpx[x, y] = 255
            elif b >= g and b >= r and bright < NAVY_MAXBRIGHT:
                npx[x, y] = 255
    return navy, teal


def clean(mask, close=5, open_=3):
    """Morphological close (fill pinholes) then open (drop specks).

    close = MaxFilter then MinFilter; open = MinFilter then MaxFilter.
    Filter sizes must be odd.
    """
    m = mask
    m = m.filter(ImageFilter.MaxFilter(close))   # dilate: fill interior holes
    m = m.filter(ImageFilter.MinFilter(close))   # erode back: close
    m = m.filter(ImageFilter.MinFilter(open_))   # erode: remove specks
    m = m.filter(ImageFilter.MaxFilter(open_))   # dilate back: open
    return m


def main():
    im = Image.open(SRC).convert("RGBA")
    assert im.size == (1536, 1024), f"unexpected size {im.size}"
    W, H = im.size
    orig_alpha = im.getchannel("A")

    navy_raw, teal_raw = classify_masks(im)
    navy = clean(navy_raw)
    teal = clean(teal_raw)

    # Resolve overlaps: a pixel claimed by both goes to whichever raw mask is
    # larger locally. In practice overlap is tiny (edge pixels). Give teal
    # priority on overlap only where teal_raw was set, else navy. Simpler and
    # safe: teal wins ties (teal glyphs are brighter / more saturated).
    npx = navy.load()
    tpx = teal.load()
    for y in range(H):
        for x in range(W):
            if tpx[x, y] and npx[x, y]:
                npx[x, y] = 0

    # Build flat-color RGB layers.
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    white_layer = Image.new("RGBA", (W, H), WHITE + (255,))
    teal_layer = Image.new("RGBA", (W, H), TEAL + (255,))

    # Paste white where navy mask, teal where teal mask (mask as alpha).
    canvas.paste(white_layer, (0, 0), navy)
    canvas.paste(teal_layer, (0, 0), teal)

    # Now apply ORIGINAL alpha as the true silhouette so edges match exactly.
    # canvas currently has alpha = union of cleaned masks (hard edges). Replace
    # its alpha with the original antialiased alpha, but zero it anywhere no
    # region was assigned (so stray original pixels outside both masks vanish).
    region_union = Image.new("L", (W, H), 0)
    region_union.paste(255, (0, 0), navy)
    region_union.paste(255, (0, 0), teal)
    # Dilate the region union slightly so the original antialiased edge pixels
    # (which sit just outside the hard mask) are kept -> smooth edges.
    region_dilated = region_union.filter(ImageFilter.MaxFilter(5))

    # final alpha = original alpha, gated by dilated region union
    oa = orig_alpha.load()
    ru = region_dilated.load()
    final_alpha = Image.new("L", (W, H), 0)
    fa = final_alpha.load()
    for y in range(H):
        for x in range(W):
            if ru[x, y]:
                fa[x, y] = oa[x, y]

    # The flat color must extend under the antialiased edge, so fill color
    # across the whole dilated region (fill holes between hard mask and edge).
    # Build color-only image, then dilate colors into the edge band.
    rgb = canvas.convert("RGB")
    # Dilate each flat region's color by taking Max/Min won't blend colors well;
    # instead paste colors onto dilated masks.
    navy_d = navy.filter(ImageFilter.MaxFilter(5))
    teal_d = teal.filter(ImageFilter.MaxFilter(5))
    color = Image.new("RGB", (W, H), (0, 0, 0))
    color.paste(WHITE, (0, 0), navy_d)
    color.paste(TEAL, (0, 0), teal_d)  # teal painted after -> teal wins the shared edge band

    out = color.convert("RGBA")
    out.putalpha(final_alpha)
    out.save(OUT)

    print("size", out.size, "mode", out.mode)
    print("navy mask px:", sum(navy.histogram()[255:]))
    print("teal mask px:", sum(teal.histogram()[255:]))
    print("saved", OUT)


if __name__ == "__main__":
    main()
