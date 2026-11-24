/* EP Brand — shared Plotly theme. */
(function () {
  'use strict';

  const root = document.documentElement;

  function tokens() {
    const css = getComputedStyle(root);
    const get = name => css.getPropertyValue(name).trim();

    return {
      surface: get('--ep-color-surface'),
      text: get('--ep-color-text'),
      muted: get('--ep-color-muted'),
      border: get('--ep-color-border'),
      accent: get('--ep-color-accent'),
      font: get('--ep-font-sans') || 'Source Sans 3, sans-serif'
    };
  }

  const observedGraphs = new WeakSet();

  function syncSelectedOptions(graph) {
    const menus = graph._fullLayout?.updatemenus || [];

    graph.querySelectorAll(
      '.updatemenu-dropdown-button'
    ).forEach(button => {
      const group = button.closest(
        '.updatemenu-dropdown-button-group'
      );

      const menuIndex = group?.__data__?._index
        ?? (menus.length === 1 ? 0 : -1);

      const menu = menus[menuIndex];
      const index = button.__data__?._index;

      button.classList.toggle(
        'ep-plotly-selected',
        !!menu && menu.showactive !== false
          && Number.isInteger(index)
          && index === menu.active
      );
    });
  }

  function observeControls(graph) {
    if (observedGraphs.has(graph)) return;
    observedGraphs.add(graph);

    const refresh = () => {
      requestAnimationFrame(() => syncSelectedOptions(graph));
    };

    const observer = new MutationObserver(refresh);
    observer.observe(graph, {
      childList: true,
      subtree: true
    });

    graph.on('plotly_buttonclicked', refresh);
    graph.on('plotly_afterplot', refresh);

    refresh();
  }

  function layoutUpdate(layout) {
    const t = tokens();

    const update = {
      paper_bgcolor: t.surface,
      plot_bgcolor: t.surface,
      'font.color': t.text,
      'font.family': t.font,
      'hoverlabel.bgcolor': t.surface,
      'hoverlabel.bordercolor': t.border,
      'hoverlabel.font.color': t.text,
      'legend.font.color': t.text,
      'legend.bgcolor': t.surface,
      'modebar.bgcolor': t.surface,
      'modebar.color': t.muted,
      'modebar.activecolor': t.accent
    };

    for (const [key, axis] of Object.entries(layout)) {
      if (!/^[xy]axis\d*$/.test(key)) continue;
      if (!axis || typeof axis !== 'object') continue;

      update[key + '.gridcolor'] = t.border;
      update[key + '.zerolinecolor'] = t.border;
      update[key + '.linecolor'] = t.border;
      update[key + '.tickfont.color'] = t.muted;
      update[key + '.title.font.color'] = t.text;

      if (axis.rangeslider) {
        update[key + '.rangeslider.bgcolor'] = t.surface;
        update[key + '.rangeslider.bordercolor'] = t.border;
      }

      if (axis.rangeselector) {
        update[key + '.rangeselector.bgcolor'] = t.surface;
        update[key + '.rangeselector.activecolor'] = t.border;
        update[key + '.rangeselector.bordercolor'] = t.border;
        update[key + '.rangeselector.font.color'] = t.text;
      }
    }

    (layout.updatemenus || []).forEach((menu, i) => {
      const key = `updatemenus[${i}]`;

      update[key + '.bgcolor'] = t.surface;
      update[key + '.bordercolor'] = t.border;
      update[key + '.font.color'] = t.text;
      update[key + '.font.family'] = t.font;
    });

    return update;
  }

  const originalColors = new WeakMap();
  const pendingGraphs = new WeakSet();
  const darkPalette = Array.from({length:8},(_,i)=>getComputedStyle(root).getPropertyValue('--ep-muted-reference-'+i).trim().toUpperCase());
  function colorBindings(data, layout) {
    const result = [];
    function visit(obj, path, index) {
      if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return;
      for (const [k,v] of Object.entries(obj)) {
        const key = path ? path+'.'+k : k;
        if (k === 'color' || k === 'fillcolor') {
          const values = Array.isArray(v) ? v : [v];
          if (values.some(c => typeof c === 'string' && darkPalette.includes(c.toUpperCase()))) {
            result.push({index,key,value:v});
          }
        } else if (v && typeof v === 'object' && !Array.isArray(v) && k !== 'template') visit(v,key,index);
      }
    }
    data.forEach((trace,i)=>visit(trace,'',i));
    // Bike zero-reference line is semantic neutral, not a data series.
    (layout.shapes || []).forEach((shape,i)=>visit(shape,'shapes['+i+']',null));
    return result;
  }
  function mapColor(value) {
    const css = getComputedStyle(root);
    const one = c => {
      const i = typeof c === 'string' ? darkPalette.indexOf(c.toUpperCase()) : -1;
      return i < 0 ? c : css.getPropertyValue('--ep-ep-muted-pastel-'+i).trim() || c;
    };
    return Array.isArray(value) ? value.map(one) : one(value);
  }
  function assignPath(obj, path, value) {
    const keys = path.replace(/\[(\d+)\]/g,'.$1').split('.');
    let target = obj;
    for (let i=0;i<keys.length-1;i++) {
      const k=keys[i];
      if (!target[k] || typeof target[k] !== 'object') target[k]={};
      target=target[k];
    }
    target[keys[keys.length-1]]=value;
  }
  function newPlot(id, data, layout, config) {
    const graph = typeof id === 'string' ? document.getElementById(id) : id;
    const bindings = colorBindings(data,layout);
    originalColors.set(graph,bindings);
    for (const b of bindings) assignPath(b.index===null?layout:data[b.index], b.key, mapColor(b.value));
    for (const [key,value] of Object.entries(layoutUpdate(layout))) assignPath(layout,key,value);
    pendingGraphs.add(graph);
    return Plotly.newPlot(graph,data,layout,window.EPPlotlyI18n?.configure(graph,config) ?? config).then(g=>{observeControls(g);syncSelectedOptions(g);return g;}).finally(()=>pendingGraphs.delete(graph));
  }
  async function styleGraph(graph) {
    if (!graph.layout || !graph.data || pendingGraphs.has(graph)) return;
    const update = layoutUpdate(graph.layout);
    for (const b of originalColors.get(graph) || []) {
      if (b.index===null) update[b.key]=mapColor(b.value);
      else await Plotly.restyle(graph,{[b.key]:[mapColor(b.value)]},[b.index]);
    }
    await Plotly.relayout(graph, update);
    observeControls(graph);
    syncSelectedOptions(graph);
  }

  let queue = Promise.resolve();

  function refresh() {
    if (!window.Plotly) return;

    queue = queue.catch(() => {}).then(async () => {
      for (const graph of document.querySelectorAll('.plotly-graph-div')) {
        try {
          await styleGraph(graph);
        } catch (error) {
          console.error('EP Plotly theme:', graph.id, error);
        }
      }
    });

    return queue;
  }

  document.addEventListener('ep:themechange', refresh);
  document.addEventListener('ep:languagechange', refresh);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', refresh);
  } else {
    refresh();
  }

  window.EPPlotlyTheme = Object.freeze({refresh,newPlot});
})();
