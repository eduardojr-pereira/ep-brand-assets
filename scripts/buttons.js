/*
 * Responsibility: Orbit magnetism, motion pause and transport-independent send state.
 * No network submission or language preference; temporary label adapters are replaced in Lot 6.
 */

(() => {
    'use strict';
    const reduce = matchMedia('(prefers-reduced-motion: reduce)');
    const fine = matchMedia('(hover: hover) and (pointer: fine)');
    const orbits = new Map();
    const reset = node => {
        node.style.removeProperty('--ui-magnet-x');
        node.style.removeProperty('--ui-magnet-y');
    };
    const clamp = value => Math.max(-12, Math.min(12, value));
    function pause(node) {
        node.toggleAttribute('data-ui-orbit-paused', document.hidden || !orbits.get(node));
    }
    function init() {
        const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => {
            entries.forEach(({target, isIntersecting}) => {
                orbits.set(target, isIntersecting);
                pause(target);
                if (!isIntersecting) reset(target);
            });
        }) : null;
        document.querySelectorAll('[data-ui-orbit]').forEach(node => {
            orbits.set(node, !observer);
            pause(node);
            observer?.observe(node);
            node.addEventListener('pointermove', event => {
                if (event.pointerType !== 'mouse' || !fine.matches || reduce.matches) return;
                const r = node.getBoundingClientRect();
                node.style.setProperty('--ui-magnet-x', `${clamp((event.clientX - r.left - r.width / 2) * .3)}px`);
                node.style.setProperty('--ui-magnet-y', `${clamp((event.clientY - r.top - r.height / 2) * .3)}px`);
            });
            ['pointerleave', 'pointercancel', 'blur'].forEach(name => node.addEventListener(name, () => reset(node)));
        });
        [fine, reduce].forEach(query => query.addEventListener('change', () => orbits.forEach((_, node) => reset(node))));
        document.addEventListener('visibilitychange', () => orbits.forEach((_, node) => { pause(node); if (document.hidden) reset(node); }));
    }
    function setOrbitLabel(node, label, ringLabel) {
        node.setAttribute('aria-label', label);
        node.querySelector('[data-ui-ring-label]').textContent = `${ringLabel} · ${ringLabel} · `;
    }
    function setSendState(node, state, options = {}) {
        if (!['idle', 'pending', 'success', 'error'].includes(state)) throw new RangeError('Invalid send state');
        if (state === 'success' && options.confirmed !== true) throw new Error('Confirmed transport response required');
        const button = node.querySelector('button');
        node.dataset.state = state;
        button.disabled = state === 'pending' || state === 'success';
        button.setAttribute('aria-busy', String(state === 'pending'));
        updateFeedback(node);
    }
    function updateFeedback(node) {
        const state = node.dataset.state;
        const copy = ['success', 'error'].includes(state) ? node.querySelector(`[data-ui-send-copy="${state}"]`).textContent : '';
        node.querySelector('[role="status"]').textContent = copy;
    }
    function setSendLabels(node, labels) {
        for (const state of ['idle', 'pending', 'success']) {
            if (typeof labels[state] === 'string') node.querySelector(`[data-ui-send-label="${state}"]`).textContent = labels[state];
        }
        for (const state of ['success', 'error']) {
            const text = labels[`${state}Feedback`];
            if (typeof text === 'string') node.querySelector(`[data-ui-send-copy="${state}"]`).textContent = text;
        }
        updateFeedback(node);
    }
    window.UI ??= {};
    window.UI.actions = Object.freeze({setOrbitLabel, setSendState, setSendLabels});
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
    else init();
})();
