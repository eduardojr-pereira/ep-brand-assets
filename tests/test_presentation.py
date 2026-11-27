"""Responsibility: Integration tests for shared locale, theme and asset contracts."""
from copy import deepcopy
from playwright.sync_api import sync_playwright
from support import ROOT, ENV, load_page, launch_browser, dictionaries, environment, head_resources, DEPENDENCIES, new_page
from test_interactive import PROJECTS, FIXTURE as INTERACTIVE

LOCAL = {
    'en': {'content.title':'Portfolio test', 'content.area':'Data Analytics', 'content.description':'Demand forecast', 'content.alt':'Figure one', 'content.caption':'Figure one'},
    'pt-BR': {'content.title':'Teste do portfólio', 'content.area':'Análise de dados', 'content.description':'Previsão da demanda', 'content.alt':'Figura um', 'content.caption':'Figura um'},
}
EXTRA = '''{% import 'components/web/navigation.html' as n %}{% import 'components/web/buttons.html' as b %}
<script>window.firstPaintContract={lang:document.documentElement.lang,theme:document.documentElement.dataset.theme,visibility:getComputedStyle(document.body).visibility};</script>
<div id="title-test">{{ n.nav_link(message('shared.nav.projects'),'#catalog') }}</div>
{{ b.orbit_link('orbit-test',message('shared.action.selected'),message('shared.action.selected_ring'),'#selected') }}
<form>{{ b.send_action() }}</form>'''


def fixture(page, theme='dark', scripts=True, lottie=False):
    env = environment(LOCAL); projects=deepcopy(PROJECTS); msg=env.globals['message']
    projects[0]['description']=msg('content.description')
    projects[0]['badges'][0].update(en_src=projects[0]['badges'][0]['src']+'#en',pt_br_src=projects[0]['badges'][0]['src']+'#pt-br')
    projects[0]['frames'][0]['alt']=msg('content.alt')
    projects[0]['frames'][0]['caption']=msg('content.caption')
    projects[0]['frames'][0]['light']='data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg"%3E%3C/svg%3E#light'
    projects[0]['frames'][0]['dark']='data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg"%3E%3C/svg%3E#dark'
    body=env.from_string(EXTRA+INTERACTIVE).render(projects=projects,areas=[{'value':'analytics','label':msg('content.area')},{'value':'python','label':'Python'}])
    load_page(page, body, theme, local=LOCAL, scripts=scripts,lottie=lottie,title='Portfolio test',title_key='content.title',css='section{margin:20px}#contact{height:1100px}')


