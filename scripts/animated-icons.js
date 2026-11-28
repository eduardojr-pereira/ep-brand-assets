/*
 * Responsibility: Manage shared animated link icon hover and focus playback and static presentation.
 * Boundaries: UI.assets exclusively owns source/runtime loading, caching, recoloring and disposal.
 */
(() => {
    'use strict';
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    function init(art) {
        const link = art.closest('a');
        const rest = art.querySelector('[data-ui-icon-rest]');
        const hover = art.querySelector('[data-ui-icon-hover]');
        const id = art.dataset.uiIconAnimation;
        const tone = art.dataset.uiIconTone;
        const restVariant = tone === 'contact' ? 'white' : 'theme';
        const hoverVariant = tone === 'editorial' ? 'copper' : restVariant;
        const last = player => { player.loop = false; player.goToAndStop(Math.max(0,Math.ceil(player.totalFrames)-1),true); };
        let mounted = false, pointer = false, focus = false;
        function sync() {
            const active = pointer || focus;
            art.toggleAttribute('data-ui-playing',active);
            const player = UI.assets.get(hover);
            if (player) { if (active && !reduced.matches && !document.hidden) { player.loop = tone !== 'editorial'; player.goToAndPlay(0,true); } else last(player); }
        }
        function mount(retry = false) {
            if (mounted && !retry) return;
            mounted = true;
            if (!UI.assets.get(rest)) UI.assets.mount(rest,{id,variant:restVariant,...(id==='initials'?{colorToken:'--ui-color-text'}:{}),onReady:last});
            if (!UI.assets.get(hover)) UI.assets.mount(hover,{id,variant:hoverVariant,...(id==='initials'?{colorToken:'--ui-color-accent'}:{}),onReady:sync});
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
    const start = () => document.querySelectorAll('[data-ui-icon-animation]').forEach(init);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',start,{once:true}); else start();
})();
