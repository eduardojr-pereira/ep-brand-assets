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
  const entries = nodes.map(node => ({node, fallback: node.textContent, animation: null}));
  let currentVariant = '';
  const variant = () => document.documentElement.getAttribute('data-theme') === 'light' ? 'graphite' : 'copper';
  function draw() {
    if (!window.lottie) return;
    const color = variant();
    if (currentVariant === color) return;
    currentVariant = color;
    for (const entry of entries) {
      entry.animation?.destroy();
      entry.node.textContent = entry.fallback;
      const holder = document.createElement('span');
      holder.style.cssText = 'display:block;width:100%;height:100%';
      entry.node.replaceChildren(holder);
      const file = `lottie_${entry.node.dataset.epFooterLottie}_${color}.json`;
      const path = new URL('../animations/' + file, scriptUrl).href;
      try {
        const anim = window.lottie.loadAnimation({container: holder, renderer: 'svg', loop: false, autoplay: false, path});
        entry.animation = anim;
        anim.addEventListener('DOMLoaded', () => anim.goToAndStop(Math.max(0, anim.totalFrames - 1), true));
        anim.addEventListener('data_failed', () => { entry.node.textContent = entry.fallback; });
      } catch (_) { entry.node.textContent = entry.fallback; }
    }
  }
  for (const entry of entries) {
    const surface = entry.node.closest('.ep-footer__icon');
    const play = () => { if (!reduceMotion.matches && entry.animation) {entry.animation.setLoop(false);entry.animation.goToAndPlay(0, true);} };
    const stop = () => { if (entry.animation) entry.animation.goToAndStop(Math.max(0,entry.animation.totalFrames-1),true); };
    surface?.addEventListener('pointerenter',play);
    surface?.addEventListener('pointerleave',stop);
    surface?.addEventListener('focusin',play);
    surface?.addEventListener('focusout',stop);
  }
  new MutationObserver(draw).observe(document.documentElement, {attributes:true,attributeFilter:['data-theme']});
  document.addEventListener('ep:themechange',draw);
  if (window.lottie) {draw();return;}
  // External player is optional: text fallbacks remain usable offline.
  const player = document.createElement('script');
  player.src = 'https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js';
  player.async = true;
  player.addEventListener('load',draw);
  document.head.appendChild(player);
})();
