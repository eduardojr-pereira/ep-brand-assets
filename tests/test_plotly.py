"""Responsibility: Real Plotly regression tests for locale, presentation and interaction preservation."""
from copy import deepcopy
import json
from playwright.sync_api import sync_playwright
from support import environment, load_page, launch_browser, new_page, close_browser
from plotly_presentation import chart_payload
from plotly.offline import get_plotlyjs

LOCAL={
 'en':{'content.title':'Hourly demand','content.x':'Hour','content.y':'Rentals','content.a':'Working day','content.b':'Holiday','content.name':'Observed','content.hover':'Hour %{text}: %{y:.2f}<extra></extra>','content.menu':'Show both','content.alt':'Interactive demand','content.fallback':'See the source notebook.'},
 'pt-BR':{'content.title':'Demanda horária','content.x':'Hora','content.y':'Aluguéis','content.a':'Dia útil','content.b':'Feriado','content.name':'Observado','content.hover':'Hora %{text}: %{y:.2f}<extra></extra>','content.menu':'Mostrar ambos','content.alt':'Demanda interativa','content.fallback':'Consulte o notebook.'}}
FIGURE={'data':[{'type':'scatter','mode':'markers','x':['work','holiday'],'y':[1234.56,456.78],'customdata':['original A','original B'],'name':'Observed','marker':{'size':14},'selectedpoints':[1]}, {'type':'scatter','mode':'markers','x':['work','holiday'],'y':[321,654],'name':'Model','visible':'legendonly'}], 'layout':{'width':900,'height':340,'margin':{'l':70,'r':25,'b':60,'t':90},'xaxis':{'type':'category','tickmode':'array','tickvals':['work','holiday'],'ticktext':['Working day','Holiday']},'yaxis':{'range':[0,1500]},'updatemenus':[{'type':'dropdown','active':0,'buttons':[{'label':'Show both','method':'restyle','args':[{'visible':[True,True]}]},{'label':'Hide model','method':'restyle','args':[{'visible':[True,'legendonly']}]}]}]}}
TRANSLATIONS={'layout':{'title.text':'content.title','xaxis.title.text':'content.x','yaxis.title.text':'content.y','xaxis.ticktext':['content.a','content.b'],'updatemenus[0].buttons[0].label':'content.menu'},'traces':[{'index':0,'fields':{'name':'content.name','text':['content.a','content.b'],'hovertemplate':'content.hover'}}]}
COLORS=[{'trace':0,'path':'marker.color','palette':'ep-muted-pastel','index':0}]

def payload(ident, **kwargs):
    return chart_payload(ident,deepcopy(FIGURE),translations=TRANSLATIONS,colors=COLORS,palette='ep-muted-pastel',local=LOCAL,**kwargs)

def validate_payload():
    raw=str(payload('demand')); assert '</script>' not in raw[:-9]; assert 'localeModule' not in raw; assert '%{text}' in LOCAL['en']['content.hover']
    for bad in [{'layout':{'yaxis.range':'content.title'}},{'traces':[{'index':0,'fields':{'x':'content.a'}}]},{'layout':{'title.text':'content.missing'}},{'layout':{'title.text':['content.a','content.b']}},{'layout':{'xaxis.ticktext':['content.a']}},{'layout':{'xaxis.ticktext':'content.a'}},{'traces':[{'index':0,'fields':{'name':['content.a','content.b']}}]},{'traces':[{'index':0,'fields':{'text':['content.a']}}]}]:
        try: chart_payload('demand',FIGURE,translations=bad,local=LOCAL)
        except ValueError: pass
        else: raise AssertionError('Unsafe binding accepted')
    scale_fig={'data':[{'type':'heatmap','z':[[1,2],[3,4]]}], 'layout':{}}
    spec=str(chart_payload('heatmap',scale_fig,colors=[{'trace':0,'path':'colorscale','palette':'nuuk'}],local=LOCAL))
    cfg=json.loads(spec[spec.index('>')+1:-9]); vals=cfg['colors'][0]['values']; assert vals['light']==vals['dark'] and vals['light'][0][0]==0 and vals['light'][-1][0]==1
    print('PASS: chart payload, safe serialization, canonical categorical/continuous palettes and presentation-only translation fields',flush=True)


