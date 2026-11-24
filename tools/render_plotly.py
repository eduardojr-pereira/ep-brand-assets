"""Canonical analytical palettes and Plotly renderer."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REG = json.loads((ROOT / 'config/colormaps.json').read_text(encoding='utf-8'))
def analytical_palette(name='ep-muted-pastel', theme='dark'):
    p = REG['palettes'][name]
    if p['kind'] == 'categorical':
        return p[theme].copy()
    return [[i/(len(p['rgb'])-1), 'rgb(%s)' % ','.join(str(round(v*255,5)) for v in rgb)] for i,rgb in enumerate(p['rgb'])]
def render_css():
    blocks = ['/* Generated from config/colormaps.json. Do not edit. */', ':root { '+ ' '.join(f'--ep-muted-reference-{i}: {c};' for i,c in enumerate(REG['palettes']['ep-muted-pastel']['dark']))+' }']
    for theme in ('dark','light'):
        selector = ':root, :root[data-theme="dark"]' if theme == 'dark' else ':root[data-theme="light"]'
        lines = [selector+' {']
        for name,p in REG['palettes'].items():
            if p['kind']=='categorical':
                lines.extend(f'  --ep-{name}-{i}: {c};' for i,c in enumerate(p[theme]))
        blocks.append('\n'.join(lines+['}']))
    return '\n'.join(blocks)+'\n'
def render_plotly(fig, plot_id):
    from plotly.io import to_html
    html = to_html(fig, full_html=False, include_plotlyjs=False, div_id=plot_id,
        config={'responsive':True,'displaylogo':False,'modeBarButtonsToRemove':['lasso2d','select2d']})
    if html.count('Plotly.newPlot(')!=1:
        raise ValueError('Unexpected Plotly HTML serialization')
    return html.replace('Plotly.newPlot(', 'EPPlotlyTheme.newPlot(', 1)
def plotly_head():
    # Standalone HTML uses the same canonical source, embedded at build time.
    css = '\n'.join((ROOT / x).read_text(encoding='utf-8') for x in ('styles/theme-tokens.css','styles/colormaps.css','styles/plotly-theme.css'))
    js = '\n'.join((ROOT / x).read_text(encoding='utf-8') for x in ('scripts/theme-init.js','scripts/plotly-i18n.js','scripts/plotly-theme.js'))
    return '<!-- EP-PLOTLY-HEAD-START --><style>'+css+'</style><script>'+js+'</script><!-- EP-PLOTLY-HEAD-END -->'
