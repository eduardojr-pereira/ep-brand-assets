"""Canonical bilingual references renderer. Project content is supplied as data."""
from html import escape
from pathlib import Path
from string import Template
from urllib.parse import urlsplit

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

def render_references(data):
    cards = []
    source = data.get('data_source')
    if source:
        content = '<p>' + link(source['name'], source['url']) + '</p>'
        if source.get('authors'):
            content += '<p>' + bilingual(source['authors']) + '</p>'
        if source.get('doi'):
            content += '<p>DOI: ' + esc(source['doi']) + '</p>'
        if source.get('license'):
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
    if knowledge:
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
        if reproduction.get('documentation'):
            content += '<p>' + link(pair('Project Documentation','Documentação do Projeto'), reproduction['documentation']) + '</p>'
        cards.append(card('reproducibility', pair('Reproducibility','Reprodutibilidade'), content, True))
    if not cards:
        return ''
    return Template(SECTION).substitute(title=bilingual(pair('References & Reproducibility','Referências e Reprodutibilidade')), cards=''.join(cards))
