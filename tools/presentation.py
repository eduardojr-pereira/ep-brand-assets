"""Responsibility: Validate shared/local translations and bindings, prepare bilingual search metadata, page configuration and ordered head resources.
Boundaries: No page composition, runtime preference, asset copying or component-specific logic.
"""
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape
from validation import LOCALES, read_json

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = read_json(ROOT / 'config/ui.json')


MESSAGE_ARGS = re.compile(r'(?<!%)\{(\w+)\}')


def static_message(messages, key):
    """Resolve a message valid in both locales and requiring no runtime arguments."""
    if not isinstance(key,str) or any(not isinstance(messages[lang].get(key),str) or MESSAGE_ARGS.search(messages[lang][key]) for lang in LOCALES):
        raise ValueError(f'Static binding requires a complete message: {key}')
    return messages['en'][key]


def inert_json(data):
    """Encode inert script data; never permit literal HTML terminators or NaN."""
    return json.dumps(data,ensure_ascii=False,allow_nan=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')

def dictionaries(local=None):
    shared = read_json(ROOT / 'config/translations.json')
    local = local if local is not None else {locale: {} for locale in LOCALES}
    for source, prefix in [(shared, 'shared.'), (local, 'content.')]:
        if set(source) != set(LOCALES) or set(source['en']) != set(source['pt-BR']):
            raise ValueError('Translation keys and supported locales must match')
        for key in source['en']:
            if not key.startswith(prefix) or not re.fullmatch(r'[a-zA-Z0-9_.-]+', key):
                raise ValueError(f'Invalid translation key: {key}')
            def fields(value):
                if isinstance(value, str):
                    return set(MESSAGE_ARGS.findall(value))
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
        return {'key': key, 'text': static_message(data,key)}
    def search_text(refs):
        parts = []
        for ref in refs:
            if isinstance(ref, dict):
                parts.extend(data[locale][ref['key']] for locale in LOCALES)
            elif ref is not None:
                parts.append(str(ref))
        return ' '.join(dict.fromkeys(parts))
    env.globals.update(message=message, search_text=search_text)
    return env


def validate_bindings(html, local=None):
    """Reject missing/invalid static binding keys before publishing generated HTML."""
    messages = dictionaries(local)
    targets = {'text', 'aria-label', 'placeholder', 'alt', 'title'}
    class Validator(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for name, key in attrs:
                if not name.startswith('data-i18n-'):
                    continue
                target = name.removeprefix('data-i18n-')
                if target not in targets or not key or key not in messages['en']:
                    raise ValueError(f'Invalid translation binding: {name}={key}')
                static_message(messages,key)
        handle_startendtag = handle_starttag
    validator = Validator()
    validator.feed(str(html))
    validator.close()


def page_config(asset_base, local=None):
    """Embed one configuration before synchronous head scripts. Escape script terminators."""
    data = {'translations': dictionaries(local), 'assetBase': asset_base, 'lottie': DEPENDENCIES['lottie'], 'plotly': DEPENDENCIES['plotly']}
    payload = inert_json(data)
    return Markup('<script type="application/json" id="ui-config">' + payload + '</script>')


def head_resources(resource_base, local=None, scripts=True):
    """Resolve canonical resources at one base; the builder owns that base."""
    base = resource_base.rstrip('/') + '/'
    asset_root = read_json(ROOT / 'config/brand.json')['asset_root']
    tags = [page_config(base + asset_root + '/', local)] if scripts else []
    if scripts:
        tags.extend(Markup('<script src="{}"></script>').format(escape(base + name)) for name in DEPENDENCIES['head_scripts'])
    tags.extend(Markup('<link rel="stylesheet" href="{}">').format(escape(base + name)) for name in DEPENDENCIES['styles'])
    if scripts:
        tags.extend(Markup('<script defer src="{}"></script>').format(escape(base + name)) for name in DEPENDENCIES['defer_scripts'])
    return Markup('\n').join(tags)
