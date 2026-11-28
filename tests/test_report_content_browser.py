"""Responsibility: Exercise built analytical and interactive consumer pages in a real browser.
Boundaries: Synthetic fixtures only, no real report design, analysis, network service or deployment.
"""
import copy
import mimetypes
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlparse

from playwright.sync_api import sync_playwright
from support import launch_browser, ORIGIN
from test_builder import fixture, write_json
from test_report_content import upgrade
from builder import build
from validation import read_json


def main():
    with TemporaryDirectory(prefix='ui-report-browser-', dir=Path.home()/'Downloads') as folder:
        root = Path(folder)
        source, output = root/'source', root/'artifact'
        plan = fixture(source)
        ident = plan['pages'][1]['project']
        upgrade(source, ident, 'analytical')
        plan['pages'][1]['sections'] = []
        app_ident = 'selected_projects/interactive_example'
        app = source/app_ident
        app.mkdir(parents=True)
        for name in ('README.md','README.pt-BR.md'):
            (app/name).write_text('fixture')
        original = copy.deepcopy(read_json(source/ident/'project.json'))
        original['schema_version'] = 1
        del original['sections'], original['report']
        write_json(app/'project.json',original)
        upgrade(source,app_ident,'app')
        registry = read_json(source/'config/projects.json')
        registry['projects'].append({'path':app_ident,'featured':False})
        write_json(source/'config/projects.json',registry)
        plan['pages'].append({'route':app_ident+'/reports/index.html','kind':'report','project':app_ident,'title':None,'sections':[]})
        build(source,plan,output)
        origin=ORIGIN
        def serve(route):
            url=route.request.url
            if not url.startswith(origin+'/'):
                route.abort(); return
            file=(output/unquote(urlparse(url).path).lstrip('/')).resolve()
            if not file.is_relative_to(output) or not file.is_file():
                route.fulfill(status=404,body='Not found'); return
            route.fulfill(status=200,content_type=mimetypes.guess_type(file.name)[0] or 'application/octet-stream',body=file.read_bytes())
        with sync_playwright() as playwright:
            browser=launch_browser(playwright)
            try:
                for viewport in ({'width':1280,'height':800},{'width':390,'height':844}):
                    page=browser.new_page(locale='en-US',viewport=viewport,color_scheme='dark')
                    errors=[];bad=[]
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
                    page.on('response',lambda response:bad.append(response.url) if response.status>=400 else None)
                    page.route('**/*',serve)
                    page.goto(origin+'/reports/demo/index.html',wait_until='load')
                    page.locator('#line-chart[data-ui-plotly-ready]').wait_for(timeout=30000)
                    assert page.locator('#line-chart').evaluate('(n)=>Array.from(n.data[0].y)')==[2,3]
                    page.evaluate("UI.i18n.set('pt-BR'); UI.theme.set('light')")
                    page.wait_for_function("document.querySelector('#line-chart').layout.title.text === 'Observações'")
                    page.wait_for_function("document.documentElement.dataset.theme === 'light'")
                    assert page.locator('#line-chart').evaluate('(n)=>Array.from(n.data[0].y)')==[2,3]
                    assert page.locator('[data-ui-artifact-explorer]').count()==1
                    assert page.locator('a[download]').count()==1
                    assert page.locator('a[download]').evaluate('a=>fetch(a.href).then(r=>r.text())')=='x,y\n1,2\n2,3\n'
                    page.goto(origin+'/'+app_ident+'/reports/index.html',wait_until='load')
                    assert page.locator('#play').inner_text()=='Jogar'
                    assert page.evaluate('typeof window.Plotly')=='undefined'
                    page.locator('#play').click()
                    page.wait_for_function("document.querySelector('#result').textContent === 'fixture'")
                    page.evaluate("UI.i18n.set('en'); UI.theme.set('dark')")
                    assert page.locator('#play').inner_text()=='Play'
                    assert page.locator('#result').inner_text()=='fixture'
                    assert not errors and not bad,(errors,bad)
                    page.close()
                    print(f"PASS: built report + application (intercepted same-origin requests), locale/theme, chart data, authorized download and app state at {viewport['width']} px",flush=True)
            finally:
                browser.close()


if __name__=='__main__':
    main()
