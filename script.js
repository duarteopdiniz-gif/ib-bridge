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

// ===== Reviews carousel (native scroll + snap, loop-aware) =====
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

  // Clone the full set before and after so the user can keep scrolling past
  // either edge; we invisibly jump back into the "real" middle band.
  const headClones = originals.map((c) => { const k = c.cloneNode(true); k.setAttribute('aria-hidden', 'true'); setupReadMore(k); return k; });
  const tailClones = originals.map((c) => { const k = c.cloneNode(true); k.setAttribute('aria-hidden', 'true'); setupReadMore(k); return k; });
  headClones.forEach((k) => track.insertBefore(k, originals[0]));
  tailClones.forEach((k) => track.appendChild(k));

  // Measured geometry (recomputed on resize). step = card width + gap.
  let stepPx = 1;
  function gap() { return parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap || '20') || 20; }
  function measure() { stepPx = originals[0].getBoundingClientRect().width + gap(); }
  function bandStart() { return n * stepPx; } // scrollLeft that shows the first real card at the left edge
  function setWidth() { return n * stepPx; }   // width of one full set of n cards

  // Dots: one per real review
  dotsWrap.innerHTML = '';
  const dots = originals.map((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-label', 'Go to review ' + (i + 1));
    b.addEventListener('click', () => { restartAuto(); goToLogical(i, true); });
    dotsWrap.appendChild(b);
    return b;
  });

  // Logical position: how many cards away from the first real card (can be
  // negative or >= n because of the clone bands). The real review index is
  // this value reduced modulo n.
  function logicalFromScroll() { return (track.scrollLeft - bandStart()) / stepPx; }
  function realIndex() {
    const r = Math.round(logicalFromScroll());
    return ((r % n) + n) % n;
  }
  function syncDots() {
    const r = realIndex();
    dots.forEach((d, i) => d.classList.toggle('active', i === r));
  }

  // Instant, invisible jump that temporarily disables scroll-snap so the browser
  // doesn't fight us by re-snapping the position we set.
  function jumpBy(delta) {
    const prevSnap = track.style.scrollSnapType;
    const prevBehavior = track.style.scrollBehavior;
    track.style.scrollSnapType = 'none';
    track.style.scrollBehavior = 'auto';
    track.scrollLeft += delta;
    // Force layout so the assignment sticks before we restore snapping.
    void track.offsetWidth;
    track.style.scrollSnapType = prevSnap;
    track.style.scrollBehavior = prevBehavior;
  }

  // Seamless loop: once the scroll settles, if we've drifted a full set into
  // either clone band, hop back by one set width (instantly) so the visible
  // card is unchanged but there's always room to keep going either way.
  function recenter() {
    const logical = logicalFromScroll();
    if (logical <= -n + 0.5) { jumpBy(setWidth()); }
    else if (logical >= n - 0.5) { jumpBy(-setWidth()); }
  }

  // Track whether a programmatic smooth scroll is in flight. We only recenter
  // when the scroll has truly settled (no animation running and velocity ~0),
  // which avoids the old race where an instant jump fought the smooth animation.
  let animating = false;
  let settleTimer = null;
  let rafPending = false;
  function onScroll() {
    if (!rafPending) {
      rafPending = true;
      requestAnimationFrame(() => { syncDots(); rafPending = false; });
    }
    clearTimeout(settleTimer);
    settleTimer = setTimeout(onSettle, 150);
  }
  function onSettle() {
    animating = false;
    recenter();
    syncDots();
  }
  track.addEventListener('scroll', onScroll, { passive: true });

  // Move to an absolute logical position. When smooth is false the jump is
  // truly instant: CSS sets scroll-behavior:smooth on the track, so we must
  // override it inline for the duration of the assignment, otherwise even an
  // "auto" scrollTo animates and the dots read the wrong card mid-flight.
  function goToLogical(i, smooth) {
    const target = bandStart() + i * stepPx;
    if (smooth) {
      animating = true;
      track.scrollTo({ left: target, behavior: 'smooth' });
    } else {
      const prevBehavior = track.style.scrollBehavior;
      const prevSnap = track.style.scrollSnapType;
      track.style.scrollBehavior = 'auto';
      track.style.scrollSnapType = 'none';
      track.scrollLeft = target;
      void track.offsetWidth;
      track.style.scrollBehavior = prevBehavior;
      track.style.scrollSnapType = prevSnap;
    }
  }

  // Advance/retreat by exactly one card. Before a move, if we're already at the
  // edge of the clone band, recenter instantly so a full step of room remains in
  // the direction we're about to go — guaranteeing a seamless wrap in both
  // directions (e.g. last real card -> first real card with no snap-back).
  function move(dir) {
    // Settle any in-flight state and normalise into the middle band first.
    recenter();
    const logical = logicalFromScroll();
    if (dir > 0 && logical >= n - 1.5) { jumpBy(-setWidth()); }
    else if (dir < 0 && logical <= -n + 1.5) { jumpBy(setWidth()); }
    animating = true;
    track.scrollTo({ left: track.scrollLeft + dir * stepPx, behavior: 'smooth' });
  }
  function nextSlide() { move(1); }
  function prevSlide() { move(-1); }
  if (next) next.addEventListener('click', () => { restartAuto(); nextSlide(); });
  if (prev) prev.addEventListener('click', () => { restartAuto(); prevSlide(); });

  // Auto-rotate — pauses while the user interacts, resumes after
  let timer = null;
  function startAuto() { stopAuto(); timer = setInterval(nextSlide, 5000); }
  function stopAuto() { if (timer) { clearInterval(timer); timer = null; } }
  function restartAuto() { stopAuto(); startAuto(); }
  ['mouseenter', 'focusin', 'touchstart', 'pointerdown'].forEach((ev) =>
    track.addEventListener(ev, stopAuto, { passive: true }));
  ['mouseleave', 'touchend', 'pointerup'].forEach((ev) =>
    track.addEventListener(ev, () => { restartAuto(); }, { passive: true }));

  window.addEventListener('resize', () => {
    const current = realIndex();
    measure();
    goToLogical(current, false);
    syncDots();
  });

  // Start positioned on the first real card
  requestAnimationFrame(() => {
    measure();
    goToLogical(0, false);
    syncDots();
    startAuto();
  });
})();
