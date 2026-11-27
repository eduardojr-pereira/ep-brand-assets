"""Responsibility: Behavior tests for canonical navigation; no visual preview is generated."""

from playwright.sync_api import sync_playwright

from support import ROOT, ENV, load_page, launch_browser, new_page, close_browser
FIXTURE = '''{% import 'components/web/navigation.html' as n %}
<nav data-ui-scroll-nav style="position:sticky;top:0;z-index:3;display:flex;gap:20px;background:var(--ui-color-bg)">{{ n.nav_link('Home','#home',true) }}{{ n.nav_link('Projects','#projects') }}{{ n.nav_link('Contact','#contact') }}</nav>
<div id="diagonal">{{ n.diagonal('View Project','#projects') }}</div>
<div id="editorial">{% call n.editorial('Home','Return to the beginning','#home') %}<span>Icon</span>{% endcall %}</div>
<div id="filters" data-ui-filter="collection" style="display:flex;gap:20px">{{ n.filter_button('All','all',true) }}{{ n.filter_button('Selected','selected') }}</div>
<div id="github">{% call n.disclosure('GitHub') %}{{ n.menu_link('Portfolio','#projects') }}{{ n.menu_link('Knowledge Base','#contact') }}{% endcall %}</div>
<div id="areas">{% call n.disclosure(message('shared.catalog.areas'),'area') %}{{ n.area_option(message('shared.catalog.areas'),'all',true) }}{{ n.area_option('Data Analytics','analytics') }}{% endcall %}</div>
<div id="back">{{ n.return_link('← Back to Portfolio','#projects') }}</div>
<div id="top">{{ n.return_link('Back to Top ↑','#home',true) }}</div>
<section data-ui-section id="home">Home</section><section data-ui-section id="projects">Projects</section><section data-ui-section id="contact">Contact</section>'''


def load(page, theme='dark', lottie=False):
    load_page(page, ENV.from_string(FIXTURE).render(), theme, lottie=lottie, css=':root{--ui-sticky-offset:40px}section{height:850px}#diagonal,#editorial,#filters,#github,#areas,#back,#top{padding:12px 20px}#editorial{max-width:340px}')


def translate(locator):
    return locator.evaluate('(e)=>{const m=new DOMMatrix(getComputedStyle(e).transform);return [m.m41,m.m42]}')


def test(page, theme):
    load(page, theme)
    link = page.locator('#diagonal a')
    link.hover()
    page.wait_for_timeout(600)
    assert translate(link.locator('.ui-link__move')) == [8, 0]
    assert translate(link.locator('.ui-link__arrow')) == [3, -3]
    assert link.evaluate("e=>getComputedStyle(e,'::after').transform") == 'matrix(1, 0, 0, 1, 0, 0)'
    nav = page.get_by_role('link', name='Projects', exact=True)
    width = nav.bounding_box()['width']
    nav.hover(); page.wait_for_timeout(500)
    assert abs(nav.bounding_box()['width'] - width) < .1
    assert nav.locator('.ui-link__semibold').evaluate('e=>getComputedStyle(e).opacity') == '1'
    page.evaluate("document.addEventListener('ui:filterchange', e=>window.lastFilter=e.detail)")
    page.get_by_role('button', name='Selected').click()
    assert page.get_by_role('button', name='Selected').get_attribute('aria-pressed') == 'true'
    assert page.get_by_role('button', name='All', exact=True).get_attribute('aria-pressed') == 'false'
    assert page.evaluate('window.lastFilter') == {'name': 'collection', 'value': 'selected'}
    github = page.locator('#github details')
    github.locator('summary').click()
    assert github.get_attribute('open') is not None
    menu_link = github.get_by_role('link', name='Portfolio', exact=True)
    menu_link.hover(); page.wait_for_timeout(600)
    assert translate(menu_link.locator('.ui-link__move')) == [8, 0]
    assert translate(menu_link.locator('.ui-link__arrow')) == [3, -3]
    menu_link.focus(); page.keyboard.press('Escape')
    assert github.get_attribute('open') is None
    assert github.locator('summary').evaluate('e=>e===document.activeElement')
    areas = page.locator('#areas details')
    areas.locator('summary').click(); areas.get_by_role('button', name='Data Analytics').click()
    assert areas.get_attribute('open') is None
    assert areas.get_attribute('data-ui-filtered') == 'true'
    assert areas.locator('summary .ui-link__regular').inner_text() == 'Data Analytics'
    assert page.evaluate('window.lastFilter') == {'name': 'area', 'value': 'analytics'}
    areas.locator('summary').click(); page.locator('#back').click(position={'x': 500,'y': 5})
    assert areas.get_attribute('open') is None
    back = page.locator('#back a'); back.hover(); page.wait_for_timeout(600)
    assert translate(back.locator('.ui-return__current'))[0] < 0
    assert translate(back.locator('.ui-return__next')) == [0, 0]
    top = page.locator('#top a')
    assert top.evaluate("e=>getComputedStyle(e,'::after').transform") == 'matrix(1, 0, 0, 1, 0, 0)'
    top.hover(); page.wait_for_timeout(600)
    assert translate(top.locator('.ui-return__current'))[1] < 0
    page.locator('#editorial a').hover(); page.wait_for_timeout(600)
    assert translate(page.locator('.ui-editorial-link__content')) == [8, 0]
    title = page.locator('.ui-editorial-link__title').bounding_box()
    desc = page.locator('.ui-editorial-link__description').bounding_box()
    assert desc['y'] >= title['y'] + title['height']
    assert abs(desc['x'] - title['x']) < .1
    page.evaluate("document.getElementById('projects').scrollIntoView()")
    page.wait_for_function("document.querySelector('nav a[href=\"#projects\"]').getAttribute('aria-current')==='location'")
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_function("document.querySelector('nav a[href=\"#contact\"]').getAttribute('aria-current')==='location'")
    print(f'PASS: {theme} links, arrow, underline, stable nav, filters, dropdowns, return links, editorial layout, scroll state')