def fixture(page, scripts=True):
    env=environment(LOCAL)
    body=env.from_string("{% import 'components/web/plotly.html' as p %}{{ p.chart('demand',message('content.alt'),message('content.fallback')) }}{{ p.chart('second',message('content.alt'),message('content.fallback')) }}").render()+str(payload('demand'))+str(chart_payload('second',{'data':[{'type':'scatter','x':['2024-01-01','2024-02-01','2024-03-01'],'y':[1,2,3]}],'layout':{'height':300,'xaxis':{'type':'date','tickmode':'array','tickvals':['2024-01-01','2024-02-01','2024-03-01'],'tickformat':'%b %Y'}}},translations={'layout':{'title.text':'content.title'}},local=LOCAL))
    load_page(page,body,local=LOCAL,scripts=scripts)


def load_runtime(page):
    # Actual installed Plotly.js, not a fake. Load after DOMContentLoaded to exercise late runtime.
    page.evaluate("()=>{window.localeRequests=0; const originalFetch=window.fetch;window.fetch=(url,...args)=>{if(String(url).endsWith('/vendor/plotly/pt-BR.json'))window.localeRequests++;return originalFetch(url,...args)}}")
    page.add_script_tag(content=get_plotlyjs())
    page.evaluate('UI.plotly.refresh()')
    page.wait_for_function("document.querySelectorAll('[data-ui-plotly-ready]').length===2")
    assert page.evaluate('window.localeRequests')==1


def check_locale(page, locale, theme):
    pt=locale=='pt-BR'; info=page.evaluate("() => {const g=document.getElementById('demand');return {title:g.layout.title.text,x:g.layout.xaxis.title.text,y:g.layout.yaxis.title.text,ticks:g.layout.xaxis.ticktext,menu:g.layout.updatemenus[0].buttons[0].label,name:g.data[0].name,traceText:g.data[0].text,hover:g.data[0].hovertemplate,locale:g._context.locale,separators:g.layout.separators,bg:g.layout.paper_bgcolor,color:g.data[0].marker.color,modebar:[...g.querySelectorAll('.modebar-btn')].map(e=>e.getAttribute('data-title'))}}")
    assert info['title']==('Demanda horária' if pt else 'Hourly demand'),info
    assert info['x']==('Hora' if pt else 'Hour') and info['y']==('Aluguéis' if pt else 'Rentals'),info
    assert info['ticks']==(['Dia útil','Feriado'] if pt else ['Working day','Holiday']),info
    assert info['menu']==('Mostrar ambos' if pt else 'Show both'),info
    assert info['name']==('Observado' if pt else 'Observed') and info['hover']==LOCAL[locale]['content.hover'],info
    assert info['traceText']==info['ticks'],info
    assert info['locale']==locale and info['separators']==(',.' if pt else '.,'),info
    assert info['bg'].lower()==('#333230' if theme=='dark' else '#ffffff'),info
    assert info['color']==('#7CA5A8' if theme=='dark' else '#427C83'),info
    assert ('Ampliar zoom' if pt else 'Zoom in') in info['modebar'],info
    assert ('Fev 2024' if pt else 'Feb 2024') in page.locator('#second .xtick').all_text_contents()


