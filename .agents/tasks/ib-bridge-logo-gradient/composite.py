#!/usr/bin/env python3
"""Composite logo-ondark.png over the navy swatch #12293f for eyeballing."""
from PIL import Image

OUT = "/projects/sandbox/ib-bridge/logo-ondark.png"
TASK = "/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-logo-gradient"

logo = Image.open(OUT).convert("RGBA")
bg = Image.new("RGBA", logo.size, (18, 41, 63, 255))  # #12293f
bg.alpha_composite(logo)
bg.convert("RGB").save(f"{TASK}/composite_on_navy.png")
# cropped to bbox for a tighter view
bbox = logo.getbbox()
bg.convert("RGB").crop(bbox).save(f"{TASK}/composite_on_navy_crop.png")
print("saved composite, bbox", bbox)
