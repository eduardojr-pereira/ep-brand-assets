"""Browser behavior tests for the shared action macros, not a design preview."""
import os
from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ENV = Environment(loader=FileSystemLoader(ROOT), autoescape=select_autoescape(['html'], default_for_string=True))
FIXTURE = '''{% import 'components/web/buttons.html' as b %}
<div class="row" id="learn">{{ b.radial_link('Learn More','#contact') }}</div>
<div class="row" id="arrows">{{ b.carousel_arrow('Previous project','previous',true) }}{{ b.carousel_arrow('Next project') }}</div>
<div class="row" id="orbits">{{ b.orbit_link('hero-test','Selected Projects','SELECTED PROJECTS','#projects') }}{{ b.orbit_link('cta-test','Say Hello','SAY HELLO','#contact','cta') }}</div>
<form id="form">{{ b.send_action('Send message','Message sent',"We'll be in touch soon.",'Sending…','Unable to send. Try again.') }}</form>
<div style="height:1100px"></div><section id="projects">Projects</section><section id="contact">Contact</section>'''


def load(page, theme='dark'):
    css = '\n'.join((ROOT/'styles'/name).read_text() for name in ['foundations.css','motion-tokens.css','links.css','buttons.css'])
    js = (ROOT/'scripts/buttons.js').read_text()
    html = ENV.from_string(FIXTURE).render()
    page.set_content(f'<!doctype html><html data-theme="{theme}"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>{css}\n.row,form{{margin:16px;display:flex;gap:24px;align-items:center}}body{{container-type:inline-size}}</style></head><body>{html}<script>{js}</script></body></html>')


def matrix(locator):
    return locator.evaluate('(e)=>{const m=new DOMMatrix(getComputedStyle(e).transform);return [m.m11,m.m22,m.m41,m.m42]}')


def desktop(page, theme):
    load(page, theme)
    link = page.get_by_role('link',name='Learn More')
    assert matrix(link.locator('.ep-action__fill'))[:2] == [0,0]
    link.hover(); page.wait_for_timeout(650)
    assert matrix(link.locator('.ep-action__fill'))[:2] == [1,1]
    assert matrix(link.locator('.ep-link__move'))[2:] == [8,0]
    assert matrix(link.locator('.ep-link__arrow'))[2:] == [3,-3]
    assert link.evaluate('e=>getComputedStyle(e).color') == ('rgb(0, 0, 0)' if theme == 'dark' else 'rgb(255, 255, 255)')
    previous = page.get_by_role('button',name='Previous project')
    previous.hover(); page.wait_for_timeout(600)
    assert previous.is_disabled()
    assert matrix(previous.locator('.ep-action__fill'))[:2] == [0,0]
    next_button = page.get_by_role('button',name='Next project')
    next_button.hover(); page.wait_for_timeout(600)
    assert matrix(next_button.locator('.ep-action__fill'))[:2] == [1,1]
    assert matrix(next_button.locator('svg'))[2:] == [0,0]
    assert next_button.evaluate('e=>!e.hasAttribute("data-ep-orbit")')
    orbit = page.get_by_role('link',name='Selected Projects')
    assert orbit.evaluate('e=>getComputedStyle(e).borderTopWidth') == '0px'
    box = orbit.bounding_box()
    page.mouse.move(box['x']+box['width']-5, box['y']+box['height']/2)
    page.wait_for_timeout(650)
    assert matrix(orbit.locator('.ep-action__body'))[2] > 0
    assert matrix(orbit.locator('.ep-action__fill'))[:2] == [1,1]
    assert orbit.locator('.ep-action__ring').evaluate('e=>getComputedStyle(e).animationDuration') == '20s'
    assert orbit.locator('.ep-action__moving').evaluate('e=>getComputedStyle(e).animationDuration') == '3.37s'
    page.mouse.move(0,0); page.wait_for_timeout(900)
    assert all(abs(v) < .05 for v in matrix(orbit.locator('.ep-action__body'))[2:])
    page.evaluate("EPActions.setOrbitLabel(document.querySelector('[data-ep-orbit]'),'Projetos Selecionados','PROJETOS SELECIONADOS')")
    assert page.get_by_role('link',name='Projetos Selecionados').count() == 1
    assert 'PROJETOS SELECIONADOS' in page.locator('[data-ep-ring-label]').first.text_content()
    assert page.locator('svg defs [id]').count() == 4
    page.evaluate('window.scrollTo(0,document.body.scrollHeight)')
    page.wait_for_function("document.querySelector('[data-ep-orbit]').hasAttribute('data-ep-orbit-paused')")
    page.evaluate('window.scrollTo(0,0)')
    page.wait_for_function("!document.querySelector('[data-ep-orbit]').hasAttribute('data-ep-orbit-paused')")
    print(f'PASS: {theme} radial fill, shared diagonal, carousel, orbit, magnetism, offscreen pause and localized ring')