def test_geometry(page):
    body = '''<nav data-ui-scroll-nav><a href="#one">One</a><a href="#two">Two</a><a href="#three">Three</a></nav><section id="one"><p data-i18n-text="content.geometry">Short</p></section><section id="two">Two</section><section id="three">Three</section>'''
    local={'en':{'content.geometry':'Short'},'pt-BR':{'content.geometry':' '.join(['Uma descrição longa']*300)}}
    load_page(page,body,local=local,css='nav{height:40px}section{min-height:850px}p{margin:0;width:260px}html{overflow-anchor:none}')
    page.evaluate("window.scrollTo(0,document.getElementById('two').offsetTop+10)")
    page.wait_for_function("document.querySelector('nav a:nth-child(2)').getAttribute('aria-current')==='location'")
    before=page.evaluate('scrollY')
    page.evaluate("UI.i18n.set('pt-BR')")
    page.wait_for_function("document.querySelector('nav a:nth-child(1)').getAttribute('aria-current')==='location'")
    assert page.evaluate('scrollY')==before
    page.evaluate("document.querySelector('#one p').style.display='none'")
    page.wait_for_function("document.querySelector('nav a:nth-child(2)').getAttribute('aria-current')==='location'")
    assert page.evaluate('scrollY')==before
    print('PASS: active section after locale and layout changes without scrolling')


def test_check_adapter(page):
    requests=[]
    page.on('request',lambda request:requests.append(request.url))
    load(page,lottie=True)
    page.wait_for_function("document.querySelectorAll('[data-ui-check-player][data-ui-lottie-ready]').length===2",timeout=15000)
    assert page.locator('[data-ui-check-player] svg').count()==2
    assert page.evaluate("window.lottie.version") == '5.12.2'
    page.evaluate('''() => {window.checkCalls=[]; for(const host of document.querySelectorAll('[data-ui-check-player]')) {const p=UI.assets.get(host); const play=p.playSegments.bind(p);p.playSegments=(s,force)=>{checkCalls.push(s);return play(s,force);};}}''')
    area = page.locator('#areas details');area.locator('summary').click(); area.get_by_role('button',name='Data Analytics').click()
    assert area.get_attribute('open') is not None
    page.wait_for_function("!document.querySelector('#areas details').open")
    segments = page.evaluate('checkCalls')
    assert [0,44] in segments and [85,119] in segments
    page.evaluate("UI.theme.set('light')")
    page.wait_for_function("document.querySelectorAll('[data-ui-check-player][data-ui-lottie-ready]').length===2")
    # Closed details hides the panel: Chromium innerText can be empty even with intact DOM labels.
    assert area.get_attribute('open') is None
    assert area.get_attribute('data-ui-value') == 'analytics'
    selected = area.locator('button[aria-pressed=true]')
    assert selected.count() == 1
    assert selected.get_attribute('data-ui-filter-value') == 'analytics'
    assert selected.locator('[data-ui-label]').all_text_contents() == ['Data Analytics', 'Data Analytics']
    assert area.locator('summary [data-ui-label]').all_text_contents() == ['Data Analytics', 'Data Analytics']
    assert area.locator('summary .ui-link__regular').inner_text() == 'Data Analytics'
    assert area.locator('button[data-ui-filter-value="all"]').get_attribute('aria-pressed') == 'false'
    assert page.evaluate('''() => {const h=document.querySelector('#areas [aria-pressed="true"] [data-ui-check-player]');return Math.abs(UI.assets.get(h).currentFrame-44)<1;}''')
    assert sum(url.endswith('/vendor/lottie/lottie.min.js') for url in requests)==1
    assert sum(url.endswith('/animations/lottie-checkbox-v1-orange.json') for url in requests)==1
    print('PASS: real Lottie SVG, cached source/player, segments, delayed closing and theme reload with selection preserved')


if __name__ == '__main__':
    with sync_playwright() as pw:

        browser = launch_browser(pw)

        page = new_page(browser, viewport={'width': 1000, 'height': 700})
        page.set_default_timeout(5000)

        test(page, 'dark'); page.close()
        page = new_page(browser, viewport={'width':1000,'height':700})
        test(page, 'light'); page.close()
        page = new_page(browser, viewport={'width':1000,'height':700})
        test_check_adapter(page); page.close()
        page = new_page(browser, viewport={'width':1000,'height':700})
        test_geometry(page); page.close()
        page = new_page(browser, viewport={'width':390,'height':844}, reduced_motion='reduce')

        load(page)
        link=page.locator('#diagonal a');link.hover()
        assert translate(link.locator('.ui-link__move')) == [0,0]
        assert translate(link.locator('.ui-link__arrow')) == [0,0]
        page.locator('#areas summary').click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.locator('#areas button').last.click()
        assert page.locator('#areas details').get_attribute('open') is None
        print('PASS: mobile width and reduced motion')
        page = new_page(browser, java_script_enabled=False)
        load(page);page.locator('#github summary').click()
        assert page.locator('#github details').get_attribute('open') is not None
        assert page.locator('#github').get_by_role('link',name='Portfolio').is_visible()
        print('PASS: native disclosure without JavaScript')

        close_browser(browser)
