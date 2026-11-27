/*
 * Responsibility: Resolve, persist and apply the single global theme preference; initialize synchronously in the head before rendering.
 * Boundaries: No component styling or asset logic.
 */
(() => {
    'use strict';
    window.UI ??= {};
    const root = document.documentElement;
    const key = 'ui.theme';
    const media = matchMedia('(prefers-color-scheme: dark)');
    const valid = value => ['dark', 'light'].includes(value);
    const stored = () => { try { return localStorage.getItem(key); } catch { return null; } };
    const initial = stored();
    let explicit = valid(initial) ? initial : null;
    let current;
    function apply(value) {
        if (current === value) return;
        current = value;
        root.dataset.theme = value;
        document.dispatchEvent(new CustomEvent('ui:themechange', {detail: {theme: current}}));
    }
    function set(value) {
        if (!valid(value)) throw new RangeError('Unsupported theme');
        explicit = value;
        try { localStorage.setItem(key, value); } catch {}
        apply(value);
    }
    media.addEventListener('change', () => { if (!explicit) apply(media.matches ? 'dark' : 'light'); });
    window.addEventListener('storage', event => {
        if (event.key !== key && event.key !== null) return;
        const value = stored();
        explicit = valid(value) ? value : null;
        apply(explicit || (media.matches ? 'dark' : 'light'));
    });
    window.UI.theme = Object.freeze({current: () => current, set});
    apply(explicit || (media.matches ? 'dark' : 'light'));
})();
