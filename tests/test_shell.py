"""Responsibility: Regression tests for canonical Header/Footer composition and consumption."""
import json
from playwright.sync_api import sync_playwright
from support import ROOT, environment, load_page, launch_browser, new_page, close_browser
from presentation import validate_bindings

BRAND=json.loads((ROOT/'config/brand.json').read_text())
NAV=json.loads((ROOT/'config/navigation.json').read_text())
LOCAL={'en':{'content.overview':'Overview','content.results':'Results'},'pt-BR':{'content.overview':'Visão geral','content.results':'Resultados'}}
FIXTURE='''{% import 'components/web/header.html' as h %}{% import 'components/web/footer.html' as f %}
{% if report %}{{ h.header(brand,navigation,[{'label':'content.overview','href':'#overview'},{'label':'content.results','href':'#results'}],'/portfolio/index.html#home','/portfolio/index.html#all-projects') }}{% else %}{{ h.landing_header(brand,navigation) }}{% endif %}
<main>{% for section in (['overview','results'] if report else navigation.sections|map(attribute='id')|list) %}<section id="{{ section }}" data-ui-section><h2>{{ section }}</h2></section>{% endfor %}</main>
{{ f.footer(brand,navigation,'/portfolio/index.html' if report else '', '/assets/logos/logo_initials.png','/privacy/','/terms/') }}'''

def fixture(page, theme='dark', *,report=False,scripts=True,lottie=False):
    body=environment(LOCAL).from_string(FIXTURE).render(brand=BRAND,navigation=NAV,report=report)
    validate_bindings(body,LOCAL)
    load_page(page,body,theme,local=LOCAL,scripts=scripts,lottie=lottie,css='main section{min-height:850px;padding:30px}')
    return page.locator('[data-ui-header]'),page.locator('[data-ui-footer]')

def desktop(page,theme):
    header,footer=fixture(page,theme)
    page.wait_for_function("!document.querySelector('[data-ui-header]').hasAttribute('data-ui-compact')")
    assert header.locator('.ui-header__links > a').count()==5
    assert header.get_by_role('link',name='Home',exact=True).get_attribute('aria-current')=='location'
    page.evaluate("document.querySelector('#all-projects').scrollIntoView()")
    page.wait_for_function("document.querySelector('.ui-header__links > a[href=\"#all-projects\"]').getAttribute('aria-current')==='location'")
    github=header.locator('.ui-header__links > details')
    github.locator('summary').click();assert github.get_attribute('open') is not None
    assert github.get_by_role('link',name='Knowledge Base').is_visible()
    github.locator('summary').press('Escape');assert github.get_attribute('open') is None
    header.get_by_role('button',name='Switch language').click()
    page.wait_for_function("document.documentElement.lang==='pt-BR'")
    assert header.get_by_role('link',name='Todos os projetos').get_attribute('aria-current')=='location'
    assert header.get_by_role('button',name='Alterar idioma').inner_text()=='PT'
    assert footer.get_by_role('link',name='Política de Privacidade').get_attribute('href')=='/privacy/'
    header.get_by_role('button',name='Alterar tema').click()
    assert page.locator('html').get_attribute('data-theme')==('light' if theme=='dark' else 'dark')
    assert footer.locator('.ui-footer__groups .ui-editorial-link').count()==8
    assert footer.locator('.ui-footer__icons a').count()==4
    # Confirm actual shared motion and row geometry rather than independent effects.
    row=footer.locator('.ui-footer__groups .ui-editorial-link').first
    title=row.locator('.ui-editorial-link__title');desc=row.locator('.ui-editorial-link__description')
    assert desc.bounding_box()['y'] >= title.bounding_box()['y']+title.bounding_box()['height']-1
    assert row.locator('.ui-link__move').count()==1 and row.locator('.ui-link__arrow').count()==1
    assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
    print(f'PASS: {theme} header, scroll navigation, GitHub, global locale/theme, footer editorial and legal composition',flush=True)

