#!/usr/bin/env python3
"""Regenerate favicon.png (32x32) and apple-touch-icon.png (180x180) from the
alpha-bbox-cropped colored logo mark, centered on a square transparent canvas."""
from PIL import Image

SRC = "/projects/sandbox/ib-bridge/logo.png"
TARGETS = [
    ("/projects/sandbox/ib-bridge/favicon.png", 32, 0.08),
    ("/projects/sandbox/ib-bridge/apple-touch-icon.png", 180, 0.10),
]

im = Image.open(SRC).convert("RGBA")
crop = im.crop(im.getbbox())
cw, ch = crop.size

for path, size, pad in TARGETS:
    inner = round(size * (1 - 2 * pad))
    scale = min(inner / cw, inner / ch)
    nw, nh = max(1, round(cw * scale)), max(1, round(ch * scale))
    resized = crop.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((size - nw) // 2, (size - nh) // 2))
    canvas.save(path)
    print(f"{path.split('/')[-1]} {size}x{size} (mark {nw}x{nh})")
