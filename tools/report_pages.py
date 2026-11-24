# Compose a shared EP header on published report HTML only.


# The original report and generator remain independent of the site header.
# End module note
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import re
import os
from render_header import render_header
from render_footer import render_web_footer


class _HeaderLocator(HTMLParser):
    # Find one legacy top-level header by balanced tags.
    def __init__(self, markup: str):
        super().__init__(convert_charrefs=False)
        self.markup = markup
        self.starts = [0]
        for m in re.finditer(r'\n', markup): self.starts.append(m.end())
        self.start = self.end = None
        self.depth = 0
    def pos_to_offset(self, pos): return self.starts[pos[0]-1] + pos[1]
    def handle_starttag(self, tag, attrs):
        if tag == 'header':
            if self.depth: self.depth += 1
            elif 'header' in dict(attrs).get('class','').split():
                if self.start is not None: raise ValueError('Multiple legacy headers')
                self.start = self.pos_to_offset(self.getpos()); self.depth = 1
    def handle_endtag(self, tag):
        if tag == 'header' and self.depth:
            self.depth -= 1
            if not self.depth:
                m = re.match(r'</header\s*>', self.markup[self.pos_to_offset(self.getpos()):], re.I)
                if not m: raise ValueError('Malformed legacy header')
                self.end = self.pos_to_offset(self.getpos()) + m.end()


def _replace_bike_legacy(markup: str) -> str:
    # Older checked-in Bike HTML has not been regenerated.
    if '<nav class="bike-local-nav ep-report-nav"' in markup:
        return markup
    left = '  .nav{position:sticky;top:0;'
    right = '  @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.nav-links a,.nav-links a::after{transition:none}}'
    if markup.count(left) != 1 or markup.count(right) != 1:
        raise ValueError('Cannot identify Bike legacy navigation CSS')
    start = markup.index(left); finish = markup.index(right, start)+len(right)
    markup = markup[:start] + '''  /* Bike local navigation layout; link effects in EP Brand. */
  .bike-local-nav{position:sticky;top:0;z-index:20;background:var(--ep-color-bg);border-bottom:1px solid var(--ep-color-border)}
  .bike-local-nav__inner{min-height:64px;display:flex;align-items:center;padding:12px 0}
  .bike-local-nav__links{display:flex;align-items:center;flex-wrap:wrap;gap:10px;width:100%}
  .bike-local-nav__back{margin-left:auto}
  @media(max-width:670px){.bike-local-nav__links{gap:6px}}
  @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}''' + markup[finish:]
    mobile = '.nav-links{gap:5px}.nav-links a{font-size:.78rem;padding:7px 8px}'
    if markup.count(mobile)!=1: raise ValueError('Bike responsive nav selector mismatch')
    markup=markup.replace(mobile,'',1)
    left='  /* Shared visual navigation convention: light-blue links, white on hover. */'
    right='/* EP-FOOTER-MOTION-V1: standardized website link; contact cards unchanged. */'
    if markup.count(left)!=1 or markup.count(right)!=1: raise ValueError('Bike duplicate CSS boundaries mismatch')
    start=markup.index(left); finish=markup.index(right,start)
    markup=markup[:start]+markup[finish:]
    start_markup='  <nav class="nav" aria-label="Main navigation">'
    end_markup='  </div></nav>'
    if markup.count(start_markup)!=1: raise ValueError('Bike legacy nav markup mismatch')
    start=markup.index(start_markup);finish=markup.index(end_markup,start)+len(end_markup)
    nav='''  <nav class="bike-local-nav ep-report-nav" aria-label="Report sections">
    <div class="container bike-local-nav__inner"><div class="bike-local-nav__links">
      <a class="ep-report-nav__link" href="#overview">Overview</a>
      <a class="ep-report-nav__link" href="#business">Business</a>
      <a class="ep-report-nav__link" href="#exploration">Exploration</a>
      <a class="ep-report-nav__link" href="#hourly">Hourly</a>
      <a class="ep-report-nav__link" href="#models">Models</a>
      <a class="ep-report-nav__link" href="#findings">Conclusions</a>
      <a class="ep-report-nav__link" href="#outputs">Outputs</a>
      <a class="ep-report-nav__back bike-local-nav__back" href="../../../index.html" aria-label="Back to Portfolio" data-replace="Back to Portfolio"><span>Back to Portfolio</span></a>
    </div></div>
  </nav>'''
    markup=markup[:start]+nav+markup[finish:]
    old='document.querySelectorAll(\'.nav-links a[href^="#"]\')'
    if markup.count(old)!=1: raise ValueError('Bike scroll tracking selector mismatch')
    return markup.replace(old, 'document.querySelectorAll(\'.bike-local-nav__links a[href^="#"]\')',1)


