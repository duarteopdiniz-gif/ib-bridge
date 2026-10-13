# Implementation Plan — Make the IB Bridge logo more present (on-dark two-tone variant)

## Goal & context

Make the IB Bridge logo confidently present across the static GitHub Pages site in
`/projects/sandbox/ib-bridge` by generating a **clean two-tone "on-dark" logo variant** and
placing it box-free in the hero and footer (dark surfaces), adding social OG/Twitter imagery,
and regenerating favicons — while preserving the bilingual EN/ES system, language switcher,
mobile nav, and accessibility.

**Why this approach (design decisions I am committing to):**

1. **Two-tone recolor, not a white chip and not a flat-white recolor.** The repo history shows two
   rejected approaches: a white rounded "chip" behind the logo (owner: "random pic with an ugly
   background… make it match with the background") and a naive full-white recolor (owner: "both logos
   don't look the same when it's just white and is nothing like the original"). The owner's KEY INSIGHT
   is that only the **navy** region disappears on dark; the **teal** region is already fine. So the
   correct variant recolors **only navy → white** and **keeps teal exactly**. This is the only
   remaining un-rejected path and matches the owner's explicit instruction.

2. **Classify navy vs teal by channel-dominance (hue), not brightness alone.** Pillow inspection of
   `logo.png` (below) shows the previous `make_ondark.py` attempt failed because it keyed whitening on
   `brightness < 120`. That left the blue-tinted anti-aliased **edge** pixels of the "IB"/tagline glyphs
   (brightness 200–255 but still blue-dominant) un-whitened, producing a navy/muddy fringe around white
   glyphs — exactly the "nothing like the original" result that got rejected. My classifier keys on
   **blue-dominance + the green-minus-red gap** (navy: `g−r` small; teal: `g−r` clearly positive) across
   the whole brightness range, with a smooth transition zone so edges go cleanly to white.

### Pillow facts confirmed by inspection (ground truth — do not re-assume)

- `logo.png` is **RGBA, 1536×1024**, fully transparent background. Alpha extrema `(0, 255)`.
- Alpha (content) **bbox = (228, 144, 1307, 814)** → content ≈ 1079 wide × 670 tall.
- **Navy family** (blue is the max channel AND `g − r < 40`): ≈ 53,100 opaque-ish pixels. Its brightness
  distribution is **bimodal**: a solid-glyph cluster at brightness ~40–79 (~27k px, e.g. the
  quantized `(32,32,80)` cluster of ~4.2k at coarse sampling) and a bright anti-aliased edge/halo
  cluster at brightness ~200–255 (~20k px). The muddy mid-band (brightness ~100–199, blue-dominant)
  is only ~3.2k px — this is the fringe the old attempt left behind.
- **Teal family** (`g` and `b` both high, `g − r ≥ 25`): ≈ 143,600 opaque pixels — dominant quantized
  cluster `(96,176,176)`. This includes the bridge arcs AND the word "Bridge".
- Dark-navy glyph region sits in the **lower band**, approx bbox `(230, 466)–(1144, 812)` — i.e. the
  "IB" wordmark + the thin "Your bridge to IB success" tagline, consistent with the owner's description.

### Project facts

- **Pure static site**, no build system, no package manifest, no README/AGENTS/CONTRIBUTING, no
  `.kiro/steering/*`. Files: `index.html`, `styles.css`, `script.js`, `logo.png` (colored master),
  `logo-light.png` + `logo-ondark.png` (earlier attempts — may be overwritten/regenerated/ignored),
  `favicon.png`, `apple-touch-icon.png`, `.nojekyll`.
- **Tooling available:** Python 3.9.25 with **Pillow 11.3.0** (confirmed) — used for all image
  generation and verification. There is no JS/CSS build step; "build" = open the files in a browser.
- Stylesheet is linked as `styles.css?v=20260923a` in `index.html` — **must be bumped on any CSS edit.**
- Current navbar: `<img class="brand-logo" src="logo.png" alt="IB Bridge — Your bridge to IB success">`
  on the light sticky header, `.brand-logo { height: 76px }` (60px under `max-width:720px`). **Keep as-is.**
- Current hero: opens with `.hero-pill` then `<h1>` — **no logo**. We re-add one.
- Current footer: `<p class="footer-brand">IB Bridge</p>` (text) + `<p class="footer-tag" data-en/data-es>` tagline.
  `.footer-brand { font-family:"Poppins"; font-weight:700; font-size:1.3rem; color:#fff; margin-bottom:2px }`.
- Hero bg: `linear-gradient(135deg,#12293f 0%,#1a3a5c 45%,#1f8b90 115%)` + a radial teal glow; contains
  `.hero-arcs` SVG positioned `top:8%` (so a logo placed above `.hero-pill` must not overlap the arcs).
- Footer bg: `--navy-deep #12293f`.
- Tokens: `--navy #1a3a5c`, `--navy-deep #12293f`, `--teal #2ba7ad`, `--teal-dark #1f8b90`,
  `--teal-light #7fd0d3`, `--radius 16px`, `--shadow-lift`. Fonts: Poppins + Nunito Sans.
- `data-en`/`data-es` attribute count is **88/88** on the current branch (per prior reviews). The
  language switcher in `script.js` iterates `[data-en]`/`[data-es]` and sets `innerHTML`; **image
  elements must carry no `data-*`** so they are never swapped.

### Assumptions (gaps noted, reasonable defaults chosen)

- Target white for navy glyphs = **near-white `#F3F7F8`** (the site's `--bg-alt`), not pure `#FFFFFF`,
  so the recolored wordmark reads as a soft brand white consistent with the hero's `#eaf5f6` text,
  avoiding a harsh pure-white clash. (If the reviewer prefers pure white, a one-line constant change.)
- The on-dark variant filename is **`logo-ondark.png`** (regenerate/overwrite the stale one).
- All generator/verifier Python scripts live under the task dir
  `.agents/tasks/ib-bridge-logo-presence/` so they are never swept into a site commit; only the PNGs
  and HTML/CSS changes are committed. The `.agents/` tree is already untracked.

---

# Implementation Plan

- [ ] 1. **Generate the clean two-tone on-dark logo variant with Pillow.**
      Write a generator script that opens `logo.png` as RGBA (assert size `(1536,1024)`), and for every
      pixel computes a **navy-ness weight `w ∈ [0,1]`** from channel-dominance (hue), NOT brightness
      alone. Classification tuned to this artwork:
      - Let `mx=max(r,g,b)`, `mn=min(r,g,b)`, `sat=(mx-mn)/mx` (0 if `mx==0`), `gr = g - r`.
      - **Teal test** (keep EXACTLY, `w=0`): `g>=r AND b>=r AND g>80 AND b>80 AND gr>=25`.
      - **Navy test** (recolor toward white): blue-dominant with small green/red gap →
        `b>=g AND b>=r AND gr < 40` (covers both the dark glyph bodies at brightness ~40–79 AND the
        bright blue-tinted anti-aliased edges at brightness ~200–255, which is what the old attempt missed).
      - **Transition zone** on `gr` between the two tests (`gr` from 25→40) → ramp `w` linearly from 1→0
        so no hard seam appears between a white glyph and an adjacent teal stroke.
      - Recolor: `new = round(channel + (TARGET - channel) * w)` per channel toward `TARGET=(243,247,248)`
        (`#F3F7F8`); **copy the original alpha byte unchanged** into the output (alpha preserved EXACTLY).
      - Edge/halo handling: because `w` is driven by hue, the bright anti-aliased navy edge pixels get
        `w≈1` and go to the same near-white as the glyph body, so white glyphs have clean edges with **no
        navy fringe and no leftover mid-band muddiness**. Teal arcs/"Bridge" keep `w=0` → unchanged.
      Save to `logo-ondark.png` (overwrite).
      Files: create `.agents/tasks/ib-bridge-logo-presence/make_ondark.py`; write `logo-ondark.png`.
      Verify: `python3 .agents/tasks/ib-bridge-logo-presence/make_ondark.py` prints
      `size (1536,1024) mode RGBA` and `alpha histogram identical: True`; the script must exit non-zero
      (assert) if the output alpha histogram differs from the source. Expected: alpha identical True.

- [ ] 2. **Verify the recolor with Pillow pixel accounting and a navy-swatch composite.**
      Write a verifier that reports, over `logo.png` → `logo-ondark.png`: (a) navy-family count
      **before vs after** using the Step 1 navy test — expect before ≈ 53k, **after ≈ near-zero**
      (specifically: opaque, blue-dominant, DARK pixels with brightness `< 120` must be **≈ 0**, i.e.
      no dark-navy survives); (b) teal-family count before vs after — expect **essentially unchanged**
      (within a tiny tolerance for the `gr` transition zone, e.g. Δ < 1%); (c) a composite of
      `logo-ondark.png` over a solid **`#12293f`** swatch saved to the task dir, plus programmatic
      samples: pixels in the lower wordmark band `(230,466)–(1144,812)` read **light** (brightness
      high) and pixels in the teal arc/"Bridge" region read **teal** (`gr>=25`, `g,b>120`). The script
      asserts and exits non-zero on any failure.
      Files: create `.agents/tasks/ib-bridge-logo-presence/verify_ondark.py`; writes
      `.agents/tasks/ib-bridge-logo-presence/ondark_on_navy.png`.
      Verify: `python3 .agents/tasks/ib-bridge-logo-presence/verify_ondark.py` exits 0 and prints
      `dark-navy after: 0` (or ≤ a few dozen stray px), `teal Δ < 1%`, `wordmark=light teal=teal: OK`.
      Open `ondark_on_navy.png` and confirm the "IB" + tagline are light and "Bridge" + arcs are teal
      with clean edges — this is the eye-test the prior attempt failed.

- [ ] 3. **Add the hero logo (box-free) using the on-dark variant.**
      In `index.html`, inside `.hero-inner`, insert an `<img class="hero-logo" src="logo-ondark.png"
      alt="IB Bridge logo" />` **above `.hero-pill`** (first child of `.hero-inner`). No wrapper chip,
      no background, no border. The `alt` is static — **no `data-*` attributes** (so the language
      switcher never touches it). In `styles.css` add `.hero-logo { height: 120px; width: auto;
      display: block; margin: 0 0 20px; }` (desktop target ~110–130px) and under `@media (max-width:720px)`
      add `.hero-logo { height: 90px; margin-bottom: 16px; }` (mobile ~84–96px). The hero logo sits above
      the pill and headline; confirm it does not overlap `.hero-arcs` (arcs are `top:8%`, height `60%`,
      low-opacity strokes — a logo at the top of flow content clears them).
      Files: `index.html`, `styles.css`.
      Verify: bump cache-bust (Step 7) then open `index.html` in a browser at desktop and mobile widths —
      the on-dark logo appears above the pill, legible on the gradient, no white box, no overlap with the
      arcs or `<h1>`. (Automated option: a Pillow/Playwright screenshot saved to the task dir if a headless
      browser is available; otherwise visual check.)

- [ ] 4. **Replace the footer text brand with the on-dark logo (box-free), keep the tagline.**
      In `index.html`, replace `<p class="footer-brand">IB Bridge</p>` with
      `<img class="footer-logo" src="logo-ondark.png" alt="IB Bridge logo" />` (static alt, no `data-*`).
      Leave `.footer-tag` and all other footer content unchanged. In `styles.css` add
      `.footer-logo { height: 58px; width: auto; display: block; margin: 0 auto 10px; }` (centered;
      desktop target ~52–64px). Remove the now-dead `.footer-brand` rule **only** after confirming no
      other HTML uses `class="footer-brand"` (grep: only the one footer `<p>` uses it today).
      Files: `index.html`, `styles.css`.
      Verify: after cache-bust bump, open the footer in a browser — the on-dark logo is centered above the
      unchanged teal tagline on the `--navy-deep` background, legible, no white box. Confirm the page has
      no remaining reference to `.footer-brand` in CSS and none in HTML.

- [ ] 5. **Create `og-image.png` (1200×630) and add OG/Twitter meta tags.**
      Write a Pillow script that creates a **1200×630** canvas filled with the site light bg
      (`#F3F7F8` or `#FFFFFF`), crops `logo.png` to its alpha bbox `(228,144,1307,814)`, scales it to fit
      within generous margins (e.g. max ~900×440, preserving aspect ratio) and composites it **centered**.
      Save `og-image.png` at the repo root. Then in `index.html` `<head>` add Open Graph + Twitter tags:
      `og:title`, `og:description` (reuse the existing meta description), `og:type=website`,
      `og:image` (→ `og-image.png`), `og:image:width/height` (1200/630), `twitter:card=summary_large_image`,
      `twitter:title`, `twitter:description`, `twitter:image`. Use relative `og-image.png` (GitHub Pages
      static) — note that some scrapers want absolute URLs; a reasonable default is the relative path since
      the deploy origin isn't specified here (flag for owner if an absolute canonical URL is known).
      Files: create `.agents/tasks/ib-bridge-logo-presence/make_og.py`; write `og-image.png`; edit `index.html`.
      Verify: `python3 .agents/tasks/ib-bridge-logo-presence/make_og.py` prints `og-image.png 1200x630`;
      open `og-image.png` to confirm the colored logo is centered with clean margins on a light bg; confirm
      the new `<meta>` tags are present once each in `<head>`.

- [ ] 6. **Regenerate `favicon.png` (32×32) and `apple-touch-icon.png` (180×180) from the bbox-cropped master.**
      Write a Pillow script that crops `logo.png` to its alpha bbox `(228,144,1307,814)`, then produces a
      **square** canvas (transparent) for each size, scales the crop to fit with small padding, centers it,
      and saves `favicon.png` (32×32) and `apple-touch-icon.png` (180×180) at the repo root (overwrite).
      Use `Image.LANCZOS` resampling. The existing `<link rel="icon">` and `<link rel="apple-touch-icon">`
      tags already point at these filenames — no HTML change needed for the links.
      Files: create `.agents/tasks/ib-bridge-logo-presence/make_icons.py`; overwrite `favicon.png`,
      `apple-touch-icon.png`.
      Verify: `python3 .agents/tasks/ib-bridge-logo-presence/make_icons.py` prints the two sizes
      `32x32` and `180x180`; open both PNGs and confirm the mark is centered and not squashed (aspect
      preserved).

- [ ] 7. **Bump the CSS cache-bust and run the i18n / nav / a11y preservation checklist.**
      In `index.html`, change `styles.css?v=20260923a` → a new token (e.g. `?v=20260924a`); it must appear
      exactly once. Then verify preservation end-to-end:
      - `data-en`/`data-es` counts are **still 88/88** and unchanged from before this task (no translated
        string added/dropped); the new logo `<img>` elements carry **no `data-*`**.
      - The language switcher still toggles EN⇄ES and persists to `localStorage` (`script.js` untouched).
      - Mobile nav toggle still opens/closes with correct `aria-expanded`/`aria-controls` (unchanged).
      - Navbar `logo.png` and its `alt`/`aria-label="IB Bridge home"` are **unchanged**; hero and footer
        logos have meaningful static `alt="IB Bridge logo"`.
      - No white boxes/chips anywhere; no horizontal overflow at 1280px and 390px.
      Files: `index.html` (cache-bust only in this step).
      Verify: in a browser, load the page, toggle EN⇄ES (all strings switch, logos never change), reload
      and confirm persisted language, open/close the mobile menu at 390px. Confirm
      `grep -c 'data-en' index.html` == `grep -c 'data-es' index.html` == 88 and the stylesheet link's
      `?v=` token appears exactly once. Everything renders with the two-tone logo present on hero + footer.

- [ ] 8. **Commit the site changes (not the task scripts' intermediate artifacts beyond what's wanted).**
      Stage and commit the real deliverables: `index.html`, `styles.css`, `logo-ondark.png`,
      `og-image.png`, `favicon.png`, `apple-touch-icon.png`. Do not commit the `.agents/` task scripts/
      screenshots (they live outside the site surface and the tree is already untracked). Commit on the
      current branch; do not push unless asked.
      Files: git staging of the six site files above.
      Verify: `git status` shows only the intended site files staged; `git diff --cached --stat` lists
      exactly those six; the working tree still builds (static — opens in browser) with the logo present.

## Notes / open items for the owner

- **Near-white target `#F3F7F8` vs pure `#FFFFFF`:** chosen `#F3F7F8` to match the site's soft brand
  white; trivially switchable if a crisper white is preferred.
- **OG image URL:** used a relative `og-image.png`. If the production GitHub Pages URL is known, switching
  `og:image`/`twitter:image` to an absolute URL improves scraper compatibility — flag for the owner.
- The crux risk is Step 1/2 (the recolor must pass the eye test that the prior attempt failed). The
  hue-based classifier + the `gr` transition zone specifically target the previously-muddy mid-band and
  bright navy edges; Step 2's navy-swatch composite is the gate before any HTML/CSS work proceeds.
