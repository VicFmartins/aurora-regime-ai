# Aurora Regime AI

## Robo quantitativo adaptativo para alocacao de portfolio por regime de mercado.

[![CI](https://github.com/VicFmartins/aurora-regime-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/VicFmartins/aurora-regime-ai/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![Ruff](https://img.shields.io/badge/quality-ruff-D7FF64?logo=ruff&logoColor=black)
![Streamlit](https://img.shields.io/badge/dashboard-streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/status-versao%20inicial%20funcional-2E8B57)

> "Nao preve o futuro. Reconhece o regime."

## Visao geral

O Aurora Regime AI e um projeto quantitativo desenvolvido para o Desafio Quant AI 2026. A proposta e construir uma estrategia sistematica de alocacao tatica de portfolio capaz de reconhecer diferentes ambientes de mercado e adaptar a carteira de forma explicavel, auditavel e reprodutivel.

Em vez de assumir que todos os ativos performam da mesma forma em qualquer contexto, o projeto usa sinais quantitativos para classificar o mercado em regimes e, a partir disso, aplicar politicas de peso definidas previamente. O objetivo nao e prever o proximo movimento de preco com precisao pontual, e sim ajustar a exposicao conforme o ambiente identificado.

Isso torna o projeto relevante por tres motivos:

- conecta pesquisa quantitativa, engenharia de software e controle metodologico;
- documenta o fluxo completo de dados ate relatorio final;
- entrega uma base funcional para evolucao futura, sem depender de caixas-pretas para tomar decisao de investimento.

## Hipotese de pesquisa

A hipotese central do Aurora e que ativos e estrategias nao performam da mesma forma em todos os ambientes de mercado. Se o projeto conseguir identificar regimes como tendencia positiva, estresse, lateralizacao e recuperacao com regras objetivas e sem look-ahead bias, entao uma politica adaptativa de alocacao pode melhorar a relacao risco-retorno frente a benchmarks passivos coerentes.

Essa hipotese e testavel porque o projeto compara a estrategia com referencias explicitas, como:

- `buy and hold` em `BOVA11.SA`
- `CDI` ou caixa defensivo
- carteira estatica diversificada `60/40`
- carteira `equal weight`

E a avaliacao nao se limita a retorno bruto. O projeto observa retorno, volatilidade, drawdown, turnover e metricas de eficiencia de risco.

## Como funciona

Fluxo principal do projeto:

`Dados -> Features -> Regime -> Pesos -> Backtest -> Metricas -> Dashboard -> Relatorio GenAI`

Resumo do pipeline:

1. carrega dados de mercado via cache, `yfinance` ou CSV manual;
2. calcula features quantitativas;
3. defasa as features de decisao em 1 periodo;
4. classifica o mercado em um dos regimes definidos;
5. converte o regime em pesos long-only a priori;
6. executa o backtest mensal com barreira temporal;
7. compara com benchmarks;
8. gera metricas, visualizacoes, dashboard e apoio documental.

## Regimes classificados

- `TENDENCIA_POSITIVA`
- `ESTRESSE`
- `LATERALIZACAO`
- `RECUPERACAO`

## Indicadores utilizados

- `Momentum`
- `Volatilidade`
- `Drawdown`
- `Z-score`
- `Correlacao`

## Universo inicial de ativos

- `BOVA11.SA`
- `IVVB11.SA`
- `IMAB11.SA`
- `USDBRL=X`
- `CDI` ou proxy defensivo

## Arquitetura

O repositorio esta organizado como uma stack de pesquisa quantitativa com modulos separados para:

- configuracao central;
- ingestao e validacao de dados;
- engenharia de features;
- classificacao de regime;
- politica de alocacao;
- motor de backtest;
- benchmarks;
- metricas e tabelas;
- visualizacoes;
- dashboard Streamlit;
- camada GenAI de explicabilidade e documentacao.

## Stack

- Python
- pandas
- numpy
- yfinance
- plotly
- streamlit
- pytest
- ruff

## Estrutura de pastas

```text
aurora-regime-ai/
|-- .github/workflows/      # CI com checks de qualidade
|-- app/                    # Dashboard Streamlit
|-- data/                   # Estrutura local de dados, cache e fallback CSV
|-- docs/                   # Metodologia, dados, vieses, GenAI e defesa tecnica
|-- notebooks/              # Exploracao inicial
|-- reports/                # Figuras, tabelas e relatorio final
|-- scripts/                # Entrypoints utilitarios
|-- src/aurora/             # Codigo principal do projeto
|-- tests/                  # Suite automatizada de testes
|-- Makefile
|-- pyproject.toml
`-- README.md
```

## Como rodar localmente

### Opcao com Python direto

```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
py -3.13 -m pip install -e ".[dev]"
py -3.13 -m ruff format .
py -3.13 -m ruff check .
py -3.13 -m pytest
```

Se o Python 3.13 nao estiver disponivel, use a versao instalada no ambiente mantendo os mesmos comandos.

### Opcao com make

Se o ambiente tiver `make` instalado:

```bash
make install
make format
make lint
make test
```

## Como rodar o pipeline

Com `make`:

```bash
make run-pipeline
```

Com Python direto:

```bash
py -3.13 scripts/run_pipeline.py --offline
```

Observacoes:

- o pipeline tenta usar cache e fluxo online quando disponivel;
- se isso falhar, existe fallback offline por CSV de exemplo ou dados sinteticos deterministas;
- os artefatos sao exportados em `reports/tables/`, `reports/figures/` e `data/processed/`.

## Como abrir o dashboard

Com `make`:

```bash
make app
```

Com Python direto:

```bash
py -3.13 -m streamlit run app/streamlit_app.py
```

O dashboard abre em modo offline por padrao e reutiliza a pipeline do projeto, sem duplicar logica quantitativa pesada dentro da aplicacao.

## Testes e qualidade

O projeto usa:

- `pytest` para testes automatizados;
- `ruff` para formatacao e lint;
- GitHub Actions para CI.

Cobertura funcional atual:

- imports basicos;
- configuracao central;
- validacao de dados;
- fallback CSV;
- features quantitativas;
- classificador de regimes;
- politica de alocacao;
- backtest mensal;
- benchmarks;
- metricas de performance;
- visualizacoes;
- pipeline end-to-end;
- camada GenAI de prompts.

## Metodologia e prevencao de vieses

O Aurora foi desenhado para reduzir vieses metodologicos comuns em projetos quant.

### Look-ahead bias

- as features usadas para decisao sao defasadas em `1` periodo;
- o classificador consome apenas essas features defasadas;
- o backtest aplica os pesos somente no periodo posterior ao sinal.

### Overfitting

- thresholds de regime sao tratados como premissas metodologicas;
- pesos sao definidos a priori;
- a estrategia nao foi calibrada retroativamente para maximizar o backtest final;
- benchmarks simples e transparentes ajudam a manter disciplina comparativa.

### Limitacoes do backtest

- custos sao simplificados em bps sobre turnover;
- nao ha slippage real;
- nao ha impacto de mercado, impostos ou restricoes operacionais completas;
- dados publicos e proxies podem introduzir ruido adicional.

## Resultados

O repositorio esta em versao inicial funcional, com pipeline, dashboard, documentacao e testes automatizados. O projeto exporta os resultados quantitativos reais para:

- `reports/tables/performance_summary.csv`
- `reports/tables/rebalance_log.csv`
- `reports/tables/target_weights.csv`
- `reports/tables/classified_regimes.csv`

Para evitar desatualizacao ou leitura indevida de numeros demonstrativos como se fossem evidencia de mercado, o README nao fixa metricas finais de performance como verdade permanente do projeto. A recomendacao e gerar os resultados localmente a partir da pipeline validada e preencher o relatorio tecnico final com base nesses artefatos.

## Uso de GenAI

A IA Generativa no Aurora nao decide pesos, nao escolhe regime e nao substitui o motor quantitativo. Seu papel e de apoio a:

- explicabilidade;
- resumo executivo;
- analise por regime;
- revisao de vieses e limitacoes;
- preparacao de defesa tecnica;
- organizacao do relatorio final.

Ou seja, a camada GenAI existe para comunicar e revisar o projeto, nao para tomar decisao de investimento.

## Limitacoes

Limitacoes reais da versao atual:

- dados publicos sujeitos a falhas e cobertura desigual;
- uso de proxies, especialmente para `CDI`;
- custos de transacao simplificados;
- ausencia de slippage real;
- thresholds iniciais definidos por premissa metodologica;
- regras de regime ainda simples;
- backtest historico nao garante performance futura;
- necessidade de validacao adicional fora da amostra e em contexto operacional mais realista.

## Disclaimer

Este projeto tem finalidade educacional, experimental e de pesquisa. Nada aqui constitui recomendacao de investimento, oferta, promessa de retorno, consultoria financeira ou inducao a compra e venda de ativos. Resultados historicos, simulados, sinteticos ou de backtest nao garantem desempenho futuro.

## Status do projeto

O Aurora Regime AI esta em versao inicial funcional, com:

- arquitetura modular implementada;
- pipeline offline e online com fallback;
- dashboard funcional;
- documentacao tecnica;
- CI configurado;
- testes automatizados passando.
