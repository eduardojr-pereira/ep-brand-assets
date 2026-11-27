"""Responsibility: Verify shared build-time validation and direct ownership of common contracts.
Boundaries: No rendering, browser tests, production source changes or domain schema migration.
"""
import ast
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from validation import LOCALES, fields, local_file, localized, read_json, require


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ui-validation-', dir=Path.home() / 'Downloads')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_require(self):
        require(True, 'unused')
        with self.assertRaisesRegex(ValueError, 'expected'):
            require(False, 'expected')

    def test_json_utf8(self):
        p = self.root / 'data.json'
        p.write_text('{"title":"Ciência","items":[true,null,3]}', encoding='utf-8')
        self.assertEqual(read_json(p), {'title':'Ciência','items':[True,None,3]})

    def test_duplicate_json_keys(self):
        p = self.root / 'data.json'
        for value in ('{"a":1,"a":2}', '{"a":{"x":1,"x":2}}'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Duplicate JSON key'):
                p.write_text(value, encoding='utf-8')
                read_json(p)

    def test_invalid_json_constants(self):
        p = self.root / 'data.json'
        for value in ('NaN','Infinity','-Infinity'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Invalid JSON constant'):
                p.write_text('{"value":'+value+'}', encoding='utf-8')
                read_json(p)

    def test_fields(self):
        fields({'a':1}, {'a'}, 'object')
        for value in ([],{}, {'a':1,'b':2}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                fields(value, {'a'}, 'object')

    def test_localized(self):
        self.assertEqual(LOCALES, ('en','pt-BR'))
        localized({'en':'Text','pt-BR':'Texto'}, 'title')
        for value in ({'en':'Text'}, {'en':'Text','pt-BR':' '}, {'en':42,'pt-BR':'Texto'}, {'en':'Text','pt-BR':'Texto','es':'Texto'}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                localized(value,'title')

    def test_local_file(self):
        (self.root/'sub').mkdir()
        p = self.root/'sub/file.txt'; p.write_text('fixture',encoding='utf-8')
        self.assertEqual(local_file(self.root,'sub/file.txt'),p)
        for value in ('','/sub/file.txt','../file.txt','sub/./file.txt','sub//file.txt','sub\\file.txt','sub/file.txt?x','sub/file.txt#x','sub/%66ile.txt','sub/a:b','sub/\nfile.txt','sub','missing.txt'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                local_file(self.root,value)

    def test_symlinks(self):
        (self.root/'sub').mkdir()
        p=self.root/'sub/file.txt'; p.write_text('fixture',encoding='utf-8')
        (self.root/'alias.txt').symlink_to(p)
        (self.root/'aliasdir').symlink_to(self.root/'sub',target_is_directory=True)
        (self.root/'broken').symlink_to(self.root/'missing')
        for value in ('alias.txt','aliasdir/file.txt','broken'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                local_file(self.root,value)

    def test_config_consumers_reject_duplicate_keys(self):
        from badge_catalog import load_catalog
        import presentation
        from plotly_presentation import chart_payload
        config=self.root/'config'; config.mkdir()
        (config/'badges.json').write_text('{"entries":[],"entries":[]}',encoding='utf-8')
        (config/'translations.json').write_text('{"en":{},"en":{},"pt-BR":{}}',encoding='utf-8')
        (config/'colormaps.json').write_text('{"palettes":{},"palettes":{}}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Duplicate JSON key'):
            load_catalog(self.root)
        with patch.object(presentation,'ROOT',self.root):
            with self.assertRaisesRegex(ValueError,'Duplicate JSON key'):
                presentation.dictionaries()
        with self.assertRaisesRegex(ValueError,'Duplicate JSON key'):
            chart_payload('chart',{'data':[],'layout':{}},root=self.root)

    def test_direct_ownership(self):
        expected={'catalog':{'fields','local_file','localized','read_json','require'},'builder':{'fields','localized','read_json','require'},'resources':{'local_file','read_json'},'presentation':{'LOCALES','read_json'},'badge_catalog':{'read_json'},'plotly_presentation':{'read_json'},'render_badges':{'require'}}
        for module,names in expected.items():
            tree=ast.parse((ROOT/'tools'/f'{module}.py').read_text(encoding='utf-8'))
            direct={a.name for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module=='validation' for a in n.names}
            self.assertEqual(direct,names,module)
            for n in ast.walk(tree):
                if isinstance(n,ast.ImportFrom) and n.module=='catalog':
                    self.assertTrue(all(a.name=='load_projects' for a in n.names),module)
                if isinstance(n,ast.FunctionDef) and n in tree.body:
                    self.assertNotIn(n.name, {'require','read_json','localized','local_file','fields'},module)
        tree=ast.parse((ROOT/'tools/resources.py').read_text(encoding='utf-8'))
        self.assertFalse(any(isinstance(n,ast.ImportFrom) and n.module in {'catalog','presentation'} for n in ast.walk(tree)))


if __name__ == '__main__':
    unittest.main()
