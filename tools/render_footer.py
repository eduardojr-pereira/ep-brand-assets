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
        entries = [('Knowledge Base' if en else 'Base de Conhecimento', brand['knowledge_base'])]
    elif kind == 'knowledge-base':
        entries = [('GitHub Portfolio' if en else 'Portfólio GitHub', brand['portfolio'])]
    else:
        entries = [('GitHub Portfolio' if en else 'Portfólio GitHub', brand['portfolio']),
                   ('Knowledge Base' if en else 'Base de Conhecimento', brand['knowledge_base'])]
    return ' &nbsp;•&nbsp; '.join(f'[**{label}**]({url})' for label, url in entries)


# One Markdown layout; the two committed .md files are rendered previews.
MARKDOWN_LAYOUT = '<!-- EP-FOOTER:START -->\n## {{heading}}\n\n<div align="center">\n\n<a href="{{website}}" title="{{website_label}} — {{name}}"><img src="{{logo_src}}" alt="{{logo_label}} — {{name}}" height="90"></a>\n\n**{{name}}**\n\n*{{tagline}}*\n\n<a href="mailto:{{email}}"><img src="{{gmail_src}}" alt="{{email_label}}" height="27"></a>&nbsp;&nbsp;\n<a href="{{linkedin}}"><img src="{{linkedin_src}}" alt="LinkedIn" height="27"></a>&nbsp;&nbsp;\n<a href="{{github}}"><img src="{{github_src}}" alt="GitHub" height="27"></a>\n\n[{{invite}}]({{linkedin}})\n\n{{related_links}}\n\n</div>\n\n<p align="right"><a href="#readme-top">↑ {{back_top}}</a></p>\n\n---\n<!-- EP-FOOTER:END -->\n'
MARKDOWN_COPY = {
    'en': {'heading': 'Contact', 'website_label': 'Personal website',
           'logo_label': 'EP logo', 'email_label': 'Email',
           'invite': "Let's connect on LinkedIn to exchange ideas and opportunities.",
           'back_top': 'BACK TO TOP'},
    'pt-BR': {'heading': 'Contato', 'website_label': 'Site pessoal',
              'logo_label': 'Logo EP', 'email_label': 'E-mail',
              'invite': 'Vamos nos conectar no LinkedIn para trocar ideias e oportunidades.',
              'back_top': 'VOLTAR AO TOPO'},
}


def render_readme(kind, lang):
    if kind not in ('portfolio', 'knowledge-base', 'other'):
        raise ValueError('Unknown README kind: ' + str(kind))
    values = brand_values()
    values.update(MARKDOWN_COPY[lang])
    values['related_links'] = links(kind, lang, values)
    return substitute(MARKDOWN_LAYOUT, values).rstrip() + '\n'


def render_markdown_previews():
    # Standalone anchor is outside the markers, never injected into consumers.
    return {ROOT / 'components/markdown' / filename:
            '<a id="readme-top"></a>\n\n' + render_readme('other', lang)
            for lang, filename in (('en', 'footer.en.md'),
                                   ('pt-BR', 'footer.pt-BR.md'))}


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


def render_web_footer(embed=True):
    """Render the canonical web footer."""
    template = (ROOT / 'components/web/footer.html').read_text(
        encoding='utf-8'
    )
    return substitute(template, brand_values(embed=embed))


def render_web_css():
    """Return design-system variables before component styles, preserving CSS order."""
    paths = [ROOT / 'styles' / name for name in ('theme-tokens.css', 'typography-v2.css')]
    paths.append(ROOT / 'styles/report-navigation.css')
    paths.append(ROOT / 'components/web/footer.css')
    return '\n'.join(path.read_text(encoding='utf-8').rstrip() for path in paths) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode', required=True)
    r = sub.add_parser('readme', help='Preview or update an approved README footer')
    r.add_argument('--file', type=Path, help='README to update; omit to print template')
    r.add_argument('--kind', choices=['portfolio', 'knowledge-base', 'other'], required=True)
    r.add_argument('--lang', choices=['en', 'pt-BR'], required=True)
    r.add_argument('--apply', action='store_true', help='Write changes (default: dry run)')
    t = sub.add_parser('templates', help='Check or regenerate standalone Markdown previews')
    t.add_argument('--apply', action='store_true', help='Write generated previews')
    w = sub.add_parser('web', help='Print the web footer for embedding at build time')
    w.add_argument('--embed-assets', action='store_true', help='Use bundled image data URIs for offline use')
    w.add_argument('--css', action='store_true', help='Print CSS instead of HTML')
    args = p.parse_args()
    if args.mode == 'templates':
        stale = []
        for path, content in render_markdown_previews().items():
            if not path.is_file() or path.read_text(encoding='utf-8') != content:
                stale.append(path)
                if args.apply:
                    path.write_text(content, encoding='utf-8')
                    print('Updated:', path)
                else:
                    print('Out of date:', path)
        if not stale:
            print('Markdown previews are current.')
        if stale and not args.apply:
            return 1
        return 0
    if args.mode == 'web':
        if args.css:
            print(render_web_css(), end='')
        else:
            print(render_web_footer(embed=args.embed_assets), end='')
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
    sys.exit(main())
