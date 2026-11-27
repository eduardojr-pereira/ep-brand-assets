# Themes, internationalization and shared assets

## Ownership and loading contract

| Owner | Responsibility |
|---|---|
| `styles/foundations.css` | Semantic palette and typography, no preference state. |
| `scripts/theme.js` | One theme preference, early application, persistence, event. |
| `scripts/i18n.js` | One locale preference, message lookup, plural/number formatting, text and attribute bindings, event. |
| `config/translations.json` | Shared EN/PT-BR messages. |
| `components/web/localization.html` | Declarative Jinja binding primitives, no local dictionaries. |
| `scripts/assets.js` | Canonical URL resolution, source/player cache, Lottie lifecycle and visual variants. |
| `tools/presentation.py` | Validated message references, page configuration and head resource tags for the builder/tests. |
| `config/ui.json` | Dependency order and pinned animation runtime/asset registry. |

`head_resources(resource_base, local)` emits configuration and synchronous theme/i18n/motion scripts before the styles, then the deferred component scripts. The resource base must refer to a single version of the canonical library (e.g. `./` or `../`). It is supplied by the [builder](builder.md); do not hardcode a mutable `main` URL. `brand.json` owns the relative `asset_root`. The helper does not build a page or copy assets. `static_message` validates argument-free message references in both languages; `inert_json` safely serializes script data for the page configuration and chart specifications. No publication mechanism is established by this lot.

The locale precedence is an explicit stored choice (`ui.locale`), first supported browser locale (en or pt mapped to en/PT-BR), then English. The theme precedence is an explicit stored choice (`ui.theme`), then system preference. On unavailable storage both controllers remain usable in memory. The browser's initial language is set before the body; a non-English initial page conceals the untranslated fallback until synchronous translation at DOMContentLoaded, without an arbitrary timeout. Without JavaScript the English HTML and its default theme remain visible. Theme and language storage are shared by pages on the same origin. Other origins do not share storage. `UI.theme.set('light'|'dark')` and `UI.i18n.set('en'|'pt-BR')` are the only setters; `current()` reads each state. The events `ui:themechange` and `ui:languagechange` are emitted after application, and components do not dispatch them themselves.

Build-time JSON configuration is read through [validation.py](validation.md), which also declares the supported build-time locale identifiers. Message-key ownership, argument parity, inert serialization and Jinja bindings remain presentation responsibilities.

## Translation references

`environment(local)` validates keys, locale parity and message arguments, then exposes `message(key)` to Jinja. Shared keys use `shared.*`; local keys use `content.*` and cannot override shared strings. Supply local translations in the same locale-first JSON structure as `config/translations.json`. The builder supplies page-specific dictionaries at generation and calls `validate_bindings(html, local)` before writing each rendered document. Static binding keys must exist and require no runtime arguments. The runtime resolves all bindings against the candidate locale before committing any text, preference or event; invalid changes leave the previous state intact. Catalogue search metadata uses the same bilingual dictionary at render time. Literal strings passed to macros are invariant data (e.g. Python, a project name unchanged across locales); use `message(key)` for any translated content. Example:

```jinja
{% import 'components/web/navigation.html' as n %}
{{ n.diagonal(message('shared.project.view'), project.href) }}
```

A macro writes the English fallback and `data-i18n-text`, `data-i18n-aria-label`, `data-i18n-placeholder`, `data-i18n-alt` or `data-i18n-title` using the common binding helper. Bind text only on leaf nodes, not wrappers containing icons or controls. No translated HTML strings or `innerHTML` are used. Runtime `UI.i18n.bind(node,target,key,args)` updates dynamic bindings; `bindFrom` transfers an existing message binding or invariant literal; `clear` removes it. Catalog counts use one complete plural message with numeric arguments; zero is plural. Send state binds the corresponding message, not a second dictionary. Changes keep current filter identifiers, query, slide, playback intent, and submission state. Marquee clones are decorative copies without translation bindings. Native Plotly `%{...}` tokens are preserved by the message formatter; [the optional chart adapter](plotly.md) consumes the same dictionary. Hero/game behavior and actual chart content require integration in their own lots; no claim of integrated visual acceptance.

## Shared assets and Lottie

`UI.assets.url(relativePath)` resolves canonical assets from the configured base, rejecting traversal and absolute paths. A consumer must supply project-specific figure URLs, not add them to the brand registry. The loader consumes one registry in `config/ui.json`, downloads each JSON once per page, clones source data before any recolor, and lazily loads one local, pinned runtime. `UI.assets.mount(host,{id,variant:'theme',colorToken,onReady})` mounts an animation; the caller owns interaction and frame semantics. `get(host)` returns the ready player, `unmount(host)` disposes it. Theme changes remount themed or recolored assets, stale asynchronous loads cannot replace a newer mount, and disconnected hosts are disposed. Retained Lotties use the registered graphite/white/copper variants; no source assets were changed. Checkbox frame semantics remain in Navigation (selected hold 44–85, select 0–44, deselect 85–119). Static fallback is preserved if the player or data is unavailable. Do not load untrusted animation JSON.

Runtime: Lottie-web 5.12.2, upstream `airbnb/lottie-web` commit `846dbf2a5c40df245db4307490cecae02b9dcca4`; `build/player/lottie.min.js` and `LICENSE.md` are stored verbatim in `assets/vendor/lottie/`, with their upstream Git blob hashes in the manifest. The original MIT notice is preserved. The installer verifies both before writing. No runtime CDN fetch or additional copy per component. Future build consumers must publish the canonical asset paths from the same version. Other original visual assets and licenses are unchanged.

`components/web/assets.html:image_variants` owns the shared image attributes for figures, badges and Evidence. Images can declare light/dark or EN/PT-BR source pairs; `UI.assets` selects the appropriate source after global state changes. A localized pair takes precedence over a theme pair, so do not supply conflicting pairs; use an intrinsically theme-aware SVG for localized badges. The `badges(items)` macro accepts resolved pairs from the canonical catalog. Consumer-specific badge composition and integrated theme/locale visual verification remain pending. `UI.assets.json(path)` exposes the same cached JSON source loader for canonical asset files, including the optional Plotly locale; consumers must not mutate cached source objects. Failed runtime/source requests are evicted; a subsequent mount or relevant theme refresh can retry. Static fallbacks remain accessible and failures are reported to the browser console.

## Validation

Run `python3 tests/support.py` with Jinja2, Playwright, Plotly, a Chromium-compatible browser, canonical fonts and the pinned runtime. Tests use the same manifest/head helper and an intercepted same-origin fixture serving actual local files; no external network is needed after installation. The checkbox test requires the real player, not a mock; tests validate translation parity, first-render guard, language changes, dynamic states, reload persistence, theme preference and fallback. Header/Footer optical scales are covered by the local shell suite; see [Header and Footer](shell.md). Integrated visual acceptance, real contact transport, project content/Plotly and Pages publication remain pending.

For Header and Footer composition and configuration, see [Header and Footer](shell.md).
