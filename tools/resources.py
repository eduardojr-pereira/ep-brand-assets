"""Responsibility: Select, validate and copy a single canonical runtime resource tree for a static artifact.
Boundaries: No route policy, UI state, template rendering, repository checkout, arbitrary project data or deployment.
"""
from pathlib import Path
import posixpath
import re
from validation import local_file, read_json
from routing import path_name
from badge_catalog import load_catalog

ROOT = Path(__file__).resolve().parents[1]
PLOTLY_RUNTIME = "assets/vendor/plotly/plotly.min.js"

_SHELL_IMAGES = {"logo_src": "logos/logo_initials.png", "favicon_src": "logos/favicon.png"}

def shell_images(asset_root):
    asset = path_name(asset_root)
    return {key: asset + "/" + path_name(name) for key, name in _SHELL_IMAGES.items()}


def resource_paths(root=ROOT, *, guide=False, plotly_runtime=False, landing=False, badges=(), report_badges=()):
    root = Path(root)
    ui = read_json(local_file(root, 'config/ui.json'))
    brand = read_json(local_file(root, 'config/brand.json'))
    asset = path_name(brand['asset_root'])
    paths = ui['styles'] + ui['head_scripts'] + ui['defer_scripts']
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate canonical dependencies')
    for name in paths:
        path_name(name)
        if not (name.startswith('styles/') and name.endswith('.css') or name.startswith('scripts/') and name.endswith('.js')):
            raise ValueError(f'Unexpected dependency: {name}')
    # Runtime paths declared by the canonical manifest, plus the shell's two images.
    lottie = ui['lottie']
    runtime = [lottie['runtime'], lottie['license'], ui['plotly']['locale'], 'vendor/plotly/LICENSE']
    for spec in lottie['animations'].values():
        runtime.extend([spec['file']] if 'file' in spec else spec['variants'].values())
    paths.extend(shell_images(asset).values())
    for name in runtime:
        paths.append(asset + '/' + path_name(name))
    # Discover local CSS dependencies (currently fonts); preserve matching font notices.
    for name in ui['styles']:
        css = local_file(root, name).read_text(encoding='utf-8')
        for raw in re.findall(r'url\(\s*([^)]*?)\s*\)', css):
            ref = raw.strip().strip('"\'')
            if not ref or ref.startswith('#'):
                continue
            if ref.startswith('data:'):
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), ref))
            path_name(target)
            if not target.startswith(asset + '/'):
                raise ValueError(f'CSS resource outside canonical assets: {name}: {ref}')
            paths.append(target)
            if target.endswith(('.ttf', '.otf', '.woff', '.woff2')):
                paths.append(posixpath.dirname(target) + '/OFL.txt')
    paths += ['LICENSE-BRAND.md', 'LICENSE-CODE.txt', 'LICENSE-CONTENT.md',
              'THIRD-PARTY-NOTICES.md', 'docs/LICENSE-SCIENTIFIC-COLOUR-MAPS.txt']
    if plotly_runtime:
        paths.append(PLOTLY_RUNTIME)
    if landing:
        paths.extend(['landing/layout.css', 'landing/behavior.js'])
        permitted = {e['path'] for e in load_catalog(root)['entries'] if e['category'] == 'technologies'}
        if not set(badges).issubset(permitted):
            raise ValueError('Unexpected landing badge')
        paths.extend(badges)
    elif badges:
        raise ValueError('Landing badge selection requires landing content')
    if report_badges:
        permitted = {e['path'] for e in load_catalog(root)['entries']}
        if not set(report_badges).issubset(permitted):
            raise ValueError('Unexpected report badge')
        paths.extend(report_badges)
    if guide:
        paths.extend(['style_guide/layout.css','style_guide/demo.js','style_guide/samples/observations.csv','style_guide/samples/summary.json'])
        paths.extend(entry['path'] for entry in load_catalog(root)['entries'])
        paths.extend(['style_guide/samples/palette-nuuk-shared.svg', 'style_guide/samples/palette-lipari-shared.svg', 'style_guide/samples/palette-vik-shared.svg', 'style_guide/samples/palette-delphi-shared.svg', 'style_guide/samples/palette-ston-shared.svg', 'style_guide/samples/palette-fes-shared.svg', 'style_guide/samples/palette-vikO-shared.svg', 'style_guide/samples/palette-ep-muted-pastel-dark.svg', 'style_guide/samples/palette-ep-muted-pastel-light.svg', 'style_guide/samples/palette-ep-lipari-adapted-dark.svg', 'style_guide/samples/palette-ep-lipari-adapted-light.svg', 'style_guide/samples/evidence-line-dark.svg', 'style_guide/samples/evidence-bar-dark.svg', 'style_guide/samples/evidence-line-light.svg', 'style_guide/samples/evidence-bar-light.svg'])
    result = sorted(set(paths))
    for name in result:
        local_file(root, name)
    return result


def copy_resources(output, root=ROOT, paths=None, *, guide=False, plotly_runtime=False, landing=False, badges=(), report_badges=()):
    allowed = resource_paths(root, guide=guide, plotly_runtime=plotly_runtime, landing=landing, badges=badges, report_badges=report_badges)
    paths = allowed if paths is None else list(paths)
    if len(paths) != len(set(paths)) or not set(paths).issubset(allowed):
        raise ValueError("Unexpected or duplicate canonical resource")
    output = Path(output).absolute()
    if not output.is_dir() or any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError(f'Unsafe resource output: {output}')
    transfers = []
    for name in paths:
        source = local_file(Path(root), path_name(name))
        dest = output / 'shared' / name
        for parent in dest.parents:
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise ValueError(f'Unsafe resource destination parent: {parent}')
        if dest.is_symlink():
            raise ValueError(f'Symlink resource destination: {dest}')
        if dest.exists():
            raise FileExistsError(dest)
        transfers.append((source, dest))
    # All destinations are checked before writing any resource.
    for source, dest in transfers:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as stream:
            stream.write(source.read_bytes())
    return {'shared/' + name for name in paths}
