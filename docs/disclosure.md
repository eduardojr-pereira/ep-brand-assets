# Shared disclosure and search

`components/web/disclosure.html`, `styles/disclosure.css` and `scripts/disclosure.js` own indexed native disclosure rows, Search-to-X artwork, and the reusable search control. They do not own consumer selection, search data, result rendering, or locale/theme preferences.

`indexed_item(number,label,opened=false)` accepts trusted Jinja caller content. Native details remain independently expandable. `search_control(id,label,close_label,placeholder,color_token='--ui-color-accent')` receives static bilingual message references and a canonical color token. It emits bubbling `ui:searchchange` with `{query}` on input and when explicitly closed (Escape or toggle). The control owns expansion, focus, clear and accessible labels; consumers filter their own data without reinitializing on locale change. Search is unavailable without JavaScript, while native details and content remain accessible.

`toggle_art()` and `UI.disclosure.toggleArt(art,active,animate=true,colorToken='--ui-color-accent')` expose the shared artwork independently of the search field. `UI.disclosure.matches(text,query)` performs accent/case-insensitive all-words matching; `search_text` in presentation prepares bilingual metadata. The asset service owns loading and caching. About integration remains a later consumer, not a dependency here.

See [report sections](report-sections.md) for artifact-specific behavior and `tests/test_report_sections.py` for shared and consumer regression coverage.
