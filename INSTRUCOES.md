# EP Brand Assets — pacote de componentes (proposta)

Pacote **aditivo**: não substitui `README.md`, logo ou ícones já existentes no repositório. Aprovado como ponto de partida a partir dos READMEs de `data-science-portfolio` e `data-science-knowledge-base` consultados em 22/11/2026.

## Arquivos

- `config/brand.json`: URLs e informações centrais.
- `components/markdown/footer.en.md` e `footer.pt-BR.md`: modelos A.
- `components/web/footer.html` e `footer.css`: modelo B.
- `tools/render_footer.py`: prévia/geração em modo somente leitura por padrão.
- `tests/test_components.py`: testes de regressão.

## Instalação no clone local de ep-brand-assets

A partir da raiz do clone, extraia o ZIP do pacote, **sem** sobrescrever arquivos existentes. Você também pode copiar apenas `components/`, `config/`, `tools/`, `tests/` e `INSTRUCOES.md`.

```bash
python -m unittest discover -s tests -v
python tools/render_footer.py readme --kind portfolio --lang en
python tools/render_footer.py readme --kind knowledge-base --lang pt-BR
python tools/render_footer.py web
python tools/render_footer.py web --css
```

## Atualização de README (primeiro: somente leitura)

```bash
python tools/render_footer.py readme --kind portfolio --lang en --file /caminho/data-science-portfolio/README.md
```

Revise o diff. **Somente depois de aprovação**, acrescente `--apply`. O comando não faz commit nem push. O programa não altera o cabeçalho do README e se recusa a substituir a seção de contato quando ela não é a última ou quando falta a âncora `readme-top`.

## Para integrar HTML na vitrine e no Bike Sharing

O gerador do site deve usar `footer.html` como trecho de HTML e incluir `footer.css` no CSS da página. Para o HTML funcionar offline, renderize com:

```bash
python tools/render_footer.py web --embed-assets
```

Isso exige que os arquivos `assets/logos/logo_initials.png` e `assets/icons/{github,linkedin,gmail}_icon.svg` estejam presentes no clone de `ep-brand-assets`; os ícones são embutidos em `data:` URLs no HTML gerado. A integração efetiva com `build_pages_site.py` e `report_builder.py` será uma etapa separada para não modificar geradores aprovados sem teste.

## Observações

- O padrão de README aprovado contém HTML no Markdown (`div align=center` e links com imagens); ele foi mantido.
- Modelo A está em EN/PT-BR. Modelo B em EN, como o conteúdo da vitrine existente.
- A família de ícones atual foi preservada sem alterações.
- O ano de copyright do rodapé HTML é definido durante a geração.
- O logo dos dois rodapés abre o website pessoal.
- Não altere links de destino antigos automaticamente sem revisão do diff.
