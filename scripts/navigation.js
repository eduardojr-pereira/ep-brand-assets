/*
 * Responsibility: Manage menu disclosure, filter selection and active section navigation.
 * Boundaries: Consume global asset and i18n services; no preference ownership.
 */

(() => {
    'use strict';
    const dropdown = '[data-ui-dropdown]';
    const filter = '[data-ui-filter]';
    const option = '[data-ui-filter-value]';
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const closeTimers = new WeakMap();
    const submenus = new WeakMap();
    const panelOf = el => el.querySelector(':scope > .ui-dropdown__panel');
    const parentOf = el => el.parentElement?.closest(dropdown);
    function clearSubmenu(el) {
        const state = submenus.get(el);
        if (!state) return;
        const panel = panelOf(el);
        if (panel.hasAttribute('popover')) {
            if (panel.matches(':popover-open')) panel.hidePopover();
            panel.removeAttribute('popover');
        }
        for (const key of ['left','top','--ui-submenu-shift']) panel.style.removeProperty(key);
        for (const sibling of state.hidden) sibling.removeAttribute('data-ui-submenu-hidden');
        if (state.mode==='stack') panelOf(state.parent).scrollTop=state.scrollTop;
        el.removeAttribute('data-ui-submenu'); el.removeAttribute('data-ui-submenu-side');
        submenus.delete(el);
    }
    function placeSubmenu(el) {
        const parent = parentOf(el);
        if (!el.open || !parent || !parent.open) { clearSubmenu(el); return; }
        const panel = panelOf(el), outer = panelOf(parent), trigger = el.querySelector(':scope > summary');
        const bounds = outer.getBoundingClientRect();
        const left = bounds.left - 12, right = innerWidth - bounds.right - 12;
        const side = left >= right ? 'left' : 'right';
        const mode = typeof panel.showPopover === 'function' && Math.max(left,right) >= 328 ? 'flyout' : 'stack';
        let state = submenus.get(el);
        if (!state || state.mode !== mode || state.parent !== parent) {
            clearSubmenu(el);
            state = {mode,parent,hidden:[],scrollTop:outer.scrollTop}; submenus.set(el,state);
            el.dataset.uiSubmenu = mode;
            if (mode === 'flyout') {
                panel.setAttribute('popover','manual'); panel.showPopover();
            } else {
                // Preserve the existing tree and hide only siblings along the submenu path.
                for (let node=el; node && node!==outer; node=node.parentElement) {
                    for (const sibling of node.parentElement.children) if (sibling!==node) {
                        sibling.setAttribute('data-ui-submenu-hidden',''); state.hidden.push(sibling);
                    }
                }
                outer.scrollTop=0;
            }
        }
        if (mode === 'flyout') {
            // Responsive relocation can remove a native popover from the top layer.
            if (!panel.matches(':popover-open')) panel.showPopover();
            const rect=panel.getBoundingClientRect(), y=trigger.getBoundingClientRect().top;
            el.dataset.uiSubmenuSide=side;
            panel.style.setProperty('--ui-submenu-shift',side==='left'?'6px':'-6px');
            panel.style.left=`${Math.max(8,Math.min(innerWidth-rect.width-8,side==='left'?bounds.left-8-rect.width:bounds.right+8))}px`;
            panel.style.top=`${Math.max(8,Math.min(innerHeight-rect.height-8,y))}px`;
        }
    }
    let submenuFrame=0;
    function scheduleSubmenus() {
        if (!submenuFrame) submenuFrame=requestAnimationFrame(()=>{
            submenuFrame=0;
            for (const el of document.querySelectorAll(`${dropdown}[open]`)) placeSubmenu(el);
        });
    }
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
        clearSubmenu(el);
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
            if (!el.open) {
                clearTimeout(closeTimers.get(el)); clearSubmenu(el);
                for (const child of el.querySelectorAll(`${dropdown}[open]`)) closeDisclosure(child);
                return;
            }
            for (const other of document.querySelectorAll(`${dropdown}[open]`)) {
                if (other !== el && !other.contains(el) && !el.contains(other)) closeDisclosure(other);
            }
            placeSubmenu(el);
        }, true);
        window.addEventListener('resize',scheduleSubmenus);
        window.addEventListener('scroll',scheduleSubmenus,{capture:true,passive:true});
        document.addEventListener('ui:languagechange',scheduleSubmenus);
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
                let menu = target.closest(dropdown);
                while (menu) {
                    const parent = menu.parentElement?.closest(dropdown);
                    closeDisclosure(menu, !parent);
                    menu = parent;
                }
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
        const footer = document.querySelector('[data-ui-footer]');
        const header = document.querySelector('[data-ui-header]');
        function footerDominates() {
            if (!footer) return false;
            const offset = Math.min(innerHeight, Math.max(0, parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--ui-sticky-offset')) || 0));
            const usable = innerHeight - offset;
            const rect = footer.getBoundingClientRect();
            const visible = Math.max(0, Math.min(rect.bottom, innerHeight) - Math.max(rect.top, offset));
            return usable > 0 && visible > usable / 2;
        }
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
            const footerActive = footerDominates();
            for (const group of groups) {
                if (footerActive) { activate(group, null); continue; }
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
        document.addEventListener('ui:languagechange', schedule);
        document.addEventListener('ui:themechange', schedule);
        // Section heights can change without a window resize (fonts, images, filtering).
        if ('ResizeObserver' in window) {
            const geometry = new ResizeObserver(schedule);
            geometry.observe(document.body);
            if (footer) geometry.observe(footer);
            if (header) geometry.observe(header);
            for (const group of groups) for (const item of group.items) geometry.observe(item.section);
        }
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
