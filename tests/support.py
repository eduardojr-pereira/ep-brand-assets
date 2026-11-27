"""Responsibility: shared browser fixtures, font/dependency validation, error tracking,
architectural checks and suite orchestration. No production rendering logic.
"""
import json
import os
import sys
import mimetypes
import shutil
from pathlib import Path
from urllib.parse import urlparse, unquote
from weakref import WeakKeyDictionary

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from presentation import environment, head_resources, DEPENDENCIES, dictionaries, validate_bindings
ENV = environment()
FONT_PATHS = ('assets/fonts/manrope/Manrope.ttf', 'assets/fonts/inter/Inter.ttf')
ORIGIN = 'http://127.0.0.1:18765'
_BROWSER_ERRORS = WeakKeyDictionary()


def launch_browser(playwright):
    executable = os.getenv('UI_TEST_BROWSER') or shutil.which('chromium') or shutil.which('google-chrome')
    return playwright.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))


def new_page(browser, *, locale="en-US", **options):
    """Explicit fixture locale; startup tests may request a different browser language."""
    page = browser.new_page(locale=locale, **options)
    errors = _BROWSER_ERRORS.setdefault(browser, [])
    page.on('pageerror', lambda error: errors.append(str(error)))
    return page


def close_browser(browser):
    """Fail on errors throughout every fixture, including pages already closed."""
    try:
        assert not _BROWSER_ERRORS.get(browser), _BROWSER_ERRORS.get(browser)
    finally:
        browser.close()


def load_page(page, body, theme='dark', *, css='', scripts=True, local=None, lottie=False, title='Fixture', title_key=None):
    """Serve a same-origin browser fixture from actual canonical files, without a live network."""
    missing = [name for name in FONT_PATHS if not (ROOT / name).is_file()]
    if missing:
        raise AssertionError(f'Missing canonical fonts: {missing}')
    page.emulate_media(color_scheme=theme)
    page.unroute(ORIGIN + '/**')
    head = head_resources('/',local,scripts)
    from html import escape
    title_attr = f' data-i18n-text="{escape(title_key)}"' if title_key else ''
    document = f'<!doctype html><html lang="en" data-theme="{theme}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title{title_attr}>{escape(title)}</title>{head}<style>{css}</style></head><body>{body}</body></html>'
    validate_bindings(document, local)
    def serve(route):
        path = unquote(urlparse(route.request.url).path).lstrip('/')
        if path == 'fixture':
            route.fulfill(status=200,content_type='text/html',body=document); return
        if path == 'assets/' + DEPENDENCIES['lottie']['runtime'] and not lottie:
            route.fulfill(status=404,body='Runtime intentionally unavailable (fallback test)'); return
        file = (ROOT / path).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file():
            route.fulfill(status=404,body='Not found'); return
        route.fulfill(status=200,content_type=mimetypes.guess_type(file.name)[0] or 'application/octet-stream',body=file.read_bytes())
    page.route(ORIGIN+'/**',serve)
    page.goto(ORIGIN+'/fixture',wait_until='domcontentloaded')
    assert page.evaluate('''async () => {
          await Promise.all([document.fonts.load('400 16px Inter'), document.fonts.load('600 20px Manrope')]);
          return ['Inter','Manrope'].every(name => [...document.fonts].some(font => font.family === name && font.status === 'loaded'));
        }'''), 'Canonical fonts did not load'
    assert not _BROWSER_ERRORS.get(page.context.browser), _BROWSER_ERRORS.get(page.context.browser)


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
    dictionaries()
    # No legacy local translation adapters or independent language/theme preference.
    for path in (ROOT / 'scripts').glob('*.js'):
        source = path.read_text()
        assert not re.search(r'\b(?:setLabel|setOrbitLabel|setSendLabels|connectChecks)\b',source),path.name
        if path.name not in {'theme.js','i18n.js'}:
            assert 'localStorage' not in source, path.name
        if path.name != 'i18n.js':
            assert not re.search(r'navigator\.languages?',source),path.name
    for path in (ROOT / 'styles').glob('*.css'):
        if path.name != 'motion.css':
            assert 'data-ui-smooth-scroll' not in path.read_text(),path.name
    for path in [*(ROOT/'tests').glob('*.py'),*(ROOT/'tools').glob('*.py')]:
        assert 'Responsibility:' in path.read_text(), path.name
    for name in ('navigation','buttons','interactive'):
        source = (ROOT / 'components/web' / (name + '.html')).read_text()
        assert not re.search(r'data-(?:singular|plural|play|pause)=',source),name
    assert all((ROOT/'assets'/path).is_file() for spec in DEPENDENCIES['lottie']['animations'].values() for path in ([spec['file']] if 'file' in spec else spec['variants'].values()))
    # Header and Footer are consumers, not preference or animation loaders.
    for name in ('header','footer'):
        source = (ROOT/'scripts'/f'{name}.js').read_text()
        assert not re.search(r'\b(?:fetch|loadAnimation|document\.documentElement\.lang)\b',source),name
        css = (ROOT/'styles'/f'{name}.css').read_text()
        assert '@keyframes' not in css and not re.search(r'--ui-color-[\w-]+\s*:',css),name
    brand = json.loads((ROOT/'config/brand.json').read_text())
    nav = json.loads((ROOT/'config/navigation.json').read_text())
    labels = dictionaries()['en']
    assert len({item['id'] for item in nav['sections']}) == len(nav['sections'])
    for item in nav['sections']+nav['github']+nav['repositories']+nav['social']:
        if 'brand_key' in item: assert item['brand_key'] in brand,item
        if 'animation' in item: assert item['animation'] in DEPENDENCIES['lottie']['animations'],item
        if item['label'].startswith('shared.'): assert item['label'] in labels,item
        if 'description' in item: assert item['description'] in labels,item
    import hashlib
    lottie = DEPENDENCIES['lottie']
    for path, source in [(lottie['runtime'],'build/player/lottie.min.js'),(lottie['license'],'LICENSE.md')]:
        data=(ROOT/'assets'/path).read_bytes()
        assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==lottie['source_files'][source],path
    print('PASS: canonical dependencies, responsibility headers, neutral names and token ownership', flush=True)


if __name__ == '__main__':
    import subprocess
    import sys
    validate_contract()
    for path in sorted((ROOT / 'tests').glob('test_*.py')):
        print(f'=== {path.name} ===', flush=True)
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)
    print('PASS: all component suites', flush=True)