def main_browser(browser):
    page=new_page(browser,locale='pt-BR',viewport={'width':950,'height':800});fixture(page);load_runtime(page)
    print('Plotly.js runtime:',page.evaluate('Plotly.version'),flush=True)
    check_locale(page,'pt-BR','dark')
    page.evaluate("Plotly.Fx.hover(document.getElementById('demand'),[{curveNumber:0,pointNumber:0}])")
    page.wait_for_function("document.querySelector('#demand .hoverlayer').textContent.includes('Dia útil')")
    assert '1234,56' in page.locator('#demand .hoverlayer').text_content() or '1.234,56' in page.locator('#demand .hoverlayer').text_content()
    page.evaluate("Plotly.Fx.unhover(document.getElementById('demand'))")
    page.evaluate("async()=>{let g=document.getElementById('demand');await Plotly.relayout(g,{'xaxis.range':[-.1,.8],'yaxis.range':[100,1000],'updatemenus[0].active':1});await Plotly.restyle(g,{visible:'legendonly'},[1]);await Plotly.restyle(g,{selectedpoints:[[0]]},[0]);window.originalGraph=g;window.originalData=JSON.stringify(g.data.map(t=>[t.x,t.y,t.customdata,t.visible,t.selectedpoints]));window.originalRange=JSON.stringify([g.layout.xaxis.range,g.layout.yaxis.range,g.layout.updatemenus[0].active]);}")
    for locale,theme in [('en','light'),('pt-BR','dark'),('en','dark')]:
        page.evaluate("([l,t])=>{UI.i18n.set(l);UI.theme.set(t);return UI.plotly.refresh()}",[locale,theme]);check_locale(page,locale,theme)
        assert page.evaluate("()=>{const g=document.getElementById('demand');return g===originalGraph && JSON.stringify(g.data.map(t=>[t.x,t.y,t.customdata,t.visible,t.selectedpoints]))===originalData && JSON.stringify([g.layout.xaxis.range,g.layout.yaxis.range,g.layout.updatemenus[0].active])===originalRange}")
    print('PASS: PT-BR cold startup, live locale/theme, native modebar, category labels, hover tokens, preserved zoom/data/visibility/selection/menu',flush=True)
    # Failure after native locale switched: reverting to last committed locale must reconcile.
    page.evaluate("""async()=>{const old=Plotly.relayout;Plotly.relayout=(g,...args)=>{if(g.id==='demand'){return Promise.reject(new Error('partial locale failure'));}return old(g,...args)};try{UI.i18n.set('pt-BR');await UI.plotly.refresh();if(document.getElementById('demand')._context.locale!=='pt-BR'||document.getElementById('demand').layout.title.text!=='Hourly demand')throw Error('partial failure not reproduced');}finally{Plotly.relayout=old;}UI.i18n.set('en');await UI.plotly.refresh();}""")
    check_locale(page,'en','dark')
    assert page.evaluate("()=>{const g=document.getElementById('demand');return g===originalGraph && JSON.stringify(g.data.map(t=>[t.x,t.y,t.customdata,t.visible,t.selectedpoints]))===originalData && JSON.stringify([g.layout.xaxis.range,g.layout.yaxis.range,g.layout.updatemenus[0].active])===originalRange}")
    # Inject rapid consecutive changes and one rejected update; other figures still settle.
    page.evaluate("()=>{const old=Plotly.relayout;window.failure=0;Plotly.relayout=(g,...args)=>{if(g.id==='demand'&&!failure++){return Promise.reject(new Error('fixture failure'));}return old(g,...args)}; UI.i18n.set('pt-BR');UI.theme.set('light');UI.i18n.set('en');UI.theme.set('dark');UI.i18n.set('pt-BR');return UI.plotly.refresh()}")
    assert page.evaluate("document.getElementById('second').layout.title.text")=='Demanda horária'
    page.evaluate('UI.plotly.refresh()');check_locale(page,'pt-BR','dark')
    print('PASS: rapid changes, isolated chart failure and retry, late runtime',flush=True)
    page.close()
    page=new_page(browser,locale='en-US',viewport={'width':360,'height':760});fixture(page);load_runtime(page)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert page.locator('#demand').get_attribute('aria-label')=='Interactive demand'
    assert page.locator('[data-ui-plotly-fallback]').first.is_hidden()
    page.close();page=new_page(browser,viewport={'width':360,'height':760});fixture(page,scripts=False)
    assert page.locator('[data-ui-plotly-fallback]').first.is_visible()
    print('PASS: narrow chart containment and accessible static fallback without JavaScript',flush=True);page.close()

if __name__=='__main__':
    validate_payload()
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        try: main_browser(browser)
        finally: close_browser(browser)
