/* EP i18n — shared interface strings. Project content is translated by the catalog layer. */
(function(){
'use strict';
const translations={
'en':{
footerRole:"Economics · Data Science · Analytics",
footerAbout:"About Me",
footerBio1:"Economist by training and data scientist by practice. I combine econometrics, machine learning, and business knowledge to turn data into decisions.",
footerBio2:"My work spans statistical analysis, predictive modeling, and interactive dashboards built with Python, SQL, and Power BI/Tableau. I focus on questions where analytical rigor meets business impact, such as forecasting, pricing, and customer analytics.",
footerBio3:"Open to connecting with teams that value data-driven decision-making.",
footerLearn:"Learn more",
footerExplore:"EXPLORE",
footerHome:"Home",
footerHomeDesc:"Return to the portfolio",
footerSelectedDesc:"Applied data science & insights",
footerLabsDesc:"Programming & experiments",
footerKnowledgeDesc:"Research, notes & documentation",
footerSocial:"Follow & Connect",
footerTop:"Back to Top ↑",
footerTopAria:"Back to Top",
footerAria:"Portfolio footer",
footerEditorialAria:"Explore and connect",
exploreAria:"Explore",
emailAria:"Email",
reportSections:"Sections",
reportSectionsAria:"Report sections",
headerAria:"Site header",
navAria:"Main navigation",
displayAria:"Display preferences",
languageSelectorAria:"Language selector",
languagesAria:"Languages",
featured:"Featured",
selectedProject:"Selected Project",
learningLab:"Learning Lab",
categoriesAria:"Project categories",
technologiesAria:"Technologies",
areasAria:"Project areas",
topicPython:"Python Programming",
topicAnalytics:"Data Analytics",
topicML:"Machine Learning",
themeToDark:"Switch to dark theme",
themeToLight:"Switch to light theme",
site:'EP Design System',headline:'Data Science Portfolio',description:'Language and theme persist when you navigate between pages.',other:'Open second page',back:'Back to start',second:'Second page: preferences preserved',secondDescription:'Try changing the controls and navigating back.',theme:'Theme',language:'Language',current:'Current preferences',dark:'Dark',light:'Light',
navProjects:'Projects',navGithub:'GitHub',personalWebsite:'Website',backToShowcase:'Back to Showcase',allProjects:'All projects',githubPortfolio:'Portfolio repository',knowledgeBase:'Knowledge Base',brandAssets:'EP Brand Assets',githubProfile:'GitHub Profile',
heroLabel:'Data Science · Analytics · Applied Projects',lead:'Explore applied analyses, interactive reports and reproducible methods. Each project connects a practical question to evidence, results and limitations, with source code and documentation available on GitHub.',
exploreTitle:'Explore by category',exploreSubtitle:'Filter projects by area or collection. Only published reports are shown.',collectionLabel:'Collection',selectedProjects:'Selected Projects',learningLabs:'Learning Labs',area:'Area',projectsReports:'Projects & reports',empty:'No published projects match these filters. Choose another category or collection.',code:'Code',documentation:'Documentation',view:'View'
},
'pt-BR':{
footerRole:"Economia · Ciência de Dados · Analytics",
footerAbout:"Sobre mim",
footerBio1:"Economista por formação e cientista de dados pela prática. Combino econometria, aprendizado de máquina e conhecimento de negócios para transformar dados em decisões.",
footerBio2:"Meu trabalho abrange análise estatística, modelagem preditiva e dashboards interativos desenvolvidos com Python, SQL e Power BI/Tableau. Meu foco está em questões que conectam rigor analítico e impacto nos negócios, como previsão, precificação e análise de clientes.",
footerBio3:"Aberto a conexões com equipes que valorizam decisões orientadas por dados.",
footerLearn:"Saiba mais",
footerExplore:"EXPLORE",
footerHome:"Início",
footerHomeDesc:"Voltar ao portfólio",
footerSelectedDesc:"Ciência de dados aplicada e insights",
footerLabsDesc:"Programação e experimentos",
footerKnowledgeDesc:"Pesquisa, anotações e documentação",
footerSocial:"Acompanhe e conecte-se",
footerTop:"Voltar ao topo ↑",
footerTopAria:"Voltar ao topo",
footerAria:"Rodapé do portfólio",
footerEditorialAria:"Explore e conecte-se",
exploreAria:"Explore",
emailAria:"E-mail",
reportSections:"Seções",
reportSectionsAria:"Seções do relatório",
headerAria:"Cabeçalho do site",
navAria:"Navegação principal",
displayAria:"Preferências de exibição",
languageSelectorAria:"Seletor de idioma",
languagesAria:"Idiomas",
featured:"Destaque",
selectedProject:"Projeto selecionado",
learningLab:"Laboratório de aprendizado",
categoriesAria:"Categorias do projeto",
technologiesAria:"Tecnologias",
areasAria:"Áreas dos projetos",
topicPython:"Programação em Python",
topicAnalytics:"Análise de Dados",
topicML:"Aprendizado de Máquina",
themeToDark:"Ativar tema escuro",
themeToLight:"Ativar tema claro",
site:'EP Design System',headline:'Portfólio de Ciência de Dados',description:'Idioma e tema permanecem ao navegar entre páginas.',other:'Abrir segunda página',back:'Voltar ao início',second:'Segunda página: preferências preservadas',secondDescription:'Altere os controles e volte à primeira página.',theme:'Tema',language:'Idioma',current:'Preferências atuais',dark:'Escuro',light:'Claro',
navProjects:'Projetos',navGithub:'GitHub',personalWebsite:'Website',backToShowcase:'Voltar à vitrine',allProjects:'Todos os projetos',githubPortfolio:'Repositório do portfólio',knowledgeBase:'Base de Conhecimento',brandAssets:'EP Brand Assets',githubProfile:'Perfil GitHub',
heroLabel:'Ciência de Dados · Analytics · Projetos aplicados',lead:'Explore análises aplicadas, relatórios interativos e métodos reproduzíveis. Cada projeto conecta uma questão prática a evidências, resultados e limitações, com código-fonte e documentação disponíveis no GitHub.',
exploreTitle:'Explore por categoria',exploreSubtitle:'Filtre os projetos por área ou coleção. Apenas relatórios publicados são exibidos.',collectionLabel:'Coleção',selectedProjects:'Projetos selecionados',learningLabs:'Laboratórios de aprendizado',area:'Área',projectsReports:'Projetos e relatórios',empty:'Nenhum projeto publicado corresponde a esses filtros. Escolha outra categoria ou coleção.',code:'Código',documentation:'Documentação',view:'Visualizar'
}};
let active='en';try{if(localStorage.getItem('ep_locale')==='pt-BR')active='pt-BR';}catch(_){}
function render(){
 const strings=translations[active];document.documentElement.lang=active;
 document.querySelectorAll('[data-i18n-aria]').forEach(node=>{
   const value=strings[node.dataset.i18nAria];
   if(typeof value==='string')node.setAttribute('aria-label',value);
 });
 document.querySelectorAll('[data-i18n-replace]').forEach(node=>{
   const value=strings[node.dataset.i18nReplace];
   if(typeof value==='string')node.setAttribute('data-replace',value);
 });
 document.querySelectorAll('[data-i18n-aria-en][data-i18n-aria-pt]').forEach(node=>{
   node.setAttribute('aria-label',active==='pt-BR'?node.dataset.i18nAriaPt:node.dataset.i18nAriaEn);
 });
 document.querySelectorAll(document.documentElement.classList.contains('ep-report-document')?'.ep-header [data-i18n],.ep-footer [data-i18n],.ep-report-nav [data-i18n]':'[data-i18n]').forEach(node=>{const value=strings[node.dataset.i18n];if(typeof value==='string')node.textContent=value;});
 document.querySelectorAll(document.documentElement.classList.contains('ep-report-document')?'.ep-header [data-i18n-en][data-i18n-pt],.ep-footer [data-i18n-en][data-i18n-pt],.ep-report-nav [data-i18n-en][data-i18n-pt]':'[data-i18n-en][data-i18n-pt]').forEach(node=>{node.textContent=active==='pt-BR'?node.dataset.i18nPt:node.dataset.i18nEn;});
 document.querySelectorAll('[data-language-toggle]').forEach(button=>{button.textContent=active==='en'?'PT-BR':'EN';button.setAttribute('aria-label',active==='en'?'Mudar para português':'Switch to English');});document.querySelectorAll('[data-language-select]').forEach(select=>{select.value=active;select.setAttribute('aria-label',strings.language);});document.querySelectorAll('[data-language-current]').forEach(node=>{node.textContent=active==='pt-BR'?'PT-BR':'EN-US';});document.querySelectorAll('[data-language-choice]').forEach(button=>{button.setAttribute('aria-current',String(button.dataset.languageChoice===active));});document.querySelectorAll('.ep-header__language-control>summary').forEach(summary=>{summary.setAttribute('aria-label',strings.language);});
 document.querySelectorAll('[data-theme-toggle]').forEach(button=>{
   button.dataset.lightLabel=strings.light;
   button.dataset.darkLabel=strings.dark;
   button.dataset.lightAria=strings.themeToLight;
   button.dataset.darkAria=strings.themeToDark;
 });
 window.EPTheme?.refresh();
 document.querySelectorAll('[data-current]').forEach(node=>{node.textContent=`${active} · ${document.documentElement.getAttribute('data-theme')}`;});
}
function apply(locale){active=locale==='pt-BR'?'pt-BR':'en';try{localStorage.setItem('ep_locale',active);}catch(_){}render();document.dispatchEvent(new CustomEvent('ep:languagechange',{detail:{locale:active}}));}
document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('[data-language-toggle]').forEach(button=>button.addEventListener('click',()=>apply(active==='en'?'pt-BR':'en')));document.querySelectorAll('[data-language-select]').forEach(select=>select.addEventListener('change',()=>apply(select.value)));document.querySelectorAll('[data-language-choice]').forEach(button=>button.addEventListener('click',()=>{apply(button.dataset.languageChoice);const dropdown=button.closest('details');if(dropdown){dropdown.open=false;dropdown.querySelector('summary')?.focus();}}));document.querySelectorAll('.ep-header__language-control').forEach(dropdown=>dropdown.addEventListener('keydown',event=>{if(event.key==='Escape'&&dropdown.open){dropdown.open=false;dropdown.querySelector('summary')?.focus();event.preventDefault();}}));document.addEventListener('ep:themechange',render);render();document.dispatchEvent(new CustomEvent('ep:languagechange',{detail:{locale:active}}));});
window.EPI18n=Object.freeze({apply,get current(){return active;}});
})();