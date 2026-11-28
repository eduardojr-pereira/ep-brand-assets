"""Responsibility: Prepare trusted project report content, declared chart data and publishable files for the canonical report shell.
Boundaries: No analysis, model training, game logic, shared UI implementation, Git operations or deployment.
"""
import json
from html.parser import HTMLParser
from pathlib import Path

from artifact_preview import prepare_artifact
from badge_catalog import active_entry, load_catalog
from plotly_presentation import chart_payload
from presentation import dictionaries, static_message
from routing import Document, path_name, relative_href, resource_base, project_source_links
from validation import fields, local_file, read_json, require

_FILE_TYPES = {
    'artifact': {'.png', '.jpg', '.jpeg', '.svg', '.csv', '.json', '.txt', '.pdf', '.xlsx'},
    'asset': {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.mp4', '.json', '.csv', '.txt'},
    'script': {'.js'},
    'style': {'.css'},
}


def prepare_report(source, record, route, local, sections, brand):
    """Load only explicitly declared files. Templates and chart inputs stay private to the build."""
    root = Path(source) / record['path']
    meta = record['report']
    fields(meta, {'files', 'charts', 'badges'}, 'report metadata')
    for key in meta:
        require(isinstance(meta[key], list), f'Report {key} must be a list')
    translations = read_json(local_file(root, 'translations.json'))
    require(isinstance(translations, dict) and all(isinstance(entries, dict) for entries in translations.values()), 'Invalid report translation dictionaries')
    dictionaries(translations)  # Same locale/key/argument contract as shared content.
    for lang, entries in translations.items():
        require(not set(entries) & set(local[lang]), 'Report translation collides with generated metadata')
        local[lang].update(entries)
    messages = dictionaries(local)

    def message(key):
        return {'key': key, 'text': static_message(messages, key)}

    template = local_file(root, 'content/project_content.html').read_text(encoding='utf-8')
    files, artifacts, scripts, styles, charts, badge_files = {}, [], [], [], {}, set()
    for item in meta['files']:
        fields(item, {'path', 'role', 'label'}, 'report file')
        path, role = path_name(item['path']), item['role']
        require(isinstance(role, str) and role in _FILE_TYPES, 'Unknown report file role')
        require(path not in files and Path(path).suffix.lower() in _FILE_TYPES[role], 'Duplicate or unsupported report file')
        require(path.startswith('outputs/') if role == 'artifact' else path.startswith('content/'), 'Report file outside its authorized directory')
        require(not path.startswith('content/charts/'), 'Chart specifications are build-only inputs')
        local_file(root, path)
        destination = record['path'] + '/' + path
        files[path] = relative_href(route, destination)
        require(item['label'] is None or role == 'artifact', 'Only artifacts have file labels')
        if role == 'artifact':
            preview = prepare_artifact(root, path, {path}, message(item['label']) if item['label'] is not None else None)
            preview['href'] = files[path]
            artifacts.append(preview)
        elif role == 'script':
            scripts.append(files[path])
        elif role == 'style':
            styles.append(files[path])
    for item in meta['charts']:
        fields(item, {'id', 'path', 'label', 'fallback'}, 'report chart')
        ident, path = item['id'], path_name(item['path'])
        require(isinstance(ident, str) and ident not in charts, 'Invalid or duplicate report chart ID')
        require(path.startswith('content/charts/') and path.endswith('.json'), 'Invalid chart specification path')
        spec = read_json(local_file(root, path))
        fields(spec, {'figure', 'translations', 'colors', 'palette', 'config'}, 'chart specification')
        charts[ident] = {'id': ident, 'label': message(item['label']),
                         'fallback': message(item['fallback']) if item['fallback'] is not None else None,
                         'payload': chart_payload(ident, local=local, **spec)}
    catalog = load_catalog()
    base = resource_base(route)
    badges = {}
    require(all(isinstance(i, str) for i in meta['badges']), 'Invalid report badge ID')
    require(len(meta['badges']) == len(set(meta['badges'])), 'Duplicate report badge ID')
    for ident in dict.fromkeys(record['technologies'] + meta['badges']):
        entry = active_entry(ident, catalog)
        badge_files.add(entry['path'])
        badges[ident] = {'src': base + entry['path'], 'label': entry['label']}
    context = {'title': message('content.page.title'), 'description': message('content.page.description'),
               'files': files, 'artifacts': artifacts, 'charts': charts, 'badges': badges,
               'technologies': [badges[i] for i in record['technologies']],
               'links': project_source_links(brand['portfolio'], record)}
    return {'template': template, 'context': context, 'sections': sections, 'scripts': scripts,
            'styles': styles, 'files': {record['path'] + '/' + path for path in files}, 'badges': badge_files}


class _ContentCheck(HTMLParser):
    """Check the output contract, not the safety of untrusted templates."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections, self.mounts, self.specs = [], [], []
        self.spec = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        require(tag not in {'html', 'head', 'body', 'main', 'style', 'link', 'meta', 'title', 'footer'}, 'Report content must not redefine the document shell or head resources')
        require(not any(k == 'style' or k.startswith('on') for k in a), 'Inline styles and event handlers are not report content')
        if 'data-ui-section' in a:
            require(tag == 'section' and a.get('id'), 'Report section requires an ID')
            self.sections.append(a['id'])
        if 'data-ui-plotly' in a:
            require(a.get('id'), 'Report chart mount requires an ID')
            self.mounts.append(a['id'])
        if tag == 'script':
            require(set(a) == {'type', 'data-ui-plotly-spec'} and a['type'] == 'application/json', 'Only canonical inert chart specifications are allowed in report content')
            self.spec = []

    def handle_data(self, data):
        if self.spec is not None:
            self.spec.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.spec is not None:
            self.specs.append(json.loads(''.join(self.spec)))
            self.spec = None

    handle_startendtag = handle_starttag


def render_report(env, report):
    """Render one trusted Jinja macro, with no project discovery or Python imports."""
    module = env.from_string(report['template']).make_module()
    macro = getattr(module, 'content', None)
    require(not str(module).strip() and callable(macro) and getattr(macro, 'arguments', ()) == ('sections', 'report'), 'Report template must define the content(sections, report) macro')
    content = macro(report['sections'], report['context'])
    Document(content)  # Canonical static HTML validation, including duplicate IDs.
    check = _ContentCheck()
    check.feed(content)
    check.close()
    require(check.spec is None, 'Unclosed report chart specification')
    require(check.sections == [s['id'] for s in report['sections']], 'Rendered report sections differ from declared navigation order')
    charts = report['context']['charts']
    require(sorted(check.mounts) == sorted(charts), 'Each declared chart needs exactly one mount')
    expected = [json.loads(str(chart['payload']).split('>', 1)[1].rsplit('</script>', 1)[0]) for chart in charts.values()]
    require(len(check.specs) == len(expected) and all(check.specs.count(spec) == 1 for spec in expected), 'Each chart needs its canonical specification exactly once')
    return content
