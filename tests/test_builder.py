"""Responsibility: Exercise declarative page builds, validation and deterministic isolated artifacts.
Boundaries: Synthetic content only; no final design, real project migration, browser acceptance or deployment.
"""
import copy
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from builder import build, render
from presentation import ROOT
from validation import read_json


def bilingual(en, pt=None):
    return {'en': en, 'pt-BR': pt or en}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def fixture(source):
    """Construct a synthetic catalog and technical-only plan, never actual legal content."""
    ident = 'learning_labs/demo'
    project = source / ident
    project.mkdir(parents=True)
    (project / 'README.md').write_text('Fixture only', encoding='utf-8')
    (project / 'README.pt-BR.md').write_text('Apenas teste', encoding='utf-8')
    (project / 'unpublished.csv').write_text('not,published', encoding='utf-8')
    write_json(source / 'config/projects.json', {'schema_version': 2, 'projects': [{'path': ident, 'featured': False}]})
    write_json(project / 'project.json', {'schema_version': 1, 'name': bilingual('Fixture report', 'Relatório de teste'), 'description': bilingual('Test only'), 'topics': [], 'technologies': ['python'], 'documentation': {'en': 'README.md', 'pt-BR': 'README.pt-BR.md'}, 'notebook': None})
    def section(id, title):
        return {'id': id, 'title': title, 'paragraphs': [bilingual('Test <text>', 'Teste <texto>')]}
    nav = read_json(ROOT / 'config/navigation.json')
    def page(route, kind, title, sections, project=None):
        return {'route': route, 'kind': kind, 'project': project, 'title': title, 'sections': sections}
    return {'schema_version': 1, 'legal': {'privacy': 'legal/fixture-one.html', 'terms': 'legal/fixture-two.html'}, 'pages': [
        page('index.html', 'landing', bilingual('Fixture landing', 'Página de teste'), [section(n['id'], None) for n in nav['sections']]),
        page('reports/demo/index.html', 'report', None, [section('overview', bilingual('Overview', 'Visão geral'))], ident),
        page('legal/fixture-one.html', 'plain', bilingual('Fixture only'), [section('example', bilingual('Fixture only'))]),
        page('legal/fixture-two.html', 'plain', bilingual('Fixture only'), [section('example', bilingual('Fixture only'))])]}


def inventory(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix='ui-builder-test-', dir=Path.home() / 'Downloads')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.plan = fixture(self.source)
        self.output = self.root / 'output'

    def test_build_and_reproducibility(self):
        original = inventory(self.source)
        pages, resources = build(self.source, self.plan, self.output)
        self.assertEqual(pages, 4)
        files = inventory(self.output)
        self.assertEqual(len(files), 5 + resources)
        self.assertIn('.nojekyll', files)
        self.assertNotIn('unpublished.csv', '\n'.join(files))
        self.assertNotIn('project.json', '\n'.join(files))
        self.assertEqual(inventory(self.source), original)
        build(self.source, self.plan, self.root / 'second')
        self.assertEqual(files, inventory(self.root / 'second'))

    def test_real_shell_links_and_escaped_text(self):
        pages = render(self.source, self.plan)
        report = pages['reports/demo/index.html']
        self.assertIn('../../index.html#home', report)
        self.assertIn('../../index.html#all-projects', report)
        self.assertIn('../../legal/fixture-one.html', report)
        self.assertIn('../../shared/styles/foundations.css', report)
        self.assertIn('Test &lt;text&gt;', report)
        self.assertIn('Relatório de teste', report)
        self.assertEqual(report.count('id="ui-config"'), 1)
        self.assertIn('href="#top"', report)

    def test_reject_route_collision_during_prepare(self):
        from builder import prepare
        self.plan['pages'][2]['route'] = 'conflict.html'
        self.plan['pages'][3]['route'] = 'conflict.html/terms.html'
        self.plan['legal'] = {'privacy': 'conflict.html', 'terms': 'conflict.html/terms.html'}
        with self.assertRaisesRegex(ValueError, 'collision'):
            prepare(self.source, self.plan)
        self.assertFalse(self.output.exists())

    def test_shell_image_paths_match_resource_selection(self):
        from resources import shell_images
        from routing import resource_base
        asset = read_json(ROOT / 'config/brand.json')['asset_root']
        pages = render(self.source, self.plan)
        route = 'reports/demo/index.html'
        for name in shell_images(asset).values():
            self.assertIn(resource_base(route) + name, pages[route])

    def test_reject_missing_legal_destination(self):
        self.plan['legal']['terms'] = 'absent.html'
        self.reject()

    def test_reject_unregistered_report(self):
        self.plan['pages'][1]['project'] = 'learning_labs/absent'
        self.reject()

    def test_reject_missing_landing_fragment(self):
        self.plan['pages'][0]['sections'].pop()
        self.reject()

    def test_reject_duplicate_page(self):
        self.plan['pages'].append(copy.deepcopy(self.plan['pages'][0]))
        self.reject()

    def test_reject_incomplete_locale(self):
        self.plan['pages'][1]['sections'][0]['title'] = {'en': 'Only English'}
        self.reject()

    def test_no_overwrite_or_source_output(self):
        self.output.mkdir()
        marker = self.output / 'keep.txt'
        marker.write_text('keep', encoding='utf-8')
        with self.assertRaises(ValueError):
            build(self.source, self.plan, self.output)
        self.assertEqual(marker.read_text(), 'keep')
        with self.assertRaises(ValueError):
            build(self.source, self.plan, self.source / 'output')
        self.assertFalse((self.source / 'output').exists())

    def reject(self):
        with self.assertRaises(ValueError):
            build(self.source, self.plan, self.output)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
