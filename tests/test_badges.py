"""Responsibility: Focused catalog, SVG regeneration and canonical badge markup tests."""
from collections import Counter
from support import environment, load_page, launch_browser, new_page, close_browser
from badge_catalog import load_catalog, technology_ids, active_entry
from render_badges import verify, contrast
from presentation import validate_bindings
from playwright.sync_api import sync_playwright

CAT=load_catalog()
LOCAL={'en':{'content.method':'Time-series CV'},'pt-BR':{'content.method':'Validação cruzada em séries temporais'}}

def catalog_checks():
    entries=CAT['entries']; counts=Counter(e['category'] for e in entries)
    assert counts['technologies']>=48 and counts['licenses']>=3 and counts['status']>=6,counts
    assert set(counts)=={'technologies','licenses','status'}
    assert all('legacy_only' not in e for e in entries)
    assert technology_ids(['surprise','python','pyspark','apache_spark','python'])==['python','pyspark','apache_spark','surprise']
    for ident in ('time_series_cv_en','data_analytics_en'):
        try: active_entry(ident)
        except ValueError: pass
        else: raise AssertionError(ident)
    assert contrast('#ffffff','#000000')==21
    print(f'PASS: catalog IDs, retired graphical categories rejected, distinct Spark identities and stable technology order ({dict(counts)})',flush=True)
    print(f'PASS: {verify()} real SVGs, canonical geometry, embedded PNGs, source hashes, contrast and localized pairs',flush=True)

FIXTURE='''{% import 'components/web/badges.html' as b %}
{{ b.badges([{'src':'/'+code.path,'label':'MIT','href':'/license/'},{'src':'/'+technology.path,'label':technology.label}]) }}
{{ b.method_badges([message('content.method')]) }}'''

def browser_checks():
    markup=environment(LOCAL).from_string(FIXTURE).render(code=active_entry('mit'),technology=active_entry('python'))
    validate_bindings(markup,LOCAL)
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        try:
            page=new_page(browser,viewport={'width':360,'height':740});load_page(page,markup,'dark',local=LOCAL)
            tag=page.locator('.ui-method-badge');assert tag.inner_text()=='Time-series CV'
            assert page.locator('.ui-badge-link').get_attribute('href')=='/license/'
            assert page.locator('.ui-badges img').count()==2
            page.wait_for_function("[...document.querySelectorAll('.ui-badges img')].every(e=>e.complete && e.naturalWidth>0)")
            assert page.locator('.ui-method-badges img,.ui-method-badges a').count()==0
            page.evaluate("UI.i18n.set('pt-BR')");assert tag.inner_text()=='Validação cruzada em séries temporais'
            before=tag.evaluate('e=>getComputedStyle(e).color');page.evaluate("UI.theme.set('light')");assert tag.evaluate('e=>getComputedStyle(e).color')!=before
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            print('PASS: linked SVG, informational HTML methods, shared language/theme and narrow layout',flush=True);page.close()
        finally: close_browser(browser)
if __name__=='__main__':
    catalog_checks();browser_checks()
