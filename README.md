# Aurora Regime AI

Aurora Regime AI e um projeto de pesquisa quantitativa para alocacao adaptativa de portfolio com base em regimes de mercado. A proposta e combinar sinais como momentum, volatilidade, drawdown, z-score e correlacao para classificar o contexto de mercado antes de decidir exposicao, risco e distribuicao entre ativos.

## Hipotese

A hipotese central do projeto e que a adaptacao de carteira por regime pode melhorar a relacao risco-retorno em comparacao com uma alocacao estatica. Em vez de assumir que o mercado segue uma unica dinamica, o Aurora busca reconhecer mudancas de contexto como:

- tendencia positiva;
- estresse;
- lateralizacao;
- recuperacao.

Nesta etapa inicial, a arquitetura do projeto foi preparada para pesquisa, backtests, analise e visualizacao. A estrategia quantitativa ainda nao foi implementada.

## Stack

- Python 3.11+
- `src/` layout para empacotamento profissional
- `ruff` para lint e formatacao
- `pytest` para testes
- `streamlit` para dashboard exploratorio

## Estrutura Do Projeto

```text
aurora-regime-ai/
|-- app/
|   `-- streamlit_app.py
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- cache/
|-- docs/
|   |-- dados.md
|   |-- metodologia.md
|   |-- prompts_genai.md
|   `-- vieses_e_limitacoes.md
|-- notebooks/
|   |-- 00_exploracao_inicial.ipynb
|   `-- README.md
|-- reports/
|   |-- figures/
|   |-- final/
|   `-- tables/
|-- src/
|   `-- aurora/
|       |-- analysis/
|       |-- backtest/
|       |-- data/
|       |-- features/
|       |-- genai/
|       |-- portfolio/
|       |-- regime/
|       |-- visualization/
|       |-- __init__.py
|       `-- config.py
|-- tests/
|   |-- conftest.py
|   `-- test_smoke.py
|-- .env.example
|-- .gitignore
|-- Makefile
`-- pyproject.toml
```

## Comandos Principais

```bash
make install
make format
make lint
make test
make run-smoke
make app
```

## Visualizacoes

As funcoes em `src/aurora/visualization/charts.py` retornam objetos Plotly independentes de Streamlit, permitindo uso em notebooks, relatorios e scripts.

Exemplo:

```python
from aurora.visualization import plot_equity_curves, save_figure

figure = plot_equity_curves(strategy_equity_curve, benchmark_equity_curves)
save_figure(figure, "reports/figures/equity_curve.html")
```

Outro exemplo:

```python
from aurora.visualization import plot_performance_table

metrics_figure = plot_performance_table(performance_summary)
```

## Dados

As pastas em `data/` existem apenas como estrutura de trabalho. Dados reais, bases intermediarias, caches e artefatos sensiveis nao devem ser versionados. Os diretorios mantem apenas arquivos `.gitkeep` para preservar a arvore no Git.

## Configuracao Central

O arquivo `src/aurora/config.py` e a fonte principal dos parametros metodologicos e operacionais do projeto. Ativos iniciais, janelas de features, limites de regime, frequencias, capital inicial e caminhos relativos ficam centralizados ali para evitar numeros magicos espalhados pelo codigo.

## Roadmap Inicial

- organizar ingestao e padronizacao de dados;
- estruturar geracao de features por regime;
- definir interface para classificacao de regimes;
- conectar motor de portfolio, backtest e analise;
- evoluir o dashboard para acompanhamento de resultados.

## Aviso Importante

Este repositorio tem finalidade educacional, de pesquisa e desenvolvimento. Nada aqui constitui recomendacao de investimento, oferta, garantia de retorno ou aconselhamento financeiro.
