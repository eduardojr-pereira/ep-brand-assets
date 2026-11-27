# Project catalog and metadata

## Ownership

`config/projects.json` in the consumer is schema v2: an ordered list of `{path, featured}` records. The path identifies the collection and project; there is no duplicate category or slug field. The registry is the sole membership and featured-order input. No implicit directory discovery.

Each registered project has `project.json` (schema v1): bilingual `name`, `description`, topic entries (`id`, bilingual `label`), canonical technology IDs, bilingual `documentation` paths and optional `notebook` (null when absent). Existing English titles/descriptions are preserved verbatim. The project owns these metadata, not EP Brand. Technology definitions and ordering belong to `config/badges.json` and `tools/badge_catalog.py`; no duplicate visual metadata. Repeated topic IDs must have identical labels. `en` and `pt-BR` are both mandatory. Documentation and notebook paths are relative to the project and identify existing files; a reference is not authorization to publish its contents.

`tools/catalog.py` validates the two schemas, registered paths, JSON uniqueness, locale parity, canonical technology IDs and file references. It returns ordered validated records to the future builder. Unknown fields, duplicates, traversal and symlinks are rejected. It does not choose public routes, copy assets, render pages or execute analytical code. Report navigation, explicit publishable artifact lists and route resolution are reserved for the respective composition and project migration stages; do not invent paths to absent reports.

Build dependencies are declared separately in root `requirements.txt`; browser tests still require their documented dependencies and Chromium. The builder is not yet implemented. Version-pinned consumption and artifact publication are handled by the future build stage, not by the registry. The existing ignored CI checkout remains reserved until the build workflow contract is implemented.

## Validation

Run `python3 -B tests/test_catalog.py` from EP Brand (isolated fixtures in `~/Downloads`). For real metadata, call `load_projects` with the consumer root. The architectural validation in `tests/support.py` requires the first-party source header to contain `Responsibility:` and `Boundaries:` in English; JSON ownership is documented here instead of using invalid comments.
