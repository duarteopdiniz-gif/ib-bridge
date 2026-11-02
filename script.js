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
  const cards = Array.from(track.querySelectorAll('.review-card'));
  const prev = document.getElementById('rev-prev');
  const next = document.getElementById('rev-next');
  const dotsWrap = document.getElementById('rev-dots');

  // Build dots
  cards.forEach((_, i) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-label', 'Go to review ' + (i + 1));
    b.addEventListener('click', () => scrollToCard(i));
    dotsWrap.appendChild(b);
  });
  const dots = Array.from(dotsWrap.children);

  function cardStep() {
    if (cards.length < 2) return cards[0].offsetWidth;
    return cards[1].offsetLeft - cards[0].offsetLeft;
  }
  function currentIndex() {
    return Math.round(track.scrollLeft / cardStep());
  }
  function scrollToCard(i) {
    const idx = Math.max(0, Math.min(cards.length - 1, i));
    track.scrollTo({ left: idx * cardStep(), behavior: 'smooth' });
  }
  function update() {
    const idx = currentIndex();
    dots.forEach((d, i) => d.classList.toggle('active', i === idx));
    if (prev) prev.disabled = idx <= 0;
    if (next) next.disabled = idx >= cards.length - 1;
  }

  if (prev) prev.addEventListener('click', () => scrollToCard(currentIndex() - 1));
  if (next) next.addEventListener('click', () => scrollToCard(currentIndex() + 1));
  let ticking = false;
  track.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { update(); ticking = false; });
  });
  window.addEventListener('resize', update);

  // Read-more: only show the toggle when the text actually overflows when clamped
  cards.forEach((card) => {
    const text = card.querySelector('.review-text');
    const btn = card.querySelector('.review-more');
    if (!text || !btn) return;
    card.classList.add('is-clamped');
    requestAnimationFrame(() => {
      if (text.scrollHeight - text.clientHeight > 4) {
        btn.hidden = false;
      } else {
        card.classList.remove('is-clamped');
      }
    });
    btn.addEventListener('click', () => {
      const expanded = card.classList.toggle('is-expanded');
      card.classList.toggle('is-clamped', !expanded);
      btn.setAttribute('aria-expanded', String(expanded));
    });
  });

  update();
})();
