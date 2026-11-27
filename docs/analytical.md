# Analytical components

Optional primitives for report content; no imposed report grid, data processing, chart engine or builder. Import `components/web/analytical.html` with the canonical Jinja environment. Use the shared resource manifest. A project can also supply ordinary semantic HTML directly. Do not duplicate the shared CSS in project content.

| Macro | Contract |
|---|---|
| `surface()` | Jinja call block, optional surface for arbitrary content; same 22px padding, 16px radius, border and shadow as All Projects. The catalogue alone adds its interactive hover. |
| `grid(columns=2)` | Call block, one, two or three equal columns; 3 becomes 2 at 1050px, 2/3 become 1 at 650px. |
| `metrics(items, compact=false)` | List of `{value,label}`; use preformatted invariant values or localized message references for both fields. Empty list omitted. Two columns, single column on narrow screens except compact Selected Projects, whose existing two-column composition is preserved. |
| `divider()` | Semantic horizontal rule using the shared border token. |
| `prose()` | Call block for paragraphs, lists and other semantic text. |
| `callout(title=none)` | Aside call block with optional shared minor heading. Neutral emphasis, not an automatically inferred validation status. |
| `figure(caption=none)` | Call block for a plot or other figure with optional localized caption. Plot and application code/data remain consumer-owned; no automatic resizing or theme adapter here. |
| `image_figure(image, caption=none)` | Static figure with required `src`, `alt`, optional paired `light`/`dark` or `en_src`/`pt_br_src`. The central asset service switches variants. |
| `data_table(caption, columns, rows)` | Required descriptive localized caption, columns `{label,numeric?,row_header?}`, rows ordered lists with exactly one value per column. Values are escaped text or localized message references; numeric fields are already formatted by consumer. Optional first column as row header; native table with keyboard-focusable horizontal scroll region. No client sorting or pagination. Empty columns omit the table. |

The All Projects catalogue consumes `ui-grid ui-grid--three` and `ui-surface` directly; Selected Projects consumes `metrics(...,true)`. These primitives preserve the current approved canonical geometry derived from the Selected Projects and All Projects studies. Analytical surfaces do not inherit catalogue hover motion. Figures, tables and prose may be used without a surface; interactive applications can use a surface or free composition. Reuse `interactive.evidence()` for image evidence playback, Navigation for links and Buttons for actions. Do not add separate chart/table/application cards, per-project palettes, independent preference state or duplicate Evidence controls. Plotly integration is deferred to 7F. Conclusion and References are deferred to 7E.

Supply translated content through the existing presentation dictionary and `message(key)`. Do not use fixture numbers as project results. Table values and units, captions, figure alt text, accessible controls and plot behavior are the consumer's responsibility. An empty table body is valid only when the consumer intentionally supplies headers without observations; provide explanatory text in the surrounding content when applicable.

Verification: `python tests/test_analytical.py` and `python tests/test_interactive.py`. Browser fixtures use synthetic evidence and require the canonical fonts. Test both themes, language change, table semantics and contained overflow, shared metric/card geometry, responsive columns and no-JavaScript fallback. This is technical validation, not integrated visual acceptance or publication.
