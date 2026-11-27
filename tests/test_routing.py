"""Responsibility: Verify portable route resolution and generated link validation.
Boundaries: No browser rendering, network access, asset copying or deployment.
"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from routing import page_path, relative_href, resource_base, validate_links, validate_page_routes


class RoutingTests(unittest.TestCase):
    def test_nested_routes(self):
        self.assertEqual(relative_href('reports/bike/index.html', 'index.html'), '../../index.html')
        self.assertEqual(resource_base('reports/bike/index.html'), '../../shared/')
        self.assertEqual(resource_base('index.html'), 'shared/')

    def test_reject_bad_page_routes(self):
        for name in ('/index.html', '../index.html', 'a//b.html', 'a/./b.html', 'a\\b.html', 'a%2fb.html', 'shared/index.html', 'a.txt', 'a.html?x', '.hidden.html'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                page_path(name)

    def test_file_directory_collision(self):
        for routes in (['conflict.html', 'conflict.html/terms.html'],
                       ['conflict.html/terms.html', 'conflict.html']):
            with self.subTest(routes=routes), self.assertRaisesRegex(ValueError, 'collision'):
                validate_page_routes(routes)
        self.assertEqual(validate_page_routes(['a/index.html', 'a/terms.html']), {'a/index.html', 'a/terms.html'})

    def test_relative_and_fragments(self):
        pages = {'index.html': '<main id="home"><a href="reports/demo.html#overview">Report</a></main>',
                 'reports/demo.html': '<main id="overview"><a href="../index.html#home">Home</a><img src="../shared/assets/logo.png"></main>'}
        self.assertEqual(set(validate_links(pages, {'shared/assets/logo.png'})), set(pages))

    def test_missing_destinations(self):
        for href in ('missing.html', '#missing', 'index.html#missing', '../outside.html', '#'):
            with self.subTest(href=href), self.assertRaises(ValueError):
                validate_links({'index.html': f'<a href="{href}">x</a>'}, set())

    def test_reject_unsafe_urls(self):
        for href in ('javascript:alert(1)', '//example.com', '/index.html', 'index.html?x=1', 'https://user:pass@example.com', 'http://example.com'):
            with self.subTest(href=href), self.assertRaises(ValueError):
                validate_links({'index.html': f'<a href="{href}">x</a>'}, set())
        with self.assertRaises(ValueError):
            validate_links({'index.html': '<script src="https://example.com/test.js"></script>'}, set())

    def test_external_links_are_not_fetched(self):
        validate_links({'index.html': '<a href="https://example.com">x</a><a href="mailto:test@example.com">y</a>'}, set())

    def test_duplicate_id(self):
        with self.assertRaises(ValueError):
            validate_links({'index.html': '<b id="a"></b><i id="a"></i>'}, set())


if __name__ == '__main__':
    unittest.main()
