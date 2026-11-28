# Static builder contract

## Ownership

`tools/builder.py` is the single orchestrator: it consumes the validated registry from [catalog.py](../tools/catalog.py), an explicit page plan, and the canonical [presentation services](presentation.md). `tools/routing.py` resolves relative routes and validates generated document IDs and local destinations. `tools/resources.py` owns the runtime allowlist, CSS asset dependencies and the single copy of canonical resources. Templates under `templates/` extend `base.html`; `landing.html` and `report.html` consume existing shell macros. The base template supports plain documents and a minimal bilingual section composition. The [generic report contract](report-content.md) adds the trusted project content slot, declared charts and explicit resources; it does not approve individual consumer layouts.

The builder and resource service consume [validation.py](validation.md) directly for shared validation; the resource service does not depend on the project catalog or presentation engine. Domain schema and URL policies remain with their owners.

## Input and output

The `--source` directory contains the [catalog contract](catalog.md). `--plan` is an explicitly supplied UTF-8 JSON file. It is not inferred from the source tree. Schema v1:

- Root: `schema_version: 1`, `legal` with `privacy` and `terms` (distinct declared plain-page routes), and ordered `pages`.
- Each page has exactly `route`, `kind`, `project`, `title`, `sections`. Routes are relative `.html` paths without traversal, reserved `shared/`, queries or absolute URLs. One landing at `index.html` is required. Kinds: `landing`, `report`, `plain`. A report identifies one registered project via `project` and sets `title` to null (title comes from its metadata); other pages set `project` to null and provide bilingual `title`.
- Each section has exactly `id`, `title`, `paragraphs`. IDs are unique per page, with `top` reserved for the report shell. Landing sections follow the canonical navigation IDs and order, and their titles are null (labels come from navigation). Other sections supply bilingual titles. Paragraphs are a list of objects with exactly `en` and `pt-BR` nonempty strings. Text is escaped, not arbitrary executable HTML. Content bindings use the presentation service.
- No default legal text or report route is fabricated. The tests use synthetic plain documents solely to exercise the routing contract. A real report uses project metadata schema v2 and `sections: []` in the plan. Its section order, body, translations and explicitly declared assets come from the [report consumer contract](report-content.md). A registry entry is not permission to publish notebooks, source, datasets, or outputs. Only reviewed files explicitly declared by a real report are eligible for copying; test content and production legal content are distinct.

The builder rejects page file/directory collisions before rendering and validates routes, section IDs, all static bindings, local `href`/`src`/image-variant references, fragments and duplicate document IDs. External HTTPS/mailto anchor destinations are allowed, not fetched. The static routing contract also validates local `poster` and `cite` references and same-document `xlink:href` SVG fragments. Duplicate attributes, base elements, active embedded documents, meta refresh and unsupported destination mechanisms (including `srcset`, `ping` and explicit form actions) are rejected; new mechanisms require an explicit consumer contract. This check is not an HTML sanitizer or MIME/content audit; trusted templates, escaped content and authorized assets remain required. CSS dependencies remain the resource service's responsibility. Canonical runtime assets are staged in one `shared/` tree: manifest CSS/JS, pinned Lottie resources and notices, Plotly locale and notice, CSS font dependencies and notices, favicon/logo (paths owned by `resources.shell_images`) and relevant repository license files, including `THIRD-PARTY-NOTICES.md` and `docs/LICENSE-SCIENTIFIC-COLOUR-MAPS.txt`. These notices accompany the technical artifact; their presence does not clear outstanding third-party artwork or trademark rights for publication. Resource copying preflights all destinations and rejects symbolic links in the output path, destination parents or destination files before any copy. Source artwork and inactive or unrequested badges, Python code and configs are not copied. Consumer resources are copied only from explicit Landing/report declarations; source templates and chart input specifications are build-only. No external runtime fetch is introduced.

Output must be a new isolated directory outside both source repositories; the parent must already exist. A temporary sibling is used and moved only after validation. Existing outputs are never overwritten. The builder creates `.nojekyll` but does not create a workflow or publish. Same version and inputs produce identical file contents; timestamps are not a reproducibility guarantee.

## Complete-site structural gate

Use `--complete-site` for an integrated candidate. The existing explicit plan schema remains unchanged. The builder requires consumer landing content, one report for every registered project at its canonical `<project>/reports/index.html` route, and the two canonical legal routes. Each report must use the v2 content-slot contract, not the v1 technical text fixture. Declared report links in landing cards are resolved from the plan and validated as local destinations. Absolute HTTPS anchors inside the institutional website prefix are checked against the same generated artifact, including fragments. Partial technical previews remain supported, but are not deployable release candidates. This gate establishes structural coverage only: real analytical content, legal approval, form transport, artwork rights, historical-route disposition, browser acceptance, and Git authorization remain separate release requirements. Do not treat test fixtures as publishable pages.

## Immutable consumption

Local checkouts, plans and generated artifacts used for temporary work belong under `~/Downloads`. The caller pins the full EP Brand Git SHA and verifies the checkout before invoking the builder. The builder does not clone, checkout, install dependencies or perform Git operations. For example, with `EP_REF` set to an approved full 40-character commit and `SOURCE`, `PLAN`, `OUTPUT` set explicitly:

```bash
checkout="$HOME/Downloads/ep-brand-build-$EP_REF"
git clone --no-checkout https://github.com/eduardojr-pereira/ep-brand-assets.git "$checkout"
git -C "$checkout" checkout --detach "$EP_REF"
test "$(git -C "$checkout" rev-parse HEAD)" = "$EP_REF"
test -z "$(git -C "$checkout" status --porcelain)"
python3 -m venv "$HOME/Downloads/ep-brand-build-env"
"$HOME/Downloads/ep-brand-build-env/bin/python" -m pip install -r "$checkout/requirements.txt"
"$HOME/Downloads/ep-brand-build-env/bin/python" -m pip check
"$HOME/Downloads/ep-brand-build-env/bin/python" -B "$checkout/tools/builder.py" --source "$SOURCE" --plan "$PLAN" --output "$OUTPUT"
```

Do not consume mutable branches at build time. Do not create a permanent library copy inside the consumer. A production workflow and its fixed SHA will be established only in the publication stage. Local technical test output is not publication or visual acceptance.

## Validation

From EP Brand, run `python -B tests/test_routing.py`, `python -B tests/test_resources.py` and `python -B tests/test_builder.py`. Tests use temporary fixtures under Downloads and actual canonical resources when run in the repository. The existing architecture checks enforce `Responsibility:` and `Boundaries:`. Full browser regression uses the separate `requirements-test.txt` environment; integrated build review and release approval are distinct steps. The Python package pins do not fix the OS, browser binary or wheel hashes.
