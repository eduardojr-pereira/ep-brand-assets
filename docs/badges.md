# EP Badge Library

**EP Badge Library — approved design; visual integration review pending.**

This library supports educational documentation, technology identification and noncommercial portfolio projects.

81 SVG badges: 48 technologies, 3 licenses, 6 localized statuses, 22 localized topics and 2 localized methods. The 44 prepared PNG icons live in `assets/icons/technologies/`; original source files are preserved in its `originals/` subdirectory for provenance and future regeneration. They are not additional badge libraries.

## Visual specification

Flat-square SVG, height 20 px, icon box 14 × 14 px, 11 px Verdana/DejaVu Sans text, white icon tile, variable width. Original proportions and approved colors are preserved. Prepared PNGs are embedded in the SVGs; no external service is required to render them.

## Usage and maintenance

The generated SVGs and their prepared icons are preserved. The former badge generator was removed with the legacy web implementation; regeneration requires a canonical tool before it can be performed again. Original sources, SHA-256 hashes, crop parameters and rights-review state are recorded in that manifest. Do not edit generated SVGs manually.

Markdown: `![Python](relative/path/to/assets/badges/technologies/python.svg)` (adjust relative path for the consumer). Cross-repository references must use the canonical published paths. HTML: `<img src="relative/path/to/assets/badges/technologies/python.svg" alt="Python" height="20">`; standalone builds may embed the canonical SVG as a data URI. Do not maintain independent copies as sources.

## Catalog, sources and rights review

A source link is provenance, not a redistribution license. Brand names and marks belong to their respective owners. No trademark permission is asserted. Experimental crops, ecosystem mappings, and third-party licenses must be checked before public use.

