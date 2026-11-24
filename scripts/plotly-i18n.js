/* EP Brand — reusable Plotly localization adapter. */
(function () {
  'use strict';

  let queue = Promise.resolve();

  function currentLocale() {
    return document.documentElement.lang === 'pt-BR' ? 'pt-BR' : 'en';
  }

  async function translate(locale) {
    if (!window.Plotly) return;

    const elements = document.querySelectorAll(
      'script[type="application/json"][data-ep-plotly-i18n]'
    );

    for (const element of elements) {
      const specification = JSON.parse(element.textContent);
      const graph = document.getElementById(specification.id);

      if (!graph || !graph.data || !graph.layout) continue;

      const translation = specification.locales[locale];
      if (!translation) continue;

      const heading = document.getElementById(
        specification.id + '-heading'
      );

      if (heading && typeof translation.heading === 'string') {
        heading.textContent = translation.heading;
      }

      // Update textual layout properties without replacing the figure.
      if (translation.layout) {
        await Plotly.relayout(graph, translation.layout);
      }

      // Update only explicitly supplied trace presentation attributes.
      for (const trace of translation.traces || []) {
        await Plotly.restyle(graph, trace.update, [trace.index]);
      }
    }
  }

  function apply(locale = currentLocale()) {
    queue = queue.catch(() => {}).then(() => translate(locale));
    return queue;
  }

  function refresh() {
    apply().catch(error => {
      console.error('EP Plotly localization:', error);
    });
  }

  document.addEventListener('ep:languagechange', refresh);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', refresh);
  } else {
    refresh();
  }

  window.EPPlotlyI18n = Object.freeze({apply});
})();
