"""Read-only tests for the transitional central EP site builder."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_site as builder
from publish_assets import SHARED_FILES, copy_shared_assets


class SiteBuilderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ep-site-build-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'portfolio'
        (self.source / 'tools').mkdir(parents=True)
        (self.source / 'selected_projects').mkdir()

    def write_metadata(self, metadata: dict):
        (self.source / "config").mkdir(exist_ok=True)
        (self.source / "config/projects.json").write_text(
            json.dumps({"schema_version": 1, "projects": metadata}, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def project_meta(name="Example Project", description="Reviewed"):
        return {
            "name": {"en": name, "pt-BR": "Projeto Exemplo"},
            "description": {"en": description, "pt-BR": "Revisado"},
            "topics": ["Data Analytics"],
            "technologies": ["Python"],
            "notebook": "notebook.ipynb",
            "featured": True,
        }

    def make_project(self, name: str) -> None:
        root = self.source / name
        (root / 'reports').mkdir(parents=True)
        (root / 'reports/index.html').write_text(
            '<!doctype html><html lang="en"><head><title>Mini Report</title></head><body><h1>Mini</h1></body></html>', encoding='utf-8')
        (root / 'README.md').write_text('Test documentation', encoding='utf-8')
        (root / 'notebook.ipynb').write_text('{}', encoding='utf-8')

    def test_catalog_reads_bilingual_data(self):
        self.write_metadata({"selected_projects/example": self.project_meta()})
        data = builder.read_project_catalog(self.source)
        self.assertEqual(data["selected_projects/example"]["name"]["pt-BR"], "Projeto Exemplo")

    def test_catalog_rejects_invalid_schema(self):
        self.write_metadata({"selected_projects/example": self.project_meta()})
        path = self.source / "config/projects.json"
        data = json.loads(path.read_text())
        data["schema_version"] = 99
        path.write_text(json.dumps(data))
        with self.assertRaises(RuntimeError):
            builder.read_project_catalog(self.source)

    def test_catalog_does_not_execute_code(self):
        self.write_metadata({})
        path = self.source / "config/projects.json"
        path.write_text('{"schema_version":1,"projects": __import__("os").system("true")}')
        with self.assertRaises(RuntimeError):
            builder.read_project_catalog(self.source)

    def test_shared_assets_copy_official_resources(self):
        out = self.root / 'output'
        copy_shared_assets(out)
        for relative in SHARED_FILES:
            self.assertEqual((out / 'assets' / relative).read_bytes(), (ROOT / relative).read_bytes())
        self.assertTrue((out / 'assets/animations').is_dir())

    def test_full_isolated_build_preserves_projects_and_header(self):
        self.make_project('selected_projects/example')
        self.write_metadata({"selected_projects/example": self.project_meta()})
        dest = self.root / 'generated'
        cmd = [sys.executable, str(ROOT / 'tools/build_site.py'), '--source', str(self.source), '--output', str(dest)]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn('1 report(s)', completed.stdout)
        homepage = (dest / 'index.html').read_text(encoding='utf-8')
        self.assertIn('Example Project', homepage)
        self.assertIn('Reviewed', homepage)
        self.assertIn('Projeto Exemplo', homepage)
        self.assertIn('Revisado', homepage)
        self.assertIn('class="ep-header"', homepage)
        self.assertIn('assets/scripts/header.js', homepage)
        self.assertIn('href="https://eduardo-pereira.webflow.io/"', homepage)
        self.assertTrue((dest / 'selected_projects/example/reports/index.html').is_file())
        report_html = (dest / 'selected_projects/example/reports/index.html').read_text(encoding='utf-8')
        self.assertIn(builder.render_footer()[0], report_html)
        self.assertEqual(report_html.count('class="ep-footer"'), 1)
        self.assertFalse((dest / 'selected_projects/example/notebook.ipynb').exists())
        self.assertTrue((dest / '.nojekyll').is_file())
        # Never rewrite portfolio-owned original HTML.
        self.assertEqual((self.source / 'selected_projects/example/reports/index.html').read_text(encoding='utf-8'),
                         '<!doctype html><html lang="en"><head><title>Mini Report</title></head><body><h1>Mini</h1></body></html>')

    def test_components_have_one_stylesheet_owner(self):
        """Page builder must not redefine shared cards, controls or footer styles."""
        page = builder.make_homepage([{
            "name": "Test", "name_pt": "Teste", "description": "Details",
            "description_pt": "Detalhes", "topics": ("Data",),
            "technologies": ("Python",), "collection": "selected_projects",
            "featured": True, "notebook": None, "readme": None,
            "report": "selected_projects/test/reports/index.html",
        }])
        inline = page.split('<style>', 1)[1].split('</style>', 1)[0]
        for selector in ('.project-card{', '.card-links{', '.ep-footer', '.ep-header', '.filter{'):
            self.assertNotIn(selector, inline)
        for asset in ('cards.css', 'buttons.css', 'footer.css', 'header.css'):
            self.assertIn('assets/components/web/' + asset, page)
        for path in ('components/web/cards.css', 'components/web/buttons.css'):
            self.assertIn(path, SHARED_FILES)
        bridge = (ROOT / 'styles/portfolio-theme.css').read_text()
        self.assertNotIn('.project-card{', bridge)
        self.assertNotIn('.ep-footer{', bridge)

    def test_legacy_footer_is_not_reintroduced(self):
        source = (ROOT / 'tools/build_site.py').read_text(encoding='utf-8')
        self.assertNotIn('def remove_legacy_report_footer_css(', source)
        self.assertNotIn('_EP_LEGACY_FOOTER_START', source)
        self.assertIn('Legacy footer CSS remains in source report', source)

    def test_output_inside_source_is_rejected(self):
        self.make_project('selected_projects/example')
        self.write_metadata({})
        cmd = [sys.executable, str(ROOT / 'tools/build_site.py'), '--source', str(self.source),
               '--output', str(self.source / 'site')]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn('outside both', completed.stderr + completed.stdout)
        self.assertFalse((self.source / 'site').exists())

    def test_unmarked_output_directory_is_rejected(self):
        self.make_project('selected_projects/example')
        self.write_metadata({})
        output = self.root / 'existing'
        output.mkdir()
        (output / 'keep.txt').write_text('preserve', encoding='utf-8')
        cmd = [sys.executable, str(ROOT / 'tools/build_site.py'), '--source', str(self.source),
               '--output', str(output)]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn('unmarked', completed.stderr + completed.stdout)
        self.assertEqual((output / 'keep.txt').read_text(), 'preserve')


if __name__ == '__main__':
    unittest.main()
