"""Responsibility: Validate chart presentation bindings, resolve analytical palettes from the canonical catalog and serialize inert chart specifications.
Boundaries: No chart calculation, runtime distribution or page building.
"""
import json
import re
from pathlib import Path
from markupsafe import Markup
from presentation import ROOT, dictionaries, static_message, inert_json

LAYOUT_TEXT = re.compile(r'(?:title\.text|legend\.title\.text|[xy]axis\d*\.(?:title\.text|ticktext|ticksuffix|tickprefix)|(?:coloraxis\d*\.colorbar|scene\d*\.[xyz]axis)\.(?:title\.text|ticktext)|annotations\[\d+\]\.text|updatemenus\[\d+\]\.buttons\[\d+\]\.label|sliders\[\d+\]\.(?:steps\[\d+\]\.label|currentvalue\.prefix|currentvalue\.suffix)|[xy]axis\d*\.rangeselector\.buttons\[\d+\]\.label)')
TRACE_TEXT = re.compile(r'(?:name|text|hovertext|hovertemplate|texttemplate|(?:marker\.)?colorbar\.title\.text|(?:marker\.)?colorbar\.ticktext|legendgrouptitle\.text)')
TRACE_COLOR = re.compile(r'(?:marker\.color|marker\.line\.color|line\.color|fillcolor|(?:marker\.)?colorscale)')


def chart_payload(ident, figure, *, translations=None, colors=(), palette=None, config=None, local=None, root=ROOT):
    """Return inert JSON. `figure` is a JSON-compatible Plotly figure, not a notebook or HTML export."""
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', ident):
        raise ValueError('Invalid chart ID')
    if not isinstance(figure, dict) or not isinstance(figure.get('data'), list) or not isinstance(figure.get('layout', {}), dict):
        raise ValueError('Expected Plotly figure data and layout')
    if figure.get('frames'):
        raise ValueError('Animated figures need a project-specific integration')
    if config is not None and not isinstance(config, dict):
        raise ValueError('Invalid chart config')
    translations = translations or {}
    if set(translations) - {'layout', 'traces'}:
        raise ValueError('Unknown translation group')
    messages = dictionaries(local)
    def get_field(obj,path):
        for part in re.sub(r'\[(\d+)\]',r'.\1',path).split('.'):
            if isinstance(obj,dict): obj=obj.get(part)
            elif isinstance(obj,list) and part.isdigit() and int(part)<len(obj): obj=obj[int(part)]
            else: return None
        return obj

    def key_check(value, path, container, trace=False):
        array=isinstance(value,list)
        ticktext=path.endswith('ticktext')
        per_point=trace and path in {'text','hovertext','hovertemplate','texttemplate'}
        if (ticktext and not array) or (array and not (ticktext or per_point)):
            raise ValueError(f'Invalid chart message type: {path}')
        if array:
            if ticktext:
                ticks=get_field(container,path.removesuffix('ticktext')+'tickvals')
                expected=len(ticks) if isinstance(ticks,list) else None
            else:
                # Determine cardinality only for unambiguous flat coordinate data.
                candidates=[container.get(k) for k in ('x','y','labels','values','lat','lon','r','theta')]
                lengths={len(v) for v in candidates if isinstance(v,list) and all(not isinstance(x,(list,dict)) for x in v)}
                expected=next(iter(lengths)) if len(lengths)==1 and not isinstance(container.get('z'),list) else None
            if expected is not None and len(value)!=expected:
                raise ValueError(f'Chart message cardinality differs: {path}')
        for key in value if array else [value]: static_message(messages,key)
    for path, value in translations.get('layout', {}).items():
        if not LAYOUT_TEXT.fullmatch(path): raise ValueError(f'Unsupported layout translation: {path}')
        key_check(value,path,figure.get('layout',{}))
    used=set()
    for item in translations.get('traces', []):
        index=item['index']
        if type(index) is not int or not 0<=index<len(figure['data']) or index in used: raise ValueError('Invalid/duplicate trace index')
        used.add(index)
        for path,value in item['fields'].items():
            if not TRACE_TEXT.fullmatch(path): raise ValueError(f'Unsupported trace translation: {path}')
            key_check(value,path,figure['data'][index],trace=True)
    root=Path(root)
    catalog=json.loads((root/'config/colormaps.json').read_text())['palettes']
    def categorical(name):
        v=catalog[name]
        if v['kind']!='categorical': raise ValueError('Expected categorical palette')
        return {theme:v[theme] for theme in ('light','dark')}
    colorway=categorical(palette) if palette else None
    color_bindings=[]; used=set()
    for item in colors:
        index,path,name=item['trace'],item['path'],item['palette']
        if type(index) is not int or not 0<=index<len(figure['data']) or not TRACE_COLOR.fullmatch(path) or (index,path) in used:
            raise ValueError('Invalid/duplicate trace color binding')
        used.add((index,path))
        if path.endswith('colorscale'):
            v=catalog[name]; rgb=v.get('rgb')
            if not rgb or len(rgb)<2: raise ValueError('Expected continuous palette')
            scale=[[i/(len(rgb)-1),'rgb('+','.join(str(round(x*255)) for x in c)+')'] for i,c in enumerate(rgb)]
            variants={theme:scale for theme in ('light','dark')}
        else:
            variants={}; index_spec=item['index']
            for theme, values in categorical(name).items():
                def pick(i):
                    if type(i) is not int or not 0<=i<len(values): raise ValueError('Palette index out of bounds')
                    return values[i]
                variants[theme]=[pick(i) for i in index_spec] if isinstance(index_spec,list) else pick(index_spec)
        color_bindings.append({'trace':index,'path':path,'values':variants})
    payload={'id':ident,'data':figure['data'],'layout':figure.get('layout',{}),'config':config or {},'translations':translations,'colorway':colorway,'colors':color_bindings}
    encoded=inert_json(payload)
    return Markup('<script type="application/json" data-ui-plotly-spec>'+encoded+'</script>')
