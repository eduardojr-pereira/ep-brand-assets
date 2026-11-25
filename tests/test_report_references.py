import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from render_references import render_references, render_report_licenses

class ReportReferencesTests(unittest.TestCase):
    def test_bike_shape(self):
        html = render_references({'technical_tabs':True,'knowledge_base':[{'label':{'en':'Machine Learning','pt-BR':'Aprendizado de Máquina'},'url':'https://example.org/ml'}], 'methods':['time_series_cv'],'technologies':['Python','CSS'], 'data_source':{'name':'Dataset','url':'https://example.org/data','license_badge':{'id':'cc_by_4_0_data','url':'https://creativecommons.org/licenses/by/4.0/'}},'reproducibility':{'intro':'Build','steps':[],'documentation':'https://example.org/docs','source_code':'https://example.org/code'}})
        self.assertEqual(html.count('data-ep-tab>'),3)
        self.assertEqual(html.count('data-ep-ref-en="Topics" data-ep-ref-pt="Tópicos"'), 2)
        self.assertNotIn('data-ep-ref-en="Knowledge Base"', html)
        self.assertEqual(html.count('data-ep-tab-panel '),3)
        self.assertIn('Data License CC BY 4.0',html)
        self.assertIn('ep-reference-project-links',html)
        self.assertLess(html.index('https://example.org/docs'),html.index('https://example.org/code'))
        self.assertIn('href="https://example.org/ml"',html)
    def test_optional_tabs(self):
        html=render_references({'technical_tabs':True,'technologies':['Python']})
        self.assertEqual(html.count('data-ep-tab>'),1)
        self.assertIn('ep-reference-card--full',html)
        self.assertNotIn('ep-tech-methods-tab',html)
        self.assertEqual(render_references({'technical_tabs':True}),'')
    def test_intro(self):
        html=render_report_licenses([{'id':'mit','url':'https://example.org/license'}])
        self.assertEqual(html.count('<a '),1)
        self.assertEqual(html.count('data-badge-theme'),2)
        self.assertIn('href="https://example.org/license"', html)
        self.assertIn('title="license"', html)
        self.assertNotIn('↗',html)
        with self.assertRaises(ValueError):render_report_licenses([{'id':'mit','url':'javascript:alert(1)'}])
if __name__=='__main__':unittest.main()
