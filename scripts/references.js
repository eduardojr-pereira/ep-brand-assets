/* Shared references localization and clipboard feedback. */
(() => {
  'use strict';
  const section = document.querySelector('.ep-references');
  if (!section) return;
  const pt = () => document.documentElement.lang.toLowerCase().startsWith('pt');
  const timers = new WeakMap();
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
