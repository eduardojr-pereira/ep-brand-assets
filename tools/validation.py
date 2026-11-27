"""Responsibility: Provide shared build-time JSON, field, bilingual value and local-file validation.
Boundaries: No project or badge schemas, repository root discovery, routing, rendering, publication or UI state.
"""
import json
from pathlib import PurePosixPath

LOCALES = ('en', 'pt-BR')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    def bad_constant(value):
        raise ValueError(f'Invalid JSON constant: {value}')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=bad_constant)


def fields(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected), f'Invalid fields: {label}')


def localized(value, label):
    fields(value, LOCALES, label)
    require(all(isinstance(v, str) and v.strip() for v in value.values()), f'Empty/invalid translation: {label}')


def local_file(root, value):
    require(isinstance(value, str) and bool(value), 'Expected relative file path')
    parts = value.split('/')
    require(not any(part in ('', '.', '..') for part in parts) and '\\' not in value
            and not any(c in value for c in ':?#%') and not any(ord(c) < 32 for c in value),
            f'Unsafe relative path: {value}')
    path = root
    for part in PurePosixPath(value).parts:
        path = path / part
        require(not path.is_symlink(), f'Symlink is not allowed: {value}')
    require(path.is_file() and path.resolve().is_relative_to(root.resolve()), f'Missing/unsafe file: {value}')
    return path
