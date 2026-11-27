# Editorial components

`components/web/editorial.html` owns the shared section heading, category eyebrow, project title/subtitle/description and minor heading. `styles/editorial.css` owns their typography and report introduction geometry. `styles/motion.css` owns the section entry timings. All components use the canonical theme tokens and localization bindings. No page-specific theme, translation controller or script is introduced.

## Usage

```jinja
{% import 'components/web/editorial.html' as e %}
{% import 'components/web/hero_projects.html' as h %}
{{ e.section_heading(message('content.results'), message('content.results_intro'), 'results-heading') }}
{{ h.hero_projects(project, 'overview') }}
```

`section_heading(title, description=none, id=none, level=2)` produces one semantic title (h2, or h1 for a standalone page), optional short description and a single bottom rule. The title and description use existing repeatable reveal/fade triggers. Shared geometry consolidates Selected Projects, All Projects and About Me studies: 32–100px desktop title, medium Manrope, 30ch description, 24px gap, mobile stack at 850px with 32–62px title and 48ch description. The short desktop variant follows the All Projects study (at most 760px height). These are a common baseline, not a new independently styled heading. Content must not be forced into a fixed viewport height. Page-level section spacing and real sticky-header composition are verified at integration.

`hero_projects(project, id='project-intro')` expects `category`, `title`, `description` and optionally `subtitle`, `licenses`, `business_context`, `objectives` (list of references), `notebook_href`, `documentation_href`, `technologies`. Text values are `message(key)` references unless invariant. The title is h1; use an ID matching the report navigation and a single intro per page. The license list uses the existing badge contract with actual `href` values; technologies reuse the existing graphical badges. The consumer resolves assets and legal/source destinations, supplies project-specific text and omits unavailable links and optional groups. No independent reproducibility section is needed; instructions belong in the linked documentation. Badge inventory, renderer/generator evolution, analytical components and References are handled separately. The intro has no tabs, fixed height or separate language handler. Its title, subtitle, descriptive text, category and minor heading styles are shared with the existing Selected Projects, cards and shell where applicable.

## Verification

`python tests/test_editorial.py` runs the actual shared templates, resources and fonts through the browser fixture: full/minimal intro, heading geometry, shared typography, links and badges, both themes/locales, narrow/short viewport, motion and no-JS fallback. `python tests/support.py` runs the architecture contract and all component suites. Integrated visual acceptance remains reserved for the published GitHub Pages website.
