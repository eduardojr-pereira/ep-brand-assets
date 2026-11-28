# Generic report consumer contract (schema v2)

## Ownership

`project.json` owns metadata, ordered section IDs/labels/titles/descriptions and explicit resource declarations. `translations.json` owns the project-only locale dictionaries. `content/project_content.html` owns the composition of the report body using trusted Jinja and existing EP components. Project-specific Python may prepare evidence or JSON figure specifications before a build; the builder never imports or executes it. Project-specific browser code may implement an application in the declared content slot; it must use the canonical `UI.i18n` and `UI.theme` services and events, not redefine preference storage, navigation, component behavior or shared styles. Source analysis, datasets, notebooks and Python code remain outside the published artifact.

`tools/catalog.py` validates the project metadata and section structure. `tools/report_content.py` prepares one project context, validates its declared files, composes the trusted macro and checks rendered section order and chart identity. `tools/plotly_presentation.py` and `tools/artifact_preview.py` retain ownership of chart bindings and bounded previews. `tools/routing.py` supplies source links and local route validation; `tools/resources.py` selects shared runtime files; `tools/builder.py` orchestrates a single atomic build. The existing report shell remains the only owner of the page head, header, main and footer. No project name, collection-specific rendering rule, secondary builder or template replacement is required.

## Metadata and site plan

Keep the seven existing v1 metadata fields (`schema_version`, `name`, `description`, `topics`, `technologies`, `documentation`, `notebook`), set `schema_version` to 2 and add exactly `sections` and `report`. Example of the two new fields (synthetic data only):

```json
{
  "sections": [
    {"id":"overview","label":{"en":"Overview","pt-BR":"Visão geral"},"title":{"en":"Overview of evidence","pt-BR":"Visão geral das evidências"},"description":null},
    {"id":"results","label":{"en":"Results","pt-BR":"Resultados"},"title":{"en":"Results","pt-BR":"Resultados"},"description":null}
  ],
  "report": {
    "files": [
      {"path":"outputs/summary.csv","role":"artifact","label":"content.summary.label"}
    ],
    "charts": [
      {"id":"observations","path":"content/charts/observations.json","label":"content.chart.label","fallback":"content.chart.fallback"}
    ],
    "badges": ["mit"]
  }
}
```

`sections` is nonempty and ordered. `label` is navigation copy, `title` is heading copy, and `description` is a bilingual string pair or null. `id` is unique, lowercase and portable; `top` is reserved. `report.files`, `report.charts` and `report.badges` are explicit lists (empty is valid). Technologies are inherited from the existing metadata, not repeated in `report.badges`; additional graphical badges must be active canonical IDs. A badge declaration is not license or trademark clearance. A site-plan report entry uses `project` equal to the registered project path, `title: null`, and `sections: []`; the latter prevents a second section source. The plan owns the route, not report copy. The `--complete-site` gate rejects v1 text-only report fixtures. V1 metadata remains readable for the existing Landing and technical previews until each consumer is migrated; no legacy renderer is involved. The existing registry schema remains unchanged.

## Trusted content slot

The file is `content/project_content.html`, relative to the project. Its top-level output must be empty. Define a `content(sections, report)` macro; imports and other macros are allowed. The slot is rendered once within the canonical `<main>`; the ordered `data-ui-section` section IDs must match metadata exactly. The canonical `report_sections.section(section, level=2)` caller macro supplies a localized heading and optional description. Other section-producing canonical components (Hero, Conclusion, References) may compose their own section wrappers; use their existing APIs and keep IDs and heading semantics consistent with the metadata. Do not nest another document shell, inject inline JS/CSS or duplicate component markup. This is a trusted first-party authoring contract, not a sandbox for untrusted Jinja, JS, CSS or arbitrary uploaded data.

```jinja
{# Responsibility: Compose project-owned report content.
   Boundaries: No shared UI, page shell, or preference implementation. #}
{% import 'components/web/report_sections.html' as r %}
{% import 'components/web/plotly.html' as p %}
{% import 'components/web/localization.html' as t %}
{% macro content(sections, report) %}
  {% call r.section(sections[0], 1) %}
    <p{{ t.binding(report.description) }}>{{ t.value(report.description) }}</p>
  {% endcall %}
  {% call r.section(sections[1]) %}
    {{ p.prepared_chart(report.charts.observations) }}
    {{ r.artifact_explorer('results-files', report.artifacts) }}
  {% endcall %}
{% endmacro %}
```

The context supplies `report.title`, `report.description` (shared message-reference format), `report.technologies` (ordered canonical badges), `report.badges` (map by ID), `report.links` (repository source, optional notebook, bilingual documentation destinations from the same resolver as the Landing), `report.files` (map of declared project-relative paths to report-relative URLs), `report.artifacts` (prepared bounded previews), and `report.charts` (map by declared chart ID). Section heading/label/description values in `sections` are translation keys; call `message(...)` to obtain a reference. `translations.json` uses the existing locale-first `{"en": {"content.key": "..."}, "pt-BR": {"content.key": "..."}}` format, including existing argument/plural rules. Generated section and page keys may not be overridden. Shared messages remain in EP. Use stable data identifiers and localized display copy separately.

## Authorized files and charts

`report.files` entries have `path`, `role`, `label` (translation key or null for artifacts; null for other roles). Explicit allowlists, regular non-symlink files and portable paths are mandatory. The output preserves the project-relative directory structure; no entire directory is copied. Roles:

- `artifact`: evidence under `outputs/`; PNG/JPG/JPEG/SVG/CSV/JSON/TXT/PDF/XLSX. The canonical preview helper renders only supported bounded previews; PDF/XLSX are download fallback. The author must review formats, provenance, private data and active content before approval.
- `asset`: intentionally publishable files under `content/`; PNG/JPG/JPEG/WEBP/SVG/GIF/MP4/JSON/CSV/TXT. An application may use `report.files[...]` for a declared lexicon URL, not a guessed path. Dynamic JS fetch and CSS dependencies require explicit declarations and browser review; the static HTML link checker does not analyze arbitrary JS/CSS.
- `script` / `style`: project-specific `.js` / `.css` under `content/` only. Loaded once, in declaration order, after the canonical head resources. No inline JS/CSS, external runtime, shared style copy or independent locale/theme service. Scope app-specific selectors to its own root. This contract allows local client-side applications; it does not provide a backend or general form transport.

Chart specifications stay under `content/charts/` and are not copied to public output. Each chart entry names a JSON file with exactly `figure`, `translations`, `colors`, `palette`, `config`, matching the existing `chart_payload` adapter (see [Plotly](plotly.md)). `p.prepared_chart(spec)` composes the existing mount and canonical inert payload. Each declared chart must occur exactly once; undeclared, missing, altered and duplicate specs/mounts fail. Only pages with declared charts load the pinned Plotly bundle (the Style Guide also uses it). The bundle and shared badges appear once in the artifact. No data generation, training or figure recreation occurs inside the builder. Prepared chart data is published in the HTML by design; review all traces and hover/custom data for publishability.

## Acceptance

Run `python -B tests/test_report_content.py` and `python -B tests/test_report_content_browser.py`, along with the builder, routing, resources, catalog, validation and canonical component checks. The fixtures exercise an analytical consumer, a client-side application, and an independent consumer without editing the builder. They are not real Bike Sharing/Hangman reports or release candidates. The full build and browser checks of the actual consumers, legacy public redirect, legal text, contact transport, rights and final Git authorization remain separate. See [builder](builder.md).
