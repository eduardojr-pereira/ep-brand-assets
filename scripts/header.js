/*
 * Responsibility: Place the same navigation nodes in responsive disclosure and measure the sticky offset.
 * Boundaries: Preference buttons call global services; no local preference state.
 */
(() => {
    'use strict';
    function init(header) {
        const entry = header.querySelector('.ui-header__entry');
        const desktop = header.querySelector('.ui-header__desktop');
        const compact = header.querySelector('.ui-header__compact');
        const details = compact.querySelector('details');
        const panel = details.querySelector('.ui-dropdown__panel');
        const links = desktop.firstElementChild;
        const controls = header.querySelector('.ui-header__controls');
        const nav = header.querySelector('.ui-header__nav');
        const logo = header.querySelector('.ui-header__logo');
        const back = header.querySelector('.ui-header__back');
        const items = [...links.children].filter(node => node.matches('a'));
        controls.hidden = false;
        header.setAttribute('data-ui-enhanced','');
        controls.querySelector('[data-ui-language-control]').addEventListener('click', () => UI.i18n.set(UI.i18n.current() === 'en' ? 'pt-BR' : 'en'));
        controls.querySelector('[data-ui-theme-control]').addEventListener('click', () => UI.theme.set(UI.theme.current() === 'dark' ? 'light' : 'dark'));
        let frame = 0;
        function layout() {
            frame = 0;
            const was = header.hasAttribute('data-ui-compact');
            if (was && header.clientWidth <= 670) {
                document.documentElement.style.setProperty('--ui-sticky-offset',`${header.offsetHeight}px`);
                return;
            }
            const focused = document.activeElement;
            const inside = links.contains(focused);
            // Measure natural desktop width synchronously, then restore the single node tree.
            header.removeAttribute('data-ui-compact');
            desktop.hidden = false; compact.hidden = true;
            if (links.parentElement !== desktop) desktop.append(links);
            items.forEach(a => { a.classList.remove('ui-link--diagonal','ui-dropdown__item'); a.classList.add('ui-underline'); });
            const css = getComputedStyle(entry);
            const available = header.clientWidth - parseFloat(css.paddingLeft) - parseFloat(css.paddingRight) - 2*parseFloat(css.columnGap) - logo.offsetWidth - controls.offsetWidth;
            const required = links.scrollWidth + (back ? back.scrollWidth + parseFloat(getComputedStyle(nav).columnGap) : 0);
            const narrow = header.clientWidth <= 670 || required > available + 1;
            if (narrow) {
                header.setAttribute('data-ui-compact','');
                compact.hidden = false; desktop.hidden = true; panel.append(links);
                items.forEach(a => { a.classList.remove('ui-underline'); a.classList.add('ui-link--diagonal','ui-dropdown__item'); });
                if (!was) details.open = false;
            } else if (was) details.open = false;
            if (was !== narrow) for (const menu of links.querySelectorAll('[data-ui-dropdown][open]')) menu.open=false;
            if (inside && document.activeElement !== focused) {
                if (narrow && !details.open) details.querySelector('summary').focus({preventScroll:true});
                else focused.focus({preventScroll:true});
            } else if (was && !narrow && compact.contains(focused)) items[0]?.focus({preventScroll:true});
            document.documentElement.style.setProperty('--ui-sticky-offset',`${header.offsetHeight}px`);
        }
        const schedule = () => { if (!frame) frame = requestAnimationFrame(layout); };
        window.addEventListener('resize',schedule);
        document.addEventListener('ui:languagechange',schedule);
        document.fonts?.ready.then(schedule);
        if ('ResizeObserver' in window) {
            let width = header.clientWidth;
            new ResizeObserver(() => {
                document.documentElement.style.setProperty('--ui-sticky-offset',`${header.offsetHeight}px`);
                if (width !== header.clientWidth) { width = header.clientWidth; schedule(); }
            }).observe(header);
        }
        layout();
    }
    const start = () => document.querySelectorAll('[data-ui-header]').forEach(init);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',start,{once:true}); else start();
})();
