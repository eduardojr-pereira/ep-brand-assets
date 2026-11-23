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
    ep_footer_html, ep_footer_css = render_footer()
    ep_header_html, ep_header_css = render_header(reports)
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
{ep_footer_css}
:root{{--bg:#0c1525;--surface:#14243a;--line:#28445f;--ink:#e7eef9;--muted:#abc0d4;--aqua:#67d8e9;--orange:#ffc07a;color-scheme:dark;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--ink)}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;min-height:100vh;background:radial-gradient(ellipse at top right,#162a40 0%,#0c1525 65%)}}a{{color:inherit}}a:focus-visible,button:focus-visible{{outline:2px solid var(--orange);outline-offset:3px}}
.container{{max-width:1120px;margin:auto;padding-left:24px;padding-right:24px}}
.site-header{{border-bottom:1px solid #263b51;background:#0c1525e8}}.header-inner{{display:flex;align-items:center;justify-content:space-between;gap:22px;min-height:86px}}
.brand{{display:inline-flex;align-items:center;gap:12px;text-decoration:none;min-width:0}}.brand img{{width:48px;height:48px;object-fit:contain}}.brand-name{{font-weight:760;letter-spacing:.055em;font-size:13px;line-height:1.35}}.brand-name small{{display:block;font-size:10px;color:var(--aqua);letter-spacing:.1em}}
.top-nav{{display:flex;align-items:center;gap:22px;flex-wrap:wrap}}.top-nav a{{font-size:13px;color:#d8e4f2;text-decoration:none}}.top-nav a:hover,.top-nav a:focus-visible{{color:#fff}}
.hero{{padding-top:62px;padding-bottom:40px}}.intro-label,.eyebrow{{text-transform:uppercase;color:var(--aqua);font-size:12px;letter-spacing:.09em;font-weight:700}}h1{{font-size:clamp(36px,6vw,64px);letter-spacing:-.045em;margin:12px 0 14px}}.lead{{font-size:17px;max-width:750px;line-height:1.75;color:var(--muted)}}
.section{{margin-bottom:48px}}h2{{font-size:25px;letter-spacing:-.025em;margin:0 0 12px}}.section-subtitle{{font-size:14px;color:var(--muted);line-height:1.7;margin:0 0 20px}}.filters,.collection-filters,.tag-row{{display:flex;gap:9px;flex-wrap:wrap}}.filter{{border:1px solid #38546d;background:#182b40;color:var(--ink);border-radius:999px;padding:9px 15px;font:inherit;font-size:13px;cursor:pointer}}.filter:hover,.filter.is-active{{border-color:var(--aqua);background:#23445a;color:#e9fcff}}.collection-filters{{margin-top:12px}}

.collection-fieldset{{display:flex;flex-wrap:wrap;align-items:center;gap:13px 28px;border:0;padding:0 0 20px;margin:0 0 18px;border-bottom:1px solid var(--line)}}
.collection-fieldset legend{{font-size:13px;font-weight:700;margin-bottom:13px;color:#bdeeff}}
.collection-option{{display:inline-flex;align-items:center;gap:8px;font-size:13px;cursor:pointer;color:#d8e4f2}}
.collection-option input{{accent-color:var(--aqua);width:16px;height:16px;cursor:pointer}}
.collection-option:hover{{color:#fff}}.area-filters h3{{font-size:13px;color:#bdeeff;margin:0 0 12px}}
.projects{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}.project-card{{display:flex;flex-direction:column;gap:12px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:26px}}.project-card:hover{{border-color:#507593}}.project-card h3{{font-size:23px;line-height:1.3;letter-spacing:-.025em;margin:0}}.project-card p{{color:#bbccdd;line-height:1.65;font-size:14px;margin:0;flex:1}}.pill,.tech{{font-size:11px;padding:5px 9px;border-radius:6px;background:#233e56;color:#b6edff}}.tech{{background:#273345;color:#e2ebf5}}.technologies{{padding-bottom:6px}}.card-links{{display:flex;gap:12px 18px;flex-wrap:wrap;justify-content:center;text-align:center;border-top:1px solid #34516a;padding-top:18px}}.card-links .report-cta{{flex:0 0 100%;margin-top:5px;color:var(--aqua);font-weight:750}}.card-links a{{font-size:13px;color:#bdeeff;text-decoration-color:var(--aqua);text-underline-offset:5px;font-weight:650}}.card-links a:hover{{color:#fff}}
.empty{{color:var(--muted);border:1px dashed #3c5368;border-radius:12px;padding:22px}}[hidden]{{display:none!important}}
.site-footer{{border-top:1px solid #263b51;text-align:center;padding:34px 16px 48px;color:var(--muted);font-size:13px}}.site-footer img{{width:72px;height:auto}}.site-footer p{{line-height:1.7}}.site-footer a{{color:#bdeeff;text-decoration-color:var(--aqua);text-underline-offset:3px}}.site-footer a:hover,.site-footer a:focus-visible{{color:#fff}}
@media(max-width:960px){{.projects{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:700px){{.projects{{grid-template-columns:1fr}}.header-inner{{align-items:flex-start;flex-direction:column;padding-top:16px;padding-bottom:18px;gap:15px}}.top-nav{{gap:10px 18px}}.top-nav a{{font-size:12px}}.brand img{{width:43px;height:43px}}.hero{{padding-top:35px}}.project-card{{padding:21px}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}

/* EP shared navigation convention */
.top-nav{{align-items:center;flex-wrap:nowrap}}.top-nav a,.github-dropdown summary{{position:relative;display:inline-flex;align-items:center;gap:5px;font-size:13px;color:#cad8e8;text-decoration:none;cursor:pointer;padding:9px 1px;background:transparent;list-style:none}}
.github-dropdown summary::-webkit-details-marker{{display:none}}.github-dropdown{{position:relative}}.github-dropdown summary::after,.top-nav__link::after{{content:"";position:absolute;bottom:5px;left:0;width:100%;height:2px;background:white;transform:scaleX(0);transform-origin:left;transition:transform .25s ease}}
.github-dropdown summary:hover,.github-dropdown summary:focus-visible,.top-nav__link:hover,.top-nav__link:focus-visible{{color:#fff}}
.github-dropdown summary:hover::after,.github-dropdown summary:focus-visible::after,.top-nav__link:hover::after,.top-nav__link:focus-visible::after{{transform:scaleX(1)}}
.github-dropdown[open] summary{{color:var(--aqua)}}.github-dropdown[open] summary::after{{background:var(--aqua);transform:scaleX(1)}}
.github-dropdown__menu{{position:absolute;top:100%;right:0;z-index:20;min-width:225px;padding:7px;background:#1a2b40;border:1px solid #42647e;border-radius:10px;box-shadow:0 16px 28px #0007}}
.github-dropdown__menu a{{display:block;padding:11px 13px;border-radius:6px;white-space:nowrap}}
.github-dropdown__menu a:hover,.github-dropdown__menu a:focus-visible{{color:#fff;background:#29445b;text-decoration:underline;text-decoration-color:#fff;text-underline-offset:4px}}
@media(max-width:700px){{.header-inner{{flex-direction:row;align-items:center;padding-top:13px;padding-bottom:13px;gap:12px}}.top-nav{{margin-left:auto;gap:12px}}.top-nav a,.github-dropdown summary{{font-size:12px}}.brand-name{{font-size:11px}}.github-dropdown__menu{{right:0}}}}
@media(max-width:420px){{.brand-name{{font-size:10px}}.brand img{{width:34px;height:34px}}.top-nav{{gap:10px}}}}
@media(prefers-reduced-motion:reduce){{.github-dropdown summary::after,.top-nav__link::after{{transition:none}}}}

/* EP navigation: click-only GitHub dropdown and Webflow-style traveling underline */
.github-dropdown summary::after,.top-nav__link::after{{transform-origin:right center;transition:transform .30s ease-in-out}}
.github-dropdown summary:hover::after,.github-dropdown summary:focus-visible::after,
.top-nav__link:hover::after,.top-nav__link:focus-visible::after{{transform-origin:left center;transform:scaleX(1)}}
.github-dropdown[open] summary::after{{transform-origin:left center;background:var(--aqua);transform:scaleX(1)}}
.github-dropdown[open] summary,.github-dropdown[open] summary:hover{{color:var(--aqua)}}
.github-dropdown__menu{{top:100%;right:0;left:auto}}
.github-dropdown__menu a{{position:relative;text-decoration:none}}
.github-dropdown__menu a:hover,.github-dropdown__menu a:focus-visible{{text-decoration:none}}
/* Card: original aqua underline, white underline slides over it on hover */
.card-links a{{position:relative;display:inline-block;text-decoration:none;border-bottom:2px solid var(--aqua);padding-bottom:3px;overflow:visible}}
.card-links a::after{{content:"";position:absolute;bottom:-2px;left:0;width:100%;height:2px;border-radius:2px;background:#fff;transform-origin:right center;transform:scaleX(0);transition:transform .3s ease-in-out}}
.card-links a:hover::after,.card-links a:focus-visible::after{{transform-origin:left center;transform:scaleX(1)}}
.card-links a:hover,.card-links a:focus-visible{{color:#fff}}
@media(prefers-reduced-motion:reduce){{.github-dropdown summary::after,.top-nav__link::after,.card-links a::after{{transition:none}}}}

/* EP-LINK-ANIMATION-V2 — card underline sized to text; CodePen direction */
.card-links {{display:grid !important;grid-template-columns:repeat(2,max-content) !important;justify-content:center !important;justify-items:center !important;column-gap:18px !important;row-gap:14px !important;text-align:center !important;}}
.card-links > a {{display:inline-block !important;position:relative !important;width:max-content !important;max-width:100%;min-width:0;justify-self:center !important;align-self:center;flex:initial !important;margin:0 !important;padding:0 0 4px !important;border:0 !important;border-radius:0;text-decoration:none !important;color:#bdeeff;white-space:normal;}}
.card-links > a.report-cta {{grid-column:1 / -1 !important;justify-self:center !important;flex:initial !important;margin:0 !important;}}
.card-links > a::before {{content:"" !important;position:absolute;bottom:0;left:0;width:100%;height:2px;background:#67d8e9;transform:none !important;display:block !important;pointer-events:none;}}
.card-links > a::after {{content:"" !important;position:absolute !important;bottom:0 !important;left:0 !important;right:auto !important;top:auto !important;width:100% !important;height:2px !important;border:0 !important;border-radius:2px !important;background:white !important;display:block !important;opacity:1 !important;transform:scaleX(0) !important;transform-origin:right center !important;transition:transform .55s cubic-bezier(.76,0,.24,1) !important;pointer-events:none;}}
.card-links > a:hover,.card-links > a:focus-visible {{color:white !important;}}
.card-links > a:hover::after,.card-links > a:focus-visible::after {{transform:scaleX(1) !important;transform-origin:left center !important;}}
/* Keep the approved click-only dropdown unchanged; external links open new tabs. */
@media (max-width:420px){{.card-links{{column-gap:12px !important}}.card-links > a{{font-size:12px !important}}}}
@media (prefers-reduced-motion:reduce){{.card-links > a::after{{transition:none !important}}}}


/* EP-CARD-ELEVATION-V1 */
/* Elevacao sutil, sem flip: conteudo e links sempre acessiveis. */
.project-card{{
  position:relative;
  transform:translate3d(0,0,0);
  transform-style:preserve-3d;
  transition:transform .42s cubic-bezier(.22,1,.36,1),
             border-color .32s ease,
             box-shadow .42s cubic-bezier(.22,1,.36,1);
  box-shadow:0 6px 18px rgba(0,0,0,.12);
}}
@media (hover:hover) and (pointer:fine){{
  .project-card:hover{{
    transform:perspective(1100px) translate3d(0,-6px,0) rotateX(1deg);
    border-color:#507e98;
    box-shadow:0 18px 38px rgba(0,0,0,.28),0 0 0 1px rgba(103,216,233,.07);
  }}
}}
.project-card:focus-within{{
  border-color:#67d8e9;
  box-shadow:0 12px 28px rgba(0,0,0,.23);
}}
@media (prefers-reduced-motion:reduce){{
  .project-card{{transition:none;transform:none;}}
  .project-card:hover{{transform:none;}}
}}


/* EP-FOOTER-MOTION-V1: standardized website link; contact cards unchanged. */
.ep-footer .ep-footer__website {{
  position:relative !important;
  display:inline-block !important;
  color:#67d8e9 !important;
  text-decoration:none !important;
  padding-bottom:5px;
  transition:color .3s ease;
}}
.ep-footer .ep-footer__website:hover,
.ep-footer .ep-footer__website:focus-visible {{ color:#ffffff !important; }}
.ep-footer .ep-footer__website::before,
.ep-footer .ep-footer__website::after {{
  content:"";position:absolute;left:0;bottom:0;width:100%;height:2px;
  pointer-events:none;border-radius:2px;
}}
.ep-footer .ep-footer__website::before {{background:#67d8e9;}}
.ep-footer .ep-footer__website::after {{
  background:#ffffff;transform:scaleX(0);transform-origin:right center;
  transition:transform .45s cubic-bezier(.76,0,.24,1);
}}
.ep-footer .ep-footer__website:hover::after,
.ep-footer .ep-footer__website:focus-visible::after {{
  transform-origin:left center;transform:scaleX(1);
}}
.ep-footer .ep-footer__website:focus-visible {{
  outline:2px solid #67d8e9;outline-offset:4px;
}}
@media (prefers-reduced-motion:reduce) {{
  .ep-footer .ep-footer__website,
  .ep-footer .ep-footer__website::after {{transition:none !important;}}
}}
@media (hover:hover) and (pointer:fine) {{
  .ep-footer__contact {{transition:transform .32s cubic-bezier(.22,1,.36,1),
    box-shadow .32s ease,border-color .2s ease;}}
  .ep-footer__contact:hover {{transform:translateY(-3px);
    box-shadow:0 11px 24px rgba(0,0,0,.20);}}
}}
@media (prefers-reduced-motion:reduce) {{
  .ep-footer__website::after,.ep-footer__contact {{transition:none !important;}}
  .ep-footer__contact:hover {{transform:none !important;}}
}}

{ep_header_css}
</style></head><body>
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
<script>
(function() {{
let topic='all',collection='all';
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



# EP-REPORT-STYLE-SYNC-V1: replace the historical embedded EP footer CSS
# in *published copies* of reports only; original reports are never rewritten.
_EP_LEGACY_FOOTER_START = '/* Scoped EP footer. Include once in the page <head>. */'
_EP_LEGACY_FOOTER_END = (
    '@media(prefers-reduced-motion:reduce){.ep-footer__contact{transition:none}'
    '.ep-footer__contact:hover,.ep-footer__contact:focus-visible{transform:none}}'
)


def synchronize_report_footer_css(report_path: Path, shared_css: str) -> None:
    """Fail closed if the historical footer block is absent or ambiguous."""
    html = report_path.read_text(encoding='utf-8')
    if html.count(_EP_LEGACY_FOOTER_START) != 1 or html.count(_EP_LEGACY_FOOTER_END) != 1:
        raise RuntimeError(f'Expected one legacy footer CSS block: {report_path}')
    start = html.index(_EP_LEGACY_FOOTER_START)
    finish = html.index(_EP_LEGACY_FOOTER_END) + len(_EP_LEGACY_FOOTER_END)
    if not (start < finish and html.rfind('<style', 0, start) > html.rfind('</style', 0, start)):
        raise RuntimeError(f'Footer CSS outside style block: {report_path}')
    refreshed = html[:start] + shared_css.rstrip() + html[finish:]
    if refreshed.count('--ep-color-footer-bg:') != 1:
        raise RuntimeError(f'Consolidated design tokens missing/duplicated: {report_path}')
    if 'background:var(--ep-color-footer-bg, #142031)' not in refreshed:
        raise RuntimeError(f'Footer background is not driven by EP tokens: {report_path}')
    report_path.write_text(refreshed, encoding='utf-8')

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
        # Keep historical reports unchanged in Git; apply canonical EP styles
        # only to the generated GitHub Pages artifact.
        if name in {"selected_projects/bike_sharing", "learning_labs/python_hangman_game"}:
            shared_css = render_footer()[1]
            synchronize_report_footer_css(destination / "reports/index.html", shared_css)
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
