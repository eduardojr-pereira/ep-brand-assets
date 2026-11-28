"""Responsibility: Load and validate the portfolio registry and per-project metadata.
Boundaries: No page rendering, publication, asset copying, analytical execution or UI preference state.
"""
import re
from pathlib import Path
from badge_catalog import load_catalog, technology_ids

from validation import fields, local_file, localized, read_json, require

COLLECTIONS = {'selected_projects', 'learning_labs', 'independent_experiments'}
SLUG = re.compile(r'[a-z0-9]+(?:_[a-z0-9]+)*\Z')


def load_projects(source, badge_data=None):
    """Return validated records in registry order; never discover projects implicitly."""
    root = Path(source).resolve(strict=True)
    registry = read_json(local_file(root, 'config/projects.json'))
    fields(registry, {'schema_version', 'projects'}, 'registry')
    require(type(registry['schema_version']) is int and registry['schema_version'] == 2, 'Unsupported registry schema')
    require(isinstance(registry['projects'], list), 'Projects must be an ordered list')
    badge_data = load_catalog() if badge_data is None else badge_data
    seen, topics, records = set(), {}, []
    for entry in registry['projects']:
        fields(entry, {'path', 'featured'}, 'registry entry')
        path = entry['path']
        require(isinstance(path, str), 'Invalid project path')
        parts = path.split('/')
        require(len(parts) == 2 and parts[0] in COLLECTIONS and SLUG.fullmatch(parts[1]), f'Invalid project path: {path}')
        require(path not in seen and type(entry['featured']) is bool, f'Duplicate/invalid registry entry: {path}')
        seen.add(path)
        meta_file = local_file(root, path + '/project.json')
        data = read_json(meta_file)
        base_fields = {'schema_version','name','description','topics','technologies','documentation','notebook'}
        require(isinstance(data, dict) and type(data.get('schema_version')) is int and data['schema_version'] in (1, 2), f'Unsupported project schema: {path}')
        fields(data, base_fields | ({'sections', 'report'} if data['schema_version'] == 2 else set()), path)
        if data['schema_version'] == 2:
            require(isinstance(data['sections'], list) and data['sections'], 'Report sections required')
            section_ids = set()
            for section in data['sections']:
                fields(section, {'id', 'label', 'title', 'description'}, 'project section')
                ident = section['id']
                require(isinstance(ident, str) and re.fullmatch(r'[a-z][a-z0-9_-]*', ident) and ident != 'top' and ident not in section_ids, 'Invalid/duplicate project section ID')
                section_ids.add(ident)
                for key in ('label', 'title'):
                    localized(section[key], ident + '/' + key)
                if section['description'] is not None:
                    localized(section['description'], ident + '/description')
        for key in ('name', 'description'):
            localized(data[key], path + '/' + key)
        require(isinstance(data['topics'], list), f'Invalid topics: {path}')
        project_topics = set()
        for topic in data['topics']:
            fields(topic, {'id','label'}, 'topic')
            ident = topic['id']
            require(isinstance(ident, str) and SLUG.fullmatch(ident) and ident not in project_topics, f'Invalid/duplicate topic: {ident}')
            localized(topic['label'], ident)
            require(ident not in topics or topics[ident] == topic['label'], f'Conflicting topic label: {ident}')
            topics[ident] = topic['label']
            project_topics.add(ident)
        ids = data['technologies']
        require(isinstance(ids, list) and all(isinstance(i, str) for i in ids), f'Invalid technologies: {path}')
        require(len(ids) == len(set(ids)), f'Duplicate technologies: {path}')
        ordered = technology_ids(ids, badge_data)
        localized(data['documentation'], path + '/documentation')
        for target in data['documentation'].values():
            require(target.endswith('.md'), f'Invalid documentation extension: {target}')
            local_file(meta_file.parent, target)
        if data['notebook'] is not None:
            require(isinstance(data['notebook'], str) and data['notebook'].endswith('.ipynb'), f'Invalid notebook: {path}')
            local_file(meta_file.parent, data['notebook'])
        records.append({**data, 'path': path, 'featured': entry['featured'], 'technologies': ordered})
    return records
