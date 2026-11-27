"""Responsibility: Verify registry and project metadata validation on isolated fixtures.
Boundaries: No browser testing, production project edits, rendering or publication.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from catalog import load_projects


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path.home() / 'Downloads')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = 'selected_projects/example'
        self.project = self.root / self.path
        self.project.mkdir(parents=True)
        (self.root / 'config').mkdir()
        for name in ('README.md', 'README.pt-BR.md', 'analysis.ipynb'):
            (self.project / name).write_text('fixture', encoding='utf-8')
        self.registry = {'schema_version': 2, 'projects': [{'path': self.path, 'featured': True}]}
        self.metadata = {'schema_version': 1, 'name': {'en':'Title','pt-BR':'Título'},
            'description': {'en':'Description','pt-BR':'Descrição'},
            'topics': [{'id':'analytics','label':{'en':'Analytics','pt-BR':'Análise'}}],
            'technologies':['python'], 'documentation':{'en':'README.md','pt-BR':'README.pt-BR.md'},
            'notebook':'analysis.ipynb'}

    def write(self):
        (self.root / 'config/projects.json').write_text(json.dumps(self.registry), encoding='utf-8')
        (self.project / 'project.json').write_text(json.dumps(self.metadata), encoding='utf-8')

    def reject(self):
        self.write()
        with self.assertRaises(ValueError):
            load_projects(self.root)

    def test_valid(self):
        self.write()
        self.assertEqual(load_projects(self.root)[0]['path'], self.path)

    def test_duplicate_project(self):
        self.registry['projects'] *= 2
        self.reject()

    def test_invalid_path(self):
        self.registry['projects'][0]['path'] = '../outside'
        self.reject()

    def test_missing_locale(self):
        del self.metadata['description']['pt-BR']
        self.reject()

    def test_bad_technology(self):
        self.metadata['technologies'] = ['unknown_technology']
        self.reject()

    def test_missing_artifact(self):
        self.metadata['notebook'] = 'missing.ipynb'
        self.reject()

    def test_escape_artifact(self):
        self.metadata['documentation']['en'] = '../README.md'
        self.reject()

    def test_symlink(self):
        (self.project / 'alias.md').symlink_to(self.project / 'README.md')
        self.metadata['documentation']['en'] = 'alias.md'
        self.reject()

    def test_duplicate_json_key(self):
        self.write()
        (self.root / 'config/projects.json').write_text('{"schema_version":2,"schema_version":2,"projects":[]}', encoding='utf-8')
        with self.assertRaises(ValueError):
            load_projects(self.root)

    def test_invalid_schema(self):
        self.metadata['schema_version'] = True
        self.reject()

    def test_duplicate_technology(self):
        self.metadata['technologies'] = ['python','python']
        self.reject()

    def test_unknown_field(self):
        self.metadata['report'] = 'unapproved.html'
        self.reject()


if __name__ == '__main__':
    unittest.main()
