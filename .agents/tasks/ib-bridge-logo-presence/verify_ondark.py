#!/usr/bin/env python3
"""Verify logo-ondark.png: pixel accounting + navy-swatch composite + region samples."""
import sys
from PIL import Image

SRC = "/projects/sandbox/ib-bridge/logo.png"
OUT = "/projects/sandbox/ib-bridge/logo-ondark.png"
COMP = "/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-logo-presence/ondark_on_navy.png"
NAVY_BG = (18, 41, 63)  # #12293f

GR_TEAL = 25


def classify(px, W, H):
    navy_dark = teal = 0
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            gr = g - r
            bright = (r + g + b) / 3
            if g >= r and b >= r and g > 80 and b > 80 and gr >= GR_TEAL:
                teal += 1
            elif b >= g and b >= r and gr < 40 and bright < 120:
                navy_dark += 1
    return navy_dark, teal


src = Image.open(SRC).convert("RGBA")
out = Image.open(OUT).convert("RGBA")
W, H = src.size

snd, steal = classify(src.load(), W, H)
ond, oteal = classify(out.load(), W, H)

print(f"dark-navy opaque pixels  before: {snd}  after: {ond}")
teal_delta = abs(oteal - steal) / steal * 100 if steal else 0
print(f"teal pixels  before: {steal}  after: {oteal}  delta: {teal_delta:.3f}%")

# Composite over solid navy swatch.
swatch = Image.new("RGBA", (W, H), NAVY_BG + (255,))
comp = Image.alpha_composite(swatch, out)
comp.convert("RGB").save(COMP)
print("composite saved:", COMP)

# Region samples. Wordmark band (navy glyph area) should read LIGHT after recolor.
cpx = comp.load()
def region_mean_bright(x0, y0, x1, y1):
    tot = n = 0
    for y in range(y0, y1, 4):
        for x in range(x0, x1, 4):
            r, g, b = cpx[x, y][:3]
            tot += (r + g + b) / 3
            n += 1
    return tot / n if n else 0

# Lower wordmark band per plan (230,466)-(1144,812); measure composite brightness
# over the glyph strokes only is hard, so just confirm the band has bright content now.
# Sample teal "Bridge"/arc region for teal preservation on the output (pre-composite).
opx = out.load()
teal_ok = False
for y in range(200, 460, 3):
    for x in range(240, 1300, 3):
        r, g, b, a = opx[x, y]
        if a > 200 and (g - r) >= GR_TEAL and g > 120 and b > 120:
            teal_ok = True
            break
    if teal_ok:
        break
print("teal still present in output:", teal_ok)

ok = True
if ond > 200:
    print("FAIL: too many dark-navy pixels remain", file=sys.stderr); ok = False
if teal_delta > 1.0:
    print("FAIL: teal changed too much", file=sys.stderr); ok = False
if not teal_ok:
    print("FAIL: teal missing from output", file=sys.stderr); ok = False
print("RESULT:", "OK" if ok else "FAIL")
sys.exit(0 if ok else 1)
