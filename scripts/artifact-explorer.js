/* Responsibility: File list filtering and preview selection; never fetches or executes artifact content.
 * Shared localization bindings, search matching and animation remain canonical services. */
(() => {
    'use strict';
    function init(root) {
        const items=[...root.querySelectorAll('[data-ui-artifact-item]')];
        const panels=[...root.querySelectorAll('[data-ui-artifact-preview]')];
        const links=items.map(item=>item.querySelector('[data-ui-artifact-select]'));
        const control=root.querySelector('[data-ui-search-control]');
        const toggle=control.querySelector('[data-ui-search-toggle]');
        const field=control.querySelector('[data-ui-search-field]');
        const input=control.querySelector('[data-ui-artifact-query]');
        const art=toggle.querySelector('[data-ui-toggle-art]');
        const empty=root.querySelector('[data-ui-artifact-empty]');
        let selected=0, opened=false;
        function select(index) {
            selected=index;
            links.forEach((link,i)=>{ if(i===selected) link.setAttribute('aria-current','true');else link.removeAttribute('aria-current'); });
            panels.forEach((panel,i)=>panel.hidden=i!==selected);
        }
        function filter() {
            items.forEach(item=>item.hidden=!UI.disclosure.matches(item.dataset.search,input.value));
            empty.hidden=items.some(item=>!item.hidden);
            // Keep the current preview and query even when a filter hides its list entry.
        }
        function setOpen(value,focus=true) {
            opened=value; field.hidden=!value;
            toggle.setAttribute('aria-expanded',String(value));
            UI.i18n.bind(toggle,'aria-label',value?'shared.artifacts.close_search':'shared.artifacts.search');
            UI.disclosure.toggleArt(art,value,focus);
            if(value && focus) input.focus();
            if(!value) { input.value='';filter(); if(focus) toggle.focus(); }
        }
        links.forEach((link,i)=>link.addEventListener('click',event=>{
            if(event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey) return;
            event.preventDefault();select(i);
        }));
        toggle.addEventListener('click',()=>setOpen(!opened));
        input.addEventListener('input',filter);
        input.addEventListener('keydown',event=>{ if(event.key==='Escape') { event.preventDefault();setOpen(false); } });
        root.querySelectorAll('[data-ui-artifact-image]').forEach(image=>{
            const failure=()=>{ image.hidden=true; image.parentElement.querySelector('[data-ui-image-error]').hidden=false; };
            image.addEventListener('error',failure); if(image.complete&&!image.naturalWidth) failure();
        });
        select(0);control.hidden=false;setOpen(false,false);
        // Static bilingual search metadata and global DOM bindings preserve selection, query and disclosure state.
    }
    const start=()=>document.querySelectorAll('[data-ui-artifact-explorer]').forEach(init);
    if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
