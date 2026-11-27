"""Responsibility: Verify shared analytical composition, semantics and responsive behavior."""
from playwright.sync_api import sync_playwright
from support import environment, load_page, launch_browser, new_page, close_browser
from presentation import validate_bindings

LOCAL={'en':{'content.metric':'Sample metric','content.value':'1,200','content.caption':'Example table','content.figure':'Example figure','content.note':'Synthetic note'},'pt-BR':{'content.metric':'Métrica de exemplo','content.value':'1.200','content.caption':'Tabela de exemplo','content.figure':'Figura de exemplo','content.note':'Nota sintética'}}
PIXEL='data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="100"%3E%3Crect width="200" height="100" fill="gray"/%3E%3C/svg%3E'
FIXTURE='''{% import 'components/web/analytical.html' as a %}
{% import 'components/web/interactive.html' as i %}
<main id="analysis-fixture">
{% call a.grid(3) %}{% call a.surface() %}One{% endcall %}{% call a.surface() %}Two{% endcall %}{% call a.surface() %}Three{% endcall %}{% endcall %}
{% call a.grid(2) %}{% call a.surface() %}Four{% endcall %}{% call a.surface() %}Five{% endcall %}{% endcall %}
{{ a.metrics(metrics) }}{{ a.metrics(metrics,true) }}{{ a.metrics([]) }}
{{ a.divider() }}{% call a.prose() %}<p>Free content</p>{% endcall %}
{% call a.callout(message('content.note')) %}<p>Interpretation</p>{% endcall %}
{{ a.data_table(message('content.caption'),columns,rows) }}
{{ a.image_figure(image,message('content.figure')) }}
{% call a.figure() %}<div id="application">Unconstrained consumer content</div>{% endcall %}
{{ i.project_card(project) }}{{ i.selected_projects([project]) }}
</main>'''

def markup():
    env=environment(LOCAL); m=env.globals['message']; metrics=[{'value':m('content.value'),'label':m('content.metric')},{'value':'0','label':'Zero'}]
    project=dict(title='Example',description='Synthetic content',collection='selected',collection_label='Selected',areas=['test'],topics=[],badges=[],links=[],href='#analysis-fixture',frames=[],metrics=metrics)
    columns=[dict(label='Category',row_header=True)]+[dict(label=f'Column {i}',numeric=True) for i in range(8)]
    rows=[['<sample>']+['1234567890123']*8]
    html=env.from_string(FIXTURE).render(metrics=metrics,project=project,columns=columns,rows=rows,image={'src':PIXEL,'alt':m('content.figure')})
    validate_bindings(html,LOCAL)
    assert '&lt;sample&gt;' in html and '<sample>' not in html
    assert 'ui-feature__metrics' not in html
    return html

def cols(page,selector):
    return len(page.locator(selector).first.evaluate('e=>getComputedStyle(e).gridTemplateColumns').split())

def check_geometry(page):
    assert page.locator('.ui-metrics').count()==3
    assert page.locator('.ui-project-card.ui-surface').count()==1
    assert page.locator('.ui-selected .ui-metrics--compact').count()==1
    for selector in ('.ui-grid .ui-surface','.ui-project-card'):
        assert page.locator(selector).first.evaluate('e=>getComputedStyle(e).padding')=='22px'
        assert page.locator(selector).first.evaluate('e=>getComputedStyle(e).borderRadius')=='16px'
    assert page.locator('.ui-table th[scope="row"]').inner_text()=='<sample>'
    assert page.locator('.ui-table th[scope="col"]').count()==9
    assert page.locator('.ui-table td.ui-table__numeric').count()==8
    assert page.locator('.ui-figure img').get_attribute('alt')=='Example figure'
    assert page.locator('#application').is_visible()
    assert page.locator('.ui-table-scroll').get_attribute('tabindex')=='0'

if __name__=='__main__':
    html=markup()
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        try:
            for theme in ('dark','light'):
                p=new_page(browser,viewport={'width':1280,'height':900},reduced_motion='reduce');load_page(p,html,theme,local=LOCAL,css='main{margin:20px;min-width:0}')
                check_geometry(p);assert cols(p,'.ui-grid--three')==3 and cols(p,'.ui-grid--two')==2
                assert p.locator('.ui-surface').first.evaluate('e=>getComputedStyle(e).backgroundColor')==('rgb(51, 50, 48)' if theme=='dark' else 'rgb(255, 255, 255)')
                p.evaluate("UI.i18n.set('pt-BR')")
                assert p.locator('.ui-metric strong').first.inner_text()=='1.200'
                assert p.locator('.ui-table caption').inner_text()=='Tabela de exemplo'
                assert p.locator('.ui-table-scroll').get_attribute('aria-label')=='Tabela de exemplo'
                assert p.locator('.ui-figure img').get_attribute('alt')=='Figura de exemplo'
                assert p.locator('.ui-callout h2').text_content()=='Nota sintética'
                print(f'PASS: {theme} shared card/metric geometry, semantic table, figure and translated values',flush=True);p.close()
            p=new_page(browser,viewport={'width':900,'height':800},reduced_motion='reduce');load_page(p,html,local=LOCAL,css='main{margin:20px;min-width:0}')
            assert cols(p,'.ui-grid--three')==2
            p.set_viewport_size({'width':360,'height':740})
            assert cols(p,'.ui-grid--three')==1 and cols(p,'.ui-grid--two')==1
            assert cols(p,'.ui-metrics:not(.ui-metrics--compact)')==1 and cols(p,'.ui-metrics--compact')==2
            assert p.locator('.ui-table-scroll').evaluate('e=>e.scrollWidth>e.clientWidth')
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            print('PASS: responsive grids, contained wide-table overflow and compact Selected metrics',flush=True);p.close()
            p=new_page(browser,viewport={'width':360,'height':740},java_script_enabled=False);load_page(p,html,local=LOCAL,scripts=False)
            assert p.locator('.ui-table caption').is_visible() and p.locator('.ui-callout').is_visible() and p.locator('.ui-metric').first.is_visible()
            print('PASS: native analytical content without JavaScript',flush=True);p.close()
        finally: close_browser(browser)
