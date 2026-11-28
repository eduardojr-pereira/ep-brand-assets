/*
 * Responsibility: Manage indexed disclosures, search controls, state-driven Search-to-X artwork and normalized matching.
 * Boundaries: No independent locale, theme, preference or animation loader.
 */
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
                if (art.closest('.ui-indexed-item') && player.frameRate > 0) {
                    const timing=getComputedStyle(art).getPropertyValue('--ui-disclosure-duration').trim() || getComputedStyle(art).getPropertyValue('--ui-duration-link').trim();
                    const duration=parseFloat(timing)/(timing.endsWith('ms')?1000:1);
                    if (duration>0) player.setSpeed(player.totalFrames/(player.frameRate*duration));
                }
                player.setDirection(state.active?1:-1); player.play();
            } else if (changed || !animate) settle(player);
        } else if (!state.mounted || changed || recolor) {
            state.mounted=true;
            UI.assets.mount(host,{id:'search_to_x',variant:'theme',colorToken:state.colorToken,onReady:settle});
        }
    }
    function searchControl(control) {
        const toggle=control.querySelector('[data-ui-search-toggle]');
        const field=control.querySelector('[data-ui-search-field]');
        const input=control.querySelector('[data-ui-search-query]');
        const art=toggle.querySelector('[data-ui-toggle-art]');
        let opened=false;
        function notify() {
            control.dispatchEvent(new CustomEvent('ui:searchchange',{bubbles:true,detail:{query:input.value}}));
        }
        function setOpen(value,focus=true) {
            opened=value;field.hidden=!value;
            toggle.setAttribute('aria-expanded',String(value));
            UI.i18n.bind(toggle,'aria-label',value?control.dataset.uiSearchCloseLabel:control.dataset.uiSearchLabel);
            toggleArt(art,value,focus,control.dataset.uiSearchColor);
            if(value && focus) input.focus();
            if(!value) {input.value='';notify();if(focus) toggle.focus();}
        }
        toggle.addEventListener('click',()=>setOpen(!opened));
        input.addEventListener('input',notify);
        input.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();setOpen(false);}});
        control.hidden=false;setOpen(false,false);
    }
    function indexedItem(item) {
        const art=item.querySelector(':scope > summary [data-ui-toggle-art]');
        const update=animate=>toggleArt(art,item.open,animate,'--ui-color-text');
        update(false);
        item.addEventListener('toggle',()=>update(true));
        // A required-selection consumer uses native exclusive details, but
        // activating the already selected summary must not empty the group.
        if (item.name && item.parentElement?.hasAttribute('data-ui-disclosure-required')) {
            item.querySelector(':scope > summary').addEventListener('click',event=>{
                if (item.open) event.preventDefault();
            });
        }
    }
    const start=()=>{
        document.querySelectorAll('[data-ui-search-control]').forEach(searchControl);
        document.querySelectorAll('.ui-indexed-item').forEach(indexedItem);
    };
    if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});else start();
    const settleAll=()=>document.querySelectorAll('[data-ui-toggle-art]').forEach(art=>{
        const state=states.get(art);if(state) toggleArt(art,state.active,false,state.colorToken);
    });
    reduced.addEventListener('change',settleAll);
    document.addEventListener('visibilitychange',()=>{if(document.hidden) settleAll();});
    window.UI.disclosure=Object.freeze({matches,toggleArt});
})();
