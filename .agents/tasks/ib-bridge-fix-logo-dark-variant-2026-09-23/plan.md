# Implementation Plan — Fix (or remove) the IB Bridge logo on the dark hero & footer

Branch: `fix/logo-dark-variant` (already checked out; created off `main`). Never commit to `main`.
Repo: `/projects/sandbox/ib-bridge` (already cloned — do NOT re-clone).
Artifacts dir (screenshots, scratch): `/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-fix-logo-dark-variant-2026-09-23/`

## Context discovered during exploration (ground truth — do not re-derive)

- **Project type:** plain static GitHub Pages site. No build step, no `package.json`, no bundler. Files served as-is. There is NO README/AGENTS/CONTRIBUTING/`.kiro` steering — there are no project-specific contribution rules beyond this plan.
- **Files that matter:** `index.html`, `styles.css`, `script.js`, `logo.png` (original colored), `logo-ondark.png` (exists — a prior partial two-tone attempt), `favicon.png`, `apple-touch-icon.png`. `.nojekyll` present (Pages serves raw).
- **Tooling present:** Python 3 with **Pillow 11.3.0** and **Playwright (Python) with Chromium** both confirmed working. Node 22 / npx present but not needed (no JS build).
- **Current working tree state (IMPORTANT):** the tree is NOT clean. `index.html` and `styles.css` already have **uncommitted** changes vs `HEAD` (`be7f892`). The current state is the PRIMARY attempt already partially wired:
  - Hero: `<div class="hero-logo-wrap"><img class="hero-logo" src="logo-ondark.png" ...></div>` (box/`logo-chip` already removed).
  - Footer: `<div class="footer-brand"><img class="footer-logo" src="logo-ondark.png" ...></div>` (box removed).
  - `styles.css`: the `.logo-chip` white-box rule has already been deleted. CSS link bumped from `?v=20260922k` to `?v=20260922m`.
  - A `logo-ondark.png` already exists but was produced by a prior partial run — the plan **regenerates it fresh** so thresholds are known/tuned, rather than trusting it.
  Treat these working-tree edits as the starting point; the plan builds on them (regenerate asset → judge → ship or fall back).
- **Hero bg:** `linear-gradient(135deg,#12293f 0%,#1a3a5c 45%,#1f8b90 115%)` + a teal radial glow. Dark navy→teal.
- **Footer bg:** `--navy-deep #12293f` (flat dark navy).
- **Navbar:** uses original colored `logo.png` at `height:76px` (mobile `60px`) on the white sticky header. **This is CORRECT — leave entirely UNCHANGED. No boxes anywhere.**
- **Cache-bust:** stylesheet is linked as `styles.css?v=<version>`. Current value in the working tree is `?v=20260922m`. Any CSS change in this task MUST bump it again (use `?v=20260923a`).
- **i18n / a11y to preserve:** every `data-en`/`data-es` attribute, the `.lang-switch` buttons + `script.js` `setLang`, mobile nav toggle (`script.js`), all `aria-label`s and `alt` text. `script.js` must not need edits for either path.

### Original `.footer-brand` recovered from git history (for the FALLBACK path)

The text wordmark was replaced by an `<img>` in commit `be7f892` ("make IB Bridge logo more prominent"). The pre-logo state is commit `614c2d4`. Exact originals to restore if falling back:

- **HTML** (`614c2d4:index.html`):
  ```html
  <p class="footer-brand">IB Bridge</p>
  ```
  (directly above the existing `<p class="footer-tag">…</p>`, inside `.footer-inner`).
- **CSS** (`614c2d4:styles.css`, line 252):
  ```css
  .footer-brand { font-family: "Poppins"; font-weight: 700; font-size: 1.3rem; color: #fff; margin-bottom: 2px; }
  ```
  (The current `styles.css` instead has the image-era rule `.footer-brand { display: inline-flex; margin: 0 auto 14px; }` — replace it with the text rule above when falling back.)

## Logo pixel-classification split (Pillow, from inspecting `logo.png`)

`logo.png` = RGBA, **1536×1024**, transparent background, hard-ish alpha edges, content **bbox (228,144,1307,814)**. The real logo = TEAL bridge arcs + NAVY "IB Bridge" wordmark + thin NAVY tagline.

Full-image classification of **opaque pixels (alpha ≥ 20)**, total opaque ≈ **211,709 px**:

