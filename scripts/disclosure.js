/* Responsibility: Shared state-driven Search-to-X artwork and normalized search matching.
 * No independent locale, theme, preference or animation loader. */
(() => {
    'use strict';
    window.UI ??= {};
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const states = new WeakMap();
    const normalize = value => String(value).normalize('NFD').replace(/\p{Diacritic}/gu,'').toLowerCase().trim();
    function matches(text,query) {
        const target=normalize(text);
        return normalize(query).split(/\s+/).filter(Boolean).every(word=>target.includes(word));
    }
    function toggleArt(art,active,animate=true,colorToken='--ui-color-accent') {
        if (!art) return;
        let state=states.get(art);
        const host=art.querySelector('[data-ui-toggle-player]');
        if (!state) {
            state={active:Boolean(active),mounted:false,colorToken}; states.set(art,state);
            art.toggleAttribute('data-ui-active',state.active);
        }
        const changed=state.active!==Boolean(active);
        const recolor=state.colorToken!==colorToken; state.colorToken=colorToken;
        state.active=Boolean(active);art.toggleAttribute('data-ui-active',state.active);
        if (!host || !UI.assets) return;
        const settle=player=>player.goToAndStop(state.active?Math.max(0,Math.ceil(player.totalFrames)-1):0,true);
        const player=UI.assets.get(host);
        if (player && !recolor) {
            if (changed && animate && !reduced.matches && !document.hidden) {
                player.setDirection(state.active?1:-1); player.play();
            } else if (changed || !animate) settle(player);
        } else if (!state.mounted || changed || recolor) {
            state.mounted=true;
            UI.assets.mount(host,{id:'search_to_x',variant:'theme',colorToken:state.colorToken,onReady:settle});
        }
    }
    const settleAll=()=>document.querySelectorAll('[data-ui-toggle-art]').forEach(art=>{
        const state=states.get(art);if(state) toggleArt(art,state.active,false,state.colorToken);
    });
    reduced.addEventListener('change',settleAll);
    document.addEventListener('visibilitychange',()=>{if(document.hidden) settleAll();});
    window.UI.disclosure=Object.freeze({matches,toggleArt});
})();
