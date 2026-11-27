# Report sections

Load resources from `config/ui.json` in canonical order; use `tools/presentation.py` for shared and content message references. No report-specific preference, dictionary, or page builder is required. Every project-specific visible string must be a `message('content.…')` reference except invariant evidence (filenames, format identifiers, source data). Technical text/CSV values are displayed as authored, not machine-translated. Do not bind translation text to a parent containing controls or child markup.

## Conclusion and reusable disclosure

`report_sections.conclusion(id, items, files)` renders the shared section heading and an indexed native disclosure list. Supply nonempty `{label,body}` items; `body` is a list of localized paragraph references. Standard shared labels include `shared.conclusion.results`, `.findings`, `.limitations`, `.next_steps`. Omit missing sections. Outputs is appended only when authorized files exist. Multiple native details may remain open independently; language/theme changes never reconstruct the list. `disclosure.indexed_item(number,label,opened=false)` also supports arbitrary trusted Jinja caller content.

Reusable indexed rows, Search-to-X and search controls are documented in [disclosure](disclosure.md). The report composes these primitives; it does not own their state, event handling or styles.

## Artifact Explorer

Use `tools/artifact_preview.py:prepare_artifact(root,relative,allowed,label=None)` for each explicitly authorized file. The future builder must supply the exact allowed relative paths, trusted publication root, safe resolved local URL, and unique component IDs; it must never expose private inputs or construct URLs from query strings. No automatic folder enumeration. This helper accepts regular in-root non-symlink files only and percent-encodes the relative URL. The report does not fetch or execute arbitrary text. PNG/JPEG/SVG use image elements (SVG never inline or object); CSV uses a semantic table of up to 20 data rows and 12 columns; TXT and JSON display inert UTF-8 source. Text reads are bounded to 64 KiB and CSV cells to 300 characters. Truncated previews are identified; invalid/unsupported formats including PDF receive a localized download fallback. A browser-independent embedded PDF reader is not provided. Only authorized downloadable evidence may enter this component; the builder must ensure safe MIME types and no active documents are exposed inline. A missing image has a localized fallback. No preview generates new results or edits source data.

`artifact_explorer(id,files)` receives the prepared objects, with optional localized description (`label`). Search is bilingual for description and invariant name/format. Selecting an item updates its preview; filtering never silently replaces the selected artifact, even if hidden by the filter. Close/Escape clears the query explicitly; language/theme changes preserve selected item, query, search expansion and open details. Without JavaScript, the search control is hidden and all previews/download links are reachable via native anchors. No extra library.

## References

`references(id,sources,topics,methods)` is static, optional and uses the analytical grid/surface. `sources` accepts `{label,href,description?,licenses?,overview?}`; actual dataset license links only, optional dataset overview metrics in the shared metric format. `topics` accepts localized `{label,href}` for official Knowledge Base areas; shared text links without arrows. `methods` is a list of localized references rendered by the existing monochrome method tags. Technical References occupies full width without data sources, and all columns stack at the shared mobile breakpoint. No tabs, rotation, technology duplication or separate reproducibility block. Notebook and Documentation remain in Hero. All destinations must be validated by the builder, including KB area paths and dataset license scope.

## Verification

Run `python tests/test_report_sections.py` and `python tests/test_interactive.py` with the canonical environment. Tests cover bounded previews and path rejection, bilingual startup and state preservation, localized fallback and accessible labels, no-script access, reduced motion, mobile containment, and catalogue search regressions. The fixture uses synthetic evidence; actual content, publication URLs and visual acceptance remain integration tasks.
