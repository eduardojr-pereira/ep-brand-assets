/*
 * Responsibility: Menu disclosure, filter selection and active section navigation.
 * Consumes global asset and i18n services; no preference ownership.
 */

(() => {
    'use strict';
    const dropdown = '[data-ui-dropdown]';
    const filter = '[data-ui-filter]';
    const option = '[data-ui-filter-value]';
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const closeTimers = new WeakMap();
    const checkHost = item => item.querySelector('[data-ui-check-player]');
    function initChecks() {
        for (const item of document.querySelectorAll(`${option}:has([data-ui-check])`)) {
            UI.assets.mount(checkHost(item), {id:'checkbox', colorToken:'--ui-color-accent',
                onReady: player => snapCheck(player,item.getAttribute('aria-pressed') === 'true')});
        }
    }
    function snapCheck(player, selected) {
        player.resetSegments(true);
        player.goToAndStop(selected ? 44 : 0, true);
    }
    function checkDuration() {
        const value = getComputedStyle(document.documentElement).getPropertyValue('--ui-duration-link').trim();
        return parseFloat(value) * (value.endsWith('ms') ? 1 : 1000) || 0;
    }
    function animateCheck(item, selected, animate) {
        const host = checkHost(item);
        const player = host && UI.assets.get(host);
        if (!player) return false;
        if (reduced.matches || !animate || !checkDuration() || !player.frameRate) {
            snapCheck(player, selected);
            return false;
        }
        const segment = selected ? [0, 44] : [85, 119];
        player.setSpeed((segment[1] - segment[0]) / player.frameRate / (checkDuration() / 1000));
        player.playSegments(segment, true);
        return true;
    }

    function select(group, value, notify = true) {
        const options = [...group.querySelectorAll(option)].filter(el => el.closest(filter) === group);
        const chosen = options.find(el => el.dataset.uiFilterValue === value);
        if (!chosen) return false;
        let animated = false;
        for (const item of options) {
            const selected = item === chosen;
            const changed = item.getAttribute('aria-pressed') !== String(selected);
            item.setAttribute('aria-pressed', String(selected));
            if (changed) animated = animateCheck(item, selected, notify) || animated;
        }
        group.dataset.uiValue = value;
        if (group.matches(dropdown)) {
            for (const part of group.querySelector('summary').querySelectorAll('[data-ui-label]'))
                UI.i18n.bindFrom(part, chosen.querySelector('[data-ui-label]'));
            group.dataset.uiFiltered = String(value !== (group.dataset.uiDefault || 'all'));
        }
        if (notify) group.dispatchEvent(new CustomEvent('ui:filterchange', {
            bubbles: true, detail: { name: group.dataset.uiFilter, value }
        }));
        return { animated };
    }
    function closeDisclosure(el, restore = false) {
        clearTimeout(closeTimers.get(el));
        el.open = false;
        if (restore) el.querySelector('summary').focus();
    }
    function init() {
        initChecks();
        reduced.addEventListener('change', () => { for (const item of document.querySelectorAll(`${option}:has([data-ui-check])`)) animateCheck(item,item.getAttribute('aria-pressed') === 'true',false); });
        for (const group of document.querySelectorAll(filter)) {
            const selected = [...group.querySelectorAll(option)].find(el => el.getAttribute('aria-pressed') === 'true');
            if (selected) select(group, selected.dataset.uiFilterValue, false);
        }
        document.addEventListener('toggle', event => {
            const el = event.target;
            if (!(el instanceof HTMLDetailsElement) || !el.matches(dropdown)) return;
            if (!el.open) { clearTimeout(closeTimers.get(el)); return; }
            for (const other of document.querySelectorAll(`${dropdown}[open]`)) {
                if (other !== el && !other.contains(el) && !el.contains(other)) closeDisclosure(other);
            }
        }, true);
        document.addEventListener('click', event => {
            const target = event.target.closest('a, button, summary');
            for (const el of document.querySelectorAll(`${dropdown}[open]`)) {
                if (!el.contains(event.target)) closeDisclosure(el);
            }
            if (!target) return;
            const group = target.closest(filter);
            if (group && target.matches(option)) {
                const result = select(group, target.dataset.uiFilterValue);
                if (group.matches(dropdown)) {
                    clearTimeout(closeTimers.get(group));
                    if (result?.animated) {
                        closeTimers.set(group, setTimeout(() => closeDisclosure(group, true), checkDuration() + 10));
                    } else closeDisclosure(group, true);
                }
            } else if (target.matches('a') && target.closest(dropdown)) {
                closeDisclosure(target.closest(dropdown));
            }
        });
        document.addEventListener('keydown', event => {
            if (event.key !== 'Escape') return;
            const el = event.target.closest(`${dropdown}[open]`);
            if (el) { event.preventDefault(); closeDisclosure(el, true); }
        });
        const groups = [...document.querySelectorAll('[data-ui-scroll-nav]')].map(root => {
            const items = [...root.querySelectorAll('a[href^="#"]')].flatMap(link => {
                let section;
                try { section = document.getElementById(decodeURIComponent(link.hash.slice(1))); }
                catch { return []; }
                return section ? [{ link, section }] : [];
            });
            return { root, items };
        }).filter(group => group.items.length);
        if (!groups.length) return;
        let frame = 0, locked = null, timer = 0;
        function activate(group, item) {
            for (const entry of group.items) {
                if (entry === item) {
                    entry.link.setAttribute('aria-current', 'location');
                    entry.link.removeAttribute('data-ui-departed');
                } else {
                    if (entry.link.hasAttribute('aria-current') && entry.link.matches(':hover')) {
                        entry.link.setAttribute('data-ui-departed', '');
                    }
                    entry.link.removeAttribute('aria-current');
                }
            }
        }
        function update() {
            frame = 0;
            const bottom = Math.ceil(window.scrollY + window.innerHeight) >= document.documentElement.scrollHeight - 2;
            for (const group of groups) {
                if (locked) {
                    const match = group.items.find(entry => entry.section === locked);
                    if (match) { activate(group, match); continue; }
                }
                const offset = parseFloat(getComputedStyle(group.items[0].section).scrollMarginTop) || 0;
                const sorted = [...group.items].sort((a, b) => a.section.getBoundingClientRect().top - b.section.getBoundingClientRect().top);
                const item = bottom && document.documentElement.scrollHeight > innerHeight ? sorted.at(-1) :
                    sorted.filter(entry => entry.section.getBoundingClientRect().top <= offset + 2).at(-1) || sorted[0];
                activate(group, item);
            }
        }
        const schedule = () => { if (!frame) frame = requestAnimationFrame(update); };
        const unlock = () => { locked = null; clearTimeout(timer); schedule(); };
        for (const group of groups) for (const item of group.items) {
            item.link.addEventListener('pointerleave', () => item.link.removeAttribute('data-ui-departed'));
            item.link.addEventListener('click', event => {
                if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
                locked = item.section;
                for (const g of groups) {
                    const match = g.items.find(entry => entry.section === locked);
                    if (match) activate(g, match);
                }
                clearTimeout(timer);
                timer = setTimeout(unlock, 1200);
            });
        }
        window.addEventListener('scroll', schedule, { passive: true });
        window.addEventListener('resize', schedule);
        window.addEventListener('scrollend', unlock);
        window.addEventListener('wheel', unlock, { passive: true });
        window.addEventListener('touchstart', unlock, { passive: true });
        window.addEventListener('keydown', event => {
            if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' '].includes(event.key)) unlock();
        });
        window.addEventListener('hashchange', schedule);
        update();
    }
    window.UI ??= {};
    window.UI.navigation = Object.freeze({ select });
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
    else init();
})();
