"""Responsibility: Select, validate and copy a single canonical runtime resource tree for a static artifact.
Boundaries: No route policy, UI state, template rendering, repository checkout, arbitrary project data or deployment.
"""
from pathlib import Path
import posixpath
import re
from validation import local_file, read_json
from routing import path_name

ROOT = Path(__file__).resolve().parents[1]

_SHELL_IMAGES = {"logo_src": "logos/logo_initials.png", "favicon_src": "logos/favicon.png"}

def shell_images(asset_root):
    asset = path_name(asset_root)
    return {key: asset + "/" + path_name(name) for key, name in _SHELL_IMAGES.items()}


def resource_paths(root=ROOT):
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
    result = sorted(set(paths))
    for name in result:
        local_file(root, name)
    return result


def copy_resources(output, root=ROOT, paths=None):
    allowed = resource_paths(root)
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
