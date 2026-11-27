/* Responsibility: Single locale preference, message resolution, formatting and DOM bindings.
 * Synchronous head initialization; never resets component state or replays animations. */
(() => {
    'use strict';
    window.UI ??= {};
    const root = document.documentElement;
    const storageKey = 'ui.locale';
    const targets = ['text','aria-label','placeholder','alt','title'];
    const selector = targets.map(t => `[data-i18n-${t}]`).join(',');
    let data;
    try { data = JSON.parse(document.getElementById('ui-config').textContent).translations; }
    catch (error) { console.error('UI translation configuration unavailable:', error); return; }
    const locales = Object.keys(data);
    const normalize = value => {
        const lang = String(value || '').toLowerCase();
        return lang === 'pt' || lang.startsWith('pt-') ? 'pt-BR' : lang === 'en' || lang.startsWith('en-') ? 'en' : null;
    };
    const getSaved = () => { try { return localStorage.getItem(storageKey); } catch { return null; } };
    const resolve = () => normalize(getSaved()) || (navigator.languages || [navigator.language]).map(normalize).find(Boolean) || 'en';
    let locale = resolve();
    let ready = false;
    const bindings = new WeakMap();
    function format(key, args = {}, language = locale) {
        let value = data[language]?.[key];
        if (value === undefined) throw new Error(`Unknown translation key: ${key}`);
        if (typeof value === 'object') value = value[args.count === 0 ? 'other' : new Intl.PluralRules(language).select(args.count)] || value.other;
        return value.replace(/\{(\w+)\}/g, (_, name) => {
            if (!(name in args)) throw new Error(`Missing translation argument: ${key}.${name}`);
            return typeof args[name] === 'number' ? new Intl.NumberFormat(language).format(args[name]) : String(args[name]);
        });
    }
    function write(node, target, value) {
        if (target === 'text') { if (node.textContent !== value) node.textContent = value; }
        else if (node.getAttribute(target) !== value) node.setAttribute(target, value);
    }
    function plan(language) {
        const updates = [];
        for (const node of document.querySelectorAll(selector)) {
            for (const target of targets) {
                const key = node.getAttribute(`data-i18n-${target}`);
                if (key) updates.push([node, target, format(key, bindings.get(node)?.[target] || {}, language)]);
            }
        }
        return updates;
    }
    function apply(updates) { for (const update of updates) write(...update); }
    function bind(node, target, key, args = {}) {
        if (!targets.includes(target)) throw new RangeError('Unsupported translation target');
        const value = format(key, args);
        const values = bindings.get(node) || {};
        values[target] = {...args}; bindings.set(node, values);
        node.setAttribute(`data-i18n-${target}`, key);
        write(node, target, value);
    }
    function clear(node, target = 'text') {
        node.removeAttribute(`data-i18n-${target}`);
        if (bindings.has(node)) delete bindings.get(node)[target];
        write(node, target, '');
    }
    function bindFrom(node, source, target = 'text') {
        const key = source.getAttribute(`data-i18n-${target}`);
        if (key) bind(node, target, key, bindings.get(source)?.[target] || {});
        else { clear(node, target); write(node, target, target === 'text' ? source.textContent : source.getAttribute(target) || ''); }
    }
    function change(value, persist = false) {
        if (!locales.includes(value)) throw new RangeError('Unsupported locale');
        const changed = value !== locale;
        const updates = ready && changed ? plan(value) : [];
        // Resolve every binding before committing DOM, preference and event.
        apply(updates);
        locale = value; root.lang = locale;
        if (persist) { try { localStorage.setItem(storageKey, value); } catch {} }
        if (ready && changed) document.dispatchEvent(new CustomEvent('ui:languagechange', {detail: {locale}}));
    }
    function set(value) { change(value, true); }
    window.UI.i18n = Object.freeze({current: () => locale, set, format, bind, clear, bindFrom});
    root.lang = locale;
    // Only conceal untranslated markup on cold startup; no arbitrary timeout.
    if (locale !== 'en' && document.readyState === 'loading' && !document.body) root.setAttribute('data-ui-localizing', '');
    function initialize() {
        try { apply(plan(locale)); }
        catch (error) {
            // No partial writes were made. Keep the server-rendered English fallback.
            locale = 'en'; root.lang = locale;
            console.error('UI translation startup failed:', error);
        } finally {
            ready = true;
            root.removeAttribute('data-ui-localizing');
        }
        document.dispatchEvent(new CustomEvent('ui:languagechange', {detail: {locale}}));
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, {once:true});
    else initialize();
    window.addEventListener('storage', e => {
        if (e.key !== storageKey && e.key !== null) return;
        try { change(resolve()); } catch (error) { console.error('UI translation change rejected:', error); }
    });
})();
