"""Responsibility: shared browser fixture, dependency loading and font validation.
No component assertions or production rendering logic.
"""
import base64
import json
import os
from pathlib import Path
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
ENV = Environment(loader=FileSystemLoader(ROOT), autoescape=select_autoescape(['html'], default_for_string=True))
DEPENDENCIES = json.loads((ROOT / 'config/ui.json').read_text())
FONT_PATHS = ('assets/fonts/manrope/Manrope.ttf', 'assets/fonts/inter/Inter.ttf')

def launch_browser(playwright):
    executable = os.getenv('UI_TEST_BROWSER') or shutil.which('chromium') or shutil.which('google-chrome')
    return playwright.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))

def load_page(page, body, theme='dark', *, css='', scripts=True):
    """Build an in-memory test document using canonical sources and manifest order."""
    styles = '\n'.join((ROOT / name).read_text() for name in DEPENDENCIES['styles'])
    missing = []
    for name in FONT_PATHS:
        path = ROOT / name
        if not path.is_file():
            missing.append(name)
            uri = 'data:font/ttf;base64,'
        else:
            uri = 'data:font/ttf;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
        styles = styles.replace('../' + name, uri)
    if missing and os.getenv('UI_TEST_ALLOW_MISSING_FONTS') != '1':
        raise AssertionError(f'Missing canonical fonts: {missing}')
    head = ''.join(f'<script>{(ROOT / name).read_text()}</script>' for name in DEPENDENCIES['head_scripts']) if scripts else ''
    # Inline classic scripts execute immediately, so place the deferred group after the body content.
    deferred = ''.join(f'<script>{(ROOT / name).read_text()}</script>' for name in DEPENDENCIES['defer_scripts']) if scripts else ''
    document = f'<!doctype html><html data-theme="{theme}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{styles}\n{css}</style>{head}</head><body>{body}{deferred}</body></html>'
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.set_content(document)
    if not missing:
        assert page.evaluate('''async () => {
          await Promise.all([document.fonts.load('400 16px Inter'), document.fonts.load('600 20px Manrope')]);
          return ['Inter','Manrope'].every(name => [...document.fonts].some(font => font.family === name && font.status === 'loaded'));
        }'''), 'Canonical fonts did not load'
    else:
        page.evaluate('document.fonts.ready')
    assert not errors, errors


def validate_contract():
    """Reject stale references, duplicate manifest entries and parallel implementations."""
    import re
    dependencies = sum((DEPENDENCIES[key] for key in ('styles', 'head_scripts', 'defer_scripts')), [])
    assert len(dependencies) == len(set(dependencies)), 'Duplicate dependencies'
    actual = {str(p.relative_to(ROOT)) for folder, suffix in [('styles', '.css'), ('scripts', '.js')] for p in (ROOT / folder).glob('*' + suffix)}
    assert set(dependencies) == actual, 'Manifest and implementation files differ'
    assert not (ROOT / 'styles' / ('motion-' + 'tokens.css')).exists(), 'Obsolete motion file'
    for name in dependencies + [str(p.relative_to(ROOT)) for p in (ROOT / 'components/web').glob('*.html')]:
        source = (ROOT / name).read_text()
        assert 'Responsibility:' in source, name
        assert not re.search(r'\b(?:ep[-:]|EP(?:Motion|Navigation|Actions)|dataset\.ep[A-Z])', source), name
        if name.endswith('.html'):
            assert not re.search(r'<(?:style|script)\b|\sstyle=', source, re.I), name
    assert '--ui-color-ink:' in (ROOT / 'styles/foundations.css').read_text()
    assert '--ui-color-ink:' not in (ROOT / 'styles/buttons.css').read_text()
    assert '--ui-distance-text:' in (ROOT / 'styles/motion.css').read_text()
    assert '--ui-distance-text:' not in (ROOT / 'styles/links.css').read_text()
    print('PASS: canonical dependencies, responsibility headers, neutral names and token ownership', flush=True)


if __name__ == '__main__':
    import subprocess
    import sys
    validate_contract()
    for path in sorted((ROOT / 'tests').glob('test_*.py')):
        print(f'=== {path.name} ===', flush=True)
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)
    print('PASS: all component suites', flush=True)
