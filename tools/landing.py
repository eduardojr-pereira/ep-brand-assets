"""Responsibility: Prepare explicit landing content, authorized catalog cards and consumer media.
Boundaries: No preference state, analytical execution, URL discovery, generic build orchestration or deployment.
"""
from pathlib import PurePosixPath
from validation import fields, localized, read_json, require, local_file
from routing import project_report_path, relative_href, project_source_links
from catalog import load_projects
from badge_catalog import load_catalog, active_entry
from presentation import inert_json, dictionaries
from markupsafe import Markup


def landing_data(source, plan):
    """Only explicit build plans can include consumer-owned landing content."""
    if 'landing_content' not in plan:
        return None
    require(plan['landing_content'] == 'landing/content.json', 'Invalid landing content path')
    data = read_json(local_file(source, plan['landing_content']))
    fields(data, {'schema_version','copy','about','media','outlines','featured'}, 'landing content')
    require(type(data['schema_version']) is int and data['schema_version'] == 1, 'Unsupported landing content')
    return data


def asset_paths(source, data):
    if data is None:
        return []
    fields(data['media'], {'portrait','video','poster','contact_base','contact_lit'}, 'landing media')
    paths = list(data['media'].values())
    for entry in data['featured'].values():
        fields(entry, {'metrics','frames'}, 'featured item')
        for frame in entry['frames']:
            fields(frame, {'caption','images'}, 'frame')
            fields(frame['images'], {'dark_en','dark_pt','light_en','light_pt'}, 'frame variants')
            paths.extend(frame['images'].values())
    for path in paths:
        require(isinstance(path,str) and path.startswith('landing/assets/') and len(PurePosixPath(path).parts)==3 and PurePosixPath(path).suffix in {'.png','.jpg','.webp','.svg','.mp4'}, 'Unsafe landing media')
        local_file(source,path)
    return sorted(set(paths))


def badge_paths(source, data):
    if data is None:
        return []
    catalog=load_catalog()
    return sorted({active_entry(ident,catalog)['path'] for project in load_projects(source,catalog) for ident in project['technologies']})


def landing_context(source, data, base, local, brand, report_routes):
    if data is None:
        return {}
    asset_paths(source,data)
    def ref(key,value):
        key='content.landing.'+key
        localized(value,key)
        require(key not in local['en'], 'Duplicate landing translation: '+key)
        for lang in local:
            local[lang][key]=value[lang]
        return {'key':key,'text':value['en']}
    def shared(key):
        return {'key':key,'text':dictionaries()['en'][key]}
    copy={key:ref(key,value) for key,value in data['copy'].items()}
    # Institutional hero lines derive from the one bilingual signature.
    shared_copy=dictionaries()
    for i,key in enumerate(('one','two','three')):
        values={lang:shared_copy[lang]['shared.brand.tagline'].split(' · ')[i].upper() for lang in local}
        # These keys are derived, never maintained as a second copy in the consumer.
        copy['hero.'+key]=ref('signature.'+key,values)
    catalog=load_catalog(); records=load_projects(source,catalog); projects=[]; selected=[]; areas={}
    require(set(data['featured']).issubset({p['path'] for p in records if p['featured']}),'Unapproved featured content')
    kinds={'selected_projects':'selected','learning_labs':'learning','independent_experiments':'independent'}
    for index,record in enumerate(records):
        path=record['path']; prefix=f'project.{index}'; kind=kinds[path.split('/')[0]]
        title=ref(prefix+'.title',record['name']); desc=ref(prefix+'.description',record['description']); topic_refs=[]
        for topic in record['topics']:
            if topic['id'] not in areas:
                areas[topic['id']]=ref('area.'+topic['id'],topic['label'])
            topic_refs.append(areas[topic['id']])
        badges=[]
        for ident in record['technologies']:
            entry=active_entry(ident,catalog); label=entry['label']
            badges.append({'src':base+entry['path'],'label':label})
        source_links=project_source_links(brand['portfolio'],record)
        # Declared reports are local destinations; existing public links are
        # retained only for the already-supported partial preview.
        report=(relative_href('index.html',report_routes[path]) if path in report_routes
                else brand['website'].rstrip('/')+'/'+project_report_path(path))
        links=[]
        if source_links['notebook']:
            links.append({'label':shared('shared.project.notebook'),'href':source_links['notebook'],'primary':False})
        links.append({'label':shared('shared.project.documentation'),'href':source_links['documentation']['en'],'href_pt':source_links['documentation']['pt-BR'],'primary':False})
        links.append({'label':shared('shared.project.view'),'href':report,'primary':True})
        p={'title':title,'description':desc,'collection':kind,'collection_label':copy['collection.'+kind],'areas':list(t['id'] for t in record['topics']),'topics':topic_refs,'badges':badges,'links':links,'href':report}
        projects.append(p)
        if record['featured']:
            entry=data['featured'].get(path)
            require(entry is not None,'Featured record requires approved landing presentation: '+path)
            # Display split title from metadata, not a second project description.
            parts={lang:record['name'][lang].split(' — ',1) for lang in local}
            title=ref(prefix+'.feature.title',{lang:parts[lang][0] for lang in local})
            subtitle=ref(prefix+'.feature.subtitle',{lang:parts[lang][-1] for lang in local}) if all(len(v)==2 for v in parts.values()) else None
            frames=[]; metrics=[]
            for i,frame in enumerate(entry['frames']):
                caption=ref(f'{prefix}.frame.{i}',frame['caption'])
                frames.append({'src':frame['images']['dark_en'],'alt':caption,'caption':caption,**frame['images']})
            for i,m in enumerate(entry['metrics']):
                fields(m,{'label','value'},'metric')
                metrics.append({k:ref(f'{prefix}.metric.{i}.{k}',m[k]) for k in ('label','value')})
            selected.append({**p,'title':title,'subtitle':subtitle,'frames':frames,'metrics':metrics})
    panels=[]
    for i,panel in enumerate(data['about']):
        require(set(panel) in ({'label','eyebrow','title','body','detail'},{'label','eyebrow','title','body','detail','link'}),'Invalid about panel')
        panels.append({k:ref(f'about.{i}.{k}',v) for k,v in panel.items()})
    # Vector paths are inert geometric data; not code. Serialize using shared safe helper.
    outlines=data['outlines']
    for label,shape in outlines.items():
        fields(shape,{'d','width','focus'},'CTA outline')
        require(isinstance(shape['d'],str) and all(isinstance(shape[k],(int,float)) and shape[k]>0 for k in ('width','focus')),'Invalid CTA geometry')
    return {'landing':{'copy':copy,'projects':projects,'selected':selected,'areas':[{'value':k,'label':v} for k,v in areas.items()],'about':panels,'media':data['media'],'outlines':Markup(inert_json(outlines))}}
