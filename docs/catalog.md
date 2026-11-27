# Project catalog and metadata

## Ownership

`config/projects.json` in the consumer is schema v2: an ordered list of `{path, featured}` records. The path identifies the collection and project; there is no duplicate category or slug field. The registry is the sole membership and featured-order input. No implicit directory discovery.

Each registered project has `project.json` (schema v1): bilingual `name`, `description`, topic entries (`id`, bilingual `label`), canonical technology IDs, bilingual `documentation` paths and optional `notebook` (null when absent). Existing English titles/descriptions are preserved verbatim. The project owns these metadata, not EP Brand. Technology definitions and ordering belong to `config/badges.json` and `tools/badge_catalog.py`; no duplicate visual metadata. Repeated topic IDs must have identical labels. `en` and `pt-BR` are both mandatory. Documentation and notebook paths are relative to the project and identify existing files; a reference is not authorization to publish its contents.

`tools/catalog.py` validates the two schemas, registered paths, JSON uniqueness, locale parity, canonical technology IDs and file references. Generic JSON, field, bilingual value and local-file validation are supplied by [validation.py](validation.md); project schemas and registry policy stay in the catalog. It returns ordered validated records to the [builder](builder.md). Unknown fields, duplicates, traversal and symlinks are rejected. It does not choose public routes, copy assets, render pages or execute analytical code. The structural builder and routing module already validate declared page routes and report section navigation. Real report composition and explicit publishable artifact lists remain project migration tasks; do not invent paths to absent reports.

Build dependencies are pinned in root `requirements.txt`; `requirements-test.txt` includes those pins and the additional browser-test packages. Chromium remains a separate system dependency. Version-pinned consumption and the explicit page plan are documented in [the builder contract](builder.md), not in the registry. Consumer-specific content and deployment remain pending.

## Validation

Run `python3 -B tests/test_catalog.py` from EP Brand (isolated fixtures in `~/Downloads`). For real metadata, call `load_projects` with the consumer root. The architectural validation in `tests/support.py` requires the first-party source header to contain `Responsibility:` and `Boundaries:` in English; JSON ownership is documented here instead of using invalid comments.
