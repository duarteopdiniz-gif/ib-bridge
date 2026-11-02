// ===== Mobile nav toggle =====
const toggle = document.querySelector('.nav-toggle');
const nav = document.getElementById('nav-menu');

toggle.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  toggle.classList.toggle('open', open);
  toggle.setAttribute('aria-expanded', String(open));
});

nav.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    nav.classList.remove('open');
    toggle.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  });
});

// ===== Language switch (EN / ES) =====
function setLang(lang) {
  document.documentElement.lang = lang;
  document.querySelectorAll('[data-' + lang + ']').forEach((el) => {
    el.innerHTML = el.getAttribute('data-' + lang);
  });
  document.querySelectorAll('.lang-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
  try { localStorage.setItem('ibbridge-lang', lang); } catch (e) {}
}

document.querySelectorAll('.lang-btn').forEach((btn) => {
  btn.addEventListener('click', () => setLang(btn.dataset.lang));
});

// Restore saved language, or auto-pick Spanish for Spanish-speaking browsers
(function initLang() {
  let saved = null;
  try { saved = localStorage.getItem('ibbridge-lang'); } catch (e) {}
  const browserEs = (navigator.language || '').toLowerCase().startsWith('es');
  setLang(saved || (browserEs ? 'es' : 'en'));
})();

// ===== Current year in footer =====
document.getElementById('year').textContent = new Date().getFullYear();

// ===== Reviews carousel =====
(function initReviews() {
  const track = document.getElementById('reviews-track');
  if (!track) return;
  const originals = Array.from(track.querySelectorAll('.review-card'));
  const prev = document.getElementById('rev-prev');
  const next = document.getElementById('rev-next');
  const dotsWrap = document.getElementById('rev-dots');
  const n = originals.length;
  if (n === 0) return;

  function setupReadMore(card) {
    const text = card.querySelector('.review-text');
    const btn = card.querySelector('.review-more');
    if (!text || !btn) return;
    card.classList.add('is-clamped');
    requestAnimationFrame(() => {
      if (text.scrollHeight - text.clientHeight > 4) { btn.hidden = false; }
      else { card.classList.remove('is-clamped'); }
    });
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const expanded = card.classList.toggle('is-expanded');
      card.classList.toggle('is-clamped', !expanded);
      btn.setAttribute('aria-expanded', String(expanded));
    });
  }
  originals.forEach(setupReadMore);

  // Multi-card viewport with a seamless infinite loop.
  // We clone the whole set before AND after the originals, so there are always
  // enough cards to fill the visible window past either edge.
  const viewport = document.createElement('div');
  viewport.className = 'reviews-viewport';
  track.parentNode.insertBefore(viewport, track);
  viewport.appendChild(track);

  const headClones = originals.map((c) => { const k = c.cloneNode(true); k.setAttribute('aria-hidden', 'true'); setupReadMore(k); return k; });
  const tailClones = originals.map((c) => { const k = c.cloneNode(true); k.setAttribute('aria-hidden', 'true'); setupReadMore(k); return k; });
  headClones.forEach((k) => track.insertBefore(k, originals[0]));
  tailClones.forEach((k) => track.appendChild(k));
  const all = Array.from(track.children); // [head(n)][orig(n)][tail(n)]

  // Responsive card sizing: ~1 card on phones, up to 3 on desktop
  function applySizing() {
    const vw = viewport.clientWidth;
    let per = 3, gap = 20;
    if (vw < 560) { per = 1; gap = 16; }
    else if (vw < 920) { per = 2; gap = 18; }
    const cardW = Math.floor((vw - gap * (per - 1)) / per);
    track.style.setProperty('--rev-gap', gap + 'px');
    all.forEach((c) => { c.style.width = cardW + 'px'; });
    return { gap, cardW };
  }

  const stepPx = () => {
    const r = applySizing();
    return r.cardW + r.gap;
  };

  let index = 0; // logical index into originals (0..n-1); start on first real card
  let animating = false;

  function offsetFor(logical) {
    // position of originals[logical] = after n head clones
    return (n + logical) * stepPx();
  }
  function layout(animate) {
    track.style.transition = animate ? 'transform .5s ease' : 'none';
    track.style.transform = 'translateX(' + (-offsetFor(index)) + 'px)';
  }
  function syncDots() {
    const r = ((index % n) + n) % n;
    dots.forEach((d, i) => d.classList.toggle('active', i === r));
  }

  // Dots: one per real review
  dotsWrap.innerHTML = '';
  const dots = originals.map((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-label', 'Go to review ' + (i + 1));
    b.addEventListener('click', () => { restartAuto(); goTo(i); });
    dotsWrap.appendChild(b);
    return b;
  });

  function move(dir) {
    if (animating) return;
    animating = true;
    index += dir;
    layout(true);
    syncDots();
  }
  function goTo(i) {
    if (animating) return;
    animating = true;
    index = i;
    layout(true);
    syncDots();
  }
  track.addEventListener('transitionend', () => {
    // Keep `index` within 0..n-1 by snapping (no animation) to the equivalent real card
    if (index >= n) { index -= n; layout(false); }
    else if (index < 0) { index += n; layout(false); }
    animating = false;
  });

  if (next) next.addEventListener('click', () => { restartAuto(); move(1); });
  if (prev) prev.addEventListener('click', () => { restartAuto(); move(-1); });

  // Auto-rotate — pauses on hover/focus, resumes after
  let timer = null;
  function startAuto() { stopAuto(); timer = setInterval(() => move(1), 5000); }
  function stopAuto() { if (timer) { clearInterval(timer); timer = null; } }
  function restartAuto() { stopAuto(); startAuto(); }
  ['mouseenter', 'focusin'].forEach((ev) => viewport.addEventListener(ev, stopAuto));
  ['mouseleave', 'focusout'].forEach((ev) => viewport.addEventListener(ev, startAuto));

  // Touch swipe
  let x0 = null;
  track.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; stopAuto(); }, { passive: true });
  track.addEventListener('touchend', (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) move(dx < 0 ? 1 : -1);
    x0 = null; startAuto();
  });

  window.addEventListener('resize', () => layout(false));
  requestAnimationFrame(() => { layout(false); syncDots(); startAuto(); });
})();
