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
    btn.addEventListener('click', () => {
      const expanded = card.classList.toggle('is-expanded');
      card.classList.toggle('is-clamped', !expanded);
      btn.setAttribute('aria-expanded', String(expanded));
    });
  }
  originals.forEach(setupReadMore);

  // Clone the full set before and after the originals for a seamless infinite loop
  const head = originals.map((c) => { const k = c.cloneNode(true); k.setAttribute('aria-hidden', 'true'); setupReadMore(k); return k; });
  const tail = originals.map((c) => { const k = c.cloneNode(true); k.setAttribute('aria-hidden', 'true'); setupReadMore(k); return k; });
  head.forEach((k) => track.insertBefore(k, originals[0]));
  tail.forEach((k) => track.appendChild(k));
  const all = Array.from(track.querySelectorAll('.review-card')); // head(n) + originals(n) + tail(n)

  // Dots: exactly one per real review
  dotsWrap.innerHTML = '';
  const dots = originals.map((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-label', 'Go to review ' + (i + 1));
    b.addEventListener('click', () => { stopAuto(); goTo(i, true); startAuto(); });
    dotsWrap.appendChild(b);
    return b;
  });

  const padLeft = () => parseInt(getComputedStyle(track).paddingLeft || '0', 10);
  const step = () => (all[1] ? all[1].offsetLeft - all[0].offsetLeft : all[0].offsetWidth);
  const baseLeft = () => all[n].offsetLeft - padLeft(); // scrollLeft that shows original #0 at the start
  let index = 0; // logical index into the ORIGINAL set (can be negative/over n during wrap)

  function positionTo(logical, smooth) {
    const target = (all[n + logical] ? all[n + logical].offsetLeft - padLeft() : baseLeft() + logical * step());
    track.scrollTo({ left: target, behavior: smooth ? 'smooth' : 'auto' });
  }
  function syncDots(logical) {
    const active = ((logical % n) + n) % n;
    dots.forEach((d, i) => d.classList.toggle('active', i === active));
  }
  function goTo(logical, smooth) { index = logical; positionTo(logical, smooth); syncDots(logical); }

  // After a scroll settles on a clone, jump invisibly to the matching real card
  let wrapTimer = null;
  function handleEdges() {
    clearTimeout(wrapTimer);
    wrapTimer = setTimeout(() => {
      const rel = Math.round((track.scrollLeft - baseLeft()) / step());
      const norm = ((rel % n) + n) % n;
      if (rel !== norm) { index = norm; positionTo(norm, false); } // snap clone -> real
      else { index = rel; }
      syncDots(index);
    }, 160);
  }

  function nextSlide() { index = index + 1; positionTo(index, true); syncDots(index); }
  function prevSlide() { index = index - 1; positionTo(index, true); syncDots(index); }
  if (next) next.addEventListener('click', () => { stopAuto(); nextSlide(); startAuto(); });
  if (prev) prev.addEventListener('click', () => { stopAuto(); prevSlide(); startAuto(); });

  let ticking = false;
  track.addEventListener('scroll', () => {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(() => {
        const rel = Math.round((track.scrollLeft - baseLeft()) / step());
        syncDots(rel);
        ticking = false;
      });
    }
    handleEdges();
  });

  // Auto-rotate (spin) — pauses on hover/touch, resumes after
  let timer = null;
  function startAuto() { stopAuto(); timer = setInterval(nextSlide, 4500); }
  function stopAuto() { if (timer) { clearInterval(timer); timer = null; } }
  ['mouseenter', 'focusin', 'touchstart', 'pointerdown'].forEach((ev) =>
    track.addEventListener(ev, stopAuto, { passive: true }));
  track.addEventListener('mouseleave', startAuto);

  window.addEventListener('resize', () => positionTo(index, false));
  requestAnimationFrame(() => { positionTo(0, false); syncDots(0); startAuto(); });
})();
