# Verification — Fix (or remove) IB Bridge logo on dark hero & footer

Branch: `fix/logo-dark-variant` (off `main`). No changes committed to `main`.

## Decision taken: FALLBACK — logo removed from hero & footer

### Why
Per the plan I FIRST attempted the primary two-tone variant: I regenerated
`logo-ondark.png` with a Pillow script
(`make_ondark.py`) that recolors only the NAVY wordmark/tagline pixels toward
near-white `#F3F7F8` while keeping the TEAL bridge arcs original, feathering
anti-alias edges. Pillow classification confirmed the mechanics worked:

```
size (1536, 1024) mode RGBA
opaque pixels: 211709
NAVY before: 36589  after: 99      <- wordmark pixels recolored
TEAL before: 138854 after: 172113
alpha histogram identical: True    <- alpha preserved exactly
```

I then rendered the primary variant and viewed the cropped screenshots on the
dark hero and footer. **It failed the decision gate by eye:** the "IB Bridge"
wordmark came out patchy/muddy — a mix of white, teal and leftover dark navy
within the glyphs — because the original wordmark is not uniformly dark navy
(it carries internal shading / teal-tinted anti-aliasing). The result looked
dirty and illegible on the navy footer and NOT recognizably the clean original
logo. This is exactly the kind of "both logos don't look the same... nothing
like the original" result the owner rejected.

Owner explicitly authorized removal as the fallback: *"try to fix that but if
not just delete both."* The plan says "when in doubt, prefer removal." So I took
the FALLBACK path.

### Changes made (fallback)
- **Hero (HTML):** removed `<div class="hero-logo-wrap"><img class="hero-logo" ...></div>`. Hero now begins with `.hero-pill` then `<h1>` (original structure).
- **Hero (CSS):** removed dead `.hero-logo-wrap` and `.hero-logo` rules.
- **Footer (HTML):** replaced the logo `<img>` with the original text wordmark `<p class="footer-brand">IB Bridge</p>`; `.footer-tag` tagline below unchanged.
- **Footer (CSS):** restored original rule `.footer-brand { font-family: "Poppins"; font-weight: 700; font-size: 1.3rem; color: #fff; margin-bottom: 2px; }` (recovered from commit `614c2d4`); removed dead `.footer-logo` rule.
- **Cache-bust:** bumped `styles.css?v=20260922m` -> `styles.css?v=20260923a`.
- **Navbar:** untouched — still `logo.png` (colored) at 76/60px on white header.
- No logo files deleted from disk (out of scope; navbar still needs `logo.png`); dark-variant references removed from hero/footer.

## Rendering / screenshots
Rendered locally via `python3 -m http.server` and captured with Playwright
(Chromium). Viewport set explicitly; only element-cropped screenshots taken —
**no `full_page` anywhere** (script uses element `.screenshot()`). Script:
`shoot.py`.

Saved artifacts (final = fallback render):
- `hero_desktop.png`  (2560x1364) — hero starts clean with pill + headline, no logo/box.
- `footer_desktop.png` (2560x440) — white bold "IB Bridge" + teal tagline, no image/box.
- `hero_mobile.png`   (780x1510) — same clean hero; navbar colored logo visible/unchanged.
- `footer_mobile.png` (780x438)  — same clean text footer.

All images are well under 8000px in both dimensions.

(Primary-attempt screenshots that led to the fallback were overwritten by the
final fallback render; the decision reasoning above records why the two-tone
variant was rejected.)

## Checks performed
- Navbar unchanged: `logo.png` at line 22 (`brand-logo`). PASS.
- No logo refs in hero/footer: `grep "logo-ondark|hero-logo|footer-logo" index.html` -> none. PASS.
- Footer text wordmark present: `<p class="footer-brand">IB Bridge</p>`. PASS.
- Original footer-brand CSS restored (Poppins/white). PASS.
- No dead hero/footer logo CSS: `grep "hero-logo|footer-logo" styles.css` -> none. PASS.
- Cache-bust bumped to `20260923a`. PASS.
- No `.logo-chip` / white box anywhere. PASS.
- i18n preserved: `data-en` count = 88 (identical to HEAD). PASS.
- a11y: remaining `alt`/`aria-label` valid; `script.js` untouched (EN/ES `setLang`, mobile nav intact). PASS.
- No horizontal overflow: desktop scrollWidth 1280 == clientWidth 1280; mobile 390 == 390. PASS.
- No broken asset references (hero/footer no longer reference images; navbar `logo.png` exists). PASS.
