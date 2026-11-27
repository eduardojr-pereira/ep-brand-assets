"""Responsibility: Manage canonical badge metadata, active IDs and technology ordering.
Boundaries: No SVG generation, page building, language/theme preference or publication.
"""
import re
from pathlib import Path
from validation import read_json

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = frozenset({'technologies', 'licenses', 'status'})

def load_catalog(root=ROOT):
    data = read_json(Path(root) / 'config/badges.json')
    ids, paths = set(), set()
    for e in data['entries']:
        ident, category = e['id'], e['category']
        if not re.fullmatch(r'[a-z0-9_]+', ident) or ident in ids:
            raise ValueError(f'Invalid or duplicate badge ID: {ident}')
        if category not in ACTIVE or e['path'] != f'assets/badges/{category}/{ident}.svg' or e['path'] in paths:
            raise ValueError(f'Invalid or duplicate badge path: {ident}')
        if 'legacy_only' in e:
            raise ValueError(f'Obsolete compatibility metadata: {ident}')
        ids.add(ident); paths.add(e['path'])
    return data

def technology_ids(ids, catalog=None):
    """Deduplicate stable IDs, then stable partition: artwork before text-only."""
    entries = {e['id']: e for e in (catalog or load_catalog())['entries']}
    unique = list(dict.fromkeys(ids))
    for ident in unique:
        if ident not in entries or entries[ident]['category'] != 'technologies':
            raise ValueError(f'Unknown technology: {ident}')
    return [ident for ident in unique if entries[ident]['icon']] + [ident for ident in unique if not entries[ident]['icon']]

def active_entry(ident, catalog=None):
    entries = {e['id']: e for e in (catalog or load_catalog())['entries']}
    if ident not in entries or entries[ident]['category'] not in ACTIVE:
        raise ValueError(f'Not an active graphical badge: {ident}')
    return entries[ident]
