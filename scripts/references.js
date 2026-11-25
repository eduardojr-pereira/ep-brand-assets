/* Shared references localization and clipboard feedback. */
(() => {
  'use strict';
  const section = document.querySelector('.ep-references');
  if (!section) return;
  const pt = () => document.documentElement.lang.toLowerCase().startsWith('pt');
  const timers = new WeakMap();
  section.querySelectorAll('[data-ep-tabs]').forEach((group, groupIndex) => {
    const list = group.querySelector('[data-ep-tablist]');
    const buttons = Array.from(list.querySelectorAll('[data-ep-tab]'));
    const panels = Array.from(group.querySelectorAll('[data-ep-tab-panel]'));
    const card = group.closest('article');
    const heading = card.querySelector('.ep-reference-card__heading');
    const title = heading.querySelector('h3');
    if (!buttons.length || buttons.length !== panels.length || !title) return;
    title.id ||= `ep-technical-references-${groupIndex + 1}`;
    list.setAttribute('role', 'tablist');
    list.setAttribute('aria-labelledby', title.id);
    list.style.setProperty('--ep-tab-count', buttons.length);

    // Move the existing controls alongside the heading; keep the no-JS fallback intact.
    const titleGroup = document.createElement('div');
    titleGroup.className = 'ep-reference-title-group';
    while (heading.firstChild) titleGroup.append(heading.firstChild);
    const controls = document.createElement('div');
    controls.className = 'ep-reference-tab-controls';
    controls.append(list);
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'ep-reference-loop-toggle';
    toggle.dataset.epLoopToggle = '';
    controls.append(toggle);
    heading.classList.add('ep-reference-card__heading--tabs');
    heading.append(titleGroup, controls);
    group.prepend(heading);

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    let current = 0, timer = null, paused = false;
    let hovering = false, focused = false, visible = !('IntersectionObserver' in window);
    function syncToggle() {
      const label = paused ? (pt() ? 'Retomar rotação automática' : 'Resume automatic rotation') :
        (pt() ? 'Pausar rotação automática' : 'Pause automatic rotation');
      toggle.textContent = paused ? '▶' : 'Ⅱ';
      toggle.setAttribute('aria-label', label);
      toggle.title = label;
      toggle.hidden = buttons.length < 2 || reduced.matches;
    }
    function schedule() {
      clearTimeout(timer);
      timer = null;
      if (buttons.length < 2 || paused || hovering || focused || !visible || document.hidden || reduced.matches) return;
      timer = setTimeout(() => {
        if (!paused && !hovering && !focused && visible && !document.hidden && !reduced.matches) activate((current + 1) % buttons.length);
      }, 5000);
    }
    function activate(index, focus = false) {
      current = index;
      buttons.forEach((button, i) => {
        button.setAttribute('aria-selected', String(i === index));
        button.tabIndex = i === index ? 0 : -1;
        panels[i].hidden = i !== index;
      });
      list.style.setProperty('--ep-tab-index', index);
      if (focus) buttons[index].focus();
      schedule();
    }
    buttons.forEach((button, i) => {
      button.setAttribute('role', 'tab');
      panels[i].setAttribute('role', 'tabpanel');
      panels[i].tabIndex = 0;
      button.addEventListener('click', () => activate(i));
      button.addEventListener('keydown', event => {
        let next;
        if (event.key === 'ArrowRight') next = (i + 1) % buttons.length;
        else if (event.key === 'ArrowLeft') next = (i + buttons.length - 1) % buttons.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = buttons.length - 1;
        else return;
        event.preventDefault(); activate(next, true);
      });
    });
    toggle.addEventListener('click', () => { paused = !paused; syncToggle(); schedule(); });
    card.addEventListener('pointerenter', event => { if (event.pointerType !== 'touch') { hovering = true; schedule(); } });
    card.addEventListener('pointerleave', () => { hovering = false; schedule(); });
    card.addEventListener('focusin', () => { focused = true; schedule(); });
    card.addEventListener('focusout', event => { focused = card.contains(event.relatedTarget); schedule(); });
    document.addEventListener('visibilitychange', schedule);
    document.addEventListener('ep:languagechange', syncToggle);
    new MutationObserver(syncToggle).observe(document.documentElement, {attributes:true, attributeFilter:['lang']});
    reduced.addEventListener('change', () => { syncToggle(); schedule(); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting;
        schedule();
      }).observe(card);
    }
    group.dataset.epReady = '';
    list.hidden = false;
    syncToggle();
    activate(0);
  });
  function updateButton(button) {
    const state = button.dataset.state;
    const label = state === 'copied' ? (pt() ? 'Copiado!' : 'Copied!') : (pt() ? 'Copiar' : 'Copy');
    button.querySelector('.ep-reference-copy__label').textContent = label;
    button.setAttribute('aria-label', label);
    const status = button.parentElement.querySelector('.ep-reference-copy__status');
    status.textContent = state === 'copied' ? (pt() ? 'Comando copiado.' : 'Command copied.') : state === 'error' ? (pt() ? 'Não foi possível copiar. Selecione o comando manualmente.' : 'Could not copy. Select the command manually.') : '';
  }
  function localize() {
    section.querySelectorAll('[data-ep-ref-en]').forEach(node => {
      node.textContent = pt() ? node.dataset.epRefPt : node.dataset.epRefEn;
    });
    section.querySelectorAll('[data-ep-copy]').forEach(updateButton);
  }
  async function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(text); return; } catch (_) { /* fallback */ }
    }
    const input = document.createElement('textarea');
    input.value = text;
    input.setAttribute('readonly', '');
    input.style.cssText = 'position:fixed;left:-9999px;top:0';
    const previous = document.activeElement;
    document.body.append(input);
    try {
      input.select();
      if (!document.execCommand('copy')) throw new Error('Clipboard unavailable');
    } finally { input.remove(); previous?.focus({preventScroll:true}); }
  }
  section.querySelectorAll('[data-ep-copy]').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      clearTimeout(timers.get(button));
      try {
        await copy(button.parentElement.querySelector('code').textContent);
        button.dataset.state = 'copied';
      } catch (_) { button.dataset.state = 'error'; }
      updateButton(button);
      timers.set(button, setTimeout(() => { delete button.dataset.state; updateButton(button); }, 2000));
    });
  });
  document.addEventListener('ep:languagechange', localize);

  // Also synchronize the initial persisted language.
  if (document.readyState !== 'complete') {
    document.addEventListener('DOMContentLoaded', localize, {
      once: true
    });
  }

  const localeObserver = new MutationObserver(localize);
  localeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['lang']
  });

  localize();
})();
