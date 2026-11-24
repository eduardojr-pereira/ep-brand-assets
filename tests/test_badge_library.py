"""Regression tests for the canonical badge catalog (offline)."""
import json, sys, unittest, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import badge_html as badges
from render_badges import render

class BadgeLibraryTests(unittest.TestCase):
    def test_catalog(self):
        es=json.loads((ROOT/'config/badges.json').read_text())['entries']
        for field in ('id','path','label'):
            self.assertEqual(len({e[field].casefold() for e in es}),len(es))
        self.assertEqual({e['area'] for e in es if e['category']=='topics'}, {f'{i:02d}' for i in range(11)})
        for e in es:
            self.assertEqual((ROOT/e['path']).read_text(),render(e))
            self.assertEqual(ET.fromstring(render(e)).get('height'),'20')
            for t in ('dark','light'):
                ET.fromstring(render(e,t))
    def test_order(self):
        markup=badges.technologies(['Surprise','Python','CSS','css3'])
        self.assertLess(markup.index('alt="Python"'),markup.index('alt="CSS"'))
        self.assertLess(markup.index('alt="CSS"'),markup.index('alt="Surprise"'))
        self.assertEqual(markup.count('alt="CSS"'),1)
    def test_localization_and_theme(self):
        markup=badges.topic('Data Analytics')
        self.assertEqual(markup.count('data-badge-theme="dark"'),2)
        self.assertEqual(markup.count('data-badge-theme="light"'),2)
        self.assertEqual(markup.count('data-badge-locale="pt-BR"'),2)
        self.assertIn('Data Analysis &amp; Visualization',markup)
        self.assertIn('Statistics',badges.topic('Statistics'))
    def test_palette(self):
        pal=json.loads((ROOT/'config/colormaps.json').read_text())['palettes']
        for e in badges.entries().values():
            if e['category'] in ('topics','methods','licenses'):
                p=e['theme_palette'];v=pal[p['id']]
                for t in ('dark','light'):
                    self.assertEqual(e['theme_colors'][t]['background'],v[t][p['index']])
                    self.assertGreaterEqual(e['contrast' if t=='light' else 'dark_contrast'],4.5)
        self.assertEqual(badges.entries()['pending_en']['background'],pal['ep-lipari-adapted']['dark'][5])
    def test_approved_status_and_license_colors(self):
        es=badges.entries()
        for ident in ('partial_en','partial_pt_br'):
            self.assertEqual(es[ident]['background'],'#E8D58A')
            self.assertEqual(es[ident]['foreground'],'#242424')
            self.assertGreaterEqual(es[ident]['contrast'],4.5)
        for ident in ('mit','cc_by_nc_4_0'):
            e=es[ident]
            for theme,bg,fg,pbg,pfg in [('light','#505B7A','#FFFFFF','#000000','#FFFFFF'),('dark','#9EA7C4','#242424','#FFFFFF','#000000')]:
                tree=ET.fromstring(render(e,theme)); ns={'s':'http://www.w3.org/2000/svg'}
                self.assertEqual(tree.find("s:rect[@class='ep-bg']",ns).get('fill'),bg)
                self.assertEqual(tree.find("s:text[@class='ep-fg']",ns).get('fill'),fg)
                self.assertEqual(tree.find("s:rect[@class='ep-prefix-bg']",ns).get('fill'),pbg)
                self.assertEqual(tree.find("s:text[@class='ep-prefix-fg']",ns).get('fill'),pfg)
            self.assertIn('.ep-prefix-bg',render(e))
            self.assertIn('.ep-bg',render(e))
if __name__=='__main__': unittest.main()
