/* Responsibility: Resolve canonical asset URLs, load/cache canonical JSON sources and animation player,
 * mount/dispose Lottie instances, apply themed asset variants. No selection or locale state. */
(() => {
    'use strict';
    window.UI ??= {};
    const config = JSON.parse(document.getElementById('ui-config').textContent);
    const base = new URL(config.assetBase.replace(/\/?$/, '/'), document.baseURI);
    const settings = config.lottie;
    const sources = new Map(), mounts = new Map();
    let runtime;
    function url(path) {
        if (typeof path !== 'string' || !path.split('/').every(part => /^[\w.-]+$/.test(part) && part !== '.' && part !== '..')) throw new Error('Invalid asset path');
        return new URL(path, base).href;
    }
    function player() {
        if (!runtime) runtime = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url(settings.runtime);
            script.onload = () => {
                const api = window.lottie;
                if (!api || api.version !== settings.version) { script.remove(); reject(new Error('Invalid Lottie runtime')); }
                else resolve(api);
            };
            script.onerror = () => { script.remove(); reject(new Error('Lottie runtime unavailable')); };
            document.head.append(script);
        }).catch(error => { runtime = undefined; throw error; });
        return runtime;
    }
    function source(path) {
        if (!sources.has(path)) sources.set(path, fetch(url(path)).then(response => {
            if (!response.ok) throw new Error(`Asset unavailable: ${path}`);
            return response.json();
        }).catch(error => { sources.delete(path); throw error; }));
        return sources.get(path);
    }
    function recolor(value, rgba) {
        if (!value || typeof value !== 'object') return;
        if ((value.ty === 'st' || value.ty === 'fl') && value.c?.a === 0) value.c.k = rgba;
        Object.values(value).forEach(child => recolor(child, rgba));
    }
    function dispose(host, entry) {
        entry.generation++;
        entry.player?.destroy(); entry.player = null;
        host.removeAttribute('data-ui-lottie-ready'); host.replaceChildren();
    }
    async function refresh(host, entry) {
        dispose(host, entry);
        const generation = entry.generation;
        const {id, variant, colorToken, onReady} = entry.options;
        try {
            const item = settings.animations[id];
            if (!item) throw new Error(`Unknown animation: ${id}`);
            const chosen = variant === 'theme' ? (UI.theme.current() === 'light' ? 'graphite' : 'white') : variant;
            const path = item.file || item.variants?.[chosen];
            const [api, original] = await Promise.all([player(), source(path)]);
            if (mounts.get(host) !== entry || generation !== entry.generation || !host.isConnected) return;
            const data = JSON.parse(JSON.stringify(original));
            if (colorToken) {
                const raw = getComputedStyle(document.documentElement).getPropertyValue(colorToken).trim();
                if (!/^#[0-9a-f]{6}$/i.test(raw)) throw new Error('Invalid animation color token');
                recolor(data, [1,3,5].map(i => parseInt(raw.slice(i,i+2),16)/255).concat(1));
            }
            const animation = api.loadAnimation({container: host, renderer:'svg', loop:false, autoplay:false, animationData:data});
            entry.player = animation;
            const loaded = () => {
                if (entry.player !== animation || generation !== entry.generation || !host.isConnected) return;
                host.setAttribute('data-ui-lottie-ready',''); onReady?.(animation);
            };
            animation.addEventListener('DOMLoaded', loaded);
            animation.addEventListener('data_failed', () => {
                if (entry.player !== animation) return;
                sources.delete(path);
                dispose(host,entry);
                console.warn(`UI animation data failed: ${id}`);
            });
        } catch (error) {
            if (mounts.get(host) === entry && generation === entry.generation) {
                dispose(host,entry);
                console.warn(`UI animation unavailable: ${id}`, error);
            }
        }
    }
    function mount(host, options) {
        unmount(host);
        const entry = {options, generation:0, player:null}; mounts.set(host,entry);
        refresh(host,entry);
    }
    function unmount(host) { const entry = mounts.get(host); if (entry) { dispose(host,entry); mounts.delete(host); } }
    function get(host) { return host.hasAttribute('data-ui-lottie-ready') ? mounts.get(host)?.player : null; }
    function images() {
        const light = UI.theme.current() === 'light';
        const portuguese = UI.i18n.current() === 'pt-BR';
        document.querySelectorAll('[data-light-src], [data-dark-src], [data-en-src], [data-pt-br-src]').forEach(image => {
            const localized = portuguese ? image.getAttribute('data-pt-br-src') : image.getAttribute('data-en-src');
            const next = localized || (light ? image.dataset.lightSrc : image.dataset.darkSrc);
            if (next && image.getAttribute('src') !== next) image.src = next;
        });
    }
    document.addEventListener('ui:themechange', () => {
        images();
        for (const [host, entry] of mounts) {
            if (!host.isConnected) unmount(host);
            else if (entry.options.colorToken || entry.options.variant === 'theme') refresh(host,entry);
        }
    });
    document.addEventListener('ui:languagechange', images);
    // Consumers explicitly unmount removed components; cleanup detached hosts on DOM removal.
    new MutationObserver(() => { for (const host of mounts.keys()) if (!host.isConnected) unmount(host); }).observe(document.documentElement,{childList:true,subtree:true});
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', images, {once:true}); else images();
    window.UI.assets = Object.freeze({url,json:source,mount,unmount,get});
})();
