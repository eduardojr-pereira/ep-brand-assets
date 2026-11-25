/* EP Brand shared Footer: links, theme-aware social Lotties, and back-to-top. */
(() => {
  'use strict';
  const footer = document.querySelector('.ep-footer');
  if (!footer) return;
  const script = document.currentScript;
  if (!script || !script.src) return;
  const scriptUrl = new URL(script.src);
  const homepage = new URL('../../index.html', scriptUrl);
  const targets = {
    home: homepage.href,
    selected: new URL('?collection=selected_projects#projects', homepage).href,
    labs: new URL('?collection=learning_labs#projects', homepage).href
  };
  footer.querySelectorAll('[data-ep-footer-route]').forEach(link => {
    const url = targets[link.dataset.epFooterRoute];
    if (url) link.href = url;
  });
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  footer.querySelector('.ep-footer__top')?.addEventListener('click', event => {
    event.preventDefault();
    window.scrollTo({top: 0, behavior: reduceMotion.matches ? 'instant' : 'smooth'});
  });
  const nodes = [...footer.querySelectorAll('[data-ep-footer-lottie]')];
  if (!nodes.length) return;
  const colors = ['graphite', 'white', 'copper'];
  const baseColor = () => document.documentElement.getAttribute('data-theme') === 'light' ? 'graphite' : 'white';
  const entries = nodes.map(node => ({node, fallback: node.textContent, slots: {}, hovered: false, focused: false, active: null, playing: false}));
  const setLoop = (animation, enabled) => {
    if (typeof animation.setLoop === 'function') animation.setLoop(enabled);
    else animation.loop = enabled;
  };
  const stop = slot => {
    if (!slot?.ready) return;
    setLoop(slot.animation, false);
    slot.animation.goToAndStop(Math.max(0, slot.animation.totalFrames - 1), true);
  };
  function update(entry) {
    const engaged = entry.hovered || entry.focused;
    const base = entry.slots[baseColor()];
    const copper = entry.slots.copper;
    const next = engaged && copper?.ready ? copper : base?.ready ? base : null;
    const play = !!next && next === copper && engaged && !reduceMotion.matches;
    if (entry.active !== next || entry.playing !== play) {
      if (entry.active && entry.active !== next) stop(entry.active);
      if (next) {
        if (play) {
          setLoop(next.animation, true);
          next.animation.goToAndPlay(0, true);
        } else stop(next);
      }
      entry.active = next;
      entry.playing = play;
    }
    for (const slot of Object.values(entry.slots)) {
      slot.holder.style.visibility = slot === next ? 'visible' : 'hidden';
    }
    if (entry.fallbackNode) {
      entry.fallbackNode.style.visibility = next ? 'hidden' : 'visible';
      entry.fallbackNode.style.color = engaged ? 'var(--ep-color-accent)' : 'var(--ep-color-text)';
    }
  }
  function initialize(entry) {
    if (entry.fallbackNode) return;
    const fallback = document.createElement('span');
    fallback.textContent = entry.fallback;
    fallback.style.gridArea = '1 / 1';
    entry.fallbackNode = fallback;
    entry.node.replaceChildren(fallback);
    for (const color of colors) {
      const holder = document.createElement('span');
      holder.style.cssText = 'display:block;width:100%;height:100%;grid-area:1 / 1;visibility:hidden;pointer-events:none';
      entry.node.appendChild(holder);
      const slot = {holder, animation: null, ready: false};
      entry.slots[color] = slot;
      const file = `lottie_${entry.node.dataset.epFooterLottie}_${color}.json`;
      const path = new URL('../animations/' + file, scriptUrl).href;
      try {
        const anim = window.lottie.loadAnimation({container: holder, renderer: 'svg', loop: false, autoplay: false, path});
        slot.animation = anim;
        anim.addEventListener('DOMLoaded', () => {
          slot.ready = true;
          stop(slot);
          update(entry);
        });
        anim.addEventListener('data_failed', () => {
          slot.ready = false;
          update(entry);
        });
      } catch (_) { slot.ready = false; }
    }
    update(entry);
  }
  function draw() {
    if (!window.lottie) return;
    for (const entry of entries) {
      initialize(entry);
      update(entry);
    }
  }
  for (const entry of entries) {
    const surface = entry.node.closest('.ep-footer__icon');
    surface?.addEventListener('pointerenter', event => {
      if (event.pointerType === 'touch') return;
      entry.hovered = true;
      update(entry);
    });
    const leave = () => { entry.hovered = false; update(entry); };
    surface?.addEventListener('pointerleave', leave);
    surface?.addEventListener('pointercancel', leave);
    surface?.addEventListener('focusin', () => {
      entry.focused = surface.matches(':focus-visible');
      update(entry);
    });
    surface?.addEventListener('focusout', () => { entry.focused = false; update(entry); });
  }
  new MutationObserver(draw).observe(document.documentElement, {attributes:true,attributeFilter:['data-theme']});
  document.addEventListener('ep:themechange',draw);
  reduceMotion.addEventListener('change',draw);
  if (window.lottie) {draw();return;}
  // External player is optional: text fallbacks remain usable offline.
  const player = document.createElement('script');
  player.src = 'https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js';
  player.async = true;
  player.addEventListener('load',draw);
  document.head.appendChild(player);
})();