def compact(page,report=False):
    header,footer=fixture(page,report=report)
    page.wait_for_function("document.querySelector('[data-ui-header]').hasAttribute('data-ui-compact')")
    expected=2 if report else 5
    assert header.locator('.ui-header__links > a').count()==expected
    summary=header.locator('.ui-header__compact > details > summary')
    summary.click()
    assert header.locator('.ui-header__compact .ui-header__links').is_visible()
    panel=header.locator('.ui-header__compact > details > .ui-dropdown__panel')
    page.wait_for_timeout(250)
    box=panel.bounding_box();assert box['x']>=-1 and box['x']+box['width']<=page.viewport_size['width']+1,box
    assert header.locator('.ui-header__links > a').first.locator('.ui-link__arrow').is_visible()
    github=header.locator('.ui-header__links > details');github.locator('summary').click()
    assert github.get_attribute('open') is not None
    github.locator('summary').press('Escape');assert github.get_attribute('open') is None
    header.locator('.ui-header__links > a').last.click()
    assert header.locator('.ui-header__compact > details').get_attribute('open') is None
    if report: assert header.locator('.ui-header__back a').get_attribute('href')=='/portfolio/index.html#all-projects'
    page.set_viewport_size({'width':1440,'height':900})
    page.wait_for_function("!document.querySelector('[data-ui-header]').hasAttribute('data-ui-compact')")
    assert header.locator('.ui-header__desktop .ui-header__links > a').count()==expected
    assert header.locator('.ui-header__links').count()==1
    page.set_viewport_size({'width':360,'height':740})
    page.wait_for_function("document.querySelector('[data-ui-header]').hasAttribute('data-ui-compact')")
    header.get_by_role('button',name='Switch language').click()
    page.wait_for_function("document.querySelector('.ui-header__compact summary').textContent.includes('Seções')")
    assert footer.locator('.ui-footer__social').evaluate('e=>getComputedStyle(e).flexDirection')=='column'
    assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
    print(f'PASS: {"report" if report else "landing"} compact layout, nested menus, single navigation tree, translation and mobile footer',flush=True)

def animations(page):
    header,footer=fixture(page,lottie=True)
    art=footer.locator('.ui-footer__groups [data-ui-footer-animation="home"]')
    art.scroll_into_view_if_needed()
    rest=art.locator('[data-ui-footer-rest]');hover=art.locator('[data-ui-footer-hover]')
    rest.locator('svg').wait_for(state='attached',timeout=15000);hover.locator('svg').wait_for(state='attached',timeout=15000)
    page.wait_for_function("[...document.querySelectorAll('.ui-footer__groups [data-ui-footer-animation=home] :is([data-ui-footer-rest],[data-ui-footer-hover])')].every(e=>e.hasAttribute('data-ui-lottie-ready'))")
    for id,scale in [('home','1.36'),('award','1'),('projects','.95'),('about','1.8'),('gmail','.8')]:
        value=footer.locator(f'.ui-footer__groups [data-ui-footer-animation="{id}"]').evaluate('e=>getComputedStyle(e).getPropertyValue("--ui-footer-optical-scale").trim()')
        assert float(value)==float(scale),(id,value)
    art.locator('..').locator('..').hover()
    page.wait_for_function("document.querySelector('.ui-footer__groups [data-ui-footer-animation=home]').hasAttribute('data-ui-playing')")
    page.emulate_media(reduced_motion='reduce')
    page.wait_for_function("UI.assets.get(document.querySelector('.ui-footer__groups [data-ui-footer-animation=home] [data-ui-footer-hover]'))?.isPaused===true")
    page.evaluate("UI.theme.set('light')")
    page.wait_for_function("document.querySelector('.ui-footer__groups [data-ui-footer-animation=home] [data-ui-footer-rest]').hasAttribute('data-ui-lottie-ready')")
    assert rest.locator('svg').count()==1
    assert page.evaluate("document.querySelectorAll('script[src$=\"lottie.min.js\"]').length") == 1
    print('PASS: real footer Lotties, optical scales, global theme reload, reduced motion and single runtime',flush=True)

def fallback(page):
    header,footer=fixture(page,scripts=False)
    assert header.get_by_role('link',name='Home',exact=True).is_visible()
    assert not header.locator('[data-ui-language-control]').is_visible()
    assert footer.get_by_role('link',name='Privacy Policy').is_visible()
    assert footer.locator('.ui-footer__fallback').first.is_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    print('PASS: readable native links and static footer without JavaScript',flush=True)

if __name__=='__main__':
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        for theme in ['dark','light']:
            page=new_page(browser,viewport={'width':1440,'height':900});desktop(page,theme);page.close()
        for report in [False,True]:
            page=new_page(browser,viewport={'width':360,'height':740});compact(page,report);page.close()
        page=new_page(browser,viewport={'width':1440,'height':900});animations(page);page.close()
        page=new_page(browser,viewport={'width':360,'height':740},java_script_enabled=False);fallback(page);page.close()
        close_browser(browser)
