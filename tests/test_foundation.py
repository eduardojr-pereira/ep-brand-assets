"""Tests of committed EP foundation files; independent of local demo pages."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FoundationTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_dark_and_light_tokens(self):
        colors = self.read("styles/theme-tokens.css")
        for token in ("#242424", "#F4F0E9", "#C98D62", "#9D603B", 'data-theme="light"'):
            with self.subTest(token=token):
                self.assertIn(token, colors)

    def test_theme_init_and_persistence(self):
        bootstrap = self.read("scripts/theme-init.js")
        controller = self.read("scripts/theme.js")
        self.assertIn("ep_theme", bootstrap)
        self.assertIn("data-theme", bootstrap)
        self.assertIn("ep_theme", controller)
        self.assertIn("ep:themechange", controller)

    def test_languages_and_persistence(self):
        code = self.read("scripts/i18n.js")
        for marker in ("pt-BR", "en", "ep_locale", "data-i18n", "data-language-select"):
            with self.subTest(marker=marker):
                self.assertIn(marker, code)

    def test_header_and_controls(self):
        html = self.read("components/web/header.html")
        js = self.read("scripts/header.js")
        css = self.read("components/web/header.css")
        self.assertIn('class="ep-header"', html)
        self.assertIn("data-language-select", html)
        self.assertIn("data-theme-toggle", html)
        self.assertIn("ep-header__dropdown", html)
        self.assertIn("Escape", js)
        self.assertIn("prefers-reduced-motion", css)

    def test_knowledge_lotties_are_valid_json(self):
        for variant in ("knowledge", "knowledge_copper", "knowledge_copper_light", "knowledge_white", "knowledge_graphite"):
            with self.subTest(variant=variant):
                path = ROOT / "assets/animations" / f"lottie_{variant}.json"
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(data, dict)
                self.assertIn("layers", data)


if __name__ == "__main__":
    unittest.main()
