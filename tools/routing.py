"""Responsibility: Resolve relative static destinations and validate generated local links and fragments.
Boundaries: No page composition, asset selection, metadata loading, network requests or publication.
"""
import posixpath
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, quote


_SEGMENT = re.compile(r'[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*\Z')


def path_name(value):
    if not isinstance(value, str) or not value or not all(_SEGMENT.fullmatch(p) for p in value.split('/')):
        raise ValueError(f'Unsafe artifact path: {value!r}')
    return value


def page_path(value):
    path_name(value)
    if not value.endswith('.html') or value.split('/')[0] == 'shared':
        raise ValueError(f'Invalid page route: {value}')
    return value


def validate_page_routes(routes):
    names = set()
    for route in routes:
        route = page_path(route)
        if route in names:
            raise ValueError(f'Duplicate page route: {route}')
        names.add(route)
    for route in sorted(names):
        parts = route.split('/')
        for i in range(1, len(parts)):
            parent = '/'.join(parts[:i])
            if parent in names:
                raise ValueError(f'Page file/directory collision: {parent} / {route}')
    return names


def relative_href(page, target):
    page_path(page)
    path_name(target)
    return posixpath.relpath(target, posixpath.dirname(page) or '.')


def project_report_path(project):
    return page_path(project + '/reports/index.html')


def project_source_links(repository, record):
    """Resolve public source/documentation links from the same validated project metadata."""
    repo = repository.rstrip('/')
    project = quote(record['path'], safe='/')
    base = repo + '/blob/main/' + project + '/'
    return {'source': repo + '/tree/main/' + project,
            'notebook': base + quote(record['notebook']) if record['notebook'] else None,
            'documentation': {lang: base + quote(name) for lang, name in record['documentation'].items()}}


def resource_base(page):
    return relative_href(page, 'shared') + '/'


# Deliberately unsupported URL mechanisms require a future explicit contract.
_UNSUPPORTED_URL_ATTRIBUTES = frozenset({
    'action', 'formaction', 'srcset', 'imagesrcset', 'ping', 'srcdoc',
    'background', 'manifest', 'longdesc', 'usemap', 'profile', 'archive',
    'codebase', 'classid', 'lowsrc', 'dynsrc', 'attributionsrc',
})
_URL_ATTRIBUTES = frozenset({
    'href', 'src', 'poster', 'cite', 'xlink:href', 'data-light-src',
    'data-dark-src', 'data-en-src', 'data-pt-br-src',
    'data-dark-en-src', 'data-dark-pt-src', 'data-light-en-src', 'data-light-pt-src',
    'data-ui-href-en', 'data-ui-href-pt-br',
})
_UNSUPPORTED_TAGS = frozenset({'base', 'iframe', 'frame', 'object', 'embed', 'applet'})


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.ids, self.links = set(), []
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if len(values) != len(attrs):
            raise ValueError(f'Duplicate HTML attribute: {tag}')
        if tag in _UNSUPPORTED_TAGS:
            raise ValueError(f'Unsupported HTML destination mechanism: {tag}')
        if tag == 'meta' and (values.get('http-equiv') or '').strip().lower() == 'refresh':
            raise ValueError('Unsupported meta refresh')
        if 'id' in values:
            ident = values['id']
            if not ident or ident in self.ids:
                raise ValueError(f'Empty or duplicate HTML id: {ident}')
            self.ids.add(ident)
        for key, val in attrs:
            if key in _UNSUPPORTED_URL_ATTRIBUTES:
                raise ValueError(f'Unsupported URL attribute: {key}')
            if key in _URL_ATTRIBUTES:
                self.links.append((tag, key, val))

    handle_startendtag = handle_starttag


def validate_links(pages, files, *, site_base=None):
    # The complete-site check treats absolute URLs within this deployment
    # prefix as artifact destinations, rather than unchecked external links.
    site = urlsplit(site_base) if site_base is not None else None
    if site is not None and (site.scheme != 'https' or not site.hostname or
                             site.username or site.password or site.query or
                             site.fragment or not site.path.endswith('/')):
        raise ValueError('Invalid canonical site base')
    documents = {name: Document(html) for name, html in pages.items()}
    files = set(files) | set(pages)
    for page, doc in documents.items():
        for tag, key, href in doc.links:
            if not href or href != href.strip() or any(ord(c) < 32 or ord(c) == 127 for c in href) or '\\' in href:
                raise ValueError(f'Invalid URL in {page}: {href!r}')
            if key == 'xlink:href' and not href.startswith('#'):
                raise ValueError(f'Only same-document SVG xlink references are supported: {href}')
            url = urlsplit(href)
            if url.scheme:
                if not (key in {'href','data-ui-href-en','data-ui-href-pt-br'} and tag == 'a' and ((url.scheme == 'https' and url.hostname and not url.username and not url.password) or (url.scheme == 'mailto' and url.path and not url.netloc))):
                    raise ValueError(f'Unsupported URL in {page}: {href}')
                same_site = (site is not None and url.scheme == site.scheme and
                             url.hostname == site.hostname and (url.port or 443) == (site.port or 443))
                prefix = site.path if same_site else None
                if not same_site or not (url.path.startswith(prefix) or url.path == prefix.rstrip('/')):
                    continue  # External destinations are not fetched.
                if url.query or '%' in url.path:
                    raise ValueError(f'Nonportable site URL in {page}: {href}')
                dest = url.path[len(prefix):]
                if not dest or dest.endswith('/'):
                    dest += 'index.html'
            else:
                if url.netloc or url.path.startswith('/') or url.query or '%' in url.path:
                    raise ValueError(f'Nonportable URL in {page}: {href}')
                dest = posixpath.normpath(posixpath.join(posixpath.dirname(page), url.path)) if url.path else page
            path_name(dest)
            if dest not in files:
                raise ValueError(f'Missing local destination in {page}: {href}')
            if '#' in href and (dest not in documents or not url.fragment or unquote(url.fragment) not in documents[dest].ids):
                raise ValueError(f'Missing fragment in {page}: {href}')
    return documents
