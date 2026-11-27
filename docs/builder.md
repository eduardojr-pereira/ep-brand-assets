# Static builder contract

## Ownership

`tools/builder.py` is the single orchestrator: it consumes the validated registry from [catalog.py](../tools/catalog.py), an explicit page plan, and the canonical [presentation services](presentation.md). `tools/routing.py` resolves relative routes and validates generated document IDs and local destinations. `tools/resources.py` owns the runtime allowlist, CSS asset dependencies and the single copy of canonical resources. Templates under `templates/` extend `base.html`; `landing.html` and `report.html` consume existing shell macros. The base template supports plain documents and a minimal bilingual section composition. This is technical infrastructure, not the approved final Landing Page or project reports.

The builder and resource service consume [validation.py](validation.md) directly for shared validation; the resource service does not depend on the project catalog or presentation engine. Domain schema and URL policies remain with their owners.

## Input and output

The `--source` directory contains the [catalog contract](catalog.md). `--plan` is an explicitly supplied UTF-8 JSON file. It is not inferred from the source tree. Schema v1:

- Root: `schema_version: 1`, `legal` with `privacy` and `terms` (distinct declared plain-page routes), and ordered `pages`.
- Each page has exactly `route`, `kind`, `project`, `title`, `sections`. Routes are relative `.html` paths without traversal, reserved `shared/`, queries or absolute URLs. One landing at `index.html` is required. Kinds: `landing`, `report`, `plain`. A report identifies one registered project via `project` and sets `title` to null (title comes from its metadata); other pages set `project` to null and provide bilingual `title`.
- Each section has exactly `id`, `title`, `paragraphs`. IDs are unique per page, with `top` reserved for the report shell. Landing sections follow the canonical navigation IDs and order, and their titles are null (labels come from navigation). Other sections supply bilingual titles. Paragraphs are a list of objects with exactly `en` and `pt-BR` nonempty strings. Text is escaped, not arbitrary executable HTML. Content bindings use the presentation service.
- No default legal text or report route is fabricated. The tests use synthetic plain documents solely to exercise the routing contract. Production legal content, landing composition and report artifact declarations remain separate authorized work. A registry entry is not permission to publish notebooks, source, datasets, or outputs. No project files are copied by this version.

The builder rejects page file/directory collisions before rendering and validates routes, section IDs, all static bindings, local `href`/`src`/image-variant references, fragments and duplicate document IDs. External HTTPS/mailto anchor destinations are allowed, not fetched. Canonical runtime assets are staged in one `shared/` tree: manifest CSS/JS, pinned Lottie resources and notices, Plotly locale and notice, CSS font dependencies and notices, favicon/logo (paths owned by `resources.shell_images`) and relevant repository license files. Resource copying preflights all destinations and rejects symbolic links in the output path, destination parents or destination files before any copy. Source artwork and inactive or unrequested badges, Python code, configs, and project files are not copied. New consumer-specific resources require an explicit contract in the relevant migration stage. No external runtime fetch is introduced.

Output must be a new isolated directory outside both source repositories; the parent must already exist. A temporary sibling is used and moved only after validation. Existing outputs are never overwritten. The builder creates `.nojekyll` but does not create a workflow or publish. Same version and inputs produce identical file contents; timestamps are not a reproducibility guarantee.

## Immutable consumption

Local checkouts, plans and generated artifacts used for temporary work belong under `~/Downloads`. The caller pins the full EP Brand Git SHA and verifies the checkout before invoking the builder. The builder does not clone, checkout, install dependencies or perform Git operations. For example, with `EP_REF` set to an approved full 40-character commit and `SOURCE`, `PLAN`, `OUTPUT` set explicitly:

```bash
checkout="$HOME/Downloads/ep-brand-build-$EP_REF"
git clone --no-checkout https://github.com/eduardojr-pereira/ep-brand-assets.git "$checkout"
git -C "$checkout" checkout --detach "$EP_REF"
test "$(git -C "$checkout" rev-parse HEAD)" = "$EP_REF"
test -z "$(git -C "$checkout" status --porcelain)"
python -m pip install -r "$checkout/requirements.txt"
python -B "$checkout/tools/builder.py" --source "$SOURCE" --plan "$PLAN" --output "$OUTPUT"
```

Do not consume mutable branches at build time. Do not create a permanent library copy inside the consumer. A production workflow and its fixed SHA will be established only in the publication stage. Local technical test output is not publication or visual acceptance.

## Validation

From EP Brand, run `python -B tests/test_routing.py`, `python -B tests/test_resources.py` and `python -B tests/test_builder.py`. Tests use temporary fixtures under Downloads and actual canonical resources when run in the repository. The existing architecture checks enforce `Responsibility:` and `Boundaries:`. Full browser regression, integrated build review and release approval are distinct steps.
