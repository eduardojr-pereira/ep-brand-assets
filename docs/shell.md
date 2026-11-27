# Header and Footer

## Ownership

- `components/web/header.html` and `components/web/footer.html`: structure and composition only; consume `navigation.html`, `buttons.html` and `localization.html`. Shared navigation destinations and semantic labels are in `config/navigation.json`; institutional URLs are in `config/brand.json`; translations are in `config/translations.json`.
- `styles/header.css` and `styles/footer.css`: component layout, responsive placement, optical icon geometry and surface presentation. Consume the shared foundations, [motion](motion.md), [links and navigation](navigation.md), and [buttons](buttons.md).
- `scripts/header.js`: move a single navigation tree between desktop and compact disclosure, measure sticky height and forward preference commands. Navigation behavior follows [navigation.md](navigation.md); global preferences and translation bindings follow [presentation.md](presentation.md).
- `scripts/footer.js`: hover/focus playback intent and frame positioning for footer artwork. Reduced motion shows the final frame. Asset loading, lifecycle, variants and fallback follow [presentation.md](presentation.md).

## Usage

The builder will load `brand.json` and `navigation.json` from the same immutable EP Brand version and pass them to the templates, along with project-specific section references. Example (Jinja):

```jinja
{% import 'components/web/header.html' as h %}
{% import 'components/web/footer.html' as f %}
{{ h.landing_header(brand,navigation) }}
{{ f.footer(brand,navigation,landing_url,logo_src,privacy_href,terms_href,year=2026) }}
```

For reports, call `h.header(brand,navigation,sections,home_href,back_href)`. Each section has `label` (a shared or content translation key) and `href` (a local hash); sections on the page have matching IDs and `data-ui-section`. The header measures `--ui-sticky-offset`. `back_href` is the single link back to the portfolio's all-projects section. `landing_url` is empty on the landing page and the resolved portfolio URL/path in reports; it must not contain a fragment. `logo_src` must resolve the canonical `assets/logos/logo_initials.png` from the same version, and `privacy_href`/`terms_href` must point to the real published destinations. No placeholder legal content, transport or page-builder logic is introduced here. The builder must validate required destinations before publication.

Desktop header: Home, Selected Projects, All Projects, About Me, Contact and GitHub (click disclosure). Report sections are supplied by the consumer. The compact trigger is text-only, and the exact same links are moved into the native disclosure when width is insufficient or at 670px and below. A nested GitHub menu reuses canonical disclosure behavior. The report return link stays visible. No JavaScript leaves native links available. The header entrance uses the shared motion primitive and never replays just for translation.

Footer: 12-column layout, institutional bio and radial Learn More, editorial navigation and repositories, social links, legal links and persistent-underlined Back to Top. Titles and descriptions remain in one aligned content block. The approved optical scales for navigation Lotties are Home 136%, Award 100%, All Projects 95%, About Me 180%, Contact 80%. Footer artwork uses theme-rest and copper-hover variants. Social labels and icons stack at narrow widths; all legal text shares the copyright font size. The logo, copy, destinations and artwork must be verified in the integrated page. The legacy Markdown footers are independent and unchanged.

## Validation

`python3 tests/support.py` runs previous suites and `test_shell.py`: light/dark desktop, language/theme controls, active scroll section, nested disclosure/Escape, compact Landing and report layouts, resize and unique link tree, footer editorial geometry, legal destinations, real Lottie SVG and optical scales, one runtime, reduced motion, and no-JS links. Browser fixtures are not production pages. Visual acceptance is reserved for the actual GitHub Pages deployment.
