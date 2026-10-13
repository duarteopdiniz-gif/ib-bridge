#!/usr/bin/env python3
"""Composite logo-ondark.png over the hero gradient ends + footer navy to judge legibility."""
from PIL import Image

logo = Image.open("/projects/sandbox/ib-bridge/logo-ondark.png").convert("RGBA")
# crop to bbox for tighter preview
logo = logo.crop(logo.getbbox())
# scale to approx hero display height 104px
scale = 104 / logo.height
logo_h = logo.resize((int(logo.width*scale), int(logo.height*scale)), Image.LANCZOS)

backgrounds = {
    "navy_deep": (0x12, 0x29, 0x3f),   # hero start / footer
    "navy_mid":  (0x1a, 0x3a, 0x5c),   # hero mid
    "teal_dark": (0x1f, 0x8b, 0x90),   # hero end (worst case for teal washout)
}
pad = 30
for name, col in backgrounds.items():
    canvas = Image.new("RGBA", (logo_h.width + pad*2, logo_h.height + pad*2), col + (255,))
    canvas.alpha_composite(logo_h, (pad, pad))
    p = f"/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-fix-logo-dark-variant-2026-09-22/preview_{name}.png"
    canvas.convert("RGB").save(p)
    print("saved", p)
