# Aurora Regime AI

[![CI](https://github.com/VicFmartins/aurora-regime-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/VicFmartins/aurora-regime-ai/actions/workflows/ci.yml)

Adaptive quantitative research project for portfolio allocation by market regime.

Aurora Regime AI was built to recognize market context, not to predict the future tick by tick. The core idea is to combine interpretable signals such as momentum, volatility, drawdown, z-score and correlation, classify the environment into explicit regimes, and map those regimes into predefined portfolio weights.

## Hypothesis

The central research hypothesis is that a regime-aware allocation process can improve risk-adjusted outcomes relative to static allocations, while remaining explainable and auditable.

Operationally, this hypothesis is tested by comparing the strategy against coherent benchmarks such as:

- `buy and hold` in `BOVA11.SA`
- `CDI` or defensive cash proxy
- static diversified `60/40`
- `equal weight`

The evaluation lens is not raw return alone. The project checks whether the regime-aware process can improve the balance between return, volatility, drawdown and portfolio turnover.

Instead of assuming a single market dynamic, Aurora evaluates whether the market is closer to:

- `TENDENCIA_POSITIVA`
- `ESTRESSE`
- `LATERALIZACAO`
- `RECUPERACAO`

## Architecture

The repository is organized as a professional research stack with separated layers for:

- configuration and project parameters;
- market data ingestion, validation and cache;
- feature engineering;
- rule-based regime classification;
- regime-to-allocation mapping;
- monthly backtest engine;
- benchmark construction;
- performance analysis;
- Plotly visualizations;
- Streamlit dashboard;
- GenAI-assisted reporting prompts and technical documentation.

## Stack

- Python 3.11+
- `pandas` and `numpy` for data handling
- `yfinance` for public market data ingestion
- `pytest` for automated tests
- `ruff` for formatting and linting
- `plotly` for modular charts
- `streamlit` for the interactive dashboard

## How To Run

Install dependencies:

```bash
make install
```

Run formatting, lint and tests:

```bash
make format
make lint
make test
```

If `make` is not available in your environment, the same checks can be run with:

```bash
python -m ruff format .
python -m ruff check .
python -m pytest
```

Run the full pipeline:

```bash
make run-pipeline
```

Run the pipeline explicitly in offline mode:

```bash
python scripts/run_pipeline.py --offline
```

## How To Run The Dashboard

Start the Streamlit app:

```bash
make app
```

The dashboard starts in offline-friendly mode by default and can still run without internet using:

- `data/raw/example_prices.csv` when valid for the current thresholds;
- deterministic synthetic data when the example file is insufficient.

## Methodology In Brief

Aurora follows a deliberately simple and defensible methodology:

1. load price data from cache, public source or manual CSV;
2. compute quantitative features;
3. shift decision features by one period to prevent look-ahead bias;
4. classify the market into one of four regimes with fixed rules;
5. assign long-only portfolio weights defined a priori;
6. rebalance monthly in the backtest engine;
7. compare the strategy with coherent benchmarks;
8. summarize performance in tables, charts and technical documentation.

Key methodological controls:

- no regime threshold is optimized on final performance;
- allocation weights are defined before reviewing the backtest outcome;
- portfolio weights decided at time `t` are only applied from the next return observation onward;
- GenAI is used for synthesis and documentation support, not for trading decisions.

Audit artifacts exported by the pipeline include:

- `reports/tables/performance_summary.csv`
- `reports/tables/rebalance_log.csv`
- `reports/tables/target_weights.csv`
- `reports/tables/classified_regimes.csv`

## Validated Status And Demo Snapshot

Current public repository status:

- the pipeline, dashboard, benchmarks and reporting layers are fully wired and tested;
- final real-market presentation metrics should be filled from the latest validated pipeline output in `reports/tables/performance_summary.csv`;
- a technical report template is available at `reports/final/relatorio_tecnico.md`.

Reproducible offline validation snapshot based on synthetic data:

- annualized return: `5.48%`
- annualized volatility: `3.87%`
- max drawdown: `-5.48%`
- number of rebalances: `119`

Important note:

- the snapshot above is a deterministic offline demonstration only;
- it is included to prove reproducibility of the pipeline, not to claim economic edge;
- it must not be interpreted as live, investable or market-validated performance.

## Limitations

Current limitations include:

- rule-based regime logic is intentionally simple in this version;
- no slippage, taxes or market impact model is included yet;
- the asset universe is still compact and research-oriented;
- public data sources may require manual fallback or validation;
- robustness still needs broader out-of-sample and operational testing.

## Folder Structure

```text
aurora-regime-ai/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- app/
|   `-- streamlit_app.py
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- cache/
|-- docs/
|   |-- dados.md
|   |-- defesa_tecnica.md
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
|-- scripts/
|   `-- run_pipeline.py
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
|       |-- config.py
|       `-- pipeline.py
|-- tests/
|   |-- conftest.py
|   |-- test_genai.py
|   |-- test_pipeline.py
|   `-- test_smoke.py
|-- .env.example
|-- .gitignore
|-- Makefile
|-- pyproject.toml
`-- README.md
```

## Disclaimer

This repository is for education, research and portfolio demonstration purposes only. Nothing here constitutes investment advice, an offer, a promise of return or a recommendation to buy or sell any asset. Historical, simulated or synthetic results do not guarantee future performance.
