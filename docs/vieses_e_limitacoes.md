# Vieses E Limitacoes

O projeto deve acompanhar, desde o inicio, riscos metodologicos comuns em pesquisa quantitativa:

- look-ahead bias;
- survivorship bias;
- data snooping;
- overfitting;
- instabilidade de regime;
- custos de transacao subestimados;
- degradacao de sinal fora da amostra.

## Controle De Look-Ahead Bias

O Aurora evita look-ahead bias em camadas complementares:

- o pipeline de features aplica `shift(1)` nas variaveis de decisao;
- o classificador consome apenas essas features defasadas;
- o motor de backtest aplica o peso decidido na data `t` somente na primeira observacao de retorno estritamente posterior a `t`.

Na pratica, isso significa que o peso usado ao longo de um mes decorre do sinal do periodo anterior. Mesmo que o rebalanceamento seja mensal, a estrategia nunca usa o proprio fechamento da data de decisao para calcular e aplicar o peso no mesmo retorno.

## Outras Limitacoes

- a versao inicial ainda usa regras fixas e simples de classificacao;
- custos sao modelados em bps sobre turnover, sem microestrutura;
- o motor atual nao incorpora slippage, impostos, limites de liquidez ou impacto de mercado;
- resultados futuros podem mudar quando novas fontes de dados e restricoes operacionais forem adicionadas.
