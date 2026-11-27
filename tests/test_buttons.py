"""Responsibility: Browser behavior tests for the shared action macros, not a design preview."""
from playwright.sync_api import sync_playwright

from support import ROOT, ENV, load_page, launch_browser, new_page, close_browser
FIXTURE = '''{% import 'components/web/buttons.html' as b %}
<div class="row" id="learn">{{ b.radial_link(message('shared.action.learn'),'#contact') }}</div>
<div class="row" id="arrows">{{ b.carousel_arrow('Previous project','previous',true) }}{{ b.carousel_arrow('Next project') }}</div>
<div class="row" id="orbits">{{ b.orbit_link('hero-test',message('shared.action.selected'),message('shared.action.selected_ring'),'#projects') }}{{ b.orbit_link('cta-test',message('shared.action.hello'),message('shared.action.hello_ring'),'#contact','cta') }}</div>
<form id="form">{{ b.send_action() }}</form>
<div style="height:1100px"></div><section id="projects">Projects</section><section id="contact">Contact</section>'''


def load(page, theme='dark'):
    load_page(page, ENV.from_string(FIXTURE).render(), theme, css='.row,form{margin:16px;display:flex;gap:24px;align-items:center}body{container-type:inline-size}')


def matrix(locator):
    return locator.evaluate('(e)=>{const m=new DOMMatrix(getComputedStyle(e).transform);return [m.m11,m.m22,m.m41,m.m42]}')


def desktop(page, theme):
    load(page, theme)
    link = page.get_by_role('link',name='Learn More')
    assert matrix(link.locator('.ui-action__fill'))[:2] == [0,0]
    link.hover(); page.wait_for_timeout(650)
    assert matrix(link.locator('.ui-action__fill'))[:2] == [1,1]
    assert matrix(link.locator('.ui-link__move'))[2:] == [8,0]
    assert matrix(link.locator('.ui-link__arrow'))[2:] == [3,-3]
    assert link.evaluate('e=>getComputedStyle(e).color') == ('rgb(0, 0, 0)' if theme == 'dark' else 'rgb(255, 255, 255)')
    previous = page.get_by_role('button',name='Previous project')
    previous.hover(); page.wait_for_timeout(600)
    assert previous.is_disabled()
    assert matrix(previous.locator('.ui-action__fill'))[:2] == [0,0]
    next_button = page.get_by_role('button',name='Next project')
    next_button.hover(); page.wait_for_timeout(600)
    assert matrix(next_button.locator('.ui-action__fill'))[:2] == [1,1]
    assert matrix(next_button.locator('svg'))[2:] == [0,0]
    assert next_button.evaluate('e=>!e.hasAttribute("data-ui-orbit")')
    orbit = page.get_by_role('link',name='Selected Projects')
    assert orbit.evaluate('e=>getComputedStyle(e).borderTopWidth') == '0px'
    box = orbit.bounding_box()
    page.mouse.move(box['x']+box['width']-5, box['y']+box['height']/2)
    page.wait_for_timeout(650)
    assert matrix(orbit.locator('.ui-action__body'))[2] > 0
    assert matrix(orbit.locator('.ui-action__fill'))[:2] == [1,1]
    assert orbit.locator('.ui-action__ring').evaluate('e=>getComputedStyle(e).animationDuration') == '20s'
    assert orbit.locator('.ui-action__moving').evaluate('e=>getComputedStyle(e).animationDuration') == '3.37s'
    page.mouse.move(0,0); page.wait_for_timeout(900)
    assert all(abs(v) < .05 for v in matrix(orbit.locator('.ui-action__body'))[2:])
    page.evaluate("UI.i18n.set('pt-BR')")
    assert page.get_by_role('link',name='Projetos Selecionados').count() == 1
    assert 'PROJETOS SELECIONADOS' in page.locator('[data-ui-ring-label]').first.text_content()
    assert page.locator('svg defs [id]').count() == 4
    page.evaluate('window.scrollTo(0,document.body.scrollHeight)')
    page.wait_for_function("document.querySelector('[data-ui-orbit]').hasAttribute('data-ui-orbit-paused')")
    page.evaluate('window.scrollTo(0,0)')
    page.wait_for_function("!document.querySelector('[data-ui-orbit]').hasAttribute('data-ui-orbit-paused')")
    print(f'PASS: {theme} radial fill, shared diagonal, carousel, orbit, magnetism, offscreen pause and localized ring')


def send(page):
    load(page)
    page.evaluate("document.querySelector('form').addEventListener('submit',e=>e.preventDefault())")
    root = page.locator('[data-ui-send]'); button = root.locator('button')
    before = button.bounding_box(); height = root.bounding_box()['height']
    button.click()
    assert root.get_attribute('data-state') == 'idle'
    assert root.get_by_role('status').text_content() == ''
    assert page.evaluate("()=>{try{UI.actions.setSendState(document.querySelector('[data-ui-send]'),'success');return false}catch(e){return true}}")
    page.evaluate("UI.actions.setSendState(document.querySelector('[data-ui-send]'),'pending')")
    assert button.is_disabled()
    assert button.get_attribute('aria-busy') == 'true'
    page.evaluate("UI.actions.setSendState(document.querySelector('[data-ui-send]'),'error')")
    assert not button.is_disabled()
    assert root.get_by_role('status').text_content() == 'Unable to send. Try again.'
    page.evaluate("UI.actions.setSendState(document.querySelector('[data-ui-send]'),'success',{confirmed:true})")
    assert root.get_by_role('status').text_content() == "We'll be in touch soon."
    assert root.locator('.ui-send__check').is_visible()
    assert not root.locator('.ui-link__arrow').is_visible()
    assert button.is_disabled()
    assert abs(before['width']-button.bounding_box()['width']) < .1
    assert abs(height-root.bounding_box()['height']) < .1
    page.evaluate("UI.i18n.set('pt-BR')")
    assert root.get_by_role('status').text_content() == 'Entraremos em contato em breve.'
    page.evaluate("UI.actions.setSendState(document.querySelector('[data-ui-send]'),'idle')")
    assert not button.is_disabled()
    print('PASS: native submit, confirmed success only, pending, retry, translated feedback and stable geometry')


if __name__ == '__main__':
    with sync_playwright() as pw:

        browser = launch_browser(pw)

        for theme in ['dark','light']:
            page = new_page(browser, viewport={'width':1200,'height':800}); page.set_default_timeout(5000)

            desktop(page,theme)
        page = new_page(browser, viewport={'width':1200,'height':800}); page.set_default_timeout(5000)

        send(page)
        page = new_page(browser, viewport={'width':390,'height':844},has_touch=True,is_mobile=True,reduced_motion='reduce')

        load(page)
        orbit = page.get_by_role('link',name='Selected Projects'); orbit.focus()
        assert all(abs(v) < .05 for v in matrix(orbit.locator('.ui-action__body'))[2:])
        assert orbit.locator('.ui-action__ring').evaluate('e=>getComputedStyle(e).animationName') == 'none'
        assert orbit.locator('.ui-action__idle').evaluate('e=>getComputedStyle(e).opacity') == '1'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        print('PASS: mobile, touch and reduced motion')
        page = new_page(browser, java_script_enabled=False);load(page)
        assert page.get_by_role('link',name='Learn More').get_attribute('href') == '#contact'
        assert page.get_by_role('button',name='Send message').is_enabled()
        print('PASS: native link and submit without JavaScript')

        close_browser(browser)