| Badge | Source | Selection / note | Rights review |
|---|---|---|---|
| ![CSS](../assets/badges/technologies/css.svg) | Asset fornecido pelo autor | original; Símbolo CSS3 fornecido pelo autor; fundo quadriculado removido; proporção e cores preservadas. | pending |
| ![Visual Studio Code](../assets/badges/technologies/visual_studio_code.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d58_visual-studio-code-2019.svg) | original; Ícone fornecido pelo autor; cores e proporção preservadas. | pending |
| ![PyTorch](../assets/badges/technologies/pytorch.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d62_pytorch-logo.png) | image_direct; Imagem integral fornecida pelo autor; proporção e cores preservadas; fundo branco para contraste nos dois temas. | pending |
| ![BeautifulSoup](../assets/badges/technologies/beautifulsoup.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d64_beatifulsoup-logo.jpg) | image_direct; Imagem integral fornecida pelo autor; proporção e cores preservadas; fundo branco para contraste nos dois temas. | pending |
| ![Anaconda](../assets/badges/technologies/anaconda.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d57_anaconda-logo.svg) | original; Ícone fornecido pelo autor; cores e proporção preservadas. | pending |
| ![Adobe Premiere Pro](../assets/badges/technologies/adobe_premiere_pro.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d38_icon50-adobe-premiere-pro.png) | original; Ícone fornecido pelo autor; cores e proporção preservadas. | pending |
| ![Adobe Photoshop](../assets/badges/technologies/adobe_photoshop.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d3c_icon50-adobe-photoshop.png) | original; Ícone fornecido pelo autor; cores e proporção preservadas. | pending |
| ![Adobe After Effects](../assets/badges/technologies/adobe_after_effects.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d45_icon50-adobe-after-effects.png) | original; Ícone fornecido pelo autor; cores e proporção preservadas. | pending |
| ![Altair](../assets/badges/technologies/altair.svg) | [Source](https://raw.githubusercontent.com/vega/altair/main/design/altair-logo-light.svg) | original; Original source colors preserved. | pending |
| ![Apache Cassandra](../assets/badges/technologies/apache_cassandra.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eabb02a15a8b694c889044_cassandra-logo.jpg) | original; Isolated eye symbol; horizontal SVG excluded. | pending |
| ![Apache Hadoop](../assets/badges/technologies/apache_hadoop.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d50_icon-hadoop.png) | cropped artwork; Elephant symbol extracted from the original artwork. | pending |
| ![Apache Spark](../assets/badges/technologies/apache_spark.svg) | [Source](https://github.com/devicons/devicon/blob/master/icons/apachespark/apachespark-original.svg) | compact; — | pending |
| ![Bokeh](../assets/badges/technologies/bokeh.svg) | [Source](https://bokeh.org/img/bokeh-icon.svg) | original; Symbol without text; brand size guidelines apply. | pending |
| ![dlib](../assets/badges/technologies/dlib.svg) | [Source](https://github.com/simple-icons/simple-icons/blob/develop/icons/dlib.svg) | compact; — | pending |
| ![Docker Compose](../assets/badges/technologies/docker_compose.svg) | [Source](https://github.com/simple-icons/simple-icons/blob/develop/icons/docker.svg) | compact; Docker ecosystem symbol; colored monochrome variant. | pending |
| ![ipykernel](../assets/badges/technologies/ipykernel.svg) | Asset fornecido pelo autor | original; Ícone genérico PyPI; não representa o logotipo oficial desta biblioteca. | pending |
| ![IPython](../assets/badges/technologies/ipython.svg) | [Source](https://ipython.org/ipython-logo.png) | original; Original source colors preserved. | pending |
| ![ipywidgets](../assets/badges/technologies/ipywidgets.svg) | Asset fornecido pelo autor | original; Ícone genérico PyPI; não representa o logotipo oficial desta biblioteca. | pending |
| ![Java](../assets/badges/technologies/java.svg) | [Source](https://github.com/devicons/devicon/blob/master/icons/java/java-original.svg) | compact; Subject to Oracle trademark terms. | pending |
| ![joblib](../assets/badges/technologies/joblib.svg) | Asset fornecido pelo autor | cropped artwork; Large grey gear isolated; original retained. | pending |
| ![JupyterLab](../assets/badges/technologies/jupyterlab.svg) | [Source](https://github.com/devicons/devicon/blob/master/icons/jupyter/jupyter-original.svg) | compact; Jupyter ecosystem symbol. | pending |
| ![Keras](../assets/badges/technologies/keras.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d5d_keras-logo.svg) | original; Original source colors preserved. | pending |
| ![Markdown](../assets/badges/technologies/markdown.svg) | [Source](https://raw.githubusercontent.com/dcurtis/markdown-mark/master/svg/markdown-mark.svg) | original; Original source colors preserved. | pending |
| ![Matplotlib](../assets/badges/technologies/matplotlib.svg) | [Source](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/mpl-data/images/matplotlib.svg) | compact; Artwork distributed with the Python package. | pending |
| ![MongoDB](../assets/badges/technologies/mongodb.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d3e_icon50-mongodb.png) | original; Original source colors preserved. | pending |
| ![nbformat](../assets/badges/technologies/nbformat.svg) | Asset fornecido pelo autor | original; Ícone genérico PyPI; não representa o logotipo oficial desta biblioteca. | pending |
| ![NLTK](../assets/badges/technologies/nltk.svg) | Asset fornecido pelo autor | original; Ícone genérico PyPI compartilhado com nbformat; não é logotipo oficial do NLTK. | pending |
| ![NumPy](../assets/badges/technologies/numpy.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d5f_numpy-logo.png) | original; Original source colors preserved. | pending |
| ![ONNX Runtime](../assets/badges/technologies/onnx_runtime.svg) | [Source](https://onnxruntime.ai/images/logos/onnxruntime/ORT_icon_for_light_bg.svg) | original; Original source colors preserved. | pending |
| ![OpenCV](../assets/badges/technologies/opencv.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d69_openCV-logo.png) | cropped artwork; Cropped artwork; original proportions preserved. | pending |
| ![openpyxl](../assets/badges/technologies/openpyxl.svg) | Asset fornecido pelo autor | image_direct; Imagem integral fornecida pelo autor; proporção e cores preservadas; fundo branco para contraste nos dois temas. | pending |
| ![pandas](../assets/badges/technologies/pandas.svg) | [Source](https://github.com/devicons/devicon/blob/master/icons/pandas/pandas-original.svg) | compact; — | pending |
| ![Plotly](../assets/badges/technologies/plotly.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d7a_Plotly-logo.png) | cropped artwork; Cropped artwork; original proportions preserved. | pending |
| ![Polars](../assets/badges/technologies/polars.svg) | [Source](https://raw.githubusercontent.com/pola-rs/polars-static/master/logos/polars_logo_blue.svg) | original; Original source colors preserved. | pending |
| ![PostgreSQL](../assets/badges/technologies/postgresql.svg) | [Source](https://www.postgresql.org/media/img/about/press/elephant.png) | original; Original source colors preserved. | pending |
| ![PySpark](../assets/badges/technologies/pyspark.svg) | [Source](https://github.com/devicons/devicon/blob/master/icons/apachespark/apachespark-original.svg) | compact; Shared Apache Spark symbol, not a dedicated PySpark mark. | pending |
| ![Python](../assets/badges/technologies/python.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d6c_python-logo.png) | original; Original source colors preserved. | pending |
| ![scikit-image](../assets/badges/technologies/scikit_image.svg) | [Source](https://scikit-image.org/docs/stable/api/skimage.data.html#skimage.data.logo) | compact; Artwork distributed with the Python package. | pending |
| ![scikit-learn](../assets/badges/technologies/scikit_learn.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d6f_scikit-learn-logo.png) | image_direct; Imagem integral fornecida pelo autor; proporção e cores preservadas; fundo branco para contraste nos dois temas. | pending |
| ![SciPy](../assets/badges/technologies/scipy.svg) | [Source](https://scipy.org/images/logo.svg) | original; Original source colors preserved. | pending |
| ![seaborn](../assets/badges/technologies/seaborn.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d6e_seaborn-logo.svg) | cropped artwork; Cropped artwork; original proportions preserved. | pending |
| ![spaCy](../assets/badges/technologies/spacy.svg) | [Source](https://cdn.prod.website-files.com/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d71_SpaCy-logo.png) | image_direct; Imagem integral fornecida pelo autor; proporção e cores preservadas; fundo branco para contraste nos dois temas. | pending |
| ![SQLite](../assets/badges/technologies/sqlite.svg) | [Source](https://github.com/devicons/devicon/blob/master/icons/sqlite/sqlite-original.svg) | compact; — | pending |
| ![statsmodels](../assets/badges/technologies/statsmodels.svg) | [Source](https://www.statsmodels.org/devel/_static/statsmodels-logo-v2-no-text.svg) | original; Original source colors preserved. | pending |
| ![Surprise](../assets/badges/technologies/surprise.svg) | — | text; Badge tipográfica: cobre EP, texto branco, sem logotipo. | not_applicable |
| ![TensorFlow](../assets/badges/technologies/tensorflow.svg) | [Source](https://s3.amazonaws.com/webflow-prod-assets/65e8b43dbacbfb739916dc49/65eaa0b0d49c78b952e22d76_tensorflow-logo.png) | original; Original source colors preserved. | pending |
| ![HTML5](../assets/badges/technologies/html5.svg) | [Source](https://www.w3.org/html/logo/downloads/HTML5_Badge.svg) | original; Original source colors preserved. | pending |
| ![JavaScript](../assets/badges/technologies/javascript.svg) | [Source](https://raw.githubusercontent.com/voodootikigod/logo.js/master/js.svg) | original; Original source colors preserved. | pending |
| ![MIT](../assets/badges/licenses/mit.svg) | — | license_split; Mineral blue identifier and theme-adaptive monochrome prefix. | not_applicable |
| ![CC BY-NC 4.0](../assets/badges/licenses/cc_by_nc_4_0.svg) | — | license_split; Mineral blue identifier and theme-adaptive monochrome prefix. | not_applicable |
| ![CC BY 4.0](../assets/badges/licenses/cc_by_4_0_data.svg) | — | license_split; dataset attribution license, same approved theme palette. | not_applicable |
| ![Partial](../assets/badges/status/partial_en.svg) | — | text; Localized path preserved for README compatibility. | not_applicable |
| ![Parcial](../assets/badges/status/partial_pt_br.svg) | — | text; Localized path preserved for README compatibility. | not_applicable |
| ![Passed](../assets/badges/status/passed_en.svg) | — | text; Localized path preserved for README compatibility. | not_applicable |
| ![Aprovado](../assets/badges/status/passed_pt_br.svg) | — | text; Localized path preserved for README compatibility. | not_applicable |
| ![Pending](../assets/badges/status/pending_en.svg) | — | text; Localized path preserved for README compatibility. | not_applicable |
| ![Pendente](../assets/badges/status/pending_pt_br.svg) | — | text; Localized path preserved for README compatibility. | not_applicable |


## Licensing and third-party attribution

Third-party logos and trademarks belong to their respective owners.
Their use is solely for technology identification and does not imply
endorsement, sponsorship or affiliation.

Source libraries and license references:

- [Devicon](https://github.com/devicons/devicon/blob/master/LICENSE)
  — MIT.
- [Simple Icons](https://github.com/simple-icons/simple-icons/blob/develop/LICENSE.md)
  — CC0 1.0, subject to individual brand restrictions.
- [Markdown Mark](https://github.com/dcurtis/markdown-mark)
  — CC0 1.0.
- [HTML5 Logo](https://www.w3.org/html/logo/)
  — CC BY 3.0, attributed to W3C.
- Other technology marks retain their respective rights and terms.

EP repository licenses:

- [Code — MIT](../LICENSE-CODE.txt)
- [Original documentation — CC BY-NC 4.0](../LICENSE-CONTENT.md)
- [EP visual identity](../LICENSE-BRAND.md)

Third-party artwork is not relicensed under the EP licenses.
Source attribution does not constitute a grant of additional rights.


## Website integration

The current library contains 81 SVG badges.

| Category | Badge | Path |
|---|---|---|
| methods | Time-series CV | `assets/badges/methods/time_series_cv_en.svg` |
| methods | Validação cruzada temporal | `assets/badges/methods/time_series_cv_pt_br.svg` |
| topics | Supplementary Resources | `assets/badges/topics/supplementary_resources_en.svg` |
| topics | Recursos Complementares | `assets/badges/topics/supplementary_resources_pt_br.svg` |
| topics | Python Programming | `assets/badges/topics/python_programming_en.svg` |
| topics | Programação em Python | `assets/badges/topics/python_programming_pt_br.svg` |
| topics | Data Analysis & Visualization | `assets/badges/topics/data_analytics_en.svg` |
| topics | Análise e Visualização de Dados | `assets/badges/topics/data_analytics_pt_br.svg` |
| topics | Statistics | `assets/badges/topics/statistics_en.svg` |
| topics | Estatística | `assets/badges/topics/statistics_pt_br.svg` |
| topics | Relational & NoSQL Databases | `assets/badges/topics/relational_nosql_databases_en.svg` |
| topics | Bancos de Dados Relacionais e NoSQL | `assets/badges/topics/relational_nosql_databases_pt_br.svg` |
| topics | Machine Learning | `assets/badges/topics/machine_learning_en.svg` |
| topics | Aprendizado de Máquina | `assets/badges/topics/machine_learning_pt_br.svg` |
| topics | Natural Language Processing | `assets/badges/topics/natural_language_processing_en.svg` |
| topics | Processamento de Linguagem Natural | `assets/badges/topics/natural_language_processing_pt_br.svg` |
| topics | Deep Learning | `assets/badges/topics/deep_learning_en.svg` |
| topics | Aprendizado Profundo | `assets/badges/topics/deep_learning_pt_br.svg` |
| topics | Image Analysis & Classification | `assets/badges/topics/image_analysis_classification_en.svg` |
| topics | Análise e Classificação de Imagens | `assets/badges/topics/image_analysis_classification_pt_br.svg` |
| topics | Recommender Systems | `assets/badges/topics/recommender_systems_en.svg` |
| topics | Sistemas de Recomendação | `assets/badges/topics/recommender_systems_pt_br.svg` |
| topics | Big Data & Distributed Processing | `assets/badges/topics/big_data_distributed_processing_en.svg` |
| topics | Big Data e Processamento Distribuído | `assets/badges/topics/big_data_distributed_processing_pt_br.svg` |

The shared `badges(items)` macro in `components/web/interactive.html` consumes canonical asset paths. The future builder and global theme/language services will resolve localized artwork and standalone embedding where required.

Generated HTML is a consumer of the canonical library,
not an independent source of badge artwork.

<!-- EP-BADGES-LOTE-20261124 -->
Revisão visual local: imagens diretas (incluindo PyTorch), ícones PyPI genéricos e cinco ícones de ferramentas; Surprise tipográfico. Direitos de uso das marcas pendentes.

## Approved category rules

| Category | READMEs | Showcase and report HTML | Current SVG count |
|---|---|---|---:|
| Technologies | Yes | Yes | 48 |
| Licenses | Yes | Yes | 3 |
| Status | Yes | Yes | 6 |
| Topics | No | Yes | 22 |
| Methods | No | Yes | 2 |
| Total | | | 81 |

Topics are limited to the eleven official Knowledge Base areas (00–10), with EN/PT-BR pairs. Numbers identify areas in the catalog, not in badge labels. Keep the existing `data_analytics` path for area 02. Methods describe actual methods used in a project; create EN/PT-BR pairs only as needed. Technologies and Methods are extensible without a predetermined limit. Do not add Topics or Methods to README badge displays. The inventory above describes the approved baseline, not a maximum.

### Approved color specification

Each cell lists background / foreground. Colors are case-insensitive hex values.

| Element | Light | Dark | Origin |
|---|---|---|---|
| License identifier (all licenses) | `#505B7A` / `#FFFFFF` | `#9EA7C4` / `#242424` | EP LipariS Adapted, index 4 (zero-based) |
| License prefix | `#000000` / `#FFFFFF` | `#FFFFFF` / `#000000` | Inverse monochrome |
| Topics | `#505B7A` / `#FFFFFF` | `#9EA7C4` / `#242424` | EP LipariS Adapted, index 4 |
| Methods | `#427C83` / `#FFFFFF` | `#7CA5A8` / `#242424` | EP Muted Pastel, index 0 |
| Passed / Aprovado | `#26733C` / `#FFFFFF` | `#26733C` / `#FFFFFF` | Existing semantic status color |
| Partial / Parcial | `#E8D58A` / `#242424` | `#E8D58A` / `#242424` | Approved exception to analytical colormaps |
| Pending / Pendente | `#D86E5E` / `#242424` | `#D86E5E` / `#242424` | EP LipariS Adapted, dark index 5 |
| Text-only technology | `#9D603B` / `#FFFFFF` | `#9D603B` / `#FFFFFF` | EP copper |

All license identifiers use mineral blue; Code License, Content License and Data License distinguish their scope. The Data License badge CC BY 4.0 applies only to the dataset, not to the project’s original content or code. Technologies with artwork retain their individually approved colors from `config/badges.json`. The icon tile is white. Direct artwork uses a white background. Do not extend the copper rule to Licenses, Topics, Methods or Status.

### Technology formats and order

- **Icon + name (42):** preferred when suitable artwork exists. Use a 24 px white tile and a 14 × 14 px icon box; preserve artwork proportions and approved colors. The existing manifest modes include `original`, `compacto`, `recorte de teste` and `cropped artwork`.
- **Direct image (5):** `image_direct`; use the approved complete artwork without repeating the name as rendered text. Current entries: BeautifulSoup, openpyxl, PyTorch, scikit-learn and spaCy. Preserve proportions; the SVG is 20 px high and the image is contained within an 18 px high area with padding. Keep an accessible text label in metadata.
- **Text only (1):** `text`; no icon, EP copper and white text. Use when no suitable logo or authorized generic symbol is available and the text-only design is approved. Surprise is the current example.

The generic PyPI symbol is explicitly approved for ipykernel, ipywidgets, nbformat and NLTK; it is not their official logo. Other ecosystem substitutions require explicit approval and provenance. Joblib uses the isolated grey gear plus its name, not the previous direct image. The original artwork is retained.

Deduplicate technologies by canonical ID. Stably partition the input list into entries with artwork (including direct images), followed by entries without artwork. Preserve the original relative order within both groups; do not alphabetize or use CSS ordering. Apply this same rule when preparing badge items for the HTML macro and README lists.

### Themes, localization and consumers

Standalone SVGs use `prefers-color-scheme`. Explicit light/dark and localized variants must be resolved by the future shared theme/language services and builder. Localized badges use `_en` and `_pt_br` IDs/paths; supply the resolved `src` and `label` to `badges(items)`. Never maintain an independent source of artwork in a consumer. Regenerate embedded HTML after catalog changes. README references retain canonical published paths; updates depend on publication and caching. GitHub's selected theme may differ from the browser color scheme: validate both after publication; this is not yet confirmed. No existing README paths are removed.

## Adding or updating a badge

1. Search `config/badges.json` for the canonical ID, label, aliases and path before creating an entry. Reuse an existing badge when possible. Identify the category and the allowed consumers. Add Methods or Technologies only when needed; do not expand the official Topics list without an approved area change.
2. Select the appropriate technology format or localized category. Obtain suitable artwork from a traceable source. Check the license and trademark terms before public use; a source URL alone does not grant rights. Preserve the original under `assets/icons/technologies/originals/` and the prepared PNG under `assets/icons/technologies/`. Record the original SHA-256, any crop and the rights-review status. Do not misrepresent generic artwork as an official logo.
3. Follow the visual specification and category colors above. Keep a 20 px SVG height, suitable variable width and 11 px text; avoid clipping, distortion and redundant names. For text-only technology, set `icon` to null, `mode` to `text`, and `approved_text_only` to true only after approval. For direct artwork, use `image_direct` and a prepared PNG. For localized Topics, Methods and Status, preserve paired EN/PT-BR entries.
4. Add or update the manifest entry, using the same schema as a comparable existing entry: `id`, `category`, `path`, `label`, `background`, `foreground`, `contrast`, `width`, `icon`, `mode`, `source`, `source_path`, `source_sha256`, `visible_icon_size_px`, `crop`, `note`, `rights_review`, `approved_text_only`. For adaptive colors also use `theme_colors`, `theme_palette` and `dark_contrast`; for split licenses use `prefix`, `prefix_width` and `theme_prefix`; Topics include `area`. Calculate contrast from actual colors, not copied metadata. Keep IDs and paths stable and unique. Do not silently rename a published badge.
5. Regeneration is pending a canonical badge maintenance tool and its dedicated validation. Do not regenerate or hand-edit the preserved SVGs using the removed legacy scripts. Verify any authorized changes with the current repository checks.

6. Check the generated SVGs against the manifest, including uniqueness of IDs, labels and paths, 20 px height, artwork proportions, text fit, readable foreground/background contrast (at least 4.5:1 for text), light/dark variants, and localized pairs. Preview both themes and languages where applicable. Check stable ordering and aliases. Review all affected README and HTML references, rebuild HTML consumers, and test their actual theme/language switches.
7. Update this document's inventory, source/rights table and category details as applicable. Extend regression tests if a new rule, alias or format needs coverage; future dedicated badge tests should iterate over manifest entries and enforce the official eleven-area Topics set. Review any other fixed-count validation in packaging scripts rather than treating the baseline count as a permanent limit.
8. Obtain visual approval, resolve rights issues before public use, and commit only the approved catalog, original/prepared assets, generated SVGs, relevant tests/documentation and necessary consumer changes. Coordinate publication of the central assets before dependent references. Verify public URLs and both GitHub themes after publication. Do not publish or push without authorization.

## Report references and reproducibility — approved reusable layout

- In the introduction, render only the applicable linked code/content license badges after the description (`render_report_licenses`). Do not place technology or method badges there.
- Render the data source in its own card, including a linked dataset-license badge when the actual license is known. Never imply the dataset license applies to code or authored analysis.
- The adjacent Technical References card uses `render_references` with `technical_tabs: true`, `knowledge_base` (bilingual labels and HTTPS area links), `methods` (canonical localized base IDs), and `technologies` (canonical technology names, preferably from project metadata). Topics are clickable without arrows; methods and technologies are informational. Only nonempty tabs are rendered. Order: Topics, Methods, Technologies (PT-BR: Tópicos, Métodos, Tecnologias). The Topics tab retains links to the Knowledge Base; only the visible tab label changes. A project without data/source cards uses the full width.
- The shared `references.css` and `references.js` implement responsive tabs beside the Technical References heading where space permits, a copper sliding indicator, and a continuous 5-second rotation through nonempty tabs. Badges enter together with scale 85% → 100% and opacity 0 → 100% over 250 ms, without staggering or elastic overshoot. Rotation pauses on pointer hover, keyboard focus, explicit pause, an inactive browser tab or an off-screen card; reduced-motion preferences disable both automatic rotation and transitions. The bilingual pause/resume control and keyboard navigation remain available as applicable. All panels remain readable without scripting; on narrow screens the tabs wrap below the heading and cards stack. Do not copy the component into projects.
- Reproducibility remains outside the tabs, at full width; documentation and source-code links are adjacent. Preserve actual installation and generation instructions. Use Status only in an appropriate validation section and only when supported by actual results.
- Regenerate the report to refresh embedded badge variants from the central catalog; publish shared CSS/JS through the existing asset builder. Verify both themes and languages. This layout applies to reports, not the showcase cards (their redesign is deferred).
