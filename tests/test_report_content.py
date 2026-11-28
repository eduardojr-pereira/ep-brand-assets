"""Responsibility: Test the generic consumer contract with analytical, interactive and independent fixtures.
Boundaries: Synthetic data only; no real report migration, model execution, or deployment.
"""
import copy
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from builder import build, render
from presentation import ROOT
from test_builder import fixture, inventory, bilingual, write_json, report_fixture
from validation import read_json

TEMPLATE = '''{# Responsibility: Compose fixture content.
Boundaries: No shell or preferences. #}
{% import 'components/web/report_sections.html' as r %}
{% import 'components/web/plotly.html' as p %}
{% import 'components/web/badges.html' as b %}
{% import 'components/web/localization.html' as t %}
{% import 'components/web/navigation.html' as n %}
{% macro content(sections, report) %}
{% call r.section(sections[0],1) %}
<p{{ t.binding(report.description) }}>{{ t.value(report.description) }}</p>
{{ b.badges(report.technologies) }}
{{ n.text_link(message('shared.project.documentation'),report.links.documentation.en,false,report.links.documentation['pt-BR']) }}
{% for chart in report.charts.values() %}{{ p.prepared_chart(chart) }}{% endfor %}
{% if report.artifacts %}{{ r.artifact_explorer('fixture-artifacts',report.artifacts) }}{% endif %}
{% if 'content/app.js' in report.files %}<div data-fixture-app data-words="{{ report.files['content/words.json'] }}"><button type="button" id="play"{{ t.binding(message('content.play')) }}>{{ t.value(message('content.play')) }}</button><output id="result"></output></div>{% endif %}
{% endcall %}
{% endmacro %}'''
APP = '''/* Responsibility: Exercise consumer-only game behavior.\nBoundaries: No global preferences or shell. */
(() => {const app=document.querySelector('[data-fixture-app]'); const button=app.querySelector('button'); button.addEventListener('click',async()=>{const words=await fetch(app.dataset.words).then(r=>r.json()); app.querySelector('output').textContent=words[0];});})();'''


def upgrade(source, ident, profile='plain'):
    project = source / ident
    meta = report_fixture(source, ident)
    local = {lang: {'content.play': 'Play' if lang == 'en' else 'Jogar', 'content.chart': 'Observations' if lang == 'en' else 'Observações', 'content.fallback': 'Chart unavailable' if lang == 'en' else 'Gráfico indisponível'} for lang in ('en','pt-BR')}
    write_json(project/'translations.json', local)
    (project/'content').mkdir(exist_ok=True)
    (project/'content/project_content.html').write_text(TEMPLATE, encoding='utf-8')
    if profile == 'analytical':
        (project/'outputs').mkdir(exist_ok=True)
        (project/'outputs/table.csv').write_text('x,y\n1,2\n2,3\n')
        (project/'outputs/private.csv').write_text('private,fixture')
        meta['report']['files'].append({'path': 'outputs/table.csv', 'role': 'artifact', 'label': None})
        write_json(project/'content/charts/line.json', {'figure': {'data': [{'type':'scatter','x':[1,2],'y':[2,3]}], 'layout': {'title':{'text':'Observations'}}}, 'translations': {'layout': {'title.text':'content.chart'}}, 'colors': [], 'palette': 'ep-muted-pastel', 'config': {'responsive': True}})
        meta['report']['charts'].append({'id':'line-chart','path':'content/charts/line.json','label':'content.chart','fallback':'content.fallback'})
    elif profile == 'app':
        (project/'content/app.js').write_text(APP, encoding='utf-8')
        (project/'content/app.css').write_text('/* Responsibility: Fixture app.\nBoundaries: No global styles. */\n[data-fixture-app] {display: grid;}')
        write_json(project/'content/words.json', ['fixture'])
        meta['report']['files'] += [{'path':'content/'+name,'role':role,'label':None} for name, role in [('app.js','script'),('app.css','style'),('words.json','asset')]]
    write_json(project/'project.json', meta)
    return meta


class ReportContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix='ui-report-test-', dir=Path.home()/'Downloads')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root/'source'
        self.plan = fixture(self.source)
        self.ident = self.plan['pages'][1]['project']
        self.project = self.source/self.ident
        self.meta = upgrade(self.source, self.ident, 'analytical')
        self.plan['pages'][1]['sections'] = []
        self.output = self.root/'output'

    def save(self):
        write_json(self.project/'project.json', self.meta)

    def reject(self, regex):
        self.save()
        with self.assertRaisesRegex(ValueError, regex):
            build(self.source, self.plan, self.output)
        self.assertFalse(self.output.exists())

    def test_three_consumers_one_builder(self):
        registry = read_json(self.source/'config/projects.json')
        for ident, profile in [('selected_projects/interactive_example','app'), ('independent_experiments/third_example','plain')]:
            project = self.source/ident
            project.mkdir(parents=True)
            for name in ('README.md','README.pt-BR.md'):
                (project/name).write_text('fixture')
            original = copy.deepcopy(self.meta)
            original['schema_version'] = 1
            del original['sections'], original['report']
            write_json(project/'project.json', original)
            upgrade(self.source, ident, profile)
            registry['projects'].append({'path':ident,'featured':False})
            self.plan['pages'].append({'route':ident+'/reports/index.html','kind':'report','project':ident,'title':None,'sections':[]})
        write_json(self.source/'config/projects.json', registry)
        original = inventory(self.source)
        build(self.source, self.plan, self.output)
        paths = inventory(self.output)
        analytic = paths['reports/demo/index.html'].decode()
        app = paths['selected_projects/interactive_example/reports/index.html'].decode()
        plain = paths['independent_experiments/third_example/reports/index.html'].decode()
        self.assertIn('data-ui-plotly-spec', analytic)
        self.assertIn('data-ui-artifact-explorer', analytic)
        self.assertIn('data-ui-href-pt-br="https://github.com/eduardojr-pereira/data-science-portfolio/blob/main/learning_labs/demo/README.pt-BR.md"', analytic)
        self.assertIn('data-words="../content/words.json"', app)
        self.assertIn('src="../content/app.js"', app)
        self.assertIn('href="../content/app.css"', app)
        self.assertNotIn('plotly.min.js', app+plain)
        self.assertNotIn('content/app.js', analytic+plain)
        self.assertEqual(sum(p.endswith('plotly.min.js') for p in paths),1)
        self.assertEqual(sum(p.endswith('/python.svg') for p in paths),1)
        for path in (self.ident+'/outputs/table.csv','selected_projects/interactive_example/content/words.json'):
            self.assertEqual(paths[path],original[path])
        for name in ('private.csv','unpublished.csv','project.json','translations.json','project_content.html','line.json'):
            self.assertFalse(any(p.endswith('/'+name) for p in paths), name)
        self.assertEqual(inventory(self.source),original)
        build(self.source,self.plan,self.root/'second')
        self.assertEqual(paths,inventory(self.root/'second'))

    def test_plain_report_needs_no_runtime(self):
        upgrade(self.source,self.ident)
        build(self.source,self.plan,self.output)
        self.assertFalse((self.output/'shared/assets/vendor/plotly/plotly.min.js').exists())

    def test_metadata_is_sole_section_source(self):
        self.plan['pages'][1]['sections']=[{'id':'other'}]
        self.reject('sections belong to project metadata')

    def test_sections_order(self):
        self.meta['sections'].append({'id':'missing','label':bilingual('Second'),'title':bilingual('Second'),'description':None})
        self.reject('navigation order')

    def test_no_inline_script(self):
        (self.project/'content/project_content.html').write_text(TEMPLATE.replace('{% endcall %}','<script>alert(1)</script>{% endcall %}'))
        self.reject('Only canonical inert')

    def test_no_shell(self):
        (self.project/'content/project_content.html').write_text(TEMPLATE.replace('{% endcall %}','<main></main>{% endcall %}'))
        self.reject('document shell')

    def test_chart_must_be_used(self):
        (self.project/'content/project_content.html').write_text(TEMPLATE.replace('{{ p.prepared_chart(chart) }}',''))
        self.reject('exactly one mount')

    def test_duplicate_mount(self):
        (self.project/'content/project_content.html').write_text(TEMPLATE.replace('{{ p.prepared_chart(chart) }}','{{ p.prepared_chart(chart) }}{{ p.prepared_chart(chart) }}'))
        self.reject('duplicate HTML id')

    def test_missing_translation(self):
        local=read_json(self.project/'translations.json');del local['pt-BR']['content.chart']
        write_json(self.project/'translations.json',local)
        self.reject('Translation keys')

    def test_metadata_translation_collision(self):
        local=read_json(self.project/'translations.json')
        for entries in local.values(): entries['content.page.title']='Other'
        write_json(self.project/'translations.json',local)
        self.reject('collides')

    def test_unapproved_artifact(self):
        self.meta['report']['files'][0]['path']='datasets/private.csv'
        self.reject('outside its authorized directory')

    def test_duplicate_file(self):
        self.meta['report']['files']*=2
        self.reject('Duplicate or unsupported')

    def test_traversal(self):
        self.meta['report']['files'][0]['path']='outputs/../unpublished.csv'
        self.reject('Unsafe artifact path')

    def test_symlink(self):
        (self.project/'outputs/table.csv').unlink()
        (self.project/'outputs/table.csv').symlink_to(self.project/'unpublished.csv')
        self.reject('Symlink')

    def test_missing_file(self):
        (self.project/'outputs/table.csv').unlink()
        self.reject('Missing/unsafe')

    def test_chart_spec_cannot_be_published(self):
        self.meta['report']['files'].append({'path':'content/charts/line.json','role':'asset','label':None})
        self.reject('build-only inputs')

    def test_unknown_badge(self):
        self.meta['report']['badges']=['java']
        self.reject('Not an active graphical badge')

    def test_undeclared_link(self):
        (self.project/'content/project_content.html').write_text(TEMPLATE.replace('{% endcall %}','<a href="missing.csv">Missing</a>{% endcall %}'))
        self.reject('Missing local destination')


if __name__ == '__main__':
    unittest.main()
