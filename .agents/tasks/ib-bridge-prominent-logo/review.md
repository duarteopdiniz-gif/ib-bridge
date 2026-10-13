# Make the IB Bridge logo more present (navbar, hero, footer)

The branch enlarges the navbar logo, drops the mark onto the hero and footer on a reusable white rounded "chip", and bumps the stylesheet cache-bust version. The chip is the central design decision: the logo artwork is a mixed teal + light + dark-navy RGBA mark that would lose contrast on the navy→teal hero gradient and the dark `--navy-deep` footer, so both dark surfaces get the logo on a white card that reuses the site's existing `--radius` and `--shadow-lift` tokens. The navbar logo needs no chip because the header is already a light translucent surface. Saved Playwright screenshots at desktop (1280px) and mobile (390px) confirm all three placements and the mobile nav. The change also bundles in a logo-derived favicon and apple-touch-icon, which is outside the stated goal.

Watch for: a favicon + two new binary assets and two `<link>` tags are bundled into a branding-copy task (confirmed) — unrelated but low-risk.

**Verdict**: APPROVED

## High-level view

Across all three placements the logo is now unmistakably more present. The navbar mark grows from 62px to 76px (52px→60px mobile) with the header min-height and the mobile dropdown offset moved in lockstep to 86px so nothing is cramped or detached. The hero gains a white-chip logo above the pill and headline, and the footer's plain-text "IB Bridge" is replaced by the same chip treatment above the unchanged tagline. The screenshots show all three legible and tasteful, matching the site's card language.

Legibility — the one real risk in this task — is handled correctly. Both dark surfaces (hero gradient, navy footer) use the white chip rather than placing the transparent mark directly on dark, which the plan's artwork analysis showed would blend out. The desktop-top and footer screenshots confirm clean contrast in practice.

Preservation is clean: data-en/data-es attribute counts are identical to base (88/88), the three logo images carry static meaningful alt with no data-* leakage, the navbar `aria-label="IB Bridge home"` is intact, and the language switcher and mobile nav are untouched and functional in the screenshots. Cache-bust bumped to `?v=20260922k`, appearing exactly once.

The only thing beyond the brief is a favicon/apple-touch-icon pair (two new PNGs plus two `<link>` tags). It's coherent with "logo more present" and harmless, but it's scope the task didn't ask for and should be noted for the owner.

<details>
<summary>Issues (1)</summary>

1. **Favicon bundled into a copy task** — the branch adds `favicon.png`, `apple-touch-icon.png`, and two `<link>` tags not covered by the logo-placement goal. Low-risk and on-theme; flag to the owner so it's a conscious inclusion rather than merge the scope silently.

</details>

<details>
<summary>Details</summary>

### Navbar enlargement kept the header balanced

`.brand-logo` goes 62px→76px (and 52px→60px under `max-width: 720px`), and the two measurements pinned to the old header height move with it: `.header-inner` min-height 72px→86px and the mobile `.nav` dropdown `top: 72px`→`86px`. That lockstep is the part worth checking in a logo-resize, because a taller logo with a stale dropdown offset would leave a gap or overlap when the mobile menu opens. The `mobile-nav-open.png` screenshot shows the open menu sitting flush beneath the taller header, so the offset is correct.

### White chip for legibility on dark surfaces

```
.logo-chip {
  display: inline-flex; align-items: center; justify-content: center;
  background: #fff; border-radius: var(--radius); padding: 14px 22px;
  box-shadow: var(--shadow-lift);
}
```

The plan's Pillow analysis found the mark is ~67% teal with ~14% dark-navy pixels — the teal would blend into the teal end of the hero gradient (`#1f8b90`) and the navy pixels would vanish on `--navy-deep #12293f`. Rather than recolor the asset or accept poor contrast, both dark placements render it on a white card that reuses `--radius` and `--shadow-lift`, so it reads as intentional and matches the existing `.card` / `.price-card` language rather than a pasted-on image. `desktop-top.png` and `footer.png` both confirm clean contrast — the mark is fully legible on the white chip against the gradient and against the dark footer respectively. The hero chip sits left-aligned above the pill with no overlap against the arcs SVG or the `<h1>`, and the footer chip is centered (`margin: 0 auto 14px`) with the teal tagline directly beneath it.

### Content, bilingual attributes, and accessibility preserved

Both base and branch carry 88 `data-en` and 88 `data-es` attributes — no translated string was dropped or added, so the EN⇄ES switcher (which iterates `[data-en]`/`[data-es]` in `script.js`) has exactly the same surface to work on. The three logo `<img>` elements correctly carry no `data-*`, so they are never swapped by the switcher; the navbar logo keeps its descriptive `alt="IB Bridge — Your bridge to IB success"` and the hero/footer images use `alt="IB Bridge logo"`. The navbar brand link's `aria-label="IB Bridge home"` is unchanged. The footer rule was correctly stripped of its old `font-*`/`color` text properties (now an image container) and keeps `.footer-tag` as-is, so the tagline still sits below the new logo. Cache-bust bumped to `?v=20260922k`, present exactly once.

### Favicon bundled in

Beyond the three logo placements, the branch adds `favicon.png` (32×32) and `apple-touch-icon.png` (180×180) generated from `logo.png`, plus `<link rel="icon">` and `<link rel="apple-touch-icon">`. The commit explains the icons were cropped to the alpha bbox and centered on a square canvas so they aren't squashed, which is sound. It is on-theme with "logo more present" and carries no functional risk, but it is not what the task scoped. Worth surfacing to the owner so the extra assets are a conscious decision rather than an unnoticed scope expansion.

</details>

<details>
<summary>File map</summary>

- `index.html` — hero logo chip added above the pill; footer plain-text brand replaced with logo chip; favicon + apple-touch-icon `<link>`s added; cache-bust `j`→`k`.
- `styles.css` — `.brand-logo` and header/mobile-nav heights enlarged; new `.logo-chip` / `.hero-logo` / `.hero-logo-wrap` rules; `.footer-brand` converted to a centered chip container with `.footer-logo`.
- `favicon.png`, `apple-touch-icon.png` — new logo-derived icons (out of scope).
- `.agents/tasks/ib-bridge-prominent-logo/*.png` — Playwright evidence (desktop, desktop-top, mobile, mobile-nav-open, footer).

Full diff: `git diff main -- index.html styles.css`

</details>
