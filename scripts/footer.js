/* Responsibility: Footer icon hover/focus playback and static presentation.
 * UI.assets exclusively owns source/runtime loading, caching, recoloring and disposal. */
(() => {
    'use strict';
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    function init(root) {
        const entries = [...root.querySelectorAll('[data-ui-footer-animation]')];
        for (const art of entries) {
            const link = art.closest('a');
            const rest = art.querySelector('[data-ui-footer-rest]');
            const hover = art.querySelector('[data-ui-footer-hover]');
            const id = art.dataset.uiFooterAnimation;
            const last = player => player.goToAndStop(Math.max(0,Math.ceil(player.totalFrames)-1),true);
            let mounted = false, pointer = false, focus = false;
            function sync() {
                const active = pointer || focus;
                art.toggleAttribute('data-ui-playing',active);
                const player = UI.assets.get(hover);
                if (player) { if (active && !reduced.matches && !document.hidden) player.goToAndPlay(0,true); else last(player); }
            }
            function mount(retry = false) {
                if (mounted && !retry) return;
                mounted = true;
                if (!UI.assets.get(rest)) UI.assets.mount(rest,{id,variant:'theme',onReady:last});
                if (!UI.assets.get(hover)) UI.assets.mount(hover,{id,variant:'copper',onReady:sync});
            }
            link.addEventListener('pointerenter', e => { if(e.pointerType === 'mouse') { pointer=true; mount(true); sync(); } });
            link.addEventListener('pointerleave', () => { pointer=false; sync(); });
            link.addEventListener('focus', () => { focus=true; mount(true); sync(); });
            link.addEventListener('blur', () => { focus=false; sync(); });
            reduced.addEventListener('change',sync);
            document.addEventListener('visibilitychange',sync);
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver(entries => { if(entries.some(e=>e.isIntersecting)) { mount(); observer.disconnect(); } },{rootMargin:'160px'});
                observer.observe(art);
            } else mount();
        }
    }
    const start = () => document.querySelectorAll('[data-ui-footer]').forEach(init);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',start,{once:true}); else start();
})();
