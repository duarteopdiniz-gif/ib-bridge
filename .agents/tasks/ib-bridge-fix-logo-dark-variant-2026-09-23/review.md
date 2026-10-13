# Logo removed from dark hero and footer; navbar logo untouched

The dark-hero and footer logo images were cut and the footer reverted to a text wordmark (`<p class="footer-brand">IB Bridge</p>`), with the dead chip/logo CSS removed and the original `.footer-brand` type styling restored. This is the owner-authorized **removal fallback** (Option B), not the two-tone recolor. The coder first attempted the two-tone `logo-ondark.png` variant, found the wordmark came out patchy/muddy on navy (white + teal + leftover dark navy inside the glyphs), judged it to be exactly the "nothing like the original" result the owner rejected, and fell back to removal as the owner explicitly permitted ("try to fix that but if not just delete both"). The change is tightly scoped: two files, three insertions, thirteen deletions.

Watch for: nothing blocking. The hero now leads with the pill + headline and the footer reads as clean white "IB Bridge" + teal tagline on navy — no white box anywhere (confirmed). The navbar still carries the colored `logo.png` and is byte-for-byte unchanged (confirmed).

**Verdict**: APPROVED

## High-level view

The chosen path is removal, explicitly sanctioned by the owner once the recolor failed the eye test. The verification note documents a genuine two-tone attempt (Pillow recolor of navy wordmark pixels, teal arcs preserved, alpha intact) rejected on legibility grounds — the owner's own stated rejection criterion. One caveat: the primary-attempt screenshots were overwritten, so the recolor-failure claim rests on the coder's note rather than a surviving artifact.

The removal is internally clean. Hero HTML now opens with `.hero-pill` then `<h1>`, matching the described original structure; footer HTML carries the text wordmark above an unchanged `.footer-tag`; and the `.footer-brand` rule restored on the branch is identical to the historical original at commit `614c2d4` (Poppins 700, 1.3rem, white). No dead CSS survives — `.logo-chip`, `.hero-logo-wrap`, `.hero-logo`, and `.footer-logo` are all gone, and there are no stray `logo-ondark`/`hero-logo`/`footer-logo` references in either file.

Branding posture is preserved where it matters. The navbar keeps the colored `logo.png` at 76px desktop / 60px mobile, unchanged, so the company mark still anchors the top of every page — the removal only drops the redundant dark-context copies that couldn't be made to look right. The mobile hero screenshot shows the colored navbar logo intact.

Content and i18n are untouched: `data-en` attribute count is 88 on both `main` and the branch, the language switcher and nav markup are unchanged, and `alt`/`aria-label` on the surviving navbar logo and nav controls are valid. The CSS cache-bust was bumped (`20260922k` → `20260923a`). No broken asset references remain, and the coder's measured scrollWidth == clientWidth on both viewports indicates no horizontal overflow.

<details>
<summary>Issues (1)</summary>

1. **Two-tone failure not independently verifiable** — the primary-attempt screenshots were overwritten by the final render, so the "muddy recolor" rejection rests on the coder's note, not a surviving artifact. Non-blocking: removal is independently owner-authorized and the final state verifies clean. No action required unless a future pass wants the rejected render retained for audit.

</details>

<details>
<summary>Details</summary>

### Removal was the correct branch to take

The owner's final instruction set two acceptable outcomes and a tie-breaker: a two-tone logo that genuinely resembles the original, or — failing that — delete both. The pivotal judgment is whether the recolor truly failed, because if it were salvageable, removal would be the lazy path. The verification note records a real attempt with concrete pixel accounting (navy wordmark pixels 36,589 → 99 recolored toward `#F3F7F8`, teal arcs preserved at 138,854 → 172,113, alpha histogram identical), and the stated failure mode — the wordmark rendering as a mix of white, teal, and leftover dark navy because the original glyphs carry internal teal-tinted anti-aliasing — is a credible, specific explanation, not a hand-wave. That is the owner's own rejection criterion ("nothing like the original"), so falling back to removal honors the instruction rather than dodging it.

The primary-attempt screenshots were overwritten by the final render, so the muddy two-tone result can't be re-inspected from the evidence. This doesn't change the verdict — removal is independently owner-authorized and the final state is verifiable — but the recolor-failure claim rests on the coder's note rather than a surviving artifact. (possible, non-blocking)

### Hero and footer match the described original structure

The hero `<img>` wrapper is gone and the section now opens with `.hero-pill` then `<h1>`, exactly the fallback structure specified. The footer logo `<img>` is replaced by `<p class="footer-brand">IB Bridge</p>` sitting directly above the unchanged bilingual `.footer-tag`. The restored `.footer-brand` rule on the branch —

```css
.footer-brand { font-family: "Poppins"; font-weight: 700; font-size: 1.3rem; color: #fff; margin-bottom: 2px; }
```

— is character-for-character the historical original at commit `614c2d4`, so this is a true revert, not an approximation. (confirmed)

### No white box, and the dark surfaces read clean

The hero screenshots (desktop and mobile) show the pill and headline leading the section with no logo and no chip. The footer screenshots show bold white "IB Bridge" over the teal "Your bridge to IB success" tagline on navy, with the phone/WhatsApp line and copyright below — no image, no white box, no leftover padding artifact. The earlier white-box reject and the flat-white reject are both resolved. (confirmed)

### Navbar branding preserved

The branch's navbar still renders `<img class="brand-logo" src="logo.png" ...>` inside the `.brand` anchor, with `.brand-logo` at 76px desktop and 60px mobile — unchanged from `main`. The mobile hero crop shows the colored logo at top-left. The removal drops only the dark-context copies, leaving the company mark on the light header where it already worked. (confirmed)

### Content, i18n, and accessibility intact

`data-en` attribute count is 88 on both `main` and the branch, so no bilingual string was dropped when the footer wordmark changed from image to text. The one piece of visible text that changed container (footer brand) is not a translated string in either version. The language switcher buttons, nav toggle with `aria-expanded`/`aria-controls`, and the navbar logo's descriptive `alt` all survive unchanged, and `script.js` is not touched by the diff. (confirmed)

### Cache-bust and asset integrity

The stylesheet link moved from `styles.css?v=20260922k` to `?v=20260923a`, so the CSS change won't be served stale. Hero and footer no longer reference any image; the only remaining logo asset reference is the navbar `logo.png`, which exists. No `logo-ondark`, `hero-logo`, `footer-logo`, or `logo-chip` reference survives in HTML or CSS. The coder's reported scrollWidth == clientWidth (1280/1280 desktop, 390/390 mobile) indicates no horizontal overflow introduced. (confirmed)

</details>

<details>
<summary>File map</summary>

- `index.html` — hero logo `<img>`/wrapper removed (hero now starts with `.hero-pill`); footer logo `<img>` replaced with `<p class="footer-brand">IB Bridge</p>`; CSS cache-bust bumped.
- `styles.css` — removed `.logo-chip`, `.hero-logo-wrap`, `.hero-logo`, `.footer-logo`; restored original `.footer-brand` type styling.

Full diff: `git -C /projects/sandbox/ib-bridge diff main...fix/logo-dark-variant`

</details>