| Class | Rule used | Count | % of opaque |
|---|---|---|---|
| **NAVY** (wordmark + tagline) | `brightness < 120` AND `b ≥ r` | 36,589 | **17.3%** |
| **TEAL** (bridge arcs) | `g>r` AND `b>r` AND `120 ≤ brightness < 232` AND `sat > 0.12` | 138,836 | **65.6%** |
| light halo (anti-alias edge) | `brightness ≥ 232` | 33,325 | 15.7% |
| other (edge blend) | remainder | 2,959 | 1.4% |

Representative sampled colors:
- NAVY wordmark/tagline: `(13,20,67)`, `(25,39,86)`, `(26,41,88)` — very dark, blue-dominant, brightness ~33–52.
- TEAL arcs: cyan/teal, green+blue well above red, saturation > 0.12, brightness ~120–230.
- The ~15.7% "halo ≥ 232" and ~1.4% "other" are the anti-aliased edge pixels between glyph/arc and transparency — these must be handled by **blending toward the target color proportionally** (see step 2) so edges stay clean (no speckle, no dark fringe).

Takeaway: a brightness/hue threshold cleanly separates the two inks. Recolor ONLY the navy class → white; keep teal untouched; blend edge pixels toward white or teal based on their nearest class so no halo artifacts remain.

---

# Implementation Plan

- [ ] 1. **Confirm the starting working-tree state matches the context above.**
      Read `index.html` (hero + footer blocks) and `styles.css` to confirm: hero & footer `<img>` both point at `logo-ondark.png`, no `.logo-chip`/white box remains, navbar still uses `logo.png`, CSS link is `styles.css?v=20260922m`. Do NOT revert these; they are the intended starting point.
      Files: (read-only) `index.html`, `styles.css`.
      Verify: `cd /projects/sandbox/ib-bridge && git --no-pager diff --stat HEAD` shows only `index.html` and `styles.css` modified; `grep -n "logo-chip" styles.css index.html` returns nothing.

- [ ] 2. **PRIMARY ATTEMPT — regenerate `logo-ondark.png` as a true two-tone "logo on dark" brand variant.**
      Write a Pillow script (keep it in the artifacts dir, e.g. `.agents/tasks/ib-bridge-fix-logo-dark-variant-2026-09-23/make_ondark.py`) that opens `logo.png` (RGBA 1536×1024), iterates every pixel, preserves the alpha channel **exactly** (never change `a`), and recolors by class:
      - **NAVY ink** (`brightness < 120` and `b ≥ r`) → set RGB to near-white **`#F3F7F8`** (243,247,248). Keep this threshold at 120; it fully captures the wordmark + tagline (17.3% of opaque pixels sampled at brightness ~33–52, well under 120).
      - **TEAL arcs** (`g>r` and `b>r` and `brightness ≥ 120` and `sat > 0.12`) → **leave RGB unchanged** (keep original teal).
      - **Edge/anti-alias pixels** (`brightness ≥ 232` halo, or ambiguous "other"): do NOT hard-recolor. Blend each toward the target of its nearest class to avoid speckle/fringe — i.e. for pixels adjacent to navy glyphs, lerp RGB toward `#F3F7F8` by `(brightness-120)/(255-120)` clamped to [0,1]; leave teal-adjacent edges on the teal side. A simple robust approach: compute a per-pixel "navy-ness" weight `w = clamp((120 - brightness)/120, 0, 1)` for pixels where `b ≥ r`, and set `RGB = lerp(originalRGB, #F3F7F8, w)`; teal pixels (`g>r and b>r`) get `w=0`. This keeps glyph interiors solid white, keeps arcs teal, and feathers edges cleanly.
      Save as `logo-ondark.png` (overwrite the existing partial file), same 1536×1024 canvas, RGBA.
      Files: create `.agents/.../make_ondark.py`, overwrite `logo-ondark.png`.
      Verify: run the script with `python3 .agents/tasks/ib-bridge-fix-logo-dark-variant-2026-09-23/make_ondark.py`; then re-run a Pillow check and confirm: size is `(1536,1024)`, mode `RGBA`, alpha histogram **identical** to `logo.png`'s alpha histogram (asserts alpha untouched), navy-class pixel count dropped to ~0 (wordmark now white), teal-class count ≈ unchanged (~138k). Print the counts.

