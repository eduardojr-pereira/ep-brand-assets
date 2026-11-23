/* EP phase 02: opt-in Lottie behavior; no changes to existing site. */
(() => {
  'use strict';
  const registry = new Map();
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const theme = () => document.documentElement.dataset.theme === 'light' ? 'light' : 'dark';
  const base = '../assets/animations/';
  const variant = (name, color) => `${base}lottie_${name}_${color}.json`;
  function fallback(node) {
    node.textContent = node.dataset.fallback || '◆';
    node.classList.add('ep-lottie-fallback');
  }
  function init(node) {
    if (!window.lottie) { fallback(node); return; }
    const name = node.dataset.lottie;
    if (!name) return;
    const mode = name === 'knowledge' ? 'hover' : (node.dataset.mode || 'hover');
    const root = node.closest('[data-lottie-control]') || node;
    const canvas = document.createElement('span');
    canvas.className = 'ep-lottie-canvas';
    node.replaceChildren(canvas);
    const obj = {node, root, canvas, name, mode, animation:null, hovered:false, token:0};
    registry.set(node, obj);
    const onHover = () => {
      obj.hovered=true;
      render(obj);
    };
    const onLeave = () => {
      obj.hovered=false;
      render(obj);
    };
    if (mode !== 'once') {
      root.addEventListener('pointerenter', onHover);
      root.addEventListener('pointerleave', onLeave);
      root.addEventListener('focusin', onHover);
      root.addEventListener('focusout', e => {
        if (!root.contains(e.relatedTarget)) onLeave();
      });
    }
    if (mode === 'once') {
      const observer = new IntersectionObserver(entries => {
        if (!entries[0].isIntersecting) return;
        observer.disconnect();
        if (!reduced.matches && obj.animation) {
          obj.animation.setLoop(false);
          obj.animation.goToAndPlay(0, true);
        }
      }, {threshold:0.35});
      obj.observer = observer;
      observer.observe(node);
    }
    render(obj, true);
  }
  function render(obj, force=false) {
    if (!window.lottie) return;
    const color = !obj.hovered ? (obj.name === 'knowledge' && theme() === 'light' ? 'copper_light' : 'copper') : theme() === 'light' ? 'graphite' : 'white';
    const path = obj.mode === 'once' || obj.mode === 'reverse' ? `${base}lottie_${obj.name}.json` : variant(obj.name, color);
    if (obj.path === path && obj.animation && !force) { applyState(obj); return; }
    obj.path = path;
    if (obj.animation) obj.animation.destroy();
    obj.canvas.replaceChildren();
    const token = ++obj.token;
    const anim = window.lottie.loadAnimation({container:obj.canvas,renderer:'svg',loop:false,autoplay:false,path});
    obj.animation = anim;
    anim.addEventListener('DOMLoaded', () => { if (obj.token === token) applyState(obj); });
    anim.addEventListener('data_failed', () => {
      if (obj.token === token) fallback(obj.node);
    });
  }
  function applyState(obj) {
    const anim = obj.animation;
    if (!anim || !anim.totalFrames) return;
    const last = Math.max(0,Math.floor(anim.totalFrames)-1);
    anim.stop();
    if (reduced.matches) { anim.goToAndStop(last,true); return; }
    if (obj.mode === 'reverse') {
      // Knowledge: visible at rest, reverse-loop from last to first only while hovering.
      if (obj.hovered) {
        anim.setLoop(true);
        anim.setDirection(-1);
        anim.goToAndPlay(last,true);
      } else {
        anim.setLoop(false);
        anim.goToAndStop(last,true);
      }
    } else if (obj.mode === 'once') {
      anim.setLoop(false);
      anim.goToAndStop(last,true);
    } else if (obj.hovered) {
      anim.setLoop(true);
      anim.setDirection(1);
      anim.goToAndPlay(0,true);
    } else {
      anim.setLoop(false);
      anim.goToAndStop(last,true);
    }
  }
  function refresh() {registry.forEach(o=>render(o));}
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-lottie]').forEach(init);
    document.addEventListener('ep:themechange',refresh);
    reduced.addEventListener?.('change',refresh);
  });
})();
