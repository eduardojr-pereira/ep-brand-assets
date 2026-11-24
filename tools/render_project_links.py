from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]

def render_project_links(repository, *, back_to_portfolio=False):
    parsed = urlsplit(repository)
    if parsed.scheme != 'https' or not parsed.netloc:
        raise ValueError('Invalid project URL')
    back_link = ''
    if back_to_portfolio:
        back_link = ('<a class="ep-report-nav__back" href="../../../index.html#projects" '
                     'aria-label="Back to Portfolio" data-replace="Back to Portfolio">'
                     '<span>Back to Portfolio</span></a>')
    return Template((ROOT/'components/web/project-links.html').read_text(encoding='utf-8')).substitute(
        repository=escape(repository, quote=True), back_link=back_link)
