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

// Default to English on first visit; remember the visitor's choice after that
(function initLang() {
  let saved = null;
  try { saved = localStorage.getItem('ibbridge-lang'); } catch (e) {}
  setLang(saved || 'en');
})();

// ===== Current year in footer =====
document.getElementById('year').textContent = new Date().getFullYear();

// ===== Reviews: animate the 100% ring when it scrolls into view =====
(function initRing() {
  const score = document.querySelector('.reviews-score');
  if (!score) return;
  if (!('IntersectionObserver' in window)) { score.classList.add('animate'); return; }
  const obs = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { score.classList.add('animate'); obs.disconnect(); }
    });
  }, { threshold: 0.4 });
  obs.observe(score);
})();

// ===== Reviews carousel (native scroll + snap, finite paged) =====
(function initReviews() {
  const track = document.getElementById('reviews-track');
  if (!track) return;
  const cards = Array.from(track.querySelectorAll('.review-card'));
  const prev = document.getElementById('rev-prev');
  const next = document.getElementById('rev-next');
  const dotsWrap = document.getElementById('rev-dots');
  const n = cards.length;
  if (n === 0) return;

  // --- Read more / Show less, with paragraph breaks collapsed while clamped ---
  // When collapsed we render the active-language text with <br> paragraph breaks
  // turned into single spaces, so the line-clamp ellipsis always lands on real
  // text (no lone "…" sitting on a blank line). When expanded we restore the
  // full text WITH its paragraph breaks. setLang() rewrites innerHTML from the
  // data-en/data-es attributes, so a MutationObserver re-applies this whenever
  // the language changes.
  function applyText(card) {
    const text = card.querySelector('.review-text');
    if (!text) return;
    const lang = document.documentElement.lang || 'en';
    const full = text.getAttribute('data-' + lang);
    if (full == null) return;
    const expanded = card.classList.contains('is-expanded');
    const want = expanded ? full : full.replace(/(\s*<br\s*\/?>\s*)+/gi, ' ');
    if (text.innerHTML !== want) {
      text._applying = true;
      text.innerHTML = want;
      text._applying = false;
    }
  }

  function setupReadMore(card) {
    const text = card.querySelector('.review-text');
    const btn = card.querySelector('.review-more');
    if (!text || !btn) return;
    card.classList.add('is-clamped');
    applyText(card);

    function refreshButton() {
      if (card.classList.contains('is-expanded')) { btn.hidden = false; return; }
      btn.hidden = (text.scrollHeight - text.clientHeight <= 4);
      if (btn.hidden) card.classList.remove('is-clamped');
      else card.classList.add('is-clamped');
    }
    requestAnimationFrame(refreshButton);

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const expanded = card.classList.toggle('is-expanded');
      card.classList.toggle('is-clamped', !expanded);
      btn.setAttribute('aria-expanded', String(expanded));
      applyText(card);
    });

    // Re-apply collapse/expand rendering after a language switch (setLang
    // rewrites innerHTML from data-en/data-es). Ignore our own writes.
    const obs = new MutationObserver(() => {
      if (text._applying) return;
      applyText(card);
      requestAnimationFrame(refreshButton);
    });
    obs.observe(text, { childList: true, characterData: true, subtree: true });
  }
  cards.forEach(setupReadMore);

  // --- Paged carousel geometry ---
  function gap() {
    return parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap || '20') || 20;
  }
  function perPage() {
    const w = window.innerWidth;
    if (w <= 560) return 1;
    if (w <= 920) return 2;
    return 3;
  }
  function pageCount() { return Math.max(1, Math.ceil(n / perPage())); }

  let stepPx = 1;
  function measure() { stepPx = cards[0].getBoundingClientRect().width + gap(); }

  // First card index shown on a given page.
  function firstCardOfPage(p) { return Math.min(p * perPage(), n - 1); }
  function pageScrollLeft(p) { return firstCardOfPage(p) * stepPx; }

  function currentPage() {
    const i = Math.round(track.scrollLeft / stepPx);
    return Math.min(pageCount() - 1, Math.floor(i / perPage() + 0.001));
  }

  // --- Dots: one per page ---
  let dots = [];
  function buildDots() {
    dotsWrap.innerHTML = '';
    const pages = pageCount();
    dots = [];
    for (let p = 0; p < pages; p++) {
      const b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-label', 'Go to page ' + (p + 1));
      b.addEventListener('click', () => goToPage(p, true));
      dotsWrap.appendChild(b);
      dots.push(b);
    }
  }

  function syncUI() {
    const p = currentPage();
    const last = pageCount() - 1;
    dots.forEach((d, i) => {
      const on = i === p;
      d.classList.toggle('active', on);
      d.setAttribute('aria-selected', String(on));
    });
    if (prev) prev.disabled = (p <= 0);
    if (next) next.disabled = (p >= last);
  }

  function goToPage(p, smooth) {
    const clamped = Math.max(0, Math.min(pageCount() - 1, p));
    track.scrollTo({ left: pageScrollLeft(clamped), behavior: smooth ? 'smooth' : 'auto' });
    syncUI();
  }

  if (next) next.addEventListener('click', () => goToPage(currentPage() + 1, true));
  if (prev) prev.addEventListener('click', () => goToPage(currentPage() - 1, true));

  let rafPending = false;
  track.addEventListener('scroll', () => {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(() => { syncUI(); rafPending = false; });
  }, { passive: true });

  let lastPerPage = perPage();
  window.addEventListener('resize', () => {
    const p = currentPage();
    const pp = perPage();
    measure();
    if (pp !== lastPerPage) { lastPerPage = pp; buildDots(); }
    goToPage(Math.min(p, pageCount() - 1), false);
  });

  requestAnimationFrame(() => {
    measure();
    buildDots();
    goToPage(0, false);
    syncUI();
  });
})();
