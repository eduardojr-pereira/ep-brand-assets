<a id="readme-top"></a>

<div align="center">

[🇺🇸 English](./README.md) &nbsp;|&nbsp; [🇧🇷 Português](./README.pt-BR.md)

<img src="assets/logos/logo_initials.png" alt="EP" width="115" />

# EP · Brand Assets

Visual identity and shared infrastructure for the professional projects of Eduardo Junior Pereira.

[GitHub](https://github.com/eduardojr-pereira) · [LinkedIn](https://www.linkedin.com/in/eduardo-jr-pereira/) · [Portfolio website](https://eduardo-pereira.webflow.io/)

</div>

---

## On This Page

[Overview](#ep-overview) · [Visual Identity](#ep-visual-identity) · [Shared Components](#ep-shared-components) · [Themes and Internationalization](#ep-themes-and-internationalization) · [EP Analytical Colour System](#ep-ep-analytical-colour-system) · [Directory Structure](#ep-directory-structure) · [Usage and Integration](#ep-usage-and-integration) · [Related Repositories](#ep-related-repositories) · [License](#ep-license) · [Contact](#ep-contact)

---

<a id="ep-overview"></a>

## Overview

This repository is the canonical source of the EP identity and shared infrastructure for the portfolio showcase, project reports and professional READMEs. It centralizes design tokens, typography, themes, bilingual interface mechanisms, visual assets, components and renderers. Projects retain their own data, analyses and project-specific texts.

---

<a id="ep-visual-identity"></a>

## Visual Identity

The identity uses the EP logo, institutional graphite and copper palette, shared typography, social icons and Lottie animations. The institutional palette is distinct from the analytical colour system.

| Asset | Preview | File |
|---|---|---|
| EP logo | <img src="assets/logos/logo_initials.png" width="64" alt="EP logo" /> | [`logo_initials.png`](./assets/logos/logo_initials.png) |
| GitHub | <img src="assets/icons/github_icon.svg" width="26" alt="GitHub" /> | [`github_icon.svg`](./assets/icons/github_icon.svg) |
| LinkedIn | <img src="assets/icons/linkedin_icon.svg" width="26" alt="LinkedIn" /> | [`linkedin_icon.svg`](./assets/icons/linkedin_icon.svg) |
| Email | <img src="assets/icons/gmail_icon.svg" width="26" alt="Email" /> | [`gmail_icon.svg`](./assets/icons/gmail_icon.svg) |
| Discord | <img src="assets/icons/discord_icon.svg" width="26" alt="Discord" /> | [`discord_icon.svg`](./assets/icons/discord_icon.svg) |

See [animations](./assets/animations/) and [theme tokens](./styles/theme-tokens.css).

---

<a id="ep-shared-components"></a>

## Shared Components

Components are maintained in EP Brand and reused where relevant. The site builder assembles the portfolio and reports from canonical sources rather than maintaining separate implementations in each project.

| Component | Source |
|---|---|
| Institutional configuration | [`config/brand.json`](./config/brand.json) |
| Web components: Header, Footer, cards, buttons, links, navigation and controls | [`components/web/`](./components/web/) |
| Bilingual Markdown footers | [`components/markdown/`](./components/markdown/) |
| Shared scripts and interactions | [`scripts/`](./scripts/) |
| Composition, rendering and publication | [`tools/`](./tools/) |
| Regression tests | [`tests/`](./tests/) |

---

<a id="ep-themes-and-internationalization"></a>

## Themes and Internationalization

Light and dark themes share [theme tokens](./styles/theme-tokens.css) and [typography](./styles/typography-v2.css). [Theme initialization](./scripts/theme-init.js), [theme switching](./scripts/theme.js) and [interface internationalization](./scripts/i18n.js) provide the common mechanisms. Project-specific translations remain with each project. The [Plotly theme adapter](./scripts/plotly-theme.js) and [localization adapter](./scripts/plotly-i18n.js) handle analytical presentation, without changing the underlying data.

---

<a id="ep-ep-analytical-colour-system"></a>

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

Preview generated from [config/colormaps.json](./config/colormaps.json), the source of truth. The continuous scales use Scientific Colour Maps 9.0.0 by Fabio Crameri; EP LipariS Adapted is an adaptation, not an official scale. Categorical colours require additional cues (markers, line styles, patterns or labels); contrast alone does not guarantee accessibility. See the [methodology and attribution](./docs/colormaps.md) and [MIT license](./docs/LICENSE-SCIENTIFIC-COLOUR-MAPS.txt). The [canonical Plotly renderer](./tools/render_plotly.py) and [generated CSS](./styles/colormaps.css) consume the colour configuration.

---

<a id="ep-directory-structure"></a>

## Directory Structure

```text
ep-brand-assets/
├── assets/
│   ├── logos/
│   ├── icons/
│   └── animations/
├── components/
│   ├── markdown/
│   └── web/
├── config/
├── docs/
├── scripts/
├── styles/
├── tests/
├── tools/
├── README.md
└── README.pt-BR.md
```

---

<a id="ep-usage-and-integration"></a>

## Usage and Integration

For other repositories, use the public asset URLs.

```markdown
![EP](https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/logos/logo_initials.png)
```

```html
<img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/github_icon.svg" alt="GitHub" width="26" />
```

Keep the canonical checkout of EP Brand alongside the Portfolio checkout. From EP Brand, replace the source path with your local Portfolio path; use a preview output directory outside both repositories.

```bash
python3 tools/build_site.py --source /path/to/data-science-portfolio --output /tmp/ep-portfolio-preview
```

Preview Markdown footers without writing files:

```bash
python3 tools/render_footer.py readme --kind portfolio --lang en
python3 tools/render_footer.py readme --kind knowledge-base --lang pt-BR
```

With `--file`, the renderer displays the proposed diff; only `--apply` writes changes. Review before applying. Render the web footer with embedded assets using `python3 tools/render_footer.py web --embed-assets`.

Regression tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

Do not rename shared assets without checking consumers. Local generation does not publish changes.

---

<a id="ep-related-repositories"></a>

## Related Repositories

| Repository | Role |
|---|---|
| [Data Science Portfolio](https://github.com/eduardojr-pereira/data-science-portfolio) | Applied projects, showcase, Bike Sharing and Hangman. |
| [Data Science Knowledge Base](https://github.com/eduardojr-pereira/data-science-knowledge-base) | Technical knowledge and professional documentation. |

---

<a id="ep-license"></a>

## License

EP identity assets do not imply permission for commercial reuse or redistribution. Terms may be defined separately; third-party assets retain their applicable rights and licenses.

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

---

<a id="ep-contact"></a>

<!-- EP-FOOTER:START -->
## Contact

<div align="center">

<a href="https://eduardo-pereira.webflow.io/" title="Personal website — Eduardo Junior Pereira"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/logos/logo_initials.png" alt="EP logo — Eduardo Junior Pereira" height="90"></a>

**Eduardo Junior Pereira**

*Economics · Data Science · Analytics*

<a href="mailto:eduardojr.pereira@gmail.com"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/gmail_icon.svg" alt="Email" height="27"></a>&nbsp;&nbsp;
<a href="https://www.linkedin.com/in/eduardo-jr-pereira/"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/linkedin_icon.svg" alt="LinkedIn" height="27"></a>&nbsp;&nbsp;
<a href="https://github.com/eduardojr-pereira"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/github_icon.svg" alt="GitHub" height="27"></a>

[Let's connect on LinkedIn to exchange ideas and opportunities.](https://www.linkedin.com/in/eduardo-jr-pereira/)

[**GitHub Portfolio**](https://github.com/eduardojr-pereira/data-science-portfolio) &nbsp;•&nbsp; [**Knowledge Base**](https://github.com/eduardojr-pereira/data-science-knowledge-base)

</div>

<p align="right"><a href="#readme-top">↑ BACK TO TOP</a></p>

---
<!-- EP-FOOTER:END -->
