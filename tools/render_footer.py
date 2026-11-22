#!/usr/bin/env python3
"""Render approved EP footers; preview is read-only unless --apply is passed."""
import argparse
import base64
import datetime
import difflib
import json
import mimetypes
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- EP-FOOTER:START -->'
END = '<!-- EP-FOOTER:END -->'
ASSETS = {
    'logo_src': 'logos/logo_initials.png',
    'github_src': 'icons/github_icon.svg',
    'linkedin_src': 'icons/linkedin_icon.svg',
    'gmail_src': 'icons/gmail_icon.svg',
}


def brand_values(embed=False):
    brand = json.loads((ROOT / 'config/brand.json').read_text(encoding='utf-8'))
    values = dict(brand)
    for key, rel in ASSETS.items():
        if embed:
            data = (ROOT / 'assets' / rel).read_bytes()
            mime = mimetypes.guess_type(rel)[0] or 'application/octet-stream'
            values[key] = f'data:{mime};base64,' + base64.b64encode(data).decode('ascii')
        else:
            values[key] = brand['asset_base'].rstrip('/') + '/' + rel
    values['year'] = str(datetime.date.today().year)
    return values


def substitute(template, values):
    def replace(match):
        key = match.group(1)
        if key not in values:
            raise ValueError(f'Unknown placeholder: {key}')
        return str(values[key])
    result = re.sub(r'\{\{([a-z_]+)\}\}', replace, template)
    if '{{' in result or '}}' in result:
        raise ValueError('Unresolved placeholders remain')
    return result


def links(kind, lang, brand):
    en = lang == 'en'
    if kind == 'portfolio':
        entries = [('Knowledge Base' if en else 'Base de Conhecimento', brand['knowledge_base']),
                   ('Personal Website' if en else 'Site Pessoal', brand['website'])]
    elif kind == 'knowledge-base':
        entries = [('GitHub Portfolio' if en else 'Portfólio GitHub', brand['portfolio']),
                   ('Personal Website' if en else 'Site Pessoal', brand['website'])]
    else:
        entries = [('GitHub Portfolio' if en else 'Portfólio GitHub', brand['portfolio']),
                   ('Knowledge Base' if en else 'Base de Conhecimento', brand['knowledge_base']),
                   ('Personal Website' if en else 'Site Pessoal', brand['website'])]
    return ' &nbsp;•&nbsp; '.join(f'[**{label}**]({url})' for label, url in entries)


def render_readme(kind, lang):
    name = 'footer.en.md' if lang == 'en' else 'footer.pt-BR.md'
    template = (ROOT / 'components/markdown' / name).read_text(encoding='utf-8')
    values = brand_values()
    values['related_links'] = links(kind, lang, values)
    return substitute(template, values).rstrip() + '\n'


def replace_footer(original, footer):
    if START in original or END in original:
        if original.count(START) != 1 or original.count(END) != 1:
            raise ValueError('Invalid or duplicated footer markers')
        start = original.index(START)
        stop = original.index(END) + len(END)
        if stop < start:
            raise ValueError('Footer markers in wrong order')
        return original[:start] + footer.rstrip() + original[stop:]
    # Approved READMEs put Contact/Contato as their LAST section.
    headings = list(re.finditer(r'^## (?:Contact|Contato)\s*$', original, re.MULTILINE))
    if len(headings) != 1:
        raise ValueError('Expected exactly one existing Contact/Contato section')
    prefix = original[:headings[0].start()]
    if re.search(r'^#{1,2} (?!Contact\s*$|Contato\s*$)', original[headings[0].end():], re.MULTILINE):
        raise ValueError('Contact section is not last; refusing automatic replacement')
    if '<a id="readme-top"></a>' not in original:
        raise ValueError('Missing approved readme-top anchor; review manually')
    return prefix + footer


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode', required=True)
    r = sub.add_parser('readme', help='Preview or update an approved README footer')
    r.add_argument('--file', type=Path, help='README to update; omit to print template')
    r.add_argument('--kind', choices=['portfolio', 'knowledge-base', 'other'], required=True)
    r.add_argument('--lang', choices=['en', 'pt-BR'], required=True)
    r.add_argument('--apply', action='store_true', help='Write changes (default: dry run)')
    w = sub.add_parser('web', help='Print the web footer for embedding at build time')
    w.add_argument('--embed-assets', action='store_true', help='Use bundled image data URIs for offline use')
    w.add_argument('--css', action='store_true', help='Print CSS instead of HTML')
    args = p.parse_args()
    if args.mode == 'web':
        if args.css:
            print((ROOT / 'components/web/footer.css').read_text(encoding='utf-8'), end='')
        else:
            print(substitute((ROOT / 'components/web/footer.html').read_text(encoding='utf-8'),
                             brand_values(embed=args.embed_assets)), end='')
        return
    footer = render_readme(args.kind, args.lang)
    if not args.file:
        print(footer, end='')
        return
    if not args.file.is_file():
        p.error(f'file not found: {args.file}')
    previous = args.file.read_text(encoding='utf-8')
    updated = replace_footer(previous, footer)
    if updated == previous:
        print('No changes needed.')
        return
    if args.apply:
        # Only explicit apply can write. Caller should keep git working tree clean.
        args.file.write_text(updated, encoding='utf-8')
        print('Updated:', args.file)
    else:
        diff = difflib.unified_diff(previous.splitlines(keepends=True),
                                    updated.splitlines(keepends=True),
                                    fromfile=str(args.file), tofile=str(args.file) + ' (proposed)')
        sys.stdout.writelines(diff)
        print('\nDRY RUN: no files changed. Use --apply only after reviewing.')


if __name__ == '__main__':
    main()
