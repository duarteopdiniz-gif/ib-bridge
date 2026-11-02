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

  // Transform-based viewport: one clone of the last card at the front and the
  // first card at the end => [clone(last), o0..o(n-1), clone(first)]
  const viewport = document.createElement('div');
  viewport.className = 'reviews-viewport';
  track.parentNode.insertBefore(viewport, track);
  viewport.appendChild(track);

  const firstClone = originals[0].cloneNode(true);
  const lastClone = originals[n - 1].cloneNode(true);
  [firstClone, lastClone].forEach((c) => { c.setAttribute('aria-hidden', 'true'); setupReadMore(c); });
  track.insertBefore(lastClone, originals[0]);
  track.appendChild(firstClone);

  const slides = Array.from(track.children); // n + 2
  let pos = 1;          // start on the first real card
  let animating = false;

  function width() { return viewport.clientWidth; }
  function layout(animate) {
    track.style.transition = animate ? 'transform .5s ease' : 'none';
    track.style.transform = 'translateX(' + (-pos * width()) + 'px)';
  }
  function realIndex() { return ((pos - 1) % n + n) % n; }
  function syncDots() {
    const r = realIndex();
    dots.forEach((d, i) => d.classList.toggle('active', i === r));
  }

  // Dots: one per real review
  dotsWrap.innerHTML = '';
  const dots = originals.map((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-label', 'Go to review ' + (i + 1));
    b.addEventListener('click', () => { restartAuto(); goReal(i); });
    dotsWrap.appendChild(b);
    return b;
  });

  function move(dir) {
    if (animating) return;
    animating = true;
    pos += dir;
    layout(true);
    syncDots();
  }
  function goReal(i) { // jump to a specific real card (via dots)
    if (animating) return;
    pos = i + 1;
    layout(true);
    syncDots();
  }
  track.addEventListener('transitionend', () => {
    // When we land on a clone, snap (without animation) to the real twin
    if (pos === slides.length - 1) { pos = 1; layout(false); }
    else if (pos === 0) { pos = n; layout(false); }
    animating = false;
  });

  if (next) next.addEventListener('click', () => { restartAuto(); move(1); });
  if (prev) prev.addEventListener('click', () => { restartAuto(); move(-1); });

  // Auto-rotate
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
