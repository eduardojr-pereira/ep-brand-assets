/* EP Brand — reusable Plotly localization adapter. */
(function () {
  'use strict';

  let queue = Promise.resolve();

  // Native Plotly locale for the EP reports; deliberately independent of project data.
  const nativePt = {
    moduleType: 'locale', name: 'pt-BR',
    dictionary: {
      'Download plot as a PNG': 'Baixar gráfico como PNG',
      'Share chart...': 'Compartilhar gráfico...',
      'Pan': 'Mover', 'Zoom in': 'Ampliar', 'Zoom out': 'Reduzir',
      'Autoscale': 'Escala automática', 'Reset axes': 'Restaurar eixos',
      'Box Select': 'Seleção retangular', 'Lasso Select': 'Seleção livre',
      'Toggle Spike Lines': 'Alternar linhas de referência',
      'Show closest data on hover': 'Mostrar dado mais próximo ao passar o cursor',
      'Compare data on hover': 'Comparar dados ao passar o cursor'
    },
    format: {
      days: ['domingo','segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado'],
      shortDays: ['dom','seg','ter','qua','qui','sex','sáb'],
      months: ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'],
      shortMonths: ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'],
      periods: ['AM','PM'], dateTime: '%d/%m/%Y %H:%M:%S',
      date: '%d/%m/%Y', time: '%H:%M:%S', decimal: ',', thousands: '.',
      grouping: [3], currency: ['R$ ', ''], year: '%Y', month: '%b %Y',
      dayMonth: '%-d %b', dayMonthYear: '%-d %b %Y'
    }
  };
  const configs = new WeakMap();
  let registeredPlotly;

  function nativeLocale(locale) {
    if (registeredPlotly !== window.Plotly) {
      Plotly.register(nativePt);
      registeredPlotly = window.Plotly;
    }
    return locale === 'pt-BR' ? 'pt-BR' : 'en-US';
  }

  function configure(graph, config) {
    configs.set(graph, {...config});
    return {...config, locale: nativeLocale(currentLocale())};
  }


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

      // Preserve all original config options as well as the live layout and trace state.
      const config = configs.get(graph);
      const targetLocale = nativeLocale(locale);
      if (config && graph._context.locale !== targetLocale) {
        await Plotly.react(graph, graph.data, graph.layout, {...config, locale: targetLocale});
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

  window.EPPlotlyI18n = Object.freeze({apply, configure});
})();
