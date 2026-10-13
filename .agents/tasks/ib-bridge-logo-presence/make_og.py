#!/usr/bin/env python3
"""Create og-image.png (1200x630): trimmed COLORED logo centered on a light canvas."""
from PIL import Image

SRC = "/projects/sandbox/ib-bridge/logo.png"
OUT = "/projects/sandbox/ib-bridge/og-image.png"
BG = (243, 247, 248, 255)  # --bg-alt #f3f7f8
CANVAS = (1200, 630)
MAX_W, MAX_H = 940, 450  # comfortable margins

im = Image.open(SRC).convert("RGBA")
bbox = im.getbbox()
crop = im.crop(bbox)
cw, ch = crop.size
scale = min(MAX_W / cw, MAX_H / ch)
nw, nh = round(cw * scale), round(ch * scale)
crop = crop.resize((nw, nh), Image.LANCZOS)

canvas = Image.new("RGBA", CANVAS, BG)
x = (CANVAS[0] - nw) // 2
y = (CANVAS[1] - nh) // 2
canvas.alpha_composite(crop, (x, y))
canvas.convert("RGB").save(OUT)

check = Image.open(OUT)
print(f"og-image.png {check.size[0]}x{check.size[1]} (logo {nw}x{nh} centered at {x},{y})")
