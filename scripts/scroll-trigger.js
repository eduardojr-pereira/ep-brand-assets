/*
 * Responsibility: Manage scroll/load animation triggers, interruption and explicit replay; initialize synchronously in the head.
 * Boundaries: No translation or theme preference ownership.
 */

(() => {
    'use strict';
    const root = document.documentElement;
    const selector = '[data-motion]:is([data-scroll-trigger="load"], [data-scroll-trigger="once"], [data-scroll-trigger="repeat"])';
    const state = 'data-ui-motion-state';
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    let observer = null;
    let active = false;

    function reveal(element, animate = true) {
        if (element.hasAttribute(state)) return;
        element.setAttribute(state, animate && active ? 'entering' : 'visible');
        if (element.dataset.scrollTrigger === 'once') observer?.unobserve(element);
    }

    function showImmediately(element) {
        element.setAttribute(state, 'visible');
        if (element.dataset.scrollTrigger === 'once') observer?.unobserve(element);
    }

    function stop() {
        active = false;
        observer?.disconnect();
        root.removeAttribute('data-ui-motion');
        document.querySelectorAll(selector).forEach(showImmediately);
    }

    function initialize(resuming = false) {
        if (!active) return;
        const entered = new WeakSet();
        try {
            observer = new IntersectionObserver(entries => {
                for (const entry of entries) {
                    const element = entry.target;
                    if (entry.isIntersecting) {
                        entered.add(element);
                        reveal(element);
                    } else if ((!resuming || entered.has(element)) && element.dataset.scrollTrigger === 'repeat' &&
                               !element.matches(':focus-within, :target')) {
                        // Rearm only when completely outside the viewport.
                        const box = element.getBoundingClientRect();
                        if (box.bottom <= 0 || box.top >= window.innerHeight ||
                            box.right <= 0 || box.left >= window.innerWidth) {
                            element.removeAttribute(state);
                        }
                    }
                }
            }, { threshold: 0 });
            for (const element of document.querySelectorAll(selector)) {
                if (element.matches(':focus-within, :target')) {
                    showImmediately(element);
                } else if (element.dataset.scrollTrigger === 'load') {
                    reveal(element);
                } else if (!(resuming && element.dataset.scrollTrigger === 'once' && element.hasAttribute(state))) {
                    observer.observe(element);
                }
            }
        } catch (error) {
            stop();
            console.error('UI motion initialization failed:', error);
        }
    }

    // A single synchronous bootstrap prevents a visible-to-hidden flash.
    // If loaded late or unsupported, leave content visible instead.
    active = !reduced.matches && 'IntersectionObserver' in window &&
        document.readyState === 'loading' && !document.body;
    if (active) root.setAttribute('data-ui-motion', 'active');

    document.addEventListener('DOMContentLoaded', () => initialize(), { once: true });
    document.addEventListener('animationend', event => {
        if (event.animationName === 'ui-motion-enter' && event.target.matches(selector)) {
            event.target.setAttribute(state, 'visible');
        }
    });
    document.addEventListener('focusin', event => {
        let target = event.target.closest(selector);
        while (target) {
            showImmediately(target);
            target = target.parentElement?.closest(selector);
        }
    });
    reduced.addEventListener('change', event => {
        if (event.matches) { stop(); return; }
        if (!('IntersectionObserver' in window) || document.readyState === 'loading') return;
        // Restore explicit replay and repeat-on-reentry, never hide previously visible content.
        document.querySelectorAll(selector).forEach(showImmediately);
        active = true;
        root.setAttribute('data-ui-motion', 'active');
        initialize(true);
    });

    // For an explicit replay (e.g. after the locale controller swaps content).
    // The caller owns any fade-out and must perform the text change first.
    window.UI ??= {};
    window.UI.motion = Object.freeze({
        replay(scope) {
            if (!active || reduced.matches) return;
            const targets = Array.from(scope.querySelectorAll('[data-motion][data-scroll-trigger="load"]'));
            if (scope.matches?.('[data-motion][data-scroll-trigger="load"]')) targets.unshift(scope);
            for (const element of targets) element.removeAttribute(state);
            // Force the reset once for the group, not once per element.
            void root.offsetWidth;
            targets.forEach(element => reveal(element));
        }
    });
})();
