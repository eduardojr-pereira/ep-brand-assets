/* EP navigation: disclosure, single-choice filters and section state. */
(() => {
    'use strict';
    const dropdown = '[data-ep-dropdown]';
    const filter = '[data-ep-filter]';
    const option = '[data-ep-filter-value]';
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const closeTimers = new WeakMap();
    const checks = new Map();
    let checkRuntime = null;
    function refreshChecks() {
        if (!checkRuntime) return;
        const raw = getComputedStyle(document.documentElement).getPropertyValue('--ep-color-accent').trim();
        if (!/^#[0-9a-f]{6}$/i.test(raw)) return;
        const color = [1, 3, 5].map(i => parseInt(raw.slice(i, i + 2), 16) / 255).concat(1);
        for (const item of document.querySelectorAll(`${option}:has([data-ep-check])`)) {
            const node = item.querySelector('[data-ep-check]');
            const host = node.querySelector('[data-ep-check-player]');
            checks.get(item)?.destroy();
            node.removeAttribute('data-ep-lottie-ready');
            host.replaceChildren();
            const data = JSON.parse(JSON.stringify(checkRuntime.source));
            function recolor(value) {
                if (!value || typeof value !== 'object') return;
                if ((value.ty === 'st' || value.ty === 'fl') && value.c?.a === 0) value.c.k = color;
                for (const child of Object.values(value)) recolor(child);
            }
            recolor(data);
            const player = checkRuntime.lottie.loadAnimation({ container: host, renderer: 'svg', loop: false, autoplay: false, animationData: data });
            checks.set(item, player);
            player.addEventListener('DOMLoaded', () => {
                if (checks.get(item) !== player) return;
                player.goToAndStop(item.getAttribute('aria-pressed') === 'true' ? 44 : 0, true);
                node.setAttribute('data-ep-lottie-ready', '');
            });
        }
    }
    function connectChecks(lottie, source) {
        if (!lottie || typeof lottie.loadAnimation !== 'function' || !source) return false;
        checkRuntime = { lottie, source };
        refreshChecks();
        return true;
    }
    function checkDuration() {
        const value = getComputedStyle(document.documentElement).getPropertyValue('--ep-duration-link').trim();
        return parseFloat(value) * (value.endsWith('ms') ? 1 : 1000) || 0;
    }
    function animateCheck(item, selected, animate) {
        const player = checks.get(item);
        if (!player || !item.querySelector('[data-ep-lottie-ready]')) return false;
        if (reduced.matches || !animate || !checkDuration()) {
            player.goToAndStop(selected ? 44 : 0, true);
            return false;
        }
        const segment = selected ? [0, 44] : [85, 119];
        player.setSpeed((segment[1] - segment[0]) / 48 / (checkDuration() / 1000));
        player.playSegments(segment, true);
        return true;
    }

    const setLabel = (element, label) => {
        for (const part of element.querySelectorAll('[data-ep-label]')) part.textContent = label;
    };
    function select(group, value, notify = true) {
        const options = [...group.querySelectorAll(option)].filter(el => el.closest(filter) === group);
        const chosen = options.find(el => el.dataset.epFilterValue === value);
        if (!chosen) return false;
        let animated = false;
        for (const item of options) {
            const selected = item === chosen;
            const changed = item.getAttribute('aria-pressed') !== String(selected);
            item.setAttribute('aria-pressed', String(selected));
            if (changed) animated = animateCheck(item, selected, notify) || animated;
        }
        group.dataset.epValue = value;
        if (group.matches(dropdown)) {
            setLabel(group.querySelector('summary'), chosen.querySelector('[data-ep-label]').textContent);
            group.dataset.epFiltered = String(value !== (group.dataset.epDefault || 'all'));
        }
        if (notify) group.dispatchEvent(new CustomEvent('ep:filterchange', {
            bubbles: true, detail: { name: group.dataset.epFilter, value }
        }));
        return { animated };
    }
    function closeDisclosure(el, restore = false) {
        clearTimeout(closeTimers.get(el));
        el.open = false;
        if (restore) el.querySelector('summary').focus();
    }
    function init() {
        document.addEventListener('ep:themechange', refreshChecks);
        reduced.addEventListener('change', refreshChecks);
        if (checkRuntime) refreshChecks();
        for (const group of document.querySelectorAll(filter)) {
            const selected = [...group.querySelectorAll(option)].find(el => el.getAttribute('aria-pressed') === 'true');
            if (selected) select(group, selected.dataset.epFilterValue, false);
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
                const result = select(group, target.dataset.epFilterValue);
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
        const groups = [...document.querySelectorAll('[data-ep-scroll-nav]')].map(root => {
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
                    entry.link.removeAttribute('data-ep-departed');
                } else {
                    if (entry.link.hasAttribute('aria-current') && entry.link.matches(':hover')) {
                        entry.link.setAttribute('data-ep-departed', '');
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
            item.link.addEventListener('pointerleave', () => item.link.removeAttribute('data-ep-departed'));
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
    window.EPNavigation = Object.freeze({ setLabel, select, connectChecks });
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
    else init();
})();
