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

  async function styleGraph(graph) {
    if (!graph.layout || !graph.data) return;

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

    for (const [key, axis] of Object.entries(graph.layout)) {
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

    (graph.layout.updatemenus || []).forEach((menu, i) => {
      const key = `updatemenus[${i}]`;

      update[key + '.bgcolor'] = t.surface;
      update[key + '.bordercolor'] = t.border;
      update[key + '.font.color'] = t.text;
    });

    await Plotly.relayout(graph, update);
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

  window.EPPlotlyTheme = Object.freeze({refresh});
})();
