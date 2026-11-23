#!/usr/bin/env python3
"""Render the approved EP Header V04 from the canonical ep-brand-assets checkout.

This module is deliberately independent of render_footer.py. It produces the
HTML and CSS used by the portfolio builder without modifying project files.

Example:
    from render_header import render_header
    html, css = render_header([{"name": "Bike Sharing", "report": "selected_projects/bike_sharing/reports/index.html"}])
"""
from __future__ import annotations

import argparse
import base64
from html import escape
import json
import mimetypes
from pathlib import Path
import re
from collections.abc import Iterable, Mapping
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
_HEADER_TEMPLATE = ROOT / "components/web/header.html"
_HEADER_CSS = ROOT / "components/web/header.css"
_PORTFOLIO_BRIDGE_CSS = ROOT / "styles/portfolio-theme.css"
_BRAND_CONFIG = ROOT / "config/brand.json"
_LOGO_RELATIVE = "logos/logo_initials.png"
_ALL_PROJECTS_ANCHOR = 'href="#projects" data-i18n="allProjects"'
_TOKEN = re.compile(r"\{\{([a-z_]+)\}\}")


def _valid_href(value: str) -> str:
    """Validate and HTML-escape a link supplied by the consuming page."""
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("Header link must be a non-empty URL without surrounding spaces")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value) or "\\" in value:
        raise ValueError("Header link contains invalid characters")
    parsed = urlsplit(value)
    if value.startswith("//") or (parsed.scheme and parsed.scheme.lower() not in {"http", "https"}):
        raise ValueError("Header link must be relative or use http(s)")
    if parsed.scheme in {"http", "https"} and not parsed.netloc:
        raise ValueError("Absolute header link requires a hostname")
    return escape(value, quote=True)


def _config_values(*, embed_logo: bool) -> dict[str, str]:
    brand = json.loads(_BRAND_CONFIG.read_text(encoding="utf-8"))
    for key in ("website", "github", "portfolio", "knowledge_base"):
        brand[key] = _valid_href(brand[key])
    if embed_logo:
        brand["logo_src"] = logo_data_uri()
    else:
        asset_base = brand["asset_base"].rstrip("/")
        brand["logo_src"] = _valid_href(asset_base + "/" + _LOGO_RELATIVE)
    return brand


def logo_data_uri() -> str:
    """Return the canonical EP logo as an embeddable data URI."""
    data = (ROOT / "assets" / _LOGO_RELATIVE).read_bytes()
    mime = mimetypes.guess_type(_LOGO_RELATIVE)[0] or "application/octet-stream"
    return "data:" + mime + ";base64," + base64.b64encode(data).decode("ascii")


def _substitute(template: str, values: Mapping[str, object]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise ValueError(f"Unknown EP header placeholder: {key}")
        return str(values[key])

    rendered = _TOKEN.sub(replace, template)
    if "{{" in rendered or "}}" in rendered:
        raise ValueError("Unresolved EP header placeholders remain")
    return rendered


def render_header_css(*, include_portfolio_bridge: bool = True) -> str:
    """Return component CSS, optionally followed by the legacy portfolio theme bridge.

    The bridge keeps the existing showcase's legacy selectors compatible with
    the approved tokens. The consumer must still load theme-tokens.css and
    typography-v2.css before this CSS.
    """
    parts = [_HEADER_CSS.read_text(encoding="utf-8").rstrip()]
    if include_portfolio_bridge:
        parts.append(_PORTFOLIO_BRIDGE_CSS.read_text(encoding="utf-8").rstrip())
    return "\n".join(parts) + "\n"


def render_header(
    projects: Iterable[Mapping[str, object]],
    *,
    all_projects_href: str = "#projects",
    embed_logo: bool = True,
    include_portfolio_bridge: bool = True,
) -> tuple[str, str]:
    """Return (HTML, CSS) for the approved header, without changing its source.

    Each project must contain 'name' and 'report' (link relative to the page).
    The caller supplies page-specific links; for an internal report page, pass
    e.g. all_projects_href='../../../index.html#projects'. All dynamic content
    is escaped; the approved header HTML/CSS is never rewritten on disk.
    """
    items: list[str] = []
    for project in projects:
        if not isinstance(project, Mapping) or "name" not in project or "report" not in project:
            raise ValueError("Each project requires 'name' and 'report'")
        title = project["name"]
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Project name must be a non-empty string")
        href = _valid_href(project["report"])
        title_pt = project.get("name_pt", title)
        if not isinstance(title_pt, str) or not title_pt.strip():
            raise ValueError("Project name_pt must be a non-empty string")
        items.append(
            f'<a href="{href}" data-i18n-en="{escape(title, quote=True)}" '
            f'data-i18n-pt="{escape(title_pt, quote=True)}">{escape(title)}</a>'
        )

    template = _HEADER_TEMPLATE.read_text(encoding="utf-8")
    if template.count(_ALL_PROJECTS_ANCHOR) != 1:
        raise ValueError("Approved V04 All Projects link not found exactly once")
    replacement = f'href="{_valid_href(all_projects_href)}" data-i18n="allProjects"'
    template = template.replace(_ALL_PROJECTS_ANCHOR, replacement, 1)

    values = _config_values(embed_logo=embed_logo)
    values["projects_menu"] = "\n            ".join(items)
    html = _substitute(template, values)
    return html, render_header_css(include_portfolio_bridge=include_portfolio_bridge)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--css", action="store_true", help="Print shared header CSS instead of HTML")
    parser.add_argument("--projects-file", type=Path, help="Optional JSON array with project name/report")
    parser.add_argument("--all-projects-href", default="#projects", help="URL of the page's project section")
    parser.add_argument("--remote-logo", action="store_true", help="Use the official asset URL instead of an embedded logo")
    parser.add_argument("--component-css-only", action="store_true", help="Exclude the portfolio theme bridge")
    args = parser.parse_args()
    if args.css:
        print(render_header_css(include_portfolio_bridge=not args.component_css_only), end="")
        return
    projects = json.loads(args.projects_file.read_text(encoding="utf-8")) if args.projects_file else []
    if not isinstance(projects, list):
        parser.error("--projects-file must contain a JSON array")
    html, _ = render_header(
        projects,
        all_projects_href=args.all_projects_href,
        embed_logo=not args.remote_logo,
        include_portfolio_bridge=not args.component_css_only,
    )
    print(html, end="")


if __name__ == "__main__":
    main()
