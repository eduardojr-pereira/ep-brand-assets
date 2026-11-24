#!/usr/bin/env python3
"""EP canonical SVG badge renderer; standalone SVG follows color scheme."""
import base64,json,html,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def render(e, theme=None):
    w=e['width']; label=html.escape(e['label']); bg=e['background']; fg=e['foreground']; icon=e['icon']; start=5
    prefix=e.get('prefix'); accessible=html.escape((prefix+' — ' if prefix else '')+e['label'],quote=True)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="20" viewBox="0 0 {w} 20" role="img" aria-label="{accessible}"><title>{accessible}</title>']
    variants=e.get('theme_colors')
    prefixes=e.get('theme_prefix')
    if variants:
        selected=variants[theme or 'light']; bg,fg=selected['background'],selected['foreground']
    if theme is None and (variants or prefixes):
        rules=[]
        for colors,cls in ((variants,'ep'),(prefixes,'ep-prefix')):
            if colors:
                dark=colors['dark']; rules.extend([f'.{cls}-bg {{fill:{dark["background"]}}}',f'.{cls}-fg {{fill:{dark["foreground"]}}}'])
        parts += ['<style>@media (prefers-color-scheme: dark) { '+ ' '.join(rules)+' }</style>']
    parts += [f'<rect width="{w}" height="20" fill="{bg}"'+(' class="ep-bg"' if variants else '')+'/>']
    if prefix:
        selected=prefixes[theme or 'light']; pw=e['prefix_width']; parts += [f'<rect width="{pw}" height="20" class="ep-prefix-bg" fill="{selected["background"]}"/>',f'<text x="{pw/2}" y="14" text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" class="ep-prefix-fg" fill="{selected["foreground"]}">{html.escape(prefix)}</text>'];start=pw+7
    elif e.get('mode') == 'image_direct':
        b64=base64.b64encode((ROOT/icon).read_bytes()).decode('ascii')
        parts += [f'<image x="2" y="1" width="{w-4}" height="18" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/png;base64,{b64}"/></svg>']
        return ''.join(parts)+'\n'
    elif icon:
        b64=base64.b64encode((ROOT/icon).read_bytes()).decode('ascii')
        parts += ['<rect width="24" height="20" fill="#ffffff"/>',f'<image x="5" y="3" width="14" height="14" xlink:href="data:image/png;base64,{b64}"/>'];start=28
    parts += [f'<text x="{start}" y="14" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" fill="{fg}"'+(' class="ep-fg"' if variants else '')+f'>{label}</text></svg>']
    return ''.join(parts)+'\n'

def main():
    config=json.loads((ROOT/'config/badges.json').read_text())
    for e in config['entries']:
        p=ROOT/e['path'];p.parent.mkdir(parents=True,exist_ok=True);s=render(e);ET.fromstring(s);p.write_text(s,encoding='utf-8')
    print(f"Rendered {len(config['entries'])} badges.")
if __name__=='__main__': main()