def switches(page):
    fixture(page)
    assert page.title()=='Portfolio test'
    page.locator('.ui-catalog__area summary').click()
    page.get_by_role('button',name='Data Analytics',exact=True).click()
    page.get_by_role('searchbox').fill('regression')
    assert page.locator('[data-ui-count]').inner_text()=='1 project'
    page.locator('[data-ui-evidence-toggle]').click()
    page.get_by_role('button',name='Next project').click()
    page.wait_for_timeout(750)
    page.get_by_role('button',name='Pause marquee').click()
    page.evaluate("UI.actions.setSendState(document.querySelector('[data-ui-send]'),'success',{confirmed:true})")
    page.evaluate("window.filterEvents=0; document.addEventListener('ui:filterchange',()=>filterEvents++); UI.i18n.set('pt-BR')")
    assert page.title()=='Teste do portfólio'
    assert page.locator('.ui-badges img').first.get_attribute('src').endswith('#pt-br')
    assert page.locator('html').get_attribute('lang')=='pt-BR'
    assert page.locator('.ui-catalog__area summary .ui-link__regular').inner_text()=='Análise de dados'
    assert page.get_by_role('searchbox').input_value()=='regression'
    assert page.get_by_role('searchbox').get_attribute('placeholder')=='Projeto ou tecnologia…'
    assert page.locator('[data-ui-count]').inner_text()=='1 projeto'
    assert page.locator('[data-ui-carousel-count]').inner_text()=='02 / 02'
    assert page.locator('[data-ui-evidence-toggle]').get_attribute('aria-label')=='Reproduzir resultados'
    assert page.locator('[data-ui-send]').get_attribute('data-state')=='success'
    assert page.locator('[data-ui-send] [role=status]').inner_text()=='Entraremos em contato em breve.'
    assert page.locator('[data-ui-ring-label]').text_content().startswith('PROJETOS SELECIONADOS')
    assert page.locator('[data-ui-frame]').first.get_attribute('alt')=='Figura um'
    assert page.get_by_role('button',name='Reproduzir faixa').is_visible()
    assert page.locator('.ui-marquee__track [data-i18n-text]').count()==1
    assert page.evaluate('filterEvents')==0
    page.get_by_role('searchbox').fill('xyz')
    assert page.locator('[data-ui-count]').inner_text()=='0 projetos'
    page.evaluate("UI.theme.set('light')")
    assert page.locator('html').get_attribute('data-theme')=='light'
    assert page.locator('[data-ui-frame]').first.get_attribute('src').endswith('#light')
    assert page.evaluate("UI.assets.url('animations/lottie-checkbox-v1-orange.json')").endswith('/assets/animations/lottie-checkbox-v1-orange.json')
    assert page.evaluate("UI.i18n.format('shared.catalog.count',{count:1234})")=='1.234 projetos'
    assert page.evaluate("() => {try{UI.assets.url('../config/brand.json');return false}catch{return true}}")
    page.evaluate("UI.i18n.set('en');UI.theme.set('dark')")
    assert page.locator('[data-ui-count]').inner_text()=='0 projects'
    assert page.locator('[data-ui-send] [role=status]').inner_text()=="We'll be in touch soon."
    print('PASS: global locale, title, SVG, accessible labels, plural, content, selection, search, carousel, marquee, send state and theme assets',flush=True)


def startup(browser):
    page=new_page(browser, locale='pt-PT',color_scheme='light')
    fixture(page,'light')
    assert page.evaluate('firstPaintContract')=={'lang':'pt-BR','theme':'light','visibility':'hidden'}
    assert page.title()=='Teste do portfólio'
    assert page.locator('body').evaluate('e=>getComputedStyle(e).visibility')=='visible'
    page.evaluate("UI.i18n.set('en');UI.theme.set('dark')")
    page.reload(wait_until='domcontentloaded')
    assert page.evaluate('firstPaintContract')=={'lang':'en','theme':'dark','visibility':'visible'}
    assert page.evaluate("localStorage.getItem('ui.locale')")=='en'
    page.emulate_media(color_scheme='light');assert page.locator('html').get_attribute('data-theme')=='dark'
    page.close()
    print('PASS: cold startup, browser locale, saved preference across reload and system theme override',flush=True)
    page=new_page(browser, locale='fr-FR');fixture(page);assert page.title()=='Portfolio test';page.close()
    page=new_page(browser, locale='pt-BR',java_script_enabled=False);fixture(page,scripts=False)
    assert page.title()=='Portfolio test' and page.locator('body').is_visible();page.close()
    print('PASS: unsupported locale falls back to English; no-JS English fallback',flush=True)


def validate():
    assert set(dictionaries()['en'])==set(dictionaries()['pt-BR'])
    try: dictionaries({'en':{'shared.nav.home':'X'},'pt-BR':{'shared.nav.home':'Y'}})
    except ValueError: pass
    else: raise AssertionError('Shared dictionary override accepted')
    try: dictionaries({'en':{'content.a':'X'},'pt-BR':{}})
    except ValueError: pass
    else: raise AssertionError('Missing locale key accepted')
    head=str(head_resources('../',LOCAL))
    assert head.index('ui-config')<head.index('scripts/theme.js')<head.index('styles/foundations.css')
    assert '../assets/' in head
    print('PASS: validated translation ownership, key parity and canonical head order',flush=True)

if __name__=='__main__':
    validate()
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        page=new_page(browser, viewport={'width':1280,'height':900},locale='en-US');errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        switches(page);assert not errors,errors;page.close()
        startup(browser);browser.close()
