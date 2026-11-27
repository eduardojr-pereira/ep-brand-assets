<a id="readme-top"></a>

<div align="center">

| [English](./README.md) · [Português](./README.pt-BR.md) |

# EP Brand Assets

*Identidade visual, componentes compartilhados e infraestrutura de apresentação para o ecossistema EP.*

</div>

<div align="center">

[Visão Geral](#overview) · [Identidade Visual](#visual-identity) · [Componentes](#shared-components) · [Temas e Idiomas](#themes-and-internationalization) · [Sistema Cromático EP](#ep-analytical-colour-system)<br>
[Estrutura de Diretórios](#directory-structure) · [Uso e Integração](#usage-and-integration) · [Testes e Validação](#testing-and-validation) · [Repositórios](#related-repositories) · [Licença](#license) · [Contato](#contact)

</div>

---

<a id="overview"></a>

## Visão Geral

EP Brand Assets é a fonte canônica da identidade visual e da infraestrutura compartilhada de apresentação do ecossistema EP. Centraliza tokens de design, tipografia, temas, mecanismos de interface bilíngue, ativos visuais, componentes e renderizadores para o portfólio interativo, os relatórios de projetos e os READMEs profissionais.

Os projetos consumidores mantêm seus próprios dados, análises e conteúdos específicos. Os componentes compartilhados são mantidos neste repositório, evitando duplicação entre repositórios.

---

<a id="visual-identity"></a>

## Identidade Visual

A identidade utiliza o logotipo EP, a paleta institucional grafite e cobre, tipografia compartilhada, ícones sociais e animações Lottie. A paleta institucional é distinta do sistema cromático analítico.

| Recurso | Prévia | Arquivo |
|---|---|---|
| Logotipo EP | <img src="assets/logos/logo_initials.png" width="64" alt="Logotipo EP" /> | [`logo_initials.png`](./assets/logos/logo_initials.png) |
| GitHub | <img src="assets/icons/github_icon.svg" width="26" alt="GitHub" /> | [`github_icon.svg`](./assets/icons/github_icon.svg) |
| LinkedIn | <img src="assets/icons/linkedin_icon.svg" width="26" alt="LinkedIn" /> | [`linkedin_icon.svg`](./assets/icons/linkedin_icon.svg) |
| E-mail | <img src="assets/icons/gmail_icon.svg" width="26" alt="E-mail" /> | [`gmail_icon.svg`](./assets/icons/gmail_icon.svg) |
| Discord | <img src="assets/icons/discord_icon.svg" width="26" alt="Discord" /> | [`discord_icon.svg`](./assets/icons/discord_icon.svg) |

Consulte as [animações](./assets/animations/) e [tokens de tema](./styles/foundations.css).

A biblioteca de animações inclui os seguintes ativos Lottie para o novo layout editorial:

| Animação | Aplicação | Variantes |
|---|---|---|
| Award | Projetos Selecionados | [Grafite](./assets/animations/lottie_award_graphite.json) · [Branco](./assets/animations/lottie_award_white.json) · [Cobre](./assets/animations/lottie_award_copper.json) |
| Search-to-X | Controles dos painéis Sobre Mim | [Grafite](./assets/animations/lottie_search_to_x_graphite.json) · [Branco](./assets/animations/lottie_search_to_x_white.json) · [Cobre](./assets/animations/lottie_search_to_x_copper.json) |

### Biblioteca de Badges

A biblioteca centralizada contém 57 badges SVG: 48 de tecnologias, 3 de licenças e 6 de status. Novos relatórios usam links textuais de Topics e tags informativas de Methods. O gerador canônico é `tools/render_badges.py`. Consulte a [documentação da biblioteca](./docs/badges.md).

> [!NOTE]
> A biblioteca de recursos está versionada; a integração na nova arquitetura ainda está em andamento. A validação integrada dos consumidores e a publicação coordenada permanecem pendentes.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="shared-components"></a>

## Componentes Compartilhados

Os componentes são mantidos no EP Brand e reutilizados quando pertinentes. O builder canônico ainda será implementado; os templates atuais são macros Jinja, não páginas publicadas.

| Componente | Fonte |
|---|---|
| Configuração institucional | [`config/brand.json`](./config/brand.json) |
| Componentes web: cards, botões, links, navegação e controles | [`components/web/`](./components/web/) |
| Rodapés Markdown bilíngues | [`components/markdown/`](./components/markdown/) |
| Scripts e interações compartilhados | [`scripts/`](./scripts/) |
| Ordem de dependências | [`config/ui.json`](./config/ui.json) |
| Traduções compartilhadas | [`config/translations.json`](./config/translations.json) |
| Preparação da apresentação | [`tools/presentation.py`](./tools/presentation.py) |
| Adaptador Plotly | [Integração e validação](./docs/plotly.md) |
| Testes de regressão | [`tests/`](./tests/) |

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="themes-and-internationalization"></a>

## Temas e Internacionalização

A paleta e a tipografia estão centralizadas em [Foundations](./styles/foundations.css). Os temas claro e escuro são definidos por tokens CSS. A biblioteca de movimento, incluindo tokens e animações genéricas, está em [Motion](./styles/motion.css). A ordem de carregamento é definida em [config/ui.json](./config/ui.json).

O [controlador de tema](./scripts/theme.js) resolve e preserva uma preferência única. O [i18n](./scripts/i18n.js) traduz texto, atributos acessíveis, SVG e mensagens dinâmicas por meio de [chaves compartilhadas](./config/translations.json) e traduções locais validadas. O [carregador de ativos](./scripts/assets.js) resolve caminhos, variantes e animações a partir da mesma versão da biblioteca. Os estados dos componentes não são reinicializados pela tradução. Consulte o [contrato técnico](./docs/presentation.md). O [Header e Footer canônicos](./docs/shell.md) consomem os mesmos serviços e componentes compartilhados. Builder e adaptadores Plotly permanecem pendentes.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="ep-analytical-colour-system"></a>

## Sistema Cromático Analítico EP

O Sistema Cromático Analítico EP separa a codificação visual dos dados da identidade institucional. Escolha a classe conforme a semântica dos dados e, em seguida, a representação, o contraste e a codificação visual redundante adequados.

| Classe | Principal | Secundária | Especializada |
|---|---|---|---|
| Categórica | EP Muted Pastel | EP LipariS Adapted | — |
| Sequencial | Nuuk | Lipari | — |
| Divergente | Vik | Delphi | Ston |
| Multissequencial | Fes | — | — |
| Cíclica | VikO | — | — |

![Nove paletas analíticas; variantes categóricas nos dois temas e sete escalas contínuas](./docs/colormaps-preview.svg)

> [!WARNING]
> - **Fonte canônica:** A prévia das paletas é gerada diretamente de [config/colormaps.json](./config/colormaps.json), a configuração cromática canônica.
> - **Origem e atribuição:** As escalas contínuas utilizam Scientific Colour Maps 9.0.0 de Fabio Crameri. EP LipariS Adapted é uma adaptação própria, não uma escala oficial. Consulte a [metodologia e atribuição](./docs/colormaps.md) e a [licença MIT](./docs/LICENSE-SCIENTIFIC-COLOUR-MAPS.txt).
> - **Acessibilidade:** As paletas categóricas exigem sinais visuais complementares, como marcadores, estilos de linha, padrões ou rótulos. O contraste cromático isolado não garante acessibilidade.
> - **Integração técnica:** O futuro adaptador Plotly utilizará a configuração cromática centralizada. Nenhum renderizador Plotly está ativo nesta reconstrução.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="directory-structure"></a>

## Estrutura de Diretórios

```text
ep-brand-assets/
├── assets/
│   ├── animations/
│   ├── badges/
│   ├── fonts/
│   ├── icons/
│   ├── logos/
│   └── vendor/lottie/
├── components/
│   ├── markdown/
│   └── web/
│       ├── navigation.html
│       ├── buttons.html
│       ├── interactive.html
│       ├── localization.html
│       ├── header.html
│       ├── footer.html
│       ├── animated_icons.html
│       ├── social.html
│       ├── editorial.html
│       ├── hero_projects.html
│       ├── badges.html
│       ├── analytical.html
│       ├── disclosure.html
│       ├── report_sections.html
│       └── plotly.html
├── config/
│   ├── badges.json
│   ├── brand.json
│   ├── colormaps.json
│   ├── navigation.json
│   ├── translations.json
│   └── ui.json
├── docs/
├── scripts/
│   ├── theme.js
│   ├── i18n.js
│   ├── assets.js
│   ├── scroll-trigger.js
│   ├── navigation.js
│   ├── buttons.js
│   ├── interactive.js
│   ├── header.js
│   ├── animated-icons.js
│   ├── disclosure.js
│   ├── artifact-explorer.js
│   └── plotly.js
├── styles/
│   ├── foundations.css
│   ├── motion.css
│   ├── links.css
│   ├── buttons.css
│   ├── interactive.css
│   ├── header.css
│   ├── footer.css
│   ├── animated-icons.css
│   ├── social.css
│   ├── editorial.css
│   ├── badges.css
│   ├── analytical.css
│   ├── report-sections.css
│   └── plotly.css
├── tests/
│   ├── support.py
│   └── test_*.py
├── tools/
│   ├── presentation.py
│   ├── badge_catalog.py
│   ├── render_badges.py
│   ├── artifact_preview.py
│   └── plotly_presentation.py
├── LICENSE-BRAND.md
├── LICENSE-CODE.txt
├── LICENSE-CONTENT.md
├── README.md
└── README.pt-BR.md
```

- `assets/` — Recursos de identidade visual e fontes.
- `components/` — Rodapés Markdown e macros Jinja canônicas.
- `config/` — Dados institucionais, catálogos e ordem de dependências.
- `docs/` — Documentação técnica e atribuições.
- `scripts/` e `styles/` — Comportamento e apresentação compartilhados.
- `tests/` — Testes de componentes com infraestrutura comum.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="usage-and-integration"></a>

## Uso e Integração

A configuração [brand.json](./config/brand.json) define `asset_root` como caminho relativo à versão do EP Brand consumida. O futuro builder deverá resolver os recursos a partir do mesmo checkout ou referência imutável que fornece os componentes, sem dependência de uma branch mutável.

Os templates de `components/web/` são macros Jinja com escape HTML. O módulo [`tools/presentation.py`](./tools/presentation.py) prepara o ambiente Jinja, as referências de mensagens e os recursos do head na ordem de `config/ui.json`. O futuro builder reutilizará esse contrato; ainda não há gerador de páginas ativo. Os rodapés Markdown existentes são preservados, independentemente da nova arquitetura web. Não renomeie ativos compartilhados sem verificar os consumidores. Nenhuma geração local publica mudanças.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="testing-and-validation"></a>

## Testes e Validação

Com Python, Jinja2, Playwright, Plotly e um navegador compatível com Chromium instalados, execute a partir da raiz:

```bash
python3 tests/support.py
```

`UI_TEST_BROWSER` permite informar o executável do navegador. A suíte utiliza o manifesto de dependências, os componentes canônicos e as fontes reais do repositório. Os testes de componentes não substituem o aceite visual e funcional integrado no GitHub Pages. A suíte exige o player Lottie real, fixado em `config/ui.json`, e testa os serviços globais. Formulário real, integração dos consumidores e publicação permanecem pendentes.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="related-repositories"></a>

## Repositórios Relacionados

| Repositório | Função |
|---|---|
| [Data Science Portfolio](https://github.com/eduardojr-pereira/data-science-portfolio) | Projetos aplicados, portfólio interativo e relatórios de projetos. |
| [Data Science Knowledge Base](https://github.com/eduardojr-pereira/data-science-knowledge-base) | Notebooks de estudo, guias e materiais técnicos de referência. |

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="license"></a>

## Licença

Os termos a seguir aplicam-se somente aos materiais sobre os quais o autor detém os direitos necessários.

<table>
<tr><td align="center" valign="middle"><a href="./LICENSE-CODE.txt"><img src="./assets/badges/licenses/mit.svg" alt="MIT"></a></td><td valign="middle"><strong>Código-fonte</strong> | Scripts, componentes, renderizadores e testes autorais.</td></tr>
<tr><td align="center" valign="middle"><a href="./LICENSE-CONTENT.md"><img src="./assets/badges/licenses/cc_by_nc_4_0.svg" alt="CC BY-NC 4.0"></a></td><td valign="middle"><strong>Documentação</strong> | Conteúdo técnico e editorial autoral.</td></tr>
<tr><td align="center" valign="middle"><a href="./LICENSE-BRAND.md">Todos os direitos reservados</a></td><td valign="middle"><strong>Identidade visual EP</strong> | Ativos autorais da identidade institucional; sem permissão automática de reutilização ou redistribuição.</td></tr>
<tr><td align="center" valign="middle">Termos de terceiros</td><td valign="middle"><strong>Ativos externos</strong> | As licenças e permissões originais permanecem aplicáveis.</td></tr>
</table>

### Scientific Colour Maps — Licença MIT

| Item | Atribuição e condições |
|---|---|
| Obra original | Scientific Colour Maps 9.0.0 — Fabio Crameri |
| Copyright | Copyright (c) 2026, Fabio Crameri |
| Licença | [MIT — texto original integral da licença](./docs/LICENSE-SCIENTIFIC-COLOUR-MAPS.txt) |
| Referência | [DOI: 10.5281/zenodo.24343380](https://doi.org/10.5281/zenodo.24343380) |
| Escalas oficiais utilizadas | Nuuk, Lipari, Vik, Delphi, Ston, Fes e VikO |
| Paleta derivada | EP LipariS Adapted — adaptação EP, não uma paleta oficial de Scientific Colour Maps. |

A licença MIT permite uso, cópia, modificação e redistribuição, inclusive comercial, desde que os avisos originais de copyright e permissão acompanhem todas as cópias ou partes substanciais. O texto integral da licença é preservado no repositório. Essa licença aplica-se ao material original de Scientific Colour Maps, incluindo as partes usadas na adaptação EP e na prévia; não licencia automaticamente outros ativos da identidade EP.

> [!WARNING]
> Ícones, marcas, animações, bibliotecas e mapas cromáticos de terceiros mantêm seus respectivos direitos e termos de licença. Revise a procedência, os direitos de redistribuição e os avisos aplicáveis antes da publicação.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="contact"></a>

<!-- EP-FOOTER:START -->
## Contato

<div align="center">

<a href="https://eduardo-pereira.webflow.io/"><img src="./assets/logos/logo_initials.png" alt="Logotipo EP" height="90"></a>

Vamos nos conectar e trocar ideias e oportunidades.

<a href="mailto:eduardojr.pereira@gmail.com"><img src="./assets/icons/gmail_icon.svg" alt="E-mail" height="27"></a>&nbsp;&nbsp;
<a href="https://www.linkedin.com/in/eduardo-jr-pereira/"><img src="./assets/icons/linkedin_icon.svg" alt="LinkedIn" height="27"></a>&nbsp;&nbsp;
<a href="https://github.com/eduardojr-pereira"><img src="./assets/icons/github_icon.svg" alt="GitHub" height="27"></a>&nbsp;&nbsp;
<a href="https://discord.com/users/533043855122235393"><img src="./assets/icons/discord_icon.svg" alt="Discord" height="27"></a>

</div>

<!-- EP-FOOTER:END -->
