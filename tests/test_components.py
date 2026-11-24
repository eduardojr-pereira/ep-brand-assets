"""Regression checks using Python stdlib only: python -m unittest discover -s tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import render_footer as mod


class FooterTests(unittest.TestCase):
    def test_approved_readme_elements(self):
        for lang in ('en', 'pt-BR'):
            for kind in ('portfolio', 'knowledge-base', 'other'):
                with self.subTest(lang=lang, kind=kind):
                    f = mod.render_readme(kind, lang)
                    self.assertIn('height="90"', f)
                    self.assertEqual(f.count('height="27"'), 3)
                    self.assertIn('<div align="center">', f)
                    self.assertIn('href="#readme-top"', f)
                    self.assertIn('href="https://eduardo-pereira.webflow.io/"', f)
                    self.assertNotIn('{{', f)
                    self.assertEqual(f.count(mod.START), 1)
                    self.assertEqual(f.count(mod.END), 1)

    def test_related_links_not_self_referential(self):
        p = mod.render_readme('portfolio', 'en')
        k = mod.render_readme('knowledge-base', 'en')
        self.assertNotIn('[**GitHub Portfolio**]', p)
        self.assertNotIn('[**Knowledge Base**]', k)
        self.assertIn('[**Knowledge Base**]', p)
        self.assertIn('[**GitHub Portfolio**]', k)

    def test_replacement_idempotent_and_preserves_top(self):
        original = '<a id="readme-top"></a>\n\n# Title\n\nKeep me\n\n## Contact\n\nOld footer\n'
        footer = mod.render_readme('portfolio', 'en')
        new = mod.replace_footer(original, footer)
        self.assertTrue(new.startswith('<a id="readme-top"></a>\n\n# Title\n\nKeep me\n'))
        self.assertEqual(mod.replace_footer(new, footer), new)

    def test_safe_refusals(self):
        footer = mod.render_readme('portfolio', 'en')
        with self.assertRaises(ValueError):
            mod.replace_footer('# Missing header\n## Contact\nOld\n', footer)
        with self.assertRaises(ValueError):
            mod.replace_footer('<a id="readme-top"></a>\n## Contact\nOld\n## More\n', footer)

    def test_web_footer(self):
        html = mod.substitute((ROOT / 'components/web/footer.html').read_text(), mod.brand_values())
        css = (ROOT / 'components/web/footer.css').read_text()
        self.assertIn('aria-labelledby="ep-footer-title"', html)
        self.assertIn('mailto:eduardojr.pereira@gmail.com', html)
        self.assertIn('@media(max-width:520px)', css)
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn('ep-footer__layout', html)
        self.assertIn('ep-footer__watermark', html)
        self.assertIn('>EXPLORE</span>', html)
        self.assertNotIn('INDEX / 01', html)
        self.assertNotIn('Code License', html)
        self.assertIn('grid-template-columns:minmax(0,5fr)', css)
        self.assertNotIn('#34516d', css)
        self.assertNotIn('#36506a', css)

    def test_shared_styles_in_web_css(self):
        css = mod.render_web_css()
        self.assertIn('#C98D62', css)
        self.assertIn('#9D603B', css)
        self.assertIn('#242424', css)
        self.assertIn('#F4F0E9', css)
        self.assertIn('Playfair Display', css)
        self.assertIn('Source Sans 3', css)
        self.assertIn('var(--ep-color-accent)', css)
        self.assertLess(css.index('#C98D62'), css.index('.ep-footer{'))
        self.assertNotIn('#67d8e9', css)
        self.assertIn('.ep-report-nav__back--vertical', css)
        self.assertIn('prefers-reduced-motion', css)


if __name__ == '__main__':
    unittest.main()
