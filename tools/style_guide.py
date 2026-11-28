"""Responsibility: Prepare Style Guide-only presentation context using canonical APIs.
Boundaries: No shared UI implementation, project analysis or publication orchestration.
"""
import csv
import json
from pathlib import Path
from badge_catalog import load_catalog
from plotly_presentation import chart_payload
from artifact_preview import prepare_artifact
from validation import require
from resources import PLOTLY_RUNTIME
ROOT=Path(__file__).resolve().parents[1]

def validate_guide_sections(ids, sections):
    require(ids == ['guide-intro', 'foundations', 'actions', 'analytical', 'motion', 'identity', 'components', 'visualization', 'report-content', 'contact-states'], 'Style Guide sections must match the declared composition')
    require([len(s['paragraphs']) for s in sections] == [1, 5, 5, 11, 14, 9, 16, 15, 14, 11], 'Incomplete Style Guide demonstration copy')


def guide_context(base,local,env):
    extra={}
    groups = {name: [] for name in ('technologies', 'licenses', 'status')}
    for entry in load_catalog()['entries']:
        groups[entry['category']].append({'src': base + entry['path'], 'label': entry['label']})
    extra['guide_badges'] = groups
    extra.update(guide_runtime_href=base+PLOTLY_RUNTIME,guide_demo_href=base+'style_guide/demo.js',guide_layout_href=base+'style_guide/layout.css')
    with (ROOT/'style_guide/samples/observations.csv').open(encoding='utf-8',newline='') as stream:
        reader=csv.DictReader(stream)
        fields=reader.fieldnames or []
        require(fields == ['period','value_a','value_b'], 'Unexpected specimen CSV schema')
        observations=list(reader)
    periods=[int(row[fields[0]]) for row in observations]
    series=[[int(row[field]) for row in observations] for field in fields[1:]]
    summary={'synthetic':True,'observations':len(periods),'series':len(series)}
    require(json.loads((ROOT/'style_guide/samples/summary.json').read_text(encoding='utf-8'))==summary, 'Stale specimen summary; regenerate derived artifacts from the CSV')
    extra['guide_summary']=summary
    figure={'data':[{'type':'scatter','mode':'lines+markers','x':periods,'y':values} for values in series],'layout':{'height':360,'margin':{'l':60,'r':25,'t':65,'b':60}}}
    keys='content.section.7.paragraph.'
    extra['guide_line']=chart_payload('guide-line',figure,palette='ep-muted-pastel',local=local,translations={'layout':{'title.text':keys+'1','xaxis.title.text':keys+'2','yaxis.title.text':keys+'3'},'traces':[{'index':0,'fields':{'name':keys+'4'}},{'index':1,'fields':{'name':keys+'5'}}]})
    heat={'data':[{'type':'heatmap','z':[[1,2,4],[2,4,6],[4,6,9]]}],'layout':{'height':350,'margin':{'l':55,'r':25,'t':60,'b':45}}}
    extra['guide_heat']=chart_payload('guide-heat',heat,local=local,colors=[{'trace':0,'path':'colorscale','palette':'nuuk'}],translations={'layout':{'title.text':keys+'7'}})
    files=['style_guide/samples/observations.csv','style_guide/samples/summary.json']
    items=[]
    for name in files:
        item=prepare_artifact(ROOT,name,set(files),env.globals['message']('content.section.8.paragraph.4'));item['href']=base+name;items.append(item)
    extra['guide_files']=items
    extra['guide_status_en']=[b for b in groups['status'] if b['src'].endswith('_en.svg')]
    extra['guide_status_pt']=[b for b in groups['status'] if b['src'].endswith('_pt_br.svg')]
    extra['guide_evidence']={kind:{theme:base+'style_guide/samples/evidence-'+kind+'-'+theme+'.svg' for theme in ('dark','light')} for kind in ('line','bar')}
    kinds={'categorical':10,'sequential':11,'diverging':12,'multi-sequential':13,'cyclic':14}
    catalog=json.loads((ROOT/'config/colormaps.json').read_text(encoding='utf-8'))['palettes']
    extra['guide_palettes']=[{'name':ident,'kind_index':kinds[v['kind']],**{theme:base+'style_guide/samples/palette-'+ident+'-'+(theme if v['kind']=='categorical' else 'shared')+'.svg' for theme in ('dark','light')}} for ident,v in catalog.items()]
    return extra
