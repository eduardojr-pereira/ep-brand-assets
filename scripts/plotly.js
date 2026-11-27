/* Responsibility: Apply canonical presentation to Plotly figures, using the single UI theme/locale.
 * Per-graph serialized updates; no analytical transformations, runtime downloads or independent preferences. */
(() => {
    'use strict';
    window.UI ??= {};
    const graphs = new WeakMap();
    const registered = new WeakSet();
    const specifications = new WeakMap();
    const report = (node, error) => console.error('UI Plotly:', node.id || '(unknown chart)', error);
    const copy = value => JSON.parse(JSON.stringify(value));
    const pathParts = path => path.replace(/\[(\d+)\]/g, '.$1').split('.');
    function put(object, path, value) {
        const parts = pathParts(path);
        if (parts.some(p => ['__proto__','prototype','constructor'].includes(p))) throw new Error('Invalid chart field');
        let target = object;
        for (let i=0; i<parts.length-1; i++) {
            const k = parts[i];
            if (typeof target[k] === 'string' && k === 'title') target[k]={text:target[k]};
            target[k] ??= /^\d+$/.test(parts[i+1]) ? [] : {};
            if (typeof target[k] !== 'object') throw new Error(`Invalid chart field: ${path}`);
            target = target[k];
        }
        target[parts.at(-1)] = copy(value);
    }
    function themeLayout(layout, spec, theme, locale) {
        const css = getComputedStyle(document.documentElement);
        const color = name => css.getPropertyValue('--ui-color-'+name).trim();
        const font = css.getPropertyValue('--ui-font-body').trim();
        const heading = css.getPropertyValue('--ui-font-heading').trim();
        const background = color('surface'), text = color('text'), border = color('border'), muted = color('muted');
        const out = {
            paper_bgcolor:background, plot_bgcolor:background, 'font.color':text, 'font.family':font,
            'title.font.color':text, 'title.font.family':heading,
            'hoverlabel.bgcolor':background, 'hoverlabel.bordercolor':border, 'hoverlabel.font.color':text, 'hoverlabel.font.family':font,
            'legend.font.color':text, 'legend.bgcolor':background,
            'modebar.bgcolor':background, 'modebar.color':muted, 'modebar.activecolor':color('accent'),
            separators:locale==='pt-BR'?',.': '.,'
        };
        if (spec.colorway) out.colorway=spec.colorway[theme];
        function axis(key, value) {
            for (const [name, val] of Object.entries({gridcolor:border,zerolinecolor:border,linecolor:border,'tickfont.color':muted,'title.font.color':text})) out[key+'.'+name]=val;
            if (value?.rangeslider) { out[key+'.rangeslider.bgcolor']=background; out[key+'.rangeslider.bordercolor']=border; }
            if (value?.rangeselector) { out[key+'.rangeselector.bgcolor']=background; out[key+'.rangeselector.activecolor']=border; out[key+'.rangeselector.bordercolor']=border; out[key+'.rangeselector.font.color']=text; }
        }
        for (const [key,value] of Object.entries(layout)) {
            if (/^[xy]axis\d*$/.test(key)) axis(key,value);
            if (/^scene\d*$/.test(key)) {
                out[key+'.bgcolor']=background;
                for (const a of ['xaxis','yaxis','zaxis']) { axis(key+'.'+a,value?.[a]); out[key+'.'+a+'.backgroundcolor']=background; }
            }
            if (/^coloraxis\d*$/.test(key)) {out[key+'.colorbar.tickfont.color']=muted;out[key+'.colorbar.title.font.color']=text;}
        }
        // Default Cartesian axes may not exist in the input layout.
        if (spec.data.some(t=>['scatter','scattergl','bar','box','violin','heatmap','histogram','contour','waterfall','funnel','candlestick','ohlc'].includes(t.type||'scatter'))) {for(const key of ['xaxis','yaxis']) if (!layout[key]) axis(key);}
        (layout.updatemenus||[]).forEach((_,i)=>Object.assign(out,{[`updatemenus[${i}].bgcolor`]:background,[`updatemenus[${i}].bordercolor`]:border,[`updatemenus[${i}].font.color`]:text}));
        (layout.sliders||[]).forEach((_,i)=>Object.assign(out,{[`sliders[${i}].bgcolor`]:background,[`sliders[${i}].bordercolor`]:border,[`sliders[${i}].font.color`]:text,[`sliders[${i}].currentvalue.font.color`]:text}));
        return out;
    }
    function presentation(spec, layout, theme, locale) {
        const msg = ref => Array.isArray(ref) ? ref.map(msg) : UI.i18n.format(ref,{},locale);
        const patch = themeLayout(layout,spec,theme,locale);
        for (const [path,ref] of Object.entries(spec.translations?.layout||{})) patch[path]=msg(ref);
        const traces = new Map();
        const fields = i => { if (!traces.has(i)) traces.set(i,{});return traces.get(i); };
        for (const item of spec.translations?.traces||[]) for (const [path,ref] of Object.entries(item.fields)) fields(item.index)[path]=msg(ref);
        for (const item of spec.colors||[]) fields(item.trace)[item.path]=item.values[theme];
        return {patch,traces};
    }
    async function apply(node,state) {
        const runtime=window.Plotly;
        if (!runtime?.newPlot || !runtime?.relayout || !runtime?.restyle || !runtime?.react) return;
        if (!registered.has(runtime)) { runtime.register(state.spec.localeModule); registered.add(runtime); }
        const theme=UI.theme.current(), locale=UI.i18n.current();
        if (state.ready && state.theme===theme && state.locale===locale) return;
        const spec=state.spec, config={...spec.config,responsive:true,locale};
        const {patch,traces}=presentation(spec,state.ready?node.layout:spec.layout,theme,locale);
        if (!state.ready) {
            const layout=copy(spec.layout), data=copy(spec.data);
            delete layout.width; layout.autosize=true;
            for (const [path,value] of Object.entries(patch)) put(layout,path,value);
            for (const [index,update] of traces) for (const [path,value] of Object.entries(update)) put(data[index],path,value);
            await runtime.newPlot(node,data,layout,config);
            state.ready=true;
            node.setAttribute('data-ui-plotly-ready','');
            const fallback=node.closest('[data-ui-plotly-container]')?.querySelector('[data-ui-plotly-fallback]');
            if (fallback) fallback.hidden=true;
        } else {
            // Only native locale config requires react. Use the LIVE data/layout, not the original spec.
            // Relayout/restyle update presentation attributes only; do not reset ranges, menus or selection.
            if (state.locale!==locale) await runtime.react(node,node.data,node.layout,config);
            await runtime.relayout(node,patch);
            for (const [index,update] of traces) {
                const values=Object.fromEntries(Object.entries(update).map(([path,value])=>[path,[copy(value)]]));
                await runtime.restyle(node,values,[index]);
            }
        }
        state.theme=theme;state.locale=locale;
    }
    function schedule(node,state) {
        state.dirty=true;
        if (state.pending) return state.pending;
        state.pending=(async()=>{
            while (state.dirty && node.isConnected) {
                state.dirty=false;
                try { await apply(node,state); }
                catch (error) { report(node,error); }
            }
        })().finally(()=>{state.pending=null;if(state.dirty&&node.isConnected) schedule(node,state);});
        return state.pending;
    }
    function refresh() {
        if (!window.Plotly || !UI.theme || !UI.i18n) return Promise.resolve([]);
        const tasks=[];
        for (const element of document.querySelectorAll('script[type="application/json"][data-ui-plotly-spec]')) {
            try {
                let spec=specifications.get(element);
                if (!spec) { spec=JSON.parse(element.textContent);specifications.set(element,spec); }
                const node=document.getElementById(spec.id);
                if (!node?.hasAttribute('data-ui-plotly')) throw new Error(`Missing chart target: ${spec.id}`);
                let state=graphs.get(node);
                if (!state) { state={spec,ready:false,dirty:false,pending:null};graphs.set(node,state); }
                else if (state.spec.id!==spec.id) throw new Error('Chart ID changed');
                tasks.push(schedule(node,state));
            } catch(error) {report(element,error);}
        }
        return Promise.allSettled(tasks);
    }
    window.UI.plotly=Object.freeze({refresh});
    document.addEventListener('ui:themechange',refresh);
    document.addEventListener('ui:languagechange',refresh);
    if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',refresh,{once:true}); else refresh();
    window.addEventListener('load',refresh,{once:true});
    // Late external Plotly script: load is non-bubbling but observable in capture.
    document.addEventListener('load',event=>{if(event.target instanceof HTMLScriptElement && window.Plotly) refresh();},true);
})();
