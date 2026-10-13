# Implementation Plan — Make the IB Bridge logo more present

Goal (owner's words): "I want the IB Bridge logo more present in the website — it's an important part and people associate it with the company." Make the logo noticeably more prominent across the navbar, hero, and footer — tastefully, matching the existing design tokens and responsive patterns. This is a static GitHub Pages site: `index.html`, `styles.css`, `script.js`, `logo.png`, `.nojekyll`. No build step; verification is visual + file checks.

## Logo artwork findings (from Pillow inspection of logo.png)

Inspected `/projects/sandbox/ib-bridge/logo.png` with `PIL.Image` (mode RGBA, 1536×1024, ~300KB).

- **Transparency: YES.** 86.5% of sampled pixels are fully transparent; all four corners and the center are `(255,255,255,0)`. There is effectively no semi-transparent fringe (0.0% in 16–240 alpha). The actual artwork occupies bbox `(228, 144, 1307, 814)` → roughly 1079×670 within the canvas, i.e. there is substantial transparent padding (notably top/bottom) around the mark.
- **Color of the mark: mostly TEAL, with light/white detail and some dark-navy.** Of the opaque (mark) pixels: **~67% teal / mid-colored**, **~19% near-white/light** (luminance > 200), and **~14% dark navy** (luminance < 70). Average luminance of the mark is ~156/255. Dominant quantized colors include teal tones `(96,160,160)`, `(64,128,160)`, `(64,160,160)` and near-white `(224,224,224)`, plus dark `(32,32,64)` accents.

### What this means for dark surfaces (hero gradient + footer)

The hero background is a navy→teal gradient (`#12293f` → `#1a3a5c` → `#1f8b90`) and the footer is `--navy-deep #12293f`. The logo's dominant teal would **blend into the teal end of the hero gradient**, and its ~14% dark-navy pixels would **nearly vanish** against both dark surfaces. Placing the raw transparent logo directly on either dark surface would read poorly and inconsistently.

### DECISION

- **Hero: PLACE the logo, on a light "chip" (rounded white/very-light card with padding).** This is chosen over (a) direct placement on the gradient — rejected because the mixed teal+navy mark loses contrast against the teal/navy gradient — and over (b) skipping the hero — rejected because the owner explicitly wants the logo *more* present and the hero is the most prominent spot. The chip guarantees consistent contrast and looks intentional/branded. It also matches the site's existing rounded-card design language (`--radius`, `.card`, soft shadows).
- **Footer: PLACE the logo on the same light chip treatment** (footer is dark navy, same contrast problem). Replaces the plain-text `<p class="footer-brand">IB Bridge</p>`.
- **Navbar: no chip needed** — the header is light (`rgba(255,255,255,.94)`), so the logo already has good contrast; just enlarge it.
- A single reusable `.logo-chip` style keeps hero + footer consistent and DRY.

> Note on the transparent padding: the mark has notable built-in top/bottom transparent padding (bbox height 670 of 1024 ≈ 65%). Chip vertical padding is kept modest so the chip doesn't look oversized relative to the visible mark. Sizes below are the rendered `img` height; the visible mark will appear a bit shorter than the stated height because of this padding — values were chosen with that in mind.

## Cache-busting (MANDATORY — flagged)

`index.html` loads the stylesheet as `styles.css?v=20260922j`. **Every task below that edits `styles.css` requires bumping this version query** so GitHub Pages does not serve a stale cached stylesheet. Bump it exactly once, as the final content step (Task 5), to `?v=20260922k`. If you re-run and the version is already `k`, bump to the next letter. HTML files are not cache-busted by Pages the same way, so only the CSS query matters.

## Constraints to preserve (verify after each change)

- Keep ALL existing content, the bilingual `data-en` / `data-es` attributes, and functionality intact.
- Do NOT break the language switcher (`script.js` `setLang` iterates `[data-en]`/`[data-es]`) or the mobile nav toggle.
- The new logo `<img>` elements are brand imagery, not translated text — give them static, meaningful `alt`, and do NOT add `data-en`/`data-es` to the images.
- Accessibility: meaningful `alt` on every logo image. The navbar brand link already has `aria-label="IB Bridge home"`; its logo `alt` can stay descriptive.

---

# Implementation Plan

- [ ] 1. **Enlarge the navbar logo and keep the header balanced.**
      In `styles.css`, change `.brand-logo { height: 62px; ... }` to `height: 76px;` (keep `width: auto; display: block;`). In the `@media (max-width: 720px)` block, change the `.brand-logo { height: 52px; }` override to `height: 60px;`. The header uses `.header-inner { min-height: 72px; }`; bump it to `min-height: 86px;` so the taller 76px logo has breathing room and the sticky header stays visually balanced. Also update the mobile nav dropdown offset that is pinned to the old header height: in the `@media (max-width: 720px)` block the `.nav` rule has `top: 72px;` — change it to `top: 86px;` so the open mobile menu still sits directly under the header.
      Files: `styles.css`
      Verify: open `index.html` in a browser (e.g. `python3 -m http.server` from the repo root, then load the page); confirm the navbar logo is visibly larger, the header isn't clipped, and on a narrow/mobile viewport the hamburger menu opens flush beneath the header. Confirm no horizontal overflow.

- [ ] 2. **Add a reusable light "chip" style for the logo on dark surfaces, plus the hero logo class.**
      In `styles.css`, add a `.logo-chip` rule: `display: inline-flex; align-items: center; justify-content: center; background: #fff; border-radius: var(--radius); padding: 14px 22px; box-shadow: var(--shadow-lift);` (white chip, existing radius + lift shadow so it matches the card language). Add `.hero-logo { height: 104px; width: auto; display: block; }` for the image inside the hero chip (desktop; within the owner's 90–120px guidance). Add a wrapper rule `.hero-logo-wrap { margin-bottom: 22px; }` so the chip sits above the `.hero-pill` with consistent spacing. Place these rules in the `/* ===== Hero ===== */` section (after `.hero-inner`, before `.hero-pill`). Do not change `index.html` yet.
      Files: `styles.css`
      Verify: temporary — reload the page; nothing visually changes yet (classes unused), and the page must still render without CSS errors. Real visual check happens in Task 3.

- [ ] 3. **Insert the logo into the hero on the chip, above the pill/headline.**
      In `index.html`, inside `<div class="container hero-inner">`, immediately before `<span class="hero-pill" ...>`, add:
      `<div class="hero-logo-wrap logo-chip"><img class="hero-logo" src="logo.png" alt="IB Bridge logo" /></div>`.
      Keep the `.hero-pill`, `<h1>`, and everything else unchanged. The hero text is left-aligned (`.hero-inner { max-width: 720px; }`), so the chip will sit at the left above the pill, consistent with the rest of the hero content — do NOT center it unless step 6 (optional polish) is taken.
      Files: `index.html`
      Verify: reload the page; the IB Bridge logo appears on a white rounded chip near the top of the hero, clearly legible against the dark gradient, above the "IB · MYP · Diploma Programme" pill. No layout overlap with the arcs SVG or the headline.

- [ ] 4. **Replace the plain-text footer brand with the logo on the chip.**
      In `index.html`, in `<footer class="site-footer"> ... <div class="container footer-inner">`, replace the line `<p class="footer-brand">IB Bridge</p>` with:
      `<div class="footer-brand logo-chip"><img class="footer-logo" src="logo.png" alt="IB Bridge logo" /></div>`.
      Keep the tagline `<p class="footer-tag" ...>` immediately after it, unchanged, and keep `footer-contact` / `footer-fine` unchanged. In `styles.css`, add `.footer-logo { height: 56px; width: auto; display: block; }` (within the owner's 48–64px range) and, because `.site-footer` is `text-align: center`, make the inline-flex chip center itself by adding `margin: 0 auto 14px;` to the `.footer-brand` rule (replace the existing `.footer-brand { ... margin-bottom: 2px; }` text styles with chip-appropriate ones: remove the `font-*`/`color` text props since it's now an image container, keep it as a centered block — e.g. `.footer-brand { display: inline-flex; margin: 0 auto 14px; }`). Keep `.footer-tag` as-is.
      Files: `index.html`, `styles.css`
      Verify: reload the page; the footer shows the IB Bridge logo on a white chip (centered), with the teal "Your bridge to IB success" tagline directly beneath it, and contact + copyright lines unchanged below.

- [ ] 5. **Bump the stylesheet cache-busting version.**
      In `index.html`, change `<link rel="stylesheet" href="styles.css?v=20260922j" />` to `href="styles.css?v=20260922k"`. Do this last so it covers all CSS edits from Tasks 1–4.
      Files: `index.html`
      Verify: `grep -n "styles.css?v=" index.html` shows `20260922k` and the string appears exactly once. Reload the page in the browser; styles apply (chips, enlarged logo) with no stale-cache artifacts.

- [ ] 6. **(Optional polish — only if it reads better) Center the hero logo chip.**
      If, on review in the browser, the left-aligned hero chip looks awkward, add `.hero-logo-wrap { display: block; }` is insufficient for centering an inline-flex chip — instead wrap intent: give `.hero-logo-wrap` `text-align` won't center inline-flex either, so set the chip container to its own line and center with `margin-left: 0` kept (left) OR change to centered by setting `.hero-logo-wrap { display: flex; justify-content: flex-start; }` (left, default) vs `justify-content: center` (centered). Decision: default to LEFT-aligned (matches hero text); only switch to centered if the reviewer prefers it. If changed, this touches `styles.css` only and still falls under the already-bumped `?v=20260922k` (no further bump needed within the same change set, but if committed separately, bump again).
      Files: `styles.css` (only if taken)
      Verify: reload the page; hero chip alignment looks intentional and consistent with the hero content.

---

## Full-change verification (run after all tasks)

1. Serve locally from the repo root: `cd /projects/sandbox/ib-bridge && python3 -m http.server 8000`, open `http://localhost:8000/`.
2. Confirm all three placements: enlarged navbar logo (76px desktop / 60px mobile), hero logo on a white chip above the pill, footer logo on a white chip above the tagline.
3. Toggle the language switcher EN ⇄ ES: all text still translates; the logo images are unaffected (no `data-*` on them) and `alt` stays "IB Bridge logo".
4. Open the mobile nav (narrow viewport): hamburger toggles the menu and it sits flush under the taller header (`top: 86px`).
5. Check responsiveness at ~375px, ~768px, ~1200px widths: no horizontal overflow, chips and logo scale sensibly, nothing overlaps.
6. `grep -n "styles.css?v=" index.html` → version is `20260922k` (bumped).
7. `git diff --stat` → only `index.html` and `styles.css` changed; `logo.png`, `script.js`, `.nojekyll` untouched.

## Assumptions / gaps noted

- No README/AGENTS/CONTRIBUTING/.kiro steering files exist in the repo; there is no build or test framework (pure static site). Verification is therefore local-serve + visual + git-diff checks, which is the project's real workflow here.
- Exact pixel values (76/60px navbar, 104px hero, 56px footer, chip padding 14px/22px) are within the owner's stated ranges and chosen to look balanced given the logo's built-in transparent padding; a reviewer may fine-tune within those ranges without changing the plan's structure.
- `logo.png` is reused as-is for all placements (no new asset). It is ~300KB and 1536×1024; this is acceptable for a single shared image already shipped. Downscaling/optimizing the asset is out of scope for this request and not required to satisfy "more present."