- [ ] 3. **Render hero and footer with the regenerated `logo-ondark.png` and capture CROPPED screenshots (NEVER full-page).**
      The HTML already points hero & footer at `logo-ondark.png` (from step 1), so no HTML change is needed to render. Write a Playwright (Python) script in the artifacts dir that serves the site locally (e.g. `python3 -m http.server` from the repo root, or load the file via `file://` — prefer the http server so relative asset paths resolve) and captures, under the artifacts dir:
      - **Desktop** viewport **1280×800**: `hero_desktop.png` via `page.locator("section.hero").screenshot()`; `footer_desktop.png` via `page.locator("footer.site-footer").screenshot()`.
      - **Mobile** viewport **390×800**: `hero_mobile.png` and `footer_mobile.png` the same element-cropped way.
      **SCREENSHOT RULES (CRITICAL):** set `viewport` explicitly on the context; capture ONLY element-cropped or viewport-sized images; scroll to the element first if needed. **NEVER pass `full_page=True`. Never take a full-page screenshot.** Every output image must be well under 8000px in BOTH width and height (element crops here are a few hundred px tall — a full-page shot of this long page would exceed 8000px and broke the previous run). Close the http server when done.
      Files: create `.agents/.../shoot.py`; outputs `hero_desktop.png`, `footer_desktop.png`, `hero_mobile.png`, `footer_mobile.png` in the artifacts dir.
      Verify: all four PNGs exist; run a Pillow check asserting each image's width < 8000 and height < 8000 (print dimensions). The coder then **opens/views all four images**.

- [ ] 4. **DECISION GATE — visual-judgment call made by the coder after viewing the step-3 screenshots.**
      Look at the four cropped screenshots. The two-tone `logo-ondark.png` **PASSES (→ SHIP, keep the primary wiring)** only if ALL hold: (a) it is still recognizably the real IB Bridge logo (teal bridge + readable wordmark), not a flat white silhouette; (b) the wordmark "IB Bridge" + tagline are legible WHITE text on both the hero gradient and the navy footer; (c) edges are clean — no speckle, no dark navy fringe, no leftover box; (d) the teal bridge does not wash out against the teal part of the hero gradient (no teal-on-teal disappearance). If it looks good on BOTH desktop and mobile, hero AND footer → **go to step 5 (ship)**. If ANY criterion fails — especially teal-on-teal washout or an ugly/illegible result — → **go to step 6 (fallback: remove both)**. **When in doubt, choose removal** — the owner explicitly said *"try to fix that but if not just delete both."* Record the decision and one-line reasoning in the step output.
      Files: none (judgment + note).
      Verify: decision recorded (SHIP or FALLBACK) with reasoning referencing the specific screenshots.

- [ ] 5. **(SHIP PATH — only if step 4 = PASS) Finalize the two-tone variant and bump the cache-bust.**
      The hero/footer HTML already references `logo-ondark.png` box-free at the correct sizes (`.hero-logo` `height:104px`, `.footer-logo` `height:56px`) — leave as-is. Only change needed: bump the stylesheet version in `index.html` from `styles.css?v=20260922m` to **`styles.css?v=20260923a`** (a CSS/asset change is shipping, so cache-bust). Confirm no `.logo-chip` or box CSS remains, navbar `logo.png` untouched, and all `data-en`/`data-es`/`alt`/`aria` intact. Then **skip step 6** and go to step 7.
      Files: modify `index.html` (version string only).
      Verify: `grep -n "styles.css?v=20260923a" index.html` matches; `grep -n "logo-chip" styles.css index.html` empty; `grep -c "data-en" index.html` unchanged from HEAD count; re-run the step-3 render+crop and re-view to confirm nothing regressed.

