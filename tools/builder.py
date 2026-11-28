"""Responsibility: Orchestrate validated declarative pages, canonical templates and isolated static output.
Boundaries: No UI behavior, analytical execution, implicit project publication, Git operations or deployment.
"""
import argparse
import re
import shutil
import tempfile
from pathlib import Path
from catalog import load_projects
from style_guide import guide_context, validate_guide_sections
from landing import landing_data, landing_context, asset_paths, badge_paths
from validation import fields, localized, read_json, require
from presentation import ROOT, environment, head_resources, validate_bindings
from routing import page_path, project_report_path, relative_href, resource_base, validate_links, validate_page_routes
from resources import resource_paths, copy_resources, shell_images, PLOTLY_RUNTIME
from report_content import prepare_report, render_report


def prepare(source, plan, *, complete_site=False):
    records = {r['path']: r for r in load_projects(source)}
    brand = read_json(ROOT / 'config/brand.json')
    navigation = read_json(ROOT / 'config/navigation.json')
    fields(plan, {'schema_version', 'legal', 'pages'} | ({'landing_content'} if 'landing_content' in plan else set()), 'build plan')
    landing = landing_data(source, plan)
    require(type(plan['schema_version']) is int and plan['schema_version'] == 1, 'Unsupported build plan')
    fields(plan['legal'], {'privacy', 'terms'}, 'legal')
    legal = {k: page_path(v) for k, v in plan['legal'].items()}
    require(legal['privacy'] != legal['terms'], 'Distinct legal routes required')
    require(isinstance(plan['pages'], list) and plan['pages'], 'No declared pages')
    pages, report_projects, reports = {}, set(), {}
    nav = {item['id']: item['label'] for item in navigation['sections']}
    for item in plan['pages']:
        fields(item, {'route', 'kind', 'project', 'title', 'sections'}, 'page')
        route = page_path(item['route'])
        kind = item['kind']
        require(route not in pages and kind in ('landing', 'report', 'plain', 'style_guide'), 'Duplicate route or invalid kind')
        require((route == 'index.html') == (kind == 'landing'), 'Landing must be index.html')
        require((route == 'style-guide/index.html') == (kind == 'style_guide'), 'Style Guide route is reserved')
        project = item['project']
        if kind == 'report':
            require(isinstance(project, str) and project in records and project not in report_projects, 'Invalid or duplicate report project')
            require(item['title'] is None, 'Report title belongs to project metadata')
            report_projects.add(project)
            title = records[project]['name']
        else:
            require(project is None, 'Only reports have a project')
            title = item['title']
            localized(title, 'page title')
        local = {'en': {}, 'pt-BR': {}}
        def add(key, value):
            localized(value, key)
            for lang in local:
                local[lang][key] = value[lang]
            return key
        title_key = add('content.page.title', title)
        if kind == 'report' and records[project]['schema_version'] == 2:
            require(item['sections'] == [], 'Real report sections belong to project metadata, not the site plan')
            record = records[project]
            add('content.page.description', record['description'])
            sections = []
            for i, section in enumerate(record['sections']):
                prefix = f'content.section.{i}.'
                sections.append({'id': section['id'], 'label': add(prefix+'label', section['label']),
                                 'title': add(prefix+'title', section['title']),
                                 'description': add(prefix+'description', section['description']) if section['description'] is not None else None})
            reports[route] = prepare_report(source, record, route, local, sections, brand)
            pages[route] = (kind, local, title_key, sections)
            continue
        require(isinstance(item['sections'], list) and item['sections'], 'No declared sections')
        sections, ids = [], []
        for i, section in enumerate(item['sections']):
            fields(section, {'id', 'title', 'paragraphs'}, 'section')
            ident = section['id']
            require(isinstance(ident, str) and re.fullmatch(r'[a-z][a-z0-9_-]*', ident) and ident != 'top' and ident not in ids, 'Invalid/duplicate section id')
            ids.append(ident)
            if kind == 'landing':
                require(ident in nav and section['title'] is None, 'Landing section labels belong to navigation')
                label = nav[ident]
            else:
                label = add(f'content.section.{i}.title', section['title'])
            require(isinstance(section['paragraphs'], list), 'Paragraphs must be a list')
            paragraphs = [add(f'content.section.{i}.paragraph.{j}', value) for j, value in enumerate(section['paragraphs'])]
            sections.append({'id': ident, 'label': label, 'paragraphs': paragraphs})
        if kind == 'landing':
            require(ids == list(nav), 'Landing sections must match canonical order and IDs')
        if kind == 'style_guide':
            validate_guide_sections(ids, sections)
        pages[route] = (kind, local, title_key, sections)
    validate_page_routes(pages)
    require('index.html' in pages, 'Missing landing')
    for route in legal.values():
        require(route in pages and pages[route][0] == 'plain', 'Legal destination must be a declared plain page')
    if complete_site:
        require(landing is not None, 'Complete site requires actual landing content')
        require(report_projects == set(records), 'Complete site requires a report for every registered project')
        for item in plan['pages']:
            if item['kind'] == 'report':
                require(item['route'] == project_report_path(item['project']), 'Complete site must preserve canonical report routes')
        require(legal == {'privacy': 'legal/privacy.html', 'terms': 'legal/terms.html'}, 'Complete site must preserve legal routes')
        require(len(reports) == len(report_projects), 'Complete site requires real report content for every project')
    return pages, brand, navigation, legal, reports


