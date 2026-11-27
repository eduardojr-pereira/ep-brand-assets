"""Responsibility: Isolated integration checks of canonical templates, not a visual preview."""
from playwright.sync_api import sync_playwright

from support import ROOT, ENV, load_page, launch_browser
LABELS = dict(collection='Collection', all='All', selected='Selected', learning='Learning Labs', all_areas='All areas', search='Search', placeholder='Project or technology…', clear_search='Clear search', clear='Clear filters', singular='project', plural='projects', empty='No matches', results='Project results', play='Play results', pause='Pause results', previous='Previous project', next='Next project', view='View Project')
PIXEL = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"%3E%3Crect width="200" height="100" fill="gray"/%3E%3C/svg%3E'
PROJECTS = [dict(title='Bike Sharing', description='Demanda histórica', collection='selected', collection_label='Selected', areas=['analytics','ml'], topics=['Analytics','Machine Learning'], badges=[dict(src=PIXEL,label='Pandas')], search='regression', links=[dict(label='Notebook',href='#notebook',primary=False),dict(label='View Project',href='#bike',primary=True)], subtitle='Demand insights', href='#bike',frames=[dict(src=PIXEL,alt='Figure one',caption='Figure one'),dict(src=PIXEL,alt='Figure two',caption='Figure two')],metrics=[dict(value='100',label='Example metric'),dict(value='200',label='Another metric')]),dict(title='Hangman', description='Jogo da Forca', collection='learning', collection_label='Learning', areas=['python'], topics=['Python'], badges=[], search='game', links=[dict(label='View Project',href='#hangman',primary=True)],href='#hangman',frames=[],metrics=[])]
FIXTURE = '''{% import 'components/web/interactive.html' as i %}<section id="catalog">{{ i.catalog('catalog', projects, areas, labels) }}</section><section id="selected">{{ i.selected_projects(projects,labels) }}</section><section id="marquee">{{ i.marquee('Contact invitation','LET’S CONNECT','example@example.org','#contact','Pause marquee','Play marquee') }}</section><section id="contact">Contact</section>'''

def load(page, theme='dark', scripts=True):
    html=ENV.from_string(FIXTURE).render(projects=PROJECTS,areas=[dict(value='analytics',label='Analytics'),dict(value='python',label='Python')],labels=LABELS)
    load_page(page, html, theme, css='section{margin:20px;min-width:0}#contact{min-height:300px}', scripts=scripts)


def desktop(page, theme):
    load(page,theme)
    cards=page.locator('[data-ui-project]:visible');assert cards.count()==2
    page.get_by_role('button',name='Learning Labs').click();assert cards.count()==1 and 'Hangman' in cards.first.inner_text()
    page.get_by_role('searchbox').fill('forca');assert cards.count()==1
    page.get_by_role('searchbox').fill('xyz');assert cards.count()==0 and page.get_by_text('No matches').is_visible()
    page.locator('.ui-catalog__info [data-ui-reset]').click();assert cards.count()==2
    page.locator('.ui-catalog__area summary').click();page.get_by_role('button',name='Analytics',exact=True).click();assert cards.count()==1 and 'Bike Sharing' in cards.first.inner_text()
    page.locator('.ui-catalog__info [data-ui-reset]').click();assert cards.count()==2
    link=cards.first.get_by_role('link',name='View Project');link.hover();page.wait_for_timeout(600)
    matrix=lambda loc: loc.evaluate('(e)=>{const m=new DOMMatrix(getComputedStyle(e).transform);return [m.m41,m.m42]}')
    assert matrix(link.locator('.ui-link__move'))==[8,0] and matrix(link.locator('.ui-link__arrow'))==[3,-3]
    sel=page.locator('[data-ui-carousel]');assert sel.get_by_role('button',name='Previous project').is_disabled()
    sel.get_by_role('button',name='Next project').click();page.wait_for_timeout(800);assert sel.locator('[data-ui-carousel-count]').inner_text()=='02 / 02';assert sel.get_by_role('button',name='Next project').is_disabled()
    sel.get_by_role('button',name='Previous project').click();page.wait_for_timeout(800);assert sel.locator('[data-ui-carousel-count]').inner_text()=='01 / 02'
    sel.get_by_role('button',name='Figure two').click();assert sel.locator('[data-ui-frame]:visible').get_attribute('alt')=='Figure two'
    assert sel.get_by_role('button',name='Figure two').get_attribute('aria-current')=='true'
    sel.get_by_role('button',name='Pause results').click();assert sel.get_by_role('button',name='Play results').is_visible()
    m=page.locator('[data-ui-marquee]');m.scroll_into_view_if_needed();page.mouse.move(0,0);page.wait_for_timeout(400)
    t=m.locator('.ui-marquee__lanes:not(.ui-marquee__lens) .ui-marquee__track').first
    before=t.evaluate('e=>e.style.transform');page.wait_for_timeout(200);assert t.evaluate('e=>e.style.transform')!=before
    m.get_by_role('link',name='Contact invitation').hover();page.wait_for_timeout(650);assert m.locator('[data-lens-active]').count()==1
    before=t.evaluate('e=>e.style.transform');page.wait_for_timeout(250);assert t.evaluate('e=>e.style.transform')==before
    lens=m.locator('.ui-marquee__lens .ui-marquee__track').first;assert lens.evaluate('e=>e.style.transform')==before
    assert m.locator('.ui-marquee__lens').evaluate('e=>getComputedStyle(e).backgroundColor')==('rgb(255, 255, 255)' if theme=='dark' else 'rgb(0, 0, 0)')
    m.get_by_role('button',name='Pause marquee').click();page.mouse.move(0,0);before=t.evaluate('e=>e.style.transform');page.wait_for_timeout(250);assert t.evaluate('e=>e.style.transform')==before
    m.get_by_role('button',name='Play marquee').click();page.mouse.move(0,0);m.scroll_into_view_if_needed();page.wait_for_function('(before)=>document.querySelector(".ui-marquee__lanes:not(.ui-marquee__lens) .ui-marquee__track").style.transform!==before',arg=before,timeout=3000)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    print(f'PASS: {theme} catalogue, shared diagonal, carousel, evidence, synchronized monochrome lens and pause')

def main():
    with sync_playwright() as p:
        browser=launch_browser(p)
        page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        desktop(page,'dark');page.close()
        page=browser.new_page(viewport={'width':1280,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));desktop(page,'light');page.close();assert not errors,errors
        mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');load(mobile)
        assert mobile.locator('[data-ui-marquee]').get_attribute('data-ui-running') is None
        assert mobile.locator('[data-ui-evidence-toggle]').is_disabled()
        assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
        mobile.locator('[data-ui-carousel] [data-ui-carousel-action="next"]').click();assert mobile.locator('[data-ui-carousel-count]').inner_text()=='02 / 02'
        print('PASS: mobile layout, reduced motion and carousel controls')
        static=browser.new_page(java_script_enabled=False,viewport={'width':390,'height':844});load(static,scripts=False)
        assert static.locator('[data-ui-project]:visible').count()==2
        assert static.get_by_role('link',name='Contact invitation').is_visible()
        assert static.locator('[data-ui-frame]:visible').count()==1
        assert not static.locator('.ui-catalog__controls').is_visible()
        print('PASS: static content and links without JavaScript')
        browser.close()

if __name__=='__main__':main()
