"""Responsibility: Test safe-preview, report localization and disclosure-state regressions.
Boundaries: No consumer report generation or publication.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright
from support import environment, load_page, launch_browser, new_page, close_browser
from presentation import validate_bindings
from artifact_preview import prepare_artifact, MAX_BYTES, MAX_ROWS, MAX_COLUMNS

LOCAL={
 'en':{'content.result':'Synthetic result','content.limit':'Synthetic limitation','content.file':'Model evaluation','content.topic':'Statistics','content.method':'Time-series CV','content.source':'Source dataset','content.metric':'Rows','content.value':'1,200'},
 'pt-BR':{'content.result':'Resultado sintético','content.limit':'Limitação sintética','content.file':'Avaliação do modelo','content.topic':'Estatística','content.method':'Validação cruzada temporal','content.source':'Conjunto de dados de origem','content.metric':'Linhas','content.value':'1.200'}
}


def preview_checks():
    with TemporaryDirectory() as tmp:
        root=Path(tmp); (root/'data.csv').write_text('name,value\n'+'<tag>,5\n'*25); (root/'long.txt').write_text('a'*(MAX_BYTES+1)); (root/'summary.json').write_text('{"value":"<script>alert(1)</script>"}'); (root/'diagram.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>'); (root/'report.pdf').write_bytes(b'%PDF'); (root/'bad.txt').write_bytes(b'\xff'); (root/'link.txt').symlink_to(root/'long.txt')
        allowed={p.name for p in root.iterdir()}
        csv_item=prepare_artifact(root,'data.csv',allowed)
        assert csv_item['kind']=='csv' and len(csv_item['rows'])==MAX_ROWS and csv_item['truncated'] and csv_item['rows'][0][0]=='<tag>'
        (root/'wide.csv').write_text(','.join('x' for _ in range(MAX_COLUMNS+2))+'\n'+','.join('y'*400 for _ in range(MAX_COLUMNS+2)))
        wide=prepare_artifact(root,'wide.csv',{'wide.csv'}); assert wide['truncated'] and len(wide['columns'])==MAX_COLUMNS and len(wide['rows'][0][0])==300
        assert len(prepare_artifact(root,'long.txt',allowed)['text'])==MAX_BYTES
        assert prepare_artifact(root,'summary.json',allowed)['kind']=='text'
        assert prepare_artifact(root,'diagram.svg',allowed)['kind']=='image'
        assert prepare_artifact(root,'report.pdf',allowed)['kind']=='fallback'
        assert prepare_artifact(root,'bad.txt',allowed)['kind']=='fallback'
        for name in ('../data.csv','/data.csv','link.txt','not-authorized.txt','a\\b'):
            try: prepare_artifact(root,name,allowed|{'../data.csv','/data.csv','a\\b'})
            except ValueError: pass
            else: raise AssertionError(name)
        assert prepare_artifact(root,'summary.json',allowed)['href']=='summary.json'
        # Even explicitly authorized existing files need portable published names.
        for name in ('with space.csv','caf\u00e9.csv','literal%20.csv','hash#.csv','double..csv'):
            (root/name).write_text('name,value\nx,1',encoding='utf-8')
            try: prepare_artifact(root,name,{name})
            except ValueError: pass
            else: raise AssertionError(name)
        (root/'nested').mkdir()
        (root/'nested/data-01.csv').write_text('name,value\nx,1',encoding='utf-8')
        assert prepare_artifact(root,'nested/data-01.csv',{'nested/data-01.csv'})['href']=='nested/data-01.csv'
        from routing import relative_href, validate_links
        href=relative_href('report/index.html','nested/data-01.csv')
        validate_links({'report/index.html':f'<a href="{href}" download>File</a>'},{'nested/data-01.csv'})
    print('PASS: explicit allowlist, safe paths, inert formats and bounded previews',flush=True)


def markup():
    env=environment(LOCAL); m=env.globals['message']
    files=[{'name':'evaluation.csv','format':'CSV','href':'/fixture-data/evaluation.csv','label':m('content.file'),'kind':'csv','columns':[{'label':'RMSE'},{'label':'Model'}],'rows':[['10','<script>test</script>']],'truncated':True},
           {'name':'summary.json','format':'JSON','href':'/fixture-data/summary.json','label':m('content.file'),'kind':'text','text':'{"value":"<script>test</script>"}','truncated':False},
           {'name':'report.pdf','format':'PDF','href':'/fixture-data/report.pdf','kind':'fallback','truncated':False},
           {'name':'image.png','format':'PNG','href':'/fixture-data/missing.png','kind':'image','truncated':False}]
    items=[{'label':m('shared.conclusion.results'),'body':[m('content.result')]},{'label':m('shared.conclusion.limitations'),'body':[m('content.limit')]},{'label':m('shared.conclusion.next_steps'),'body':[]}]
    sources=[{'label':m('content.source'),'href':'/source','overview':[{'label':m('content.metric'),'value':m('content.value')}]}]
    topics=[{'label':m('content.topic'),'href':'/kb/statistics'}];methods=[m('content.method')]
    tpl="""{% import 'components/web/report_sections.html' as r %}<main>{{ r.conclusion('conclusion',items,files) }}{{ r.references('references',sources,topics,methods) }}{{ r.references('technical-only',none,topics,methods) }}{{ r.conclusion('empty',[],[]) }}</main>"""
    html=env.from_string(tpl).render(items=items,files=files,sources=sources,topics=topics,methods=methods)
    validate_bindings(html,LOCAL); assert '<script>test</script>' not in html and '&lt;script&gt;test&lt;/script&gt;' in html
    return html


def state_check(page, locale):
    is_pt=locale=='pt-BR'
    assert page.locator('html').get_attribute('lang')==locale
    assert page.locator('#conclusion-title').text_content()==('Conclusão' if is_pt else 'Conclusion')
    assert page.locator('#references-title').text_content()==('Referências' if is_pt else 'References')
    assert page.locator('#references .ui-method-badge').inner_text()==('Validação cruzada temporal' if is_pt else 'Time-series CV')
    assert page.locator('#references .ui-reference-topics a').inner_text()==('Estatística' if is_pt else 'Statistics')
    assert page.locator('#references .ui-metric strong').inner_text()==('1.200' if is_pt else '1,200')
    assert page.locator('#references .ui-reference-topics svg').count()==0
    assert page.locator('#technical-only .ui-grid--two').count()==0
    assert page.locator('#empty').count()==0
    assert page.locator('.ui-indexed-item').count()==3


def browser_checks(html):
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        try:
            page=new_page(browser,locale='pt-BR',viewport={'width':1280,'height':900},reduced_motion='reduce');load_page(page,html,local=LOCAL,lottie=True,css='main{margin:20px;min-width:0}')
            state_check(page,'pt-BR')
            rows=page.locator('.ui-indexed-item');rows.nth(0).locator('summary').click();rows.nth(2).locator('summary').click()
            toggle=page.locator('[data-ui-search-toggle]');toggle.click();query=page.locator('[data-ui-search-query]');query.fill('avaliacao json')
            assert page.locator('[data-ui-artifact-item]:visible').count()==1
            page.locator('[data-ui-artifact-select]:visible').click()
            assert page.locator('[data-ui-artifact-preview]:visible h4').inner_text()=='summary.json'
            assert page.locator('[data-ui-artifact-preview]:visible pre').inner_text()=='{"value":"<script>test</script>"}'
            assert toggle.get_attribute('aria-label')=='Fechar busca'
            page.wait_for_function("document.querySelector('[data-ui-toggle-player]').hasAttribute('data-ui-lottie-ready')")
            assert page.evaluate("Math.round(UI.assets.get(document.querySelector('[data-ui-toggle-player]')).currentFrame) >= 28")
            for locale in ('en','pt-BR','en'):
                page.evaluate('(locale)=>UI.i18n.set(locale)',locale);state_check(page,locale)
                assert query.input_value()=='avaliacao json' and query.is_visible()
                assert rows.nth(0).get_attribute('open') is not None and rows.nth(2).get_attribute('open') is not None
                assert page.locator('[data-ui-artifact-item]:visible').count()==1
                assert page.locator('[data-ui-artifact-preview]:visible h4').inner_text()=='summary.json'
                assert toggle.get_attribute('aria-label')==('Close search' if locale=='en' else 'Fechar busca')
                assert query.get_attribute('placeholder')==('File name or format…' if locale=='en' else 'Nome ou formato do arquivo…')
                assert page.locator('[data-ui-artifact-preview]:visible a[download]').inner_text()==('Download file' if locale=='en' else 'Baixar arquivo')
            page.evaluate("UI.theme.set('light')")
            assert query.input_value()=='avaliacao json' and page.locator('[data-ui-artifact-preview]:visible h4').inner_text()=='summary.json'
            query.fill('no match');assert page.locator('[data-ui-artifact-empty]').is_visible();assert page.locator('[data-ui-artifact-preview]:visible h4').inner_text()=='summary.json'
            page.evaluate("UI.i18n.set('pt-BR')");assert page.locator('[data-ui-artifact-empty]').inner_text()=='Nenhum arquivo encontrado.'
            query.press('Escape');assert not query.is_visible() and query.input_value()=='' and toggle.get_attribute('aria-expanded')=='false'
            assert page.locator('[data-ui-artifact-item]:visible').count()==4
            page.wait_for_function("UI.assets.get(document.querySelector('[data-ui-toggle-player]'))?.currentFrame===0")
            print('PASS: PT-BR cold startup, repeated locale/theme switches preserve query, selection and expansion; localized accessibility and real Lottie settling',flush=True)
            page.close()
            page=new_page(browser,viewport={'width':360,'height':740},reduced_motion='reduce');load_page(page,html,local=LOCAL,css='main{margin:12px;min-width:0}')
            page.locator('.ui-indexed-item').nth(2).locator('summary').click();page.locator('[data-ui-artifact-select]').nth(2).click()
            assert page.locator('[data-ui-artifact-preview]:visible').inner_text().find('Preview unavailable')>=0
            page.evaluate("UI.i18n.set('pt-BR')");assert 'Prévia indisponível' in page.locator('[data-ui-artifact-preview]:visible').inner_text()
            page.locator('[data-ui-artifact-select]').nth(3).click();page.locator('[data-ui-image-error]').wait_for(state='visible');assert 'Prévia indisponível' in page.locator('[data-ui-image-error]').inner_text()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            assert len(page.locator('.ui-artifact-layout').evaluate('e=>getComputedStyle(e).gridTemplateColumns').split())==1
            print('PASS: mobile stacking, unsupported/missing image fallback and no overflow',flush=True);page.close()
            page=new_page(browser,java_script_enabled=False,viewport={'width':360,'height':740});load_page(page,html,local=LOCAL,scripts=False)
            page.locator('.ui-indexed-item').nth(2).locator('summary').click()
            assert page.locator('[data-ui-artifact-preview]:visible').count()==4
            assert page.locator('[data-ui-artifact-preview] a[download]:visible').count()==4
            assert not page.locator('[data-ui-search-control]').is_visible()
            assert page.locator('iframe,object,embed').count()==0
            print('PASS: native disclosure and all authorized download links without JavaScript',flush=True);page.close()
        finally: close_browser(browser)

def shared_search_checks():
    local={'en':{'content.search':'Search notes','content.close':'Close notes search','content.placeholder':'Note title'},'pt-BR':{'content.search':'Buscar notas','content.close':'Fechar busca de notas','content.placeholder':'Título da nota'}}
    image={'src':'/assets/icons/flag_us.svg','en_src':'/assets/icons/flag_us.svg','pt_br_src':'/assets/icons/flag_br.svg','label':'Example','alt':'Example','caption':'Example'}
    html=environment(local).from_string("{% import 'components/web/disclosure.html' as d %}{% import 'components/web/analytical.html' as a %}{% import 'components/web/interactive.html' as i %}{% import 'components/web/badges.html' as b %}{{ d.search_control('notes',message('content.search'),message('content.close'),message('content.placeholder')) }}{{ a.image_figure(image) }}{{ i.evidence([image]) }}{{ b.badges([image]) }}").render(image=image)
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        try:
            page=new_page(browser,locale='pt-BR',reduced_motion='reduce');load_page(page,html,local=local,lottie=True)
            page.evaluate("window.queries=[];document.addEventListener('ui:searchchange',e=>queries.push(e.detail.query))")
            toggle=page.locator('[data-ui-search-toggle]');query=page.locator('[data-ui-search-query]')
            assert toggle.get_attribute('aria-label')=='Buscar notas'
            toggle.click();assert query.evaluate('e=>e===document.activeElement')
            query.fill('ação');assert page.evaluate('queries.at(-1)')=='ação'
            assert page.evaluate("UI.disclosure.matches('Acao em notas','ação')")
            assert page.locator('img').count()==3 and page.locator('img').evaluate_all("els=>els.every(e=>e.getAttribute('src')==='/assets/icons/flag_br.svg')")
            page.evaluate("UI.i18n.set('en')");assert query.input_value()=='ação' and toggle.get_attribute('aria-label')=='Close notes search' and query.get_attribute('placeholder')=='Note title'
            assert page.locator('img').evaluate_all("els=>els.every(e=>e.getAttribute('src')==='/assets/icons/flag_us.svg')")
            query.press('Escape');assert not query.is_visible() and query.input_value()=='' and page.evaluate('queries.at(-1)')=='' and toggle.evaluate('e=>e===document.activeElement')
            assert not page.locator('[data-ui-artifact-explorer]').count()
            page.close()
        finally: close_browser(browser)
    print('PASS: independent reusable search control, bilingual labels, focus, query event and shared image variants',flush=True)

if __name__=='__main__':
    preview_checks();browser_checks(markup());shared_search_checks()