def integrate_report(report_file: Path, published: list[dict], output_root: Path) -> None:
    # Add shared header, theme and scripts to one output-only report page.
    markup = report_file.read_text(encoding='utf-8')
    if markup.count('<body>')!=1 or markup.count('</head>')!=1 or markup.count('</body>')!=1:
        raise ValueError(f'Unexpected report document structure: {report_file}')
    # Render the same canonical Footer used by the homepage at build time.
    # Never edit the project report source or copy the Footer's implementation.
    footer_html = render_web_footer(embed=True)
    footer_pattern = r'<footer\b[^>]*\bclass="ep-footer"[^>]*>.*?</footer\s*>'
    footers = list(re.finditer(footer_pattern, markup, flags=re.S | re.I))
    if len(footers) > 1:
        raise ValueError(f'Multiple EP footers in report: {report_file}')
    if footers:
        old = footers[0]
        markup = markup[:old.start()] + footer_html + markup[old.end():]
    elif re.search(r'<footer\b', markup, flags=re.I):
        raise ValueError(f'Unexpected noncanonical footer in report: {report_file}')
    else:
        # Synthetic/minimal reports may omit a footer entirely.
        markup = markup.replace('</body>', footer_html + '\n</body>', 1)
    if 'class="ep-header"' in markup: raise ValueError('Already has shared header')
    # Migrates legacy Bike markup on published copy without generating Plotly again.
    if 'class="nav" aria-label="Main navigation"' in markup:
        markup = _replace_bike_legacy(markup)
    # Drop the old Bike-specific Footer animation from published HTML only.
    footer_marker = '/* EP-FOOTER-MOTION-V1: standardized website link; contact cards unchanged. */'
    if footer_marker in markup:
        part, rest = markup.split(footer_marker, 1)
        if '</style>' not in rest: raise ValueError('Missing Bike footer style boundary')
        _, tail = rest.split('</style>', 1)
        # Footer motion is now owned by components/web/footer.css.
        markup = part + '</style>' + tail
    # Old Bike inline scroll tracking cannot coexist with shared navigation.
    # Remove only the known, self-contained legacy script in the published copy.
    if 'EP-NAV-CLICK-LOCK-V1' in markup:
        pattern = r'<script>\s*\(\(\) => \{\s*// EP-NAV-CLICK-LOCK-V1:.*?</script>'
        markup, count = re.subn(pattern, '', markup, count=1, flags=re.S)
        if count != 1: raise ValueError('Could not isolate old Bike navigation script')
    # Keep the Hangman built-in locale buttons as functional hooks, but display
    # one global language selector. The game script will still use these IDs.
    if 'id="locale-pt"' in markup and 'id="locale-en"' in markup:
        markup = markup.replace('</head>', '<style>.ep-report-document .lang{display:none}</style>\n</head>', 1)
    # Hangman's own locale script must only translate its game content.
    # Otherwise its missing keys erase labels in the shared EP header.
    if 'id="locale-pt"' in markup and 'id="locale-en"' in markup:
        original_selector = "document.querySelectorAll('[data-i18n]')"
        if markup.count(original_selector) != 1:
            raise ValueError('Cannot safely scope Hangman locale translation')
        markup = markup.replace(original_selector, "document.querySelectorAll('main [data-i18n]')", 1)
    # Existing Hangman branded header would otherwise produce two headers.
    locator=_HeaderLocator(markup)
    locator.feed(markup)
    if locator.start is not None:
        if locator.end is None: raise ValueError('Unclosed old report header')
        markup=markup[:locator.start]+markup[locator.end:]
    prefix=os.path.relpath(output_root, report_file.parent).replace(os.sep, '/') + '/'
    links=[{'name':p['name'],'name_pt':p['name_pt'],'report':prefix+str(p['report'])} for p in published]
    header,_=render_header(links,all_projects_href=prefix+'index.html#projects', include_portfolio_bridge=False)
    head='''<script src="{base}assets/scripts/theme-init.js"></script>
<link rel="stylesheet" href="{base}assets/styles/theme-tokens.css">
<link rel="stylesheet" href="{base}assets/styles/typography-v2.css">
<link rel="stylesheet" href="{base}assets/components/web/header.css">
<link rel="stylesheet" href="{base}assets/components/web/footer.css">
<link rel="stylesheet" href="{base}assets/styles/report-navigation.css">
<link rel="stylesheet" href="{base}assets/styles/report-theme.css">
<link rel="stylesheet" href="{base}assets/components/web/project-intro.css">
<link rel="stylesheet" href="{base}assets/components/web/cards.css">
<link rel="stylesheet" href="{base}assets/components/web/links.css">
<link rel="stylesheet" href="{base}assets/components/web/buttons.css">
'''
    head=head.replace('{base}', prefix)
    # Styles after legacy inline report styles, so tokens override fixed legacy vars.
    if '</style>' in markup:
        pos=markup.rfind('</style>',0,markup.index('</head>'))
        if pos<0: raise ValueError('No report style block before head')
        pos+=len('</style>')
        markup=markup[:pos]+'\n'+head+markup[pos:]
    else:
        markup=markup.replace('</head>',head+'</head>',1)
    markup=markup.replace('<html lang=', '<html class="ep-report-document" lang=',1)
    markup=markup.replace('<body>', '<body class="ep-report-page">\n'+header,1)
    scripts='''<script src="{base}assets/scripts/theme.js" defer></script>
<script src="{base}assets/scripts/i18n.js" defer></script>
<script src="{base}assets/scripts/header.js" defer></script>
<script src="{base}assets/scripts/footer.js" defer></script>
<script src="{base}assets/scripts/report-navigation.js" defer></script>
'''
    scripts=scripts.replace('{base}', prefix)
    scripts += f'<script src="{prefix}assets/scripts/report-language.js" defer></script>\n'
    if 'data-ep-plotly-i18n' in markup:
        scripts += f'<script src="{prefix}assets/scripts/plotly-i18n.js" defer></script>\n'
        scripts += f'<script src="{prefix}assets/scripts/plotly-theme.js" defer></script>\n'
        markup = markup.replace(
            '</head>',
            f'<link rel="stylesheet" href="{prefix}assets/styles/plotly-theme.css">\n</head>',
            1
        )
    if 'class="ep-references"' in markup:
        markup = markup.replace('</head>', f'<link rel="stylesheet" href="{prefix}assets/components/web/references.css">\n</head>', 1)
        scripts += f'<script src="{prefix}assets/scripts/references.js" defer></script>\n'
    if 'class="ep-outputs"' in markup:
        markup = markup.replace('</head>', f'<link rel="stylesheet" href="{prefix}assets/components/web/outputs.css">\n</head>', 1)
        scripts += f'<script src="{prefix}assets/scripts/outputs.js" defer></script>\n'
    if 'class="ep-project-links"' in markup:
        scripts += f'<script src="{prefix}assets/scripts/project-links.js" defer></script>\n'
    markup=markup.replace('</body>',scripts+'</body>',1)
    report_file.write_text(markup,encoding='utf-8')
