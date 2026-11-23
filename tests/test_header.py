"""Read-only tests for the canonical EP Header V04 render contract."""
from __future__ import annotations

import base64
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_header as mod


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.current_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.current_href = dict(attrs).get("href")

    def handle_data(self, data: str) -> None:
        if self.current_href and data.strip():
            self.links.append((self.current_href, data.strip()))

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.current_href = None


class HeaderTests(unittest.TestCase):
    def test_approved_v04_structure(self):
        markup, css = mod.render_header([])
        for expected in ('class="ep-header"', 'data-i18n="navProjects"',
                         'data-i18n="navGithub"', 'data-language-select',
                         'data-theme-toggle', 'role="switch"',
                         'href="#projects" data-i18n="allProjects"'):
            with self.subTest(expected=expected):
                self.assertIn(expected, markup)
        self.assertIn(".ep-header__inner", css)
        self.assertNotIn("{{", markup)
        self.assertNotIn("}}", markup)
        self.assertNotIn('brandAssets', markup)

    def test_links_are_escaped_and_dynamic_menu_is_correct(self):
        projects = [
            {"name": 'Bike & Sharing <Analysis>', "report": 'selected_projects/bike_sharing/reports/index.html?x=1&y="ok"'},
            {"name": "Hangman Game", "report": "learning_labs/python_hangman_game/reports/index.html"},
        ]
        before = [dict(p) for p in projects]
        markup, _ = mod.render_header(projects)
        self.assertIn("Bike &amp; Sharing &lt;Analysis&gt;", markup)
        self.assertIn("x=1&amp;y=&quot;ok&quot;", markup)
        self.assertNotIn('<Analysis>', markup)
        self.assertEqual(projects, before)
        links = LinkCollector()
        links.feed(markup)
        self.assertIn((projects[0]["report"], projects[0]["name"]), links.links)
        self.assertIn((projects[1]["report"], projects[1]["name"]), links.links)

    def test_config_links_and_logo_embedded(self):
        html, _ = mod.render_header([])
        self.assertIn('href="https://eduardo-pereira.webflow.io/"', html)
        self.assertIn('href="https://github.com/eduardojr-pereira"', html)
        self.assertIn('src="data:image/png;base64,', html)
        logo = mod.logo_data_uri()
        self.assertEqual(base64.b64decode(logo.split(',', 1)[1]), (ROOT / 'assets/logos/logo_initials.png').read_bytes())

    def test_remote_logo_is_explicit_option(self):
        markup, _ = mod.render_header([], embed_logo=False)
        self.assertIn('raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/logos/logo_initials.png', markup)
        self.assertNotIn('src="data:', markup)

    def test_all_projects_href_can_target_the_showcase(self):
        markup, _ = mod.render_header([], all_projects_href="../../../index.html#projects")
        self.assertIn('href="../../../index.html#projects" data-i18n="allProjects"', markup)
        self.assertEqual(markup.count('data-i18n="allProjects"'), 1)

    def test_unsafe_links_are_rejected(self):
        for href in ("javascript:alert(1)", "data:text/html,test", "//host.test/x", "https://", "bad\npath", "bad\\path", ""):
            with self.subTest(href=href), self.assertRaises(ValueError):
                mod.render_header([{"name": "Bad", "report": href}])
        with self.assertRaises(ValueError):
            mod.render_header([], all_projects_href="javascript:alert(1)")
        for invalid in ({"name": "No link"}, {"report": "x"}, {"name": "", "report": "x"}, None):
            with self.subTest(project=invalid), self.assertRaises(ValueError):
                mod.render_header([invalid])

    def test_css_can_include_or_exclude_bridge(self):
        complete = mod.render_header_css()
        component = mod.render_header_css(include_portfolio_bridge=False)
        self.assertIn(".ep-header", complete)
        self.assertIn(".site-header{display:none", complete)
        self.assertNotIn(".site-header{display:none", component)
        self.assertTrue(complete.startswith(component))

    def test_no_source_files_are_modified(self):
        from hashlib import sha256
        files = [ROOT / "components/web/header.html", ROOT / "components/web/header.css", ROOT / "config/brand.json"]
        before = [sha256(f.read_bytes()).hexdigest() for f in files]
        mod.render_header([{"name": "One", "report": "reports/index.html"}])
        after = [sha256(f.read_bytes()).hexdigest() for f in files]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
