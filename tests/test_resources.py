"""Responsibility: Verify canonical runtime resource selection and single-copy output.
Boundaries: No source mutation, visual review, project artifact publication or network requests.
"""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from resources import resource_paths, copy_resources, shell_images
from presentation import ROOT, DEPENDENCIES


class ResourceTests(unittest.TestCase):
    def test_manifest_and_notices(self):
        paths = resource_paths()
        self.assertEqual(paths, sorted(set(paths)))
        for name in DEPENDENCIES['styles'] + DEPENDENCIES['head_scripts'] + DEPENDENCIES['defer_scripts']:
            self.assertIn(name, paths)
        for name in ('assets/fonts/manrope/OFL.txt', 'assets/fonts/inter/OFL.txt', 'assets/vendor/lottie/LICENSE.md', 'assets/vendor/plotly/LICENSE', 'LICENSE-BRAND.md', 'THIRD-PARTY-NOTICES.md', 'docs/LICENSE-SCIENTIFIC-COLOUR-MAPS.txt'):
            self.assertIn(name, paths)
        self.assertFalse(any(p.startswith(('tools/', 'tests/', 'components/', 'config/')) for p in paths))
        self.assertFalse(any('/originals/' in p for p in paths))

    def test_single_copy_and_byte_integrity(self):
        with TemporaryDirectory(prefix='ui-resource-test-', dir=Path.home() / 'Downloads') as folder:
            out = Path(folder)
            paths = resource_paths()
            published = copy_resources(out, paths=paths)
            actual = {p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}
            self.assertEqual(actual, published)
            for name in paths:
                self.assertEqual((ROOT / name).read_bytes(), (out / 'shared' / name).read_bytes())
            with self.assertRaises(FileExistsError):
                copy_resources(out, paths=paths)

    def test_symlink_destinations_rejected_before_any_copy(self):
        with TemporaryDirectory(prefix='ui-resource-test-', dir=Path.home() / 'Downloads') as folder:
            root = Path(folder)
            outside = root / 'outside'
            outside.mkdir()
            for mode in ('output', 'shared', 'nested', 'file'):
                with self.subTest(mode=mode):
                    out = root / mode
                    if mode == 'output':
                        out.symlink_to(outside, target_is_directory=True)
                    else:
                        out.mkdir()
                        shared = out / 'shared'
                        if mode == 'shared':
                            shared.symlink_to(outside, target_is_directory=True)
                        else:
                            shared.mkdir()
                            if mode == 'nested':
                                (shared / 'styles').symlink_to(outside, target_is_directory=True)
                            else:
                                (shared / 'styles').mkdir()
                                (shared / 'styles/foundations.css').symlink_to(outside / 'missing.css')
                    with self.assertRaises(ValueError):
                        copy_resources(out, paths=['LICENSE-BRAND.md', 'styles/foundations.css'])
                    self.assertFalse(list(outside.iterdir()))
                    self.assertFalse((out / 'shared/LICENSE-BRAND.md').exists())

    def test_shell_images_are_canonical_resources(self):
        from validation import read_json
        asset = read_json(ROOT / 'config/brand.json')['asset_root']
        images = shell_images(asset)
        self.assertEqual(set(images), {'logo_src', 'favicon_src'})
        self.assertTrue(set(images.values()).issubset(resource_paths()))

    def test_missing_and_traversal(self):
        with TemporaryDirectory(prefix='ui-resource-test-', dir=Path.home() / 'Downloads') as folder:
            out = Path(folder)
            for path in ('../README.md', 'does-not-exist.js'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    copy_resources(out, paths=[path])
            self.assertFalse(list(out.rglob('*')))


if __name__ == '__main__':
    unittest.main()