def _render(source, plan, *, complete_site=False):
    pages, brand, navigation, legal, reports = prepare(source, plan, complete_site=complete_site)
    report_routes = {item['project']: item['route'] for item in plan['pages'] if item['kind'] == 'report'}
    rendered = {}
    landing = landing_data(source, plan)
    for route, (kind, local, title_key, sections) in pages.items():
        base = resource_base(route)
        extra = landing_context(source, landing, base, local, brand, report_routes) if kind == 'landing' else {}
        env = environment(local)
        if kind == 'style_guide':
            extra = guide_context(base,local,env)
        if route in reports:
            report = reports[route]
            extra = {'report_content': render_report(env, report), 'report_scripts': report['scripts'],
                     'report_styles': report['styles'], 'report_plotly_href': base + PLOTLY_RUNTIME if report['context']['charts'] else None}
        html = env.get_template('templates/' + ('base' if kind == 'plain' else kind) + '.html').render(
            brand=brand, navigation=navigation, title_key=title_key, sections=sections, **extra,
            head=head_resources(base, local),
            **{key: base + path for key, path in shell_images(brand['asset_root']).items()},
            landing_href=relative_href(route, 'index.html'),
            privacy_href=relative_href(route, legal['privacy']), terms_href=relative_href(route, legal['terms']),
            report_sections=[{'label': s['label'], 'href': '#' + s['id']} for s in sections])
        validate_bindings(html, local)
        rendered[route] = html
    return rendered, reports


def render(source, plan, *, complete_site=False):
    return _render(source, plan, complete_site=complete_site)[0]


def build(source, plan, output, *, complete_site=False):
    source = Path(source).resolve(strict=True)
    requested = Path(output)
    if requested.exists() or requested.is_symlink():
        raise ValueError('Output must not exist; never overwrite an existing artifact')
    output = requested.resolve()
    for protected in (source, ROOT.resolve()):
        require(not output.is_relative_to(protected) and not protected.is_relative_to(output), 'Output must be isolated from source and brand')
    require(output.parent.is_dir(), 'Output parent must exist')
    pages, reports = _render(source, plan, complete_site=complete_site)
    guide = 'style-guide/index.html' in pages
    landing = landing_data(source, plan)
    media = sorted(set(asset_paths(source, landing)).union(*(r['files'] for r in reports.values())))
    badges = badge_paths(source, landing)
    report_badges = sorted(set().union(*(r['badges'] for r in reports.values())))
    plotly_runtime = guide or any(r['context']['charts'] for r in reports.values())
    paths = resource_paths(guide=guide, plotly_runtime=plotly_runtime, landing=landing is not None, badges=badges, report_badges=report_badges)
    site_base = read_json(ROOT / 'config/brand.json')['website'] if complete_site else None
    validate_links(pages, {'shared/' + name for name in paths} | set(media), site_base=site_base)
    require(not set(media).intersection(pages), 'Consumer media collides with a page')
    stage = Path(tempfile.mkdtemp(prefix='.ui-build-', dir=output.parent))
    try:
        copy_resources(stage, paths=paths, guide=guide, plotly_runtime=plotly_runtime, landing=landing is not None, badges=badges, report_badges=report_badges)
        for name in media:
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write((source / name).read_bytes())
        for name, html in pages.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('x', encoding='utf-8', newline='\n') as file:
                file.write(html)
        (stage / '.nojekyll').touch(exist_ok=False)
        require(not output.exists() and not output.is_symlink(), 'Output appeared during build')
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return len(pages), len(paths) + len(media)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--complete-site', action='store_true', help='Require complete structural route coverage; not release authorization')
    args = parser.parse_args()
    pages, resources = build(args.source, read_json(args.plan), args.output, complete_site=args.complete_site)
    print(f'Build validated: {pages} pages, {resources} resource files, no deployment')


if __name__ == '__main__':
    main()