def send(page):
    load(page)
    page.evaluate("document.querySelector('form').addEventListener('submit',e=>e.preventDefault())")
    root = page.locator('[data-ep-send]'); button = root.locator('button')
    before = button.bounding_box(); height = root.bounding_box()['height']
    button.click()
    assert root.get_attribute('data-state') == 'idle'
    assert root.get_by_role('status').text_content() == ''
    assert page.evaluate("()=>{try{EPActions.setSendState(document.querySelector('[data-ep-send]'),'success');return false}catch(e){return true}}")
    page.evaluate("EPActions.setSendState(document.querySelector('[data-ep-send]'),'pending')")
    assert button.is_disabled()
    assert button.get_attribute('aria-busy') == 'true'
    page.evaluate("EPActions.setSendState(document.querySelector('[data-ep-send]'),'error')")
    assert not button.is_disabled()
    assert root.get_by_role('status').text_content() == 'Unable to send. Try again.'
    page.evaluate("EPActions.setSendState(document.querySelector('[data-ep-send]'),'success',{confirmed:true})")
    assert root.get_by_role('status').text_content() == "We'll be in touch soon."
    assert root.locator('.ep-send__check').is_visible()
    assert not root.locator('.ep-link__arrow').is_visible()
    assert button.is_disabled()
    assert abs(before['width']-button.bounding_box()['width']) < .1
    assert abs(height-root.bounding_box()['height']) < .1
    page.evaluate("EPActions.setSendLabels(document.querySelector('[data-ep-send]'),{idle:'Enviar mensagem',success:'Mensagem enviada',successFeedback:'Entraremos em contato em breve.'})")
    assert root.get_by_role('status').text_content() == 'Entraremos em contato em breve.'
    page.evaluate("EPActions.setSendState(document.querySelector('[data-ep-send]'),'idle')")
    assert not button.is_disabled()
    print('PASS: native submit, confirmed success only, pending, retry, translated feedback and stable geometry')


if __name__ == '__main__':
    with sync_playwright() as pw:
        executable = os.environ.get('EP_TEST_BROWSER') or shutil.which('chromium') or shutil.which('google-chrome')
        browser = pw.chromium.launch(**({'executable_path':executable} if executable else {}),headless=True,args=['--no-sandbox'])
        errors = []
        for theme in ['dark','light']:
            page = browser.new_page(viewport={'width':1200,'height':800}); page.set_default_timeout(5000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            desktop(page,theme)
        page = browser.new_page(viewport={'width':1200,'height':800}); page.set_default_timeout(5000)
        page.on('pageerror',lambda e:errors.append(str(e)))
        send(page)
        page = browser.new_page(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,reduced_motion='reduce')
        page.on('pageerror',lambda e:errors.append(str(e)))
        load(page)
        orbit = page.get_by_role('link',name='Selected Projects'); orbit.focus()
        assert all(abs(v) < .05 for v in matrix(orbit.locator('.ep-action__body'))[2:])
        assert orbit.locator('.ep-action__ring').evaluate('e=>getComputedStyle(e).animationName') == 'none'
        assert orbit.locator('.ep-action__idle').evaluate('e=>getComputedStyle(e).opacity') == '1'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        print('PASS: mobile, touch and reduced motion')
        page = browser.new_page(java_script_enabled=False);load(page)
        assert page.get_by_role('link',name='Learn More').get_attribute('href') == '#contact'
        assert page.get_by_role('button',name='Send message').is_enabled()
        print('PASS: native link and submit without JavaScript')
        assert not errors,errors
        browser.close()
