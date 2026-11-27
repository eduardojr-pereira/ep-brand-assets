"""Responsibility: Prepare validated shared/local translation data and Jinja bindings.
No page composition, runtime preference, asset copying or component-specific logic.
"""
import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = json.loads((ROOT / 'config/ui.json').read_text())
LOCALES = ('en', 'pt-BR')


def dictionaries(local=None):
    shared = json.loads((ROOT / 'config/translations.json').read_text())
    local = local if local is not None else {locale: {} for locale in LOCALES}
    for source, prefix in [(shared, 'shared.'), (local, 'content.')]:
        if set(source) != set(LOCALES) or set(source['en']) != set(source['pt-BR']):
            raise ValueError('Translation keys and supported locales must match')
        for key in source['en']:
            if not key.startswith(prefix) or not re.fullmatch(r'[a-zA-Z0-9_.-]+', key):
                raise ValueError(f'Invalid translation key: {key}')
            def fields(value):
                if isinstance(value, str):
                    return set(re.findall(r'\{(\w+)\}', value))
                if isinstance(value, dict) and set(value) == {'one', 'other'} and all(isinstance(v,str) for v in value.values()):
                    if fields(value['one']) != fields(value['other']):
                        raise ValueError(f'Plural arguments differ: {key}')
                    return fields(value['one'])
                raise ValueError(f'Invalid translation: {key}')
            en, pt = (source[locale][key] for locale in LOCALES)
            if type(en) is not type(pt) or fields(en) != fields(pt):
                raise ValueError(f'Translation arguments differ: {key}')
    return {locale: {**shared[locale], **local[locale]} for locale in LOCALES}


def environment(local=None):
    data = dictionaries(local)
    env = Environment(loader=FileSystemLoader(ROOT), autoescape=select_autoescape(['html'], default_for_string=True))
    def message(key):
        value = data['en'][key]
        if not isinstance(value, str):
            raise ValueError(f'Dynamic plural requires runtime arguments: {key}')
        return {'key': key, 'text': value}
    env.globals['message'] = message
    return env


def page_config(asset_base, local=None):
    """Embed one configuration before synchronous head scripts. Escape script terminators."""
    data = {'translations': dictionaries(local), 'assetBase': asset_base, 'lottie': DEPENDENCIES['lottie']}
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return Markup('<script type="application/json" id="ui-config">' + payload + '</script>')


def head_resources(resource_base, local=None, scripts=True):
    """Resolve canonical resources at one base; the future builder owns that base."""
    base = resource_base.rstrip('/') + '/'
    asset_root = json.loads((ROOT / 'config/brand.json').read_text())['asset_root']
    tags = [page_config(base + asset_root + '/', local)] if scripts else []
    if scripts:
        tags.extend(Markup('<script src="{}"></script>').format(escape(base + name)) for name in DEPENDENCIES['head_scripts'])
    tags.extend(Markup('<link rel="stylesheet" href="{}">').format(escape(base + name)) for name in DEPENDENCIES['styles'])
    if scripts:
        tags.extend(Markup('<script defer src="{}"></script>').format(escape(base + name)) for name in DEPENDENCIES['defer_scripts'])
    return Markup('\n').join(tags)
