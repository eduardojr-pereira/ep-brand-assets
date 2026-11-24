#!/usr/bin/env python3
"""Build a responsive GitHub Pages showcase from approved project reports.

Run from any directory:
    python /path/to/ep-brand-assets/tools/build_site.py --source /path/to/04_Projetos --output /tmp/ep-portfolio-new

Project editorial metadata is read from source/config/projects.json.
The old portfolio builder is not imported, parsed, or executed.

Only report directories and verified generated outputs are published, never source
notebooks, raw data, or arbitrary project files. Project descriptions and topics
are editorial metadata; do not infer scientific claims from a filename.
"""
from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
from render_header import render_header, logo_data_uri
from render_footer import brand_values, substitute, render_web_css
from publish_assets import copy_shared_assets
from report_pages import integrate_report
import shutil
from urllib.parse import unquote, urlsplit

BRAND_ROOT = Path(__file__).resolve().parents[1]
ROOT: Path = Path.cwd()  # The actual source is supplied with --source to main().


def render_footer() -> tuple[str, str]:
    """Use the approved, independent render_footer module from EP Brand."""
    html = substitute((BRAND_ROOT / 'components/web/footer.html').read_text(encoding='utf-8'),
                      brand_values(embed=True))
    return html, render_web_css()


def read_project_catalog(source_root: Path) -> dict[str, dict]:
    """Load portfolio-owned bilingual metadata; never execute portfolio code."""
    path = source_root / "config/projects.json"
    if not path.is_file():
        raise RuntimeError(f"Missing project catalog: {path}")
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Invalid project catalog: {path}") from exc
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        raise RuntimeError("Unsupported projects.json schema_version")
    projects = catalog.get("projects")
    if not isinstance(projects, dict):
        raise RuntimeError("projects.json must contain a projects object")
    for key, meta in projects.items():
        if (not isinstance(key, str) or not key or key.startswith("/")
            or "\\\\" in key or any(part in {"", ".", ".."} for part in key.split("/"))
            or not key.startswith(("selected_projects/", "learning_labs/"))
            or not isinstance(meta, dict)):
            raise RuntimeError(f"Invalid project catalog entry: {key!r}")
        for field in ("name", "description"):
            localized = meta.get(field)
            if not isinstance(localized, dict) or any(
                not isinstance(localized.get(lang), str) or not localized[lang].strip()
                for lang in ("en", "pt-BR")
            ):
                raise RuntimeError(f"{key}: {field} requires en and pt-BR")
        for field in ("topics", "technologies"):
            values = meta.get(field)
            if not isinstance(values, list) or any(
                not isinstance(v, str) or not v.strip() for v in values
            ):
                raise RuntimeError(f"{key}: {field} must be a list of strings")
        if "notebook" in meta and (
            not isinstance(meta["notebook"], str)
            or Path(meta["notebook"]).name != meta["notebook"]
        ):
            raise RuntimeError(f"{key}: invalid notebook filename")
        if "featured" in meta and not isinstance(meta["featured"], bool):
            raise RuntimeError(f"{key}: featured must be boolean")
    return projects


REPORT_COLLECTIONS = ("selected_projects", "learning_labs")
REPO = "https://github.com/eduardojr-pereira/data-science-portfolio"
KNOWLEDGE = "https://github.com/eduardojr-pereira/data-science-knowledge-base"
WEBSITE = "https://eduardo-pereira.webflow.io/"
LOGO = "https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/logos/logo_initials.png"

# Add an entry after reviewing and approving each project; discovered reports
# without metadata are listed conservatively (no invented tools or findings).
PROJECT_METADATA: dict[str, dict] = {}



class PageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []
        self.title_parts: list[str] = []
        self.inside_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "title":
            self.inside_title = True
        key = "href" if tag in {"a", "link"} else "src" if tag in {"script", "img"} else None
        if key and attributes.get(key):
            self.urls.append(str(attributes[key]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.inside_title = False

    def handle_data(self, data: str) -> None:
        if self.inside_title:
            self.title_parts.append(data)


def discover_reports() -> list[Path]:
    return sorted(report for collection in REPORT_COLLECTIONS
        if (ROOT / collection).is_dir()
        for report in (ROOT / collection).rglob("reports/index.html")
        if not any(part.startswith(".") for part in report.relative_to(ROOT).parts))


def ensure_valid_local_links(source_html: Path, parser: PageLinks) -> None:
    for url in parser.urls:
        if url in {"../../../index.html", "../../../../index.html"}:
            continue  # Homepage created by the Pages builder
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
            continue
        destination = (source_html.parent / unquote(parsed.path)).resolve()
        if not destination.is_relative_to(ROOT) or not destination.is_file():
            raise RuntimeError(f"Missing or unsafe local link in {source_html}: {url}")
        project = source_html.parent.parent
        if not (destination.is_relative_to(project / "reports") or destination.is_relative_to(project / "outputs")):
            raise RuntimeError(f"Link points outside published report assets: {url}")


def make_homepage(reports: list[dict[str, object]]) -> str:
    topics = sorted({t for p in reports for t in p["topics"]})
    filters = ['<button class="filter is-active" type="button" data-topic="all" aria-pressed="true" data-i18n="allProjects">All projects</button>']
    filters += [f'<button class="filter" type="button" data-topic="{escape(t, quote=True)}" aria-pressed="false">{escape(t)}</button>' for t in topics]
    cards = []
    for p in reports:
        collection = str(p["collection"])
        kind = "Selected Project" if collection == "selected_projects" else "Learning Lab"
        topic_tags = "".join(f'<span class="pill">{escape(str(t))}</span>' for t in p["topics"])
        tech_tags = "".join(f'<span class="tech">{escape(str(t))}</span>' for t in p["technologies"])
        document_links = []
        if p["notebook"]:
            document_links.append(f'<a href="{escape(str(p["notebook"]), quote=True)}"><span data-i18n="code">Code</span> <span aria-hidden="true">↗</span></a>')
        if p["readme"]:
            document_links.append(f'<a href="{escape(str(p["readme"]), quote=True)}"><span data-i18n="documentation">Documentation</span> <span aria-hidden="true">↗</span></a>')
        document_links.append(f'<a class="report-cta" href="{escape(str(p["report"]), quote=True)}"><span data-i18n="view">View</span> <span aria-hidden="true">↗</span></a>')
        label = "Featured · " if p["featured"] else ""
        cards.append(f'''<article class="project-card" data-collection="{escape(collection, quote=True)}" data-topics="{escape('|'.join(p['topics']), quote=True)}">
  <div class="card-head"><span class="eyebrow">{label}{kind}</span></div>
  <h3 data-i18n-en="{escape(str(p['name']), quote=True)}" data-i18n-pt="{escape(str(p['name_pt']), quote=True)}">{escape(str(p['name']))}</h3>
  <p data-i18n-en="{escape(str(p['description']), quote=True)}" data-i18n-pt="{escape(str(p['description_pt']), quote=True)}">{escape(str(p['description']))}</p>
  <div class="tag-row" aria-label="Project categories">{topic_tags}</div>
  <div class="tag-row technologies" aria-label="Technologies">{tech_tags}</div>
  <div class="card-links">{' '.join(document_links)}</div>
</article>''')
    markup = '\n'.join(cards)
    ep_footer_html, _ = render_footer()
    ep_header_html, _ = render_header(reports)
    ep_logo_src = logo_data_uri()
    return f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<script src="assets/scripts/theme-init.js"></script>
<link rel="stylesheet" href="assets/styles/theme-tokens.css">
<link rel="stylesheet" href="assets/styles/typography-v2.css">
<meta name="description" content="Applied data science projects, reproducible notebooks, and interactive analytical reports.">
<title>Data Science Portfolio · Eduardo Junior Pereira</title>
<style>
/* Page composition only. Shared controls, cards, header and footer live in EP Brand CSS. */
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;min-height:100vh;background:var(--ep-color-bg);color:var(--ep-color-text)}}
.container{{max-width:1120px;margin:auto;padding-left:24px;padding-right:24px}}
.hero{{padding-top:62px;padding-bottom:40px}}
.intro-label,.eyebrow{{text-transform:uppercase;color:var(--ep-color-accent);font-size:12px;letter-spacing:.09em;font-weight:700}}
h1{{font-size:clamp(36px,6vw,64px);letter-spacing:-.045em;margin:12px 0 14px}}
.lead{{font-size:17px;max-width:750px;line-height:1.75;color:var(--ep-color-muted)}}
.section{{margin-bottom:48px}}
h2{{font-size:25px;letter-spacing:-.025em;margin:0 0 12px}}
.section-subtitle{{font-size:14px;color:var(--ep-color-muted);line-height:1.7;margin:0 0 20px}}
.projects{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}
.tag-row,.filters,.collection-filters{{display:flex;gap:9px;flex-wrap:wrap}}
.technologies{{padding-bottom:6px}}
.collection-filters{{margin-top:12px}}
.collection-fieldset{{display:flex;flex-wrap:wrap;align-items:center;gap:13px 28px;border:0;padding:0 0 20px;margin:0 0 18px;border-bottom:1px solid var(--ep-color-border)}}
.collection-fieldset legend{{font-size:13px;font-weight:700;margin-bottom:13px;color:var(--ep-color-accent)}}
.area-filters h3{{font-size:13px;color:var(--ep-color-accent);margin:0 0 12px}}
.empty{{color:var(--ep-color-muted);border:1px dashed var(--ep-color-border);border-radius:12px;padding:22px}}
[hidden]{{display:none!important}}
@media(max-width:960px){{.projects{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:700px){{.projects{{grid-template-columns:1fr}}.hero{{padding-top:35px}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
</style>
<link rel="stylesheet" href="assets/components/web/header.css">
<link rel="stylesheet" href="assets/components/web/footer.css">
<link rel="stylesheet" href="assets/styles/report-navigation.css">
<link rel="stylesheet" href="assets/components/web/cards.css">
<link rel="stylesheet" href="assets/components/web/buttons.css">
<link rel="stylesheet" href="assets/styles/portfolio-theme.css">
</head><body>
{ep_header_html}

<main class="container">
<section class="hero" id="home"><div class="intro-label" data-i18n="heroLabel">Data Science · Analytics · Applied Projects</div><h1 data-i18n="headline">Data Science Portfolio</h1><p class="lead" data-i18n="lead">Explore applied analyses, interactive reports and reproducible methods. Each project connects a practical question to evidence, results and limitations, with source code and documentation available on GitHub.</p></section>
<section class="section" aria-labelledby="explore-title"><h2 id="explore-title" data-i18n="exploreTitle">Explore by category</h2><p class="section-subtitle" data-i18n="exploreSubtitle">Filter projects by area or collection. Only published reports are shown.</p>
<fieldset class="collection-fieldset"><legend data-i18n="collectionLabel">Collection</legend>
<label class="collection-option"><input type="radio" name="collection" value="all" checked> <span data-i18n="allProjects">All Projects</span></label>
<label class="collection-option"><input type="radio" name="collection" value="selected_projects"> <span data-i18n="selectedProjects">Selected Projects</span></label>
<label class="collection-option"><input type="radio" name="collection" value="learning_labs"> <span data-i18n="learningLabs">Learning Labs</span></label>
</fieldset>
<div class="area-filters"><h3 data-i18n="area">Area</h3><div class="filters" role="group" aria-label="Project areas">{''.join(filters)}</div></div>
</section>
<section class="section" aria-labelledby="projects-title"><h2 id="projects-title" data-i18n="projectsReports">Projects &amp; reports</h2><p class="section-subtitle" id="result-count" aria-live="polite"></p><div class="projects" id="projects">{markup}</div><p class="empty" id="empty" hidden data-i18n="empty">No published projects match these filters. Choose another category or collection.</p></section>
</main>
{ep_footer_html}
<script src="assets/scripts/theme.js" defer></script>
<script src="assets/scripts/i18n.js" defer></script>
<script src="assets/scripts/header.js" defer></script>
<script src="assets/scripts/footer.js" defer></script>
<script>
(function() {{
let topic='all',collection='all';
const requestedCollection=new URLSearchParams(location.search).get('collection');
if(['selected_projects','learning_labs'].includes(requestedCollection)){{collection=requestedCollection;const input=document.querySelector(`input[name="collection"][value="${{requestedCollection}}"]`);if(input)input.checked=true;}}
const cards=Array.from(document.querySelectorAll('.project-card'));
const githubMenu=document.querySelector('.github-dropdown');
if(githubMenu){{
  const githubToggle=githubMenu.querySelector('summary');
  /* Native <details> toggles on click, Enter and Space. Never toggle on hover. */
  document.addEventListener('pointerdown',event=>{{
    if(!githubMenu.contains(event.target))githubMenu.open=false;
  }});
  document.addEventListener('keydown',event=>{{
    if(event.key==='Escape' && githubMenu.open){{
      githubMenu.open=false;
      githubToggle.focus();
    }}
  }});
}}
function apply() {{let visible=0;cards.forEach(card=>{{const topics=card.dataset.topics.split('|');const show=(topic==='all'||topics.includes(topic))&&(collection==='all'||card.dataset.collection===collection);card.hidden=!show;if(show)visible++;}});document.getElementById('empty').hidden=visible!==0;document.getElementById('result-count').textContent=visible+' published '+(visible===1?'project':'projects')+' shown';}}
document.querySelectorAll('button[data-topic]').forEach(button=>button.addEventListener('click',()=>{{topic=button.dataset.topic;document.querySelectorAll('button[data-topic]').forEach(b=>{{let selected=b===button;b.classList.toggle('is-active',selected);b.setAttribute('aria-pressed',String(selected));}});apply();}}));document.querySelectorAll('input[name="collection"]').forEach(input=>input.addEventListener('change',()=>{{if(input.checked){{collection=input.value;apply();}}}}));apply();
}})();
</script></body></html>'''



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Portfolio repository root")
    parser.add_argument("--output", type=Path, required=True, help="Destination for static Pages artifacts")
    args = parser.parse_args()
    global ROOT, PROJECT_METADATA
    ROOT = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not ROOT.is_dir() or not (ROOT / 'selected_projects').is_dir():
        raise SystemExit(f"Not a supported portfolio source directory: {ROOT}")
    if (output == ROOT or ROOT.is_relative_to(output) or output.is_relative_to(ROOT)
        or output == BRAND_ROOT or BRAND_ROOT.is_relative_to(output)
        or output.is_relative_to(BRAND_ROOT)):
        raise SystemExit("Output directory must be outside both source and EP Brand repositories")
    PROJECT_METADATA = read_project_catalog(ROOT)
    reports = discover_reports()
    if not reports:
        raise SystemExit("No reports/index.html found under selected_projects/ or learning_labs/")
    parsed: list[tuple[Path, PageLinks]] = []
    for report in reports:
        page = PageLinks()
        page.feed(report.read_text(encoding="utf-8"))
        ensure_valid_local_links(report, page)
        parsed.append((report, page))
    if output.exists():
        if not (output / ".portfolio-pages-build").is_file():
            raise SystemExit(f"Refusing to overwrite an unmarked directory: {output}")
        shutil.rmtree(output)
    output.mkdir(parents=True)
    copy_shared_assets(output)
    (output / ".portfolio-pages-build").touch()
    published: list[dict[str, object]] = []
    for report, page in parsed:
        project = report.parent.parent
        relative = project.relative_to(ROOT)
        name = relative.as_posix()
        for asset_root in (project / "reports", project / "outputs"):
            if asset_root.is_dir() and any(p.is_symlink() for p in asset_root.rglob("*")):
                raise RuntimeError(f"Symlinks are not allowed in published assets: {asset_root}")
        destination = output / relative
        shutil.copytree(project / "reports", destination / "reports", ignore=shutil.ignore_patterns("*.bak", ".ipynb_checkpoints", "__pycache__", "*.pyc"))
        # Published reports must already use the canonical EP Brand footer.
        # Do not silently rewrite legacy footer CSS in generated artifacts.
        published_report = destination / "reports/index.html"
        raw_report = published_report.read_text(encoding="utf-8")
        if "/* Scoped EP footer. Include once in the page <head>. */" in raw_report:
            raise RuntimeError(f"Legacy footer CSS remains in source report: {report}")
        if (project / "outputs").is_dir():
            shutil.copytree(project / "outputs", destination / "outputs")
        meta = PROJECT_METADATA.get(name, {})
        report_title = " ".join(page.title_parts).split(" · ", 1)[0].strip()
        notebook = project / str(meta.get("notebook", "")) if meta.get("notebook") else None
        readme = project / "README.md"
        published.append({
            "name": str(meta.get("name", {}).get("en") or report_title or project.name.replace('_',' ').title()),
            "name_pt": str(meta.get("name", {}).get("pt-BR") or report_title or project.name.replace('_',' ').title()),
            "description": str(meta.get("description", {}).get("en") or "Explore the published interactive report and consult the project documentation for scope and limitations."),
            "description_pt": str(meta.get("description", {}).get("pt-BR") or "Explore the published interactive report and consult the project documentation for scope and limitations."),
            "topics": tuple(meta.get("topics") or ("Data Analytics" if relative.parts[0]=="selected_projects" else "Learning Labs",)),
            "technologies": tuple(meta.get("technologies") or ()),
            "collection": relative.parts[0],
            "featured": bool(meta.get("featured", False)),
            "report": name + "/reports/index.html",
            "readme": REPO + "/blob/main/" + name + "/README.md" if readme.is_file() else None,
            "notebook": REPO + "/blob/main/" + name + "/" + notebook.name if notebook and notebook.is_file() else None,
        })
        print(f"Prepared: {name}/reports/index.html")
    published.sort(key=lambda p: (not p["featured"], p["name"]))
    for item in published:
        integrate_report(output / str(item["report"]), published, output)
    (output / "index.html").write_text(make_homepage(published), encoding="utf-8")
    # Compatibilidade com o endereço histórico, sem manter a pasta antiga no Git.
    legacy = output / "learning_labs/python/jogo_da_forca/reports/index.html"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0;url=../../../python_hangman_game/reports/index.html">'
        '<title>Hangman — moved</title></head><body>'
        '<p><a href="../../../python_hangman_game/reports/index.html">Continue to Hangman</a></p>'
        '</body></html>', encoding="utf-8"
    )
    (output / ".nojekyll").touch()
    print(f"Ready for Pages: {len(published)} report(s), {output}")


if __name__ == "__main__":
    main()