- [ ] 6. **(FALLBACK PATH — only if step 4 = FALLBACK) Remove the logo from BOTH hero and footer; restore original markup/CSS.**
      Make all of these in one coherent edit (they leave the page buildable together):
      - **HERO (HTML):** delete the hero logo line `<div class="hero-logo-wrap"><img class="hero-logo" src="logo-ondark.png" alt="IB Bridge logo" /></div>`. The hero then begins with `.hero-pill` then `<h1>` as it did originally.
      - **HERO (CSS):** delete the now-dead `.hero-logo-wrap { margin-bottom: 22px; }` and `.hero-logo { height: 104px; width: auto; display: block; }` rules in `styles.css`.
      - **FOOTER (HTML):** replace `<div class="footer-brand"><img class="footer-logo" src="logo-ondark.png" alt="IB Bridge logo" /></div>` with the original text wordmark `<p class="footer-brand">IB Bridge</p>` (recovered from `614c2d4`). Keep the existing `<p class="footer-tag">…</p>` line directly below unchanged.
      - **FOOTER (CSS):** replace the image-era rule `.footer-brand { display: inline-flex; margin: 0 auto 14px; }` with the recovered original text rule `.footer-brand { font-family: "Poppins"; font-weight: 700; font-size: 1.3rem; color: #fff; margin-bottom: 2px; }`. Delete the dead `.footer-logo { height: 56px; width: auto; display: block; }` rule.
      - **CACHE-BUST:** bump `index.html` stylesheet to `styles.css?v=20260923a`.
      - Leave navbar `logo.png` untouched. Do NOT delete `logo.png`/`logo-light.png`/`logo-ondark.png` files from disk (harmless unused assets; removing files is out of scope and risks breaking the navbar reference) — just stop referencing the dark variants in hero/footer. No boxes anywhere.
      Files: modify `index.html`, `styles.css`.
      Verify: `grep -n "logo-ondark\|hero-logo\|footer-logo" index.html` returns nothing; `grep -n 'footer-brand">IB Bridge' index.html` matches; `grep -n '\.footer-brand { font-family: "Poppins"' styles.css` matches; `grep -n "hero-logo\|footer-logo" styles.css` returns nothing; `grep -n "styles.css?v=20260923a" index.html` matches. Re-run step-3 render+crop (hero now starts with pill+h1; footer shows white "IB Bridge" text over the tagline) and view the four images to confirm clean result, no box, navbar unchanged.

- [ ] 7. **Final integrity pass — i18n, a11y, assets, no full-page screenshots left behind.**
      Confirm whichever path shipped kept everything intact: all `data-en`/`data-es` attributes present (compare count to HEAD), `.lang-switch` + `script.js` untouched, mobile nav toggle untouched, remaining `alt`/`aria-label` text valid, no broken `src` references (every referenced image exists on disk), navbar still `logo.png` at 76/60px, zero `.logo-chip`/box CSS, cache-bust bumped to `20260923a`. Ensure no screenshot step anywhere used `full_page=True`.
      Files: (read-only) `index.html`, `styles.css`, `script.js`.
      Verify: `git --no-pager diff --stat HEAD`; manually confirm diff touches only the intended lines; `grep -rn "full_page" .agents/tasks/ib-bridge-fix-logo-dark-variant-2026-09-23/` shows only `full_page=False`/absent (no `True`); open the site in Playwright at 1280×800 and 390×800, element-crop hero+footer once more, and confirm render is correct.

- [ ] 8. **Commit on `fix/logo-dark-variant`, push, and open a PR into `main` via `gh api` (NOT `gh pr create`).**
      Stage only the task's real source changes — `index.html`, `styles.css`, and (ship path only) `logo-ondark.png`. Do NOT stage the `.agents/` scratch/screenshot artifacts. Commit with a clear message (e.g. ship: `fix: recolor logo wordmark white for dark hero/footer (teal bridge kept)`, or fallback: `fix: remove logo from dark hero/footer, restore text wordmark`). Push the branch. Open the PR with `gh api repos/duarteopdiniz-gif/ib-bridge/pulls` (fields: `title`, `head=fix/logo-dark-variant`, `base=main`, `body`). Never commit to `main` directly; never use `gh pr create`.
      Files: git operations only.
      Verify: `git log --oneline -1` shows the new commit on `fix/logo-dark-variant`; `git status` clean for tracked source files (artifacts remain untracked); `gh api repos/duarteopdiniz-gif/ib-bridge/pulls` call returns a PR URL/number; `git --no-pager diff main...fix/logo-dark-variant --stat` shows only intended files.

## Notes & assumptions
- The working tree already carries the primary attempt's wiring; the plan treats that as the starting point rather than reverting, so the branch stays coherent. Step 2 regenerates `logo-ondark.png` from scratch with documented thresholds so the asset is trustworthy regardless of the prior partial file.
- The decision gate (step 4) is deliberately a human-style visual judgment the coder makes from the cropped screenshots — the owner rejected both the white box and the flat-white silhouette, so the bar for SHIP is "still recognizably the real logo, legible, clean." Default to the fallback when uncertain.
- Files `logo-light.png` / `logo-ondark.png` are left on disk even in the fallback path; only their references are removed. Deleting assets is out of scope and risks the navbar. Navbar `logo.png` is never touched.
