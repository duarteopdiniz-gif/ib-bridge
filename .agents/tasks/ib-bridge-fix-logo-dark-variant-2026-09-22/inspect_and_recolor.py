#!/usr/bin/env python3
"""Inspect logo.png color regions and generate logo-ondark.png (teal bridge + white text)."""
from PIL import Image
import numpy as np

src = "/projects/sandbox/ib-bridge/logo.png"
out = "/projects/sandbox/ib-bridge/logo-ondark.png"

im = Image.open(src).convert("RGBA")
print("size:", im.size, "mode:", im.mode)
arr = np.array(im).astype(np.int32)
r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]

opaque = a > 20
print("bbox:", im.getbbox())
print("opaque pixel count:", int(opaque.sum()))

# brightness
bright = (r + g + b) / 3.0

# Classify opaque pixels.
# NAVY/DARK: low brightness, blue-dominant (b >= r, b >= g roughly), dark text.
# TEAL: higher green+blue, brighter cyan/teal.
# Teal bridge: g and b both relatively high; r low. brightness moderate-high.
# Navy text: all low, blue slightly dominant.

navy_mask = opaque & (bright < 110) & (b >= r)
teal_mask = opaque & ~navy_mask

print("navy/dark pixels:", int(navy_mask.sum()))
print("teal pixels:", int(teal_mask.sum()))

# sample average colors
def avg(mask):
    if mask.sum() == 0:
        return None
    return (int(r[mask].mean()), int(g[mask].mean()), int(b[mask].mean()))

print("avg navy color:", avg(navy_mask))
print("avg teal color:", avg(teal_mask))

# Build output: recolor navy -> near white #F3F7F8, keep teal original. Preserve alpha exactly.
NEAR_WHITE = (0xF3, 0xF7, 0xF8)
out_arr = arr.copy()
out_arr[navy_mask, 0] = NEAR_WHITE[0]
out_arr[navy_mask, 1] = NEAR_WHITE[1]
out_arr[navy_mask, 2] = NEAR_WHITE[2]
# alpha unchanged
out_im = Image.fromarray(out_arr.astype(np.uint8), "RGBA")
out_im.save(out)
print("saved:", out)
