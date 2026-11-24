/* Published report translations. Plotly traces are deliberately unchanged here. */
(function () {
  'use strict';
  const bike = document.querySelector('.bike-local-nav');
  const hangmanLocale = document.getElementById('locale-pt') && document.getElementById('locale-en');

  if (hangmanLocale) {
    // The game already owns a complete, working PT/EN dictionary. Its existing
    // locale buttons remain in the DOM for compatibility but are hidden.
    function syncHangman() {
      const button = document.getElementById(document.documentElement.lang === 'pt-BR' ? 'locale-pt' : 'locale-en');
      if (button && button.getAttribute('aria-pressed') !== 'true') button.click();
    }
    document.addEventListener('ep:languagechange', syncHangman);
    document.addEventListener('DOMContentLoaded', syncHangman);
  }
  if (!bike) return;

  const pt = {
    'Overview':'Visão geral',
    'Business':'Negócio',
    'Exploration':'Exploração',
    'Hourly':'Padrões horários',
    'Models':'Modelos',
    'Conclusions':'Conclusões',
    'Outputs':'Resultados',
    'Interactive technical report · Academic regression exercise':'Relatório técnico interativo · Exercício acadêmico de regressão',
    'Bike Sharing Demand Analysis':'Análise da Demanda por Bicicletas Compartilhadas',
    'Explore daily and hourly demand patterns from Washington, D.C. (2011–2012), compare regression models through chronological validation, and examine the limitations of retrospective demand estimation.':'Explore os padrões diários e horários da demanda em Washington, D.C. (2011–2012), compare modelos de regressão com validação cronológica e examine as limitações da estimativa retrospectiva da demanda.',
    'Time-series CV':'Validação temporal',
    'Dataset overview':'Visão geral dos dados',
    'The UCI dataset contains daily and hourly bike rental totals and weather-related variables. These figures are historical observations, not forecasts.':'O conjunto de dados da UCI contém totais diários e horários de aluguéis de bicicletas e variáveis meteorológicas. Esses números representam observações históricas, não previsões.',
    'Daily observations':'Observações diárias',
    'Total rentals':'Total de aluguéis',
    'Development days':'Dias de desenvolvimento',
    'Holdout days':'Dias de teste cronológico',
    'Total recorded rentals':'Total de aluguéis registrados',
    'Business questions & operational insights':'Questões de negócio e insights operacionais',
    'A historical system-level demand study: where might the operator investigate staffing, bicycle availability or rebalancing windows? These are planning hypotheses, not measured cost savings or station-level prescriptions.':'Um estudo histórico da demanda no sistema: em quais períodos o operador poderia investigar equipes, disponibilidade de bicicletas ou redistribuição? São hipóteses de planejamento, não economias comprovadas nem recomendações específicas por estação.',
    'Most active clock hour':'Horário de maior movimento',
    'Average':'Média de',
    '461.5 rentals':'461,5 aluguéis',
    'per recorded observation at this hour, over 2011–2012. Missing clock-hour records are not imputed as zero.':'por observação registrada nesse horário, em 2011–2012. Horários ausentes não foram imputados como zero.',
    'Demand growth':'Crescimento da demanda',
    'Change in mean daily rentals from 2011 to 2012. It does not establish the causes of growth or a future growth rate.':'Variação da média diária de aluguéis de 2011 para 2012. Isso não estabelece as causas do crescimento nem uma taxa futura.',
    'Operational questions':'Questões operacionais',
    'Compare registered and casual hourly patterns, workdays and non-workdays, and peak windows before planning inventory coverage. Station-level supply data are required to design actual rebalancing routes.':'Compare padrões horários de usuários registrados e ocasionais, dias úteis e não úteis e horários de pico antes de planejar a cobertura da frota. Dados de disponibilidade por estação são necessários para definir rotas de redistribuição.',
    'Evidence, not a production forecast':'Evidências, não previsões em produção',
    'Historical hourly holdout R²:':'R² do teste cronológico horário:',
    '; daily holdout R²:':'; R² do teste cronológico diário:',
    '. These models use observed contemporaneous weather; deployment requires available-at-prediction-time inputs and independent evaluation.':'. Esses modelos utilizam o clima observado no mesmo período; sua implantação exige variáveis disponíveis no momento da previsão e avaliação independente.',
    'Exploratory analysis':'Análise exploratória',
    'Hover to inspect values; use the modebar to zoom, pan or download chart images. In the first chart, switch rider groups and use the range slider to focus on a period.':'Passe o cursor para inspecionar valores; use a barra de ferramentas para ampliar, deslocar ou baixar imagens dos gráficos. No primeiro gráfico, alterne entre grupos de usuários e use o seletor de intervalo para focar um período.',
    'Daily rental demand':'Demanda diária por aluguéis',
    'Choose a rider segment or period; explore detailed values by hovering over the line.':'Escolha um segmento de usuários ou período; passe o cursor sobre a linha para explorar os valores.',
    'Correlations are descriptive; `cnt` is the sum of casual and registered rentals, so its association with those components is structural.':'As correlações são descritivas; `cnt` é a soma dos aluguéis ocasionais e registrados, portanto a associação com esses componentes é estrutural.',
    'Weather comparisons are observational. Group sizes differ, and no causal effect should be inferred from these summaries.':'As comparações meteorológicas são observacionais. Os grupos têm tamanhos diferentes, e não se deve inferir causalidade desses resumos.',
    'Hourly patterns & validation':'Padrões horários e validação',
    'The hourly UCI records cover the same 2011–2012 Capital Bikeshare rentals as the daily dataset, shown at a finer aggregation level. These are not additional rentals.':'Os registros horários da UCI abrangem os mesmos aluguéis do Capital Bikeshare de 2011–2012 presentes nos dados diários, em um nível mais detalhado. Não são aluguéis adicionais.',
    'Recorded hourly observations':'Observações horárias registradas',
    'Selected hourly candidate':'Modelo horário selecionado',
    'Random forest':'Floresta aleatória',
    'Hourly CV RMSE':'RMSE da validação horária',
    'Hourly holdout R²':'R² do teste horário',
    'Hourly chronological holdout':'Teste cronológico horário',
    '76 days':'76 dias',
    'Data completeness':'Completude dos dados',
    'The source has':'A fonte possui',
    'unrecorded clock hours across those days. The absent hours were not artificially imputed.':'horários sem registro nesses dias. As horas ausentes não foram imputadas artificialmente.',
    'How to interpret:':'Como interpretar:',
    "Hourly and daily RMSE/MAE are measured in different units and should not be compared numerically. Both models are retrospective conditional estimates using observed weather at the target date/hour, not proven advance forecasts. The daily model's negative holdout R² is reported transparently. An earlier iteration already examined the holdout; this evaluation is not an untouched external benchmark.":'O RMSE/MAE horário e diário é medido em unidades diferentes e não deve ser comparado numericamente. Ambos os modelos produzem estimativas condicionais retrospectivas usando o clima observado na data/hora de interesse, não previsões antecipadas comprovadas. O R² negativo do modelo diário no teste cronológico é apresentado de forma transparente. Uma versão anterior já examinou esse conjunto de teste; portanto, a avaliação não representa um teste externo ainda não explorado.',
    'Operational questions: How do commute peaks differ from leisure use? Which hours would be important to examine for bicycle rebalancing and staffing? These associations are descriptive and do not prove that a specific intervention would increase demand.':'Questões operacionais: como os picos de deslocamento diferem do uso recreativo? Quais horários merecem investigação para redistribuição de bicicletas e dimensionamento de equipes? Essas associações são descritivas e não comprovam que uma intervenção específica aumentaria a demanda.',
    'Daily model evaluation':'Avaliação do modelo diário',
    'Candidate models are evaluated using expanding-window cross-validation on the development period. The final chronological holdout was examined in earlier pilot revisions, so it must not be presented as an untouched independent benchmark.':'Os modelos candidatos são avaliados por validação cruzada com janela de treinamento crescente no período de desenvolvimento. O conjunto final de teste cronológico já foi examinado em versões piloto anteriores e não pode ser apresentado como uma referência independente ainda não explorada.',
    'Selected candidate':'Modelo selecionado',
    'Polynomial ridge (degree 2)':'Ridge polinomial (grau 2)',
    'Mean CV RMSE:':'RMSE médio da validação:',
    'daily rentals':'aluguéis diários',
    'Chronological holdout':'Teste cronológico',
    'Importance comes from an illustrative Random Forest, not from the selected Polynomial Ridge model; impurity-based importances can be biased.':'A importância das variáveis vem de uma floresta aleatória ilustrativa, não do modelo Ridge polinomial selecionado; medidas baseadas na impureza podem apresentar vieses.',
    'Key findings and limitations':'Principais resultados e limitações',
    'Generalization warning:':'Alerta de generalização:',
    'Negative R² indicates a poor fit relative to the holdout mean baseline. This is not evidence of deployment-ready prediction.':'Um R² negativo indica desempenho inferior à referência baseada na média do conjunto de teste. Isso não demonstra prontidão para previsões em produção.',
    'Demand variation':'Variação da demanda',
    'Rental counts vary across seasons, weather categories and rider groups. These are descriptive patterns, not causal explanations.':'A quantidade de aluguéis varia conforme as estações do ano, as condições meteorológicas e os grupos de usuários. São padrões descritivos, não explicações causais.',
    'Interpretation of model performance':'Interpretação do desempenho dos modelos',
    'Training-only cross-validation was used to select candidates. A difficult chronological holdout reveals limitations not evident from development-fold scores.':'A validação cruzada realizada apenas nos dados de treinamento foi utilizada para selecionar os candidatos. O teste cronológico mais difícil revela limitações que não aparecem nos resultados das partições de desenvolvimento.',
    'Same-day weather':'Clima do mesmo dia',
    'The models use observed same-day weather variables. This is':'Os modelos utilizam variáveis meteorológicas observadas no próprio dia. Trata-se de',
    'retrospective conditional demand estimation':'estimativa retrospectiva condicional da demanda',
    'and must not be described as a day-ahead forecast.':'e não deve ser descrita como previsão para o dia seguinte.',
    'External validity':'Validade externa',
    'These results cover a single city and 2011–2012. Prospective evaluation with a new period would be required before operational use.':'Esses resultados abrangem uma única cidade e os anos de 2011–2012. Uma avaliação prospectiva com novos dados seria necessária antes do uso operacional.',
    'Validated outputs & additional figures':'Resultados validados e figuras adicionais',
    "The HTML is built from the notebook's exported metrics and tables. Use these source artifacts to inspect exact numbers. Additional PNG figures remain available without reproducing them in new storage formats.":'O HTML é construído a partir de métricas e tabelas exportadas pelo notebook. Utilize esses arquivos para conferir os números exatos. As figuras PNG adicionais continuam disponíveis sem necessidade de reproduzi-las em outros formatos.',
    'Daily metrics JSON':'Métricas diárias (JSON)',
    'Hourly metrics JSON':'Métricas horárias (JSON)',
    'Hourly model comparison CSV':'Comparação de modelos horários (CSV)',
    'Hourly holdout predictions CSV':'Predições do teste horário (CSV)',
    'Model comparison CSV':'Comparação de modelos (CSV)',
    'Holdout predictions CSV':'Predições do teste (CSV)',
    'Feature importance CSV':'Importância das variáveis (CSV)',
    'Variable distributions':'Distribuições das variáveis',
    'Tree excerpt':'Trecho de árvore',
    'Notebook demand patterns':'Padrões de demanda do notebook',
    'References and reproducibility':'Referências e reprodutibilidade',
    'Original dataset:':'Conjunto de dados original:',
    ', Fanaee-T & Gama, DOI 10.24432/C5W894, distributed under CC BY 4.0 with attribution.':', Fanaee-T & Gama, DOI 10.24432/C5W894, distribuído sob CC BY 4.0, com atribuição.',
    'Knowledge Base:':'Base de conhecimento:',
    'Machine Learning':'Aprendizado de Máquina',
    'and':'e',
    'Data Analysis & Visualization':'Análise e Visualização de Dados',
    'Implementation:':'Implementação:',
    'execute':'execute',
    'to regenerate data exports, then run':'para regenerar os dados exportados; depois execute',
    'from the project directory to rebuild this HTML. The HTML requires no Python server and includes Plotly.js offline; GitHub Pages hosting is supported.':'na pasta do projeto para reconstruir este HTML. O HTML não requer servidor Python, inclui Plotly.js para uso offline e pode ser hospedado no GitHub Pages.',
    'MAE':'MAE',
    'rentals/hour · R²':'aluguéis/hora · R²',
  };
  const rootNodes = [document.querySelector('.hero'),document.querySelector('main'),bike].filter(Boolean);
  const originals = [];
  const normalize = value => value.replace(/\s+/g,' ').trim();
  for (const root of rootNodes) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement.closest('script,style,svg,.plotly-graph-div')) continue;
      const key = normalize(node.nodeValue);
      if (Object.prototype.hasOwnProperty.call(pt,key)) originals.push({node,original:node.nodeValue,key});
    }
  }
  function syncBike() {
    const translated = document.documentElement.lang === 'pt-BR';
    for (const item of originals) {
      if (!item.node.isConnected) continue;
      if (!translated) { item.node.nodeValue = item.original; continue; }
      const value = item.original;
      const start = value.match(/^\s*/)[0];
      const end = value.match(/\s*$/)[0];
      item.node.nodeValue = start + pt[item.key] + end;
    }
  }
  document.addEventListener('DOMContentLoaded', syncBike);
  document.addEventListener('ep:languagechange', syncBike);
})();
