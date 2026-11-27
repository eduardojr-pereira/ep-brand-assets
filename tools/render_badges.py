"""Responsibility: Offline SVG maintenance from the canonical manifest and prepared PNGs.
Checks by default. Explicit writes only; no network, source preparation, build or publication.
"""
import argparse
import base64
import hashlib
import re
import struct
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape, quoteattr
from badge_catalog import ROOT, ACTIVE, load_catalog, active_entry

NS = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def inside(root, name):
    p = (root/name).resolve()
    require(p.is_relative_to(root.resolve()), f'Path outside catalog: {name}')
    return p

def contrast(bg, fg):
    def luminance(s):
        require(re.fullmatch(r'#[0-9A-Fa-f]{6}',s), f'Invalid color: {s}')
        channels = [int(s[i:i+2],16)/255 for i in (1,3,5)]
        return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip((.2126,.7152,.0722), channels))
    a,b=sorted((luminance(bg),luminance(fg)))
    return (b+.05)/(a+.05)

def png_data(root, path):
    raw = inside(root,path).read_bytes()
    require(raw[:8]==b'\x89PNG\r\n\x1a\n' and raw[12:16]==b'IHDR' and len(raw)>24, f'Not a prepared PNG: {path}')
    w,h=struct.unpack('>II',raw[16:24]); require(w>0 and h>0,f'Invalid PNG size: {path}')
    return base64.b64encode(raw).decode('ascii')

def validate_entry(e, root):
    ident=e['id']; width=e['width']; mode=e['mode']; category=e['category']; label=e['label']
    require(isinstance(width,int) and not isinstance(width,bool) and width>0 and isinstance(label,str) and bool(label.strip()),f'Invalid size or label: {ident}')
    if mode!='image_direct':
        require(contrast(e['background'],e['foreground'])>=4.5, f'Contrast below 4.5:1: {ident}')
    if e.get('theme_colors'):
        for c in e['theme_colors'].values():
            require(contrast(c['background'],c['foreground'])>=4.5,f'Theme contrast: {ident}')
        c=e['theme_colors']['light']; require(c['background'].lower()==e['background'].lower() and c['foreground'].lower()==e['foreground'].lower(),f'Light colors disagree: {ident}')
    if category=='technologies':
        if e['icon']:
            require(mode not in {'text','license_split'} and bool(e['source_path']) and bool(e['source']) and bool(e['source_sha256']),f'Artwork provenance missing: {ident}')
            require(hashlib.sha256(inside(root,e['source_path']).read_bytes()).hexdigest()==e['source_sha256'], f'Original checksum mismatch: {ident}')
            png_data(root,e['icon'])
            require(width>(4 if mode=='image_direct' else 28),f'Insufficient artwork width: {ident}')
        else:
            require(mode=='text' and e['approved_text_only'] and e['background'].lower()=='#9d603b' and e['foreground'].lower()=='#ffffff',f'Text-only technology not approved: {ident}')
    elif category=='licenses':
        require(mode=='license_split' and 0<e['prefix_width']<width and e['prefix'] and not e['icon'],f'Invalid split license: {ident}')
        for c in e['theme_prefix'].values(): require(contrast(c['background'],c['foreground'])>=4.5,f'Prefix contrast: {ident}')
    else:
        require(mode=='text' and not e['icon'],f'Unexpected localized graphic: {ident}')

