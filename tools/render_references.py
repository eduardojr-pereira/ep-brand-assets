"""Canonical bilingual references renderer. Project content is supplied as data."""
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlsplit
from badge_html import image, topic, localized, technologies

ROOT = Path(__file__).resolve().parents[1]
PARTS = (ROOT / 'components/web/references.html').read_text(encoding='utf-8').strip()
SECTION, rest = PARTS.split('<!-- EP-REFERENCE-CARD -->')
CARD, rest = rest.split('<!-- EP-REFERENCE-STEP -->')
STEP, COMMAND = rest.split('<!-- EP-REFERENCE-COMMAND -->')

def esc(value):
    return escape(str(value), quote=True)

def bilingual(value):
    if isinstance(value, str):
        return esc(value)
    en, pt = value['en'], value['pt-BR']
    return f'<span data-ep-ref-en="{esc(en)}" data-ep-ref-pt="{esc(pt)}">{esc(en)}</span>'

def pair(en, pt):
    return {'en': en, 'pt-BR': pt}

def link(label, url):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.netloc:
        raise ValueError(f'Invalid reference URL: {url}')
    return f'<a class="ep-reference-link ep-external-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{bilingual(label)}<span class="ep-editorial-arrow" aria-hidden="true">↗</span></a>'

def icon(name):
    if name not in {'data_source','knowledge_base','reproducibility','copy','check'}:
        raise ValueError('Unknown reference icon')
    return (ROOT / 'assets/icons' / (name + '_icon.svg')).read_text(encoding='utf-8').strip()

def card(name, title, content, full=False):
    return Template(CARD).substitute(icon=icon(name), title=bilingual(title), content=content,
                                     modifier='ep-reference-card--full' if full else '')

def badge_link(markup, url, title=None):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.netloc:
        raise ValueError(f'Invalid badge URL: {url}')
    hint = f' title="{esc(title)}"' if title else ""
    return f'<a class="ep-reference-badge-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer"{hint}>{markup}</a>'


def render_report_licenses(licenses):
    return '<div class="tags ep-report-licenses">' + ''.join(
        badge_link(image(item['id']), item['url'], item['url'].rsplit('/', 1)[-1]) for item in licenses
    ) + '</div>' if licenses else ''


def render_technical_tabs(data):
    tabs = []
    knowledge = data.get('knowledge_base', [])
    if knowledge:
        tabs.append(('knowledge', pair('Topics', 'Tópicos'), ''.join(
            badge_link(topic(item['label']['en']), item['url']) for item in knowledge)))
    methods = data.get('methods', [])
    if methods:
        tabs.append(('methods', pair('Methods', 'Métodos'), ''.join(localized(item) for item in methods)))
    tech = data.get('technologies', [])
    if tech:
        tabs.append(('technologies', pair('Technologies', 'Tecnologias'), technologies(tech)))
    if not tabs:
        return ''
    buttons, panels = [], []
    for ident, label, content in tabs:
        key = 'ep-tech-' + ident
        buttons.append(f'<button type="button" id="{key}-tab" aria-controls="{key}-panel" data-ep-tab>{bilingual(label)}</button>')
        panels.append(f'<div id="{key}-panel" data-ep-tab-panel aria-labelledby="{key}-tab"><h4 class="ep-tab-fallback-heading">{bilingual(label)}</h4><div class="ep-reference-badges">{content}</div></div>')
    return ('<div class="ep-reference-tabs" data-ep-tabs>'
            '<div class="ep-reference-tablist" data-ep-tablist hidden>' + ''.join(buttons) + '</div>'
            '<div class="ep-reference-panels">' + ''.join(panels) + '</div></div>')


def render_references(data):
    cards = []
    source = data.get('data_source')
    if source:
        content = '<p>' + link(source['name'], source['url']) + '</p>'
        if source.get('authors'):
            content += '<p>' + bilingual(source['authors']) + '</p>'
        if source.get('doi'):
            content += '<p>DOI: ' + esc(source['doi']) + '</p>'
        if source.get('license_badge'):
            license_data = source['license_badge']
            content += '<div class="ep-reference-badges">' + badge_link(image(license_data['id']), license_data['url']) + '</div>'
        elif source.get('license'):
            content += '<span class="tag ep-reference-license">' + esc(source['license']) + '</span>'
        if source.get('note'):
            content += '<p>' + bilingual(source['note']) + '</p>'
        cards.append(card('data_source', pair('Data Source','Fonte dos Dados'), content))
    code = data.get('source_code')
    if code:
        content = '<p>' + bilingual(code['intro']) + '</p>'
        content += '<ul class="ep-reference-links">' + ''.join('<li>'+link(item['label'],item['url'])+'</li>' for item in code['links']) + '</ul>'
        cards.append(card('knowledge_base', pair('Source Code','Código-fonte'), content))
    knowledge = data.get('knowledge_base')
    if data.get('technical_tabs'):
        content = render_technical_tabs(data)
        if content:
            cards.append(card('knowledge_base', pair('Technical References','Referências Técnicas'), content, not bool(source or code)))
    elif knowledge:
        content = '<ul class="ep-reference-links">' + ''.join('<li>'+link(item['label'],item['url'])+'</li>' for item in knowledge) + '</ul>'
        cards.append(card('knowledge_base', pair('Knowledge Base','Base de Conhecimento'), content))
    reproduction = data.get('reproducibility')
    if reproduction:
        content = '<p>' + bilingual(reproduction['intro']) + '</p><ol class="ep-reference-steps">'
        for step in reproduction['steps']:
            command = ''
            if step.get('command'):
                command = Template(COMMAND).substitute(command=esc(step['command']), copy_icon=icon('copy'), check_icon=icon('check'), label=bilingual(pair('Copy','Copiar')))
            content += Template(STEP).substitute(label=bilingual(step['label']), command=command)
        content += '</ol>'
        if reproduction.get('note'):
            content += '<p>' + bilingual(reproduction['note']) + '</p>'
        links = []
        if reproduction.get('documentation'):
            links.append(link(pair('Project Documentation','Documentação do Projeto'), reproduction['documentation']))
        if reproduction.get('source_code'):
            links.append(link(pair('Source Code','Código-fonte'), reproduction['source_code']))
        if links:
            if reproduction.get('source_code'):
                content += '<div class="ep-reference-project-links">' + ''.join(links) + '</div>'
            else:
                content += '<p>' + ''.join(links) + '</p>'
        cards.append(card('reproducibility', pair('Reproducibility','Reprodutibilidade'), content, True))
    if not cards:
        return ''
    return Template(SECTION).substitute(title=bilingual(pair('References & Reproducibility','Referências e Reprodutibilidade')), cards=''.join(cards))
