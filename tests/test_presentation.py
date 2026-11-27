"""Responsibility: Test integration of shared locale, theme and asset contracts.
Boundaries: No production preference or asset service implementation.
"""
from copy import deepcopy
from playwright.sync_api import sync_playwright
from support import ROOT, ENV, load_page, launch_browser, dictionaries, environment, head_resources, DEPENDENCIES, new_page, close_browser, validate_bindings
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
    page=new_page(browser,locale='pt-BR')
    # Simulate a malformed runtime binding added after server-side validation.
    body='<span id="valid" data-i18n-text="shared.nav.home">Home</span><script>const bad=document.createElement("span");bad.setAttribute("data-i18n-text","content.missing");bad.textContent="English fallback";document.body.append(bad);</script>'
    load_page(page,body)
    assert page.locator('#valid').inner_text()=='Home'
    assert page.locator('html').get_attribute('lang')=='en'
    assert page.evaluate("UI.i18n.current()")=='en'
    assert page.locator('body').is_visible()
    assert page.locator('html').get_attribute('data-ui-localizing') is None
    page.close()
    print('PASS: startup failure preserves complete English fallback and reveals page',flush=True)


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
    for html in ['<span data-i18n-text="content.missing">X</span>', '<span data-i18n-text="shared.catalog.count">0</span>', '<span data-i18n-invalid="shared.nav.home">Home</span>']:
        try: validate_bindings(html,LOCAL)
        except ValueError: pass
        else: raise AssertionError('Invalid generated binding accepted')
    validate_bindings('<span data-i18n-text="shared.nav.home">Home</span>',LOCAL)
    print('PASS: generation rejects unknown keys, unsupported targets and incomplete static messages',flush=True)

def atomic_and_search(page):
    fixture(page)
    page.evaluate("UI.i18n.set('en')")
    search=page.get_by_role('searchbox')
    cards=page.locator('[data-ui-project]:visible')
    search.fill('Demand forecast')
    assert cards.count()==1
    page.evaluate("UI.i18n.set('pt-BR')")
    assert search.input_value()=='Demand forecast' and cards.count()==1
    assert page.locator('[data-ui-count]').inner_text()=='1 projeto'
    search.fill('Previsão da demanda')
    assert cards.count()==1
    page.evaluate("UI.i18n.set('en')")
    assert search.input_value()=='Previsão da demanda' and cards.count()==1
    assert page.locator('[data-ui-count]').inner_text()=='1 project'
    print('PASS: bilingual search index preserves English and Portuguese queries across locale changes',flush=True)
    # Inject an invalid runtime binding after valid generation; no partial translation or saved preference.
    result=page.evaluate("""() => {
        let events=0; document.addEventListener('ui:languagechange',()=>events++);
        const invalid=document.createElement('span'); invalid.textContent='Unchanged';
        invalid.setAttribute('data-i18n-text','content.missing'); document.body.append(invalid);
        const original=document.title; let rejected=false;
        try { UI.i18n.set('pt-BR'); } catch { rejected=true; }
        const stable=rejected && document.title===original && UI.i18n.current()==='en' &&
            document.documentElement.lang==='en' && localStorage.getItem('ui.locale')==='en' && events===0;
        invalid.remove(); UI.i18n.set('pt-BR');
        return stable && events===1 && document.title==='Teste do portfólio';
    }""")
    assert result
    print('PASS: atomic language change, stored preference and event on rejected binding; recovery',flush=True)


def asset_recovery(page):
    load_page(page,'<div id="host" style="width:40px;height:40px"></div><span id="fallback">Fallback</span>',lottie=True)
    counts={'runtime':0,'source':0}
    def fail_once(route,kind):
        counts[kind]+=1
        if counts[kind]==1: route.fulfill(status=503,body='Temporary test failure')
        else: route.fallback()
    page.route('**/vendor/lottie/lottie.min.js',lambda route:fail_once(route,'runtime'))
    page.route('**/animations/lottie_home_white.json',lambda route:fail_once(route,'source'))
    mount="UI.assets.mount(document.querySelector('#host'),{id:'checkbox'})"
    with page.expect_console_message(predicate=lambda message: 'UI animation unavailable: checkbox' in message.text):
        page.evaluate(mount)
    assert page.locator('#host').get_attribute('data-ui-lottie-ready') is None
    assert page.locator('#fallback').is_visible()
    page.evaluate(mount)
    page.wait_for_function("document.querySelector('#host').hasAttribute('data-ui-lottie-ready')")
    assert counts['runtime']==2
    mount="UI.assets.mount(document.querySelector('#host'),{id:'home',variant:'theme'})"
    with page.expect_console_message(predicate=lambda message: 'UI animation unavailable: home' in message.text):
        page.evaluate(mount)
    assert page.locator('#host').get_attribute('data-ui-lottie-ready') is None
    page.evaluate(mount)
    page.wait_for_function("document.querySelector('#host').hasAttribute('data-ui-lottie-ready')")
    assert counts=={'runtime':2,'source':2}
    page.evaluate("UI.assets.unmount(document.querySelector('#host'))")
    assert page.locator('#host svg').count()==0
    print('PASS: retry after real runtime/source failures, static fallback and disposal',flush=True)


if __name__=='__main__':
    validate()
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        page=new_page(browser, viewport={'width':1280,'height':900},locale='en-US')
        switches(page);page.close()
        startup(browser)
        page=new_page(browser,viewport={'width':1280,'height':900});atomic_and_search(page);page.close()
        page=new_page(browser,viewport={'width':1280,'height':900});asset_recovery(page);page.close()
        close_browser(browser)