def render(e, style, root=ROOT):
    root=Path(root); validate_entry(e,root)
    require(style['height']==20 and style['icon_box']==14 and style['font_size']==11 and style['shape']=='flat-square', 'Unapproved badge geometry')
    w=e['width']; mode=e['mode']; label=e['label']; bg=e['background']; fg=e['foreground']; font=quoteattr(style['font_family'])
    title=f"{e['prefix']} — {label}" if mode=='license_split' else label
    parts=[f'<svg xmlns="{NS}" xmlns:xlink="{XLINK}" width="{w}" height="20" viewBox="0 0 {w} 20" role="img" aria-label={quoteattr(title)}><title>{escape(title)}</title>']
    theme=e.get('theme_colors'); prefix=e.get('theme_prefix')
    if theme:
        c=theme['dark']; css=f".ep-bg {{fill:{c['background']}}} .ep-fg {{fill:{c['foreground']}}}"
        if prefix:
            p=prefix['dark']; css+=f" .ep-prefix-bg {{fill:{p['background']}}} .ep-prefix-fg {{fill:{p['foreground']}}}"
        parts.append('<style>@media (prefers-color-scheme: dark) { '+css+' }</style>')
    bg_class=' class="ep-bg"' if theme else ''; fg_class=' class="ep-fg"' if theme else ''
    parts.append(f'<rect width="{w}" height="20" fill="{bg}"{bg_class}/>')
    def text(x,content):
        return f'<text x="{x}" y="14" font-family={font} font-size="11" fill="{fg}"{fg_class}>{escape(content)}</text>'
    if mode=='license_split':
        pw=e['prefix_width']; p=prefix['light']
        parts.append(f'<rect width="{pw}" height="20" class="ep-prefix-bg" fill="{p["background"]}"/>')
        parts.append(f'<text x="{pw/2}" y="14" text-anchor="middle" font-family={font} font-size="11" class="ep-prefix-fg" fill="{p["foreground"]}">{escape(e["prefix"])}</text>')
        parts.append(text(pw+7,label))
    elif e['icon']:
        image=png_data(root,e['icon'])
        if mode=='image_direct':
            parts.append(f'<image x="2" y="1" width="{w-4}" height="18" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{image}"/>')
        else:
            parts.append('<rect width="24" height="20" fill="#ffffff"/>')
            parts.append(f'<image x="5" y="3" width="14" height="14" xlink:href="data:image/png;base64,{image}"/>')
            parts.append(text(28,label))
    else: parts.append(text(5,label))
    return (''.join(parts)+'</svg>\n').encode('utf-8')

def signature(raw):
    """Compare semantic XML, allowing serialization and color-case differences only."""
    def walk(n):
        attrs=dict(n.attrib)
        for k in ('fill','stroke'):
            if k in attrs: attrs[k]=attrs[k].lower()
        t=(n.text or '').strip()
        if n.tag==f'{{{NS}}}style':
            t=re.sub(r'#[0-9a-fA-F]{6}',lambda m:m[0].lower(),t)
            t=re.sub(r'\s+','',t)
        return n.tag, attrs, t, tuple(walk(child) for child in n)
    return walk(ET.fromstring(raw))

def verify(root=ROOT, ids=None):
    root=Path(root); catalog=load_catalog(root); entries=catalog['entries']; byid={e['id']:e for e in entries}
    selected=entries if ids is None else [byid[i] for i in ids]
    errors=[]
    for e in selected:
        try:
            expected=render(e,catalog['style'],root)
            actual=inside(root,e['path']).read_bytes()
            require(signature(actual)==signature(expected),f'SVG differs from canonical render: {e["id"]}')
        except (ValueError,KeyError,OSError,ET.ParseError) as exc: errors.append(str(exc))
    if ids is None:
        paths={str(p.relative_to(root)) for p in (root/'assets/badges').rglob('*.svg')}
        expected={e['path'] for e in entries}
        if paths!=expected: errors.append(f'Catalog/path mismatch: {sorted(paths^expected)}')
        for category in ('status',):
            group={e['id'] for e in entries if e['category']==category}
            for ident in group:
                if ident.endswith('_en'): other=ident[:-3]+'_pt_br'
                elif ident.endswith('_pt_br'): other=ident[:-6]+'_en'
                else: other=''
                if other not in group: errors.append(f'Missing locale pair: {ident}')
    if errors: raise ValueError('\n'.join(errors))
    return len(selected)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--id',action='append',dest='ids',help='Canonical graphical badge ID (repeatable)')
    p.add_argument('--all',action='store_true',help='All graphical badges; for checks without IDs all entries are verified')
    p.add_argument('--write',action='store_true',help='Explicitly generate selected active SVGs')
    p.add_argument('--check',action='store_true',help='Read-only validation (default)')
    a=p.parse_args()
    if a.ids and a.all or a.write and a.check or a.write and not (a.ids or a.all): p.error('Choose IDs or --all; explicit selection required for --write')
    c=load_catalog(); ids=list(dict.fromkeys(a.ids)) if a.ids else ([e['id'] for e in c['entries'] if e['category'] in ACTIVE] if a.all else None)
    try:
        if a.write:
            # Preflight the complete selected set before any writes.
            rendered=[(active_entry(i,c),render(active_entry(i,c),c['style'])) for i in ids]
            for e,raw in rendered:
                out=inside(ROOT,e['path']); out.parent.mkdir(parents=True,exist_ok=True)
                if not out.exists() or out.read_bytes()!=raw: out.write_bytes(raw); print('GENERATED',e['path'])
            print(f'WRITE OK — {verify(ids=ids)} active badges verified; no publication')
        else:
            print(f'PASS: {verify(ids=ids)} SVG badges match catalog and original-source hashes; read-only')
    except (ValueError,KeyError,OSError) as exc: raise SystemExit(str(exc))

if __name__=='__main__': main()
