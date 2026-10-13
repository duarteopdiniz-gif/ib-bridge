# Implementation Plan — Blend the IB Bridge logo into the dark backgrounds (remove the ugly white chip)

Goal (owner's words): the hero/footer logo "doesn't match the rest of the page, it's just a random pic with an ugly background … just try to make it match with the background." The current fix wrapped the logo in a white rounded card (`.logo-chip`) on the dark hero gradient and dark navy footer; the owner finds that sticker-like white box ugly. **Correct solution:** make the logo itself legible on dark WITHOUT any box — by shipping a white (light) version of the mark and placing it directly on the dark surfaces. The navbar stays exactly as-is.

This is a pure static GitHub Pages site: `index.html`, `styles.css`, `script.js`, `logo.png`, `.nojekyll`. There is **no build step and no test framework** — verification is Pillow asset inspection + local-serve + mandatory Playwright screenshots + git diff. (No README/AGENTS/CONTRIBUTING/.kiro steering files exist in the repo; confirmed by listing the tree.)

## Exploration findings (grounded in the actual files)

### Logo artwork (`logo.png`, inspected with Pillow 11.3.0)
- Mode **RGBA**, size **1536×1024**, content bbox **(228, 144, 1307, 814)**.
- **Hard alpha edges: 0 semi-transparent pixels** (every pixel is either fully opaque, alpha 255, or fully transparent, alpha 0). This is the single most important finding: recoloring all opaque pixels to white yields a crisp white silhouette with **no gray halo**, and alpha is preserved by simply copying it.
- Average opaque RGB ≈ **(112, 162, 180)** — muted teal-blue; it loses contrast on the dark hero gradient and navy footer, which is exactly why the chip was added.

### DOM elements that render the logo (`index.html`)
1. **Navbar (LEAVE UNCHANGED):** inside `<header class="site-header">` → `<a class="brand" …>` → `<img class="brand-logo" src="logo.png" alt="IB Bridge — Your bridge to IB success" />`.
2. **Hero chip (REMOVE BOX):** inside `<div class="container hero-inner">`, immediately before `<span class="hero-pill" …>`:
   `<div class="hero-logo-wrap logo-chip"><img class="hero-logo" src="logo.png" alt="IB Bridge logo" /></div>`.
3. **Footer chip (REMOVE BOX):** inside `<footer class="site-footer">` → `<div class="container footer-inner">`, first child:
   `<div class="footer-brand logo-chip"><img class="footer-logo" src="logo.png" alt="IB Bridge logo" /></div>`, followed by `<p class="footer-tag" …>Your bridge to IB success</p>`.

### CSS selectors involved (`styles.css`)
- `.logo-chip` (the ugly box — the white background/radius/padding/shadow lives here):
  ```
  .logo-chip {
    display: inline-flex; align-items: center; justify-content: center;
    background: #fff; border-radius: var(--radius); padding: 14px 22px;
    box-shadow: var(--shadow-lift);
  }
  ```
- `.hero-logo-wrap { margin-bottom: 22px; }` and `.hero-logo { height: 104px; width: auto; display: block; }` (in the `/* ===== Hero ===== */` section).
- `.footer-brand { display: inline-flex; margin: 0 auto 14px; }` and `.footer-logo { height: 56px; width: auto; display: block; }` (in the `/* ===== Footer ===== */` section). `.site-footer` is `text-align: center`.
- Navbar `.brand-logo { height: 76px; … }` (desktop) and the `@media (max-width: 720px)` override `.brand-logo { height: 60px; }` — **do not touch either.**

### Cache-busting
`index.html` currently links `<link rel="stylesheet" href="styles.css?v=20260922k" />`. Bump to `?v=20260922l`.

### Tooling available (for the implementer)
- `python3` with Pillow 11.3.0 (for asset generation + inspection).
- Playwright **CLI 1.64.0** is available via `npx playwright`, **but the Chromium browser binary is NOT installed** — the implementer must run `npx playwright install chromium` once before screenshots. `gh` 2.95.0 is available for the PR. The git remote `origin` points at the project's GitHub mirror.

### DECISION (recorded rationale)
- **Ship a recolored white asset `logo-light.png`** rather than CSS-filtering the colored logo. Rationale: the mark is two-tone (teal graphic + navy wordmark), so a single CSS `filter: brightness(0) invert(1)` would work but couples legibility to a fragile filter; a dedicated white PNG is deterministic, needs no runtime filter, and the hard-alpha source guarantees a clean result. Chosen over keeping the chip (owner rejected it) and over tinting via `mix-blend-mode` (unreliable across the gradient).
- **Recolor to pure `#FFFFFF`** (within the brief's `#FFFFFF`/`#F3F7F8` option). Rationale: pure white gives maximum, uniform contrast on both the navy→teal hero gradient and the `--navy-deep` footer; the near-white `#F3F7F8` option buys nothing here and slightly reduces contrast against the teal end of the gradient.
- **No drop-shadow by default.** A pure-white silhouette on `#12293f`/gradient is already high-contrast; add a subtle shadow only if the mobile screenshot shows the wordmark washing out against the teal end — decided per the visual review in step 7, not pre-emptively.
- **Delete `.logo-chip` entirely** (not neutralize). Rationale: after removing it from both DOM nodes it is dead CSS; the hero wrapper `.hero-logo-wrap` and footer `.footer-brand` already provide spacing/centering, so no centering wrapper from `.logo-chip` is needed. Leaving no renderable white-box styling is the explicit requirement.

### Constraints to preserve (verify after each change)
- Keep ALL bilingual `data-en`/`data-es` attributes, the language switcher (`script.js` `setLang` iterates `[data-en]`/`[data-es]`), the mobile nav toggle, and all `aria-label`s. The logo `<img>`s are brand imagery — keep static meaningful `alt`, do NOT add `data-*` to them.
- Navbar logo untouched (colored `logo.png`, 76px desktop / 60px mobile).
- Commit on a NEW branch `fix/logo-blend-dark-bg`; never commit to `main`; push and open a PR into `main`.

---

# Implementation Plan

- [ ] 1. **Create the working branch.**
      From `main` (clean, up to date), create and switch to `fix/logo-blend-dark-bg`. Do all work here; never commit to `main`.
      Files: none (git only)
      Verify: `git branch --show-current` prints `fix/logo-blend-dark-bg`; `git status` shows a clean tree on the new branch.

- [ ] 2. **Generate `logo-light.png` (white version) with Pillow, preserving alpha exactly.**
      Write and run a short Python script (run inline, do not commit the script) that opens `logo.png` as RGBA, keeps the full 1536×1024 canvas, and for every pixel sets RGB to pure white `(255,255,255)` while copying the **original alpha unchanged** (e.g. split channels, rebuild as `Image.merge('RGBA', (white, white, white, orig_alpha))` or `putdata` setting `(255,255,255,a)` per pixel). Save to `/projects/sandbox/ib-bridge/logo-light.png`. Because the source has 0 semi-transparent pixels, the result is a clean silhouette with no gray fringe.
      Files: `logo-light.png` (new)
      Verify: run Pillow checks confirming the output is `RGBA 1536×1024`, its `getbbox()` equals the source `(228, 144, 1307, 814)` (geometry/alpha preserved), every opaque pixel (alpha > 0) is exactly `(255,255,255)`, and the count of alpha-0 vs alpha-255 pixels matches the source. Additionally open/eyeball it (or composite onto a dark swatch via Pillow and save a temp preview) to confirm the wordmark and tagline are present as a white silhouette.

- [ ] 3. **Point the hero logo at the white asset and remove the chip wrapper box.**
      In `index.html`, change the hero node from
      `<div class="hero-logo-wrap logo-chip"><img class="hero-logo" src="logo.png" alt="IB Bridge logo" /></div>`
      to
      `<div class="hero-logo-wrap"><img class="hero-logo" src="logo-light.png" alt="IB Bridge" /></div>`
      (drop the `logo-chip` class, swap the `src`, give meaningful `alt`). Leave `.hero-pill`, `<h1>`, and the rest untouched.
      Files: `index.html`
      Verify: covered by the visual check in step 7 (served page); for now, `git diff index.html` shows only this hero line changed and no `logo-chip` remains on the hero node.

- [ ] 4. **Point the footer logo at the white asset and remove the chip wrapper box.**
      In `index.html`, change the footer node from
      `<div class="footer-brand logo-chip"><img class="footer-logo" src="logo.png" alt="IB Bridge logo" /></div>`
      to
      `<div class="footer-brand"><img class="footer-logo" src="logo-light.png" alt="IB Bridge" /></div>`
      (drop `logo-chip`, swap `src`, meaningful `alt`). Keep `<p class="footer-tag">`, `footer-contact`, and `footer-fine` exactly as-is immediately after.
      Files: `index.html`
      Verify: covered by step 7; `git diff index.html` shows only this footer line changed, no `logo-chip` remains anywhere in `index.html` (`grep -c logo-chip index.html` → 0).

- [ ] 5. **Delete the dead `.logo-chip` CSS and keep sizing/centering rules.**
      In `styles.css`, delete the entire `.logo-chip { … }` rule block (the white background/radius/padding/shadow). Keep `.hero-logo-wrap { margin-bottom: 22px; }` and `.hero-logo { height: 104px; width: auto; display: block; }` as the hero sizing (≈104px, within the 96–120px desktop range; the existing `@media (max-width: 720px)` hero padding already shrinks surrounding spacing — if the mobile logo looks oversized in step 7, add a `.hero-logo { height: 72px; }` override inside that media query). Keep `.footer-brand { display: inline-flex; margin: 0 auto 14px; }` (centers the logo in the `text-align: center` footer) and `.footer-logo { height: 56px; width: auto; display: block; }` (within the 44–56px range). Do NOT touch `.brand-logo` rules.
      Files: `styles.css`
      Verify: `grep -c "logo-chip" styles.css` → 0; `grep -n "background: #fff" styles.css` no longer matches a logo wrapper; the file still parses (page renders in step 7 with no missing-rule errors). No renderable white-box styling remains.

- [ ] 6. **Bump the stylesheet cache-busting version.**
      In `index.html`, change `href="styles.css?v=20260922k"` to `href="styles.css?v=20260922l"`. (If re-running and it is already `l`, bump to the next letter.)
      Files: `index.html`
      Verify: `grep -n "styles.css?v=" index.html` shows `20260922l` exactly once.

- [ ] 7. **Visual verification with Playwright screenshots at desktop (~1280px) and mobile (~390px) — MANDATORY.**
      Install the browser if needed (`npx playwright install chromium`), serve the site (`python3 -m http.server 8000` from the repo root), and use a short Playwright script (Node or Python) to screenshot `http://localhost:8000/` at viewport 1280×~900 and 390×~844. Capture: hero region (logo on the dark gradient) and footer region (logo on the dark navy) at both sizes. Save screenshots under `.agents/tasks/ib-bridge-logo-blend/` (e.g. `desktop.png`, `desktop-footer.png`, `mobile.png`, `mobile-footer.png`). Inspect them: the white logo must read cleanly on both dark surfaces with **no white box/card/border**, sit centered above the hero pill and above the footer tagline, and be sensibly sized. If the wordmark washes out against the teal end of the hero gradient on mobile, add a subtle `filter: drop-shadow(0 1px 2px rgba(0,0,0,.35))` to `.hero-logo` (and bump the cache version again if already committed) — otherwise leave it off.
      Files: screenshots under `.agents/tasks/ib-bridge-logo-blend/` (not committed to the site)
      Verify: all four screenshots show a boxless white logo matching the background; navbar logo in the desktop shot is still the colored `logo.png` at full size (unchanged); language switcher and mobile nav still function (toggle EN/ES and open the hamburger in the Playwright run or a manual load).

- [ ] 8. **Confirm nothing else regressed and the scope is tight.**
      Reload the served page; toggle EN ⇄ ES (all text translates, logos unaffected); open the mobile nav (hamburger toggles, menu sits under the header). 
      Files: none
      Verify: `git diff --name-only` lists exactly `index.html` and `styles.css` as modified plus `logo-light.png` as a new untracked file; `logo.png`, `script.js`, `favicon.png`, `apple-touch-icon.png`, `.nojekyll` are untouched. No horizontal overflow at 390/768/1280px.

- [ ] 9. **Commit on the branch, push, and open a PR into `main`.**
      Stage exactly `index.html`, `styles.css`, and `logo-light.png` (do NOT stage the Playwright script or the screenshots unless intended; the brief says commit the fix). Commit with a clear message (e.g. `fix: blend logo into dark hero/footer with white logo-light.png, remove white chip`). Push `fix/logo-blend-dark-bg` to `origin` and open a PR into `main` with `gh pr create` summarizing the chip removal, the new white asset, and the cache-bust.
      Files: git/gh only
      Verify: `git log --oneline -1` shows the commit on `fix/logo-blend-dark-bg`; `git branch --show-current` is still the fix branch (NOT `main`); `gh pr view --json url,baseRefName` shows the PR targets `main`. `git branch --contains main` confirms no commits were added to `main`.

---

## Full-change verification (run after all tasks)
1. `cd /projects/sandbox/ib-bridge && python3 -m http.server 8000`, load `http://localhost:8000/`.
2. Hero: white logo directly on the gradient, no box, centered above the pill. Footer: white logo directly on navy, no box, above the teal tagline. Navbar: unchanged colored logo.
3. Playwright screenshots at 1280px and 390px captured and visually confirmed boxless.
4. EN ⇄ ES toggles all copy; mobile hamburger works.
5. `grep -c logo-chip index.html styles.css` → 0 in both; `grep -n "styles.css?v=" index.html` → `20260922l`.
6. `git diff --name-only` → only `index.html`, `styles.css` (+ new `logo-light.png`).
7. PR open against `main`; `main` has no new direct commits.

## Assumptions / gaps noted
- Pure `#FFFFFF` chosen over `#F3F7F8` for maximum uniform contrast on both dark surfaces (see DECISION).
- Hero ≈104px / footer 56px retained from the existing rules (within the brief's 96–120px and 44–56px ranges); a mobile hero override to ~72px is listed as a conditional tweak gated on the mobile screenshot.
- Drop-shadow is off by default and only added if the mobile visual check shows wash-out — the brief explicitly prefers none when the logo reads fine.
- The Pillow generation script and Playwright screenshot script are run ad hoc; only the site files (`index.html`, `styles.css`) and the new `logo-light.png` asset are committed. Screenshots live under `.agents/tasks/…` for evidence and are not required on the site.

---

## VERIFICATION (first iteration — completed)

Branch: `fix/logo-blend-dark-bg` (off `main`, no commits added to `main`).

### Asset generation + Pillow pixel check (`logo-light.png`)
Generated by splitting the source alpha and merging it with three pure-white (255) channels: `Image.merge('RGBA', (white, white, white, orig_alpha))`.
- Source `logo.png`: RGBA 1536×1024, bbox `(228, 144, 1307, 814)`, **0 semi-transparent pixels** (alpha-0 = 1,361,155 / alpha-255 = 211,709).
- Output `logo-light.png`: RGBA 1536×1024, bbox `(228, 144, 1307, 814)` — identical geometry/alpha.
- Pixel audit: 211,709 opaque pixels, **0 with non-white color** (every opaque pixel is exactly `(255,255,255)`), alpha-0 count unchanged (1,361,155). Clean white silhouette, transparency intact, no black box, no leftover color.

### Code changes
- Hero: `logo-chip` class removed, `src` → `logo-light.png`, `alt="IB Bridge"`.
- Footer: `logo-chip` class removed, `src` → `logo-light.png`, `alt="IB Bridge"`.
- `.logo-chip { … }` rule block deleted from `styles.css` (the white background/radius/padding/shadow). `grep -c logo-chip` → 0 in both `index.html` and `styles.css`.
- Hero kept at 104px (`.hero-logo`), footer at 56px (`.footer-logo`) — within the brief's ranges; no mobile override needed (see screenshots).
- No drop-shadow added — white silhouette reads cleanly on both dark surfaces.
- Cache-bust bumped `styles.css?v=20260922k` → `?v=20260922l`.
- Navbar untouched (colored `logo.png`, `.brand-logo` 76px/60px).

### Browser verification (Playwright/Chromium 1.64.0, `python3 -m http.server 8000`)
Screenshots saved under `.agents/tasks/ib-bridge-logo-blend/`: `{desktop,mobile}-{full,hero,footer,navbar}.png`.
- Desktop (1280×900) & mobile (390×844):
  - (a) **No white box/card/border** behind the logo in hero or footer — confirmed in all crops.
  - (b) White logo (wordmark + bridge + tagline) is **clearly legible** on the navy→teal hero gradient AND the dark navy footer.
  - (c) Navbar logo **unchanged** — colored `logo.png` on the white header (desktop-navbar.png).
  - (d) No horizontal overflow at either viewport (`scrollWidth <= innerWidth`); nothing broken.
  - (e) Mobile renders correctly; logo centered above the pill (hero) and above the teal tagline (footer).
- Language switcher works: toggling ES updates the hero pill to "IB · MYP · Programa del Diploma" at both viewports; EN restores it.

### Scope
`git diff --name-only` → `index.html`, `styles.css` only; `logo-light.png` new untracked asset. `logo.png`, `script.js`, favicons, `.nojekyll` untouched.
