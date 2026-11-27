<a id="readme-top"></a>

<div align="center">

| [English](./README.md) · [Português](./README.pt-BR.md) |

# EP Brand Assets

*Visual identity, shared components and presentation infrastructure for the EP ecosystem.*

</div>

<div align="center">

[Overview](#overview) · [Visual Identity](#visual-identity) · [Shared Components](#shared-components) · [Themes and Internationalization](#themes-and-internationalization) · [EP Analytical Colour System](#ep-analytical-colour-system)<br>
[Directory Structure](#directory-structure) · [Usage and Integration](#usage-and-integration) · [Testing and Validation](#testing-and-validation) · [Related Repositories](#related-repositories) · [License](#license) · [Contact](#contact)

</div>

---

<a id="overview"></a>

## Overview

EP Brand Assets is the canonical source of visual identity and shared presentation infrastructure for the EP ecosystem. It centralizes design tokens, typography, themes, bilingual interface mechanisms, visual assets, components and renderers for the interactive portfolio, project reports and professional READMEs.

Consuming projects retain their own data, analyses and project-specific content. Shared components are maintained here rather than duplicated across repositories.

---

<a id="visual-identity"></a>

## Visual Identity

The identity uses the EP logo, institutional graphite and copper palette, shared typography, social icons and Lottie animations. The institutional palette is distinct from the analytical colour system.

| Asset | Preview | File |
|---|---|---|
| EP logo | <img src="assets/logos/logo_initials.png" width="64" alt="EP logo" /> | [`logo_initials.png`](./assets/logos/logo_initials.png) |
| GitHub | <img src="assets/icons/github_icon.svg" width="26" alt="GitHub" /> | [`github_icon.svg`](./assets/icons/github_icon.svg) |
| LinkedIn | <img src="assets/icons/linkedin_icon.svg" width="26" alt="LinkedIn" /> | [`linkedin_icon.svg`](./assets/icons/linkedin_icon.svg) |
| Email | <img src="assets/icons/gmail_icon.svg" width="26" alt="Email" /> | [`gmail_icon.svg`](./assets/icons/gmail_icon.svg) |
| Discord | <img src="assets/icons/discord_icon.svg" width="26" alt="Discord" /> | [`discord_icon.svg`](./assets/icons/discord_icon.svg) |

See [animations](./assets/animations/) and [theme tokens](./styles/foundations.css).

The animation library includes the following Lottie assets for the new editorial layout:

| Animation | Application | Variants |
|---|---|---|
| Award | Selected Projects | [Graphite](./assets/animations/lottie_award_graphite.json) · [White](./assets/animations/lottie_award_white.json) · [Copper](./assets/animations/lottie_award_copper.json) |
| Search-to-X | About Me panel controls | [Graphite](./assets/animations/lottie_search_to_x_graphite.json) · [White](./assets/animations/lottie_search_to_x_white.json) · [Copper](./assets/animations/lottie_search_to_x_copper.json) |

### Badge Library

The centralized library contains 81 SVG badges: 48 technologies, 3 licenses, 6 statuses, 22 topics and 2 methods. Technologies, Licenses and Status may be used in READMEs and HTML; Topics and Methods are reserved for showcase and report HTML. See the [badge library documentation](./docs/badges.md).

> [!NOTE]
> The asset library is versioned; integration into the new architecture is still in progress. Integrated consumer validation and coordinated publication remain pending.

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="shared-components"></a>

## Shared Components

Components are maintained in EP Brand and reused where relevant. The canonical builder is still pending; the current templates are Jinja macros, not published pages.

| Component | Source |
|---|---|
| Institutional configuration | [`config/brand.json`](./config/brand.json) |
| Web components: cards, buttons, links, navigation and controls | [`components/web/`](./components/web/) |
| Bilingual Markdown footers | [`components/markdown/`](./components/markdown/) |
| Shared scripts and interactions | [`scripts/`](./scripts/) |
| Dependency order | [`config/ui.json`](./config/ui.json) |
| Shared translations | [`config/translations.json`](./config/translations.json) |
| Presentation preparation | [`tools/presentation.py`](./tools/presentation.py) |
| Regression tests | [`tests/`](./tests/) |

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="themes-and-internationalization"></a>

## Themes and Internationalization

The palette and typography are centralized in [Foundations](./styles/foundations.css). Light and dark themes are defined by CSS tokens. Shared motion tokens and generic animations live in [Motion](./styles/motion.css). Loading order is declared in [config/ui.json](./config/ui.json).

The [theme controller](./scripts/theme.js) resolves and persists a single preference. [Internationalization](./scripts/i18n.js) binds text, accessible attributes, SVG labels and dynamic messages using [shared keys](./config/translations.json) and validated local translations. The [asset loader](./scripts/assets.js) resolves paths, variants and animations from the same library version. Translation does not reset component state. See the [technical contract](./docs/presentation.md). Header, Footer, the builder and Plotly adapters are not yet part of the new architecture.

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="ep-analytical-colour-system"></a>

## EP Analytical Colour System

The EP Analytical Colour System separates visual encoding of data from institutional branding. Choose the class according to the data semantics, then the appropriate representation, contrast and redundant visual encoding.

| Class | Primary | Secondary | Specialized |
|---|---|---|---|
| Categorical | EP Muted Pastel | EP LipariS Adapted | — |
| Sequential | Nuuk | Lipari | — |
| Diverging | Vik | Delphi | Ston |
| Multi-sequential | Fes | — | — |
| Cyclic | VikO | — | — |

![Nine analytical palettes; categorical variants in both themes and seven continuous scales](./docs/colormaps-preview.svg)

> [!WARNING]
> - **Source of Truth:** The palette preview is generated directly from [config/colormaps.json](./config/colormaps.json), the canonical colour configuration.
> - **Origin and Attribution:** Continuous scales use Scientific Colour Maps 9.0.0 by Fabio Crameri. EP LipariS Adapted is a custom adaptation, not an official scale. See the [methodology and attribution](./docs/colormaps.md) and [MIT license](./docs/LICENSE-SCIENTIFIC-COLOUR-MAPS.txt).
> - **Accessibility:** Categorical palettes require complementary visual cues, such as markers, line styles, patterns or labels. Colour contrast alone does not guarantee accessibility.
> - **Technical Integration:** The future Plotly adapter will consume the canonical colour configuration. No Plotly renderer is active in this reconstruction.

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="directory-structure"></a>

## Directory Structure

```text
ep-brand-assets/
├── assets/
│   ├── animations/
│   ├── badges/
│   ├── fonts/
│   ├── icons/
│   ├── logos/
│   └── vendor/lottie/
├── components/
│   ├── markdown/
│   └── web/
│       ├── navigation.html
│       ├── buttons.html
│       ├── interactive.html
│       └── localization.html
├── config/
│   ├── badges.json
│   ├── brand.json
│   ├── colormaps.json
│   ├── translations.json
│   └── ui.json
├── docs/
├── scripts/
│   ├── theme.js
│   ├── i18n.js
│   ├── assets.js
│   ├── scroll-trigger.js
│   ├── navigation.js
│   ├── buttons.js
│   └── interactive.js
├── styles/
│   ├── foundations.css
│   ├── motion.css
│   ├── links.css
│   ├── buttons.css
│   └── interactive.css
├── tests/
│   ├── support.py
│   └── test_*.py
├── tools/
│   └── presentation.py
├── LICENSE-BRAND.md
├── LICENSE-CODE.txt
├── LICENSE-CONTENT.md
├── README.md
└── README.pt-BR.md
```

- `assets/` — Visual identity resources and fonts.
- `components/` — Markdown footers and canonical Jinja macros.
- `config/` — Institutional data, catalogues and dependency order.
- `docs/` — Technical documentation and attribution.
- `scripts/` and `styles/` — Shared behavior and presentation.
- `tests/` — Component tests with shared infrastructure.

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="usage-and-integration"></a>

## Usage and Integration

[brand.json](./config/brand.json) declares `asset_root` relative to the consumed EP Brand version. The future builder must resolve resources from the same checkout or immutable reference as the components, not a mutable branch.

The templates in `components/web/` are HTML-autoescaped Jinja macros. [`tools/presentation.py`](./tools/presentation.py) prepares the Jinja environment, message references and head resources in the order declared by `config/ui.json`. The future builder will reuse this contract; no page builder is currently active. Existing Markdown footer templates are preserved independently of the new web architecture. Do not rename shared assets without checking consumers. Local generation does not publish changes.

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="testing-and-validation"></a>

## Testing and Validation

With Python, Jinja2, Playwright and a Chromium-compatible browser installed, run from the repository root:

```bash
python3 tests/support.py
```

`UI_TEST_BROWSER` can specify the browser executable. The suite uses the dependency manifest, canonical components and the actual repository fonts. Component tests do not replace integrated visual and functional acceptance on GitHub Pages. The suite requires the real Lottie player pinned in `config/ui.json` and tests the global presentation services. Real contact transport, consumer integration and publication remain pending.

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="related-repositories"></a>

## Related Repositories

| Repository | Role |
|---|---|
| [Data Science Portfolio](https://github.com/eduardojr-pereira/data-science-portfolio) | Applied projects, interactive portfolio and project reports. |
| [Data Science Knowledge Base](https://github.com/eduardojr-pereira/data-science-knowledge-base) | Study notebooks, guides and technical reference materials. |

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="license"></a>

## License

The following terms apply only to material for which the author holds the necessary rights.

<table>
<tr><td align="center" valign="middle"><a href="./LICENSE-CODE.txt"><img src="./assets/badges/licenses/mit.svg" alt="MIT"></a></td><td valign="middle"><strong>Source code</strong> | Original scripts, components, renderers and tests.</td></tr>
<tr><td align="center" valign="middle"><a href="./LICENSE-CONTENT.md"><img src="./assets/badges/licenses/cc_by_nc_4_0.svg" alt="CC BY-NC 4.0"></a></td><td valign="middle"><strong>Documentation</strong> | Original technical and editorial content.</td></tr>
<tr><td align="center" valign="middle"><a href="./LICENSE-BRAND.md">All rights reserved</a></td><td valign="middle"><strong>EP visual identity</strong> | Original institutional brand assets; no automatic permission for reuse or redistribution.</td></tr>
<tr><td align="center" valign="middle">Third-party terms</td><td valign="middle"><strong>External assets</strong> | Original licenses and permissions remain applicable.</td></tr>
</table>

### Scientific Colour Maps — MIT License

| Item | Attribution and terms |
|---|---|
| Original work | Scientific Colour Maps 9.0.0 — Fabio Crameri |
| Copyright | Copyright (c) 2026, Fabio Crameri |
| License | [MIT — full original license text](./docs/LICENSE-SCIENTIFIC-COLOUR-MAPS.txt) |
| Reference | [DOI: 10.5281/zenodo.24343380](https://doi.org/10.5281/zenodo.24343380) |
| Official scales used | Nuuk, Lipari, Vik, Delphi, Ston, Fes and VikO |
| Derived palette | EP LipariS Adapted — an EP adaptation, not an official Scientific Colour Maps palette. |

The MIT license permits use, copying, modification and redistribution, including commercial use, provided the original copyright and permission notices accompany all copies or substantial portions. The full license is preserved in the repository. This license applies to the original Scientific Colour Maps material, including the portions used in the EP adaptation and preview; it does not automatically license unrelated EP identity assets.

> [!WARNING]
> Third-party icons, trademarks, animations, libraries and colour maps retain their respective rights and license terms. Review provenance, redistribution rights and applicable notices before publication.

<p align="right"><sub><a href="#readme-top">↑ Back to top</a></sub></p>

---

<a id="contact"></a>

<!-- EP-FOOTER:START -->
## Contact

<div align="center">

<a href="https://eduardo-pereira.webflow.io/"><img src="./assets/logos/logo_initials.png" alt="EP logo" height="90"></a>

Let's connect and exchange ideas and opportunities.

<a href="mailto:eduardojr.pereira@gmail.com"><img src="./assets/icons/gmail_icon.svg" alt="Email" height="27"></a>&nbsp;&nbsp;
<a href="https://www.linkedin.com/in/eduardo-jr-pereira/"><img src="./assets/icons/linkedin_icon.svg" alt="LinkedIn" height="27"></a>&nbsp;&nbsp;
<a href="https://github.com/eduardojr-pereira"><img src="./assets/icons/github_icon.svg" alt="GitHub" height="27"></a>&nbsp;&nbsp;
<a href="https://discord.com/users/533043855122235393"><img src="./assets/icons/discord_icon.svg" alt="Discord" height="27"></a>

</div>

<!-- EP-FOOTER:END -->
