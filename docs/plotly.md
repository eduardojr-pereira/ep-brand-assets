# Plotly presentation adapter

`tools/plotly_presentation.py`, `components/web/plotly.html`, `scripts/plotly.js` and `styles/plotly.css` form the optional chart adapter. The report owns its actual figure and content translations. The adapter consumes `UI.theme.current()` and `UI.i18n.current()` and listens to the existing committed state events. It never owns a preference, reads browser language, or changes analytical values.

## Integration contract

The canonical builder supports one optional, shared Plotly.js runtime per page with graphs. The Style Guide explicitly selects the pinned bundle; the actual project reports will select it during their migration. Ordinary builds without a declared chart consumer do not copy the runtime. The adapter does not fetch a CDN or introduce another runtime. Use the shared editorial headings and analytical figure/surface primitives outside the mount. Give each chart a unique ID. Example:

```python
import json
from plotly_presentation import chart_payload

spec = chart_payload(
    'demand', json.loads(fig.to_json()), local=translations,
    translations={
        'layout': {
            'title.text': 'content.chart.title',
            'xaxis.title.text': 'content.chart.axis',
            'xaxis.ticktext': ['content.work', 'content.holiday'],
            'updatemenus[0].buttons[0].label': 'content.chart.show',
        },
        'traces': [{'index': 0, 'fields': {
            'name': 'content.chart.series',
            'text': ['content.work', 'content.holiday'],
            'hovertemplate': 'content.chart.hover',
        }}],
    },
    palette='ep-muted-pastel',
    colors=[{'trace': 0, 'path': 'marker.color',
             'palette': 'ep-muted-pastel', 'index': 0}],
)
```

```jinja
{% import 'components/web/plotly.html' as p %}
{{ p.chart('demand', message('content.chart.accessible_label'), message('content.chart.fallback')) }}
{{ spec }}
```

`chart_payload` returns safely encoded inert JSON. Supply JSON-compatible figure data and layout, not an arbitrary Plotly HTML export. Animated frames need separate project integration. The runtime discovers the mount on DOM ready, global events, late external script load or an explicit `await UI.plotly.refresh()` after a dynamic mount/runtime load. Keep specs immutable for the lifetime of each mount. Initial rendering uses the already-resolved global language/theme; the fallback remains visible until a successful mount. Fixed input width is removed for responsive containers; authored height is retained.

## Translation and data identity

Use the same locale-first `content.*` dictionaries and message keys as the rest of the report. All supplied bindings must exist in both languages. `chart_payload` accepts only presentation fields, not data, ranges, filters or visibility. See `LAYOUT_TEXT` and `TRACE_TEXT` for supported fields. Axis titles, tick labels, annotations, legend titles/names, trace hover/text templates, dropdown labels, range-selector buttons and slider labels use explicit bindings. Supply every translatable field; omitted fields are invariant and will not be guessed. Plotly tokens `%{x}`, `%{text}`, `%{y:.2f}` remain untouched by the shared message formatter. Use stable category values with `tickvals`/translated `ticktext` and per-point presentation `text` with `%{text}` in hover; do not replace underlying category IDs. Pie/sunburst legends that derive labels directly from data, dynamic menu arguments carrying localized values, and animated figures need explicit project-level integration rather than rewriting data identities. Scalar fields require scalar message keys; ticktext requires an array. Array lengths are checked against declared tickvals or unambiguous flat point coordinates when available. Other dimensions require consumer validation. The project owns meaningful wording and translation coverage.

For native Plotly modebar and date/number formatting, the adapter loads the official Brazilian locale once through the canonical JSON asset cache and registers once per runtime. No per-chart locale payload. Source: JSON transcription of `plotly/plotly.js` v3.3.1, `lib/locales/pt-br.js`, upstream blob `9a85104b0627a11f7f984b2d2ecdec502c2e957d`; MIT notice at `assets/vendor/plotly/LICENSE`, upstream blob `13ffac3c942fd6f6e8af7d4e58860bb306db3e2f`. English is Plotly's built-in locale. Upstream locale coverage is limited to its dictionary; project-specific labels use the central dictionary. No second translation preference is introduced.

## Styling and updates

Institutional tokens set typography, paper/plot surfaces, grid, axes, legend, hover, controls and borders. Analytical palettes are distinct. Optional categorical `palette` sets the colorway from `config/colormaps.json`; explicit `colors` bindings resolve categorical indices or lists of indices, or continuous `colorscale` references. Preserve authored colors unless an explicit binding is supplied; do not recolor semantic categories indiscriminately. A continuous scale remains the same across themes. `colors` supports marker/line/fill paths and marker/trace colorscales. Project data semantics, redundant encoding and palette choice are authored in the report.

After initial `newPlot`, theme and text changes use `Plotly.relayout` and `Plotly.restyle` on the existing graph. Native config locale changes use `Plotly.react` with the live data/layout, not the original specification. No newPlot, purge, replacement of data arrays, or explicit resets of zoom/menu/visibility/selection occur on theme/locale changes. Work is serialized per graph and coalesced to the latest global preferences; a failure invalidates the recorded presentation state for that graph, does not block others, and can retry on a later refresh even when the user reverts to the last successful preference. The tested scope is Cartesian charts and their controls; verify every real project figure and uncommon chart type before publication.

## Validation

Run `python tests/test_plotly.py` in the existing environment with Plotly, Jinja2, Playwright and a Chromium-compatible browser. The suite loads the actual installed Plotly.js bundle after DOM ready; it covers native modebar translation, localized hover, theme palette, category identities, repeated switches, selection/zoom/menu/visibility, failure isolation, responsive width and no-JS fallback. Run `test_presentation.py` because the shared formatter now excludes native `%{...}` syntax. Validate real Bike Sharing figures, all 16 chart translations and responsive layouts after builder integration; do not claim integrated visual acceptance yet.

The shared optional runtime is `assets/vendor/plotly/plotly.min.js` (4.1.1, exact bytes from Plotly.py 7.1.0). `resource_paths(..., plotly_runtime=True)` selects it; `copy_resources` requires the same selection. Consumers must explicitly include its resolved URL. Builds without charts do not need the runtime. The guide currently selects it; real reports will select it during migration. The existing vendor MIT license matches the tagged upstream license. The adapter normalizes the pinned runtime’s modebar logo link and removes its unreferenced repeated decorative group ID after plots and redraws, without changing vendor code or branding.
