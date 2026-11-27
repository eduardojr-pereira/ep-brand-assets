# Header and Footer

## Ownership

- `components/web/header.html` and `components/web/footer.html`: contextual composition; consume the canonical navigation, buttons, localization and social components. `config/brand.json` owns institutional URLs; `config/navigation.json` owns landing section IDs, semantic roles, order, social destinations and labels. Translations are in `config/translations.json`.
- `styles/header.css` and `styles/footer.css`: shell layout, responsive placement and editorial optical icon geometry; consume the shared foundations, [motion](motion.md), [navigation](navigation.md) and [buttons](buttons.md).
- `scripts/header.js`: moves one navigation tree between desktop and compact disclosure, measures sticky height and forwards preference commands. Global preferences follow [presentation.md](presentation.md).
- `components/web/animated_icons.html`, `styles/animated-icons.css`, `scripts/animated-icons.js`: shared link artwork, fallback, hover/focus playback intent and final-frame reduced motion. Asset loading and variants are owned by UI.assets (see [presentation.md](presentation.md)).
- `components/web/social.html` and `styles/social.css`: Follow & Connect content, shared radial fill, icon geometry and contextual contrast. The parent controls placement; no separate player or preference state.

Footer headings use the shared [editorial primitives](editorial.md); placement and spacing remain shell responsibilities.

## Usage

Load brand and navigation from the same immutable EP Brand version. The canonical landing destination is `brand.website`; `legacy_website` is historical only. Section roles home/about/portfolio resolve to IDs in `navigation.sections` through `navigation.landing_href`. Do not hardcode fragments or repeat URLs. The builder must verify actual target sections before publication.

```jinja
{% import 'components/web/header.html' as h %}
{% import 'components/web/footer.html' as f %}
{% import 'components/web/social.html' as s %}
{{ h.landing_header(brand,navigation) }}
{# Place Follow & Connect at the end of the Contact section. #}
{{ s.follow_connect(brand,navigation,'contact') }}
{{ f.footer(brand,navigation,'',logo_src,privacy_href,terms_href) }}
```

Report composition:

```jinja
{{ h.report_header(brand,navigation,sections) }}
{{ f.footer(brand,navigation,none,logo_src,privacy_href,terms_href,report=true) }}
```

`sections` contains project-local translation keys and local hash hrefs, matching `data-ui-section` IDs. For local fixtures a resolved landing URL without fragment can be supplied to both report macros; `none` selects `brand.website`. The footer logo and Header EP. resolve to the same home role as Navigation/Home. Back to Portfolio is present once in every report Header and points to the portfolio role. Back to Top targets the current `#top`, after Terms of Use, in report Footers only. Landing Footer has neither social links nor Back to Top. Report Footer places Follow & Connect below Repositories; mobile stacks its label and icons. The shared social control uses the approved monochrome radial fill, fixed white/black over the Contact artwork and theme-aware contrast in reports. Social order is LinkedIn, GitHub, Email, Discord. Social animations loop during hover/focus; editorial animations play once. Reduced motion and inactive tabs stop at the final frame.

Desktop Landing navigation preserves Home, Selected Projects, All Projects, About Me, Contact and GitHub click disclosure. Report sections are contextual. At insufficient width (including 670px and below), the same tree moves into the compact disclosure; native links remain without JS. The header measures `--ui-sticky-offset`; entry uses shared motion and does not replay for translation. The 12-column Footer retains institutional bio, Learn More, Navigation and Repositories, editorial title/description geometry and legal typography. Editorial optical scales: Home 136%, Award 100%, All Projects 95%, About Me 180%, Contact 80%. Editorial icons use theme-rest/copper-hover. `logo_src` resolves the canonical logo; legal URLs must be real destinations supplied by the builder, not placeholders. No document migration or legal content is generated here.

## Validation

Run `python3 tests/support.py` with canonical assets and the supported browser. Shell fixtures cover contextual destinations, social placement/order, desktop and compact navigation, themes/locales, native fallback and real shared Lottie playback. Local tests are technical checks only. Final visual acceptance requires integrated GitHub Pages publication.
