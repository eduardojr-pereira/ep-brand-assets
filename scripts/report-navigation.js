/* Shared contextual navigation: locale-aware return and accurate active section. */
(function () {
  'use strict';
  const nav = document.querySelector('nav.ep-report-nav');
  const backLabels = {en: 'Back to Portfolio', 'pt-BR': 'Voltar ao portfólio'};

  function syncLabels() {
    const locale = document.documentElement.lang === 'pt-BR' ? 'pt-BR' : 'en';
    document.querySelectorAll('.ep-report-nav__back:not(.ep-footer__top)').forEach(link => {
      const value = backLabels[locale];
      link.dataset.replace = '← ' + value;
      link.setAttribute('aria-label', value);
      const span = link.querySelector('span');
      if (span) span.textContent = '← ' + value;
      // Existing report structure places the homepage three levels above the report.
      const target = new URL(link.getAttribute('href'), document.baseURI);
      if (target.pathname.endsWith('/index.html') && !target.hash) link.hash = '#projects';
    });
  }
  document.addEventListener('DOMContentLoaded', syncLabels);
  document.addEventListener('ep:languagechange', syncLabels);
  if (!nav) return;

  const links = [...nav.querySelectorAll('a[href^="#"]')];
  const entries = links.map(link => ({link, section: document.getElementById(link.hash.slice(1))}))
    .filter(entry => entry.section);
  if (!entries.length) return;

  // EP responsive report sections — canonical dropdown reuse.
  const layout = links[0].parentElement;
  layout.classList.add('ep-report-nav__section-layout');
  nav.dataset.i18nAria = 'reportSectionsAria';

  const dropdown = document.createElement('details');
  dropdown.className =
    'ep-header__dropdown ep-report-nav__sections';

  const summary = document.createElement('summary');

  const label = document.createElement('span');
  label.dataset.i18n = 'reportSections';
  label.textContent = 'Sections';

  const caret = document.createElement('span');
  caret.className = 'ep-header__caret';
  caret.setAttribute('aria-hidden', 'true');
  caret.textContent = '⌄';

  summary.append(label, caret);

  const panel = document.createElement('div');
  panel.className = 'ep-header__menu';

  dropdown.append(summary, panel);

  // Preserve a reference to the original position.
  const anchor = document.createComment('EP report sections');
  layout.insertBefore(anchor, links[0]);
  layout.insertBefore(dropdown, anchor);

  const mobile = window.matchMedia('(max-width: 670px)');

  function syncLayout() {
    dropdown.open = false;

    if (mobile.matches) {
      links.forEach(link => panel.append(link));
    } else {
      links.forEach(link => layout.insertBefore(link, anchor));
    }
  }

  mobile.addEventListener('change', syncLayout);
  syncLayout();

  let targetId = null;
  let unlockTimer = null;
  let pendingFrame = false;

  const gap = 28;
  function offset() { return nav.getBoundingClientRect().bottom + gap; }
  function select(id) {
    entries.forEach(({link, section}) => {
      const yes = section.id === id;
      link.classList.toggle('is-active', yes);
      if (yes) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  function detect() {
    const line = offset() + 12;
    let current = entries[0].section.id;
    for (const {section} of entries) {
      if (section.getBoundingClientRect().top <= line) current = section.id;
    }
    select(current);
  }
  function unlock() {
    if (unlockTimer !== null) clearTimeout(unlockTimer);
    unlockTimer = null;
    targetId = null;
    detect();
  }
  function requestDetect() {
    if (targetId || pendingFrame) return;
    pendingFrame = true;
    requestAnimationFrame(() => { pendingFrame = false; if (!targetId) detect(); });
  }
  entries.forEach(({link,section}) => link.addEventListener('click', event => {
    // Handle our report anchors in the capture phase so a legacy listener cannot
    // reapply the previous active item during smooth scrolling.
    event.preventDefault();
    event.stopImmediatePropagation();
    if (mobile.matches) {
      dropdown.open = false;
      summary.focus({preventScroll: true});
    }
    targetId = section.id;
    select(targetId);
    if (unlockTimer !== null) clearTimeout(unlockTimer);
    const top = section.getBoundingClientRect().top + window.scrollY - nav.offsetHeight - gap;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({top: Math.max(0, top), behavior: reduce ? 'instant' : 'smooth'});
    if (window.location.hash !== '#' + targetId) history.replaceState(null, '', '#' + targetId);
    unlockTimer = setTimeout(unlock, 2500);
  }, {capture: true}));
  // Scrollend can fire at intermediate positions. Keep clicked selection until
  // the target actually reaches the navigation offset.
  window.addEventListener('scrollend', () => {
    if (!targetId) return requestDetect();
    const target = document.getElementById(targetId);
    if (target && Math.abs(target.getBoundingClientRect().top - offset()) < 36) unlock();
  }, {passive:true});
  window.addEventListener('scroll', requestDetect, {passive:true});
  window.addEventListener('resize', requestDetect);
  window.addEventListener('wheel', unlock, {passive:true});
  window.addEventListener('touchstart', unlock, {passive:true});
  document.addEventListener('DOMContentLoaded', () => {
    if (window.location.hash) {
      const entry = entries.find(({section}) => '#' + section.id === window.location.hash);
      if (entry) select(entry.section.id);
      else detect();
    } else detect();
  });
})();
