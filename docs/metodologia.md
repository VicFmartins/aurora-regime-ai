# Metodologia

Este documento vai consolidar a metodologia do Aurora Regime AI, incluindo:

- definicao operacional dos regimes de mercado;
- regras de calculo de indicadores e features;
- processos de rotulagem, calibracao e validacao;
- criterios de alocacao e controle de risco;
- protocolo de backtest e comparacao com benchmarks.

Fonte principal de parametros:

- `src/aurora/config.py` centraliza o universo inicial de ativos, as janelas de calculo, os thresholds de regime, a frequencia padrao e os caminhos relativos usados pelo projeto.

Nesta fase, o projeto esta apenas estruturado. Nenhuma regra quantitativa foi implementada ainda.
