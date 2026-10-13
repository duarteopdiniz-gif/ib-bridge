# Verification — IB Bridge logo presence (feature/logo-presence)

## Branch
`feature/logo-presence`, created off `main`. No push, no PR.

## STEP A — Clean on-dark two-tone logo variant

Generator: `.agents/tasks/ib-bridge-logo-presence/make_ondark.py`
Verifier:  `.agents/tasks/ib-bridge-logo-presence/verify_ondark.py`

Approach: classify each opaque pixel by **hue (green-minus-red gap `gr`)**, not brightness.
- Navy family (blue-dominant, small `gr`) → recolored toward near-white `#F3F7F8`.
- Teal family (`gr >= 25`, g & b elevated) → kept EXACTLY (hard guard + ramp finishes at `gr=25`).
- Alpha channel copied byte-for-byte.

### Ground truth (inspect_logo.py)
```
mode RGBA size (1536, 1024)
alpha extrema (0, 255)
alpha bbox (228, 144, 1307, 814)
```

### make_ondark.py output
```
size (1536, 1024) mode RGBA
pixels recolored: 50687
alpha histogram identical: True
```

### verify_ondark.py output
```
dark-navy opaque pixels  before: 30577  after: 1
teal pixels  before: 143611  after: 143611  delta: 0.000%
teal still present in output: True
RESULT: OK
```
- Dark-navy glyph pixels eliminated (30577 → 1).
- Teal unchanged (0.000% delta — exact).
- Composite over `#12293f` saved to `ondark_on_navy.png`: "IB" + tagline read clean WHITE,
  "Bridge" + arcs stay TEAL, crisp edges, no navy fringe, no muddy mid-band.

## STEP B — Placement

1. **Hero**: `<img class="hero-logo" src="logo-ondark.png" alt="IB Bridge logo">` placed as first
   child of `.hero-inner`, ABOVE `.hero-pill`. Box-free (removed old `.hero-logo-wrap`).
   CSS `.hero-logo { height:120px; margin:0 0 22px }`, mobile `height:90px; margin-bottom:18px`.
   No overlap with `.hero-arcs`.
2. **Footer**: replaced the `<div class="footer-brand">` wrapper with
   `<img class="footer-logo" src="logo-ondark.png" alt="IB Bridge logo">`, box-free, centered,
   `height:56px`, above the unchanged teal `.footer-tag`. Removed dead `.footer-brand` CSS.
3. **Navbar**: colored `logo.png` left as-is.
4. **OG / social**: `make_og.py` → `og-image.png` 1200×630, trimmed COLORED logo (725×450)
   centered on `#f3f7f8`, aspect preserved. OG + Twitter meta tags added to `<head>`.
5. **Favicons**: `make_icons.py` → `favicon.png` 32×32, `apple-touch-icon.png` 180×180, both
   from the alpha-bbox-cropped mark, centered on transparent square with padding, LANCZOS, no squash.

## STEP C / VERIFY (screenshots.py — viewport & element crops only, never fullPage)

```
desktop overflow: {'sw': 1280, 'cw': 1280}        # no horizontal overflow
mobile  overflow: {'sw': 390,  'cw': 390}          # no horizontal overflow
EN h1: 'Ace the IB with tutors who’ve scored top'
ES h1: 'Domina el IB con tutores que lo superaro'
EN h1 restored: 'Ace the IB with tutors who’ve scored top'
toggle changes text: True | restores: True
hero-logo src unchanged by ES: logo-ondark.png     # logo never swapped by language switch
mobile nav aria-expanded after click: true         # mobile nav opens
```

- `data-en` = 88, `data-es` = 88 (balanced, unchanged).
- Stylesheet cache-bust bumped `?v=20260922l` → `?v=20260923b`, appears exactly once.
- Logo `<img>` elements carry NO `data-*`; meaningful static alt text.
- No white boxes/chips anywhere.
- `script.js` untouched.

### Saved screenshots (under this task dir)
- `hero-desktop.png`   — hero crop, 1280×800 viewport
- `hero-mobile.png`    — hero crop, 390×800 viewport
- `footer-desktop.png` / `footer-mobile.png` — footer crops
- `navbar-desktop.png` — navbar colored logo unchanged
- `mobile-nav-open.png`— mobile nav open
- `ondark_on_navy.png` — on-dark logo composited on #12293f (the eye-test)
- `og-image-inspect.png` — copy of og-image.png (1200×630)

## Visual confirmation
- (a) Hero on-dark logo: crisp, real logo — white "IB", teal "Bridge", teal arcs, white tagline,
  legible on gradient, no box. ✓
- (b) Footer on-dark logo: legible on navy-deep, no box, teal tagline below. ✓
- (c) Navbar colored logo unchanged. ✓
- (d) No overflow desktop & mobile; mobile nav works. ✓
- (e) EN/ES toggle switches all strings and restores; logos never change. ✓
