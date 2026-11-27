# Shared build-time validation

`tools/validation.py` provides the shared build-time validation contract. It uses only the Python standard library and has no dependency on the catalog, presentation, resources or builder modules.

| API | Contract |
|---|---|
| `require(condition, message)` | Raise `ValueError` if a condition fails. |
| `read_json(path)` | Read UTF-8 JSON; reject duplicate object keys at any depth and the nonstandard constants `NaN`, `Infinity` and `-Infinity`. |
| `fields(value, expected, label)` | Require a dictionary with exactly the expected keys. |
| `LOCALES`, `localized(value, label)` | Declare supported build-time locales (`en`, `pt-BR`); validate nonempty bilingual strings with exactly these keys. |
| `local_file(root, value)` | Resolve an existing regular file inside a caller-supplied trusted root; reject unsafe relative paths and symlink components below that root. |

The original catalog validation rules are preserved. Domain-specific schemas, technology identities, message arguments, route syntax, output paths and artifact authorization remain with their respective owners. This helper is not a complete filesystem sandbox and does not authorize publication or implement URL validation. It does not select a repository root or manage runtime preferences.

The catalog, builder, resources, presentation, badge catalog, badge renderer and Plotly presentation services import the common functions directly. Production configuration readers use `read_json`; presentation still owns inert JSON serialization. Resource selection no longer imports the project catalog or the presentation engine. Repository-relative roots are resolved by the respective service rather than obtained from an unrelated domain module. Do not add compatibility wrappers or unrelated general-purpose helpers.

Run `python -B tests/test_validation.py` and `python -B tests/support.py` in the existing test environment. The full regression covers domain contracts and existing components. Valid canonical input must produce unchanged build artifacts; schema errors must fail explicitly.
