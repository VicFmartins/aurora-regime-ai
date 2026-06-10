# Metodologia

Este documento vai consolidar a metodologia do Aurora Regime AI, incluindo:

- definicao operacional dos regimes de mercado;
- regras de calculo de indicadores e features;
- processos de rotulagem, calibracao e validacao;
- criterios de alocacao e controle de risco;
- protocolo de backtest e comparacao com benchmarks.

Fonte principal de parametros:

- `src/aurora/config.py` centraliza o universo inicial de ativos, as janelas de calculo, os thresholds de regime, a frequencia padrao e os caminhos relativos usados pelo projeto.

## Features Quantitativas

As features do Aurora transformam a serie de precos em sinais interpretableis para classificacao de regime. O pipeline preserva `NaN` no inicio das janelas e aplica `shift(1)` apenas ao final da montagem do conjunto de decisao, evitando look-ahead bias no backtest.

### Momentum

Momentum mede o retorno acumulado em janelas como 63, 126 e 252 periodos. Ele ajuda a diferenciar contextos de tendencia positiva, perda de forca ou recuperacao apos quedas.

### Volatilidade

Volatilidade e calculada sobre retornos em janela movel e pode ser anualizada. Ela ajuda a identificar transicoes para ambientes de estresse, incerteza elevada e mudancas bruscas de comportamento.

### Drawdown

Drawdown mede a distancia do preco atual para o pico recente da janela. Esse indicador ajuda a detectar deterioracao persistente, estresse e fragilidade estrutural mesmo quando a volatilidade isolada nao captura toda a perda acumulada.

### Z-Score

O z-score padroniza retornos em relacao a sua media e dispersao recentes. Isso ajuda a encontrar desvios anormais, excessos de movimento e sinais de compressao ou esticamento que podem marcar mudanca de regime.

### Correlacao

Correlacoes moveis entre ativos mostram quando diferentes blocos de mercado passam a andar mais juntos ou se desacoplam. Em regimes de estresse, correlacoes tendem a subir, reduzindo diversificacao efetiva.

## Uso Metodologico

- momentum ajuda a separar tendencia e recuperacao;
- volatilidade ajuda a detectar estresse e instabilidade;
- drawdown ajuda a capturar perdas acumuladas;
- z-score ajuda a medir anomalias de curto e medio prazo;
- correlacao ajuda a avaliar contagio e quebra de diversificacao.

## Arvore De Decisao Dos Regimes

O classificador inicial do Aurora e propositalmente baseado em regras simples, explicaveis e parametrizadas em `config.py`. Os thresholds nao sao ajustados olhando o desempenho final do backtest; eles sao definidos ex ante para manter interpretabilidade metodologica.

Ordem de decisao:

1. `ESTRESSE`
   Se `drawdown` estiver abaixo do limite de estresse ou se a volatilidade anualizada estiver acima do teto configurado.
2. `TENDENCIA_POSITIVA`
   Se `momentum_126 > 0`, `momentum_252 > 0` e a volatilidade permanecer controlada.
3. `RECUPERACAO`
   Se o `drawdown` ainda for negativo, mas `momentum_63 > 0` e o `z-score` estiver melhorando.
4. `LATERALIZACAO`
   Caso residual, quando nenhum dos gatilhos anteriores estiver ativo.

Os sinais usados na classificacao sao armazenados junto com o regime e a explicacao textual, o que facilita auditoria e revisao do racional de cada decisao.
