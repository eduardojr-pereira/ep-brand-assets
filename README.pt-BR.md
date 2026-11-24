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

Consulte as [animações](./assets/animations/) e [tokens de tema](./styles/theme-tokens.css).

### Biblioteca de Badges

A biblioteca centralizada contém 80 badges SVG: 48 de tecnologias, 2 de licenças, 6 de status, 22 de tópicos e 2 de métodos. Technologies, Licenses e Status podem ser utilizados em READMEs e HTMLs; Topics e Methods são exclusivos dos HTMLs da vitrine e dos relatórios. Consulte a [documentação da biblioteca](./docs/badges.md).

> [!NOTE]
> A biblioteca foi integrada e versionada localmente. A validação integrada dos consumidores e a publicação coordenada permanecem pendentes.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="shared-components"></a>

## Componentes Compartilhados

Os componentes são mantidos no EP Brand e reutilizados quando pertinentes. O builder compõe o portfólio e os relatórios a partir das fontes canônicas, evitando implementações separadas em cada projeto.

| Componente | Fonte |
|---|---|
| Configuração institucional | [`config/brand.json`](./config/brand.json) |
| Componentes web: Header, Footer, cards, botões, links, navegação e controles | [`components/web/`](./components/web/) |
| Rodapés Markdown bilíngues | [`components/markdown/`](./components/markdown/) |
| Scripts e interações compartilhados | [`scripts/`](./scripts/) |
| Composição, renderização e publicação | [`tools/`](./tools/) |
| Testes de regressão | [`tests/`](./tests/) |

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="themes-and-internationalization"></a>

## Temas e Internacionalização

Uma camada centralizada de apresentação garante consistência visual e linguística no portfólio e nos relatórios dos projetos.

| Mecanismo | Responsabilidade | Fonte |
|---|---|---|
| Tokens de tema | Definições compartilhadas dos temas claro e escuro | [theme-tokens.css](./styles/theme-tokens.css) |
| Tipografia | Sistema tipográfico consistente | [typography-v2.css](./styles/typography-v2.css) |
| Inicialização do tema | Configuração inicial do tema | [theme-init.js](./scripts/theme-init.js) |
| Alternância de tema | Alternância entre os temas claro e escuro | [theme.js](./scripts/theme.js) |
| Internacionalização | Mecanismos compartilhados de interface bilíngue | [i18n.js](./scripts/i18n.js) |
| Temas do Plotly | Apresentação analítica consistente | [plotly-theme.js](./scripts/plotly-theme.js) |
| Localização do Plotly | Apresentação dos gráficos conforme o idioma | [plotly-i18n.js](./scripts/plotly-i18n.js) |

> [!IMPORTANT]
> Os mecanismos de apresentação são centralizados no EP Brand, enquanto as traduções específicas permanecem nos respectivos projetos. As mudanças de tema e idioma afetam apenas a apresentação, preservando os dados analíticos subjacentes.

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
> - **Integração técnica:** O [renderizador Plotly canônico](./tools/render_plotly.py) e o [CSS gerado](./styles/colormaps.css) utilizam a mesma configuração cromática centralizada.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="directory-structure"></a>

## Estrutura de Diretórios

<details>
<summary><strong>Árvore do repositório</strong></summary>

```text
ep-brand-assets/
├── .github/
│   └── workflows/
├── .gitignore
├── LICENSE-BRAND.md
├── LICENSE-CODE.txt
├── LICENSE-CONTENT.md
├── README.md
├── README.pt-BR.md
├── assets/
│   ├── animations/
│   ├── badges/
│   ├── icons/
│   │   └── technologies/
│   └── logos/
├── components/
│   ├── markdown/
│   └── web/
├── config/
│   └── badges.json
├── docs/
│   └── badges.md
├── scripts/
├── styles/
├── tests/
│   └── test_badge_library.py
└── tools/
    ├── badge_html.py
    └── render_badges.py
```

</details>

- `assets/` — Recursos de identidade visual.
- `components/` — Componentes canônicos Markdown e web.
- `config/` — Configuração cromática institucional e analítica.
- `docs/` — Documentação técnica e atribuições de terceiros.
- `scripts/` e `styles/` — Comportamento, temas e apresentação compartilhados.
- `tests/` — Testes automatizados de regressão.
- `tools/` — Utilitários de renderização, composição e publicação.

A árvore inclui a biblioteca de badges e reflete a estrutura local; a publicação coordenada permanece pendente.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="usage-and-integration"></a>

## Uso e Integração

Em outros repositórios, utilize os endereços públicos dos ativos.

```markdown
![EP](https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/logos/logo_initials.png)
```

```html
<img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/github_icon.svg" alt="GitHub" width="26" />
```

Mantenha o checkout canônico do EP Brand ao lado do checkout do Portfolio. A partir do EP Brand, substitua o caminho de origem pelo caminho local do Portfolio; utilize um diretório de saída fora dos dois repositórios.

```bash
python3 tools/build_site.py --source /path/to/data-science-portfolio --output /tmp/ep-portfolio-preview
```

Visualize os rodapés Markdown sem alterar arquivos:

```bash
python3 tools/render_footer.py readme --kind portfolio --lang en
python3 tools/render_footer.py readme --kind knowledge-base --lang pt-BR
```

Com `--file`, o renderizador exibe o diff proposto; somente `--apply` grava alterações. Revise antes de aplicar. Renderize o footer web com ativos embutidos usando `python3 tools/render_footer.py web --embed-assets`.

Não renomeie ativos compartilhados sem verificar os consumidores. A geração local não publica alterações.

<p align="right"><sub><a href="#readme-top">↑ Voltar ao topo</a></sub></p>

---

<a id="testing-and-validation"></a>

## Testes e Validação

Execute a suíte de testes de regressão a partir da raiz do repositório:

```bash
python3 -m unittest discover -s tests -v
```

Revise as prévias geradas e verifique os componentes compartilhados, temas, alternância de idioma, navegação e apresentação analítica nos projetos consumidores antes da publicação.

> [!NOTE]
> A validação integrada final e a publicação coordenada permanecem pendentes. A geração local não publica alterações.

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

<a href="https://eduardo-pereira.webflow.io/"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/logos/logo_initials.png" alt="Logotipo EP" height="90"></a>

Vamos nos conectar e trocar ideias e oportunidades.

<a href="mailto:eduardojr.pereira@gmail.com"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/gmail_icon.svg" alt="E-mail" height="27"></a>&nbsp;&nbsp;
<a href="https://www.linkedin.com/in/eduardo-jr-pereira/"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/linkedin_icon.svg" alt="LinkedIn" height="27"></a>&nbsp;&nbsp;
<a href="https://github.com/eduardojr-pereira"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/github_icon.svg" alt="GitHub" height="27"></a>&nbsp;&nbsp;
<a href="https://discord.com/users/533043855122235393"><img src="https://raw.githubusercontent.com/eduardojr-pereira/ep-brand-assets/main/assets/icons/discord_icon.svg" alt="Discord" height="27"></a>

</div>

<!-- EP-FOOTER:END -->
