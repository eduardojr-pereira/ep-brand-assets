"""Responsibility: Validate shared editorial composition, responsiveness and native fallback."""
from playwright.sync_api import sync_playwright
from support import environment, load_page, launch_browser, new_page, close_browser
from presentation import validate_bindings

LOCAL = {
    'en': {'content.title':'Demand analysis', 'content.category':'Selected Projects', 'content.subtitle':'Forecasting demand', 'content.description':'Evidence to support operational decisions.', 'content.context':'Plan capacity based on observed demand.', 'content.objective':'Evaluate a baseline model.', 'content.section':'Results', 'content.section_intro':'Review the evidence.', 'content.license':'Code license'},
    'pt-BR': {'content.title':'Análise de demanda', 'content.category':'Projetos selecionados', 'content.subtitle':'Previsão de demanda', 'content.description':'Evidências para apoiar decisões operacionais.', 'content.context':'Planejar capacidade com base na demanda observada.', 'content.objective':'Avaliar um modelo de referência.', 'content.section':'Resultados', 'content.section_intro':'Revise as evidências.', 'content.license':'Licença do código'}
}
PIXEL='data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 20"%3E%3Crect width="80" height="20" fill="gray"/%3E%3C/svg%3E'
FIXTURE='''{% import 'components/web/editorial.html' as e %}{% import 'components/web/hero_projects.html' as h %}{% import 'components/web/interactive.html' as i %}
<main>{{ h.hero_projects(project, 'overview') }}<section class="fixture-section" id="results" data-ui-section>{{ e.section_heading(message('content.section'), message('content.section_intro'), 'results-heading') }}{{ i.selected_projects([slide]) }}</section><section class="fixture-section">{{ e.section_heading(message('content.section'), id='no-intro') }}</section></main>'''

def render(full=True):
    env=environment(LOCAL);m=env.globals['message']
    project={key:m('content.'+key) for key in ('title','category','description')}
    if full:
        project.update(subtitle=m('content.subtitle'),licenses=[dict(src=PIXEL,label=m('content.license'),href='/license.txt')],business_context=m('content.context'),objectives=[m('content.objective')],notebook_href='/notebook/',documentation_href='/documentation/',technologies=[dict(src=PIXEL,label='Python')])
    slide=dict(title=project['title'],subtitle=project.get('subtitle'),description=project['description'],badges=[],frames=[],metrics=[],href='#overview')
    body=env.from_string(FIXTURE).render(project=project,slide=slide)
    validate_bindings(body,LOCAL)
    return body

def fixture(page, theme='dark', full=True, scripts=True):
    load_page(page,render(full),theme,local=LOCAL,scripts=scripts,css='.fixture-section{padding:24px var(--ui-page-gutter);min-height:450px}')
    return page.locator('.ui-project-hero'),page.locator('#results .ui-section-heading')

def desktop(page,theme):
    hero,head=fixture(page,theme)
    assert hero.get_by_role('heading',level=1).count()==1
    assert head.get_by_role('heading',level=2).count()==1
    assert page.locator('#no-intro + p').count()==0
    assert hero.get_by_role('link',name='Code license').get_attribute('href')=='/license.txt'
    assert hero.get_by_role('link',name='Notebook').get_attribute('href')=='/notebook/'
    assert hero.get_by_role('link',name='Documentation').get_attribute('href')=='/documentation/'
    assert hero.locator('.ui-project-hero__technologies img').count()==1
    assert hero.locator('.ui-project-hero__context li').count()==1
    assert hero.locator('[role=tablist]').count()==0
    def style(loc): return loc.evaluate('e=>[getComputedStyle(e).fontFamily,getComputedStyle(e).fontSize,getComputedStyle(e).fontWeight,getComputedStyle(e).lineHeight]')
    assert style(hero.locator('.ui-project-title'))==style(page.locator('.ui-feature .ui-project-title'))
    assert head.evaluate('e=>getComputedStyle(e).flexDirection')=='row'
    assert head.evaluate('e=>getComputedStyle(e).borderBottomWidth')=='1px'
    page.evaluate("UI.i18n.set('pt-BR')")
    assert hero.get_by_role('heading',name='Análise de demanda').count()==1
    assert hero.get_by_role('link',name='Licença do código').get_attribute('href')=='/license.txt'
    assert hero.get_by_role('link',name='Documentação').get_attribute('href')=='/documentation/'
    assert head.get_by_role('heading',name='Resultados').count()==1
    assert hero.get_by_text('Avaliar um modelo de referência.',exact=True).count()==1
    page.evaluate("theme=>UI.theme.set(theme)", "light" if theme=="dark" else "dark")
    assert page.locator('html').get_attribute('data-theme')==('light' if theme=='dark' else 'dark')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    print(f'PASS: {theme} editorial geometry, shared project typography, license and source links, bilingual labels and global theme')

def responsive(page):
    hero,head=fixture(page)
    assert head.evaluate('e=>getComputedStyle(e).flexDirection')=='column'
    assert hero.locator('.ui-project-hero__details').evaluate('e=>getComputedStyle(e).gridTemplateColumns.split(" ").length')==1
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert hero.locator('.ui-project-hero__title').evaluate('e=>getComputedStyle(e).opacity')=='1'
    page.set_viewport_size({'width':1280,'height':700})
    assert head.evaluate('e=>getComputedStyle(e).flexDirection')=='row'
    assert head.evaluate('e=>getComputedStyle(e).paddingBottom')=='10px'
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    print('PASS: narrow stacked layout, reduced motion, short desktop heading and no overflow')

def minimal(page):
    hero,head=fixture(page,full=False,scripts=False)
    assert hero.get_by_role('heading',level=1).is_visible()
    assert hero.locator('.ui-project-hero__context,.ui-project-hero__technologies,.ui-project-hero__links,.ui-project-subtitle,.ui-badges').count()==0
    assert hero.locator('.ui-project-hero__details--single').count()==1
    assert head.get_by_role('heading',level=2).is_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    print('PASS: minimal project, optional fields omitted, static headings without JavaScript')

if __name__=='__main__':
    with sync_playwright() as p:
        browser=launch_browser(p)
        for theme in ('dark','light'):
            page=new_page(browser,viewport={'width':1440,'height':900});desktop(page,theme);page.close()
        page=new_page(browser,viewport={'width':320,'height':740},reduced_motion='reduce');responsive(page);page.close()
        page=new_page(browser,viewport={'width':360,'height':740},java_script_enabled=False);minimal(page);page.close()
        close_browser(browser)
